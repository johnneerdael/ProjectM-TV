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
 * Automatic resolution can reach the physical panel when FPS and live memory headroom allow
 * it. Memory warnings lower a temporary ceiling, released after sustained healthy headroom.
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

    /** @deprecated Compatibility threshold used to activate native trails, not an Auto cap. */
    @Deprecated
    public static final int RENDER_HEIGHT_CAP = 1330;

    /** Native selection sentinel; legacy setMode still normalizes it to Auto. */
    public static final int NATIVE_HEIGHT = -1;

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
    private final DisplayInfo display;
    private final MemoryProvider memoryProvider;
    private final int initialIndex;
    private MemorySnapshot memorySnapshot;
    private int nativeTrailsLevel;
    private long allocationBytesBeforeSettings;
    private boolean memoryConstrained;
    private boolean lastChangeForMemoryPressure;
    private int healthyMemorySamples;
    private boolean started;
    // Until a confirmed rendered FPS sample, available memory still includes resources to allocate.
    private boolean fullAllocationPending;
    private int resolutionMode;     // 0 Auto, -1 Native, positive fixed height
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
    private int ceiling;                     // temporary highest level Auto may use
    private long pressureQuietUntil;
    private float fpsBeforeLowering;         // > 0: judge whether the last lowering helped
    private int loweredFrom = -1;            // level before the last lowering
    private int cpuBoundPreset = -1;         // preset for which a lower resolution did not help
    private int beforePressure = -1;         // auto level when memory pressure first lowered the ceiling

    /** Legacy memoryLimit is ignored; live memory headroom controls automatic resolution. */
    public QualityController(DisplayInfo display, DeviceProfile profile, int memoryLimit, Listener listener) {
        this(display, profile, memoryLimit, listener, ProjectMCore.memoryProvider());
    }

    /** Injectable memory sampling for hosts/tests; null samples prohibit growth. */
    public QualityController(DisplayInfo display, DeviceProfile profile, int memoryLimit,
                             Listener listener, MemoryProvider memoryProvider) {
        this.listener = listener;
        this.display = display;
        this.memoryProvider = memoryProvider;
        List<Integer> usable = new ArrayList<>();
        int maxHeight = display.physicalHeight;
        for (int h : AUTO_LADDER) if (h <= maxHeight) usable.add(h);
        if (usable.isEmpty() || usable.get(usable.size() - 1) < maxHeight) usable.add(maxHeight);
        levels = new int[usable.size()];
        for (int i = 0; i < levels.length; i++) levels[i] = usable.get(i);
        blockedUntilPreset = new int[levels.length];
        failures = new int[levels.length];
        minIndex = indexAtMost(profile.minAutoHeight());
        initialIndex = Math.max(minIndex, indexAtMost(profile.initialAutoHeight()));
        current = initialIndex;
        ceiling = levels.length - 1;
    }

    /** @deprecated All hosts start in Auto, regardless of legacy memory settings. */
    @Deprecated
    public static int defaultMode(DisplayInfo display, int memoryLimit) { return 0; }

    /** @deprecated Resolution is automatic; no manual choices remain. */
    @Deprecated
    public static int[] manualHeights(DisplayInfo display, int memoryLimit) { return new int[0]; }

    /** @deprecated Every saved fixed/native preference becomes Auto. */
    @Deprecated
    public static int validFixedHeight(DisplayInfo display, int memoryLimit, int savedHeight) { return 0; }

    /** Explicit menu choices: Auto, standard heights supported by the panel, and Native. */
    public static int[] resolutionModes(DisplayInfo display) {
        List<Integer> modes = new ArrayList<>();
        modes.add(0);
        for (int height : new int[]{720, 1080, 1440, 2160}) {
            if (height <= display.physicalHeight) modes.add(height);
        }
        modes.add(NATIVE_HEIGHT);
        int[] result = new int[modes.size()];
        for (int i = 0; i < result.length; i++) result[i] = modes.get(i);
        return result;
    }

    /** Reject unsupported saved choices after a display change. */
    public static int validResolutionMode(DisplayInfo display, int mode) {
        for (int choice : resolutionModes(display)) if (choice == mode) return mode;
        return 0;
    }

    /**
     * Opt-in resolution selector. Fixed/Native ignore FPS downshifts and slow-preset skipping,
     * but retain live memory checks; the actual height can temporarily be below the selection.
     * Legacy setMode keeps its Auto-only contract for existing embedding apps.
     */
    public void setResolutionMode(int mode, int lastAutoHeight) {
        int normalized = validResolutionMode(display, mode);
        if (resolutionMode != normalized) beforePressure = -1;
        resolutionMode = normalized;
        startMode(lastAutoHeight);
    }

    /** @deprecated height is ignored; lastAutoHeight is a remembered automatic starting point. */
    @Deprecated
    public void setMode(int height, int lastAutoHeight) {
        if (resolutionMode != 0) beforePressure = -1;
        resolutionMode = 0;
        startMode(lastAutoHeight);
    }

    private void startMode(int lastAutoHeight) {
        fullAllocationPending = true;
        resetAllocationProbe();
        resetCounters(0);
        memorySnapshot = sampleMemory();
        int wanted = !isAuto() ? selectedIndex()
                : lastAutoHeight > 0 ? indexAtMost(lastAutoHeight) : initialIndex;
        wanted = Math.max(minIndex, Math.min(ceiling, wanted));
        current = wanted;
        if (memorySnapshot == null || !memorySnapshot.isValid()) {
            current = Math.min(current, initialIndex);
            memoryConstrained = true;
        } else {
            while (current > minIndex && !RenderMemoryBudget.canGrow(memorySnapshot, 0, estimate(current))) current--;
            memoryConstrained = current < wanted || !RenderMemoryBudget.hasRecoveryHeadroom(memorySnapshot);
        }
        lastChangeForMemoryPressure = false;
        started = true;
        listener.onApplyRenderHeight(currentHeight());
    }

    /**
     * Revalidate before visibility/rendering resumes and before the first draw in a new GL
     * context. A recreated context needs the full replacement allocation; a preserved context
     * already contributes to Android's available-memory reading. Always publish the chosen
     * height, even unchanged, so the host can acknowledge its paused render configuration.
     */
    public void revalidateForResume(boolean contextRecreated) {
        if (contextRecreated) fullAllocationPending = true;
        memorySnapshot = sampleMemory();
        resetAllocationProbe();
        int to = current;
        if (memorySnapshot == null || !memorySnapshot.isValid()) {
            // Missing data cannot authorize reusing/rebuilding an expensive saved allocation.
            to = minIndex;
        } else if (fullAllocationPending) {
            while (to > minIndex && !RenderMemoryBudget.canGrow(memorySnapshot, 0, estimate(to))) to--;
        } else if (!RenderMemoryBudget.hasRecoveryHeadroom(memorySnapshot)) {
            to = Math.max(minIndex, current - (memorySnapshot.lowMemory ? 2 : 1));
            while (to > minIndex && !RenderMemoryBudget.canRecoverByShrinking(
                    memorySnapshot, estimate(current), estimate(to))) to--;
        }
        if (to < current) {
            pressureQuietUntil = System.currentTimeMillis() + PRESSURE_QUIET_MS;
            constrainTo(to); // Publishes exactly once before the host releases its render guard.
        } else {
            memoryConstrained = ceiling < levels.length - 1
                    || !RenderMemoryBudget.hasRecoveryHeadroom(memorySnapshot)
                    || (fullAllocationPending && !RenderMemoryBudget.canGrow(memorySnapshot, 0, estimate(to)));
            listener.onApplyRenderHeight(currentHeight());
        }
    }

    /**
     * Publish a changed allocation tuple after the host invalidates its old FPS generation.
     * Growth and unconfirmed allocations require a fresh budget. A confirmed reduction keeps
     * its height until GL releases the old textures; the next completed-generation FPS sample
     * then checks actual available memory. Visibility resumes still use revalidateForResume.
     */
    public void revalidateForAllocationChange() {
        // The setter can lower current and invoke the host listener before it returns. Compare
        // the resulting tuple against the allocation captured before that edit/height change.
        boolean growing = estimate(current) > allocationBytesBeforeSettings;
        if (growing || fullAllocationPending) {
            revalidateForResume(growing);
        } else {
            resetAllocationProbe();
            listener.onApplyRenderHeight(currentHeight());
        }
    }

    private void resetAllocationProbe() {
        healthyMemorySamples = 0;
        fpsBeforeLowering = 0;
        loweredFrom = -1;
        cpuBoundPreset = -1;
        lastChangeForMemoryPressure = false;
        resetCounters(SETTLE_MS);
    }

    /** Standard=0, Medium=1, High=2. Medium and High allocate the same detail textures. */
    public void setNativeTrailsLevel(int level) {
        setRenderAllocationSettings(level, (int) (transitionMs / 1000L));
    }

    /** Review the final allocation tuple, avoiding intermediate growth in opposite-field edits. */
    public void setRenderAllocationSettings(int trailsLevel, int transitionSeconds) {
        allocationBytesBeforeSettings = estimate(current);
        nativeTrailsLevel = Math.max(0, Math.min(2, trailsLevel));
        transitionMs = Math.max(0, transitionSeconds) * 1000L;
        recheckBudgetGrowth(allocationBytesBeforeSettings);
    }

    public boolean isMemoryConstrained() { return memoryConstrained; }

    /** Read inside the height listener to clear native caches once per memory downshift. */
    public boolean wasLastChangeForMemoryPressure() { return lastChangeForMemoryPressure; }

    public void setTargetFps(float fps) {
        targetFps = fps;
        resetCounters(SETTLE_MS);
    }

    public void setSkipSlowPresets(boolean enabled) {
        skipSlowPresets = enabled;
        tooSlowSamples = 0;
    }

    public void setTransitionSeconds(int seconds) {
        setRenderAllocationSettings(nativeTrailsLevel, seconds);
    }

    public boolean isAuto() { return resolutionMode == 0; }

    /** Whether the explicit Native selection follows the physical panel. */
    public boolean isNative() { return resolutionMode == NATIVE_HEIGHT; }

    private int selectedIndex() {
        return isNative() ? levels.length - 1 : indexAtMost(resolutionMode);
    }

    public int currentHeight() { return levels[current]; }

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

    /** Android foreground memory trim: normal warnings debounce, critical ones act immediately. */
    public void onMemoryPressure(int level) {
        long now = System.currentTimeMillis();
        // ComponentCallbacks2.TRIM_MEMORY_RUNNING_CRITICAL=15; older BACKGROUND/COMPLETE
        // warnings >=40 also warrant immediate relief.
        boolean critical = level == 15 || level >= 40;
        if (now < pressureQuietUntil && !critical) return;
        pressureQuietUntil = now + PRESSURE_QUIET_MS;
        constrainTo(Math.max(minIndex, current - (critical ? 2 : 1)));
    }

    private MemorySnapshot sampleMemory() {
        try { return memoryProvider == null ? null : memoryProvider.sample(); }
        catch (RuntimeException unavailable) { return null; }
    }

    private long estimate(int index) {
        int height = levels[index];
        return RenderMemoryBudget.estimatedBytes(display.widthForHeight(height), height,
                nativeTrailsLevel, transitionMs > 0);
    }

    /** Settings may allocate detail textures or a second live preset without a height change. */
    private void recheckBudgetGrowth(long beforeBytes) {
        if (!started || estimate(current) <= beforeBytes) return;
        memorySnapshot = sampleMemory();
        long residentBytes = fullAllocationPending ? 0 : beforeBytes;
        if (RenderMemoryBudget.canGrow(memorySnapshot, residentBytes, estimate(current))) return;
        int to = current;
        do { to--; } while (to > minIndex && !RenderMemoryBudget.canGrow(
                memorySnapshot, residentBytes, estimate(to)));
        pressureQuietUntil = System.currentTimeMillis() + PRESSURE_QUIET_MS;
        constrainTo(Math.max(minIndex, to));
    }

    private void constrainTo(int index) {
        memoryConstrained = true;
        healthyMemorySamples = 0;
        if (beforePressure < 0) beforePressure = current;
        ceiling = Math.min(ceiling, index);
        fpsBeforeLowering = 0;
        if (current > ceiling) {
            apply(ceiling, "live memory headroom", true);
        }
    }

    private void updateMemory() {
        memorySnapshot = sampleMemory();
        if (RenderMemoryBudget.isUnderPressure(memorySnapshot)) {
            memoryConstrained = true;
            healthyMemorySamples = 0;
            long now = System.currentTimeMillis();
            if (now < pressureQuietUntil && !memorySnapshot.lowMemory) return;
            int to = Math.max(minIndex, current - (memorySnapshot.lowMemory ? 2 : 1));
            while (to > minIndex && !RenderMemoryBudget.canRecoverByShrinking(
                    memorySnapshot, estimate(current), estimate(to))) to--;
            pressureQuietUntil = now + PRESSURE_QUIET_MS;
            constrainTo(to);
        } else if (RenderMemoryBudget.hasRecoveryHeadroom(memorySnapshot)) {
            if (++healthyMemorySamples >= 3 && System.currentTimeMillis() >= pressureQuietUntil) {
                ceiling = levels.length - 1;
                beforePressure = -1;
                memoryConstrained = false;
            }
        } else {
            healthyMemorySamples = 0;
            memoryConstrained = true;
        }
    }

    private boolean canGrowTo(int index) {
        boolean allowed = healthyMemorySamples >= 3 && index <= ceiling && RenderMemoryBudget.canGrow(memorySnapshot,
                estimate(current), estimate(index));
        if (!allowed) memoryConstrained = true;
        return allowed;
    }

    /**
     * One-second sample from a confirmed rendered context/configuration; the host must discard
     * stale or render-guarded callbacks. Samples memory even during preset/FPS settling.
     */
    public int onFpsSample(float fps) {
        updateMemory();
        if (fps > 0) fullAllocationPending = false;
        if (System.currentTimeMillis() < settleUntil || fps <= 0) return ACTION_NONE;
        if (!isAuto()) {
            // Memory relief may lower a selected size. Restore it only after healthy samples,
            // bounded by the selection, independent of FPS and automatic preset backoff.
            int wanted = Math.min(selectedIndex(), ceiling);
            if (current < wanted && canGrowTo(current + 1)) {
                apply(current + 1, "selected resolution restored after memory relief");
            }
            return ACTION_NONE;
        }

        // Presets that stay far below target even at the lowest resolution, or that a lower
        // resolution did not help (CPU-bound), are too heavy for this device: optionally skip them
        // for good.
        boolean atFloor = current == minIndex || cpuBoundPreset == presetCount;
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

        // A preset that is limited by the CPU is not helped by a lower resolution: if the last
        // lowering gained less than 10%, go back up and leave the resolution for this preset.
        if (fpsBeforeLowering > 0) {
            float before = fpsBeforeLowering;
            fpsBeforeLowering = 0;
            if (fps < before * MIN_GAIN && loweredFrom > current && canGrowTo(loweredFrom)) {
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
            if (fps >= targetFps * UP_THRESHOLD && current < ceiling
                    && presetCount >= blockedUntilPreset[current + 1] && canGrowTo(current + 1)) {
                if (++goodSamples >= UP_SAMPLES) apply(current + 1, "headroom");
            } else {
                goodSamples = 0;
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
        apply(index, reason, false);
    }

    private void apply(int index, String reason, boolean forMemoryPressure) {
        if (index == current) return;
        Log.i(TAG, "Render height " + levels[current] + " -> " + levels[index] + ": " + reason);
        current = index;
        lastChangeForMemoryPressure = forMemoryPressure;
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
