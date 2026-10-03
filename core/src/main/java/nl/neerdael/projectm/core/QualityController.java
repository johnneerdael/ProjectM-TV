package nl.neerdael.projectm.core;

import android.util.Log;

import java.util.ArrayList;
import java.util.List;

/**
 * Dynamic resolution: picks the render height from a ladder of levels so the frame rate stays at
 * its target, and raises it again when there is headroom.
 *
 * Changes apply immediately: since 1.9.12 a new render size keeps the presets' frames (scaled,
 * projectM patch 0002), so no preset switch or hard cut is needed to hide it. After a change the
 * frame rate is left to settle before the next decision.
 *
 * Heights are limited to the panel, to {@link #RENDER_HEIGHT_CAP} and to a memory-safe maximum (see
 * {@link DeviceProfile#memorySafeHeight()}); memory pressure reported by Android lowers that
 * maximum for the rest of the session.
 *
 * All methods run on the UI thread.
 */
public final class QualityController {
    private static final String TAG = "QualityController";

    public interface Listener {
        void onApplyRenderHeight(int height);
    }

    /** Result of {@link #onFpsSample}. */
    public static final int ACTION_NONE = 0;
    /** Current preset is too slow for this device even at the lowest resolution: skip it. */
    public static final int ACTION_SKIP = 2;

    /**
     * Highest render height, for automatic and fixed resolution alike; the display's scaler upscales
     * to the panel. projectM draws lines, blur and the presets' texel steps as at MilkDrop's
     * 1024x768 (patch 0021), but presets that feed their image back also re-sample it bilinearly
     * every frame, which smooths by a fraction of a real texel: above about twice the reference's
     * size (665 lines at 16:9) that smoothing is too small a share of the picture and such presets
     * settle into another pattern (Acid Mandala's red spokes die out from 2880x1620). Measured on
     * 24 presets against the authored 1182x665 render; see docs/ARCHITECTURE.md (Lines).
     */
    public static final int RENDER_HEIGHT_CAP = 1330;

    /** Auto ladder, filtered to the panel resolution. */
    private static final int[] AUTO_LADDER = {360, 432, 540, 720, 900, 1080, 1260, 1440, 1800, 2160};

    private static final float DOWN_THRESHOLD = 0.85f;     // of target fps
    private static final float SEVERE_THRESHOLD = 0.55f;
    private static final float UP_THRESHOLD = 0.97f;
    private static final int DOWN_SAMPLES = 3;              // consecutive 1 s samples
    private static final int SEVERE_SAMPLES = 4;
    private static final int UP_SAMPLES = 15;
    private static final float SKIP_THRESHOLD = 0.5f;
    private static final int SKIP_SAMPLES = 5;
    private static final long SETTLE_MS = 3000;             // ignore load hitch + transition start
    private static final long PRESSURE_QUIET_MS = 10000;    // one step per burst of memory warnings
    private static final float MIN_GAIN = 1.10f;             // a lower level must be this much faster
    private static final int MAX_BACKOFF_PRESETS = 16;       // longest wait before a failed level is retried

    private final Listener listener;
    private final int[] levels;
    private final int minIndex;
    private boolean auto;
    private int fixedHeight;
    private int current;            // index into levels (auto mode)
    private float targetFps = 60f;
    private long settleUntil;
    private long transitionMs;
    private int slowSamples, severeSamples, goodSamples, tooSlowSamples;
    private boolean skipSlowPresets;
    private boolean switchRequested;  // skip asked for, waiting for onPresetChanged
    private final int[] blockedUntilPreset;  // per level: don't retry until this preset count
    private final int[] failures;            // per level: exponential back-off after failed probes
    private int presetCount;
    private int ceiling;                     // highest level auto may use (lowered by memory pressure)
    private long pressureQuietUntil;
    private float fpsBeforeLowering;         // > 0: judge whether the last lowering helped
    private int loweredFrom = -1;            // level before the last lowering
    private int cpuBoundPreset = -1;         // preset for which a lower resolution did not help
    private int beforePressure = -1;         // auto level when memory pressure first lowered the ceiling

    /** @param memoryLimit highest render height allowed for memory reasons, 0 for none. */
    public QualityController(DisplayInfo display, DeviceProfile profile, int memoryLimit, Listener listener) {
        this.listener = listener;
        List<Integer> usable = new ArrayList<>();
        int maxHeight = limit(display, memoryLimit);
        for (int h : AUTO_LADDER) if (h <= maxHeight) usable.add(h);
        if (usable.isEmpty() || usable.get(usable.size() - 1) < maxHeight) usable.add(maxHeight);
        levels = new int[usable.size()];
        for (int i = 0; i < levels.length; i++) levels[i] = usable.get(i);
        blockedUntilPreset = new int[levels.length];
        failures = new int[levels.length];
        minIndex = indexAtMost(profile.minAutoHeight());
        current = indexAtMost(profile.initialAutoHeight());
        ceiling = levels.length - 1;
    }

