package nl.neerdael.projectmtv.corpus;

/** Private corpus controls exported only by an instrumented, actual ProjectM core AAR. */
public final class LabBridge {
    static { System.loadLibrary("projectmtv"); }
    private LabBridge() {}
    public static native void initialize(long seed, int referenceWidth, int referenceHeight);
    public static native void setFrameClock(double seconds);
}
