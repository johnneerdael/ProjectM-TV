package com.example.projectm.visualizer;

import android.app.ActivityManager;
import android.app.ApplicationExitInfo;
import android.content.Context;
import android.os.Build;
import android.util.Log;

import nl.neerdael.projectm.core.ProjectMJNI;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

/**
 * Why the app's process ended before, without adb: Android's exit records (Android 11 and later)
 * next to the engine's trail file, which says what the render and background compile threads were
 * last doing (written by the native engine, see diagnostics_trail.h). Shown under Settings ›
 * Advanced › Last exit.
 */
final class ExitDiagnostics {
    private static final String TAG = "ExitDiagnostics";
    private static final String TRAIL_FILE = "engine_trail.txt";
    private static final int MAX_EXITS = 5;

    // ApplicationExitInfo.REASON_* and ActivityManager.RunningAppProcessInfo.IMPORTANCE_VISIBLE,
    // as literals so the formatting is testable on the JVM and compiles against any SDK level.
    static final int REASON_SIGNALED = 2;
    static final int REASON_LOW_MEMORY = 3;
    static final int REASON_CRASH = 4;
    static final int REASON_CRASH_NATIVE = 5;
    static final int REASON_ANR = 6;
    static final int REASON_INITIALIZATION_FAILURE = 7;
    static final int REASON_EXCESSIVE_RESOURCE_USAGE = 9;
    static final int IMPORTANCE_VISIBLE = 200;

    /** One exit record, independent of the framework class. */
    static final class Exit {
        final int pid;
        final int reason;
        final int status;
        final int importance;
        final long timestampMs;
        final long pssKb;
        final long rssKb;
        final String description;

        Exit(int pid, int reason, int status, int importance, long timestampMs, long pssKb, long rssKb,
             String description) {
            this.pid = pid;
            this.reason = reason;
            this.status = status;
            this.importance = importance;
            this.timestampMs = timestampMs;
            this.pssKb = pssKb;
            this.rssKb = rssKb;
            this.description = description == null ? "" : description;
        }

        /** The app was on screen (not just its notification listener in the background). */
        boolean wasVisible() {
            return importance > 0 && importance <= IMPORTANCE_VISIBLE;
        }
    }

    /**
     * A line of the trail file: which thread, its process, when, the troubleshooting switches of that
     * process ({@code null} if not recorded) and what it was doing.
     */
    static final class TrailLine {
        final String thread;
        final int pid;
        final long timeMs;
        final String switches;
        final String message;

        TrailLine(String thread, int pid, long timeMs, String switches, String message) {
            this.thread = thread;
            this.pid = pid;
            this.timeMs = timeMs;
            this.switches = switches;
            this.message = message;
        }
    }

    /** The previous processes' trail, read before this process's engine starts writing it. */
    private static volatile String previousTrail = "";

    private ExitDiagnostics() {}

    /**
     * From {@code Application.onCreate}: keeps the earlier trail, then hands the file to the engine.
     * The file lives in no-backup storage, so preset names never leave the TV through Android backup
     * or device transfer, and a restored device cannot show another device's trail.
     */
    static void start(Context context) {
        File file = new File(context.getNoBackupFilesDir(), TRAIL_FILE);
        previousTrail = read(file);
        ProjectMJNI.setDiagnosticsFile(file.getAbsolutePath());
    }

    private static String read(File file) {
        if (!file.isFile()) return "";
        byte[] data = new byte[(int) Math.min(file.length(), 16 * 1024)];
        try (FileInputStream in = new FileInputStream(file)) {
            int total = 0;
            while (total < data.length) {
                int n = in.read(data, total, data.length - total);
                if (n < 0) break;
                total += n;
            }
            return new String(data, 0, total, StandardCharsets.UTF_8);
        } catch (IOException e) {
            Log.w(TAG, "Could not read " + file, e);
            return "";
        }
    }

    /** The app's latest exits, newest first (empty before Android 11). */
    static List<Exit> recentExits(Context context) {
        if (Build.VERSION.SDK_INT < 30) return Collections.emptyList();
        List<Exit> exits = new ArrayList<>();
        try {
            ActivityManager manager = context.getSystemService(ActivityManager.class);
            for (ApplicationExitInfo info : manager.getHistoricalProcessExitReasons(
                    context.getPackageName(), 0, MAX_EXITS)) {
                exits.add(new Exit(info.getPid(), info.getReason(), info.getStatus(), info.getImportance(),
                        info.getTimestamp(), info.getPss(), info.getRss(), info.getDescription()));
            }
        } catch (RuntimeException e) {
            Log.w(TAG, "Exit records unavailable", e);
        }
        return exits;
    }

    static List<TrailLine> parseTrail(String text) {
        List<TrailLine> lines = new ArrayList<>();
        for (String raw : text.split("\n")) {
            String line = raw.trim();
            String[] parts = line.split(" ", 4);
            if (parts.length < 4 || !parts[1].startsWith("pid=") || !parts[2].startsWith("ms=")) continue;
            String switches = null;
            String message = parts[3].trim();
            String[] states = message.split(" ", 3);
            if (states.length == 3 && states[0].startsWith("cache=") && states[1].startsWith("compile=")) {
                switches = "shader binary cache " + states[0].substring(6) + ", background compile "
                        + states[1].substring(8);
                message = states[2].trim();
            }
            try {
                lines.add(new TrailLine(parts[0], Integer.parseInt(parts[1].substring(4)),
                        Long.parseLong(parts[2].substring(3)), switches, message));
            } catch (NumberFormatException ignored) {
                // a line cut short by the crash
            }
        }
        return lines;
    }

