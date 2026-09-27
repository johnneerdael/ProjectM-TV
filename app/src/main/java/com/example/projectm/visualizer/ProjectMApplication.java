package com.example.projectm.visualizer;

import android.app.Application;
import android.util.Log;

import nl.neerdael.projectm.core.ProjectMCore;

import java.io.File;

public class ProjectMApplication extends Application {
    private static final String TAG = "ProjectMApplication";
    private static final String PREF_SKIP_LIST_RESET = "skip_list_reset_1_9";

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

        ProjectMCore.init(this);

        // Versions up to 1.7 extracted ~130MB of presets on every launch; reclaim that space.
        new Thread(() -> {
            android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_BACKGROUND);
            deleteRecursively(new File(getCacheDir(), "projectM"));
            deleteRecursively(new File(getFilesDir(), "projectM"));
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
