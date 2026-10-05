package nl.neerdael.projectm.core;

/** Pure conservative texture/headroom policy; estimates are not measured total process RAM. */
public final class RenderMemoryBudget {
    private static final long MIB = 1024L * 1024;
    private static final long RECOVERY_MARGIN = 64 * MIB;
    private RenderMemoryBudget() {}

    /**
     * Budget 32 bytes/native pixel/preset for ping-pong RGBA, flip, UV map, blur and
     * authored feedback textures, plus driver/surface allowance. Detail modes add 8 bytes
     * above the activation threshold for Hc and D. Both gains allocate the same textures.
     * Budget two complete presets whenever soft transitions are enabled.
     */
    public static long estimatedBytes(int width, int height, int trailsLevel, boolean blending) {
        long bytesPerPixel = trailsLevel > 0 && height > QualityController.RENDER_HEIGHT_CAP ? 40 : 32;
        return Math.max(0L, width) * Math.max(0L, height) * bytesPerPixel * (blending ? 2 : 1);
    }

    public static long reserveBytes(MemorySnapshot sample) {
        if (sample == null || !sample.isValid()) return Long.MAX_VALUE;
        return Math.max(sample.totalBytes / 5, sample.thresholdBytes + 128 * MIB);
    }

    /** Existing render RAM is already absent from availableBytes: only deduct growth. */
    public static boolean canGrow(MemorySnapshot sample, long currentBytes, long candidateBytes) {
        if (sample == null || !sample.isValid() || sample.lowMemory) return false;
        long growth = Math.max(0, candidateBytes - currentBytes);
        // Conservative extra half-candidate allowance for resize/copy/driver overlap.
        long projectedAvailable = sample.availableBytes - growth - candidateBytes / 2;
        return projectedAvailable >= reserveBytes(sample) + RECOVERY_MARGIN;
    }

    public static boolean hasRecoveryHeadroom(MemorySnapshot sample) {
        return sample != null && sample.isValid() && !sample.lowMemory
                && sample.availableBytes >= reserveBytes(sample) + RECOVERY_MARGIN;
    }

    public static boolean isUnderPressure(MemorySnapshot sample) {
        return sample != null && sample.isValid()
                && (sample.lowMemory || sample.availableBytes < reserveBytes(sample));
    }

    public static boolean canRecoverByShrinking(MemorySnapshot sample, long currentBytes, long candidateBytes) {
        if (sample == null || !sample.isValid()) return false;
        long released = Math.max(0, currentBytes - candidateBytes);
        return sample.availableBytes + released >= reserveBytes(sample) + RECOVERY_MARGIN;
    }
}
