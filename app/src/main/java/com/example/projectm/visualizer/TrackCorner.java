package com.example.projectm.visualizer;

import android.animation.LayoutTransition;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

/**
 * The playing track in the upper left, as Milkbeat shows it: cover art, then the artist and, below
 * it, the title, straight over the visual. Without a cover the text starts where the cover would,
 * and a cover that arrives later pushes it aside. Another track crossfades in. It stays left of the
 * settings panel, so it can remain on screen while the panel is open; a line that does not fit
 * scrolls continuously. Main thread only.
 */
final class TrackCorner {
    private static final long FADE_MS = 180;
    private static final float MAX_WIDTH_FRACTION = 0.6f;  // of the screen, as in Milkbeat

    private final ViewGroup root;
    private final ImageView cover;
    private final TextView primary;
    private final TextView secondary;
    private final LayoutTransition coverTransition;
    private final int maxWidth;
    private final int coverSpace;
    private TrackWatcher.Track shown;
    private boolean visible;

    TrackCorner(ViewGroup root) {
        this.root = root;
        cover = root.findViewById(R.id.track_cover);
        primary = root.findViewById(R.id.track_primary);
        secondary = root.findViewById(R.id.track_secondary);
        cover.setClipToOutline(true);  // the rounded background shape clips the artwork
        coverTransition = root.getLayoutTransition();
        android.content.res.Resources res = root.getResources();
        maxWidth = maxWidth(res.getDisplayMetrics().widthPixels,
                res.getDimensionPixelSize(R.dimen.safe_horizontal),
                res.getDimensionPixelSize(R.dimen.panel_width),
                res.getDimensionPixelSize(R.dimen.track_panel_gap));
        ViewGroup.MarginLayoutParams params = (ViewGroup.MarginLayoutParams) cover.getLayoutParams();
        coverSpace = params.width + params.getMarginEnd();
    }

    boolean isVisible() {
        return visible;
    }

    /** Shows {@code track}: fades in, crossfades from another track, or updates the one shown. */
    void show(TrackWatcher.Track track) {
        root.animate().cancel();  // a cancelled animation does not run its end action
        if (visible && shown != null && !shown.sameAs(track)) {
            shown = track;
            root.animate().alpha(0f).setDuration(FADE_MS).withLayer().withEndAction(() -> {
                bind(track, false);
                root.animate().alpha(1f).setDuration(FADE_MS).withLayer().start();
            }).start();
            return;
        }
        bind(track, visible && root.getAlpha() == 1f);  // a late cover slides in only while settled
        shown = track;
        visible = true;
        root.setVisibility(View.VISIBLE);
        root.animate().alpha(1f).setDuration(FADE_MS).withLayer().start();
    }

    void hide() {
        if (!visible) return;
        visible = false;
        root.animate().cancel();
        root.animate().alpha(0f).setDuration(FADE_MS).withLayer()
                .withEndAction(() -> root.setVisibility(View.GONE)).start();
    }

    private void bind(TrackWatcher.Track track, boolean animateCover) {
        root.setLayoutTransition(animateCover ? coverTransition : null);
        boolean hasCover = track.cover != null;
        cover.setImageBitmap(track.cover);
        cover.setVisibility(hasCover ? View.VISIBLE : View.GONE);
        int textWidth = maxWidth - (hasCover ? coverSpace : 0);
        String[] lines = lines(track.title, track.artist);
        setLine(primary, lines[0], textWidth);
        setLine(secondary, lines[1], textWidth);
    }

    private static void setLine(TextView view, String text, int maxWidth) {
        view.setMaxWidth(maxWidth);
        view.setVisibility(text.isEmpty() ? View.GONE : View.VISIBLE);
        if (!text.contentEquals(view.getText())) view.setText(text);
        // The marquee only starts on a laid-out line: (re)select it once the layout pass is done,
        // also when the corner was hidden or the cover changed the width.
        view.setSelected(false);
        view.post(() -> view.setSelected(true));
    }

    /**
     * Widest the corner may be: Milkbeat's 60% of the screen, but never into the settings panel
     * on the right (its width plus {@code gap}), so the two can be on screen together.
     */
    static int maxWidth(int screenWidth, int safeHorizontal, int panelWidth, int gap) {
        return Math.min(Math.round(screenWidth * MAX_WIDTH_FRACTION),
                screenWidth - 2 * safeHorizontal - panelWidth - gap);
    }

    /** Artist on top and the title below it; a lone title or artist takes the top line. */
    static String[] lines(String title, String artist) {
        if (artist.isEmpty()) return new String[]{title, ""};
        if (title.isEmpty()) return new String[]{artist, ""};
        return new String[]{artist, title};
    }
}
