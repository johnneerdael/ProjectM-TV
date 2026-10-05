package nl.neerdael.projectm.core;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class VisualizerRendererTest {
    private VisualizerRenderer renderer() {
        return new VisualizerRenderer(new VisualizerRenderer.StatsListener() {
            @Override public void onFpsSample(float fps) { }
            @Override public void onPresetChanged() { }
        });
    }

    @Test
    public void sameSizeNewGenerationCannotRelabelTheOldPerformanceWindow() {
        VisualizerRenderer renderer = renderer();
        assertTrue(Float.isNaN(renderer.sampleRenderedFrameRate(0, 0, 1)));
        assertTrue(Float.isNaN(renderer.sampleRenderedFrameRate(900_000_000L, 27, 1)));
        assertTrue("new budget must discard the old 27 frames",
                Float.isNaN(renderer.sampleRenderedFrameRate(1_000_000_000L, 28, 2)));
        assertTrue(Float.isNaN(renderer.sampleRenderedFrameRate(1_900_000_000L, 55, 2)));
        assertEquals(30f, renderer.sampleRenderedFrameRate(2_000_000_000L, 58, 2), 0.001f);
    }

    @Test
    public void guardCallsDoNotCountAsCompletedFrames() {
        VisualizerRenderer renderer = renderer();
        renderer.sampleRenderedFrameRate(0, 5, 1);
        renderer.sampleRenderedFrameRate(500_000_000L, 5, 1);
        assertEquals(0f, renderer.sampleRenderedFrameRate(1_000_000_000L, 5, 1), 0f);
    }

    @Test
    public void unchangedLegacyGenerationKeepsItsNormalCadence() {
        VisualizerRenderer renderer = renderer();
        renderer.sampleRenderedFrameRate(0, 0, 0);
        renderer.sampleRenderedFrameRate(500_000_000L, 15, 0);
        assertEquals(30f, renderer.sampleRenderedFrameRate(1_000_000_000L, 30, 0), 0.001f);
    }
}
