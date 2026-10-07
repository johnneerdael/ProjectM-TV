package com.example.projectm.visualizer;

import android.app.Activity;
import android.app.Instrumentation;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.SystemClock;
import android.view.KeyEvent;
import android.view.View;
import java.io.*;
import java.lang.reflect.Field;
import java.net.*;
import java.util.zip.*;
import java.util.concurrent.atomic.AtomicReference;
import nl.neerdael.projectm.core.ProjectMJNI;

/** Full temporary-listener, ZIP-import and native selection journey on an isolated TV app. */
final class CustomPackSetupTest {
    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static void await(String mood, int count) {
        long deadline = SystemClock.elapsedRealtime() + 60000;
        while (SystemClock.elapsedRealtime() < deadline) {
            if (!ProjectMJNI.isMusicCategoryPending() && mood.equals(ProjectMJNI.getMusicCategory())
                    && ProjectMJNI.getPresetCount() == count && !ProjectMJNI.getCurrentPresetName().isEmpty()) return;
            SystemClock.sleep(50);
        }
        throw new AssertionError("Selection not applied: " + mood + ", count=" + ProjectMJNI.getPresetCount()
                + ", current=" + ProjectMJNI.getCurrentPresetName());
    }

    private static File archive(File cache, int count, String prefix) throws Exception {
        File file = new File(cache, "custom-pack-test.zip");
        try (ZipOutputStream out = new ZipOutputStream(new FileOutputStream(file))) {
            for (int i = 0; i < count; i++) {
                out.putNextEntry(new ZipEntry(prefix + "/preset-" + i + (i % 2 == 0 ? ".milk" : ".MILK")));
                out.write("[preset00]\nfRating=3\nfDecay=0.98\n".getBytes("UTF-8"));
                out.closeEntry();
            }
            out.putNextEntry(new ZipEntry("textures/ignored.png")); out.write(new byte[]{1,2,3}); out.closeEntry();
            out.putNextEntry(new ZipEntry("README.txt")); out.write("ignored".getBytes("UTF-8")); out.closeEntry();
        }
        return file;
    }

    private static String upload(URL url, File file) throws Exception {
        try (Socket socket = new Socket(url.getHost(), url.getPort())) {
            socket.setSoTimeout(240000);
            OutputStream out = socket.getOutputStream();
            out.write(("POST " + url.getPath() + " HTTP/1.1\r\nHost: " + url.getAuthority()
                    + "\r\nContent-Length: " + file.length() + "\r\nContent-Type: application/zip\r\n\r\n").getBytes("US-ASCII"));
            try (InputStream in = new FileInputStream(file)) {
                byte[] buffer = new byte[32768]; int n;
                while ((n = in.read(buffer)) != -1) out.write(buffer, 0, n);
            }
            out.flush();
            ByteArrayOutputStream response = new ByteArrayOutputStream();
            byte[] buffer = new byte[4096]; int n;
            while ((n = socket.getInputStream().read(buffer)) != -1) response.write(buffer, 0, n);
            return response.toString("UTF-8");
        }
    }

    private static void capture(Instrumentation test, String name) throws Exception {
        Bitmap bitmap = test.getUiAutomation().takeScreenshot();
        File file = new File(test.getTargetContext().getExternalFilesDir(null), name + ".png");
        try (FileOutputStream out = new FileOutputStream(file)) { bitmap.compress(Bitmap.CompressFormat.PNG, 100, out); }
        bitmap.recycle();
    }

    private static String uploadWhileRendering(Instrumentation test, URL url, File zip) throws Exception {
        AtomicReference<String> response = new AtomicReference<>();
        AtomicReference<Throwable> failure = new AtomicReference<>();
        Thread upload = new Thread(() -> {
            try { response.set(upload(url, zip)); } catch (Throwable error) { failure.set(error); }
        }, "CustomPackTestUpload");
        upload.start();
        int renderingIntervals = 0;
        long previous = ProjectMJNI.getRenderedFrameSerial();
        File incoming = new File(test.getTargetContext().getFilesDir(), "custom-presets/incoming.zip");
        while (upload.isAlive()) {
            SystemClock.sleep(500);
            long current = ProjectMJNI.getRenderedFrameSerial();
            if (incoming.exists() && current > previous) renderingIntervals++;
            previous = current;
        }
        if (failure.get() != null) throw new AssertionError("upload failed", failure.get());
        check(renderingIntervals >= 2, "rendering did not advance during active ZIP import");
        return response.get();
    }

