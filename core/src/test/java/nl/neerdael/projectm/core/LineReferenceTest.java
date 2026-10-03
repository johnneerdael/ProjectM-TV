package nl.neerdael.projectm.core;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

import org.junit.Test;

/** Line thickness setting: option index to the engine's line reference size. */
public class LineReferenceTest {
    @Test
    public void defaultIsMilkDropsAuthoringResolution() {
        assertEquals(0, LineReference.DEFAULT_INDEX);
        assertArrayEquals(new int[]{1024, 768}, LineReference.size(LineReference.DEFAULT_INDEX));
        assertEquals("MilkDrop (1024×768)", LineReference.LABELS[0]);
    }

    @Test
    public void secondOptionIs1080p() {
        assertEquals(2, LineReference.LABELS.length);
        assertEquals("1080p", LineReference.LABELS[1]);
        assertArrayEquals(new int[]{1920, 1080}, LineReference.size(1));
    }

    @Test
    public void unknownSavedIndexFallsBackToDefault() {
        assertEquals(0, LineReference.validIndex(-1));
        assertEquals(0, LineReference.validIndex(7));
        assertEquals(1, LineReference.validIndex(1));
        assertArrayEquals(new int[]{1024, 768}, LineReference.size(5));
    }
}