    private static int limit(DisplayInfo display, int memoryLimit) {
        int max = Math.min(display.physicalHeight, RENDER_HEIGHT_CAP);
        return memoryLimit > 0 ? Math.min(max, memoryLimit) : max;
    }

    /**
     * Levels available for manual selection in the menu (ascending heights): 720, 1080, 1440 and
     * 2160 up to the panel, {@link #RENDER_HEIGHT_CAP} and the memory limit, plus that maximum.
     */
    public static int[] manualHeights(DisplayInfo display, int memoryLimit) {
        int maxHeight = limit(display, memoryLimit);
        List<Integer> list = new ArrayList<>();
        for (int h : new int[]{720, 1080, 1440, 2160}) if (h <= maxHeight) list.add(h);
        if (list.isEmpty() || list.get(list.size() - 1) < maxHeight) list.add(maxHeight);
        int[] result = new int[list.size()];
        for (int i = 0; i < result.length; i++) result[i] = list.get(i);
        return result;
    }

    /**
     * Returns {@code savedHeight} if it is still a valid fixed level for this panel, otherwise 0
     * (automatic). A saved 2160 must not be used after the device moved to a 1080p panel, or
     * above the memory limit. A height above {@link #RENDER_HEIGHT_CAP} (a 1440 or 4K saved before
     * the cap) means "the sharpest" and becomes the cap where the panel and memory allow it.
     */
    public static int validFixedHeight(DisplayInfo display, int memoryLimit, int savedHeight) {
        int wanted = Math.min(savedHeight, RENDER_HEIGHT_CAP);
        for (int h : manualHeights(display, memoryLimit)) if (h == wanted) return wanted;
        return 0;
    }

    /** @param height 0 for automatic, otherwise a fixed render height (at most {@link #RENDER_HEIGHT_CAP}). */
    public void setMode(int height, int lastAutoHeight) {
        auto = height <= 0;
        fixedHeight = Math.min(height, RENDER_HEIGHT_CAP);
        resetCounters(0);
        if (auto && lastAutoHeight > 0) current = Math.max(minIndex, Math.min(ceiling, indexAtMost(lastAutoHeight)));
        listener.onApplyRenderHeight(currentHeight());
    }

    public void setTargetFps(float fps) {
        targetFps = fps;
        resetCounters(SETTLE_MS);
    }

    public void setSkipSlowPresets(boolean enabled) {
        skipSlowPresets = enabled;
        tooSlowSamples = 0;
    }

    public void setTransitionSeconds(int seconds) {
        transitionMs = seconds * 1000L;
    }

    public boolean isAuto() {
        return auto;
    }

    public int currentHeight() {
        return auto ? levels[current] : fixedHeight;
    }

    /**
     * Automatic height to remember for the next launch: the level chosen for the frame rate, not
     * the lower one memory pressure imposed on this session (that limit must not carry over).
     */
    public int autoHeightToRemember() {
        return current == ceiling && beforePressure > current ? levels[beforePressure] : levels[current];
    }

    /** Called when a new preset starts: its load and blend are not judged. */
    public void onPresetChanged() {
        presetCount++;
        switchRequested = false;
        fpsBeforeLowering = 0;
        resetCounters(SETTLE_MS + transitionMs);
    }

    /**
     * Android reports that memory is running low while we are in the foreground: other apps (such
     * as the music player) are about to be killed. Lowers the automatic resolution one level now
     * (one step per burst of warnings) and never goes back above it in this session.
     */
    public void onMemoryPressure(int level) {
        if (!auto) {
            Log.w(TAG, "Memory pressure (level " + level + ") at fixed " + fixedHeight + "p");
            return;
        }
        long now = System.currentTimeMillis();
        if (now < pressureQuietUntil) return;
        pressureQuietUntil = now + PRESSURE_QUIET_MS;
        if (beforePressure < 0) beforePressure = current;
        ceiling = Math.min(ceiling, Math.max(minIndex, current - 1));
        Log.w(TAG, "Memory pressure (level " + level + "): limiting resolution to " + levels[ceiling]
                + " for this session");
        if (current > ceiling) apply(ceiling, "memory pressure");
    }

