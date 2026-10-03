package com.example.projectm.visualizer;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class TrackCornerTest {
    @Test
    public void artistOnTopTitleBelow() {
        assertArrayEquals(new String[]{"Massano", "Numb"}, TrackCorner.lines("Numb", "Massano"));
    }

    @Test
    public void staysLeftOfTheSettingsPanel() {
        // 1080p TV at 2x: 960 dp wide, 48 dp margins, 340 dp panel, 24 dp gap → 500 dp
        assertEquals(1000, TrackCorner.maxWidth(1920, 96, 680, 48));
    }

    @Test
    public void neverWiderThanMilkbeatsSixtyPercent() {
        // A wide UI (1280 dp at 1.5x): the panel leaves 820 dp, 60% is 768 dp
        assertEquals(1152, TrackCorner.maxWidth(1920, 72, 510, 36));
    }

    @Test
    public void aLoneTitleOrArtistTakesTheTopLine() {
        assertArrayEquals(new String[]{"Numb", ""}, TrackCorner.lines("Numb", ""));
        assertArrayEquals(new String[]{"Massano", ""}, TrackCorner.lines("", "Massano"));
    }
}
