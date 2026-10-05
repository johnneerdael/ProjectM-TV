package nl.neerdael.projectm.core;

/** Supplies current system memory on the controller's existing one-second stats callback. */
public interface MemoryProvider {
    /** Return null when a reliable sample is unavailable. */
    MemorySnapshot sample();
}
