package com.example.projectm.visualizer;

import android.util.Log;

import java.util.ArrayList;
import java.util.List;

/**
 * Dynamic resolution: picks the render height from a ladder of levels so the frame rate stays at
 * its target, and raises it again when there is headroom.
 *
 * Changing the render size resets projectM's framebuffers ("Calling this function will reset the
 * OpenGL renderer", parameters.h), so changes are only applied right after a preset switch, which
 * is then forced to be a hard cut: the new preset starts from scratch anyway, so the reset is not
 * visible. Only a severe, sustained slowdown triggers an immediate change (with a preset switch).
 *
 * Memory: running out is a short peak, not a steady state. At a preset switch two presets'
 * frame buffers exist at once, and a resize reallocates them. So there is no fixed cap: Auto
 * only goes up (or starts high) when Android's free memory covers the estimated extra memory
 * of the higher level including a switch, and when Android reports memory pressure it steps
 * down one level for {@link #PRESSURE_BACKOFF_PRESETS} presets, then may climb again.
 *
 * Heavy presets: presets.idx gives every preset a weight (estimated extra MB for its images and
 * complex shaders, see tools/gen-preset-index.py). {@link #heightForNextPreset} lowers the
 * resolution for the upcoming preset only when free memory cannot hold its switch peak plus its
 * weight; the engine resizes before loading it and goes back up for the next normal preset.
 *
 * All methods run on the UI thread.
 */
public final class QualityController {
    private static final String TAG = "QualityController";

    public interface Listener {
        void onApplyRenderHeight(int height);
    }

    /** Free memory before Android starts killing apps (bytes), or a negative value if unknown. */
    public interface MemoryProbe {
        long headroomBytes();
    }

    /** Result of {@link #onFpsSample}. */
    public static final int ACTION_NONE = 0;
    /** Switch preset now (hard cut) so a severe downgrade can be applied. */
    public static final int ACTION_SWITCH = 1;
    /** Current preset is too slow for this device even at the lowest resolution: skip it. */
    public static final int ACTION_SKIP = 2;

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
    /**
     * Estimated bytes per rendered pixel. Each projectM preset holds two RGBA8 frame buffers and an
     * RG16F motion-vector map plus smaller blur buffers (~13 B/px); the window surface has up to
     * three RGBA8 buffers (12 B/px). During a switch two presets exist at once.
     */
    static final long PRESET_BYTES_PER_PIXEL = 13;
    static final long SURFACE_BYTES_PER_PIXEL = 12;
    static final long MEMORY_MARGIN_BYTES = 64L << 20;
    static final int PRESSURE_BACKOFF_PRESETS = 10;

    private final Listener listener;
    private final MemoryProbe memory;
    private final DisplayInfo display;
    private final int[] levels;
    private final int minIndex;
    private boolean auto;
    private int fixedHeight;
    private int current;            // index into levels (auto mode)
    private int pending = -1;       // level to apply at the next preset switch
    private float targetFps = 60f;
    private long settleUntil;
    private long transitionMs;
    private int slowSamples, severeSamples, goodSamples, tooSlowSamples;
    private boolean skipSlowPresets;
    private boolean switchRequested;  // immediate switch asked for, waiting for onPresetChanged
    private final int[] blockedUntilPreset;  // per level: don't retry until this preset count
    private final int[] failures;            // per level: exponential back-off after failed probes
    private int presetCount;
    private int pressureCeiling = Integer.MAX_VALUE;  // level index auto may not exceed ...
    private int pressureUntilPreset;                  // ... until this preset count
    private int pressurePreset = -1;
    private boolean started;                          // first setMode (launch) done
    private int shownHeight;                          // render height in use (lower for a heavy preset)

    public QualityController(DisplayInfo display, DeviceProfile profile, MemoryProbe memory, Listener listener) {
        this.listener = listener;
        this.memory = memory;
        this.display = display;
        List<Integer> usable = new ArrayList<>();
        int maxHeight = display.physicalHeight;
        for (int h : AUTO_LADDER) if (h <= maxHeight) usable.add(h);
        if (usable.isEmpty() || usable.get(usable.size() - 1) < maxHeight) usable.add(maxHeight);
        levels = new int[usable.size()];
        for (int i = 0; i < levels.length; i++) levels[i] = usable.get(i);
        blockedUntilPreset = new int[levels.length];
        failures = new int[levels.length];
        minIndex = indexAtMost(profile.minAutoHeight());
        current = indexAtMost(profile.initialAutoHeight());
    }

