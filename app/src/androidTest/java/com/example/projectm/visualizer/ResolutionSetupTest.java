package com.example.projectm.visualizer;

import android.app.Activity;
import android.app.Instrumentation;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.SystemClock;
import android.view.KeyEvent;
import android.widget.TextView;
import java.io.File;
import java.io.FileOutputStream;
import java.lang.reflect.Field;
import nl.neerdael.projectm.core.ProjectMJNI;
import nl.neerdael.projectm.core.QualityController;

/** Real menu, D-pad, persistence and completed-render generation checks in the isolated APK. */
final class ResolutionSetupTest {
    private static void check(boolean ok, String message) {
        if (!ok) throw new AssertionError(message);
    }

    private static void onUi(Instrumentation test, Runnable action) {
        Throwable[] failure = new Throwable[1];
        test.runOnMainSync(() -> {
            try { action.run(); }
            catch (Throwable error) { failure[0] = error; }
        });
        if (failure[0] != null) throw new AssertionError("UI assertion failed", failure[0]);
    }

    private static QualityController quality(Activity activity) throws Exception {
        Field field = MainActivity.class.getDeclaredField("quality");
        field.setAccessible(true);
        return (QualityController) field.get(activity);
    }

    private static void awaitFrame(Instrumentation test, Activity activity) throws Exception {
        Field field = MainActivity.class.getDeclaredField("renderBudgetGeneration");
        field.setAccessible(true);
        long deadline = SystemClock.elapsedRealtime() + 15000;
        while (SystemClock.elapsedRealtime() < deadline) {
            long[] generation = new long[1];
            onUi(test, () -> {
                try { generation[0] = field.getLong(activity); }
                catch (IllegalAccessException error) { throw new AssertionError(error); }
            });
            if (generation[0] > 0 && ProjectMJNI.getCompletedRenderBudgetGeneration() == generation[0]
                    && ProjectMJNI.getRenderedFrameSerial() > 0) return;
            SystemClock.sleep(100);
        }
        throw new AssertionError("selected render generation never completed");
    }

    private static void openAdvanced(Instrumentation test, Activity activity) {
        test.sendKeyDownUpSync(KeyEvent.KEYCODE_MENU);
        onUi(test, () -> activity.findViewById(R.id.row_advanced).performClick());
        SystemClock.sleep(300);
    }

    static void run(Instrumentation test) {
        Bundle result = new Bundle();
        Activity activity = null;
        int code = Activity.RESULT_CANCELED;
        try {
            check(test.getTargetContext().getPackageName().endsWith(".setuptest"), "requires isolated setup APK");
            SharedPreferences prefs = test.getTargetContext().getSharedPreferences("projectm_settings", 0);
            prefs.edit().putBoolean("track_access_explained", true).putBoolean("auto_change_enabled", false)
                    .putBoolean("blank_detection_v3", false).putInt("transition_duration", 0)
                    .putInt("render_height", -1).remove("resolution_mode").commit();
            Intent launch = new Intent(test.getTargetContext(), MainActivity.class)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            activity = test.startActivitySync(launch);
            Activity target = activity;
            QualityController controller = quality(target);
            onUi(test, () -> check(controller.isAuto(), "fresh install/legacy Native did not use Auto"));
            awaitFrame(test, target);
            openAdvanced(test, target);
            onUi(test, () -> {
                check(target.findViewById(R.id.row_resolution).isFocusable(), "resolution is not D-pad focusable");
                target.findViewById(R.id.row_resolution).requestFocus();
            });
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_RIGHT);
            check(prefs.getInt("resolution_mode", 0) == 720, "D-pad did not save 720p");
            awaitFrame(test, target);
            onUi(test, () -> check(!controller.isAuto() && controller.currentHeight() > 0 && controller.currentHeight() <= 720,
                    "720p selection not applied"));
            int autoHistory = prefs.getInt("auto_render_height", 0);
            // Left -> Auto, Left again wraps to Native without depending on the panel's choices.
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_LEFT);
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_LEFT);
            check(prefs.getInt("resolution_mode", 0) == -1, "Native not saved");
            awaitFrame(test, target);
            onUi(test, () -> check(controller.isNative() && !controller.isAuto(), "Native mode not active"));
            check(prefs.getInt("auto_render_height", 0) == autoHistory, "Native overwrote Auto history");
            onUi(test, target::finish);
            test.waitForIdleSync();
            SystemClock.sleep(1500); // let the old GL thread release its instance before a new activity
            activity = test.startActivitySync(launch);
            Activity restarted = activity;
            QualityController restored = quality(restarted);
            awaitFrame(test, restarted);
            onUi(test, () -> check(restored.isNative(), "Native not restored after activity restart"));
            openAdvanced(test, restarted);
            onUi(test, () -> {
                String text = ((TextView) restarted.findViewById(R.id.diagnostics)).getText().toString();
                check(text.contains("(native)"), "diagnostics omit Native mode: " + text);
            });
            onUi(test, () -> restarted.findViewById(R.id.row_skipped).requestFocus());
            SystemClock.sleep(300);
            onUi(test, () -> {
                android.graphics.Rect visible = new android.graphics.Rect();
                android.view.View row = restarted.findViewById(R.id.row_skipped);
                check(row.getGlobalVisibleRect(visible) && visible.height() == row.getHeight(),
                        "last Advanced row is clipped rather than scrollable: visible=" + visible
                        + ", height=" + row.getHeight() + ", focus=" + row.hasFocus()
                        + ", scroll=" + restarted.findViewById(R.id.advanced_menu).getScrollY());
                restarted.findViewById(R.id.row_resolution).requestFocus();
            });
            SystemClock.sleep(300);
            Bitmap screenshot = test.getUiAutomation().takeScreenshot();
            check(screenshot != null, "settings screenshot unavailable");
            try (FileOutputStream output = new FileOutputStream(new File(
                    test.getTargetContext().getExternalCacheDir(), "resolution-advanced.png"))) {
                check(screenshot.compress(Bitmap.CompressFormat.PNG, 100, output), "screenshot write failed");
            } finally { screenshot.recycle(); }
            onUi(test, () -> restarted.findViewById(R.id.row_resolution).requestFocus());
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_RIGHT); // Native -> Auto
            awaitFrame(test, restarted);
            onUi(test, () -> check(restored.isAuto(), "return to Auto failed"));
            result.putString("stream", "PASS: Auto default, legacy migration, D-pad 720p, Native wrap, completed frames, separate Auto history, Native persistence, diagnostics and return to Auto\n");
            code = Activity.RESULT_OK;
        } catch (Throwable failure) {
            result.putString("stream", "FAIL: " + failure + "; cause=" + failure.getCause() + "\n");
        } finally {
            if (activity != null) {
                Activity target = activity;
                onUi(test, target::finish);
            }
        }
        test.finish(code, result);
    }
}
