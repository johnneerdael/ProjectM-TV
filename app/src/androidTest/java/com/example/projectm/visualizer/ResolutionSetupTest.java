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

    /** Optional 4K hardware recording fixture; synthetic PCM is test input, not player capture. */
    static void record(Instrumentation test) {
        Bundle result = new Bundle();
        Activity activity = null;
        java.util.concurrent.atomic.AtomicBoolean feeding = new java.util.concurrent.atomic.AtomicBoolean(true);
        Thread signal = null;
        int code = Activity.RESULT_CANCELED;
        try {
            check(test.getTargetContext().getPackageName().endsWith(".setuptest"), "requires isolated setup APK");
            SharedPreferences prefs = test.getTargetContext().getSharedPreferences("projectm_settings", 0);
            prefs.edit().putBoolean("track_access_explained", true).putBoolean("auto_change_enabled", false)
                    .putBoolean("blank_detection_v3", false).putInt("transition_duration", 0)
                    .putInt("native_trails", 0).remove("resolution_mode").remove("auto_render_height").commit();
            File directory = test.getTargetContext().getExternalCacheDir();
            check(directory != null, "external cache unavailable");
            File ready = new File(directory, "resolution-recording.ready");
            File go = new File(directory, "resolution-recording.go");
            check(!ready.exists() || ready.delete(), "cannot clear old recording readiness");
            check(!go.exists() || go.delete(), "cannot clear old recording trigger");
            activity = test.startActivitySync(new Intent(test.getTargetContext(), MainActivity.class)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK));
            Activity target = activity;
            QualityController controller = quality(target);
            Field rendererField = MainActivity.class.getDeclaredField("renderer");
            rendererField.setAccessible(true);
            nl.neerdael.projectm.core.VisualizerRenderer renderer =
                    (nl.neerdael.projectm.core.VisualizerRenderer) rendererField.get(target);
            signal = new Thread(() -> {
                byte[] waveform = new byte[1024];
                while (feeding.get()) {
                    double time = SystemClock.elapsedRealtime() / 1000.0;
                    double pulse = .25 + .20 * Math.pow(Math.max(0, Math.sin(time * Math.PI * 3)), 4);
                    for (int i = 0; i < waveform.length; i++) {
                        double tone = Math.sin(2 * Math.PI * 220 * (time + i / 44100.0));
                        waveform[i] = (byte) Math.round(128 + 127 * pulse * tone);
                    }
                    ProjectMJNI.addWaveform(waveform, waveform.length);
                    SystemClock.sleep(50);
                }
            }, "RecordingTestSignal");
            signal.start();
            awaitFrame(test, target);
            onUi(test, () -> check(controller.isAuto(), "recording must start with Auto default"));
            check(ready.createNewFile(), "cannot publish recording readiness");
            long deadline = SystemClock.elapsedRealtime() + 45000;
            while (!go.exists() && SystemClock.elapsedRealtime() < deadline) SystemClock.sleep(50);
            check(go.exists(), "recorder did not send its start trigger");
            SystemClock.sleep(2000);
            openAdvanced(test, target);
            SystemClock.sleep(2000);
            onUi(test, () -> target.findViewById(R.id.row_resolution).requestFocus());
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_LEFT); // Auto -> Native
            awaitFrame(test, target);
            long first = ProjectMJNI.getRenderedFrameSerial();
            for (int level = 0; level <= 2; level++) {
                if (level == 1) {
                    for (int down = 0; down < 3; down++) test.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_DOWN);
                    onUi(test, () -> check(target.findViewById(R.id.row_native_trails).hasFocus(),
                            "D-pad did not reach Native trails"));
                }
                if (level > 0) test.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_RIGHT);
                awaitFrame(test, target);
                long until = SystemClock.elapsedRealtime() + 5000;
                while (SystemClock.elapsedRealtime() < until) {
                    onUi(test, () -> check(controller.isNative() && controller.currentHeight() == 2160
                            && renderer.getSurfaceWidth() == 3840 && renderer.getSurfaceHeight() == 2160,
                            "recording left actual 3840x2160 Native rendering"));
                    check(ProjectMJNI.getAudioLevel() > .001f, "synthetic PCM did not reach the renderer");
                    SystemClock.sleep(250);
                }
                String status = ProjectMJNI.getNativeTrailsStatus();
                check(status.contains("1280×720 canvas"), "Native trails fallback: " + status);
                check(status.startsWith(new String[]{"Standard", "Medium", "High"}[level]), "wrong trails level: " + status);
                Bitmap screenshot = test.getUiAutomation().takeScreenshot();
                check(screenshot != null, "4K screenshot unavailable");
                try (FileOutputStream output = new FileOutputStream(new File(directory, "native-4k-" + level + ".png"))) {
                    check(screenshot.compress(Bitmap.CompressFormat.PNG, 100, output), "4K screenshot failed");
                } finally { screenshot.recycle(); }
            }
            check(ProjectMJNI.getRenderedFrameSerial() - first >= 50, "insufficient completed Native frames");
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_BACK); // Advanced -> main
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_BACK); // close panel
            SystemClock.sleep(4000);
            result.putString("stream", "PASS: Auto default to actual Native 3840x2160, Standard/Medium/High at 1280x720 canvas, synthetic unsigned mono PCM, completed frames; preset="
                    + ProjectMJNI.getCurrentPresetName() + ", final_fps=" + renderer.getCurrentFps() + "\n");
            code = Activity.RESULT_OK;
        } catch (Throwable failure) {
            result.putString("stream", "FAIL: " + failure + "; cause=" + failure.getCause() + "\n");
        } finally {
            feeding.set(false);
            if (signal != null) {
                try { signal.join(1000); }
                catch (InterruptedException interrupted) { Thread.currentThread().interrupt(); }
            }
            if (activity != null) onUi(test, activity::finish);
        }
        test.finish(code, result);
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