    /** One-second frame-rate sample; returns one of the ACTION_ constants. */
    public int onFpsSample(float fps) {
        if (System.currentTimeMillis() < settleUntil || fps <= 0) return ACTION_NONE;

        // Presets that stay far below target even at the lowest resolution, or that a lower
        // resolution did not help (CPU-bound), are too heavy for this device: optionally skip them
        // for good.
        boolean atFloor = !auto || current == minIndex || cpuBoundPreset == presetCount;
        if (skipSlowPresets && atFloor && fps < targetFps * SKIP_THRESHOLD) {
            if (++tooSlowSamples >= SKIP_SAMPLES && !switchRequested) {
                tooSlowSamples = 0;
                switchRequested = true;
                Log.w(TAG, "Preset too slow at the lowest resolution (" + fps + " fps)");
                return ACTION_SKIP;
            }
        } else {
            tooSlowSamples = 0;
        }
        if (!auto) return ACTION_NONE;

        // A preset that is limited by the CPU is not helped by a lower resolution: if the last
        // lowering gained less than 10%, go back up and leave the resolution for this preset.
        if (fpsBeforeLowering > 0) {
            float before = fpsBeforeLowering;
            fpsBeforeLowering = 0;
            if (fps < before * MIN_GAIN && loweredFrom > current) {
                failures[loweredFrom] = Math.max(0, failures[loweredFrom] - 1);  // the level was not too heavy
                blockedUntilPreset[loweredFrom] = 0;
                cpuBoundPreset = presetCount;
                apply(loweredFrom, "lower resolution did not help (" + before + " -> " + fps + " fps): CPU-bound");
                if (skipSlowPresets && fps < targetFps * SKIP_THRESHOLD && !switchRequested) {
                    // Far too slow, and the resolution is not the cause: no need to watch it longer.
                    switchRequested = true;
                    Log.w(TAG, "Preset too slow (" + fps + " fps), and a lower resolution does not help");
                    return ACTION_SKIP;
                }
                return ACTION_NONE;
            }
        }
        boolean mayLower = current > minIndex && cpuBoundPreset != presetCount;

        if (fps < targetFps * SEVERE_THRESHOLD) {
            if (++severeSamples >= SEVERE_SAMPLES && mayLower) {
                block(current);
                lower(stepDown(current), fps, "severe slowdown (" + fps + " fps)");
                return ACTION_NONE;
            }
        } else {
            severeSamples = 0;
        }

        if (fps < targetFps * DOWN_THRESHOLD) {
            goodSamples = 0;
            if (++slowSamples >= DOWN_SAMPLES && mayLower) {
                int to = stepDown(current);
                block(current);
                lower(to, fps, fps + " fps < target " + targetFps);
            }
        } else {
            slowSamples = 0;
            if (fps >= targetFps * UP_THRESHOLD && ++goodSamples >= UP_SAMPLES
                    && current < ceiling && presetCount >= blockedUntilPreset[current + 1]) {
                apply(current + 1, "headroom");
            }
        }
        return ACTION_NONE;
    }

    /**
     * Remembers that a level was too heavy. Presets differ a lot, so it is tried again from the next
     * preset on; a level that keeps failing waits longer each time (1, 2, 4, 8, at most 16 presets),
     * which stops back-and-forth switching without one heavy preset holding the resolution down.
     */
    private void block(int index) {
        failures[index]++;
        blockedUntilPreset[index] = presetCount + Math.min(MAX_BACKOFF_PRESETS, 1 << Math.min(4, failures[index] - 1));
    }

    /** Lowers now and remembers the frame rate, to check after settling that it helped. */
    private void lower(int index, float fps, String reason) {
        int from = current;
        apply(index, reason);
        loweredFrom = from;
        fpsBeforeLowering = fps;
    }

    /** Switches to a level now; the frame rate then settles before the next decision. */
    private void apply(int index, String reason) {
        if (index == current) return;
        Log.i(TAG, "Render height " + levels[current] + " -> " + levels[index] + ": " + reason);
        current = index;
        listener.onApplyRenderHeight(levels[current]);
        resetCounters(SETTLE_MS);
    }

    private int stepDown(int index) {
        // Drop two steps when far off target, so heavy scenes recover in one switch.
        int step = slowSamples >= DOWN_SAMPLES * 2 || severeSamples > 0 ? 2 : 1;
        return Math.max(minIndex, index - step);
    }

    private void resetCounters(long settleMs) {
        slowSamples = severeSamples = goodSamples = tooSlowSamples = 0;
        settleUntil = System.currentTimeMillis() + settleMs;
    }

    private int indexAtMost(int height) {
        int best = 0;
        for (int i = 0; i < levels.length; i++) if (levels[i] <= height) best = i;
        return best;
    }
}