    static void run(Instrumentation test, boolean restart) {
        Bundle result = new Bundle();
        Activity activity = null;
        try {
            test.getTargetContext().getSharedPreferences("projectm_settings", 0).edit()
                    .putBoolean("track_access_explained", true).putBoolean("auto_change_enabled", false)
                    .putBoolean("blank_detection_v3", false).putBoolean("skip_slow_presets", false).apply();
            Intent intent = new Intent(test.getTargetContext(), MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            activity = test.startActivitySync(intent);
            ProjectMJNI.setAutoChange(false);
            if (restart) {
                await("custom", 2);
                check(ProjectMJNI.getCurrentPresetName().contains("/replacement/"), "restart lost replacement pack");
                result.putString("stream", "PASS: cold restart retains pack and Custom selection\n");
                test.finish(Activity.RESULT_OK, result);
                return;
            }
            ProjectMJNI.setMusicCategory("all");
            long deadline = SystemClock.elapsedRealtime() + 30000;
            while (ProjectMJNI.isMusicCategoryPending() && SystemClock.elapsedRealtime() < deadline) SystemClock.sleep(50);
            int bundled = ProjectMJNI.getCategoryPresetCount("all");
            check(bundled == 9606, "test must start with a fresh app, found " + bundled);
            int[] scored = {ProjectMJNI.getCategoryPresetCount("chill"), ProjectMJNI.getCategoryPresetCount("normal"), ProjectMJNI.getCategoryPresetCount("intense")};
            Activity target = activity;
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_MENU);
            test.runOnMainSync(() -> target.findViewById(R.id.row_advanced).requestFocus());
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_CENTER);
            test.runOnMainSync(() -> {
                View row = target.findViewById(R.id.row_custom_pack);
                check(row.isFocusable() && row.requestFocus(), "custom upload row is not reachable");
            });
            SystemClock.sleep(300);
            capture(test, "custom-pack-advanced");
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_CENTER);
            SystemClock.sleep(300);
            capture(test, "custom-pack-upload");
            Field field = MainActivity.class.getDeclaredField("customPackServer"); field.setAccessible(true);
            PresetPackUploadServer server = (PresetPackUploadServer)field.get(activity);
            check(server != null, "D-pad did not open the upload listener");
            URL url = new URL(server.url());
            long started = SystemClock.elapsedRealtime();
            File zip = archive(test.getTargetContext().getCacheDir(), 50000, "large");
            check(uploadWhileRendering(test, url, zip).startsWith("HTTP/1.1 200"), "large pack upload failed");
            await("custom", 50000);
            long elapsed = SystemClock.elapsedRealtime() - started;
            check(ProjectMJNI.getCurrentPresetName().contains("/large/"), "Custom selected a bundled preset");
            check(ProjectMJNI.getCategoryPresetCount("all") == bundled + 50000, "All does not include the entire pack");
            String[] ids = {"chill", "normal", "intense"};
            for (int i = 0; i < ids.length; i++) check(ProjectMJNI.getCategoryPresetCount(ids[i]) == scored[i], ids[i] + " changed after upload");
            for (int i = 0; i < 3; i++) {
                ProjectMJNI.randomPreset(true); SystemClock.sleep(300);
                check(ProjectMJNI.getCurrentPresetName().contains("/large/"), "Random escaped Custom");
            }
            ProjectMJNI.previousPreset(true); SystemClock.sleep(300);
            check(ProjectMJNI.getCurrentPresetName().contains("/large/"), "Previous escaped Custom");
            check(upload(url, archive(test.getTargetContext().getCacheDir(), 2, "replacement/😀")).startsWith("HTTP/1.1 200"), "replacement failed");
            await("custom", 2);
            check(ProjectMJNI.getCategoryPresetCount("all") == bundled + 2, "replacement accumulated old entries");
            check(ProjectMJNI.getCurrentPresetName().contains("/replacement/"), "old custom preset remained on screen");
            check(ProjectMJNI.getCurrentPresetName().contains("😀"), "JNI corrupted supplementary Unicode");
            File previousPack = CustomPresetPack.current(new File(test.getTargetContext().getFilesDir(), "custom-presets"));
            File bad = new File(test.getTargetContext().getCacheDir(), "invalid.zip");
            try (FileOutputStream out = new FileOutputStream(bad)) { out.write(new byte[]{1,2,3}); }
            check(upload(url, bad).startsWith("HTTP/1.1 400"), "invalid ZIP succeeded");
            await("custom", 2);
            check(previousPack.equals(CustomPresetPack.current(new File(test.getTargetContext().getFilesDir(), "custom-presets"))), "invalid ZIP changed the active pointer");
            check(ProjectMJNI.getCurrentPresetName().startsWith("custom/" + previousPack.getName() + "/"), "invalid ZIP changed the native generation");
            check("custom".equals(test.getTargetContext().getSharedPreferences("projectm_settings", 0).getString("music_category", "")), "Custom was not saved");
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_BACK);
            SystemClock.sleep(200);
            check(field.get(activity) == null, "closing the dialog left the listener attached");
            try (Socket unexpected = new Socket(url.getHost(), url.getPort())) { throw new AssertionError("closed listener accepted a connection"); }
            catch (IOException expected) { }
            ProjectMJNI.setMusicCategory("all"); await("all", bundled + 2);
            for (String id : ids) {
                ProjectMJNI.setMusicCategory(id);
                await(id, ProjectMJNI.getCategoryPresetCount(id));
                check(!ProjectMJNI.getCurrentPresetName().startsWith("custom/"), id + " selected a custom preset");
            }
            ProjectMJNI.setMusicCategory("custom"); await("custom", 2);
            SystemClock.sleep(700); // allow the real settings row to reflect and save the applied selection
            check("custom".equals(test.getTargetContext().getSharedPreferences("projectm_settings", 0)
                    .getString("music_category", "")), "final Custom selection was not persisted");
            test.sendKeyDownUpSync(KeyEvent.KEYCODE_BACK); // Advanced -> main settings
            test.runOnMainSync(() -> target.findViewById(R.id.row_music_category).requestFocus());
            capture(test, "custom-pack-selected");
            result.putString("stream", "PASS: Advanced D-pad upload, 50,000 presets, rendering during import, nested .MILK, ignored files, All inclusion, scored exclusions, Random/Previous, replacement, invalid ZIP preservation, persisted Custom, closed listener. Large import including ZIP generation: " + elapsed + " ms\n");
            test.finish(Activity.RESULT_OK, result);
        } catch (Throwable failure) {
            result.putString("stream", "FAIL: " + failure + "\n");
            test.finish(Activity.RESULT_CANCELED, result);
        } finally {
            if (activity != null) {
                Activity target = activity;
                test.runOnMainSync(target::finish);
            }
        }
    }
}
