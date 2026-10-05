package com.example.projectm.visualizer;

import android.app.Activity;
import android.app.Instrumentation;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.SystemClock;
import android.view.KeyEvent;
import android.view.View;
import android.widget.TextView;
import java.lang.reflect.Method;
import nl.neerdael.projectm.core.ProjectMJNI;

/** Exercises persistence, D-pad focus and resolution gating in the isolated setup APK. */
final class NativeTrailsSetupTest {
    private static void check(boolean ok, String message) {
        if (!ok) throw new AssertionError(message);
    }
    private static String status() throws Exception {
        Method method = ProjectMJNI.class.getMethod("getNativeTrailsStatus");
        return (String) method.invoke(null);
    }
    private static void awaitStatus(String expected) throws Exception {
        long deadline = SystemClock.elapsedRealtime() + 15000;
        while (SystemClock.elapsedRealtime() < deadline) {
            if (status().toLowerCase(java.util.Locale.ROOT).contains(expected)) return;
            SystemClock.sleep(100);
        }
        throw new AssertionError("expected trails " + expected + ", actual=" + status());
    }
    static void run(Instrumentation test) {
        Bundle result = new Bundle();
        Activity activity = null;
        int code = Activity.RESULT_CANCELED;
        try {
            check(test.getTargetContext().getPackageName().endsWith(".setuptest"), "requires isolated setup APK");
            SharedPreferences prefs = test.getTargetContext().getSharedPreferences("projectm_settings", 0);
            prefs.edit().putBoolean("track_access_explained", true).putBoolean("auto_change_enabled", false)
                    .putBoolean("skip_slow_presets", false).putBoolean("blank_detection_v3", false)
                    .putBoolean("memory_limit", true).putInt("render_height", -1) // retired settings must not override Auto
                    .remove("native_trails").commit();
            Intent launch = new Intent(test.getTargetContext(), MainActivity.class)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            activity = test.startActivitySync(launch);
            Activity target = activity;
            int rowId = test.getTargetContext().getResources().getIdentifier("row_native_trails", "id",
                    test.getTargetContext().getPackageName());
            check(rowId != 0, "Native trails row missing");
            awaitStatus("standard");
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_MENU);
            test.runOnMainSync(() -> target.findViewById(R.id.row_advanced).performClick());
            SystemClock.sleep(300); // panel entrance; D-pad exits touch mode on the phone emulator
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_DOWN);
            test.runOnMainSync(() -> {
                View row = target.findViewById(rowId);
                check(row.getVisibility() == View.VISIBLE && row.isFocusable(), "trails row not available in Native");
                check(row.requestFocus(), "trails row cannot receive D-pad focus");
            });
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_RIGHT);
            awaitStatus("medium");
            check(prefs.getInt("native_trails", -1) == 1, "Medium not persisted");
            test.runOnMainSync(() -> target.findViewById(rowId).performClick());
            awaitStatus("high");
            check(prefs.getInt("native_trails", -1) == 2, "High not persisted");
            check(test.getTargetContext().getResources().getIdentifier("row_resolution", "id",
                    test.getTargetContext().getPackageName()) == 0, "manual resolution row remains");
            check(test.getTargetContext().getResources().getIdentifier("row_memory_limit", "id",
                    test.getTargetContext().getPackageName()) == 0, "manual RAM limiter row remains");
            test.runOnMainSync(target::finish);
            test.waitForIdleSync();
            SystemClock.sleep(1500);
            activity = test.startActivitySync(launch);
            awaitStatus("high");
            Activity restarted = activity;
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_MENU);
            test.runOnMainSync(() -> restarted.findViewById(R.id.row_advanced).performClick());
            SystemClock.sleep(750);
            test.runOnMainSync(() -> {
                String diagnostics = ((TextView) restarted.findViewById(R.id.diagnostics)).getText().toString();
                check(diagnostics.toLowerCase(java.util.Locale.ROOT).contains("auto")
                        && diagnostics.toLowerCase(java.util.Locale.ROOT).contains("high"),
                        "diagnostics missing automatic mode/selected trails: " + diagnostics);
            });
            result.putString("stream", "PASS: Auto-only UI, Standard default, D-pad Medium, High selection, persisted High, retired manual controls absent, diagnostics\n");
            code = Activity.RESULT_OK;
        } catch (Throwable failure) {
            result.putString("stream", "FAIL: " + failure + "\n");
        } finally {
            if (activity != null) {
                Activity target = activity;
                test.runOnMainSync(target::finish);
            }
        }
        test.finish(code, result);
    }
}
