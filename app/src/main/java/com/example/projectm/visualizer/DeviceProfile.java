package com.example.projectm.visualizer;

import android.app.ActivityManager;
import android.content.Context;
import android.os.Build;
import android.util.Log;

/**
 * Single source of truth for device-dependent defaults.
 *
 * Only decides things that must be known before the GL surface exists: the default render
 * resolution and the per-vertex mesh size (CPU cost of the preset equations).
 */
public final class DeviceProfile {
    private static final String TAG = "DeviceProfile";

    public enum Tier { LOW, STANDARD, HIGH }

    public final Tier tier;
    public final long totalRamMb;

    private DeviceProfile(Tier tier, long totalRamMb) {
        this.tier = tier;
        this.totalRamMb = totalRamMb;
    }

    public static DeviceProfile detect(Context context) {
        ActivityManager am = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
        ActivityManager.MemoryInfo memoryInfo = new ActivityManager.MemoryInfo();
        am.getMemoryInfo(memoryInfo);
        long totalRamMb = memoryInfo.totalMem / (1024 * 1024);

        String model = (Build.MANUFACTURER + " " + Build.MODEL).toLowerCase();
        Tier tier;
        if (model.contains("shield") || Build.HARDWARE.toLowerCase().contains("tegra")) {
            tier = Tier.HIGH;
        } else if (am.isLowRamDevice() || totalRamMb < 1600) {
            tier = Tier.LOW;
        } else {
            tier = Tier.STANDARD;
        }
        Log.i(TAG, "Device " + Build.MANUFACTURER + " " + Build.MODEL + " (" + Build.HARDWARE
                + "), RAM " + totalRamMb + "MB, cores " + Runtime.getRuntime().availableProcessors()
                + " -> tier " + tier);
        return new DeviceProfile(tier, totalRamMb);
    }

    /** Starting point for automatic resolution; it adapts from there and is remembered. */
    public int initialAutoHeight() {
        switch (tier) {
            case HIGH: return 1440;
            case STANDARD: return 1080;
            case LOW:
            default: return 720;
        }
    }

    /** Lowest height automatic resolution may use. */
    public int minAutoHeight() {
        switch (tier) {
            case HIGH: return 720;
            case STANDARD: return 540;
            case LOW:
            default: return 360;
        }
    }

    /** Default soft transition. During a transition two presets render at once (double cost). */
    public int defaultTransitionSeconds() {
        return tier == Tier.LOW ? 2 : 7;
    }

    /** Skip presets that stay far below target even at the lowest resolution. */
    public boolean defaultSkipSlowPresets() {
        return tier == Tier.LOW;
    }

    /** Default frame-rate cap. Low-end boxes rarely hold 60 fps; an even 30 looks smoother. */
    public int defaultFrameRateCap() {
        return tier == Tier.LOW ? 30 : 60;
    }

    /** Default index into {@link #MESH_SIZES}. */
    public int defaultMeshLevel() {
        switch (tier) {
            case HIGH: return 3;
            case STANDARD: return 2;
            case LOW:
            default: return 1;
        }
    }

    /**
     * Per-vertex equation mesh (width, height) per detail level. Evaluated on the CPU for every
     * vertex on every frame, so it is the main CPU cost of a preset; finer meshes give smoother
     * warps and zooms.
     */
    public static final int[][] MESH_SIZES = {{24, 16}, {32, 24}, {48, 32}, {64, 48}, {96, 72}};
    public static final String[] MESH_LABELS = {"Minimal", "Low", "Medium", "High", "Ultra"};
}
