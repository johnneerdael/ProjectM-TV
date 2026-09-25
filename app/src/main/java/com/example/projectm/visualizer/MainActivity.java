package com.example.projectm.visualizer;

import android.Manifest;
import android.app.Activity;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.media.audiofx.Visualizer;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.Looper;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.TextView;

import java.text.NumberFormat;
import java.util.Locale;

public class MainActivity extends Activity {
    private static final String TAG = "ProjectMTV";
    private static final int AUDIO_PERMISSION_REQUEST = 1;
    private static final long MENU_AUTO_HIDE_MS = 10000;
    private static final long NOW_PLAYING_MS = 6000;
    private static final long UI_REFRESH_MS = 500;
    private static final long FADE_MS = 180;

    // Preference keys (kept compatible with earlier versions)
    private static final String PREFS = "projectm_settings";
    private static final String PREF_RESOLUTION = "selected_resolution";
    private static final String PREF_AUTO_CHANGE = "auto_change_enabled";
    private static final String PREF_PRESET_DURATION = "preset_duration";
    private static final String PREF_TRANSITION_DURATION = "transition_duration";
    private static final String PREF_HALF_FRAME_RATE = "half_frame_rate";

    // Stored resolution values; RES_NATIVE replaces the former fixed "4K" option.
    private static final int RES_480P = 0;
    private static final int RES_720P = 1;
    private static final int RES_1080P = 2;
    private static final int RES_NATIVE = 3;
    private static final String[] RESOLUTION_LABELS = {"480p", "720p", "1080p", "Native"};

    private static final int[] PRESET_DURATIONS = {10, 15, 20, 30, 45, 60, 90};
    private static final int MAX_TRANSITION = 10;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private SharedPreferences prefs;
    private DeviceProfile profile;
    private final NumberFormat numberFormat = NumberFormat.getIntegerInstance(Locale.getDefault());

    private VisualizerView visualizerView;
    private VisualizerRenderer renderer;

    // Audio capture runs on its own looper so UI work (menu animations) never delays it.
    private HandlerThread audioThread;
    private Handler audioHandler;
    private Visualizer audioVisualizer;

    private View overlayMenu;
    private TextView presetName;
    private TextView presetMeta;
    private TextView statusLine;
    private OptionRow skippedRow;
    private View nowPlaying;
    private TextView nowPlayingText;
    private boolean menuVisible;
    private int lastPresetChange = -1;
    private String currentPreset = "";

