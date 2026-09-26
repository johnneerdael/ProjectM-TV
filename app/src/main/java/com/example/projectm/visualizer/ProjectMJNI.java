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

    /**
     * projectM's blend, rendered below the render resolution (75% to start) and adapted to keep
     * the frame rate: lower when a blend drops frames, higher when blends have frames to spare.
     */
    public static final int TRANSITION_AUTO = 0;
    /** projectM hard-cuts; the last frame of the old preset fades out on top (cheap). */
    public static final int TRANSITION_LIGHTWEIGHT = 1;
    /** projectM's own blend at the full render resolution: both presets render for the whole transition. */
    public static final int TRANSITION_CLASSIC = 2;

    private ProjectMJNI() {}

    /**
     * Starts background work: copies the bundled texture pack to {@code textureDir} (projectM only
     * loads textures from real folders) and indexes the presets. Safe to call repeatedly.
     */
    public static native void init(AssetManager assets, String skipListPath, String textureDir);

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
    /** projectM's hard cut to the next preset on a loud beat (off: presets only change by blending). */
    public static native void setBeatCuts(boolean enabled);
    /** Memory runs low: pauses compiling upcoming presets in the background for a minute. */
    public static native void onMemoryPressure();
    public static native void setMeshSize(int width, int height);
    /** Adds the current preset to the skip list and moves on (hard cut). */
    public static native void skipCurrentPreset();
    /**
     * Enables skipping of presets that stay black while music plays. Off by default: output is
     * always measured and logged, but only skipped on request.
     */
    public static native void setBlankDetection(boolean enabled);
    /** Transition mode: {@link #TRANSITION_AUTO}, {@link #TRANSITION_LIGHTWEIGHT} or {@link #TRANSITION_CLASSIC}. */
    /** @param lowEndDevice Auto's blends start at a lower resolution. */
    public static native void setTransitionMode(int mode, boolean lowEndDevice);
    /** Resolution of Auto's blends in percent of the render resolution, 0 before the first blend. */
    public static native int getBlendScalePercent();
    /** True when automatic preset switches currently use the lightweight transition. */
    public static native boolean isLightweightTransition();
    /** Makes the next automatic preset switch a hard cut (used before resolution changes). */
    public static native void setForceHardCut(boolean enabled);
    /** Reads an Android system property ("" if unset or not readable). */
    public static native String getSystemProperty(String name);
    public static native String getCurrentPresetName();
    /** Recent audio input level (RMS, 0..1); 0 if no audio arrived in the last second. */
    public static native float getAudioLevel();
    /** Increments every time a new preset is shown. */
    public static native int getPresetChangeCounter();
    public static native int getPresetCount();
    /** Increments when a transition finishes; see {@link #getLastTransitionFps()}. */
    public static native int getTransitionCounter();
    /** Average FPS over the last transition, including the preset-load stall. */
    public static native float getLastTransitionFps();
    public static native int getSkippedCount();
    public static native void resetSkippedPresets();
    public static native String getVersion();
}
