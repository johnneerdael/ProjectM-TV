package nl.neerdael.projectm.core;

import org.junit.Test;
import static org.junit.Assert.*;

public class RenderMemoryBudgetTest {
    @Test public void liveAvailableMemoryAlreadyIncludesCurrentRenderer() {
        MemorySnapshot healthy = new MemorySnapshot(2L << 30, 900L << 20, 128L << 20, false);
        assertTrue(RenderMemoryBudget.canGrow(healthy, 300L << 20, 320L << 20));
        assertFalse(RenderMemoryBudget.canGrow(healthy, 300L << 20, 700L << 20));
    }
    @Test public void trailsAndTwoLivePresetsConsumeLargerBudget() {
        long standard = RenderMemoryBudget.estimatedBytes(3840, 2160, 0, false);
        long medium = RenderMemoryBudget.estimatedBytes(3840, 2160, 1, false);
        long high = RenderMemoryBudget.estimatedBytes(3840, 2160, 2, false);
        assertTrue(medium > standard);
        assertEquals("both detail modes allocate the same textures", medium, high);
        assertEquals(2 * high, RenderMemoryBudget.estimatedBytes(3840, 2160, 2, true));
        assertTrue(RenderMemoryBudget.estimatedBytes(1920, 1080, 2, false) < high);
    }
    @Test public void unknownInvalidAndLowMemoryNeverPermitGrowth() {
        for (MemorySnapshot sample : new MemorySnapshot[]{null,
                new MemorySnapshot(0, 0, 0, false),
                new MemorySnapshot(2L << 30, 3L << 30, 0, false),
                new MemorySnapshot(2L << 30, 1L << 30, -1, false),
                new MemorySnapshot(2L << 30, 1L << 30, 0, true)}) {
            assertFalse(RenderMemoryBudget.canGrow(sample, 0, 1L << 20));
        }
    }
    @Test public void largerDevicesReserveForAndroidPressureRatherThanInstalledRamFraction() {
        assertEquals(256L << 20, RenderMemoryBudget.reserveBytes(
                new MemorySnapshot(3960360L << 10, 740L << 20, 128L << 20, false)));
        assertEquals(256L << 20, RenderMemoryBudget.reserveBytes(
                new MemorySnapshot(8L << 30, 740L << 20, 128L << 20, false)));
        assertEquals(640L << 20, RenderMemoryBudget.reserveBytes(
                new MemorySnapshot(4L << 30, 900L << 20, 512L << 20, false)));
    }
    @Test public void smallerDevicesRetainConservativeReserveAndLargeDeviceBoundaryIsExplicit() {
        assertEquals((2L << 30) / 5, RenderMemoryBudget.reserveBytes(
                new MemorySnapshot(2L << 30, 900L << 20, 128L << 20, false)));
        assertEquals(640L << 20, RenderMemoryBudget.reserveBytes(
                new MemorySnapshot(2L << 30, 1L << 30, 512L << 20, false)));
        long boundary = 3584L << 20;
        assertEquals((boundary - 1) / 5, RenderMemoryBudget.reserveBytes(
                new MemorySnapshot(boundary - 1, 900L << 20, 128L << 20, false)));
        assertEquals(256L << 20, RenderMemoryBudget.reserveBytes(
                new MemorySnapshot(boundary, 900L << 20, 128L << 20, false)));
    }
    @Test public void moderateAvailableMemoryCanGrowButCannotAuthorizeAnUnsafeAllocation() {
        MemorySnapshot sample = new MemorySnapshot(3960360L << 10, 740L << 20, 184L << 20, false);
        long current = RenderMemoryBudget.estimatedBytes(1920, 1080, 0, true);
        assertTrue(RenderMemoryBudget.canGrow(sample, current,
                RenderMemoryBudget.estimatedBytes(2240, 1260, 0, true)));
        assertFalse(RenderMemoryBudget.canGrow(sample, current,
                RenderMemoryBudget.estimatedBytes(3840, 2160, 0, true)));
    }
    @Test public void downshiftSelectsEnoughEstimatedReleaseToRecoverReserve() {
        MemorySnapshot sample = new MemorySnapshot(4L << 30, 200L << 20, 128L << 20, false);
        assertFalse(RenderMemoryBudget.canRecoverByShrinking(sample, 500L << 20, 450L << 20));
        assertTrue(RenderMemoryBudget.canRecoverByShrinking(sample, 500L << 20, 250L << 20));
    }
}
