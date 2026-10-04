package nl.neerdael.projectm.corecorpus;

final class LabBridge {
    static { System.loadLibrary("projectmtv"); }
    static native void configureSeed(int seed);
    static native void setClock(double seconds);
    static native void prepareDefaultReadBuffer();
    static native byte[] captureRgba(int width, int height);
    static native void clearDefaultFramebuffer();
    static native int glError();
    static native String glInfo();
}