    /** Levels available for manual selection in the menu (ascending heights). */
    public static int[] manualHeights(DisplayInfo display) {
        int maxHeight = display.physicalHeight;
        List<Integer> list = new ArrayList<>();
        for (int h : new int[]{720, 1080, 1440, 2160}) if (h <= maxHeight) list.add(h);
        if (list.isEmpty() || list.get(list.size() - 1) < maxHeight) list.add(maxHeight);
        int[] result = new int[list.size()];
        for (int i = 0; i < result.length; i++) result[i] = list.get(i);
        return result;
    }

    /**
     * Returns {@code savedHeight} if it is still a valid fixed level for this panel, otherwise 0
     * (automatic). A saved 2160 must not be used after the device moved to a 1080p panel.
     */
    public static int validFixedHeight(DisplayInfo display, int savedHeight) {
        for (int h : manualHeights(display)) if (h == savedHeight) return savedHeight;
        return 0;
    }

    /** @param height 0 for automatic, otherwise a fixed render height. */
    public void setMode(int height, int lastAutoHeight) {
        auto = height <= 0;
        fixedHeight = height;
        pending = -1;
        resetCounters(0);
        if (auto) {
            if (lastAutoHeight > 0) current = Math.max(minIndex, indexAtMost(lastAutoHeight));
            // At launch nothing is allocated yet, so the whole level has to fit; later (switching
            // back to Auto) the current buffers already exist and only the difference counts.
            while (current > minIndex && !(started ? memoryAllows(current, current - 1) : memoryAllowsStart(current))) {
                current--;
            }
        }
        started = true;
        listener.onApplyRenderHeight(currentHeight());
    }

