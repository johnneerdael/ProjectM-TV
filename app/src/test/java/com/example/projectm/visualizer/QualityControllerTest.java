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

    private static DisplayInfo display(int width, int height) throws Exception {
        Constructor<DisplayInfo> c = DisplayInfo.class.getDeclaredConstructor(
                int.class, int.class, int.class, int.class, float.class);
        c.setAccessible(true);
        return c.newInstance(width, height, 1920, 1080, 60f);
    }

    private static DeviceProfile profile(DeviceProfile.Tier tier) throws Exception {
        Constructor<DeviceProfile> c = DeviceProfile.class.getDeclaredConstructor(DeviceProfile.Tier.class, long.class);
        c.setAccessible(true);
        return c.newInstance(tier, 3000L);
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
                profile(DeviceProfile.Tier.HIGH), h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        settle(q);
        samples(q, 3, 40);
        assertTrue(q.hasPendingChange());
        q.setTargetFps(30);
        assertFalse(q.hasPendingChange());
        q.onPresetChanged();
        assertEquals(1440, applied);
    }

    @Test
    public void autoChangesOnlyAtPresetSwitchAndBacksOff() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        assertEquals(1440, applied);

        settle(q);
        samples(q, 3, 40);
        assertTrue(q.hasPendingChange());
        assertEquals("not applied mid-preset", 1440, applied);
        q.onPresetChanged();
        assertEquals(1260, applied);

        settle(q);
        samples(q, 15, 60);
        assertFalse("1440 just failed, so it is backed off", q.hasPendingChange());
        for (int i = 0; i < 3; i++) q.onPresetChanged();
        settle(q);
        samples(q, 15, 60);
        assertTrue(q.hasPendingChange());
        q.onPresetChanged();
        assertEquals(1440, applied);
    }

    @Test
    public void severeSlowdownSwitchesOnceAndDropsTwoLevels() throws Exception {
        QualityController q = new QualityController(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        settle(q);
        assertEquals(QualityController.ACTION_SWITCH, samples(q, 4, 25));
        assertNotEquals(QualityController.ACTION_SWITCH, q.onFpsSample(25));
        q.onPresetChanged();
        assertTrue(applied <= 1080);
    }

    @Test
    public void slowPresetsAreSkippedOnlyWhenEnabled() throws Exception {
        QualityController q = new QualityController(display(1920, 1080),
                profile(DeviceProfile.Tier.LOW), h -> applied = h);
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
                profile(DeviceProfile.Tier.LOW), h -> applied = h);
        q.setTargetFps(30);
        q.setMode(0, 0);
        settle(q);
        samples(q, 3, 20);
        q.onPresetChanged();
        assertTrue(applied < 720 && applied >= 360);
    }
}
