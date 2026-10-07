package com.example.projectm.visualizer;

import android.app.Application;
import android.util.Log;

import nl.neerdael.projectm.core.ProjectMCore;
import nl.neerdael.projectm.core.ProjectMJNI;

import java.io.File;

public class ProjectMApplication extends Application {
    private static final String TAG = "ProjectMApplication";
    private static final String PREF_SKIP_LIST_RESET = "skip_list_reset_1_9";
    private static final String PREF_FRAME_RATE_RESET = "frame_rate_reset_30";

    @Override
    public void onCreate() {
        super.onCreate();
        Log.i(TAG, "Starting on " + android.os.Build.MANUFACTURER + " " + android.os.Build.MODEL
                + ", Android " + android.os.Build.VERSION.RELEASE);

        // Up to 1.8 texture-based presets rendered without their textures and could be skipped as
        // blank. The textures ship now, so give every preset a new chance once.
        File skipList = ProjectMCore.skipListFile(this);
        android.content.SharedPreferences prefs = getSharedPreferences("projectm_settings", MODE_PRIVATE);
        if (!prefs.getBoolean(PREF_SKIP_LIST_RESET, false)) {
            if (skipList.exists() && !skipList.delete()) Log.w(TAG, "Could not reset " + skipList);
            prefs.edit().putBoolean(PREF_SKIP_LIST_RESET, true).apply();
        }

        // The default frame rate became half the refresh rate (30 fps at 60 Hz), which lets Auto
        // pick a much higher resolution. Move everyone to it once, also those who chose a rate, and
        // let Auto learn its level anew at that rate.
        if (!prefs.getBoolean(PREF_FRAME_RATE_RESET, false)) {
            prefs.edit()
                    .remove("frame_rate_cap")
                    .remove("auto_render_height")
                    .putBoolean(PREF_FRAME_RATE_RESET, true)
                    .apply();
        }

        ProjectMCore.init(this);

        File customRoot = new File(getFilesDir(), "custom-presets");
        File custom = CustomPresetPack.current(customRoot);
        if (custom != null) ProjectMJNI.setCustomPresetPack(custom.getAbsolutePath());

        // Versions up to 1.7 extracted ~130MB of presets on every launch; reclaim that space.
        new Thread(() -> {
            android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_BACKGROUND);
            deleteRecursively(new File(getCacheDir(), "projectM"));
            deleteRecursively(new File(getFilesDir(), "projectM"));
            synchronized (CustomPresetPack.STORE_LOCK) {
                // Once the worker's index owns the active generation, remove interrupted imports.
                while (ProjectMJNI.isCustomPresetPackPending()) {
                    try { Thread.sleep(50); } catch (InterruptedException interrupted) { return; }
                }
                CustomPresetPack.cleanUnused(customRoot, CustomPresetPack.current(customRoot));
                new File(customRoot, "incoming.zip").delete();
                new File(customRoot, "current.tmp").delete();
            }
        }, "LegacyCleanup").start();
    }

    private static void deleteRecursively(File file) {
        if (!file.exists()) return;
        File[] children = file.listFiles();
        if (children != null) {
            for (File child : children) deleteRecursively(child);
        }
        if (!file.delete()) Log.w(TAG, "Could not delete " + file);
    }
}
