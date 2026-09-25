package com.example.projectm.visualizer;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

/** Captured PCM must reach the engine in the Visualizer's format and scale. */
public class PcmConverterTest {
    private static int u8(byte b) {
        return b & 0xFF;
    }

    @Test
    public void silenceIsCentered() {
        byte[] out = new byte[4];
        assertEquals(4, PcmConverter.toUnsignedMono8(new short[8], 8, 2, out));
        for (byte b : out) assertEquals(128, u8(b));
    }

    @Test
    public void quietMusicIsNormalizedLikeTheVisualizer() {
        // Peak of the summed channels is 200 of 65536: scaled so it reaches 0.99 of full range.
        short[] in = {100, 100, -100, -100, 50, 50, 0, 0};
        byte[] out = new byte[4];
        PcmConverter.toUnsignedMono8(in, in.length, 2, out);
        assertEquals(255, u8(out[0]));  // 128 + 0.99 * 128 = 254.7
        assertEquals(1, u8(out[1]));
        assertEquals(191, u8(out[2]));  // half the peak
        assertEquals(128, u8(out[3]));
    }

    @Test
    public void channelsAreSummedBeforeScaling() {
        // Left and right in opposite phase cancel out, as in the Visualizer's mono sum.
        short[] in = {1000, -1000, 2000, 2000};
        byte[] out = new byte[2];
        PcmConverter.toUnsignedMono8(in, in.length, 2, out);
        assertEquals(128, u8(out[0]));
        assertTrue(u8(out[1]) >= 254);
    }

    @Test
    public void partialReadsAndSmallOutputsAreRespected() {
        short[] in = {1000, 1000, 1000, 1000, 1000, 1000};
        byte[] out = new byte[2];
        assertEquals(1, PcmConverter.toUnsignedMono8(in, 3, 2, out));  // 3 samples = 1 full frame
        assertEquals(2, PcmConverter.toUnsignedMono8(in, 6, 2, out));  // limited by the output
    }
}
