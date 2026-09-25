package com.example.projectm.visualizer;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertTrue;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;

import org.junit.Test;

/** Dynamic-resolution behaviour (runs on the JVM; android.util.Log returns defaults). */
public class QualityControllerTest {
    private int applied = -1;
    private long free = 1L << 32;  // free memory reported by the probe (4 GB: never the limit)

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
        assertEquals(4, QualityController.manualHeights(display(3840, 2160)).length);
        assertEquals(2, QualityController.manualHeights(display(1920, 1080)).length);
        assertEquals(2560, display(3840, 2160).widthForHeight(1440));
    }

    @Test
    public void savedFixedHeightIsValidatedAgainstPanel() throws Exception {
        assertEquals(2160, QualityController.validFixedHeight(display(3840, 2160), 2160));
        assertEquals("4K on a 1080p panel falls back to Auto",
                0, QualityController.validFixedHeight(display(1920, 1080), 2160));
        assertEquals(0, QualityController.validFixedHeight(display(1920, 1080), 480));
        assertEquals(1080, QualityController.validFixedHeight(display(1920, 1080), 1080));
    }

    @Test
    public void changingTargetFpsDropsQueuedChange() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), () -> free, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        settle(q);
        samples(q, 3, 40);
        assertTrue(q.hasPendingChange());
        q.setTargetFps(30);
        assertFalse(q.hasPendingChange());
        q.onPresetChanged();
        assertEquals(1440, q.currentHeight());
    }

    @Test
    public void autoChangesOnlyAtPresetSwitchAndBacksOff() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), () -> free, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        assertEquals(1440, applied);

        settle(q);
        samples(q, 3, 40);
        assertTrue(q.hasPendingChange());
        assertEquals("not applied mid-preset", 1440, applied);
        q.onPresetChanged();
        assertEquals(1260, q.currentHeight());

        settle(q);
        samples(q, 15, 60);
        assertFalse("1440 just failed, so it is backed off", q.hasPendingChange());
        for (int i = 0; i < 10; i++) q.onPresetChanged();
        settle(q);
        samples(q, 15, 60);
        assertTrue("retried once after 10 presets", q.hasPendingChange());
        q.onPresetChanged();
        assertEquals(1440, q.currentHeight());

        settle(q);
        samples(q, 3, 40);
        q.onPresetChanged();
        assertEquals(1260, q.currentHeight());
        for (int i = 0; i < 100; i++) q.onPresetChanged();
        settle(q);
        samples(q, 15, 60);
        assertFalse("a level that failed twice is not tried again this session", q.hasPendingChange());
    }

    @Test
    public void noFixedMemoryCap() throws Exception {
        assertEquals("all panel levels offered", 4, QualityController.manualHeights(display(3840, 2160)).length);
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH, 1941L), () -> free, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 2160);
        assertEquals("a remembered 4K level is kept when memory allows it", 2160, applied);
    }

    @Test
    public void stepsUpOnlyWithFreeMemoryForTheSwitchPeak() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), () -> free, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        assertEquals(1440, applied);
        free = 100L << 20;  // 100 MB: 1440 -> 1800 needs ~64 MB margin + ~75 MB second preset + growth
        settle(q);
        samples(q, 30, 60);
        assertFalse("not enough free memory for the step up", q.hasPendingChange());
        free = 600L << 20;
        samples(q, 15, 60);
        assertTrue("enough free memory now", q.hasPendingChange());
        q.onPresetChanged();
        assertEquals(1800, q.currentHeight());
    }

    @Test
    public void startLevelFitsFreeMemory() throws Exception {
        free = 150L << 20;
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), () -> free, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 2160);
        assertTrue("starts lower than the remembered 4K when memory is tight", applied < 2160);
        assertTrue(applied >= 720);
        free = -1;  // unknown never blocks
        q.setMode(0, 2160);
        assertEquals(2160, applied);
    }

    @Test
    public void memoryPressureBacksOffTemporarily() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), () -> free, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        assertEquals(1440, applied);
        q.onMemoryPressure(10);
        q.onMemoryPressure(15);  // repeated callbacks before the switch count once
        assertTrue(q.hasPendingChange());
        q.onPresetChanged();
        assertEquals(1260, q.currentHeight());
        settle(q);
        samples(q, 30, 60);
        assertFalse("not raised during the back-off", q.hasPendingChange());
        for (int i = 0; i < QualityController.PRESSURE_BACKOFF_PRESETS; i++) q.onPresetChanged();
        settle(q);
        samples(q, 15, 60);
        assertTrue("may climb again after the back-off", q.hasPendingChange());
    }

    @Test
    public void severeSlowdownSwitchesOnceAndDropsTwoLevels() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), () -> free, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        settle(q);
        assertEquals(QualityController.ACTION_SWITCH, samples(q, 4, 25));
        assertNotEquals(QualityController.ACTION_SWITCH, q.onFpsSample(25));
        q.onPresetChanged();
        assertTrue(q.currentHeight() <= 1080);
    }

    @Test
    public void slowPresetsAreSkippedOnlyWhenEnabled() throws Exception {
        QualityController q = new QualityController(display(1920, 1080),
                profile(DeviceProfile.Tier.LOW), () -> free, h -> applied = h);
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
    public void lowTierAutoCanGoBelow720p() throws Exception {
        QualityController q = new QualityController(display(1920, 1080),
                profile(DeviceProfile.Tier.LOW), () -> free, h -> applied = h);
        q.setTargetFps(30);
        q.setMode(0, 0);
        settle(q);
        samples(q, 3, 20);
        q.onPresetChanged();
        assertTrue(q.currentHeight() < 720 && q.currentHeight() >= 360);
    }

    @Test
    public void onlyHeavyPresetsGetALowerHeightWhenMemoryIsShort() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), () -> free, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 1440);
        q.setShownHeight(1440);
        free = 200L << 20;  // enough for a normal switch at 1440 (~48 MB second preset + margin)
        assertEquals("normal preset keeps the auto level", 1440, q.heightForNextPreset(0));
        assertEquals("light preset keeps the auto level", 1440, q.heightForNextPreset(3));
        int heavy = q.heightForNextPreset(120);
        assertTrue("heavy preset rendered lower", heavy < 1440 && heavy >= 720);
        assertEquals("auto level itself unchanged", 1440, q.currentHeight());

        free = 1L << 32;
        assertEquals("heavy preset keeps the level when memory allows", 1440, q.heightForNextPreset(120));
        free = -1;
        assertEquals("unknown free memory never lowers", 1440, q.heightForNextPreset(500));

        q.setMode(1080, 0);
        assertEquals("fixed resolution is the user's choice", 0, q.heightForNextPreset(500));
    }

    @Test
    public void samplesAtAReducedHeavyPresetHeightDoNotMoveTheAutoLevel() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), () -> free, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 1440);
        q.setShownHeight(1080);  // heavy preset running lower
        settle(q);
        samples(q, 30, 60);
        assertFalse("no step up from a heavy preset's frame rate", q.hasPendingChange());
        samples(q, 10, 30);
        assertFalse("no step down either", q.hasPendingChange());
        q.setShownHeight(1440);
        samples(q, 3, 40);
        assertTrue("normal presets drive it again", q.hasPendingChange());
    }
}
