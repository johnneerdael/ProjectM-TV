package com.example.projectm.visualizer;

import android.Manifest;
import android.app.Activity;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.media.audiofx.Visualizer;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.RadioGroup;
import android.widget.RelativeLayout;
import android.widget.SeekBar;
import android.widget.Switch;
import android.widget.TextView;

import java.util.Locale;

public class MainActivity extends Activity {
    private static final String TAG = "ProjectMTV";
    private static final int AUDIO_PERMISSION_REQUEST = 1;
    private static final long MENU_AUTO_HIDE_MS = 8000;
    private static final long NOW_PLAYING_MS = 4000;
    private static final long UI_REFRESH_MS = 500;

    // Preference keys (kept compatible with earlier versions)
    private static final String PREFS = "projectm_settings";
    private static final String PREF_RESOLUTION = "selected_resolution";
    private static final String PREF_AUTO_CHANGE = "auto_change_enabled";
    private static final String PREF_PRESET_DURATION = "preset_duration";
    private static final String PREF_TRANSITION_DURATION = "transition_duration";

    // Stored resolution values; RES_NATIVE replaces the former fixed "4K" option.
    private static final int RES_480P = 0;
    private static final int RES_720P = 1;
    private static final int RES_1080P = 2;
    private static final int RES_NATIVE = 3;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private SharedPreferences prefs;
    private DeviceProfile profile;

    private VisualizerView visualizerView;
    private VisualizerRenderer renderer;
    private Visualizer audioVisualizer;

    private View overlayMenu;
    private TextView presetNameText;
    private TextView fpsDisplay;
    private TextView skippedInfo;
    private TextView nowPlaying;
    private int lastPresetChange = -1;

    private final Runnable hideMenu = () -> setMenuVisible(false);
    private final Runnable hideNowPlaying = () -> nowPlaying.setVisibility(View.GONE);
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

        initMenu();

