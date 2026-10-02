package com.example.projectm.visualizer;

import org.junit.Test;
import static org.junit.Assert.*;

public class MusicCategoriesTest {
    @Test public void onlyAvailableGenresAreSelectable() {
        String[] ids = MusicCategories.available(id -> "all".equals(id) ? 14 : "dance".equals(id) ? 3 : 0);
        assertArrayEquals(new String[]{"all", "dance"}, ids);
        assertEquals("Dance", MusicCategories.label("dance"));
    }
    @Test public void unknownPersistenceFallsBackToAll() {
        assertEquals("all", MusicCategories.normalize("nonexistent"));
        assertEquals("all", MusicCategories.normalize(null));
        assertEquals("ambient", MusicCategories.normalize("ambient"));
    }
    @Test public void pendingRequestDoesNotBecomeFalseFallback() {
        assertEquals("dance", MusicCategories.appliedSelection("dance", "all", true));
        assertEquals("all", MusicCategories.appliedSelection("dance", "all", false));
        assertEquals("dance", MusicCategories.appliedSelection("dance", "dance", false));
    }
    @Test public void selectedIndexUsesStableIds() {
        assertEquals(1, MusicCategories.selectedIndex(new String[]{"all","dance"}, "dance"));
        assertEquals(0, MusicCategories.selectedIndex(new String[]{"all"}, "dance"));
    }
}
