package nl.neerdael.projectm.core;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

/** The single Core artifact always retains the public Native capability fields. */
public class RenderingPolicyTest {
    @Test
    public void compiledPolicyAlwaysSupportsNativeRendering() {
        assertEquals("native", RenderingPolicy.NAME);
        assertTrue(RenderingPolicy.NATIVE_ENABLED);
    }
}
