package nl.neerdael.projectm.core;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertTrue;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;

import org.junit.Test;

/** Dynamic-resolution behaviour (runs on the JVM; android.util.Log returns defaults). */
public class QualityControllerTest {
    private int applied = -1;

    private static DisplayInfo display(int width, int height) throws Exception {
        Constructor<DisplayInfo> c = DisplayInfo.class.getDeclaredConstructor(
                int.class, int.class, int.class, int.class, float.class);
        c.setAccessible(true);
        return c.newInstance(width, height, 1920, 1080, 60f);
    }

    private static DeviceProfile profile(DeviceProfile.Tier tier) throws Exception {
        return profile(tier, 4096L);
    }

    private static DeviceProfile profile(DeviceProfile.Tier tier, long ramMb) throws Exception {
        Constructor<DeviceProfile> c = DeviceProfile.class.getDeclaredConstructor(DeviceProfile.Tier.class, long.class);
        c.setAccessible(true);
        return c.newInstance(tier, ramMb);
    }

    /** Skips the settle period that follows a preset change. */
    private static void settle(QualityController q) throws Exception {
        Field f = QualityController.class.getDeclaredField("settleUntil");
        f.setAccessible(true);
        f.setLong(q, 0);
    }

    private static int samples(QualityController q, int count, float fps) {
        int action = QualityController.ACTION_NONE;
        for (int i = 0; i < count; i++) action = q.onFpsSample(fps);
        return action;
    }

    @Test
    public void manualLevelsFollowPhysicalPanel() throws Exception {
        assertArrayEquals(new int[]{720, 1080, 1330, QualityController.NATIVE_HEIGHT}, QualityController.manualHeights(display(3840, 2160), 0));
        assertArrayEquals(new int[]{720, 1080}, QualityController.manualHeights(display(1920, 1080), 0));
        assertEquals(2560, display(3840, 2160).widthForHeight(1440));
    }

    @Test
    public void savedFixedHeightIsValidatedAgainstPanel() throws Exception {
        assertEquals("4K saved before the cap is the cap", 1330, QualityController.validFixedHeight(display(3840, 2160), 0, 2160));
        assertEquals("4K on a 1080p panel falls back to Auto",
                0, QualityController.validFixedHeight(display(1920, 1080), 0, 2160));
        assertEquals(0, QualityController.validFixedHeight(display(1920, 1080), 0, 480));
        assertEquals(1080, QualityController.validFixedHeight(display(1920, 1080), 0, 1080));
        assertEquals("4K above the memory limit falls back to Auto",
                0, QualityController.validFixedHeight(display(3840, 2160), 1260, 2160));
    }

    @Test
    public void autoAndLegacyFixedHeightsStayCapped() throws Exception {
        assertEquals(1330, QualityController.RENDER_HEIGHT_CAP);
        // Auto and saved numeric heights keep the cap; Native is a separate explicit option.
        assertArrayEquals(new int[]{720, 1080, 1330, QualityController.NATIVE_HEIGHT}, QualityController.manualHeights(display(2560, 1440), 0));
        assertEquals(1330, QualityController.validFixedHeight(display(3840, 2160), 0, 1440));
        assertEquals(1330, QualityController.validFixedHeight(display(2560, 1440), 0, 1440));
        assertEquals(1080, QualityController.validFixedHeight(display(3840, 2160), 0, 1080));
        assertEquals(0, QualityController.validFixedHeight(display(3840, 2160), 0, 0));
        // A memory limit below the cap still wins.
        assertArrayEquals(new int[]{720, 1080}, QualityController.manualHeights(display(3840, 2160), 1080));

        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 0, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(2160, 0);
        assertEquals("a fixed 4K passed in directly is not trusted either", 1330, applied);
        q.setMode(0, 2160);
        assertEquals("a remembered 4K auto level is clamped", 1330, applied);
        settle(q);
        samples(q, 30, 60);
        assertEquals("no headroom probe above the cap", 1330, applied);
    }

    @Test
    public void autoChangesApplyImmediatelyAndBackOff() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 0, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        assertEquals(1330, applied);

        settle(q);
        samples(q, 3, 40);
        assertEquals("lowered at once, no preset switch needed", 1260, applied);

        settle(q);
        samples(q, 15, 60);
        assertEquals("the cap just failed, so it is backed off for this preset", 1260, applied);
        q.onPresetChanged();
        settle(q);
        samples(q, 15, 60);
        assertEquals("retried with the next preset", 1330, applied);

