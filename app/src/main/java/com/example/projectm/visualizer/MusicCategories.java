package com.example.projectm.visualizer;

import java.util.ArrayList;

final class MusicCategories {
    interface Counts { int count(String id); }
    private static final String[] IDS = {"all", "dance", "pop", "rock", "hip-hop", "rnb-soul", "jazz",
            "classical", "ambient", "folk-acoustic", "country", "reggae", "latin"};
    private static final String[] LABELS = {"All", "Dance", "Pop", "Rock", "Hip-Hop", "R&B / Soul", "Jazz",
            "Classical", "Ambient", "Folk / Acoustic", "Country", "Reggae", "Latin"};

    static String normalize(String id) {
        for (String candidate : IDS) if (candidate.equals(id)) return id;
        return "all";
    }
    static String label(String id) {
        return label(id,BuildConfig.AUDIENCE_REVIEW);
    }
    static String label(String id,boolean review) {
        if(review) {
            if("ambient".equals(id))return "Chill";
            if("pop".equals(id))return "Normal";
            if("dance".equals(id))return "Party";
            return "All";
        }
        for (int i = 0; i < IDS.length; i++) if (IDS[i].equals(id)) return LABELS[i];
        return LABELS[0];
    }
    static String[] available(Counts counts) {
        return available(counts,BuildConfig.AUDIENCE_REVIEW);
    }
    static String[] available(Counts counts,boolean review) {
        ArrayList<String> ids = new ArrayList<>();
        ids.add("all");
        String[] candidates=review?new String[]{"all","ambient","pop","dance"}:IDS;
        for (int i = 1; i < candidates.length; i++) if (counts.count(candidates[i]) > 0) ids.add(candidates[i]);
        return ids.toArray(new String[0]);
    }
    static int selectedIndex(String[] ids, String selected) {
        for (int i = 0; i < ids.length; i++) if (ids[i].equals(selected)) return i;
        return 0;
    }
    static String appliedSelection(String requested, String actual, boolean pending) {
        return normalize(pending ? requested : actual);
    }
    private MusicCategories() {}
}
