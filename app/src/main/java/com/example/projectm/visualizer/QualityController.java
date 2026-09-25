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
 * All methods run on the UI thread.
 */
public final class QualityController {
    private static final String TAG = "QualityController";

    public interface Listener {
        void onApplyRenderHeight(int height);
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

    private final Listener listener;
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

    public QualityController(DisplayInfo display, DeviceProfile profile, Listener listener) {
        this.listener = listener;
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
        List<Integer> list = new ArrayList<>();
        for (int h : new int[]{720, 1080, 1440, 2160}) if (h <= display.physicalHeight) list.add(h);
        if (list.isEmpty() || list.get(list.size() - 1) < display.physicalHeight) list.add(display.physicalHeight);
        int[] result = new int[list.size()];
        for (int i = 0; i < result.length; i++) result[i] = list.get(i);
        return result;
    }

    /** @param height 0 for automatic, otherwise a fixed render height. */
    public void setMode(int height, int lastAutoHeight) {
        auto = height <= 0;
        fixedHeight = height;
        pending = -1;
        resetCounters(0);
        if (auto && lastAutoHeight > 0) current = Math.max(minIndex, indexAtMost(lastAutoHeight));
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
            listener.onApplyRenderHeight(levels[current]);
        }
        pending = -1;
        resetCounters(SETTLE_MS + transitionMs);
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
            if (fps >= targetFps * UP_THRESHOLD && ++goodSamples >= UP_SAMPLES
                    && current < levels.length - 1 && pending < 0
                    && presetCount >= blockedUntilPreset[current + 1]) {
                pending = current + 1;
                Log.i(TAG, "Headroom at " + levels[current] + ": will try " + levels[pending]);
            }
        }
        return ACTION_NONE;
    }

    /** Remembers that a level was too heavy: retry after 3, 6, 12 ... (max 48) presets. */
    private void block(int index) {
        failures[index] = Math.min(failures[index] + 1, 5);
        blockedUntilPreset[index] = presetCount + (3 << (failures[index] - 1));
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
