package nl.neerdael.projectm.core;

/** Immutable Android system-memory sample, in bytes. Available memory includes this process. */
public final class MemorySnapshot {
    public final long totalBytes;
    public final long availableBytes;
    public final long thresholdBytes;
    public final boolean lowMemory;

    public MemorySnapshot(long totalBytes, long availableBytes, long thresholdBytes, boolean lowMemory) {
        this.totalBytes = totalBytes;
        this.availableBytes = availableBytes;
        this.thresholdBytes = thresholdBytes;
        this.lowMemory = lowMemory;
    }

    public boolean isValid() {
        return totalBytes > 0 && availableBytes >= 0 && availableBytes <= totalBytes
                && thresholdBytes >= 0 && thresholdBytes <= totalBytes;
    }
}
