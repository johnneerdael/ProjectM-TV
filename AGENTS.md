# ProjectM TV contributor instructions

## Pull requests and release notes

Each successfully tested merge to `main` publishes a versioned APK and one Native core AAR, then updates Milkbeat through the canonical core alias. Use a feature branch and PR for changes. Android APK CI retains full Git history and tags with `filter: blob:none`; current source and historical version metadata are fetched on demand rather than downloading every historical evidence blob.

- Include a substantive `## Release notes` section in every PR body. Follow `.github/pull_request_template.md`.
- Write for people using the app: describe the changed behavior, its effect, and relevant limits. Include a concrete trigger or before/after example when useful.
- State only changes supported by the final diff and verified evidence. Avoid invented performance figures, broad crash-free claims, or promises beyond the implementation.
- Keep release notes aligned with the final PR scope. Rewrite them when implementation changes.
- Use an `Internal` subsection for documentation, tests, or CI-only work with no user-visible effect, and explain the actual change. A bare “No user-visible changes” is insufficient.
- Put test commands/results in `## Validation`, outside release notes. Omit badges, agent transcripts, implementation process, and manual install instructions from the release-notes section.
- Let CI append the current Downloader code, APK/core AAR links, checksums and comparison link. Update the canonical install blockquote in `README.md` when the Downloader code changes.
- Preserve upstream attribution when describing backported fixes.
- Do not bump versions in routine PRs. The base version/code/commit in `app/build.gradle` define the automatic release sequence. Change them together only for a planned new release line; follow `docs/RELEASING.md`.

For release tooling changes, run `python3 -m unittest discover -s .github/scripts/tests -v`. Review factual accuracy of the PR release notes: CI validates their presence and placeholders, not the truth of English prose.

## Maintaining this file

Keep the repository-specific sections below current whenever a task changes architecture, commands, dependencies, documentation or constraints, in the same worktree and PR as that task. Record only facts backed by repository files or observed command results; mark unverified commands and unresolved facts explicitly, and link to existing docs instead of duplicating them. Do not import assumptions from other repositories (including Milkbeat).

CI/review workflow discovery: 2026-10-05 against `main` at `910e837b`; JDK 21.0.11, resolved JUnit 4.13.2/Hamcrest 1.3, release JVM tests, release APK/Native AAR and strict MkDocs build verified. Last full discovery: 2026-10-04, against `main` at `4fc66208` (projectM patch series 0001–0029). "Verified" below means the command was run with the stated result on that date; everything else is described from the source files and CI configuration.

## Repository overview

ProjectM TV is a music visualizer for Android TV, powered by **ProjectM TV Engine**, the maintained projectM fork based on upstream 4.1.7 plus this repository's patch series. It renders MilkDrop presets that react to the audio another app plays on the same TV; it is not a music player. It bundles 9,606 *Cream of the Crop* presets. GitHub: `johnneerdael/ProjectM-TV` (verified with `gh repo view`; a checkout's `origin` URL may still use the former name `projectm-android-tv`, which redirects).

| | `:app` | `:core` |
|---|---|---|
| Type | Android application (APK) | Android library (AAR), the engine |
| Namespace / Java package | `com.example.projectm.visualizer` (legacy package; the installed ID differs) | `nl.neerdael.projectm.core` |
| Application ID | `nl.neerdael.projectmtv` (since 1.9.7); suffixes `.profile`, `.presettest`, `.setuptest` for side-by-side builds | – |
| Languages | Java (source/target 1.8), XML views | Java + C++17 (JNI), CMake; builds `libprojectmtv.so` |
| SDK levels | compileSdk 34, targetSdk 34, minSdk 21 | compileSdk 34, minSdk 21; ABIs `armeabi-v7a`, `arm64-v8a` |
| Dependencies | `project(':core')`; test: JUnit 4.13.2. No AndroidX, Kotlin or Compose (framework APIs only, to keep the APK small) | test: JUnit 4.13.2; projectM built from source |

- **Devices:** Android TV only. The manifest requires `android.software.leanback`, OpenGL ES 3.0 and audio output; touchscreen, gamepad and microphone are optional. README: Android 5.0+ (API 21), at least 2 GB RAM highly recommended, no touch/phone support.
- **Build types (no product flavors):** `debug`; `release` (R8 minify + resource shrinking, release key when `SIGNING_KEYSTORE_PATH` is set, otherwise the local debug key); `profile` (`initWith release`, debug key, `.profile` suffix, `profileable` via `app/src/profile/AndroidManifest.xml`). Gradle properties `-PpresetLabDeviceTest` / `-PsetupScreenshotTest` give the debug build the `.presettest` / `.setuptest` suffix and a distinct app name.
- **Entry points:** `ProjectMApplication` (one-time preference migrations, `ProjectMCore.init`); `MainActivity` (single `singleTask` landscape activity: UI, remote keys, audio capture, settings panels); `TrackListenerService` (notification listener used only for media sessions); `Updater` + `UpdateFileProvider` (opt-in GitHub auto-update). Engine: `ProjectMCore`, `ProjectMJNI`, `VisualizerView`, `VisualizerRenderer`, `QualityController`, `DeviceProfile`, `DisplayInfo`; native `core/src/main/cpp/native-lib.cpp` plus `snapshot_fade.cpp` and `preset_prewarm.cpp`.
- **projectM relationship:** submodule `third_party/projectm` tracks upstream `https://github.com/projectM-visualizer/projectm.git`, pinned at tag `v4.1.7` (commit `e0b0a967`). All engine changes are the ordered patch series `tools/projectm-patches/NNNN-*.patch` (0001–0044;0044 preserves float32 shader literal round-trips and rejects nonfinite literals;0043 preserves authored shape/wave recurrence and explicit per-vertex shape inputs;0038 supplies the legacy diffusion/fallback,0039 is the historical capped-policy opt-out,0040 preserves implicit globals,0041 preserves blur framebuffer bindings,0042 adds instance-owned authored feedback/native trail detail), applied at CMake configure time by `core/src/main/cpp/CMakeLists.txt` and linked statically into `libprojectmtv.so`. The personal fork `johnneerdael/projectm` is not referenced by the build; it is used for upstream PRs.
- **App/core boundary and Milkbeat:** `:app` holds UI, audio capture, track titles and the updater; `:core` holds the engine, JNI, presets, textures and preset indexes. [Milkbeat](https://github.com/johnneerdael/Milkbeat) consumes the released core AAR: CI publishes the single Native `projectM-TV-core-<version>.aar` and canonical alias, then dispatches `projectm-core-release` to Milkbeat (see *Generated artifacts*). Milkbeat consumes canonical artifact names and uses QualityController; managed hosts acknowledge context/configuration generations and publish a coherent size/trails/transition tuple after live RAM review. Retired fixed-resolution and static-RAM methods normalize to Auto.
- **Build tasks:** `./gradlew assembleRelease` (APK at `app/build/outputs/apk/release/app-release.apk` and AAR at `core/build/outputs/aar/core-release.aar`), `./gradlew :core:assembleRelease`, `./gradlew assembleDebug`, `./gradlew assembleProfile`.
- **Single Native core:** `:core` and the APK use Native rendering; canonical `projectM-TV-core[-<version>].aar` names contain Native bytes. The separate capped/core-native artifacts are retired for new releases; preserve historical releases. Deprecated `-PprojectmCoreRenderingPolicy=native` remains accepted; `capped` is rejected. QualityController is always Auto up to the physical panel and uses live FPS/memory headroom. Its fixed-mode/static-RAM compatibility methods normalize to Auto. JNI defaults Standard trails; settings are additive (`setNativeTrails`, `getNativeTrailsStatus`). The underlying projectM C API retains explicit-off compatibility controls. See `docs/RELEASING.md`.

The focused `tools/milk-analyzer` subset imports PR #25's selector-domain proof and
models the native implicit-global policy. It also includes the separate beta activity
scorer using the published standard core AAR through JNI, and a source-bound collection
exporter/verifier. Its direct-delta beta model is fitted on eight historical user
judgments transferred onto native features; archived producer and derived-scoring
identities are kept separate. Optional offline refitting uses
`tools/milk-analyzer/requirements-calibration.txt`. These execution-based predictions are not independent source-only
visual forecasts. Build its source adapters against a hash-
identified host engine before `python -m pytest tools/milk-analyzer -q`; Preset Lab CI
performs this setup. Its results are source diagnostics, not visual certification.

## Codebase navigation and knowledge tools

- No `.codegraph/` or `graphify-out/` exists at the repository root (checked 2026-10-04). Use `git grep`/`rg`; do not assume a code graph.
- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) §5 (threading rules, transitions, resolution, frame pacing, threads, overlay UI, device tiers). Its title says v1.9 and §1–4 and §6–8 are historical analysis; verify against the code. Design specs, plans and evidence for engine work are in `docs/superpowers/{specs,plans,evidence}`.
- projectM sources: `third_party/projectm` shows patched code only after a CMake configure or a manual apply; the committed source of truth is `tools/projectm-patches/`. Search both the submodule and the patches.
- Logs for tracing behavior: native tag `projectM-Native` (`LOAD`, `PREWARM`, `TRANSITION`, `OUTPUT` lines per switch); `VisualizerRenderer` logs `STATS fps=… surface=… audio=…` every 5 s.
- Committed generated data indexes (not code indexes): `core/src/main/assets/presets.idx` (regenerate with `tools/gen-preset-index.py` whenever presets or textures change; CI enforces `--check`) and the collection bundle in `core/src/main/assets/preset-genres/` (current beta schema2 produced/verified with `tools/milk-analyzer/beta_export.py`;
  legacy schema1 Preset Lab imports are historical).

