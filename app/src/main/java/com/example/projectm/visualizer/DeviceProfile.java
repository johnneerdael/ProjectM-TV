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

    /** Default render height; the hardware scaler stretches it to the full screen. */
    public int defaultRenderHeight() {
        switch (tier) {
            case HIGH: return 1080;
            case LOW:
            case STANDARD:
            default: return 720;
        }
    }

    /** Per-vertex equation mesh; evaluated on the CPU for every vertex on every frame. */
    public int meshWidth() {
        return tier == Tier.LOW ? 32 : 48;
    }

    public int meshHeight() {
        return tier == Tier.LOW ? 24 : 32;
    }
}
