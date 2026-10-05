package com.example.projectm.visualizer;

import android.app.Activity;
import android.app.Instrumentation;
import android.content.Intent;
import android.os.Bundle;
import android.os.SystemClock;
import android.view.KeyEvent;
import android.view.View;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.HashSet;
import java.util.Set;
import nl.neerdael.projectm.core.ProjectMJNI;

/** Runtime test using only Android framework APIs; adds no dependencies to the app. */
public final class MusicCategoryInstrumentation extends Instrumentation {
    private boolean liveAudio;
    private String setupCase;
    @Override public void onCreate(Bundle arguments) {
        super.onCreate(arguments);
        liveAudio = arguments != null && "true".equals(arguments.getString("live_audio"));
        setupCase = arguments == null ? null : arguments.getString("setup_case");
        start();
    }
    private void check(boolean ok, String message) {
        if (!ok) throw new AssertionError(message);
    }
    private Set<String> members(String category) throws Exception {
        Set<String> names = new HashSet<>();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(
                getTargetContext().getAssets().open("preset-genres/genres/" + category + ".idx")))) {
            String line;
            while ((line = reader.readLine()) != null) names.add(line.split("\t")[0]);
        }
        return names;
    }
    private void awaitCategory(String expected) {
        long deadline = SystemClock.elapsedRealtime() + 15000;
        while (SystemClock.elapsedRealtime() < deadline) {
            if (!ProjectMJNI.isMusicCategoryPending() && expected.equals(ProjectMJNI.getMusicCategory())
                    && !ProjectMJNI.getCurrentPresetName().isEmpty()) return;
            SystemClock.sleep(50);
        }
        throw new AssertionError("category not applied: " + expected + ", actual=" + ProjectMJNI.getMusicCategory());
    }
    @Override public void onStart() {
        if (setupCase != null) {
            if ("native_trails".equals(setupCase)) NativeTrailsSetupTest.run(this);
            else TrackAccessSetupTest.run(this, setupCase);
            return;
        }
        Bundle result = new Bundle();
        Activity activity = null;
        try {
            Intent intent = new Intent(getTargetContext(), MainActivity.class);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            activity = startActivitySync(intent);
            ProjectMJNI.setAutoChange(false);
            ProjectMJNI.setMusicCategory("all");
            awaitCategory("all");
            Set<String> dance = members("dance");
            check(!dance.isEmpty(), "missing dance members");
            ProjectMJNI.setMusicCategory("dance");
            awaitCategory("dance");
            check(dance.contains(ProjectMJNI.getCurrentPresetName()), "out-of-category initial preset");
            int eligible = ProjectMJNI.getCategoryPresetCount("dance");
            check(eligible > 0 && eligible <= dance.size(), "invalid eligible Dance count");
            check(ProjectMJNI.getPresetCount() == eligible, "active count is not category-specific");
            result.putString("dance_members", "packaged=" + dance.size() + ", eligible=" + eligible);
            if (liveAudio) {
                int audible = 0;
                float peak = 0;
                SystemClock.sleep(4000); // allow capture/session discovery to settle
                String name = ProjectMJNI.getCurrentPresetName();
                for (int i = 0; i < 150; i++) {
                    float level = ProjectMJNI.getAudioLevel();
                    if (level > .001f) audible++;
                    peak = Math.max(peak, level);
                    check(dance.contains(ProjectMJNI.getCurrentPresetName()), "live playback escaped Dance");
                    SystemClock.sleep(100);
                }
                result.putString("live_audio", "preset=" + name + ", audible_samples=" + audible
                        + "/150, peak_rms=" + peak);
                check(audible >= 75, "live music was not received reliably: " + audible + "/150 samples");
            }
            for (int i = 0; i < 5; i++) {
                ProjectMJNI.randomPreset(true);
                SystemClock.sleep(300);
                check(dance.contains(ProjectMJNI.getCurrentPresetName()), "random escaped category");
            }
            ProjectMJNI.setMusicCategory("ambient");
            if (ProjectMJNI.getCategoryPresetCount("ambient") > 0) {
                awaitCategory("ambient");
                check(members("ambient").contains(ProjectMJNI.getCurrentPresetName()), "ambient switch failed");
            } else {
                awaitCategory("all");
            }
            Activity target = activity;
            runOnMainSync(() -> {
                View row = target.findViewById(R.id.row_music_category);
                check(row != null && row.isFocusable(), "category row unavailable");
            });
            ProjectMJNI.setMusicCategory("not-a-category");
            awaitCategory("all");
            if (liveAudio) {
                getTargetContext().getSharedPreferences("projectm_settings", 0).edit()
                        .putString("music_category", "dance").apply();
                ProjectMJNI.setMusicCategory("dance");
                awaitCategory("dance");
            }
            result.putString("stream", "PASS: category application, active count, random membership, optional category, focusable row, fallback\n");
            finish(Activity.RESULT_OK, result);
        } catch (Throwable failure) {
            result.putString("stream", "FAIL: " + failure + "\n");
            finish(Activity.RESULT_CANCELED, result);
        } finally {
            if (activity != null) {
                Activity target = activity;
                runOnMainSync(target::finish);
            }
        }
    }
}
