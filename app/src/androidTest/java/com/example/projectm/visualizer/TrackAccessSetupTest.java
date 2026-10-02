package com.example.projectm.visualizer;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Instrumentation;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.SystemClock;
import android.os.ParcelFileDescriptor;
import android.view.KeyEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import java.io.File;
import java.io.FileOutputStream;
import java.lang.reflect.Field;
import nl.neerdael.projectm.core.ProjectMJNI;

/** Isolated setup-app checks; never grants notification access or resets the installed release. */
final class TrackAccessSetupTest {
    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
    private static AlertDialog dialog(Activity activity) throws Exception {
        Field field = MainActivity.class.getDeclaredField("trackAccessDialog");
        field.setAccessible(true);
        return (AlertDialog) field.get(activity);
    }
    private static void capture(Instrumentation test, String name) throws Exception {
        test.getUiAutomation();
        SystemClock.sleep(3500); // settle the window and let Android's automation-service toast expire
        File directory = new File(test.getTargetContext().getExternalFilesDir(null), "setup-screenshots");
        directory.mkdirs();
        try (ParcelFileDescriptor.AutoCloseInputStream input = new ParcelFileDescriptor.AutoCloseInputStream(
                    test.getUiAutomation().executeShellCommand("screencap -p"));
             FileOutputStream output = new FileOutputStream(new File(directory, name + ".png"))) {
            byte[] buffer = new byte[8192];
            int count;
            while ((count = input.read(buffer)) > 0) output.write(buffer, 0, count);
        }
    }
    static void run(Instrumentation test, String mode) {
        Bundle result = new Bundle();
        Activity activity = null;
        int code = Activity.RESULT_CANCELED;
        try {
            check(test.getTargetContext().getPackageName().endsWith(".setuptest"), "requires isolated setup test app");
            SharedPreferences prefs = test.getTargetContext().getSharedPreferences("projectm_settings", 0);
            prefs.edit().remove("track_access_explained").commit();
            if ("guide".equals(mode)) prefs.edit().putString("music_category", "all").commit();
            Intent launch = new Intent(test.getTargetContext(), MainActivity.class)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            activity = test.startActivitySync(launch);
            AlertDialog prompt = null;
            long deadline = SystemClock.elapsedRealtime() + 12000;
            while (SystemClock.elapsedRealtime() < deadline) {
                prompt = dialog(activity);
                if (prompt != null && prompt.isShowing()) break;
                SystemClock.sleep(100);
            }
            check(prompt != null && prompt.isShowing(), "startup prompt not shown");
            check("Configure".contentEquals(prompt.getButton(AlertDialog.BUTTON_POSITIVE).getText()), "Configure missing");
            check("Dismiss".contentEquals(prompt.getButton(AlertDialog.BUTTON_NEGATIVE).getText()), "Dismiss missing");
            check(!prefs.getBoolean("track_access_explained", false), "prompt display persisted dismissal");
            capture(test, "track-titles-prompt");
            AlertDialog shown = prompt;
            if ("configure".equals(mode)) {
                test.runOnMainSync(() -> shown.getButton(AlertDialog.BUTTON_POSITIVE).performClick());
                SystemClock.sleep(1500);
                AccessibilityNodeInfo window = test.getUiAutomation().getRootInActiveWindow();
                check(window != null && !test.getTargetContext().getPackageName().contentEquals(window.getPackageName()), "Configure stayed in app");
                check(!prefs.getBoolean("track_access_explained", false), "Configure permanently dismissed prompt");
                capture(test, "notification-access");
            } else {
                test.runOnMainSync(() -> shown.getButton(AlertDialog.BUTTON_NEGATIVE).performClick());
                long savedDeadline = SystemClock.elapsedRealtime() + 2000;
                while (!prefs.getBoolean("track_access_explained", false)
                        && SystemClock.elapsedRealtime() < savedDeadline) SystemClock.sleep(50);
                check(prefs.getBoolean("track_access_explained", false), "Dismiss not persisted");
                Activity previous = activity;
                test.runOnMainSync(previous::finish);
                test.waitForIdleSync();
                SystemClock.sleep(1000); // allow the old GL surface to finish destroying
                activity = test.startActivitySync(launch);
                SystemClock.sleep(2500);
                AlertDialog repeated = dialog(activity);
                check(repeated == null || !repeated.isShowing(), "dismissed prompt returned after restart");
                capture(test, "after-dismiss");
                if ("guide".equals(mode)) {
                    Activity target = activity;
                    test.sendKeyDownUpSync(KeyEvent.KEYCODE_MENU);
                    test.runOnMainSync(() -> target.findViewById(R.id.row_music_category).requestFocus());
                    capture(test, "main-settings");
                    test.runOnMainSync(() -> target.findViewById(R.id.row_music_category).performClick());
                    long categoryDeadline = SystemClock.elapsedRealtime() + 15000;
                    while ((ProjectMJNI.isMusicCategoryPending() || !"dance".equals(ProjectMJNI.getMusicCategory()))
                            && SystemClock.elapsedRealtime() < categoryDeadline)
                        SystemClock.sleep(100);
                    check("dance".equals(ProjectMJNI.getMusicCategory()) && !ProjectMJNI.isMusicCategoryPending(),
                            "Dance did not apply: category=" + ProjectMJNI.getMusicCategory()
                            + ", pending=" + ProjectMJNI.isMusicCategoryPending()
                            + ", packaged=" + ProjectMJNI.getCategoryPresetCount("dance")
                            + ", requested=" + prefs.getString("music_category", "missing"));
                    capture(test, "dance-selected");
                    test.runOnMainSync(() -> target.findViewById(R.id.row_advanced).performClick());
                    capture(test, "advanced-settings");
                    test.runOnMainSync(() -> target.findViewById(R.id.row_track_titles).performClick());
                    capture(test, "track-titles-manual");
                }
            }
            result.putString("stream", "PASS: startup buttons, " + mode + ", persistence and screenshot capture\n");
            code = Activity.RESULT_OK;
        } catch (Throwable failure) {
            result.putString("stream", "FAIL: " + failure + "\n");
        } finally {
            if (activity != null) {
                Activity current = activity;
                test.runOnMainSync(current::finish);
            }
        }
        test.finish(code, result);
    }
}
