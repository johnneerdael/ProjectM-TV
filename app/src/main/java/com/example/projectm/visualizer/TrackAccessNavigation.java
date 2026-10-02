package com.example.projectm.visualizer;

/** Prefer the app-specific notification access view, then fall back for TV/OEM settings apps. */
final class TrackAccessNavigation {
    static final String DETAIL = "android.settings.NOTIFICATION_LISTENER_DETAIL_SETTINGS";
    static final String LIST = "android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS";
    interface Launcher { boolean launch(String action); }

    static boolean open(int apiLevel, Launcher launcher) {
        if (apiLevel >= 30 && launcher.launch(DETAIL)) return true;
        if (launcher.launch(LIST)) return true;
        if (launcher.launch("android.settings.APPLICATION_SETTINGS")) return true;
        return launcher.launch("android.settings.SETTINGS");
    }
}
