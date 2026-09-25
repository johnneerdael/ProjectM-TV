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
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class MainActivity extends Activity {
    private static final String TAG = "ProjectMTV";
    private static final int AUDIO_PERMISSION_REQUEST = 1;
    private static final long MENU_AUTO_HIDE_MS = 10000;
    private static final long NOW_PLAYING_MS = 6000;
    private static final long UI_REFRESH_MS = 500;
    private static final long FADE_MS = 180;

    private static final String PREFS = "projectm_settings";
    private static final String PREF_AUTO_CHANGE = "auto_change_enabled";
    private static final String PREF_PRESET_DURATION = "preset_duration";
    private static final String PREF_TRANSITION_DURATION = "transition_duration";
    private static final String PREF_RENDER_HEIGHT = "render_height";      // 0 = automatic
    private static final String PREF_AUTO_HEIGHT = "auto_render_height";  // last automatic level
    private static final String PREF_FRAME_RATE_CAP = "frame_rate_cap";
    private static final String PREF_MESH_LEVEL = "mesh_level";
    private static final String PREF_SKIP_SLOW = "skip_slow_presets";
    private static final String PREF_BLANK_DETECTION = "blank_detection";

    private static final int[] PRESET_DURATIONS = {10, 15, 20, 30, 45, 60, 90};
    private static final int MAX_TRANSITION = 10;

    private enum Menu { NONE, MAIN, ADVANCED }

    private final Handler handler = new Handler(Looper.getMainLooper());
    private final NumberFormat numberFormat = NumberFormat.getIntegerInstance(Locale.getDefault());
    private SharedPreferences prefs;
    private DeviceProfile profile;
    private DisplayInfo display;
    private QualityController quality;
    private int frameRateTarget;

    private VisualizerView visualizerView;
    private VisualizerRenderer renderer;

    // Audio capture runs on its own looper so UI work (menu animations) never delays it.
    private HandlerThread audioThread;
    private Handler audioHandler;
    private Visualizer audioVisualizer;

    private View mainMenu;
    private View advancedMenu;
    private TextView presetName;
    private TextView presetMeta;
    private TextView statusLine;
    private TextView diagnostics;
    private OptionRow skippedRow;
    private View nowPlaying;
    private TextView nowPlayingText;
    private Menu menu = Menu.NONE;
    private int lastPresetChange = -1;
    private String currentPreset = "";

    private final Runnable hideMenu = () -> showMenu(Menu.NONE);
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
        getWindow().setBackgroundDrawable(null);  // the GL surface covers the screen

        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        profile = DeviceProfile.detect(this);
        display = DisplayInfo.detect(this);

        // Settings go to the native engine before the surface exists; they are applied on the
        // GL thread as soon as projectM is created.
        int[] mesh = DeviceProfile.MESH_SIZES[meshLevel()];
        ProjectMJNI.setMeshSize(mesh[0], mesh[1]);
        ProjectMJNI.setAutoChange(prefs.getBoolean(PREF_AUTO_CHANGE, true));
        ProjectMJNI.setPresetDuration(prefs.getInt(PREF_PRESET_DURATION, 30));
        ProjectMJNI.setSoftCutDuration(transitionSeconds());
        ProjectMJNI.setBlankDetection(prefs.getBoolean(PREF_BLANK_DETECTION, true));

        visualizerView = findViewById(R.id.visualizer_view);
        renderer = new VisualizerRenderer(new VisualizerRenderer.StatsListener() {
            @Override
            public void onFpsSample(float fps) {
                handler.post(() -> onFrameRate(fps));
            }

            @Override
            public void onPresetChanged() {
                handler.post(() -> quality.onPresetChanged());
            }
        });
        quality = new QualityController(display, profile, this::applyRenderHeight);
        quality.setTransitionSeconds(transitionSeconds());
        quality.setSkipSlowPresets(prefs.getBoolean(PREF_SKIP_SLOW, profile.defaultSkipSlowPresets()));
        quality.setMode(savedRenderHeight(), prefs.getInt(PREF_AUTO_HEIGHT, 0));
        visualizerView.start(renderer);
        applyFrameRateCap(prefs.getInt(PREF_FRAME_RATE_CAP, profile.defaultFrameRateCap()));

        initMenus();

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
    // Quality: resolution and frame rate
    // ---------------------------------------------------------------------------------------

    private void applyRenderHeight(int height) {
        visualizerView.setRenderSize(display.widthForHeight(height), height);
        ProjectMJNI.setForceHardCut(false);
        if (quality != null && quality.isAuto()) prefs.edit().putInt(PREF_AUTO_HEIGHT, height).apply();
    }

    private void onFrameRate(float fps) {
        int action = quality.onFpsSample(fps);
        if (action == QualityController.ACTION_SKIP) {
            ProjectMJNI.skipCurrentPreset();
        } else if (action == QualityController.ACTION_SWITCH) {
            ProjectMJNI.nextPreset(true);
        } else if (quality.hasPendingChange()) {
            // The resolution changes at the next preset switch; make that switch a hard cut.
            ProjectMJNI.setForceHardCut(true);
        }
    }

    /** Frame-rate options: the refresh rate divided by 4, 2 or 1 (at least 24 fps), ascending. */
    private int[] frameRateOptions() {
        List<Integer> rates = new ArrayList<>();
        for (int divisor : new int[]{4, 2, 1}) {
            int rate = Math.round(display.refreshRate / divisor);
            if (rate >= 24 && !rates.contains(rate)) rates.add(rate);
        }
        int[] result = new int[rates.size()];
        for (int i = 0; i < result.length; i++) result[i] = rates.get(i);
        return result;
    }

    private void applyFrameRateCap(int cap) {
        int best = 1;
        float bestDiff = Float.MAX_VALUE;
        for (int divisor : new int[]{1, 2, 4}) {
            float rate = display.refreshRate / divisor;
            if (rate < 24 && divisor > 1) continue;
            float diff = Math.abs(rate - cap);
            if (diff < bestDiff) {
                bestDiff = diff;
                best = divisor;
            }
        }
        frameRateTarget = Math.round(display.refreshRate / best);
        visualizerView.setFrameDivisor(best);
        quality.setTargetFps(display.refreshRate / best);
        ProjectMJNI.setForceHardCut(false);  // any queued resolution change was dropped
    }

    /** Saved fixed render height if valid for the current panel, else 0 (automatic). */
    private int savedRenderHeight() {
        return QualityController.validFixedHeight(display, prefs.getInt(PREF_RENDER_HEIGHT, 0));
    }

    private int meshLevel() {
        int level = prefs.getInt(PREF_MESH_LEVEL, profile.defaultMeshLevel());
        return Math.max(0, Math.min(level, DeviceProfile.MESH_SIZES.length - 1));
    }

    private int transitionSeconds() {
        return Math.min(MAX_TRANSITION, prefs.getInt(PREF_TRANSITION_DURATION, profile.defaultTransitionSeconds()));
    }

    private static String heightLabel(int height) {
        if (height == 2160) return "4K";
        if (height == 1440) return "1440p";
        return height + "p";
    }

    // ---------------------------------------------------------------------------------------
    // Menus
    // ---------------------------------------------------------------------------------------

    private void initMenus() {
        mainMenu = findViewById(R.id.overlay_menu);
        advancedMenu = findViewById(R.id.advanced_menu);
        presetName = findViewById(R.id.preset_name);
        presetMeta = findViewById(R.id.preset_meta);
        statusLine = findViewById(R.id.status_line);
        diagnostics = findViewById(R.id.diagnostics);
        nowPlaying = findViewById(R.id.now_playing);
        nowPlayingText = findViewById(R.id.now_playing_text);

        TextView versionInfo = findViewById(R.id.version_info);
        versionInfo.setText("v" + appVersion() + "  ·  projectM " + ProjectMJNI.getVersion());

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
        transition.setup("Transition", transitions, transitionSeconds(), false, index -> {
            ProjectMJNI.setSoftCutDuration(index);
            quality.setTransitionSeconds(index);
            prefs.edit().putInt(PREF_TRANSITION_DURATION, index).apply();
        });

        // Resolution: Auto + fixed heights up to the panel's physical resolution.
        int[] heights = QualityController.manualHeights(display);
        String[] resolutionLabels = new String[heights.length + 1];
        resolutionLabels[0] = "Auto";
        int selectedResolution = 0;
        int savedHeight = savedRenderHeight();
        for (int i = 0; i < heights.length; i++) {
            resolutionLabels[i + 1] = heightLabel(heights[i]);
            if (heights[i] == savedHeight) selectedResolution = i + 1;
        }
        OptionRow resolution = findViewById(R.id.row_resolution);
        resolution.setup("Resolution", resolutionLabels, selectedResolution, false, index -> {
            int height = index == 0 ? 0 : heights[index - 1];
            prefs.edit().putInt(PREF_RENDER_HEIGHT, height).apply();
            quality.setMode(height, prefs.getInt(PREF_AUTO_HEIGHT, 0));
        });

        int[] caps = frameRateOptions();
        String[] capLabels = new String[caps.length];
        int selectedCap = caps.length - 1;
        for (int i = 0; i < caps.length; i++) {
            capLabels[i] = caps[i] + " fps";
            if (caps[i] == frameRateTarget) selectedCap = i;
        }
        OptionRow frameRate = findViewById(R.id.row_frame_rate);
        frameRate.setup("Frame rate", capLabels, selectedCap, false, index -> {
            prefs.edit().putInt(PREF_FRAME_RATE_CAP, caps[index]).apply();
            applyFrameRateCap(caps[index]);
        });

        OptionRow advanced = findViewById(R.id.row_advanced);
        advanced.setupAction("Advanced", "›", () -> showMenu(Menu.ADVANCED));

        // Advanced panel
        OptionRow detail = findViewById(R.id.row_detail);
        detail.setup("Detail", DeviceProfile.MESH_LABELS, meshLevel(), false, index -> {
            int[] size = DeviceProfile.MESH_SIZES[index];
            ProjectMJNI.setMeshSize(size[0], size[1]);
            prefs.edit().putInt(PREF_MESH_LEVEL, index).apply();
        });

        OptionRow skipSlow = findViewById(R.id.row_skip_slow);
        skipSlow.setup("Skip slow presets", new String[]{"Off", "On"},
                prefs.getBoolean(PREF_SKIP_SLOW, profile.defaultSkipSlowPresets()) ? 1 : 0, true, index -> {
                    quality.setSkipSlowPresets(index == 1);
                    prefs.edit().putBoolean(PREF_SKIP_SLOW, index == 1).apply();
                });

        OptionRow blank = findViewById(R.id.row_blank_detection);
        blank.setup("Skip blank presets", new String[]{"Off", "On"},
                prefs.getBoolean(PREF_BLANK_DETECTION, true) ? 1 : 0, true, index -> {
                    ProjectMJNI.setBlankDetection(index == 1);
                    prefs.edit().putBoolean(PREF_BLANK_DETECTION, index == 1).apply();
                });

        skippedRow = findViewById(R.id.row_skipped);
        skippedRow.setupAction("Skipped presets", "None", () -> {
            ProjectMJNI.resetSkippedPresets();
            refreshStatus();
        });

        mainMenu.setVisibility(View.GONE);
        advancedMenu.setVisibility(View.GONE);
    }

    private static int nearestIndex(int[] values, int target) {
        int best = 0;
        for (int i = 1; i < values.length; i++) {
            if (Math.abs(values[i] - target) < Math.abs(values[best] - target)) best = i;
        }
        return best;
    }

    /** Shows one panel (or none). The advanced panel slides in over the main panel. */
    private void showMenu(Menu target) {
        handler.removeCallbacks(hideMenu);
        if (target == menu) return;
        Menu previous = menu;
        menu = target;

        if (target == Menu.NONE) {
            slide(previous == Menu.ADVANCED ? advancedMenu : mainMenu, false);
            return;
        }
        fade(nowPlaying, false);
        refreshStatus();
        if (target == Menu.MAIN) {
            if (previous == Menu.ADVANCED) {
                slide(advancedMenu, false);
                fade(mainMenu, true);
                findViewById(R.id.row_advanced).requestFocus();
            } else {
                slide(mainMenu, true);
                findViewById(R.id.random_preset_button).requestFocus();
            }
        } else {
            fade(mainMenu, false);
            slide(advancedMenu, true);
            findViewById(R.id.row_detail).requestFocus();
        }
        handler.postDelayed(hideMenu, MENU_AUTO_HIDE_MS);
    }

    private void slide(View view, boolean in) {
        float offset = dp(24);
        if (in) view.setTranslationX(offset);
        view.animate().translationX(in ? 0 : offset).setDuration(FADE_MS).start();
        fade(view, in);
    }

    /** Alpha fade that ends with GONE, so hidden views cost nothing to compose. */
    private static void fade(View view, boolean in) {
        view.animate().cancel();  // a cancelled animation does not run its end action
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
                if (menu == Menu.NONE) showNowPlaying(currentPreset);
            }
        }
        if (menu == Menu.NONE) return;

        int skipped = ProjectMJNI.getSkippedCount();
        String mode = quality.isAuto() ? "auto" : "fixed";
        if (menu == Menu.MAIN) {
            setText(presetMeta, numberFormat.format(ProjectMJNI.getPresetCount()) + " presets in rotation"
                    + (skipped > 0 ? "  ·  " + numberFormat.format(skipped) + " skipped" : ""));
            setText(statusLine, String.format(Locale.US, "%5.1f fps  ·  %s %s",
                    renderer.getCurrentFps(), heightLabel(quality.currentHeight()), mode));
        } else {
            skippedRow.setActionValue(skipped > 0 ? numberFormat.format(skipped) + "  ·  Reset" : "None");
            setText(diagnostics, String.format(Locale.US,
                    "Render  %dx%d (%s)%nPanel   %dx%d @ %.0f Hz%nUI      %dx%d%nFPS     %.1f of %d%nDevice  %s tier, %d MB RAM",
                    renderer.getSurfaceWidth(), renderer.getSurfaceHeight(), mode,
                    display.physicalWidth, display.physicalHeight, display.refreshRate,
                    display.uiWidth, display.uiHeight,
                    renderer.getCurrentFps(), frameRateTarget,
                    profile.tier.name().toLowerCase(Locale.US), profile.totalRamMb));
        }
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
    // Remote control
    // ---------------------------------------------------------------------------------------

    @Override
    public boolean dispatchKeyEvent(KeyEvent event) {
        if (menu != Menu.NONE) {  // any interaction keeps the menu open
            handler.removeCallbacks(hideMenu);
            handler.postDelayed(hideMenu, MENU_AUTO_HIDE_MS);
        }
        return super.dispatchKeyEvent(event);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (menu != Menu.NONE) {
            if (keyCode == KeyEvent.KEYCODE_BACK) {
                showMenu(menu == Menu.ADVANCED ? Menu.MAIN : Menu.NONE);
                return true;
            }
            if (keyCode == KeyEvent.KEYCODE_MENU) {
                showMenu(Menu.NONE);
                return true;
            }
            return super.onKeyDown(keyCode, event);  // focus navigation inside the panel
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
                showMenu(Menu.MAIN);
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
