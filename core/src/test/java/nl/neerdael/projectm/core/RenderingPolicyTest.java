package nl.neerdael.projectm.core;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

/** Checks the compiled AAR policy against the property selected for this test invocation. */
public class RenderingPolicyTest {
    @Test
    public void compiledPolicyMatchesRequestedBuild() {
        String expected = System.getProperty("projectmCoreRenderingPolicy", "native");
        assertEquals(expected, RenderingPolicy.NAME);
        assertEquals("native".equals(expected), RenderingPolicy.NATIVE_ENABLED);
        assertTrue("native".equals(RenderingPolicy.NAME) || "capped".equals(RenderingPolicy.NAME));
    }
}
