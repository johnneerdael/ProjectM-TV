package com.example.projectm.visualizer;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class TrackWatcherTest {
    @Test
    public void labelJoinsTitleAndArtist() {
        assertEquals("Underground — Silver Panda, Ruback", TrackWatcher.label("Underground", "Silver Panda, Ruback"));
    }

    @Test
    public void labelUsesWhateverIsKnown() {
        assertEquals("Underground", TrackWatcher.label(" Underground ", ""));
        assertEquals("Silver Panda", TrackWatcher.label(null, "Silver Panda"));
        assertEquals("", TrackWatcher.label(null, "  "));
    }

    @Test
    public void trackLabelMatchesTheStaticLabel() {
        TrackWatcher.Track track = new TrackWatcher.Track("Numb", "Massano", null);
        assertEquals("Numb — Massano", track.label());
    }

    @Test
    public void reportsPlaybackThatStartsAgain() {
        assertTrue(TrackWatcher.reportable(false, "Numb — Massano", "Numb — Massano", false));
    }

    @Test
    public void reportsOtherTextOrAnotherCover() {
        assertTrue(TrackWatcher.reportable(true, "Numb — Massano", "Glow — Rebūke", false));
        assertTrue(TrackWatcher.reportable(true, "Numb — Massano", "Numb — Massano", true));
    }

    @Test
    public void staysQuietWhileNothingChanges() {
        assertFalse(TrackWatcher.reportable(true, "Numb — Massano", "Numb — Massano", false));
    }

    @Test
    public void tracksWithTheSameTitleAndArtistAreTheSameTrack() {
        TrackWatcher.Track track = new TrackWatcher.Track("Numb", "Massano", null);
        assertTrue(track.sameAs(new TrackWatcher.Track("Numb", "Massano", null)));
        assertFalse(track.sameAs(new TrackWatcher.Track("Numb", "", null)));
        assertFalse(track.sameAs(null));
    }
}
