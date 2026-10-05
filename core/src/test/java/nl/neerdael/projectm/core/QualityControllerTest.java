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

    private static QualityController controller(DisplayInfo display, DeviceProfile profile,
                                                int oldLimit, QualityController.Listener listener) {
        return new QualityController(display, profile, oldLimit, listener,
                () -> new MemorySnapshot(4L << 30, 3L << 30, 128L << 20, false));
    }

    private static final class FakeMemory implements MemoryProvider {
        MemorySnapshot snapshot = new MemorySnapshot(4L << 30, 3L << 30, 128L << 20, false);
        int reads;
        @Override public MemorySnapshot sample() { reads++; return snapshot; }
    }

    private QualityController withMemory(FakeMemory memory, long ramMb) throws Exception {
        return new QualityController(display(3840, 2160), profile(DeviceProfile.Tier.HIGH, ramMb),
                1260, h -> applied = h, memory);
    }

    private static void healthySamples(QualityController q, int count) throws Exception {
        for (int i = 0; i < count; i++) { settle(q); q.onFpsSample(60); }
    }

    private static void endPressureQuiet(QualityController q) throws Exception {
        Field f = QualityController.class.getDeclaredField("pressureQuietUntil");
        f.setAccessible(true);
        f.setLong(q, 0);
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
    public void everySavedModeNormalizesToAutomatic() throws Exception {
        DisplayInfo panel = display(3840, 2160);
        assertEquals(0, QualityController.defaultMode(panel, 1260));
        assertArrayEquals(new int[0], QualityController.manualHeights(panel, 0));
        for (int saved : new int[]{0, -1, 360, 1080, 1330, 2160}) {
            assertEquals(0, QualityController.validFixedHeight(panel, 1260, saved));
            QualityController q = controller(panel, profile(DeviceProfile.Tier.HIGH),
                    1260, h -> applied = h);
            q.setMode(saved, 1800);
            assertTrue(q.isAuto());
            assertTrue(!q.isNative());
            assertEquals("remembered automatic height survives legacy mode migration", 1800, applied);
        }
    }

    @Test
    public void automaticLadderUsesPanelCeilingAndIgnoresInstalledRamLimit() throws Exception {
        QualityController q = controller(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH, 1941), 1260, h -> applied = h);
        q.setMode(0, 2160);
        assertEquals(2160, applied);
        assertEquals(0, profile(DeviceProfile.Tier.HIGH, 1941).memorySafeHeight());
        q = controller(display(1920, 1080), profile(DeviceProfile.Tier.HIGH),
                0, h -> applied = h);
        q.setMode(-1, 2160);
        assertEquals(1080, applied);
        assertEquals(2560, display(3840, 2160).widthForHeight(1440));
    }

    @Test
    public void autoChangesApplyImmediatelyAndBackOff() throws Exception {
        QualityController q = controller(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 0, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        assertEquals(1440, applied);

        settle(q);
        samples(q, 3, 40);
        assertEquals("lowered at once, no preset switch needed", 1260, applied);

        settle(q);
        samples(q, 15, 60);
        assertEquals("the higher level just failed, so it is backed off for this preset", 1260, applied);
        q.onPresetChanged();
        settle(q);
        samples(q, 15, 60);
        assertEquals("retried with the next preset", 1440, applied);

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
        assertEquals("retried after 2 presets", 1440, applied);

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
            assertEquals("retried after " + wait + " presets, never given up", 1440, applied);
        }
    }

    @Test
    public void lowerResolutionThatDoesNotHelpIsUndoneForThePreset() throws Exception {
        QualityController q = controller(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 0, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        settle(q);
        samples(q, 3, 40);
        assertEquals(1260, applied);
        settle(q);
        q.onFpsSample(41);  // hardly faster: the preset is limited by the CPU
        assertEquals("back to the sharper level", 1440, applied);
        settle(q);
        samples(q, 12, 40);
        assertEquals("not lowered again for this preset", 1440, applied);

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
        QualityController q = controller(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 0, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        settle(q);
        q.onPresetChanged();
        samples(q, 10, 20);
        assertEquals("a load and blend are not judged", 1440, applied);
    }

    @Test
    public void memoryPressureLowersOneLevelPerBurstAndCanRecover() throws Exception {
        QualityController q = controller(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 0, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        assertEquals(1440, applied);
        q.onMemoryPressure(10);
        q.onMemoryPressure(10);  // repeated callbacks in one burst count once
        assertEquals("lowered at once", 1260, applied);
        settle(q);
        samples(q, 30, 60);
        assertEquals("a warning burst has a recovery cooldown", 1260, applied);
        endPressureQuiet(q);
        healthySamples(q, 30);
        assertTrue("healthy live headroom releases the temporary ceiling", applied > 1260);
    }

    @Test
    public void memoryPressureLimitIsNotRememberedForTheNextLaunch() throws Exception {
        QualityController q = controller(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 0, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        q.onMemoryPressure(10);
        assertEquals(1260, applied);
        assertEquals("next launch starts at the level chosen for the frame rate",
                1440, q.autoHeightToRemember());

        // A frame-rate drop below the pressure limit is remembered as usual.
        settle(q);
        samples(q, 3, 40);
        assertEquals(1080, applied);
        assertEquals(1080, q.autoHeightToRemember());
    }

    @Test
    public void severeSlowdownLowersTwoLevelsWithoutSwitchingPreset() throws Exception {
        QualityController q = controller(display(3840, 2160),
                profile(DeviceProfile.Tier.HIGH), 0, h -> applied = h);
        q.setTargetFps(60);
        q.setMode(0, 0);
        settle(q);
        assertEquals("no preset switch", QualityController.ACTION_NONE, samples(q, 4, 25));
        assertTrue(applied <= 1080);
    }

    @Test
    public void slowPresetsAreSkippedOnlyWhenEnabled() throws Exception {
        QualityController q = controller(display(1920, 1080),
                profile(DeviceProfile.Tier.LOW), 0, h -> applied = h);
        q.setTargetFps(30);
        q.setSkipSlowPresets(true);
        q.setMode(720, 360);
        assertEquals(360, applied);
        settle(q);
        assertEquals(QualityController.ACTION_SKIP, samples(q, 5, 12));

        q.onPresetChanged();
        q.setSkipSlowPresets(false);
        settle(q);
        assertNotEquals(QualityController.ACTION_SKIP, samples(q, 10, 10));
    }

    @Test
    public void cpuBoundSlowPresetsAreSkippedAboveTheFloor() throws Exception {
        QualityController q = controller(display(1920, 1080),
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
        QualityController q = controller(display(1920, 1080),
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
        QualityController q = controller(display(1920, 1080),
                profile(DeviceProfile.Tier.LOW), 0, h -> applied = h);
        q.setTargetFps(30);
        q.setMode(0, 0);
        settle(q);
        samples(q, 3, 20);
        assertTrue(applied < 720 && applied >= 360);
    }
    @Test
    public void ampleTwoGbHeadroomCanReachFourKWithoutInstalledRamCeiling() throws Exception {
        FakeMemory memory = new FakeMemory();
        memory.snapshot = new MemorySnapshot(2L << 30, 1536L << 20, 128L << 20, false);
        QualityController q = withMemory(memory, 2048);
        q.setMode(0, 0);
        healthySamples(q, 80);
        assertEquals(2160, applied);
        healthySamples(q, 30);
        assertEquals("never grows above the panel", 2160, applied);
    }

    @Test
    public void lowHeadroomFourGbCannotGrowEvenAtTargetFps() throws Exception {
        FakeMemory memory = new FakeMemory();
        memory.snapshot = new MemorySnapshot(4L << 30, 900L << 20, 128L << 20, false);
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 0);
        int start = applied;
        healthySamples(q, 60);
        assertEquals(start, applied);
        assertTrue(q.isMemoryConstrained());
    }

    @Test
    public void lowMemoryIsSampledAndLowersMultipleStepsBeforeFpsSettles() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 4096);
        q.setNativeTrailsLevel(2);
        q.setTransitionSeconds(7);
        q.setMode(0, 2160);
        memory.snapshot = new MemorySnapshot(4L << 30, 450L << 20, 512L << 20, true);
        q.onPresetChanged();
        int reads = memory.reads;
        q.onFpsSample(0);
        assertEquals(reads + 1, memory.reads);
        assertTrue("critical headroom deficit drops multiple ladder steps", applied <= 1440);
        assertTrue(q.wasLastChangeForMemoryPressure());
        assertTrue(q.isMemoryConstrained());
    }

    @Test
    public void unknownMemoryBlocksGrowthButAllowsFpsDownshift() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 1440);
        memory.snapshot = null;
        healthySamples(q, 60);
        assertEquals(1440, applied);
        samples(q, 3, 40);
        assertEquals(1260, applied);
        settle(q);
        q.onFpsSample(40);
        assertEquals("CPU-bound restoration cannot bypass unknown headroom", 1260, applied);
    }

    @Test
    public void recoveryNeedsSustainedHeadroomAndDoesNotChatterAtReserve() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 2160);
        memory.snapshot = new MemorySnapshot(4L << 30, 700L << 20, 128L << 20, false);
        q.onFpsSample(60);
        int reduced = applied;
        assertTrue(reduced < 2160);
        endPressureQuiet(q);
        for (int i = 0; i < 40; i++) {
            memory.snapshot = new MemorySnapshot(4L << 30, (i % 2 == 0 ? 870L : 850L) << 20,
                    128L << 20, false);
            settle(q);
            q.onFpsSample(60);
        }
        assertEquals("marginal headroom does not oscillate", reduced, applied);
        memory.snapshot = new MemorySnapshot(4L << 30, 3L << 30, 128L << 20, false);
        healthySamples(q, 80);
        assertEquals(2160, applied);
        assertTrue(!q.wasLastChangeForMemoryPressure());
    }

    @Test
    public void criticalTrimBypassesBurstDebounce() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 2160);
        q.onMemoryPressure(10);
        int first = applied;
        q.onMemoryPressure(15);
        assertTrue(applied < first);
    }

    @Test
    public void fpsTargetChangeResetsGoodSampleWindow() throws Exception {
        QualityController q = controller(display(3840, 2160), profile(DeviceProfile.Tier.HIGH),
                0, h -> applied = h);
        q.setMode(0, 1440);
        healthySamples(q, 14);
        q.setTargetFps(30);
        settle(q);
        samples(q, 14, 30);
        assertEquals(1440, applied);
        q.onFpsSample(30);
        assertEquals(1800, applied);
    }

    @Test
    public void allDeviceTiersCanEventuallyUseTheFullPanel() throws Exception {
        for (DeviceProfile.Tier tier : DeviceProfile.Tier.values()) {
            QualityController q = controller(display(3840, 2160), profile(tier, 1024),
                    720, h -> applied = h);
            q.setMode(0, 0);
            healthySamples(q, 160);
            assertEquals(tier.toString(), 2160, applied);
        }
    }

    @Test
    public void enablingHighTrailsRechecksAdditionalMemoryBeforeKeepingFourK() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 2160);
        memory.snapshot = new MemorySnapshot(4L << 30, 1000L << 20, 128L << 20, false);
        q.setNativeTrailsLevel(2);
        assertTrue("detail allocation must retain protected headroom", applied < 2160);
        assertTrue(q.wasLastChangeForMemoryPressure());
    }

    @Test
    public void enablingTransitionsBudgetsBothPresetsBeforeKeepingFourK() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 2160);
        memory.snapshot = new MemorySnapshot(4L << 30, 1100L << 20, 128L << 20, false);
        q.setTransitionSeconds(7);
        assertTrue("a blend reserves a second complete preset", applied < 2160);
        assertTrue(q.wasLastChangeForMemoryPressure());
    }

    @Test
    public void unknownStartupCannotRestoreAnUnbudgetedSavedFourK() throws Exception {
        FakeMemory memory = new FakeMemory();
        memory.snapshot = null;
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 2160);
        assertEquals(1440, applied);
        assertTrue(q.isMemoryConstrained());
    }

    @Test
    public void cpuBoundPresetStillLowersImmediatelyForMemory() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 1440);
        settle(q);
        samples(q, 3, 40);
        settle(q);
        q.onFpsSample(40);
        assertEquals(1440, applied);
        memory.snapshot = new MemorySnapshot(4L << 30, 700L << 20, 128L << 20, false);
        q.onFpsSample(40);
        assertTrue(applied < 1440);
        assertTrue(q.wasLastChangeForMemoryPressure());
    }

    @Test
    public void restoredUnknownHeadroomStillNeedsSustainedSafeGrowthSamples() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 1440);
        memory.snapshot = null;
        healthySamples(q, 40);
        memory.snapshot = new MemorySnapshot(4L << 30, 3L << 30, 128L << 20, false);
        healthySamples(q, 14);
        assertEquals("unknown samples cannot accumulate upscale credit", 1440, applied);
        healthySamples(q, 3);
        assertEquals(1800, applied);
    }

    @Test
    public void candidateHeadroomThatAlternatesDoesNotAccumulateUpscaleCredit() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 1440);
        for (int i = 0; i < 40; i++) {
            memory.snapshot = new MemorySnapshot(4L << 30, (i % 2 == 0 ? 1200L : 900L) << 20,
                    128L << 20, false);
            settle(q);
            q.onFpsSample(60);
        }
        assertEquals("a growth candidate needs consecutive safe headroom", 1440, applied);
    }

    @Test
    public void resumeWithPreservedContextRechecksLostHeadroomBeforeRendering() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 2160);
        q.onFpsSample(60); // The preserved context has rendered and owns its allocation.
        memory.snapshot = new MemorySnapshot(4L << 30, 650L << 20, 128L << 20, false);
        int reads = memory.reads;
        q.revalidateForResume(false);
        assertEquals("resume must take a fresh sample", reads + 1, memory.reads);
        assertTrue(applied < 2160);
        assertTrue(q.wasLastChangeForMemoryPressure());
        assertEquals("temporary pressure is not permanently remembered", 2160, q.autoHeightToRemember());
        int reduced = applied;
        memory.snapshot = new MemorySnapshot(4L << 30, 3L << 30, 128L << 20, false);
        samples(q, 30, 60);
        assertEquals("resume gives the frame rate time to settle", reduced, applied);
        endPressureQuiet(q);
        healthySamples(q, 110); // Six 15-sample ladder steps from the conservative floor.
        assertEquals("a healthy system releases the resume pressure ceiling", 2160, applied);
    }

    @Test
    public void recreatedContextBudgetsFullReplacementRatherThanOnlyExistingFootprint() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController preserved = withMemory(memory, 4096);
        preserved.setMode(0, 2160);
        preserved.onFpsSample(60);
        QualityController recreated = withMemory(memory, 4096);
        recreated.setMode(0, 2160);
        memory.snapshot = new MemorySnapshot(4L << 30, 1100L << 20, 128L << 20, false);
        preserved.revalidateForResume(false);
        assertEquals("already allocated 4K fits existing headroom", 2160, preserved.currentHeight());
        recreated.revalidateForResume(true);
        assertEquals("full 4K replacement would cross the reserve", 1440, recreated.currentHeight());
        assertEquals("listener resized before any stats or first frame", 1440, applied);
        assertTrue(recreated.wasLastChangeForMemoryPressure());
    }

    @Test
    public void invalidResumeMemoryUsesConservativeFloorForBothContextPaths() throws Exception {
        for (boolean recreated : new boolean[]{false, true}) {
            for (MemorySnapshot invalid : new MemorySnapshot[]{null,
                    new MemorySnapshot(0, 0, 0, false),
                    new MemorySnapshot(2L << 30, 3L << 30, 0, false)}) {
                FakeMemory memory = new FakeMemory();
                QualityController q = withMemory(memory, 4096);
                q.setMode(0, 2160);
                memory.snapshot = invalid;
                q.revalidateForResume(recreated);
                assertEquals("unknown headroom cannot rebuild or resume 4K blindly", 720, applied);
                assertTrue(q.isMemoryConstrained());
            }
        }
    }

    @Test
    public void resumeClearsStaleUpscaleCreditAndReappliesHeightForConfigurationAck() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 1440);
        healthySamples(q, 16);
        assertEquals(1440, applied);
        applied = -1;
        q.revalidateForResume(false);
        assertEquals("host gets configuration acknowledgement even at unchanged height", 1440, applied);
        healthySamples(q, 16);
        assertEquals("paused FPS/headroom samples give no credit", 1440, applied);
        healthySamples(q, 1);
        assertEquals(1800, applied);
    }

    @Test
    public void recreatedContextBudgetsSelectedTrailsAndTwoLivePresets() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 4096);
        q.setNativeTrailsLevel(2);
        q.setTransitionSeconds(7);
        q.setMode(0, 2160);
        memory.snapshot = new MemorySnapshot(4L << 30, 1100L << 20, 128L << 20, false);
        q.revalidateForResume(true);
        assertTrue("both live presets and trails must fit before allocation", applied <= 1080);
        assertTrue(q.isMemoryConstrained());
    }

    @Test
    public void settingsBeforeFirstRenderedSampleBudgetTheFullStartupAllocation() throws Exception {
        FakeMemory memory = new FakeMemory();
        memory.snapshot = new MemorySnapshot(4L << 30, 1300L << 20, 128L << 20, false);
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 2160);
        assertEquals("the full Standard allocation fits", 2160, applied);
        q.setNativeTrailsLevel(2);
        assertEquals("unallocated Standard textures cannot be credited toward High", 1800, applied);
        assertTrue(q.wasLastChangeForMemoryPressure());
    }

    @Test
    public void aConfirmedPositiveRenderedSampleAllowsIncrementalSettingsBudget() throws Exception {
        FakeMemory memory = new FakeMemory();
        memory.snapshot = new MemorySnapshot(4L << 30, 1300L << 20, 128L << 20, false);
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 2160);
        q.onPresetChanged(); // A confirmed draw can arrive inside the FPS settle period.
        q.onFpsSample(60);
        q.setNativeTrailsLevel(2);
        assertEquals("resident Standard RAM is already absent from available memory", 2160, applied);
    }

    @Test
    public void aZeroSampleCannotConfirmTheStartupAllocation() throws Exception {
        FakeMemory memory = new FakeMemory();
        memory.snapshot = new MemorySnapshot(4L << 30, 1300L << 20, 128L << 20, false);
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 2160);
        q.onFpsSample(0);
        q.setNativeTrailsLevel(2);
        assertEquals(1800, applied);
    }

    @Test
    public void contextRecreationRequiresFullBudgetAgainUntilAConfirmedFrame() throws Exception {
        FakeMemory memory = new FakeMemory();
        memory.snapshot = new MemorySnapshot(4L << 30, 1300L << 20, 128L << 20, false);
        QualityController q = withMemory(memory, 4096);
        q.setMode(0, 2160);
        q.onFpsSample(60);
        q.revalidateForResume(true);
        assertEquals(2160, applied);
        q.setNativeTrailsLevel(2);
        assertEquals("previous-context allocations cannot credit the replacement", 1800, applied);
    }

    @Test
    public void equalTopologyMediumToHighDoesNotRebudgetThePendingAllocation() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 4096);
        q.setNativeTrailsLevel(1);
        q.setMode(0, 2160);
        int reads = memory.reads;
        memory.snapshot = null;
        q.setNativeTrailsLevel(2);
        assertEquals("gain changes reuse the same detail allocations", 2160, applied);
        assertEquals(reads, memory.reads);
    }

    @Test
    public void batchedUnallocatedTrailsAndBlendCannotSpendResidentCreditTwice() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 2048);
        q.setMode(0, 2160);
        q.onFpsSample(60); // Standard/no-blend resources are genuinely resident.
        memory.snapshot = new MemorySnapshot(2L << 30, 1050L << 20, 128L << 20, false);
        q.setTransitionSeconds(10);
        q.setNativeTrailsLevel(2);
        // Setters describe desired settings; neither intermediate allocation has reached GL.
        assertEquals("sequential incremental reviews alone are insufficient", 2160, applied);
        q.revalidateForResume(true);
        assertEquals("full final-tuple review cannot credit unallocated RAM", 1440, applied);
        q.setNativeTrailsLevel(0);
        q.setTransitionSeconds(0);
        q.setNativeTrailsLevel(2);
        q.setTransitionSeconds(10);
        q.revalidateForResume(true);
        assertEquals("rapid unpublished edits still require the full final budget", 1440, applied);
    }

    @Test
    public void confirmedAllocationReductionsPreserveResidentHeight() throws Exception {
        for (boolean removeTrails : new boolean[]{true, false}) {
            FakeMemory memory = new FakeMemory();
            QualityController q = withMemory(memory, 2048);
            q.setNativeTrailsLevel(2);
            q.setTransitionSeconds(10);
            q.setMode(0, 2160);
            q.onFpsSample(60);
            memory.snapshot = new MemorySnapshot(2L << 30, 700L << 20, 128L << 20, false);
            q.setRenderAllocationSettings(removeTrails ? 0 : 2, removeTrails ? 10 : 0);
            q.revalidateForResume(false);
            assertEquals("freeing resident allocations must not debit a full replacement", 2160, applied);
        }
    }

    @Test
    public void oppositeSettingsChangesReviewTheirFinalNetReduction() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 2048);
        q.setTransitionSeconds(10);
        q.setMode(0, 2160);
        q.onFpsSample(60);
        memory.snapshot = new MemorySnapshot(2L << 30, 650L << 20, 128L << 20, false);
        q.setRenderAllocationSettings(2, 0);
        q.revalidateForResume(false);
        assertEquals("High without blending is cheaper than Standard with blending", 2160, applied);
    }

    @Test
    public void pendingReductionsAndRapidGrowthDoNotInventResidentCredit() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 4096);
        q.setRenderAllocationSettings(2, 10);
        q.setMode(0, 2160); // No confirmed rendered sample yet.
        memory.snapshot = new MemorySnapshot(4L << 30, 1300L << 20, 128L << 20, false);
        q.setRenderAllocationSettings(2, 0);
        q.revalidateForResume(false);
        assertEquals("an unrendered reduction still needs the full remaining allocation", 1800, applied);
        q.setRenderAllocationSettings(0, 10);
        q.revalidateForResume(true);
        assertEquals("rapid growth cannot credit the unrendered intermediate tuple", 1440, applied);
    }

    @Test
    public void unknownMemoryCannotAuthorizeAResidentReductionAtFullHeight() throws Exception {
        FakeMemory memory = new FakeMemory();
        QualityController q = withMemory(memory, 2048);
        q.setRenderAllocationSettings(2, 10);
        q.setMode(0, 2160);
        q.onFpsSample(60);
        memory.snapshot = null;
        q.setRenderAllocationSettings(0, 0);
        q.revalidateForResume(false);
        assertTrue("a missing memory sample remains conservative", applied < 2160);
    }

}