## Design and user experience

Follow the project's established design system and platform conventions. Reuse existing theme tokens and components. Preserve accessibility, keyboard/focus behavior, responsiveness, and supported input methods. Avoid introducing decorative styles or changing appearance incidentally during a refactor.

- **Toolkit:** framework Views and XML only (no AndroidX, Leanback library, Material or Compose). One layout, `app/src/main/res/layout/activity_main.xml`. Theme `Theme.Leanback` in `res/values/themes.xml` (parent `@android:style/Theme.Black.NoTitleBar.Fullscreen`); text styles `Overlay.*` in `res/values/styles.xml`; tokens in `res/values/colors.xml` and `dimens.xml`; drawables in `res/drawable*`. Reusable views: `OptionRow` (focusable settings row), `AudioMeterView`, `TrackCorner`. Dialogs use `android.R.style.Theme_DeviceDefault_Dialog_Alert`.
- **Remote/D-pad contract** (`MainActivity.onKeyDown`/`dispatchKeyEvent`; documented in the README *Remote control* table and `docs/user-guide/controls.md`; keep all three in sync):
  - No panel: Right/Next/Fast forward = random preset (hard cut); Left/Previous/Rewind = previous preset; Up/Down/Info = show the track again; Center/Enter/Menu = open the panel; Back exits.
  - Panel open: Up/Down move focus between rows, Left/Right change a value, Center cycles or runs an action; Back closes (from *Advanced* or *Track display* it returns to the main panel); Menu closes; it hides after 10 s without input, and every key event restarts that timer.
- **Layout:** landscape, fullscreen, immersive sticky. The GL surface renders at its own size (`SurfaceHolder.setFixedSize`) and is scaled by the display; the overlay UI uses the UI resolution.
- **Accessibility:** no documented requirements and no TalkBack verification found; the layout has only three `contentDescription` attributes. Keep every new control reachable by D-pad focus and give icon-only controls a `contentDescription`.
- **Visual references:** user-guide setup screenshots (`docs/user-guide/images/setup/`) come from the `-PsetupScreenshotTest` build on an Ugoos AM6. Rendering changes need before/after captures (PR template).

## Use existing platform and dependency APIs

Before implementing a component, parser, formatter, scheduler, transport, or similar utility:

1. Check existing project code for a suitable implementation.
2. Check the declared and resolved dependencies for a supported API.
3. Verify the API and recommended usage against the version in use and official documentation.
4. Implement a custom alternative only when the existing options are absent or unsuitable, and record the reason in the PR.

Prefer configuration, composition, or a small wrapper to copied library source or overlapping dependencies. Use maintained implementations for security-sensitive primitives.

| Need | Existing API / implementation | Version truth | Constraints |
|---|---|---|---|
| Audio input | `android.media.audiofx.Visualizer` on the player's session (`PlayerSessionFinder`), on the `AudioCapture` `HandlerThread` → `ProjectMJNI.addWaveform` | framework, minSdk 21 | 8-bit mono; needs `RECORD_AUDIO`; no microphone use |
| Playing track | `MediaSessionManager` via `TrackListenerService` / `TrackWatcher` | framework | needs notification access; no notification content is read |
| Rendering | `GLSurfaceView` + GLES 3.0 + projectM C API via JNI | `third_party/projectm` tag + `tools/projectm-patches/` | projectM handle only on the GL thread |
| Frame pacing | `Choreographer` in `VisualizerView` | framework | |
| Settings | `SharedPreferences` file `projectm_settings` | framework | see *Dependencies, state, and lifecycle* |
| Auto-update | `HttpURLConnection` + `Updater` + custom `UpdateFileProvider` (no AndroidX `FileProvider`) | framework | the app's only network use; off by default |
| Engine fixes | new patch in `tools/projectm-patches/` | patch series | never edit committed submodule files |
| Preset analysis | `tools/preset-lab` (numpy, opencv-python-headless) | `tools/preset-lab/pyproject.toml`, `requirements.lock` | offline only; does not change the Android renderer |
| Docs site | MkDocs | `docs/site-requirements.txt` (`mkdocs==1.6.1`) | |
| Build toolchain | AGP 8.12.0, Gradle 8.14.2, NDK 27.3.13750724, CMake 3.22.1 | `build.gradle`, `gradle/wrapper/gradle-wrapper.properties`, `app/build.gradle`, `core/build.gradle` | no version catalog |

Adding AndroidX or another runtime dependency departs from the documented small-APK policy (`app/build.gradle`) and affects F-Droid reproducibility; justify it in the PR.

## Performance and resource use

Avoid blocking work on latency-sensitive threads, unnecessary polling, duplicate requests, unbounded concurrency, and background work that outlives its owner. Honor existing cache, cancellation, visibility, lifecycle, and resource-release contracts. Back performance claims with measurements and state what was not measured.