    private final Runnable hideMenu = () -> setMenuVisible(false);
    private final Runnable hideNowPlaying = () -> fade(nowPlaying, false);
    private final Runnable uiRefresh = new Runnable() {
        @Override
        public void run() {
            refreshStatus();
            handler.postDelayed(this, UI_REFRESH_MS);
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON
                | WindowManager.LayoutParams.FLAG_FULLSCREEN);
        setContentView(R.layout.activity_main);

        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        profile = DeviceProfile.detect(this);

        // Settings go to the native engine before the surface exists; they are applied on the
        // GL thread as soon as projectM is created.
        ProjectMJNI.setMeshSize(profile.meshWidth(), profile.meshHeight());
        ProjectMJNI.setAutoChange(prefs.getBoolean(PREF_AUTO_CHANGE, true));
        ProjectMJNI.setPresetDuration(prefs.getInt(PREF_PRESET_DURATION, 30));
        ProjectMJNI.setSoftCutDuration(prefs.getInt(PREF_TRANSITION_DURATION, 7));

        visualizerView = findViewById(R.id.visualizer_view);
        visualizerView.setRenderHeight(renderHeightFor(savedResolution()));
        renderer = new VisualizerRenderer();
        visualizerView.start(renderer);
        visualizerView.setHalfFrameRate(prefs.getBoolean(PREF_HALF_FRAME_RATE, profile.defaultHalfFrameRate()));

        initMenu();

        audioThread = new HandlerThread("AudioCapture", android.os.Process.THREAD_PRIORITY_AUDIO);
        audioThread.start();
        audioHandler = new Handler(audioThread.getLooper());
        if (hasAudioPermission()) {
            audioHandler.post(this::startAudio);
        } else if (Build.VERSION.SDK_INT >= 23) {
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, AUDIO_PERMISSION_REQUEST);
        }
    }

    // ---------------------------------------------------------------------------------------
    // Menu
    // ---------------------------------------------------------------------------------------

    private void initMenu() {
        overlayMenu = findViewById(R.id.overlay_menu);
        presetName = findViewById(R.id.preset_name);
        presetMeta = findViewById(R.id.preset_meta);
        statusLine = findViewById(R.id.status_line);
        nowPlaying = findViewById(R.id.now_playing);
        nowPlayingText = findViewById(R.id.now_playing_text);

        TextView versionInfo = findViewById(R.id.version_info);
        versionInfo.setText("v" + appVersion() + "  ·  projectM " + ProjectMJNI.getVersion()
                + "  ·  " + profile.tier.name().toLowerCase(Locale.US) + " device");

        findViewById(R.id.prev_preset_button).setOnClickListener(v -> ProjectMJNI.previousPreset(true));
        findViewById(R.id.random_preset_button).setOnClickListener(v -> ProjectMJNI.randomPreset(true));
        findViewById(R.id.next_preset_button).setOnClickListener(v -> ProjectMJNI.nextPreset(true));

        OptionRow autoChange = findViewById(R.id.row_auto_change);
        autoChange.setup("Auto change", new String[]{"Off", "On"},
                prefs.getBoolean(PREF_AUTO_CHANGE, true) ? 1 : 0, true, index -> {
                    ProjectMJNI.setAutoChange(index == 1);
                    prefs.edit().putBoolean(PREF_AUTO_CHANGE, index == 1).apply();
                });

        String[] durations = new String[PRESET_DURATIONS.length];
        for (int i = 0; i < durations.length; i++) durations[i] = PRESET_DURATIONS[i] + " s";
        OptionRow presetDuration = findViewById(R.id.row_preset_duration);
        presetDuration.setup("Preset duration", durations,
                nearestIndex(PRESET_DURATIONS, prefs.getInt(PREF_PRESET_DURATION, 30)), false, index -> {
                    ProjectMJNI.setPresetDuration(PRESET_DURATIONS[index]);
                    prefs.edit().putInt(PREF_PRESET_DURATION, PRESET_DURATIONS[index]).apply();
                });

        String[] transitions = new String[MAX_TRANSITION + 1];
        transitions[0] = "Instant";
        for (int i = 1; i <= MAX_TRANSITION; i++) transitions[i] = i + " s";
        OptionRow transition = findViewById(R.id.row_transition);
        transition.setup("Transition", transitions,
                Math.min(MAX_TRANSITION, prefs.getInt(PREF_TRANSITION_DURATION, 7)), false, index -> {
                    ProjectMJNI.setSoftCutDuration(index);
                    prefs.edit().putInt(PREF_TRANSITION_DURATION, index).apply();
                });

        OptionRow resolution = findViewById(R.id.row_resolution);
        resolution.setup("Resolution", RESOLUTION_LABELS, savedResolution(), false, index -> {
            prefs.edit().putInt(PREF_RESOLUTION, index).apply();
            visualizerView.setRenderHeight(renderHeightFor(index));
        });

        int refresh = Math.round(visualizerView.displayRefreshRate());
        OptionRow frameRate = findViewById(R.id.row_frame_rate);
        frameRate.setup("Frame rate",
                new String[]{Math.round(refresh / 2f) + " fps  (smooth)", refresh + " fps  (max)"},
                prefs.getBoolean(PREF_HALF_FRAME_RATE, profile.defaultHalfFrameRate()) ? 0 : 1, true,
                index -> {
                    boolean half = index == 0;
                    visualizerView.setHalfFrameRate(half);
                    prefs.edit().putBoolean(PREF_HALF_FRAME_RATE, half).apply();
                });

        skippedRow = findViewById(R.id.row_skipped);
        skippedRow.setupAction("Skipped presets", "0", () -> {
            ProjectMJNI.resetSkippedPresets();
            refreshStatus();
        });

        overlayMenu.setVisibility(View.GONE);
    }

    private static int nearestIndex(int[] values, int target) {
        int best = 0;
        for (int i = 1; i < values.length; i++) {
            if (Math.abs(values[i] - target) < Math.abs(values[best] - target)) best = i;
        }
        return best;
    }

    private void setMenuVisible(boolean visible) {
        handler.removeCallbacks(hideMenu);
        if (visible == menuVisible) return;
        menuVisible = visible;
        if (visible) {
            fade(nowPlaying, false);
            refreshStatus();
            overlayMenu.setTranslationX(dp(24));
            overlayMenu.animate().translationX(0).setDuration(FADE_MS).start();
            fade(overlayMenu, true);
            findViewById(R.id.random_preset_button).requestFocus();
            handler.postDelayed(hideMenu, MENU_AUTO_HIDE_MS);
        } else {
            overlayMenu.animate().translationX(dp(24)).setDuration(FADE_MS).start();
            fade(overlayMenu, false);
        }
    }

    private boolean isMenuVisible() {
        return menuVisible;
    }

    /** Alpha fade that ends with GONE, so hidden views cost nothing to compose. */
    private static void fade(View view, boolean in) {
        view.animate().cancel();
        if (in) {
            view.setVisibility(View.VISIBLE);
            view.animate().alpha(1f).setDuration(FADE_MS).withLayer().start();
        } else if (view.getVisibility() == View.VISIBLE) {
            view.animate().alpha(0f).setDuration(FADE_MS).withLayer()
                    .withEndAction(() -> view.setVisibility(View.GONE)).start();
        }
    }

    /** Updates text only when it changed: a changed text restarts the marquee and costs a layout. */
    private static void setText(TextView view, CharSequence text) {
        if (!text.toString().contentEquals(view.getText())) view.setText(text);
    }

    private void refreshStatus() {
        int change = ProjectMJNI.getPresetChangeCounter();
        if (change != lastPresetChange) {
            lastPresetChange = change;
            currentPreset = displayName(ProjectMJNI.getCurrentPresetName());
            if (!currentPreset.isEmpty()) {
                setText(presetName, currentPreset);
                presetName.setSelected(true);  // start marquee for long names
                if (!isMenuVisible()) showNowPlaying(currentPreset);
            }
        }
        if (!isMenuVisible()) return;

        int skipped = ProjectMJNI.getSkippedCount();
        setText(presetMeta, numberFormat.format(ProjectMJNI.getPresetCount()) + " presets in rotation"
                + (skipped > 0 ? "  ·  " + numberFormat.format(skipped) + " skipped" : ""));
        skippedRow.setActionValue(skipped > 0 ? numberFormat.format(skipped) + "  ·  Reset" : "None");
        setText(statusLine, String.format(Locale.US, "%5.1f fps  ·  %dx%d",
                renderer.getCurrentFps(), renderer.getSurfaceWidth(), renderer.getSurfaceHeight()));
    }

    private void showNowPlaying(String name) {
        if (name.isEmpty()) return;
        setText(nowPlayingText, name);
        nowPlayingText.setSelected(true);
        fade(nowPlaying, true);
        handler.removeCallbacks(hideNowPlaying);
        handler.postDelayed(hideNowPlaying, NOW_PLAYING_MS);
    }

    private static String displayName(String preset) {
        if (preset == null) return "";
        int slash = preset.lastIndexOf('/');
        String name = slash >= 0 ? preset.substring(slash + 1) : preset;
        return name.regionMatches(true, Math.max(0, name.length() - 5), ".milk", 0, 5)
                ? name.substring(0, name.length() - 5) : name;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    // ---------------------------------------------------------------------------------------
    // Resolution
    // ---------------------------------------------------------------------------------------

    private int savedResolution() {
        int fallback = profile.defaultRenderHeight() >= 1080 ? RES_1080P : RES_720P;
        int saved = prefs.getInt(PREF_RESOLUTION, fallback);
        return saved >= RES_480P && saved <= RES_NATIVE ? saved : fallback;
    }

    private static int renderHeightFor(int resolution) {
        switch (resolution) {
            case RES_480P: return 480;
            case RES_1080P: return 1080;
            case RES_NATIVE: return 0;
            case RES_720P:
            default: return 720;
        }
    }

    // ---------------------------------------------------------------------------------------
    // Remote control
    // ---------------------------------------------------------------------------------------

    @Override
    public boolean dispatchKeyEvent(KeyEvent event) {
        if (isMenuVisible()) {  // any interaction keeps the menu open
            handler.removeCallbacks(hideMenu);
            handler.postDelayed(hideMenu, MENU_AUTO_HIDE_MS);
        }
        return super.dispatchKeyEvent(event);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (isMenuVisible()) {
            if (keyCode == KeyEvent.KEYCODE_BACK || keyCode == KeyEvent.KEYCODE_MENU) {
                setMenuVisible(false);
                return true;
            }
            return super.onKeyDown(keyCode, event);  // focus navigation inside the menu
        }
        switch (keyCode) {
            case KeyEvent.KEYCODE_DPAD_RIGHT:
            case KeyEvent.KEYCODE_MEDIA_NEXT:
            case KeyEvent.KEYCODE_MEDIA_FAST_FORWARD:
                ProjectMJNI.randomPreset(true);
                return true;
            case KeyEvent.KEYCODE_DPAD_LEFT:
            case KeyEvent.KEYCODE_MEDIA_PREVIOUS:
            case KeyEvent.KEYCODE_MEDIA_REWIND:
                ProjectMJNI.previousPreset(true);
                return true;
            case KeyEvent.KEYCODE_DPAD_UP:
            case KeyEvent.KEYCODE_DPAD_DOWN:
            case KeyEvent.KEYCODE_INFO:
                showNowPlaying(currentPreset);
                return true;
            case KeyEvent.KEYCODE_DPAD_CENTER:
            case KeyEvent.KEYCODE_ENTER:
            case KeyEvent.KEYCODE_MENU:
                setMenuVisible(true);
                return true;
            default:
                return super.onKeyDown(keyCode, event);
        }
    }

    // ---------------------------------------------------------------------------------------
    // Audio (all Visualizer calls run on audioThread)
    // ---------------------------------------------------------------------------------------

    private boolean hasAudioPermission() {
        return Build.VERSION.SDK_INT < 23
                || checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED;
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == AUDIO_PERMISSION_REQUEST && grantResults.length > 0
                && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            audioHandler.post(this::startAudio);
        } else {
            Log.w(TAG, "Audio permission denied - visuals will not react to music");
        }
    }

    private void startAudio() {
        if (audioVisualizer != null) return;
        try {
            // Session 0 = global output mix. The waveform is 8-bit unsigned mono PCM, passed to
            // projectM unchanged. Callbacks arrive on the looper of the thread that registers the
            // listener, i.e. audioThread.
            audioVisualizer = new Visualizer(0);
            audioVisualizer.setEnabled(false);
            audioVisualizer.setCaptureSize(Visualizer.getCaptureSizeRange()[1]);
            audioVisualizer.setDataCaptureListener(new Visualizer.OnDataCaptureListener() {
                @Override
                public void onWaveFormDataCapture(Visualizer v, byte[] waveform, int samplingRate) {
                    if (waveform != null) ProjectMJNI.addWaveform(waveform, waveform.length);
                }

                @Override
                public void onFftDataCapture(Visualizer v, byte[] fft, int samplingRate) {}
            }, Visualizer.getMaxCaptureRate(), true, false);
            int status = audioVisualizer.setEnabled(true);
            Log.i(TAG, "Audio capture enabled (status " + status + ")");
        } catch (RuntimeException e) {
            Log.e(TAG, "Audio capture unavailable", e);
            audioVisualizer = null;
        }
    }

    private void setAudioEnabled(boolean enabled) {
        audioHandler.post(() -> {
            if (audioVisualizer != null) audioVisualizer.setEnabled(enabled);
        });
    }

    // ---------------------------------------------------------------------------------------
    // Lifecycle
    // ---------------------------------------------------------------------------------------

    @Override
    protected void onResume() {
        super.onResume();
        visualizerView.onResume();
        setAudioEnabled(true);
        handler.post(uiRefresh);
    }

    @Override
    protected void onPause() {
        handler.removeCallbacks(uiRefresh);
        setAudioEnabled(false);
        visualizerView.onPause();
        super.onPause();
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                    | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                    | View.SYSTEM_UI_FLAG_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        }
    }

    @Override
    protected void onDestroy() {
        handler.removeCallbacksAndMessages(null);
        audioHandler.post(() -> {
            if (audioVisualizer != null) {
                audioVisualizer.setEnabled(false);
                audioVisualizer.release();
                audioVisualizer = null;
            }
        });
        audioThread.quitSafely();
        // projectM owns GL objects, so it is destroyed on the GL thread. If the thread is already
        // gone, the next onSurfaceCreated() cleans up instead.
        visualizerView.queueEvent(renderer::release);
        super.onDestroy();
    }

    private String appVersion() {
        try {
            return getPackageManager().getPackageInfo(getPackageName(), 0).versionName;
        } catch (PackageManager.NameNotFoundException e) {
            return "?";
        }
    }
}
