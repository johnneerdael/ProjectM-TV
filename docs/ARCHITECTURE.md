# projectM Android TV: Codebase Analysis & Architecture (v1.9)

## 1. Summary

Version 1.8 rebuilds the rendering and preset pipeline. The goals were to start visuals right away, skip presets that show nothing, and fix the causes of black presets, several of which were already present before 1.7.

| Area | Before (tag `v1.7`, app "1.6") | After (1.8) |
|---|---|---|
| Startup | Deleted and re-extracted ~9,800 presets (~130 MB) on **every** launch; UI waited up to 15 s | Presets read straight from the APK; indexing (~10k names) on a native background thread; first preset on the first frames |
| Preset switching | D-pad, menu buttons and the startup preset switched presets **from the UI thread** (no GL context) | Commands are queued; the GL thread executes them |
| GL context | OpenGL ES **2.0** requested, but projectM 4 needs ES 3 | ES 3.0 requested (and declared in the manifest) |
| Audio | 8-bit mono samples misread as 16-bit stereo | Raw 8-bit mono passed to `projectm_pcm_add_uint8` |
| Render resolution | Forced to full screen (1.7), setting had no effect; earlier versions shrank the image | Hardware scaler (`SurfaceHolder.setFixedSize`); full screen at any resolution |
| Broken or black presets | Retried forever | Skipped automatically and remembered; reset from the menu |
| Adaptive "performance mode" | Changed preset duration, transition, beat sensitivity and resolution behind the user's back; oscillated | Removed; the user's settings are respected |
| Code size (Java) | 2,830 lines | ~670 lines |
| Tests | None | Host-side engine test suite (23 checks, ASan/UBSan) |

## 2. The 1.7 regression

Tags are off by one: tag `v1.6` = app `versionName "1.5"`, and tag `v1.7` = app `versionName "1.6"` (commit `6b21612`). The regression is the diff `v1.6..v1.7`.

| # | Change in 1.7 | Effect |
|---|---|---|
| R1 | `nativeOnSurfaceChanged` and `VisualizerRenderer.onSurfaceChanged` always use the full display size | The resolution setting became a no-op. Every device rendered at full panel resolution (≥2.25× the pixels of the former 720p default), so FPS dropped |
| R2 | New FPS-driven `optimizeForPerformance()` / `restoreQualitySettings()` with high thresholds (e.g. Shield below 40–50 fps) | Oscillation between modes. Each flip rewrote preset duration (15–35 s), transition (2–10 s) and beat sensitivity (0.6–1.2), and called `setRenderResolution()`. That calls `projectm_set_window_size`, which per `parameters.h` *"will reset the OpenGL renderer"*, so the screen flashed black and the preset's feedback buffer was lost |
| R3 | PCM truncated to 512 values and beat sensitivity lowered to 0.6 whenever "memory optimized" | Visuals reacted less to the music |
| R4 | `applyPerformanceOptimizations()` ran after initialization; `initUI()` hard-coded `autoChangeEnabled = false` | Saved preset and transition durations were overridden; the auto-change state was inconsistent |
| R5 | Duplicated auto-change block in `onDrawFrame` | Redundant logic, two timers |

## 3. Pre-existing defects (also in 1.6)