        settle(q);
        samples(q, 3, 40);
        assertEquals("failed a second time", 1260, applied);
        q.onPresetChanged();
        settle(q);
        samples(q, 15, 60);
        assertEquals("now backed off for 2 presets", 1260, applied);
        q.onPresetChanged();
        settle(q);
        samples(q, 15, 60);
        assertEquals("retried after 2 presets", 1330, applied);

        for (int failure = 3; failure <= 8; failure++) {  // keeps failing: the wait grows to 16 presets
            settle(q);
            samples(q, 3, 40);
            assertEquals(1260, applied);
            int wait = Math.min(16, 1 << Math.min(4, failure - 1));
            for (int i = 0; i < wait - 1; i++) q.onPresetChanged();
            settle(q);
            samples(q, 15, 60);
            assertEquals("still backed off after " + (wait - 1) + " presets", 1260, applied);
            q.onPresetChanged();
            settle(q);
            samples(q, 15, 60);
            assertEquals("retried after " + wait + " presets, never given up", 1330, applied);
        }
    }

    @Test
    public void lowerResolutionThatDoesNotHelpIsUndoneForThePreset() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 0, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        settle(q);
        samples(q, 3, 40);
        assertEquals(1260, applied);
        settle(q);
        q.onFpsSample(41);  // hardly faster: the preset is limited by the CPU
        assertEquals("back to the sharper level", 1330, applied);
        settle(q);
        samples(q, 12, 40);
        assertEquals("not lowered again for this preset", 1330, applied);

        q.onPresetChanged();
        settle(q);
        samples(q, 3, 40);
        assertEquals("the next preset may be lowered again", 1260, applied);
        settle(q);
        q.onFpsSample(55);  // clearly faster: kept
        assertEquals(1260, applied);
    }

    @Test
    public void newPresetAndNewLevelAreGivenTimeToSettle() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 0, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        settle(q);
        q.onPresetChanged();
        samples(q, 10, 20);
        assertEquals("a load and blend are not judged", 1330, applied);
    }

    @Test
    public void memoryLimitCapsAutoAndManualLevels() throws Exception {
        DeviceProfile twoGb = profile(DeviceProfile.Tier.HIGH, 1941L);
        assertEquals(1260, twoGb.memorySafeHeight());
        assertEquals(0, profile(DeviceProfile.Tier.HIGH, 4096L).memorySafeHeight());
        int[] manual = QualityController.manualHeights(display(3840, 2160), 1260);
        assertEquals(1260, manual[manual.length - 1]);

        QualityController q = new QualityController(display(3840, 2160), twoGb, 1260, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 2160);
        assertEquals("a remembered 4K auto level is clamped", 1260, applied);
        settle(q);
        samples(q, 30, 60);
        assertEquals("no headroom probe above the limit", 1260, applied);
    }

    @Test
    public void memoryPressureLowersOneLevelPerBurstForTheSession() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 0, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        assertEquals(1330, applied);
        q.onMemoryPressure(10);
        q.onMemoryPressure(15);  // repeated callbacks in one burst count once
        assertEquals("lowered at once", 1260, applied);
        settle(q);
        samples(q, 30, 60);
        assertEquals("never raised above the lowered limit", 1260, applied);
    }

    @Test
    public void memoryPressureLimitIsNotRememberedForTheNextLaunch() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 0, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        q.onMemoryPressure(10);
        assertEquals(1260, applied);
        assertEquals("next launch starts at the level chosen for the frame rate",
                1330, q.autoHeightToRemember());

        // A frame-rate drop below the pressure limit is remembered as usual.
        settle(q);
        samples(q, 3, 40);
        assertEquals(1080, applied);
        assertEquals(1080, q.autoHeightToRemember());
    }

    @Test
    public void severeSlowdownLowersTwoLevelsWithoutSwitchingPreset() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 0, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        settle(q);
        assertEquals("no preset switch", QualityController.ACTION_NONE, samples(q, 4, 25));
        assertTrue(applied <= 1080);
    }

    @Test
    public void slowPresetsAreSkippedOnlyWhenEnabled() throws Exception {
        QualityController q = new QualityController(display(1920, 1080),
                profile(DeviceProfile.Tier.LOW), 0, h -> applied = h);
        q.setTargetFps(30);
        q.setSkipSlowPresets(true);
        q.setMode(720, 0);
        assertEquals(720, applied);
        settle(q);
        assertEquals(QualityController.ACTION_SKIP, samples(q, 5, 12));

        q.onPresetChanged();
        q.setSkipSlowPresets(false);
        settle(q);
        assertNotEquals(QualityController.ACTION_SKIP, samples(q, 10, 10));
    }

    @Test
    public void cpuBoundSlowPresetsAreSkippedAboveTheFloor() throws Exception {
        QualityController q = new QualityController(display(1920, 1080),
                profile(DeviceProfile.Tier.STANDARD), 0, h -> applied = h);
        q.setTargetFps(30);
        q.setSkipSlowPresets(true);
        q.setMode(0, 0);
        assertEquals(1080, applied);
        settle(q);
        samples(q, 3, 7);
        assertEquals("lowered", 720, applied);
        settle(q);
        assertEquals("far below target and a lower resolution does not help: skipped at once",
                QualityController.ACTION_SKIP, q.onFpsSample(5));
        assertEquals("the next preset starts at the sharper level", 1080, applied);
    }

    @Test
    public void cpuBoundPresetsAtAWatchableRateAreKept() throws Exception {
        QualityController q = new QualityController(display(1920, 1080),
                profile(DeviceProfile.Tier.STANDARD), 0, h -> applied = h);
        q.setTargetFps(30);
        q.setSkipSlowPresets(true);
        q.setMode(0, 0);
        settle(q);
        samples(q, 3, 20);
        assertEquals("one step down: slow, not severe", 900, applied);
        settle(q);
        assertEquals("CPU-bound but above half the target: kept", QualityController.ACTION_NONE, q.onFpsSample(20));
        settle(q);
        assertNotEquals(QualityController.ACTION_SKIP, samples(q, 10, 20));
    }

    @Test
    public void lowTierAutoCanGoBelow720p() throws Exception {
        QualityController q = new QualityController(display(1920, 1080),
                profile(DeviceProfile.Tier.LOW), 0, h -> applied = h);
        q.setTargetFps(30);
        q.setMode(0, 0);
        settle(q);
        samples(q, 3, 20);
        assertTrue(applied < 720 && applied >= 360);
    }
    @Test
    public void nativeIsAnExplicitOptionAboveTheCap() throws Exception {
        assertArrayEquals(new int[]{720, 1080, 1330, QualityController.NATIVE_HEIGHT},
                QualityController.manualHeights(display(3840, 2160), 0));
        assertArrayEquals(new int[]{720, 1080, 1330, QualityController.NATIVE_HEIGHT},
                QualityController.manualHeights(display(2560, 1440), 0));
        assertArrayEquals(new int[]{720, 1080}, QualityController.manualHeights(display(1920, 1080), 0));
        assertEquals(QualityController.NATIVE_HEIGHT,
                QualityController.validFixedHeight(display(3840, 2160), 0, QualityController.NATIVE_HEIGHT));
        assertEquals(1330, QualityController.validFixedHeight(display(3840, 2160), 0, 2160));
    }

    @Test
    public void nativeRendersAtPhysicalPanelHeightAndKeepsAutoCapped() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 0, h -> applied = h);
        q.setMode(QualityController.NATIVE_HEIGHT, 0);
        assertEquals(2160, applied);
        assertEquals(3840, display(3840, 2160).widthForHeight(applied));
        assertTrue(q.isNative());
        assertTrue(!q.isAuto());
        settle(q);
        samples(q, 20, 10);
        assertEquals("a fixed Native selection does not enter the Auto ladder", 2160, applied);
        q.setMode(0, 2160);
        assertEquals(1330, applied);
        assertTrue(!q.isNative());
        assertTrue(q.isAuto());
    }

    @Test
    public void nativeRespectsMemoryAndChangedPanels() throws Exception {
        assertEquals(0, QualityController.validFixedHeight(display(3840, 2160), 1260, QualityController.NATIVE_HEIGHT));
        assertEquals(0, QualityController.validFixedHeight(display(3840, 2160), 1440, QualityController.NATIVE_HEIGHT));
        assertEquals(0, QualityController.validFixedHeight(display(1920, 1080), 0, QualityController.NATIVE_HEIGHT));
        assertArrayEquals(new int[]{720, 1080, 1330}, QualityController.manualHeights(display(3840, 2160), 1440));
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 1260, h -> applied = h);
        q.setMode(QualityController.NATIVE_HEIGHT, 0);
        assertTrue(q.isAuto());
        assertTrue(applied <= 1260);
    }

}