- **Threads** ([ARCHITECTURE §5 *Threads*](docs/ARCHITECTURE.md)): GL thread (`THREAD_PRIORITY_DISPLAY`) owns the projectM handle (create, render, load, settings) and output measurement; `AudioCapture` HandlerThread (`THREAD_PRIORITY_AUDIO`); a native worker for preset indexing and prefetch; a background shader-compile `std::thread` started from the GL thread (`preset_prewarm`); the UI polls status every 500 ms. Other entry points only write atomics or mutex-protected buffers; keep it that way.
- **Visibility and cleanup:** `MainActivity.onPause` stops the track watcher, UI refresh, updater and audio, then calls `visualizerView.onPause()`; `onResume` restarts them and re-checks notification access. `onDestroy` releases projectM on the GL thread (`queueEvent(renderer::release)`); after context loss the next `onSurfaceCreated` cleans up.
- **Frame pacing/quality:** half-refresh-rate pacing uses Choreographer. QualityController always uses Auto up to the detected panel, with FPS hysteresis/CPU-bound probe checks and a live ActivityManager memory budget initialized from application context in ProjectMCore.init. Standard is the Native trails default; Medium/High add the same passes with different gain. No user-facing fixed-resolution/static-RAM controls remain. Use `QualityController.setRenderAllocationSettings(trails, transitionSeconds)` to review the final tuple atomically. The controller captures the pre-edit allocation before height callbacks. After renewing the FPS generation, use `revalidateForAllocationChange()`: confirmed reductions defer memory sampling until the new tuple renders and releases old textures, while net growth and pending allocations require a full review. Managed clients publish dimensions/trails/transition as one generation-tagged rendering configuration; GL holds allocation settings until surface-size acknowledgement. Use `revalidateForResume` for preserved/context-recreated resumes, reject stale generations, and base FPS on completed frames tagged with context/size. When an applied size change has `wasLastChangeForMemoryPressure()`, call the existing native pressure hook to flush pooled textures and pause prewarming. Do not claim a universal music-process survival guarantee from heuristic headroom.
- **No measured universal frame-time or memory bound is defined. Automatic memory uses documented conservative footprint/reserve estimates; see `docs/superpowers/specs/2026-10-05-native-trails.md`.** Compare before/after on the same TV, preset, render height and audio (PR template).
- **Measurement tools:** profile build + simpleperf ([docs/PROFILING.md](docs/PROFILING.md)); pin a preset with `adb shell setprop debug.projectmtv.preset '<name prefix>'` and clear it afterwards (`debug.projectmtv.update_from` also exists); `tools/tv-diagnostics.sh <tv-ip>:5555 --no-install --duration 180` ([docs/DIAGNOSTICS.md](docs/DIAGNOSTICS.md); profile builds require `--package nl.neerdael.projectmtv.profile` with a matching `--apk` or `--no-install`; build/`--release` modes reject alternate package IDs before connecting); Record actual Auto render sizes and compare target-FPS/trails workloads rather than forcing a resolution sweep. Preset Lab provides offline rendering comparisons (desktop timings do not establish TV performance).
- **Documented device coverage:** NVIDIA SHIELD TV 2019 (`sif`, 2 GB, 32-bit) and SHIELD TV Pro 2019 (`mdarcy`, 3 GB), Android 11; Ugoos AM6 (Amlogic S922X, Mali-G52 MP6, Android 9). No emulator configuration is committed.
- **The notification listener restarts the app after `am force-stop`** (within about a second, verified on the AM6, Android 9, and the AM9 Pro, Android 14): a stop/start is warm, and the process reads `projectm_settings` at that restart. A process that reads the file mid-write saves its migration flags over it. Resolve `am get-current-user` once; use that numeric ID for settings/listener commands, permission grants, installation and `am force-stop`/`am start`. Filter `ps -A -o UID,PID,NAME` by exact process name and `UID / 100000` for that user; `pidof` includes other users. Failed/malformed queries must not mean "no process". Write `/data/user/<userId>/<package>/shared_prefs/projectm_settings.xml`, not user 0's `/data/data` alias. Disallow the listener only if that user enabled it, restore the same user's access, and check `surface=` in its STATS lines ([docs/PROFILING.md](docs/PROFILING.md)); `tv-diagnostics.sh` uses this scope for its cold start and records the user. Command support was checked in Android 9/14 sources; older releases remain unverified.
- **Diagnostics signing conflicts:** `--allow-uninstall` attempts removal only for the captured Android user. Before removing data, inspect `pm list users` and exact package results from `pm list packages --user <userId>` for every other user, including stopped users; refuse if another user has the package or a query fails/is malformed. Shared or preinstalled package code can retain the incompatible signing key. A retained conflict fails explicitly after the scoped retry; never broaden to all-user uninstall. Use `--no-install` or a matching-key APK instead ([docs/DIAGNOSTICS.md](docs/DIAGNOSTICS.md)).
- **Measured lessons (ARCHITECTURE §5):** listing ~10k assets took 8.4 s and blocked UI inflation → the worker reads `presets.idx`; GL linking at switches froze the picture 0.5–1.9 s → background prewarm and program caches; tile-based GPUs paid for render-target loads → patches 0009–0016.

## Dependencies, state, and lifecycle

Follow the existing dependency injection and ownership model. Prefer explicit dependencies and testable boundaries. Preserve instance identity, initialization timing, lifecycle, cancellation, and cleanup when refactoring. Keep migrations focused on the task and avoid creating duplicate services, caches, clients, or background workers.

- **No DI framework.** `MainActivity` constructs its collaborators directly (`TrackWatcher`, `QualityController`, the `AudioCapture` handler thread). `Updater` is a process-wide singleton (`Updater.get`, own `Updater` background thread; the activity attaches/detaches its listener). The engine is a process-wide native singleton behind static `ProjectMJNI` methods.
- **Initialization:** `ProjectMCore.init(context)` once from `Application.onCreate` (safe to repeat); it keeps the application `AssetManager` for the process lifetime and starts native preset indexing and the one-time texture copy before the first preset loads.
- **Persistence:** `SharedPreferences` `projectm_settings` (`MainActivity`, `ProjectMApplication`); `files/skipped_presets.txt` (skip list, `ProjectMCore.skipListFile`); `files/textures/` (texture copy). `android:allowBackup="true"`. There is no schema version: one-time migrations in `ProjectMApplication` are guarded by boolean keys (`skip_list_reset_1_9`, `frame_rate_reset_30`); add a new key for a new migration rather than reusing one.
- **Settings flow:** Java writes settings through `ProjectMJNI` setters; native code applies dirty settings on the GL thread at the next frame.
- **Validation when changing these:** native engine tests (commands, skip list, transitions, context loss), `QualityControllerTest`, app JVM tests, and a TV check of pause/resume (Home and return), audio re-attachment and low-memory behavior.

## User-facing text and localization

Use the project's established resource or localization mechanism for user-facing text. Follow its locale ownership and translation workflow; do not invent an English-only or all-locales policy.

- **Not localized today.** `app/src/main/res/values/strings.xml` holds only `app_name` (overridden by `resValue` for test builds); there are no `values-*` locale directories and no translation workflow. UI text is English literals in Java (`MainActivity`, `OptionRow`, …) and the layout XML. Introducing localization is a deliberate change that should move strings to resources consistently.
- **Wording conventions:** the app name is "ProjectM TV" and its maintained engine is "ProjectM TV Engine". Use "based on projectM 4.1.7" for upstream provenance; do not present the patched engine as stock upstream 4.1.7. The core AAR shares the app release version; `ProjectMJNI.getVersion()` still reports the upstream version. Preserve package/API/artifact names and historical evidence identities. Menu paths use `›` (e.g. *Settings › Advanced › Auto-update*). Keep setting names and values identical in the UI, the README settings tables and `docs/user-guide/settings.md`.
- Store listing text: `fastlane/metadata/android/en-US/` (F-Droid metadata, English only).