    public void setTargetFps(float fps) {
        targetFps = fps;
        pending = -1;  // a queued change was computed against the old target
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

    /** True while a change waits for the next preset switch (which should then be a hard cut). */
    public boolean hasPendingChange() {
        return pending >= 0 && pending != current;
    }

    /** Called when a new preset starts. */
    public void onPresetChanged() {
        presetCount++;
        switchRequested = false;
        if (auto && hasPendingChange()) {
            Log.i(TAG, "Render height " + levels[current] + " -> " + levels[pending] + " at preset switch");
            current = pending;
        }
        pending = -1;
        resetCounters(SETTLE_MS + transitionMs);
    }

    /** The render height actually in use changed (auto level, heavy preset or fixed). */
    public void setShownHeight(int height) {
        shownHeight = height;
    }

    /**
     * Render height for the preset the next automatic switch loads: the auto level (or the pending
     * change), lowered only while free memory cannot hold that switch: a second preset's frame
     * buffers plus the preset's weight. 0 in fixed mode, where the user's choice applies.
     *
     * @param weightMb the upcoming preset's weight from presets.idx (negative: unknown)
     */
    public int heightForNextPreset(int weightMb) {
        if (!auto) return 0;
        int level = pending >= 0 ? pending : current;
        while (level > minIndex && !fitsSwitch(level, Math.max(0, weightMb))) level--;
        return levels[level];
    }

    private boolean fitsSwitch(int level, int weightMb) {
        if (memory == null) return true;
        long headroom = memory.headroomBytes();
        if (headroom < 0) return true;
        long pixels = (long) display.widthForHeight(levels[level]) * levels[level];
        long shown = shownHeight > 0 ? (long) display.widthForHeight(shownHeight) * shownHeight : pixels;
        long needed = Math.max(0, pixels - shown) * (PRESET_BYTES_PER_PIXEL + SURFACE_BYTES_PER_PIXEL)
                + pixels * PRESET_BYTES_PER_PIXEL + ((long) weightMb << 20) + MEMORY_MARGIN_BYTES;
        return headroom >= needed;
    }

    /**
     * Android reports that memory is running low while we are in the foreground: other apps (such
     * as the music player) are about to be killed. Lowers the automatic resolution one level at
     * the next preset switch and stays at or below it for {@link #PRESSURE_BACKOFF_PRESETS}
     * presets; after that the free-memory check decides again.
     */
    public void onMemoryPressure(int level) {
        if (!auto) {
            Log.w(TAG, "Memory pressure (level " + level + ") at fixed " + fixedHeight + "p");
            return;
        }
        if (presetCount == pressurePreset) return;  // one step per preset: it applies at the switch
        pressurePreset = presetCount;
        int from = pending >= 0 ? Math.min(current, pending) : current;
        pressureCeiling = Math.max(minIndex, from - 1);
        pressureUntilPreset = presetCount + PRESSURE_BACKOFF_PRESETS;
        if (current > pressureCeiling) pending = pressureCeiling;
        Log.w(TAG, "Memory pressure (level " + level + "): at most " + levels[pressureCeiling]
                + " for the next " + PRESSURE_BACKOFF_PRESETS + " presets");
    }

    /** True if Android's free memory covers starting at a level: surface plus two presets at a switch. */
    private boolean memoryAllowsStart(int level) {
        long pixels = (long) display.widthForHeight(levels[level]) * levels[level];
        return enoughFree(levels[level], pixels * (2 * PRESET_BYTES_PER_PIXEL + SURFACE_BYTES_PER_PIXEL)
                + MEMORY_MARGIN_BYTES);
    }

    /**
     * True if Android's free memory covers going from level {@code from} to {@code to}: the extra
     * frame buffers and surface of the bigger size, plus a second preset during a switch.
     * Unknown free memory never blocks.
     */
    private boolean memoryAllows(int to, int from) {
        long pixelsTo = (long) display.widthForHeight(levels[to]) * levels[to];
        long pixelsFrom = (long) display.widthForHeight(levels[from]) * levels[from];
        return enoughFree(levels[to], Math.max(0, pixelsTo - pixelsFrom) * (PRESET_BYTES_PER_PIXEL + SURFACE_BYTES_PER_PIXEL)
                + pixelsTo * PRESET_BYTES_PER_PIXEL + MEMORY_MARGIN_BYTES);
    }

    private boolean enoughFree(int height, long needed) {
        if (memory == null) return true;
        long headroom = memory.headroomBytes();
        if (headroom < 0 || headroom >= needed) return true;
        Log.i(TAG, "Not enough free memory for " + height + " (needs ~" + (needed >> 20) + " MB, "
                + (headroom >> 20) + " MB free)");
        return false;
    }

    /** One-second frame-rate sample; returns one of the ACTION_ constants. */
    public int onFpsSample(float fps) {
        if (System.currentTimeMillis() < settleUntil || fps <= 0) return ACTION_NONE;

        // Presets that stay far below target even at the lowest resolution are CPU-bound or
        // simply too heavy for this device: optionally skip them for good.
        boolean atFloor = !auto || current == minIndex;
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
        // A heavy preset running at a reduced height says nothing about the auto level.
        if (shownHeight > 0 && shownHeight != levels[current]) return ACTION_NONE;

        if (fps < targetFps * SEVERE_THRESHOLD) {
            if (++severeSamples >= SEVERE_SAMPLES && current > minIndex && !switchRequested) {
                Log.w(TAG, "Severe slowdown (" + fps + " fps), lowering resolution now");
                block(current);
                pending = stepDown(current);
                switchRequested = true;
                return ACTION_SWITCH;
            }
        } else {
            severeSamples = 0;
        }

        if (fps < targetFps * DOWN_THRESHOLD) {
            goodSamples = 0;
            if (++slowSamples >= DOWN_SAMPLES && current > minIndex && pending < 0) {
                pending = stepDown(current);
                block(current);
                Log.i(TAG, fps + " fps < target " + targetFps + ": will lower to " + levels[pending]);
            }
        } else {
            slowSamples = 0;
            boolean pressureOver = presetCount >= pressureUntilPreset;
            if (fps >= targetFps * UP_THRESHOLD && ++goodSamples >= UP_SAMPLES
                    && current < levels.length - 1 && pending < 0
                    && (pressureOver || current < pressureCeiling)
                    && presetCount >= blockedUntilPreset[current + 1]) {
                goodSamples = 0;
                if (!memoryAllows(current + 1, current)) return ACTION_NONE;
                pending = current + 1;
                Log.i(TAG, "Headroom at " + levels[current] + ": will try " + levels[pending]);
            }
        }
        return ACTION_NONE;
    }

    /**
     * Remembers that a level was too heavy: retry once after 10 presets; after a second failure it
     * is not tried again in this session (each attempt reallocates all frame buffers).
     */
    private void block(int index) {
        failures[index]++;
        blockedUntilPreset[index] = failures[index] >= 2 ? Integer.MAX_VALUE : presetCount + 10;
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
