package com.example.projectm.visualizer;

import android.media.audiofx.Visualizer;
import android.os.SystemClock;
import android.util.Log;

import java.util.ArrayList;
import java.util.List;

/**
 * Finds the audio session of the app that is playing music, by probing recent session ids.
 *
 * Why: on some TVs (NVIDIA SHIELD with Dolby output) media audio bypasses the output that the
 * global Visualizer (session 0) and playback capture listen to, so both hear silence. A Visualizer
 * attached to the player's own session is placed on the output that really plays it, so it does
 * receive the music. Players rarely announce their session, and Android 11 does not expose it, so
 * we probe: session ids come from one counter in steps of 8, and a fresh id marks its top.
 *
 * Runs on the audio thread and blocks for up to a few hundred ms per batch.
 */
final class PlayerSessionFinder {
    private static final String TAG = "ProjectMTV";
    private static final int ID_STEP = 8;              // AUDIO_UNIQUE_ID_USE_MAX: ids share one counter
    static final int MAX_CANDIDATES = 128;             // ~1000 ids back: hours of normal use
    private static final int BATCH = 16;
    private static final long SETTLE_MS = 300;         // time for audio to reach a new Visualizer
    static final double MIN_RMS = 2.0;                 // of 128; music is typically 20-70
    // Sessions refused with an error are retried after these delays: on a SHIELD the player's
    // session is refused (INVALID_OPERATION) for a moment after our process restarts.
    private static final long[] RETRY_REFUSED_MS = {500, 1500};

    // Per-search counters for the log line: probes created, not creatable, unreadable, already enabled.
    private static int created, failed, unreadable, shared;
    private static final List<Integer> refused = new ArrayList<>();
    private static double loudest;

    private PlayerSessionFinder() {}

    /** Candidate session ids below {@code top}, newest first. */
    static int[] candidates(int top, int count) {
        int n = Math.max(0, Math.min(count, (top - 1) / ID_STEP));
        int[] ids = new int[n];
        for (int i = 0; i < n; i++) ids[i] = top - ID_STEP * (i + 1);
        return ids;
    }

    /** RMS of an 8-bit unsigned waveform around its centre (128), 0..128. */
    static double rms(byte[] waveform, int length) {
        if (length <= 0) return 0;
        long sum = 0;
        for (int i = 0; i < length; i++) {
            int x = (waveform[i] & 0xFF) - 128;
            sum += (long) x * x;
        }
        return Math.sqrt(sum / (double) length);
    }

    /**
     * Returns the session carrying the loudest signal, or 0 when none does. {@code preferred}
     * (the last session that worked, 0 for none) is tried first; {@code top} is a freshly
     * generated session id.
     */
    static int find(int top, int preferred) {
        long start = SystemClock.elapsedRealtime();
        created = failed = unreadable = shared = 0;
        loudest = 0;
        refused.clear();
        int found = preferred > 0 ? probe(new int[]{preferred}) : 0;
        int tried = preferred > 0 ? 1 : 0;
        int[] ids = candidates(top, MAX_CANDIDATES);
        for (int i = 0; found == 0 && i < ids.length; i += BATCH) {
            int[] batch = new int[Math.min(BATCH, ids.length - i)];
            System.arraycopy(ids, i, batch, 0, batch.length);
            tried += batch.length;
            found = probe(batch);
        }
        for (int r = 0; found == 0 && r < RETRY_REFUSED_MS.length && !refused.isEmpty(); r++) {
            int[] retry = new int[refused.size()];
            for (int i = 0; i < retry.length; i++) retry[i] = refused.get(i);
            refused.clear();
            SystemClock.sleep(RETRY_REFUSED_MS[r]);
            found = probe(retry);
        }
        Log.i(TAG, "Player session search: " + (found > 0 ? "found " + found : "nothing playing")
                + " (" + tried + " ids below " + top + ", " + (SystemClock.elapsedRealtime() - start) + " ms; created "
                + created + ", failed " + failed + ", unreadable " + unreadable + ", shared " + shared
                + String.format(java.util.Locale.US, ", loudest %.1f)", loudest));
        return found;
    }

    /** True when {@code session} carries signal right now (one probe, ~300 ms). */
    static boolean hasSignal(int session) {
        refused.clear();
        return session > 0 && probe(new int[]{session}) == session;
    }

    /** Attaches a short-lived Visualizer to each id and returns the loudest one above MIN_RMS. */
    private static int probe(int[] ids) {
        List<Visualizer> probes = new ArrayList<>();
        List<Integer> probeIds = new ArrayList<>();
        for (int id : ids) {
            Visualizer v;
            try {
                v = new Visualizer(id);
            } catch (RuntimeException e) {
                failed++;  // id not usable (released session, effect limit, or refused for now)
                refused.add(id);
                continue;
            }
            // A Visualizer on a session is shared. If another instance (e.g. one left by our
            // previous process) already enabled it, this one is enabled too, possibly only once we
            // try to configure it: then it can no longer be configured, only read.
            try {
                if (!v.getEnabled()) {
                    v.setCaptureSize(Visualizer.getCaptureSizeRange()[0]);
                    v.setEnabled(true);
                } else {
                    shared++;
                }
            } catch (RuntimeException e) {
                if (!v.getEnabled()) {
                    failed++;
                    v.release();
                    continue;
                }
                shared++;
            }
            probes.add(v);
            probeIds.add(id);
            created++;
        }
        if (probes.isEmpty()) return 0;
        SystemClock.sleep(SETTLE_MS);
        int best = 0;
        double bestRms = MIN_RMS;
        for (int i = 0; i < probes.size(); i++) {
            Visualizer v = probes.get(i);
            try {
                byte[] waveform = new byte[v.getCaptureSize()];
                if (v.getWaveForm(waveform) != Visualizer.SUCCESS) {
                    unreadable++;
                } else {
                    double level = rms(waveform, waveform.length);
                    loudest = Math.max(loudest, level);
                    if (level >= bestRms) {
                        bestRms = level;
                        best = probeIds.get(i);
                    }
                }
            } catch (RuntimeException e) {
                unreadable++;  // released underneath us: treat as silent
            } finally {
                v.release();
            }
        }
        return best;
    }
}