## Code structure and modularization

Place code according to its responsibility and actual consumers. Reuse shared code when appropriate without creating speculative abstractions. Split oversized or mixed-responsibility files along meaningful boundaries. Preserve behavior during refactors and remove obsolete code.

| Responsibility | Location |
|---|---|
| App UI, audio capture, track titles, updater | `app/src/main/java/com/example/projectm/visualizer/` |
| App resources; profile-build manifest | `app/src/main/res/`; `app/src/profile/` |
| App JVM tests | `app/src/test/java/com/example/projectm/visualizer/` |
| On-device tests | `app/src/androidTest/…` (`MusicCategoryInstrumentation` is a custom `Instrumentation` and the configured runner; `TrackAccessSetupTest`) |
| Engine Java API | `core/src/main/java/nl/neerdael/projectm/core/` |
| JNI and native engine glue | `core/src/main/cpp/` (`native-lib.cpp`, `snapshot_fade.*`, `preset_prewarm.*`, `CMakeLists.txt`) |
| Core JVM tests | `core/src/test/java/…` (`QualityControllerTest`) |
| Native host tests | `core/src/test/native/` (`engine_test.cpp` against stubs, `fade_gl_test.cpp`, `projectm-regressions/`) |
| Presets, textures, indexes | `core/src/main/assets/{presets,textures,presets.idx,preset-genres}` |
| projectM changes | `tools/projectm-patches/NNNN-<slug>.patch` (4-digit order, header explains the change and any upstream source) |
| Upstream engine (do not commit edits) | `third_party/projectm` |
| Tools | `tools/*.sh`, `tools/*.py`, `tools/preset-lab/` |
| Release tooling / CI | `.github/scripts/` (+ `tests/`), `.github/workflows/` |
| Docs | `README.md`, `docs/`, `docs/user-guide/` |

- JNI functions bind by name (`Java_nl_neerdael_projectm_core_ProjectMJNI_*`), kept by `core/consumer-rules.pro`; renaming `ProjectMJNI`, its package or a native method requires matching native changes and breaks consumers.
- No file-size limits are established. `MainActivity.java` (~1,200 lines) and `native-lib.cpp` (~2,000 lines) are large; split only along real responsibilities.
- Root scripts `build.sh`, `build_android.sh`, `debug.sh`, `install.sh` are local helpers not used by CI (not validated).

## Repository-specific constraints

Preserve the release/version rules above. Treat the core AAR’s interface and compatibility with Milkbeat as an integration boundary; verify the actual API and consumers before changing it.

- **Core API:** public classes in `nl.neerdael.projectm.core` (`ProjectMCore`, `ProjectMJNI` incl. `TRANSITION_*` constants, `VisualizerView`, `VisualizerRenderer`, `QualityController`, `DeviceProfile`, `DisplayInfo`) are used by `:app` and by Milkbeat through the released AAR. There is no API/ABI compatibility check. Before removing or changing public members or native signatures, inspect Milkbeat's usage. Because every `main` merge publishes the core and triggers a Milkbeat rebuild, a deliberate incompatible change needs a coordinated Milkbeat change; no written procedure exists yet (unresolved).
- **Native toolchain:** NDK `27.3.13750724`, CMake `3.22.1`, C++17, ABIs `armeabi-v7a`/`arm64-v8a`, projectM linked statically. Keep the reproducible-build settings in `CMakeLists.txt` (`-ffile-prefix-map`, disabled flex/bison) and `dependenciesInfo` off in `app/build.gradle`: F-Droid rebuilds and compares the release APK.
- **projectM patches:** never commit edits inside `third_party/projectm` (submodule has `ignore = dirty`). To write a patch: apply the existing series in `third_party/projectm` and stage it (`git -C third_party/projectm add -A`) so new edits show as a clean diff, then use `tools/regen-projectm-patch.sh <name>`. That script only diffs `src/` and `tests/`; patches touching `vendor/hlslparser` (0003, 0008, 0018, 0019, 0021, 0030, 0031) must be produced manually with a `git diff` that includes `vendor/hlslparser`. `vendor/projectm-eval` is a nested submodule (patches 0004, 0020, 0034): diff it with `git -C third_party/projectm/vendor/projectm-eval diff --src-prefix=a/vendor/projectm-eval/ --dst-prefix=b/vendor/projectm-eval/` and stage it with `git -C third_party/projectm/vendor/projectm-eval add -A`. Its `Scanner.c`/`Compiler.c` are pre-generated (the build disables flex/bison); for a `Scanner.l` change commit only the delta between two runs of the same flex (`flex --noline --prefix=prjm_eval_ --header-file=Scanner.h -o Scanner.c Scanner.l` before and after), because Apple's flex 2.6.4 skeleton differs from the committed one (patch 0034). Patch numbers are taken in merge order: check `main` for new patches before numbering yours. For several new patches at once, a local-only branch in the submodule with one commit per patch (series, then each new patch) lets `git diff <commit> <commit>` regenerate any of them; never stage `third_party/projectm` in the superproject, and reset the submodule to the pinned commit afterwards. After pulling patch changes, reset the submodule (`git submodule foreach --recursive git checkout -- .`). Shader changes must link as GLSL ES 3.00 (`glslangValidator -l` with `#version 300 es` prepended; PR template).
- **Preset equation loading (patches 0029, 0033–0035):** code the evaluator rejects is compiled once more in MilkDrop's form (numbered records joined, `//`/`\\` comments removed, NS-EEL's stray `;` in parentheses read as a space); a lone `.` is the number 0; a block that still does not compile is left out like MilkDrop's `CState::RecompileExpressions` (q/t variables zero after a failed init) and reported through `projectm_set_preset_initialization_warning_event_callback`, which `native-lib.cpp` logs as `Preset code left out (<preset>): <reason> (line N, column M)`. Only parse errors fail a load. Keep accepted programs on the unchanged path.
- **Random textures (0037):** image selection belongs to slots 00–15 in a preset and is reused across warp/composite and shader reloads. Rebuild the descriptor for each exact alias and requested mode. Within a shader, filtered `randNN_prefix` aliases choose an empty slot before unfiltered aliases; competing prefixes keep lexical precedence. Across stages, the already selected slot wins. `sampler_state` fields remain ignored (0032); name prefixes select mode. Default user-texture mode is linear/wrap. Bind emitted short aliases to the same unit as their full alias and deduplicate declaration lines. Preserve `Texture::SourcePath()` and base names for diagnostics; generated textures have no source path. Production uses `std::random_device` for each new texture choice; a host seed does not establish Android/AAR association.
- **Blur framebuffer ownership (0041):** capture both caller read/draw framebuffer bindings before allocating or resizing blur textures. `Framebuffer::SetSize` unbinds both targets; saving after allocation sends later shapes/waves/borders to framebuffer zero when warp shaders sample blur. The native runner checks first use, unchanged size, resize, scaled blur, constant-color output and the unchanged midgit preset with isolated TGA assets. The same ownership control is verified on AM6/Mali-G52; Android framebuffer zero can be valid and hide the host error, so assert binding identity as well as checking GL errors (evidence: `docs/superpowers/evidence/midgit-framebuffer/`).
- **Predictive collection identity:** `tools/milk-analyzer/beta_export.py --check --bundle core/src/main/assets/preset-genres` validates the beta schema2 source/texture/weight inventory, frozen scoring code/model, standard published-AAR identity, raw activity formula, relative ranks and exact overlapping group membership. The numerical profile is capped2.3.3 at128×72, not a certificate of Native/TV fidelity. A changed renderer needs a separately identified run; historical schema1 Preset Lab imports do not produce the current bundle.
- **Presets and textures:** CI rejects presets that cannot react to audio or use excluded or missing textures (`tools/check-presets.py`) and a stale `presets.idx` (`tools/gen-preset-index.py --check`). Preset Lab CI rejects tracked audio/raw capture files under `tools/preset-lab` and `core/src/main/assets/preset-genres`.
- **Licensing and attribution:** app code LGPL-2.1 (`LICENSE`); presets and textures CC0 1.0 (`LICENSES/CC0-1.0.txt`). Record new third-party content and new patches in [docs/THIRD_PARTY.md](docs/THIRD_PARTY.md); keep upstream attribution in patch headers and release notes.
- **Privacy claims:** README states no network access except opt-in auto-update to GitHub, and in-memory audio analysis only. New network use or data storage contradicts published documentation and must update it.
- **Worktrees:** never remove another task's worktree. Follow the mandatory workflow below for cleanup of this task's clean, pushed and merged worktree; it is authorized as part of implementation. For this research checkpoint the user has authorized removal of `.worktrees/native-feedback-recovery` only after the main merge, all intended work is pushed, its tracked state is clean, task-owned jobs are stopped and external evidence archives are hash-verified. This exception does not authorize removing any other worktree or its data.
- **Native trails/fallback:**0042 owns authored feedback/resources per preset; Standard skips native warp, Medium/High use centered headroom-limited detail. Preserve per-frame RNG reuse, native viewport restoration after canvas init, UV-map invalidation on resizing/mode changes, authored blur timing and authored geometry recurrence. Patch0043 reuses evaluated shape/wave geometry for native presentation and alternates the existing canvas buffers; do not rerun persistent equations or RNG for the native draw. Shader/canvas failures retain0038 and diagnostics. The new Android core defaults Standard, while the projectM C API remains off by default for compatibility tests. Historical dual-AAR/capped evidence does not validate new automatic quality. Use the owner-approved17 known-preset focused matrix against source/released2.3.3, rather than claiming whole-corpus coverage. Record source/PCM/clock/seed/capture identities and quantify brightness/structure; chaotic and near-black cases need visual review.
- **Device ownership for native-trails-validation-fixes:** use only this task's `emulator-5602` (AVD/logs in ignored `build/native-trails-investigation/`), or the user-authorized AM9 `192.168.51.53:5555` and AM6 `192.168.50.80:5555`. AM9 runs64-bit Android14/Mali-G310; AM6 runs32-bit Android9. Build matched validation roles with `--abi armeabi-v7a` for AM6. Do not operate other tasks' emulators. Always pass an explicit `adb -s SERIAL` and captured Android user. Never wake a TV remotely; stop testing when it sleeps.
- **Do not commit:** `local.properties`, keystores, APK/AAR outputs, `build/`, raw diagnostics (see `.gitignore`).

