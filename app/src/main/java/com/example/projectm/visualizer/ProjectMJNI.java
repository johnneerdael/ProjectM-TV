package com.example.projectm.visualizer;

import android.content.res.AssetManager;
import android.util.Log;

/**
 * Bindings to the native engine (native-lib.cpp).
 *
 * The surface/frame/release methods must be called on the GL thread. All other methods are
 * thread-safe: they only record a request that the GL thread applies on its next frame.
 */
public final class ProjectMJNI {
    private static final String TAG = "ProjectMJNI";

    static {
        try {
            System.loadLibrary("projectmtv");
        } catch (UnsatisfiedLinkError e) {
            Log.e(TAG, "Failed to load projectmtv library", e);
        }
    }

    private ProjectMJNI() {}

    /** Starts background indexing of the presets bundled in the APK. Safe to call repeatedly. */
    public static native void init(AssetManager assets, String skipListPath);

    // GL thread only
    public static native void onSurfaceCreated();
    public static native void onSurfaceChanged(int width, int height);
    public static native void onDrawFrame();
    public static native void release();

    // Any thread
    /** Raw Visualizer waveform: 8-bit unsigned mono PCM. */
    public static native void addWaveform(byte[] waveform, int length);
    public static native void nextPreset(boolean hardCut);
    public static native void previousPreset(boolean hardCut);
    public static native void randomPreset(boolean hardCut);
    public static native void setPresetDuration(int seconds);
    public static native void setSoftCutDuration(int seconds);
    public static native void setAutoChange(boolean enabled);
    public static native void setMeshSize(int width, int height);
    /** Adds the current preset to the skip list and moves on (hard cut). */
    public static native void skipCurrentPreset();
    /** Enables skipping of presets that render nothing while music plays. */
    public static native void setBlankDetection(boolean enabled);
    /** Makes the next automatic preset switch a hard cut (used before resolution changes). */
    public static native void setForceHardCut(boolean enabled);
    /** Reads an Android system property ("" if unset or not readable). */
    public static native String getSystemProperty(String name);
    public static native String getCurrentPresetName();
    /** Increments every time a new preset is shown. */
    public static native int getPresetChangeCounter();
    public static native int getPresetCount();
    public static native int getSkippedCount();
    public static native void resetSkippedPresets();
    public static native String getVersion();
}
