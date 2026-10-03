package com.example.projectm.visualizer;

import android.content.ComponentName;
import android.content.Context;
import android.graphics.Bitmap;
import android.media.MediaMetadata;
import android.media.session.MediaController;
import android.media.session.MediaSessionManager;
import android.media.session.PlaybackState;
import android.os.Handler;
import android.provider.Settings;
import android.util.Log;

import java.util.ArrayList;
import java.util.List;

/**
 * Reports the track the music app is playing, from its media session: when one starts, plays again
 * after a pause, or its details are completed, and when nothing plays any more. Needs
 * notification-listener access for {@link TrackListenerService}; without it, nothing is reported.
 * Main thread only.
 */
final class TrackWatcher {
    interface Listener {
        /**
         * A track plays: a new one ({@code newTrack}), the same one again after a pause, or the same
         * one with more details (the artist after the title, or the cover after the text).
         */
        void onTrack(Track track, boolean newTrack);

        /** Nothing plays any more (paused, stopped, or the watch stopped). */
        void onStopped();
    }

    /** Title, artist and cover art of one track; title or artist may be empty, the cover null. */
    static final class Track {
        final String title;
        final String artist;
        final Bitmap cover;

        Track(String title, String artist, Bitmap cover) {
            this.title = title == null ? "" : title.trim();
            this.artist = artist == null ? "" : artist.trim();
            this.cover = cover;
        }

        /** "Title — Artist", or whichever of the two is known. */
        String label() {
            return TrackWatcher.label(title, artist);
        }

        /** Same title and artist; the cover may differ. */
        boolean sameAs(Track other) {
            return other != null && title.equals(other.title) && artist.equals(other.artist);
        }
    }

    // Where sessions keep the cover, best first: apps fill in one or more of these.
    private static final String[] COVER_KEYS = {MediaMetadata.METADATA_KEY_ALBUM_ART,
            MediaMetadata.METADATA_KEY_ART, MediaMetadata.METADATA_KEY_DISPLAY_ICON};

    private static final String TAG = "ProjectMTV";

    private final Context context;
    private final Handler handler;
    private final Listener listener;
    private final ComponentName component;
    private final List<MediaController> controllers = new ArrayList<>();
    private MediaSessionManager sessions;
    private String lastTitle = "";
    private String lastLabel = "";
    private Bitmap lastCover;
    private boolean playing;

    private final MediaSessionManager.OnActiveSessionsChangedListener sessionsChanged = this::watch;
    private final MediaController.Callback controllerCallback = new MediaController.Callback() {
        @Override
        public void onMetadataChanged(MediaMetadata metadata) {
            report();
        }

        @Override
        public void onPlaybackStateChanged(PlaybackState state) {
            report();
        }
    };

    TrackWatcher(Context context, Handler handler, Listener listener) {
        this.context = context;
        this.handler = handler;
        this.listener = listener;
        this.component = new ComponentName(context, TrackListenerService.class);
    }

    /** Whether the user granted notification-listener access (Settings › Apps › Special app access). */
    boolean hasAccess() {
        String enabled = Settings.Secure.getString(context.getContentResolver(), "enabled_notification_listeners");
        return enabled != null && (enabled.contains(component.flattenToString())
                || enabled.contains(component.flattenToShortString()));
    }

    /** Starts watching if access was granted; returns whether it did. */
    boolean start() {
        if (sessions != null) return true;
        if (!hasAccess()) return false;
        try {
            MediaSessionManager manager = (MediaSessionManager) context.getSystemService(Context.MEDIA_SESSION_SERVICE);
            manager.addOnActiveSessionsChangedListener(sessionsChanged, component, handler);
            sessions = manager;
            watch(manager.getActiveSessions(component));
            return true;
        } catch (SecurityException e) {  // access revoked in the meantime
            Log.w(TAG, "Track watch unavailable: " + e.getMessage());
            stop();
            return false;
        }
    }

    void stop() {
        if (sessions != null) sessions.removeOnActiveSessionsChangedListener(sessionsChanged);
        sessions = null;
        watch(null);
    }

    private void watch(List<MediaController> active) {
        for (MediaController controller : controllers) controller.unregisterCallback(controllerCallback);
        controllers.clear();
        if (active != null) {
            for (MediaController controller : active) {
                controller.registerCallback(controllerCallback, handler);
                controllers.add(controller);
            }
        }
        report();
    }

    /**
     * Reports the first playing session with track text if its track differs from the last one
     * reported (another cover counts: one that arrives, replaces a fallback or goes), or if it
     * plays again after a pause; reports a stop when no session plays a track.
     */
    private void report() {
        for (MediaController controller : controllers) {
            PlaybackState state = controller.getPlaybackState();
            MediaMetadata metadata = controller.getMetadata();
            if (state == null || state.getState() != PlaybackState.STATE_PLAYING || metadata == null) continue;
            String title = first(metadata, MediaMetadata.METADATA_KEY_TITLE, MediaMetadata.METADATA_KEY_DISPLAY_TITLE);
            String artist = first(metadata, MediaMetadata.METADATA_KEY_ARTIST,
                    MediaMetadata.METADATA_KEY_ALBUM_ARTIST, MediaMetadata.METADATA_KEY_DISPLAY_SUBTITLE);
            Track track = new Track(title, artist, cover(metadata));
            String label = track.label();
            if (label.isEmpty()) continue;  // nothing to show here; another session may play a track
            if (!reportable(playing, lastLabel, label, !sameCover(track.cover, lastCover))) return;
            boolean newTrack = !title.equals(lastTitle) || (title.isEmpty() && !label.equals(lastLabel));
            if (!label.equals(lastLabel)) {
                Log.i(TAG, "Track: " + label + " (" + controller.getPackageName() + ")");
            }
            lastTitle = title;
            lastLabel = label;
            lastCover = track.cover;
            playing = true;
            listener.onTrack(track, newTrack);
            return;
        }
        if (playing) {
            playing = false;
            listener.onStopped();
        }
    }

    /** Whether a playing track is reported: playback (re)started, other text, or another cover. */
    static boolean reportable(boolean wasPlaying, String lastLabel, String label, boolean coverChanged) {
        return !wasPlaying || !label.equals(lastLabel) || coverChanged;
    }

    /** Each read of the metadata is a new bitmap, so covers are compared by their pixels. */
    private static boolean sameCover(Bitmap a, Bitmap b) {
        return a == b || (a != null && b != null && a.sameAs(b));
    }

    private static Bitmap cover(MediaMetadata metadata) {
        for (String key : COVER_KEYS) {
            Bitmap cover = metadata.getBitmap(key);
            if (cover != null) return cover;
        }
        return null;
    }

    private static String first(MediaMetadata metadata, String... keys) {
        for (String key : keys) {
            CharSequence value = metadata.getText(key);
            if (value != null && value.toString().trim().length() > 0) return value.toString().trim();
        }
        return "";
    }

    /** "Title — Artist", or whichever of the two is known. */
    static String label(String title, String artist) {
        title = title == null ? "" : title.trim();
        artist = artist == null ? "" : artist.trim();
        if (title.isEmpty()) return artist;
        if (artist.isEmpty()) return title;
        return title + " — " + artist;
    }
}