## Formatting and linting

Follow the repository's configured formatting and lint rules. Review automatic formatting changes and avoid unrelated churn. Fix violations rather than disabling checks to obtain a passing result.

- No project-wide source formatter or linter is configured: no `.editorconfig`, `.clang-format`, ktlint/detekt, `lint.xml`, pre-commit or Python lint configuration outside `third_party/`. CI does not run Android Lint. Match the surrounding style (Java: 4-space indent).
- Validate workflow changes with `actionlint`. Older local versions reject GitHub's documented `queue: max` and `cache-mode: none`; use narrow ignores for those two schema fields only if necessary, and do not suppress other errors. Also run `git diff --check`.
- The JNI library compiles with `-Wall -Wextra -Wno-unused-parameter`; do not add warnings.
- Checks that act as lint in CI: `release_notes.py validate` (PR body), `tools/gen-preset-index.py --check`, `tools/check-presets.py`, `mkdocs build --strict` (user guide). `tools/check-patch-series.sh` is not in CI; CI applies the series through CMake during the native tests and `assembleRelease`.

## Building and testing

Choose validation that exercises the changed behavior. Compilation alone does not establish functional correctness. For UI or integration changes, exercise relevant user journeys and error paths when the environment supports them. Record baseline failures and environmental limitations honestly.

For release tooling changes, the required check is:

```bash
python3 -m unittest discover -s .github/scripts/tests -v
```

**Prerequisites** (from `app/build.gradle`, `core/build.gradle`, wrapper and CI): JDK 21 (CI Temurin 21, matching F-Droid; sources compile as Java 1.8), Gradle wrapper 8.14.2, AGP 8.12.0, Android SDK platform 34, NDK `27.3.13750724`, CMake `3.22.1` (CI installs the last three with `sdkmanager`), `local.properties` with `sdk.dir` (git-ignored; CI writes it), initialized submodules. CI runs on `ubuntu-24.04`.

