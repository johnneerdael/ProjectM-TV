package com.example.projectm.visualizer;

import java.io.StringReader;
import org.junit.Test;
import static org.junit.Assert.*;

public class AudienceScoresTest {
    @Test public void preservesScoreAndRelativeRankAsDifferentValues() throws Exception {
        AudienceScores scores=AudienceScores.read(new StringReader("name.milk\t30.8\t12.5\n"));
        assertEquals("Score 30.8 / 100 · rank 12.5 / 100",scores.describe("name.milk"));
        assertEquals("Score unavailable",scores.describe("other.milk"));
    }
    @Test public void rejectsInvalidOrDuplicateRecords() throws Exception {
        for(String value:new String[]{"name.milk\tNaN\t50\n","name.milk\t101\t50\n","name.milk\t30\t0\n","name.milk\t30\t50\nname.milk\t40\t60\n"}) {
            try {AudienceScores.read(new StringReader(value));fail("Invalid score table accepted");}
            catch(IllegalArgumentException expected) {}
        }
    }
    @Test public void reviewGroupsUseExistingPublishedCoreIds() {
        assertEquals("Chill",MusicCategories.label("ambient",true));
        assertEquals("Normal",MusicCategories.label("pop",true));
        assertEquals("Party",MusicCategories.label("dance",true));
        assertArrayEquals(new String[]{"all","ambient","pop","dance"},MusicCategories.available(id->10,true));
        assertEquals("Dance",MusicCategories.label("dance",false));
    }
}
