package com.example.projectm.visualizer;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class ExitDiagnosticsTest {
    private static final long NOW = 1_800_000_000_000L;

    private static String pad(String line) {
        StringBuilder padded = new StringBuilder(line);
        while (padded.length() < 383) padded.append(' ');
        return padded.append('\n').toString();
    }

    private static final String TRAIL =
            pad("render pid=4321 ms=" + (NOW - 63_000) + " cache=off compile=on blending into 'Geiss - Spiral.milk' (auto, 7 s, 1152x648)")
            + pad("prewarm pid=4321 ms=" + (NOW - 62_500) + " cache=off compile=on compiling 'Martin - liquid arrows.milk'");

    @Test
    public void parsesFixedWidthTrailLinesAndSkipsCutOnes() {
        List<ExitDiagnostics.TrailLine> lines = ExitDiagnostics.parseTrail(TRAIL + "render pid=99 ms=12");
        assertEquals(2, lines.size());
        assertEquals("render", lines.get(0).thread);
        assertEquals(4321, lines.get(0).pid);
        assertEquals(NOW - 63_000, lines.get(0).timeMs);
        assertEquals("blending into 'Geiss - Spiral.milk' (auto, 7 s, 1152x648)", lines.get(0).message);
        assertEquals("compiling 'Martin - liquid arrows.milk'", lines.get(1).message);
        assertEquals("shader binary cache off, background compile on", lines.get(0).switches);
        // Lines without recorded switches (or an unknown order) keep the whole message.
        ExitDiagnostics.TrailLine plain = ExitDiagnostics.parseTrail("render pid=7 ms=1 loading 'x'").get(0);
        assertEquals(null, plain.switches);
        assertEquals("loading 'x'", plain.message);
        assertTrue(ExitDiagnostics.parseTrail("render pid=x ms=1 broken\n\n").isEmpty());
    }

    @Test
    public void namesReasonsAndSignals() {
        assertEquals("crashed (native code)", ExitDiagnostics.reasonLabel(ExitDiagnostics.REASON_CRASH_NATIVE, 11));
        assertEquals("killed by signal 11 (SIGSEGV)", ExitDiagnostics.reasonLabel(ExitDiagnostics.REASON_SIGNALED, 11));
        assertEquals("killed by signal 6 (SIGABRT)", ExitDiagnostics.reasonLabel(ExitDiagnostics.REASON_SIGNALED, 6));
        assertEquals("killed for low memory", ExitDiagnostics.reasonLabel(ExitDiagnostics.REASON_LOW_MEMORY, 0));
        assertEquals("stopped: app updated", ExitDiagnostics.reasonLabel(16, 0));
        assertEquals("unknown reason", ExitDiagnostics.reasonLabel(99, 0));
        assertTrue(ExitDiagnostics.isProblem(ExitDiagnostics.REASON_ANR));
        assertFalse(ExitDiagnostics.isProblem(10));
    }

    @Test
    public void summaryShowsTheLatestExitWhileOnScreen() {
        ExitDiagnostics.Exit background = new ExitDiagnostics.Exit(5000, 13, 0, 400, NOW - 10_000, 0, 0, "");
        ExitDiagnostics.Exit crash = new ExitDiagnostics.Exit(4321, ExitDiagnostics.REASON_CRASH_NATIVE, 11, 100,
                NOW - 60_000, 300 * 1024, 410 * 1024, "crash");
        assertEquals("Crashed (native code)  ·  60 s ago",
                ExitDiagnostics.summary(Arrays.asList(background, crash), true, NOW));
        assertEquals("None recorded", ExitDiagnostics.summary(Collections.singletonList(background), true, NOW));
        assertEquals("Needs Android 11", ExitDiagnostics.summary(Collections.emptyList(), false, NOW));
    }

    @Test
    public void reportMatchesTrailLinesToTheExitedProcess() {
        ExitDiagnostics.Exit crash = new ExitDiagnostics.Exit(4321, ExitDiagnostics.REASON_CRASH_NATIVE, 11, 100,
                NOW - 60_000, 300 * 1024, 410 * 1024, "crash");
        ExitDiagnostics.Exit other = new ExitDiagnostics.Exit(4000, 10, 0, 100, NOW - 7_200_000, 0, 0, "");
        String report = ExitDiagnostics.report(Arrays.asList(crash, other), true, TRAIL, NOW, "Device\n");
        assertTrue(report, report.startsWith("Device\n"));
        assertTrue(report, report.contains("60 s ago: crashed (native code), on screen\n  crash\n"
                + "  memory: 300 MB PSS, 410 MB RSS\n"
                + "  switches: shader binary cache off, background compile on\n"
                + "  render: blending into 'Geiss - Spiral.milk' (auto, 7 s, 1152x648) (3 s before)\n"
                + "  prewarm: compiling 'Martin - liquid arrows.milk' (2 s before)\n"));
        // The trail belongs to process 4321 only.
        assertTrue(report, report.contains("2 h ago: stopped on request, on screen\n"));
        assertEquals(report.indexOf("render:"), report.lastIndexOf("render:"));
    }

    @Test
    public void reusedPidsGetTheTrailOnlyAtTheFirstExitAfterIt() {
        // Android reused PID 4321: an older exit before the trail was written, a later one after it.
        ExitDiagnostics.Exit older = new ExitDiagnostics.Exit(4321, ExitDiagnostics.REASON_LOW_MEMORY, 0, 100,
                NOW - 3_600_000, 0, 0, "");
        ExitDiagnostics.Exit crash = new ExitDiagnostics.Exit(4321, ExitDiagnostics.REASON_CRASH_NATIVE, 11, 100,
                NOW - 60_000, 0, 0, "");
        ExitDiagnostics.Exit later = new ExitDiagnostics.Exit(4321, 10, 0, 100, NOW - 1_000, 0, 0, "");
        List<ExitDiagnostics.Exit> exits = Arrays.asList(later, crash, older);  // newest first, as Android lists them
        for (ExitDiagnostics.TrailLine line : ExitDiagnostics.parseTrail(TRAIL)) {
            assertEquals(1, ExitDiagnostics.exitForLine(exits, line));
        }
        String report = ExitDiagnostics.report(exits, true, TRAIL, NOW, "");
        assertEquals(report.indexOf("render:"), report.lastIndexOf("render:"));
        assertTrue(report, report.indexOf("render:") > report.indexOf("crashed (native code)"));
        assertTrue(report, report.indexOf("render:") < report.indexOf("killed for low memory"));
        // A trail newer than every exit belongs to the running process: attached to none.
        assertEquals(-1, ExitDiagnostics.exitForLine(Arrays.asList(older),
                ExitDiagnostics.parseTrail(TRAIL).get(0)));
    }

    @Test
    public void switchesComeFromTheNewestLineOfTheProcess() {
        // The render line is older; a switch changed before the prewarm line was written.
        String trail = pad("render pid=4321 ms=" + (NOW - 63_000) + " cache=on compile=on showing 'a.milk' (transition done)")
                + pad("prewarm pid=4321 ms=" + (NOW - 61_000) + " cache=off compile=on compiling 'b.milk'");
        ExitDiagnostics.Exit crash = new ExitDiagnostics.Exit(4321, ExitDiagnostics.REASON_CRASH_NATIVE, 11, 100,
                NOW - 60_000, 0, 0, "");
        String report = ExitDiagnostics.report(Collections.singletonList(crash), true, trail, NOW, "");
        assertTrue(report, report.contains("  switches: shader binary cache off, background compile on\n"));
    }

    @Test
    public void reportWithoutExitRecordsStillShowsTheTrail() {
        String report = ExitDiagnostics.report(Collections.emptyList(), false, TRAIL, NOW, "");
        assertTrue(report, report.contains("Android 11 or later is needed"));
        assertTrue(report, report.contains("Last render: blending into 'Geiss - Spiral.milk'"));
        assertTrue(report, report.contains("Last prewarm: compiling"));
        assertTrue(report, report.contains("(shader binary cache off, background compile on)"));
        assertTrue(ExitDiagnostics.report(Collections.emptyList(), true, "", NOW, "").contains("No exits recorded yet."));
    }

    @Test
    public void agesRoundToReadableUnits() {
        assertEquals("5 s ago", ExitDiagnostics.age(NOW, NOW - 5_000));
        assertEquals("3 min ago", ExitDiagnostics.age(NOW, NOW - 170_000));
        assertEquals("2 h ago", ExitDiagnostics.age(NOW, NOW - 7_000_000));
        assertEquals("3 d ago", ExitDiagnostics.age(NOW, NOW - 3L * 86_400_000));
        assertEquals("0 s ago", ExitDiagnostics.age(NOW, NOW + 5_000));
    }
}