| Command | Covers | Status |
|---|---|---|
| `git submodule update --init --recursive` | setup | Verified |
| `tools/check-patch-series.sh` | full series applies to a clean export of the submodule's `HEAD` (so the submodule must be at the pinned commit) | Verified: "all 29 patches apply" on `main`; the 32-patch series was verified with the same steps against `e0b0a967`; "all 35 patches apply" on 2026-10-04 with 0033–0035; 37 patches verified after integrating the parser fix for the random-binding task; all 41 patches verified on 2026-10-05; all 44 patches verified on 2026-10-06 for the float-literal fix |
| `tools/projectm-host-tests.sh [--gtest_filter=…]` | patched projectM GTest suite (build in `build/projectm-host`); needs CMake, Ninja, C++ compiler, Homebrew googletest | Verified on macOS: 179/179 on `main`, 204/204 with 0030–0032, 222/222 with 0001–0035 (configured with `-DCMAKE_DISABLE_FIND_PACKAGE_FLEX=ON -DCMAKE_DISABLE_FIND_PACKAGE_BISON=ON` to match the Android build's pre-generated parser) |
| `python3 -m unittest discover -s .github/scripts/tests -v` | release tooling | Verified: 74 tests OK (Python 3.13.12) |
| `python3 -m unittest discover -s tools -p test_tv_diagnostics.py -v` | diagnostics package/APK-source options; user-scoped cold start, process filtering, fail-safe queries and signing-conflict recovery; isolated fake adb, no TV/build/network | Run by Android CI; see task validation for the current revision |
| `core/src/test/native/run_native_tests.sh` | engine tests, GL fade overlay, patched-projectM regressions (ASan/UBSan); needs a C++17 compiler, JDK (`jni.h`), CMake, EGL/GLES dev libs on Linux (macOS uses OpenGL) | Verified on macOS 2026-10-04 (JDK 21): engine tests and projectm-regressions pass; GL fade overlay skipped without EGL/GLES; CI runs all on Linux |
| `./gradlew testReleaseUnitTest` (CI) / `./gradlew testDebugUnitTest` (PR template) | app and core JVM tests | Verified 2026-10-04: `testReleaseUnitTest` BUILD SUCCESSFUL |
| `./gradlew assembleRelease` / `./gradlew :core:assembleDebug` / `./gradlew assembleProfile` | APK + AAR; patch application through CMake; profile build | CI runs `assembleRelease`; verified 2026-10-04: `:app:assembleProfile :core:assembleRelease`, and `:core:assembleDebug` from a fresh recursive clone (CMake applied the series); a new worktree needs `local.properties` copied from the primary checkout |
| `tools/gen-preset-index.py --check`, `tools/check-presets.py` | asset checks | CI; not validated in this pass |
| `python -m pytest tools/preset-lab/tests` (`-m native` needs the native worker; see `tools/preset-lab/README.md`) | Preset Lab | CI (Preset Lab workflow); not validated in this pass |
| `mkdocs build --strict` (after `pip install -r docs/site-requirements.txt`) | user guide | CI (User guide workflow); verified 2026-10-04, no warnings |
| `./gradlew -PpresetLabDeviceTest :app:assembleDebug :app:assembleDebugAndroidTest`, then `adb -s DEVICE shell am instrument -r -w -e live_audio true nl.neerdael.projectmtv.presettest.test/com.example.projectm.visualizer.MusicCategoryInstrumentation` | music-category behavior on a TV ([development guide](docs/user-guide/development.md)) | needs a TV; not validated in this pass |

**What to run when:**

- JNI, `native-lib.cpp`, transitions, skip list: native tests, JVM tests, a build, and a TV check for rendering/audio/frame rate.
- Random-binding changes: real-GL `random-texture-*` controls in `core/src/test/native/projectm-regressions/` inspect units/samplers and compare known TGA bytes. The optional `random-texture-regressions presets <new-fixture-dir>` diagnostic records exact bundled asset identities and full-load/render results separately; full JPEG decoding exposes pre-existing SOIL2 UBSan warnings. See the random-binding evidence for unverified appearance/device limits.
- projectM patches: `check-patch-series.sh`, `projectm-host-tests.sh`, native tests, `:core:assembleDebug` log, TV before/after; complete the PR template's *projectM patches* checklist. Shader translation changes: the native runner includes float32 round-trip/locale/nonfinite controls (`float-literal-regressions`), a one-frame warp/composite RGB control (`float-literal-render`), 95 unchanged hashed shader sections (`float-literal-presets`), and `shader-parser-regressions`, `shader-render-regressions` and `parser-presets` (16 original files pinned by `parser-presets.tsv` hashes); also run `PresetShaderTranslationTest` (generated GLSL plus composite shaders rendered through the engine on macOS CGL; render cases skip without a GL context) and, where useful, translating the bundled presets' shaders before and after and compiling both with `glslangValidator` as GLSL ES 3.00.
- Presets/textures: `check-presets.py`, regenerate `presets.idx`, consider the genre bundle.
- UI, settings, remote keys: JVM tests plus a D-pad journey on a TV (open panel, sub-panels, Back/Menu, auto-hide); refresh setup screenshots with `-PsetupScreenshotTest` when visuals change.
- Audio and track titles: a TV with a verified music app (Spotify, SoundCloud, SmartTube, Milkbeat); include pause/resume.
- Public core API: build `:core:assembleRelease` and build Milkbeat against the new Native core (`-PprojectmCoreRepo=<dir> -PprojectmCoreVersion=<version>`, see [docs/RELEASING.md](docs/RELEASING.md)); not validated in this pass.
- After TV work: clear `debug.projectmtv.*` properties and restore app settings.

## Generated artifacts and release preparation

Feature pushes and PRs targeting other branches do not start builds. Ready PRs targeting main need a completed latest-commit Codex or qualified non-author human review, no outstanding review requests, observable pending reviews or changes requested, and no unresolved threads (including outdated ones). Preserve trusted-main execution of the review controller and status reporter: never check out PR code in a write-token job, pass publishing/signing secrets to PR code, or let PR code write main caches. Private draft reviews are visible only to their author and cannot be detected here; require an outstanding review request to represent planned unfinished reviews. Require exact 40-character SHA equality for latest-commit review evidence; never qualify from an abbreviated Codex summary or legacy comment, or use it to satisfy an outstanding request. Submitted Codex code/security review bodies plus full API `commit_id` values provide SHA evidence; empty review records from bot replies do not count. Track Codex request commands by the latest comment update time, falling back to creation time only when no update timestamp is available. Only current-head completions strictly later than the request at whole-second precision fulfill explicit Codex commands, including retained commands after a push. Automatically rerun successful validation invalidated by review eligibility, a preflight error with no builds started, or a final reporter API error after successful builds, once eligibility recovers; actual build failures require an explicit retry. Read the live main ref and verify the immutable test merge parents; recheck head/base/review before reporting success. Require `Reviewed PR builds` from GitHub Actions in the main ruleset, with up-to-date-branch and thread-resolution enforcement. GitHub's approving-review count remains zero because a completed Codex review is allowed; the custom status enforces the one-review minimum. See `docs/RELEASING.md` for exact completion signals, scheduled rechecks, unstructured-feedback limits and manual retry.

A successful tested merge to `main` triggers the versioned APK/single Native core AAR release and Milkbeat update through the canonical alias. Routine PRs must not manually bump the base version/code/commit. Follow `docs/RELEASING.md` for a planned new release line.

| Workflow (file) | Trigger | What it does |
|---|---|---|
| Android CI/CD (`android.yml`) | main push or main manual run | Calls Android build, Preset Lab and User guide; publishes only after the full suite passes, updates Milkbeat and deploys Pages. Main runs queue without cancellation |
| Android build (`android-build.yml`) | reusable call only | Native/tooling/assets and JVM tests; Native APK/AAR/mapping artifacts (30 days). Main receives signing secrets; PR calls receive none and disable Gradle cache access |
| PR review gate (`review-gate.yml`) | PR/comment/main-push events, trusted workflow_run relay from an unprivileged review signal, five-minute schedule, validation completion, manual | Trusted-main controller checks current Codex or qualified human review, outstanding review requests/changes and every thread; dispatches eligible PR validation and cancels obsolete runs. Schedules may be delayed by GitHub |
| PR review signal (`review-signal.yml`) | submitted/edited/dismissed review events | Unprivileged relay with no checkout; default-branch controller follows its completion |
| Reviewed PR validation (`pr-builds.yml`) | controller/manual dispatch on main | Preflight validates immutable head/base/test-merge SHAs; runs all Android, Preset Lab and guide builds without secrets; required `Reviewed PR builds` status passes only after actual success and a final eligibility/revision check |
| PR release notes (`release-notes.yml`) | PR opened, synchronized, reopened, edited, ready for review | `release_notes.py validate` on the PR body |
| User guide build (`docs-build.yml`) | reusable call from main, reviewed PRs or the manual guide workflow | Read-only `mkdocs build --strict` and Pages artifact; no publishing token |
| User guide (`docs.yml`) | manual run on main | Calls guide build and the shared Pages deployer; other branches skip |
| Publish user guide (`pages-deploy.yml`) | reusable call from main Android or manual User guide | Shared `projectm-tv-pages` queue with no cancellation; publish only if caller SHA still equals current main; API failure stops publication |
| Preset Lab (`preset-lab.yml`) | reusable call from main/eligible PR validation, or main manual run | Native/source-analysis tests under xvfb; rejects tracked audio/raw captures |

- **Versioning (`.github/scripts/release_version.py`):** publishing happens only for `refs/heads/main` on `push` or `workflow_dispatch`. Version = `baseVersionName` patch + (first-parent ordinal since `baseVersionCommit` − 1); the code advances in step from `baseVersionCode`. Other builds get a `-ci.<run>` suffix and file names `…-ci.<run>-<sha>.apk/.aar`. The user-planned Native minor release line sets the base triple to 2.3.0 / code 49 / `8b70620339018cfaf5ac05acdb4ea8104dc2eb59`; this deliberate line change is the documented exception to routine no-bump rules. Publication remains contingent on successful main CI.
- **Signing secrets (names only):** `SIGNING_KEYSTORE_BASE64`, `SIGNING_STORE_PASSWORD`, `SIGNING_KEY_ALIAS`, `SIGNING_KEY_PASSWORD`. A publishing build without the keystore fails; PR artifacts use a temporary debug key.
- **Publication:** GitHub Release `v<version>` with `projectM-TV-<version>.apk`, `projectM-TV-core-<version>.aar` (Native), stable-named `projectM-TV.apk` / `projectM-TV-core.aar`, `projectM-TV-<version>-mapping.txt` and `checksums.txt`. Notes come from merged PRs' `## Release notes` sections plus a CI footer.
- **Downloader code:** read by `release_notes.py` from the README blockquote `` > **Install on your TV with the Downloader app: code `4821216`** `` (exact regex; changing its format breaks release-note generation). The code is an AFTVnews short link to `releases/latest/download/projectM-TV.apk`; who manages the short link is not recorded in the repository.
- **Milkbeat:** `publish_release.py milkbeat` (token secret `MILKBEAT_TOKEN`) sends `repository_dispatch` `projectm-core-release` with the version to `johnneerdael/Milkbeat`, unless Milkbeat's latest release already names this core version or newer.
- **Committed generated files:** `core/src/main/assets/presets.idx`, `core/src/main/assets/preset-genres/`. Not committed: APKs, AARs, `build/`, raw diagnostics. `RELEASE_NOTES.md` is a manual archive (last entry 2.1.5) and is not used by CI.

## Documentation map

| Source | Role |
|---|---|
| `README.md` | Product overview, settings tables, permissions, install (canonical Downloader blockquote), troubleshooting, developer build/test |
| `docs/user-guide/*.md` + `mkdocs.yml` | User guide source, built by the User guide build reusable workflow and published through the shared main/manual Pages deployer to https://johnneerdael.github.io/ProjectM-TV/ (`docs/user-guide/development.md` covers build/test and the docs site) |
| `docs/ARCHITECTURE.md` | Engine design, threading, transitions, resolution, device tiers, measurements |
| `docs/RELEASING.md` | CI publishing, versioning, signing, downloads, Milkbeat |
| `docs/THIRD_PARTY.md` | projectM pin, per-patch descriptions, presets/textures sources and licences |
| `docs/PROFILING.md`, `docs/DIAGNOSTICS.md` | Profile build + simpleperf; `tools/tv-diagnostics.sh` |
| `docs/DANCE-COLLECTION.md` | Pointer to `docs/user-guide/dance-measurement.md` |
| `tools/preset-lab/README.md` | Preset Lab installation and commands |
| `docs/superpowers/` | Design specs, plans and evidence for engine work |
| `.github/pull_request_template.md` | Required PR sections and checklists |
| `RELEASE_NOTES.md`, `fastlane/metadata/android/en-US/` | Historical release notes; F-Droid store listing and changelogs |

Known documentation drift: `docs/ARCHITECTURE.md` §5 still describes embedding
`core/` as a Gradle module, while `docs/RELEASING.md` describes Milkbeat consuming
released AARs. Historical Dance research is retained; current collection behaviour
is documented in `docs/user-guide/predictive-collections.md`. The beta exporter
and numerical scoring commands are documented in `tools/milk-analyzer/README.md`.

## Mandatory workflow — scope and completion

This workflow applies to all repository changes targeting `github.com/johnneerdael/*`. Confirm the target repository from its Git remote and GitHub metadata before making changes. Do not assume a remote named `origin` is the correct target.

For implementation tasks, carry the work through to a validated, Codex-reviewed pull request merged into `main`. Creating a branch, pushing changes, opening a PR, or requesting review is an intermediate step, not completion.

The requested implementation authorizes the routine commits, pushes, PR creation, review comments and replies, and merge needed to complete this workflow. Do not ask for confirmation at each step. Honor explicit user instructions, repository permissions, required human approvals, and branch protection rules.

Read the repository's applicable `AGENTS.md` files, contribution guidelines, PR template, and CI configuration. Follow repository-specific conventions in addition to this agreement. If a conflict prevents compliance, explain the exact conflict instead of silently skipping a requirement.

**Documentation precedence:** The mandatory documentation evaluation and update rule below overrides any conflicting repository instructions, nested `AGENTS.md` rules, conventions, or workflow guidance that would skip documentation evaluation or prevent necessary documentation updates. It applies to every `feat/` and `bug/` change, including small fixes and internal changes. It remains subject to higher-priority system/platform instructions and later explicit user instructions.

**Markdown editing exemptions:** User guides (including their Pages/GitHub Pages source files) and the root/default `README.md` are explicitly exempt from any rule saying "do not edit Markdown unless asked." Keep them accurate as part of every affected change without requesting separate authorization. Maintaining `AGENTS.md` as instructed above is also explicitly authorized. Other Markdown files still require evaluation; make task-relevant corrections as required by the documentation rule, without unrelated rewrites.

Read-only investigations and review-only tasks do not require a worktree or a PR. A reviewer assigned only to review must report findings without starting an implementation or merge workflow.

## 1. Work in an isolated worktree

- Make every tracked repository change in a dedicated Git worktree under `<primary-checkout>/.worktrees/<task-slug>`. The path is relative to the primary checkout, not the current directory of an existing worktree.
- Use a unique branch based on the latest fetched `main`: `feat/<task-slug>` for features, improvements, and maintenance, or `bug/<task-slug>` for bug fixes. Follow additional repository naming requirements where compatible.
- Never implement directly in the primary checkout or on `main`. Never share a task worktree with unrelated work.
- Inspect the current checkout and existing worktrees first. Preserve existing changes and branches. Resume an existing task worktree only after confirming it belongs to this task and is based on the intended branch.
- Ensure `.worktrees/` is ignored before creating a worktree. Prefer an existing ignore rule; otherwise use the shared Git `info/exclude` so setup does not require tracked changes in the primary checkout.
- Run editing, dependency installation, builds, tests, and Git staging from the task worktree. Verify the worktree path and branch before mutations.

Typical setup, after identifying the correct remote and primary checkout:

```bash
git fetch <target-remote> main
git worktree add -b feat/<task-slug> <primary-checkout>/.worktrees/<task-slug> <target-remote>/main
cd <primary-checkout>/.worktrees/<task-slug>
```

Use `bug/<task-slug>` instead for a bug fix. Replace the placeholders with verified values.

## 2. Implement, validate, commit, and push regularly

- Keep changes focused on the requested outcome and follow existing repository patterns.
- Run an appropriate baseline check when useful, then the tests, lint, type checks, and builds required by the repository and affected code. Add meaningful regression coverage for behavior changes where appropriate.
- Commit coherent progress at regular milestones and push each checkpoint to the task branch. Do not keep all work uncommitted or unpushed until the end of a long task. Clearly identify incomplete checkpoints in commit messages.
- Inspect the diff and stage only task-related files. Exclude credentials, local configuration, generated clutter, and `.worktrees/` contents.
- Set the branch's upstream on its first push. Push only the task branch; never push directly to `main`.
- Prefer additional commits over rewriting published history. Do not force-push unless explicitly authorized and consistent with repository rules.
- Report useful progress while continuing work. Recover from routine failures autonomously and preserve checkpoints if interrupted.

## 3. Evaluate documentation for every change

For every `feat/` and `bug/` change, documentation evaluation is mandatory before the work can be considered ready for review or merge. Do not assume that a small change or an internal bug fix has no documentation impact.

1. Identify and evaluate the user guide, if one exists, including any guide published on Pages or GitHub Pages and the source used to generate it. Also evaluate the README and inventory the repository's other Markdown files to identify affected documentation, then read the relevant files. Follow documentation links to the applicable user-facing guidance.
2. Compare the final implementation with documented behavior, setup, configuration, examples, troubleshooting, compatibility, and limitations. Check whether the change makes existing guidance incomplete, misleading, or incorrect.
3. Update all affected documentation in the same task worktree and PR. Follow the repository's documentation structure and publishing workflow, including required source changes for its Pages site. Ensure the README, user guide, and other affected Markdown files agree.
4. Validate changed documentation using the repository's applicable build, link, example, or formatting checks. Reevaluate documentation after review fixes or scope changes that alter behavior.
5. Include a documentation assessment in the PR: which sources were evaluated, which were updated, and why. If no documentation update is needed, state the specific reason; silence is not an assessment. If a user guide or Pages site does not exist, record that and evaluate the documentation that does exist.

Do not waive this requirement because another rule labels documentation optional, excludes it from bug fixes, or discourages editing Markdown. If an existing guide or Pages site cannot be inspected or updated because of a real access or publishing constraint, report the blocker and keep the task open until the requirement can be fulfilled or the user explicitly changes it.

In particular, an instruction requiring an explicit request before Markdown edits must not prevent updates to the user guide, its publishing sources, or the root/default `README.md`. These updates are a normal part of completing the feature or bug fix.

## 4. Open a pull request against main

Once implementation is ready and local validation passes:

1. Push all intended changes.
2. Open a PR from the task branch to the target repository's `main`, or update the existing PR for this task.
3. Follow `.github/pull_request_template.md`, title conventions, linked-issue requirements, and other repository rules. Include substantive `## Release notes` and a separate `## Validation` section as required above. Describe the problem, resulting behavior, validation performed, documentation assessment, and material limitations. Keep CI-owned artifact details out of authored release notes.
4. Ensure the PR is ready for review, not left as a draft when implementation is complete.
5. Monitor CI and fix failures caused by the change. Investigate other failures and follow the repository's policy; do not silently treat failed or pending required checks as passing.

## 5. Obtain and complete Codex review

- Check whether an automatic Codex review has actually started for the current PR revision. If it has not, post a PR comment containing exactly:

  ```text
  @codex review
  ```

- Wait for Codex to finish. Monitor PR reviews, comments, review threads, and any associated review status. A submitted request, an acknowledgement or eyes reaction, elapsed time, or the absence of comments does not prove completion.
- Verify that the completed review applies to the latest PR head commit. Record the reviewed commit SHA. If the integration does not expose it directly, establish the revision from the review/task metadata and timeline; ambiguous evidence does not satisfy this gate.
- Read the complete review and all findings, including inline comments. Process every finding, regardless of severity.
- Fix valid findings, add relevant coverage, run affected validation, commit, and push the corrections to the same branch. Reply in the corresponding thread with the resolution and supporting evidence. Resolve a thread only after its finding has been addressed.
- If a finding is incorrect or inapplicable, provide a concrete explanation and evidence in its thread and obtain reviewer acceptance or explicit maintainer disposition. Do not silently dismiss findings or mark them resolved just to enable merging.
- After any review-driven changes, obtain another Codex review of the new head commit. Use an automatic review if it starts; otherwise post `@codex review` again. Repeat the fix, validate, push, and review loop as many times as needed.
- Avoid duplicate requests while a review of the same revision is running. For complex changes, allow additional focused review passes as useful; complexity never removes the final review requirement.
- Close the review cycle only when Codex has completed review of the final head commit, every finding has a documented disposition, all review threads are resolved, and no further changes are requested. Codex review completion does not replace any separately required GitHub approval.

If review cannot start or finish because of access, configuration, service failure, or quota, investigate available diagnostics and report the concrete blocker. Keep the PR open and preserve the branch. Never substitute self-review or a timeout for the required Codex review.

## 6. Merge the validated and reviewed change

Merge autonomously once all of these conditions hold:

- The requested work is complete and the final diff contains only intended changes.
- The user guide/Pages, README, and other Markdown documentation have been evaluated, necessary updates are included and validated, and the PR records the documentation assessment.
- Repository-specific guidance in `AGENTS.md` has been populated or maintained as required by the task, with unresolved facts identified honestly.
- Local validation and all required CI checks pass for the final revision.
- Codex review is complete for the current PR head commit, with all findings addressed and review threads resolved.
- All repository-required approvals and merge conditions are satisfied.
- PR release notes are factual and match the final diff; validation is recorded separately, and any required release-tooling tests pass. Routine changes have not manually bumped release versions.
- The PR targets `main`, is mergeable, and meets any requirements to be current with its base branch.

Refresh the PR state immediately before merging and verify that its head SHA still matches the validated and reviewed SHA. Use the repository's permitted merge method through GitHub. Do not bypass protections, use an administrative override, or merge an unreviewed revision.

If updating from `main` or resolving conflicts changes the PR head, push the update, rerun appropriate validation, and obtain Codex review of that new head before merging. Any further change reopens the validation and review gates.

If the repository requires a merge queue, enqueue the eligible PR and monitor until it actually merges. Continue responding to failures or new findings. Enabling auto-merge or entering a queue does not itself complete the task.

## 7. Confirm and close the work

- Verify on GitHub that the PR is merged into `main` and record the merge commit or squash commit SHA.
- Monitor the automatic APK/core AAR release and Milkbeat update workflow. Verify reported publication/update results before claiming success. If a job fails, investigate and address task-related failures through another isolated branch and reviewed PR where appropriate, or report the concrete release/update blocker. Do not manually bypass the release pipeline or push fixes directly to `main`.
- Preserve unrelated worktrees, branches and uncommitted changes. The user authorized removal only of this task's `.worktrees/native-feedback-recovery` after the merged/pushed/clean and verified-external-archive conditions in *Worktrees* are satisfied. Do not generalize that authorization to another task or force-remove unchecked tracked changes. Delete a branch only when repository policy and explicit user constraints permit.
- Report the outcome concisely: what changed, relevant validation, PR link, Codex review disposition, and merge confirmation.
- If a real blocker prevents completion, report the current branch, worktree, PR, completed checks, exact blocker, and next required action. Describe the task as blocked, not completed.

## Native trails follow-up validation notes (2026-10-05)

- Current0042 host253/253 andASan/UBSan253/253 pass;42patchesapply; scoped review fixes viewport and UV-map state errors. Direct authored-state test covers20 animated geometry-free frames; full preset fidelity remains separate. First-frame blur fixture can emit a macOS zero-texture warning; image/GL assertions pass.
- Automatic quality JVM suite42 tests passes (FPS/memory/migration/budget). Release tooling82 tests passes. Revalidate after final integration/review changes.
- Focused actual-AAR workers: `tools/native-trails/README.md`; no full-corpus claim. Released2.3.3 Native/capped AARs are local historical controls only. Native AAR Acid4K smoke480frames passed. Instrumented comparison, liveAM6, finalCI/Codex/merge/release remain required evidence, not established by these host results.
- Owner authorizes awake rootedAM6 at192.168.50.80 for live debug/profile in this task. Verify current Android user and media-session state3; never wake remotely; restore task properties/profile preferences. Initial link briefly connected then went offline before player/user queries.