        if (hasAudioPermission()) {
            startAudio();
        } else if (Build.VERSION.SDK_INT >= 23) {
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, AUDIO_PERMISSION_REQUEST);
        }
    }

    // ---------------------------------------------------------------------------------------
    // Menu
    // ---------------------------------------------------------------------------------------

    private void initMenu() {
        overlayMenu = findViewById(R.id.overlay_menu);
        presetNameText = findViewById(R.id.preset_name);
        fpsDisplay = findViewById(R.id.fps_display);
        skippedInfo = findViewById(R.id.skipped_info);
        nowPlaying = findViewById(R.id.now_playing);

        TextView versionInfo = findViewById(R.id.version_info);
        versionInfo.setText("App v" + appVersion() + " | projectM " + ProjectMJNI.getVersion()
                + " | " + profile.tier + " tier");

        Switch autoChange = findViewById(R.id.auto_change_switch);
        autoChange.setChecked(prefs.getBoolean(PREF_AUTO_CHANGE, true));
        autoChange.setOnCheckedChangeListener((button, checked) -> {
            ProjectMJNI.setAutoChange(checked);
            prefs.edit().putBoolean(PREF_AUTO_CHANGE, checked).apply();
        });

        bindSeekBar(R.id.preset_duration_seekbar, R.id.preset_duration_text, PREF_PRESET_DURATION, 30,
                ProjectMJNI::setPresetDuration);
        bindSeekBar(R.id.transition_duration_seekbar, R.id.transition_duration_text,
                PREF_TRANSITION_DURATION, 7, ProjectMJNI::setSoftCutDuration);

        findViewById(R.id.prev_preset_button).setOnClickListener(v -> ProjectMJNI.previousPreset(true));
        findViewById(R.id.random_preset_button).setOnClickListener(v -> ProjectMJNI.randomPreset(true));
        findViewById(R.id.next_preset_button).setOnClickListener(v -> ProjectMJNI.nextPreset(true));

        Button resetSkipped = findViewById(R.id.reset_skipped_button);
        resetSkipped.setOnClickListener(v -> {
            ProjectMJNI.resetSkippedPresets();
            refreshStatus();
        });

        RadioGroup resolutionGroup = findViewById(R.id.resolution_group);
        resolutionGroup.check(radioIdFor(savedResolution()));
        resolutionGroup.setOnCheckedChangeListener((group, checkedId) -> {
            int resolution = resolutionFor(checkedId);
            prefs.edit().putInt(PREF_RESOLUTION, resolution).apply();
            visualizerView.setRenderHeight(renderHeightFor(resolution));
        });

        overlayMenu.setVisibility(View.GONE);
    }

    private interface IntSetting { void apply(int value); }

    private void bindSeekBar(int seekBarId, int labelId, String prefKey, int defaultValue, IntSetting setting) {
        SeekBar seekBar = findViewById(seekBarId);
        TextView label = findViewById(labelId);
        int value = prefs.getInt(prefKey, defaultValue);
        seekBar.setProgress(value);
        label.setText(value + "s");
        seekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar bar, int progress, boolean fromUser) {
                label.setText(progress + "s");
                // D-pad changes arrive as individual steps: apply them immediately.
                setting.apply(progress);
                prefs.edit().putInt(prefKey, progress).apply();
            }

            @Override public void onStartTrackingTouch(SeekBar bar) {}
            @Override public void onStopTrackingTouch(SeekBar bar) {}
        });
    }

    private void setMenuVisible(boolean visible) {
        handler.removeCallbacks(hideMenu);
        if (!visible) {
            overlayMenu.setVisibility(View.GONE);
            visualizerView.requestFocus();
            return;
        }
        RelativeLayout.LayoutParams params = (RelativeLayout.LayoutParams) overlayMenu.getLayoutParams();
        params.width = (int) (getResources().getDisplayMetrics().widthPixels * 0.4f);
        overlayMenu.setLayoutParams(params);
        overlayMenu.setVisibility(View.VISIBLE);
        findViewById(R.id.auto_change_switch).requestFocus();
        refreshStatus();
        handler.postDelayed(hideMenu, MENU_AUTO_HIDE_MS);
    }

    private boolean isMenuVisible() {
        return overlayMenu.getVisibility() == View.VISIBLE;
    }

    /** Updates FPS, preset name and skip counter; shows the name briefly when a preset starts. */
    private void refreshStatus() {
        String preset = displayName(ProjectMJNI.getCurrentPresetName());
        int change = ProjectMJNI.getPresetChangeCounter();
        if (change != lastPresetChange && !preset.isEmpty()) {
            lastPresetChange = change;
            nowPlaying.setText(preset);
            nowPlaying.setVisibility(View.VISIBLE);
            handler.removeCallbacks(hideNowPlaying);
            handler.postDelayed(hideNowPlaying, NOW_PLAYING_MS);
        }
        if (!isMenuVisible()) return;

        float fps = renderer.getCurrentFps();
        fpsDisplay.setText(String.format(Locale.US, "FPS: %.1f", fps));
        fpsDisplay.setTextColor(fps < 20 ? 0xFFFF5050 : fps < 28 ? 0xFFFFAA00 : 0xFF00FF00);
        presetNameText.setText(String.format(Locale.US, "Current: %s (%d presets)",
                preset.isEmpty() ? "loading..." : preset, ProjectMJNI.getPresetCount()));
        presetNameText.setSelected(true);
        skippedInfo.setText("Skipped presets: " + ProjectMJNI.getSkippedCount());
    }

    private static String displayName(String preset) {
        if (preset == null) return "";
        int slash = preset.lastIndexOf('/');
        String name = slash >= 0 ? preset.substring(slash + 1) : preset;
        return name.endsWith(".milk") ? name.substring(0, name.length() - 5) : name;
    }

    // ---------------------------------------------------------------------------------------
    // Resolution
    // ---------------------------------------------------------------------------------------

    private int savedResolution() {
        int fallback = profile.defaultRenderHeight() >= 1080 ? RES_1080P : RES_720P;
        return prefs.getInt(PREF_RESOLUTION, fallback);
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

    private static int radioIdFor(int resolution) {
        switch (resolution) {
            case RES_480P: return R.id.resolution_480p;
            case RES_1080P: return R.id.resolution_1080p;
            case RES_NATIVE: return R.id.resolution_native;
            case RES_720P:
            default: return R.id.resolution_720p;
        }
    }

    private static int resolutionFor(int radioId) {
        if (radioId == R.id.resolution_480p) return RES_480P;
        if (radioId == R.id.resolution_1080p) return RES_1080P;
        if (radioId == R.id.resolution_native) return RES_NATIVE;
        return RES_720P;
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
    // Audio
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
            startAudio();
        } else {
            Log.w(TAG, "Audio permission denied - visuals will not react to music");
        }
    }

    private void startAudio() {
        if (audioVisualizer != null) return;
        try {
            // Session 0 = global output mix. The waveform is 8-bit unsigned mono PCM, which is
            // passed to projectM unchanged.
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

    // ---------------------------------------------------------------------------------------
    // Lifecycle
    // ---------------------------------------------------------------------------------------

    @Override
    protected void onResume() {
        super.onResume();
        visualizerView.onResume();
        if (audioVisualizer != null) audioVisualizer.setEnabled(true);
        handler.post(uiRefresh);
    }

    @Override
    protected void onPause() {
        handler.removeCallbacks(uiRefresh);
        if (audioVisualizer != null) audioVisualizer.setEnabled(false);
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
        if (audioVisualizer != null) {
            audioVisualizer.setEnabled(false);
            audioVisualizer.release();
            audioVisualizer = null;
        }
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
