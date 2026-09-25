# projectM Android TV: Codebase Analysis & Architecture (v1.8)

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
                                                             ├─ index presets/*.milk from APK
                                                             ├─ load skip list, shuffle
                                                             └─ prefetch next preset text
MainActivity (UI thread)
  ├─ remote keys / menu ──► ProjectMJNI.next/previous/random/settings  (atomic, any thread)
  ├─ Visualizer (audio) ──► ProjectMJNI.addWaveform                    (mutex buffer)
  └─ VisualizerView.setRenderHeight ─► SurfaceHolder.setFixedSize (hardware scaler)

VisualizerRenderer (GL thread) ─► onDrawFrame (native)
  1. apply dirty settings        4. feed buffered audio
  2. first preset / commands     5. projectm_opengl_render_frame
  3. auto-switch requests        6. black-frame detector, FPS → projectM
```

### Threading rules
- Only the GL thread touches the projectM handle (create, render, load, settings).
- All other entry points only write atomics or mutex-protected buffers. This removes a whole class of races and makes `queueEvent()` unnecessary for correctness.

### Preset skipping
A preset is added to `files/skipped_presets.txt` and never picked again when:
1. its file is empty or unreadable;
2. projectM reports a load or compile failure (`projectm_set_preset_switch_failed_event_callback`); or
3. **it renders nothing while music plays.** After the transition plus 2 s, five sparse rows and five columns of the frame are read every 0.5 s (4 bytes × a few thousand pixels, a handful of `glReadPixels` calls). If 5 samples in a row have no pixel brighter than ~8 %, the preset is skipped. Samples taken during silence don't count, so quiet passages never blacklist presets. The check stops at the first visible frame or after 20 s.

*Reset* in the menu clears the list.

### Resolution
The GL surface buffer is resized with `SurfaceHolder.setFixedSize(w, h)`. The display composer scales it to the panel, so a 720p render fills a 1080p or 4K screen without extra GPU work ([Android Developers blog: using the hardware scaler](https://android-developers.googleblog.com/2013/09/using-hardware-scaler-for-performance.html)). projectM always renders at the surface size, so no viewport workarounds are needed.

**True 4K (`DisplayInfo`).** Android TVs commonly drive the UI at 1080p on a 4K panel, while a SurfaceView can still be shown at the panel's full physical resolution. `getRealSize()` reports the UI size, so before 1.8 "Native" was 1080p on such TVs. The physical size is now detected as AndroidX Media3 does in `Util.getCurrentDisplayModeSize`: the `vendor.display-size` / `sys.display-size` property, Sony's 4K panel feature, then `Display.Mode.getPhysicalWidth/Height()`. **Needs on-device confirmation per TV model:** *Advanced › Diagnostics* shows the panel, UI and render sizes.

**Dynamic resolution (`QualityController`).** Heights ladder: 360 … 2160, capped by the panel, with a floor per tier. Once the settle period after a preset change has passed (transition + 3 s), 1-second FPS samples drive it:

| Condition | Action |
|---|---|
| < 85 % of target for 3 s | lower one level (two if far off) **at the next preset switch**, which is forced to be a hard cut |
| < 55 % for 4 s | lower now and switch preset (hard cut) |
| ≥ 97 % for 15 s | try one level higher at the next switch, unless that level recently failed (back-off 3, 6, 12 … 48 presets) |
| < 50 % at the lowest level, *Skip slow presets* on | add the preset to the skip list |

Changes wait for a preset switch because `projectm_set_window_size` resets the renderer; right after a hard cut the new preset starts from scratch anyway, so the reset is invisible. The last automatic level is remembered across launches.

### Frame pacing
Full rate renders continuously (`RENDERMODE_CONTINUOUSLY`). Half rate switches to `RENDERMODE_WHEN_DIRTY` and a `Choreographer` callback calls `requestRender()` on every second vsync: 30 fps at 60 Hz, 25 fps at 50 Hz. A steady half rate looks smoother than an uneven 40–50 fps and leaves the GPU room for heavy presets. projectM animates on wall-clock time, so the speed of the visuals doesn't change.

### Threads
| Thread | Priority | Work |
|---|---|---|
| GL (GLSurfaceView) | `THREAD_PRIORITY_DISPLAY` | projectM render, preset loading, black-frame detection |
| AudioCapture (HandlerThread) | `THREAD_PRIORITY_AUDIO` | `Visualizer` callbacks → `addWaveform` |
| Native worker | default | Preset indexing and prefetch |
| UI | default | Overlay; status polled every 500 ms, text only updated when changed |

### Overlay UI
`OptionRow` is a focusable settings row: ↑/↓ moves between rows, ‹ › changes the value, and center cycles it or runs an action. The main panel (now playing, transport, auto change, duration, transition, resolution, frame rate) ends with **Advanced ›**, which slides a separate panel over it: detail (mesh), skip slow presets, skip blank presets, skipped-preset reset and live diagnostics. BACK returns. Both panels sit within the 48 dp / 27 dp overscan-safe margins. Views fade out and are set to `GONE`, so a hidden overlay costs nothing to draw. Long preset names use a marquee, which is only restarted when the text actually changes.

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
| GitHub Actions: Gradle build + NDK/CMake native build + APK packaging on ubuntu-24.04 | green |
| **On-device test** | **Not done yet.** Needs a run on Shield / TCL / Fire TV |

## 7. What could go wrong

| Risk | Likelihood | Mitigation |
|---|---|---|
| Black detector skips a legitimately very dark preset | Low–medium | Only while audio is playing, 5 consecutive samples, ~8 % threshold; *Reset* restores all |
| Visualizer returns silence (DRM apps, some vendors), so black detection never runs | Medium | Load-failure skipping still works; visuals follow projectM's idle response |
| A device without OpenGL ES 3.0 can no longer install the app | Low (projectM 4 never worked there anyway) | Manifest now states the real requirement |
| `setFixedSize` behaves oddly on a specific TV firmware | Low | Choose "Native" in the menu (uses the layout size) |
| Shader compilation still causes a short hitch on each switch | Certain on weak GPUs | projectM compiles on the GL thread by design; file reading is already prefetched |
| Pulling this change removes build caches from the index | Certain | Harmless; Gradle and CMake regenerate them |

## 8. Recommended next steps
1. Build 1.8 locally (`./gradlew assembleRelease && ./install.sh`) and test on your weakest and strongest TVs.
2. Run `tools/tv-diagnostics.sh <tv-ip>:5555 --sweep` (see `docs/DIAGNOSTICS.md`) for startup, FPS, resolution and composition data.
3. Move Gradle to a stable release.
4. ~~Add CI~~ Done: `.github/workflows/android.yml` (see `docs/RELEASING.md`).