| # | Defect | Evidence | Effect |
|---|---|---|---|
| P1 | `ProjectMApplication.extractAssets()` deleted and re-copied all presets on every launch (1 KB buffer, background priority); `MainActivity` polled for up to 15 s | Code | Slow startup; a partial playlist if the timeout hit |
| P2 | Preset switches ran on the UI thread (`onKeyDown`, menu buttons, the `postDelayed` startup preset) | Code; GL calls require a current context on the calling thread ([GLSurfaceView docs](https://developer.android.com/reference/android/opengl/GLSurfaceView#queueEvent(java.lang.Runnable))) | projectM compiles shaders while loading a preset. Without a context this fails or leaves the preset blank. **Likely main cause of "some visualizations stay black".** Not verified on a device |
| P3 | ES 2.0 context requested (`setEGLContextClientVersion(2)`) | `readelf`: `libprojectM-4.so` NEEDS `libGLESv3.so`; its built-in shaders are `#version 300 es` | Black output on drivers that honour a strict ES 2.0 request |
| P4 | Visualizer waveform decoded as 16-bit stereo | [Visualizer.getWaveForm](https://developer.android.com/reference/android/media/audiofx/Visualizer#getWaveForm(byte[])): *"8-bit (unsigned) mono PCM samples"* | Silence became a DC offset near full scale; waveform presets drew at the screen edge; weak reactivity |
| P5 | Two independent auto-switch timers (playlist `preset_duration` + Java timer) | Code | Unpredictable switching |
| P6 | Per frame: four JNI viewport calls with `Log.d`, native `LOGI`, `glGetIntegerv` read-backs | Code | Logcat flooding and wasted CPU on weak TV SoCs |
| P7 | `requestRender()` override queued a `glClear` on every audio callback | Code | Unneeded GL work |
| P8 | `ProjectMJNI.destroy()` ran on the main thread while the GL thread could still render; context loss created a second instance without freeing the first | Code | Use-after-free risk and a leak |
| P9 | `assets/presets/.DS_Store` inside the preset folder | Repo | A junk entry wherever the folder is listed blindly |
| P10 | No texture pack shipped and no texture search path set. 1,866 presets reference 71 image textures (`sampler_worms`, `sampler_clouds`, `sampler_rand00` …) | `grep sampler_` over the presets; `libprojectM-4.so` contains `TextureManager::ScanTextures` and `GetRandomTexture` | Those parts of presets render empty, so presets look dull. **Fixed after 1.8:** the projectM texture pack is bundled (it covers 46 of the 71 names; `randNN` then picks from it), copied to `files/textures` on first start, and set with `projectm_set_texture_search_paths` before the first preset |

## 4. Infrastructure findings

| # | Finding | Action in 1.8 |
|---|---|---|
| I1 | Build caches (`.gradle/`, `app/.cxx/`, 95 files including a 16 MB binary) and `.DS_Store` files committed despite `.gitignore` | Removed from the index |
| I2 | Dead code: `jni_simple.cpp` (projectM 3 API), `CMakeLists_simple.txt`, `MainActivity.java.part` | Deleted |
| I3 | Unused `appcompat` and `leanback` dependencies plus Jetifier (`Theme.Leanback` is a local framework-based style) | Removed; the app uses framework APIs only |
| I4 | `install.sh` installed the debug APK (debuggable, slower ART); the JNI layer built at `-O0` in debug | Release build signed with the debug key; `install.sh` prefers it; JNI always `-O2` |
| I5 | `proguard-rules.pro` referenced but missing | Reference removed (minify is off) |
| I6 | projectM playlist library shipped but not needed with the new engine | Deleted (`.so` files and headers) |
| I7 | No automated tests | `app/src/test/native/run_native_tests.sh` |
| I8 | Gradle `9.0-milestone-1` (pre-release) with AGP 8.12 | **Not changed.** Moving to a stable Gradle release is recommended |
| I9 | `local.properties` (machine path) and `.idea/` tracked | **Not changed.** Untracking would delete them from your checkout on pull |

## 5. Architecture

```
ProjectMApplication ── ProjectMJNI.init(assets, skipList) ──► native worker thread
                                                             ├─ read presets.idx (prebuilt list; folder listing as fallback)
                                                             ├─ load skip list, shuffle
                                                             └─ prefetch next preset text
MainActivity (UI thread)
  ├─ remote keys / menu ──► ProjectMJNI.next/previous/random/settings  (atomic, any thread)
  ├─ Visualizer (audio) ──► ProjectMJNI.addWaveform                    (mutex buffer)
  │   or AudioCaptureService (media capture, Android 10+) ──► PcmConverter ──► addWaveform
  └─ VisualizerView.setRenderHeight ─► SurfaceHolder.setFixedSize (hardware scaler)

VisualizerRenderer (GL thread) ─► onDrawFrame (native)
  1. apply dirty settings        5. projectm_opengl_render_frame
  2. first preset / commands     6. output measurement (black skip only if enabled)
  3. auto-switch requests        7. lightweight-transition overlay, capture outgoing frame
  4. feed buffered audio         8. transition stats, FPS → projectM
```

### Threading rules
- Only the GL thread touches the projectM handle (create, render, load, settings).
- All other entry points only write atomics or mutex-protected buffers. This removes a whole class of races and makes `queueEvent()` unnecessary for correctness.

### Preset checks
`tools/check-presets.py` (run by CI) reads every bundled `.milk` file and fails when a preset:
- **cannot react to music:** no `bass`, `mid`, `treb`, `vol` or `*_att` in any equation or shader, the main waveform hidden (`fWaveAlpha` ≤ 0.01 or `wave_a = 0` in code), and no custom waveform enabled;
- uses an **excluded texture** (text, logos or photos of people), or a **texture that isn't bundled**. A texture counts only when its sampler is declared and used, directly or through `#define sampler_x sampler_y`.

`--remove` deletes the failing presets. In 1.9 that removed 116 non-reactive and 73 excluded-texture presets (one was both), leaving 9,606.

### Preset memory (measuring)
The frame buffers of a preset depend only on the resolution. What differs per preset, read from the `.milk` files by `tools/gen-preset-index.py` following projectM's own rules:
- **Images.** projectM loads every image named by `sampler_<name>` or `texsize_<name>` in the warp/comp shaders, used or not, at width × height × 4 bytes (no mipmaps, no power-of-two rounding). Random-image slots count as the largest bundled image. Per preset: median 0.4 MB, max 12 MB.
- **Complex shaders:** the top 1 % by size (≥ 4.2 KB) or with two or more loops. They get a placeholder 32 MB for the GPU driver's compile memory, which can't be read from the file.

The weight (extra MB) is the second column of `presets.idx`: 7,799 presets 0 MB, 1,419 presets 1–4 MB, 388 presets 5 MB or more. 1.9.1 only **measures**. Every `LOAD` log line records the preset's weight, its shader size and loop count, how much the system's available memory dropped, and how much the process grew during the load. The next runs show which presets cause memory peaks at a switch, and whether shaders or images drive them. The RAM-based resolution cap stays in place as a temporary measure until then.

### Preset index
`tools/gen-preset-index.py` writes `app/src/main/assets/presets.idx`: the sorted list of bundled presets, each with a memory weight (see *Preset memory*). CI fails if it is out of date. The worker reads that one small asset. Listing ~10k assets with `AAssetManager_openDir` took 8.4 s on an NVIDIA SHIELD and held the asset-manager lock that UI inflation also needs, so cold start took 10.4 s. Without the index file, the folder is listed as before.

### Transitions
projectM's soft cut renders the outgoing and incoming preset for the whole transition, which doubles CPU (per-vertex equations) and GPU cost and keeps two presets' frame buffers. On a SHIELD at 1260p, 5-second FPS averages fell to 19–36 around every switch, even at 720p.

| Mode | What happens at an automatic switch |
|---|---|
| **Lightweight** | At the end of the frame in which projectM asks for a switch, `SnapshotFade` copies the window into a texture (`glCopyTexImage2D`). The next frame loads the new preset as a hard cut: projectM still seeds it with the old image (`DrawInitialImage`). The snapshot is then drawn over it, fading out with a slow zoom over min(transition, 3 s): one textured full-screen pass per frame. The texture exists only during the fade. |
| **Classic** | projectM's own blend (random transition shader). |
| **Auto** (default) | Lightweight on the LOW tier and below 2.6 GB RAM, otherwise classic. It switches to lightweight for the session when a classic blend runs below 80 % of the FPS before it. |

Remote-control switches, beat-triggered hard cuts and forced hard cuts are never faded. If the capture or the overlay shader fails, the switch uses classic. Every load is logged (`LOAD preset=… ms=…`), and every transition too (`TRANSITION … mode= fps= blend_fps= before_fps= slow_frames=`).

**Not solved yet: the load stall.** `projectm_load_preset_data` parses the preset, loads its textures and compiles its shaders on the GL thread, so the picture freezes for that long at every switch. Hiding it requires a second, shared EGL context that renders projectM off the display thread. The `LOAD` log lines size this before building it.

### Preset skipping
A preset is added to `files/skipped_presets.txt` and never picked again when:
1. its file is empty or unreadable;
2. projectM reports a load or compile failure (`projectm_set_preset_switch_failed_event_callback`);
3. *Skip slow presets* is on and it stays below 50 % of the target FPS at the lowest resolution; or
4. *Skip blank presets* is on (**on by default since 1.9.4**) and it has been black **twice**, in any showings: 5 samples in a row, 1 s apart, with no channel above 20/255 while music plays (samples count only after 3 s of uninterrupted music, since presets that draw from the music start from black). The first time the app only moves on to the next preset and records a strike in `files/skipped_presets.txt.blank`; a one-off (music starting late, a slow build-up) therefore never removes a preset. After 3 black verdicts in a row with no visible preset in between, nothing is struck or skipped until a preset shows output again (a rendering fault must not empty the library).

**Output measurement.** For 20 s after each transition, 5 rows and 5 columns of the window are sampled once per second while audio is present. One `OUTPUT` log line per preset records the luma range (flatness), the share of sampled pixels that changed visibly since the previous sample (luma ≥ 8/255, or hue ≥ 12° on saturated pixels), for the whole frame and for the most active of 40 regions (quarters of each line), and how many changes were luma versus hue-only. Flat and still output are **only measured**. Presets that looked dull on the SHIELD ran on a build without textures, and a wrong skip is permanent, so thresholds get chosen from real runs first. For the same reason, 1.9 clears the skip list once on first launch.

*Reset* in the menu clears the list and the strikes.

### Resolution
The GL surface buffer is resized with `SurfaceHolder.setFixedSize(w, h)`. The display composer scales it to the panel, so a 720p render fills a 1080p or 4K screen without extra GPU work ([Android Developers blog: using the hardware scaler](https://android-developers.googleblog.com/2013/09/using-hardware-scaler-for-performance.html)). projectM always renders at the surface size, so no viewport workarounds are needed.

**True 4K (`DisplayInfo`).** Android TVs commonly drive the UI at 1080p on a 4K panel, while a SurfaceView can still be shown at the panel's full physical resolution. `getRealSize()` reports the UI size, so before 1.8 "Native" was 1080p on such TVs. The physical size is now detected as AndroidX Media3 does in `Util.getCurrentDisplayModeSize`: the `vendor.display-size` / `sys.display-size` property, Sony's 4K panel feature, then `Display.Mode.getPhysicalWidth/Height()`. **Needs on-device confirmation per TV model:** *Advanced › Diagnostics* shows the panel, UI and render sizes.

**Memory limit.** On a 2 GB SHIELD, rendering at 1440p and above made Android's low-memory killer close SoundCloud (a foreground service), taking up to 11 other processes with it. Resolutions are therefore capped by installed RAM (`DeviceProfile.memorySafeHeight`): below 1.6 GB 1080p, below 2.6 GB 1260p, below 3.6 GB 1440p, otherwise the panel. The cap applies to Auto and to the fixed choices. *Advanced › Memory limit › Off* removes it. While the app is visible, `onTrimMemory(RUNNING_LOW / RUNNING_CRITICAL)` lowers the Auto level by one step at the next switch and keeps it there for the session (at most one step per preset). **The thresholds are estimates** from the SHIELD run, which predates the texture pack. The next run should confirm them.

**Dynamic resolution (`QualityController`).** Heights ladder: 360 … 2160, capped by the panel and the memory limit, with a floor per tier. Once the settle period after a preset change has passed (transition + 3 s), 1-second FPS samples drive it:

| Condition | Action |
|---|---|
| < 85 % of target for 3 s | lower one level (two if far off) **at the next preset switch**, which is forced to be a hard cut |
| < 55 % for 4 s | lower now and switch preset (hard cut) |
| ≥ 97 % for 15 s | try one level higher at the next switch. A level that failed is retried once after 10 presets; after a second failure it is not tried again in this session (the SHIELD oscillated 1440 ↔ 1800 before) |
| < 50 % at the lowest level, *Skip slow presets* on | add the preset to the skip list |

Changes wait for a preset switch: in projectM 4.1 `projectm_set_window_size` only stores the size, and each preset reallocates its frame buffers (losing their contents) on its next frame. Right after a hard cut the new preset starts from scratch anyway, so the reallocation is invisible. The last automatic level is remembered across launches.

### Frame pacing
Full rate renders continuously (`RENDERMODE_CONTINUOUSLY`). Half rate switches to `RENDERMODE_WHEN_DIRTY` and a `Choreographer` callback calls `requestRender()` on every second vsync: 30 fps at 60 Hz, 25 fps at 50 Hz. A steady half rate looks smoother than an uneven 40–50 fps and leaves the GPU room for heavy presets. projectM animates on wall-clock time, so the speed of the visuals doesn't change.

### Threads
| Thread | Priority | Work |
|---|---|---|
| GL (GLSurfaceView) | `THREAD_PRIORITY_DISPLAY` | projectM render, preset loading, output measurement, transition overlay |
| AudioCapture (HandlerThread) | `THREAD_PRIORITY_AUDIO` | `Visualizer` callbacks → `addWaveform` |
| PlaybackCapture (media capture only) | `THREAD_PRIORITY_AUDIO` | `AudioRecord` reads (1024 frames) → `PcmConverter` → `addWaveform` |
| Native worker | default | Preset indexing and prefetch |
| UI | default | Overlay; status polled every 500 ms, text only updated when changed |

### Overlay UI
`OptionRow` is a focusable settings row: ↑/↓ moves between rows, ‹ › changes the value, and center cycles it or runs an action. The main panel (now playing, transport, auto change, duration, transition, resolution, frame rate) ends with **Advanced ›**, which slides a separate panel over it: detail (mesh), transitions (Auto / Lightweight / Classic), memory limit, skip slow presets, skip blank presets, skipped-preset reset and live diagnostics. BACK returns. Both panels sit within the 48 dp / 27 dp overscan-safe margins. Views fade out and are set to `GONE`, so a hidden overlay costs nothing to draw. Long preset names use a marquee, which is only restarted when the text actually changes.

### Device tiers (`DeviceProfile`)
| Tier | Rule | Auto start / floor | Frame rate | Detail (mesh) | Transition | Skip slow |
|---|---|---|---|---|---|---|
| HIGH | NVIDIA Shield / Tegra | 1440p / 720p | 60 | High 64×48 | 7 s | off |
| STANDARD | everything else | 1080p / 540p | 60 | Medium 48×32 | 7 s | off |
| LOW | `isLowRamDevice()` or <1.6 GB RAM (e.g. older Fire TV sticks) | 720p / 360p | 30 | Low 32×24 | 2 s | on |

Detail levels: Minimal 24×16, Low 32×24, Medium 48×32, High 64×48, Ultra 96×72. The per-vertex equations run on the CPU for every vertex on every frame, which is usually the bottleneck on low-end ARM boxes.

Saved resolution preferences are kept. The former "4K" choice maps to "Native".

## 6. Verification performed

| Check | Result |
|---|---|
| Native engine compiled with `-Wall -Wextra` (host clang, projectM 4.1 headers, stub Android headers) | Clean |
| Java compiled against the Android 14 framework (`android-all` jar) with a generated `R` | Clean (deprecation warnings only) |
| All 19 JNI names and signatures cross-checked (`javac -h` header compiled against the implementation) | Match |
| Host engine tests under ASan + UBSan: indexing/filtering, first frame, settings, next/random/previous, auto-switch, forced hard cut, mesh re-apply, failure skip + persistence, audio cap, black detection (silence / visible / black / disabled), skip-current, reset, context-loss resume | all pass |
| JVM tests (`QualityControllerTest`): levels per panel, change only at preset switch, back-off, severe drop, slow-preset skip, low-tier floor | 5/5 pass |
| 1.9 host engine tests (ASan + UBSan): `presets.idx` with CRLF/blank/junk lines and folder fallback; lightweight capture → hard cut → fade; remote switch ends fade; hard cuts never faded; capture failure → classic; classic mode; Auto switches only after a slow classic blend; black skipping off by default; `OUTPUT` flat/still lines; readback from the window framebuffer | all pass |
| 1.9 `fade_gl_test` on Mesa llvmpipe (OpenGL ES 3.2, headless EGL): capture, fade curve (start / half / end), self-stop, GL state restored (blend, scissor, program, VAO, texture unit, sampler binding) | all pass |
| 1.9 JVM tests: memory limit caps Auto and fixed levels, remembered 4K clamped, memory pressure lowers once per preset, second failure blocks a level | 9/9 pass |
| GitHub Actions: Gradle build + NDK/CMake native build + APK packaging on ubuntu-24.04 | green |
| **On-device test** | **Not done yet.** Needs a run on Shield / TCL / Fire TV |

## 7. What could go wrong

| Risk | Likelihood | Mitigation |
|---|---|---|
| Black detector skips a legitimately very dark preset | Low (off by default since 1.9) | Only when enabled, only while audio plays, 5 consecutive samples; *Reset* restores all |
| Memory limit too strict on a device with plenty of free RAM, or too loose once textures are loaded | Medium | Estimates from one SHIELD run; *Memory limit › Off*; `onTrimMemory` lowers further at runtime; confirm with the next diagnostics run |
| `glCopyTexImage2D` from the window is slow or unsupported on a driver | Low | Only on switch frames; any GL error falls back to classic; *Transitions › Classic* |
| The fade's still frame looks worse than projectM's blend on strong devices | Medium (taste) | Auto keeps classic where it runs at full speed; *Transitions › Classic* |
| Visualizer returns silence (DRM apps, some vendors), so black detection never runs | Medium | Load-failure skipping still works; visuals follow projectM's idle response |
| A device without OpenGL ES 3.0 can no longer install the app | Low (projectM 4 never worked there anyway) | Manifest now states the real requirement |
| `setFixedSize` behaves oddly on a specific TV firmware | Low | Choose "Native" in the menu (uses the layout size) |
| Preset load (parse, textures, shader compile) still freezes the picture at each switch | Certain | Measured by `LOAD` log lines; the fix (second shared EGL context) is planned once sized |
| Pulling this change removes build caches from the index | Certain | Harmless; Gradle and CMake regenerate them |

## 8. Recommended next steps
1. Build 1.8 locally (`./gradlew assembleRelease && ./install.sh`) and test on your weakest and strongest TVs.
2. Run `tools/tv-diagnostics.sh <tv-ip>:5555 --sweep` (see `docs/DIAGNOSTICS.md`) for startup, FPS, resolution and composition data.
3. Move Gradle to a stable release.
4. ~~Add CI~~ Done: `.github/workflows/android.yml` (see `docs/RELEASING.md`).

## Audio sources

**Why the Visualizer can hear nothing.** On an NVIDIA SHIELD (Android 11) with HDMI eARC and Dolby output, media is mixed on an output of the Dolby "MSD" module (`AUDIO_DEVICE_OUT_BUS`), encoded to E-AC3 and bridged to HDMI. Android picks the output for session-0 effects in `AudioPolicyManager::selectOutputForMusicEffects()` from the outputs of the device media would normally use (HDMI), not the MSD outputs. No active output qualifies, so it falls back to the idle primary output, and the Visualizer receives silence. The 1.9 diagnostics show exactly this: the Visualizer (effect 51) sits on `AudioOut_D` with 0 tracks while SoundCloud plays on `AudioOut_1D`. The selection code is unchanged in Android 14 (see the [Android 11](https://raw.githubusercontent.com/LineageOS/android_frameworks_av/lineage-18.1/services/audiopolicy/managerdefault/AudioPolicyManager.cpp) and [Android 14](https://raw.githubusercontent.com/LineageOS/android_frameworks_av/lineage-21.0/services/audiopolicy/managerdefault/AudioPolicyManager.cpp) sources, LineageOS mirror).

**Media capture.** Playback capture copies a matching track's audio before the Dolby module, independently of which output Android chose (`AudioPolicyMix.cpp`: a loop-back-and-render mix is a secondary output of the track). `AudioCaptureService`:
- matches `USAGE_MEDIA` only, so notification, system and assistant sounds never reach the visuals;
- runs as a foreground service of type `mediaProjection` and starts foreground before it creates the projection (required on Android 14);
- reads 16-bit stereo at 48 kHz in blocks of 1024 frames. `PcmConverter` sums the channels and scales each block so its peak reaches 0.99 of full range, as the Visualizer's normalized mode does (`EffectVisualizer.cpp`). Presets should therefore react the same to either source.

Only one source feeds the engine: the Visualizer is released while capture runs and recreated when it ends. The consent result can't be stored for later, so the app asks again at every launch. Declining it, or a device without the consent dialog, switches the setting back to *Standard*.

**Limits.** Apps can opt out of capture (`setAllowedCapturePolicy`, or targeting Android 9 or lower without opting in), and audio that an app sends to the TV already Dolby-encoded is never mixed, so neither source can see it.
