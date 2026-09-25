package com.example.projectm.visualizer;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

import org.junit.Test;

/** Session candidates and the silence test used to find the player's audio session. */
public class PlayerSessionFinderTest {
    @Test
    public void candidatesStepBackFromTheNewestId() {
        // Measured on a SHIELD: a fresh id of 289 while SoundCloud played on session 217.
        int[] ids = PlayerSessionFinder.candidates(289, 64);
        assertEquals(281, ids[0]);
        assertEquals(217, ids[8]);
        for (int id : ids) assertEquals(1, id % 8);  // stays on session ids
    }

    @Test
    public void candidatesStopAboveZero() {
        assertArrayEquals(new int[]{17, 9, 1}, PlayerSessionFinder.candidates(25, 64));
        assertEquals(0, PlayerSessionFinder.candidates(1, 64).length);
    }

    @Test
    public void candidatesAreCapped() {
        assertEquals(128, PlayerSessionFinder.candidates(100000, 128).length);
    }

    @Test
    public void silenceHasNoLevel() {
        byte[] silence = new byte[128];
        java.util.Arrays.fill(silence, (byte) 128);
        assertEquals(0.0, PlayerSessionFinder.rms(silence, silence.length), 0.0);
    }

    @Test
    public void fullScaleSquareWaveIsLoud() {
        byte[] wave = new byte[4];
        wave[0] = (byte) 255;
        wave[1] = 0;
        wave[2] = (byte) 255;
        wave[3] = 0;
        // Deviations 127 and -128 around the centre.
        assertEquals(Math.sqrt((127 * 127 + 128 * 128) / 2.0), PlayerSessionFinder.rms(wave, 4), 1e-9);
    }
}