    static String reasonLabel(int reason, int status) {
        switch (reason) {
            case 1: return "closed itself (status " + status + ")";
            case REASON_SIGNALED: return "killed by signal " + status + signalName(status);
            case REASON_LOW_MEMORY: return "killed for low memory";
            case REASON_CRASH: return "crashed (Java)";
            case REASON_CRASH_NATIVE: return "crashed (native code)";
            case REASON_ANR: return "stopped responding (ANR)";
            case REASON_INITIALIZATION_FAILURE: return "failed to start";
            case 8: return "stopped: permission changed";
            case REASON_EXCESSIVE_RESOURCE_USAGE: return "killed for excessive resource use";
            case 10: return "stopped on request";
            case 11: return "force stopped";
            case 12: return "stopped: a dependency died";
            case 13: return "stopped by the system";
            case 14: return "frozen";
            case 15: return "stopped: package state changed";
            case 16: return "stopped: app updated";
            default: return "unknown reason";
        }
    }

    private static String signalName(int signal) {
        switch (signal) {
            case 4: return " (SIGILL)";
            case 6: return " (SIGABRT)";
            case 7: return " (SIGBUS)";
            case 8: return " (SIGFPE)";
            case 9: return " (SIGKILL)";
            case 11: return " (SIGSEGV)";
            default: return "";
        }
    }

    static boolean isProblem(int reason) {
        return reason == REASON_SIGNALED || reason == REASON_LOW_MEMORY || reason == REASON_CRASH
                || reason == REASON_CRASH_NATIVE || reason == REASON_ANR
                || reason == REASON_INITIALIZATION_FAILURE || reason == REASON_EXCESSIVE_RESOURCE_USAGE;
    }

    static String age(long nowMs, long thenMs) {
        long seconds = Math.max(0, (nowMs - thenMs) / 1000);
        if (seconds < 90) return seconds + " s ago";
        if (seconds < 90 * 60) return (seconds + 30) / 60 + " min ago";
        if (seconds < 36 * 3600) return (seconds + 1800) / 3600 + " h ago";
        return (seconds + 43200) / 86400 + " d ago";
    }

    /** Value of the Last exit row: the latest exit while the app was on screen. */
    static String summary(List<Exit> exits, boolean supported, long nowMs) {
        if (!supported) return "Needs Android 11";
        for (Exit exit : exits) {
            if (exit.wasVisible()) {
                String label = reasonLabel(exit.reason, exit.status);
                return Character.toUpperCase(label.charAt(0)) + label.substring(1) + "  ·  " + age(nowMs, exit.timestampMs);
            }
        }
        return "None recorded";
    }

    /**
     * The exit each trail line belongs to: the earliest exit of the same PID at or after the line was
     * written, or -1. Android reuses PIDs, so a PID alone could also match an older, unrelated exit.
     */
    static int exitForLine(List<Exit> exits, TrailLine line) {
        int best = -1;
        for (int i = 0; i < exits.size(); i++) {
            Exit exit = exits.get(i);
            if (exit.pid != line.pid || exit.timestampMs < line.timeMs) continue;
            if (best < 0 || exit.timestampMs < exits.get(best).timestampMs) best = i;
        }
        return best;
    }

    /** The full report for the Last exit dialog. */
    static String report(List<Exit> exits, boolean supported, String trail, long nowMs, String header) {
        StringBuilder out = new StringBuilder(header);
        List<TrailLine> lines = parseTrail(trail);
        int[] owners = new int[lines.size()];
        for (int i = 0; i < lines.size(); i++) owners[i] = exitForLine(exits, lines.get(i));
        if (!supported) {
            out.append("\nAndroid 11 or later is needed for exit records.\n");
        } else if (exits.isEmpty()) {
            out.append("\nNo exits recorded yet.\n");
        }
        for (int e = 0; e < exits.size(); e++) {
            Exit exit = exits.get(e);
            out.append('\n').append(age(nowMs, exit.timestampMs)).append(": ")
                    .append(reasonLabel(exit.reason, exit.status))
                    .append(exit.wasVisible() ? ", on screen" : ", in the background");
            if (!exit.description.isEmpty()) out.append("\n  ").append(exit.description);
            if (exit.pssKb > 0 || exit.rssKb > 0) {
                out.append(String.format(Locale.US, "\n  memory: %d MB PSS, %d MB RSS", exit.pssKb / 1024, exit.rssKb / 1024));
            }
            // The switches of the process that ended, from its newest trail line (today's settings may differ).
            TrailLine newest = null;
            for (int i = 0; i < lines.size(); i++) {
                TrailLine line = lines.get(i);
                if (owners[i] == e && line.switches != null && (newest == null || line.timeMs > newest.timeMs)) newest = line;
            }
            if (newest != null) out.append("\n  switches: ").append(newest.switches);
            for (int i = 0; i < lines.size(); i++) {
                if (owners[i] != e) continue;
                TrailLine line = lines.get(i);
                out.append("\n  ").append(line.thread).append(": ").append(line.message)
                        .append(" (").append((exit.timestampMs - line.timeMs) / 1000).append(" s before)");
            }
            out.append('\n');
        }
        if (!supported) {
            for (TrailLine line : lines) {
                out.append("\nLast ").append(line.thread).append(": ").append(line.message);
                if (line.switches != null) out.append(" (").append(line.switches).append(')');
            }
        }
        return out.toString();
    }

    static String previousTrail() {
        return previousTrail;
    }
}
