package nl.neerdael.projectm.core;

import android.app.ActivityManager;
import android.content.Context;

/** Process-owned sampler; retains only the application ActivityManager, never an Activity. */
final class AndroidMemoryProvider implements MemoryProvider {
    private final ActivityManager activityManager;
    private final ActivityManager.MemoryInfo memoryInfo = new ActivityManager.MemoryInfo();

    AndroidMemoryProvider(Context applicationContext) {
        activityManager = (ActivityManager) applicationContext.getSystemService(Context.ACTIVITY_SERVICE);
    }

    @Override public MemorySnapshot sample() {
        if (activityManager == null) return null;
        try {
            activityManager.getMemoryInfo(memoryInfo);
            return new MemorySnapshot(memoryInfo.totalMem, memoryInfo.availMem,
                    memoryInfo.threshold, memoryInfo.lowMemory);
        } catch (RuntimeException unavailable) {
            return null;
        }
    }
}
