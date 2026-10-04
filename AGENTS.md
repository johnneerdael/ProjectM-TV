# ProjectM TV contributor instructions

## Pull requests and release notes

Each successfully tested merge to `main` publishes a versioned APK and core AAR, then updates Milkbeat. Use a feature branch and PR for changes.

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

Last full discovery: 2026-10-04, against `main` at `4fc66208` (projectM patch series 0001–0029). "Verified" below means the command was run with the stated result on that date; everything else is described from the source files and CI configuration.

## Repository overview

ProjectM TV is a music visualizer for Android TV. It renders [projectM](https://github.com/projectM-visualizer/projectm) (a MilkDrop reimplementation) presets that react to the audio another app plays on the same TV; it is not a music player. It bundles 9,606 *Cream of the Crop* presets. GitHub: `johnneerdael/ProjectM-TV` (verified with `gh repo view`; a checkout's `origin` URL may still use the former name `projectm-android-tv`, which redirects).

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
- **projectM relationship:** submodule `third_party/projectm` tracks upstream `https://github.com/projectM-visualizer/projectm.git`, pinned at tag `v4.1.7` (commit `e0b0a967`). All engine changes are the ordered patch series `tools/projectm-patches/NNNN-*.patch` (0001–0033; 0033 is the Native 4K feedback-diffusion compensation), applied at CMake configure time by `core/src/main/cpp/CMakeLists.txt` and linked statically into `libprojectmtv.so`. The personal fork `johnneerdael/projectm` is not referenced by the build; it is used for upstream PRs.
- **App/core boundary and Milkbeat:** `:app` holds UI, audio capture, track titles and the updater; `:core` holds the engine, JNI, presets, textures and preset indexes. [Milkbeat](https://github.com/johnneerdael/Milkbeat) consumes the released core AAR: CI publishes `projectM-TV-core-<version>.aar` and dispatches `projectm-core-release` to Milkbeat (see *Generated artifacts*). Milkbeat's own build and API usage live in its repository and were not inspected here.
- **Build tasks:** `./gradlew assembleRelease` (APK at `app/build/outputs/apk/release/app-release.apk` and AAR at `core/build/outputs/aar/core-release.aar`), `./gradlew :core:assembleRelease`, `./gradlew assembleDebug`, `./gradlew assembleProfile`.

## Codebase navigation and knowledge tools

- No `.codegraph/` or `graphify-out/` exists at the repository root (checked 2026-10-04). Use `git grep`/`rg`; do not assume a code graph.
- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) §5 (threading rules, transitions, resolution, frame pacing, threads, overlay UI, device tiers). Its title says v1.9 and §1–4 and §6–8 are historical analysis; verify against the code. Design specs, plans and evidence for engine work are in `docs/superpowers/{specs,plans,evidence}`.
- projectM sources: `third_party/projectm` shows patched code only after a CMake configure or a manual apply; the committed source of truth is `tools/projectm-patches/`. Search both the submodule and the patches.
- Logs for tracing behavior: native tag `projectM-Native` (`LOAD`, `PREWARM`, `TRANSITION`, `OUTPUT` lines per switch); `VisualizerRenderer` logs `STATS fps=… surface=… audio=…` every 5 s.
- Committed generated data indexes (not code indexes): `core/src/main/assets/presets.idx` (regenerate with `tools/gen-preset-index.py` whenever presets or textures change; CI enforces `--check`) and the genre bundle in `core/src/main/assets/preset-genres/` (produced by Preset Lab, imported with `tools/import-preset-genres.py`).

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
- **Frame pacing and quality:** default is half the refresh rate (`RENDERMODE_WHEN_DIRTY` + `Choreographer`); `QualityController` moves the render height on a ladder; Auto and numeric fixed heights are capped at 1330p (`QualityController.RENDER_HEIGHT_CAP`) and by installed RAM (`DeviceProfile.memorySafeHeight`); the explicit opt-in Native choice (`QualityController.NATIVE_HEIGHT = -1`) uses the detected panel height when it exceeds 1330p and the memory limit permits it, and does not lower itself for slow presets or memory pressure; legacy saved numeric 1440/2160 choices stay capped rather than becoming Native; `onTrimMemory` → `ProjectMJNI.onMemoryPressure`. Device tiers (HIGH/STANDARD/LOW) are in `DeviceProfile` and ARCHITECTURE §5.
- **No numeric frame-time or memory budget is defined.** Compare before/after on the same TV, preset, render height and audio (PR template).
- **Measurement tools:** profile build + simpleperf ([docs/PROFILING.md](docs/PROFILING.md)); pin a preset with `adb shell setprop debug.projectmtv.preset '<name prefix>'` and clear it afterwards (`debug.projectmtv.update_from` also exists); `tools/tv-diagnostics.sh <tv-ip>:5555 --sweep` ([docs/DIAGNOSTICS.md](docs/DIAGNOSTICS.md)); Preset Lab for offline rendering comparisons (desktop timings do not establish TV performance).
- **Documented device coverage:** NVIDIA SHIELD TV 2019 (`sif`, 2 GB, 32-bit) and SHIELD TV Pro 2019 (`mdarcy`, 3 GB), Android 11; Ugoos AM6 (Amlogic S922X, Mali-G52 MP6, Android 9). No emulator configuration is committed.
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
- **Wording conventions:** the product name is "ProjectM TV"; menu paths use `›` (e.g. *Settings › Advanced › Auto-update*). Keep setting names and values identical in the UI, the README settings tables and `docs/user-guide/settings.md`.
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
- **projectM patches:** never commit edits inside `third_party/projectm` (submodule has `ignore = dirty`). To write a patch: apply the existing series in `third_party/projectm` and stage it (`git -C third_party/projectm add -A`) so new edits show as a clean diff, then use `tools/regen-projectm-patch.sh <name>`. That script only diffs `src/` and `tests/`; patches touching `vendor/hlslparser` (0003, 0008, 0018, 0019, 0021, 0030, 0031) must be produced manually with a `git diff` that includes `vendor/hlslparser`. For several new patches at once, a local-only branch in the submodule with one commit per patch (series, then each new patch) lets `git diff <commit> <commit>` regenerate any of them; never stage `third_party/projectm` in the superproject, and reset the submodule to the pinned commit afterwards. After pulling patch changes, reset the submodule (`git submodule foreach --recursive git checkout -- .`). Shader changes must link as GLSL ES 3.00 (`glslangValidator -l` with `#version 300 es` prepended; PR template).
- **Patch identity in the Dance bundle:** `tools/import-preset-genres.py` refuses a bundle whose `app_patches_sha256` differs from the current patch series. Changing the series means a re-measured bundle is needed before the next import.
- **Presets and textures:** CI rejects presets that cannot react to audio or use excluded or missing textures (`tools/check-presets.py`) and a stale `presets.idx` (`tools/gen-preset-index.py --check`). Preset Lab CI rejects tracked audio/raw capture files under `tools/preset-lab` and `core/src/main/assets/preset-genres`.
- **Licensing and attribution:** app code LGPL-2.1 (`LICENSE`); presets and textures CC0 1.0 (`LICENSES/CC0-1.0.txt`). Record new third-party content and new patches in [docs/THIRD_PARTY.md](docs/THIRD_PARTY.md); keep upstream attribution in patch headers and release notes.
- **Privacy claims:** README states no network access except opt-in auto-update to GitHub, and in-memory audio analysis only. New network use or data storage contradicts published documentation and must update it.
- **Worktrees:** never remove any Git worktree unless the user explicitly asks, including after merge; other agents work in parallel worktrees.
- **Native 4K feedback diffusion (patch 0033):** an unaccepted feature under investigation, not evidence for raising the default 1330p cap. Above the line-reference area it filters only bilinear warp reads; point-sampled warp reads and the composite read an exact copy (see ARCHITECTURE *Feedback diffusion*). Actual-core evidence, protocols and artifact identities live in `docs/superpowers/evidence/0025-feedback-diffusion/` (start with `current-main-validation/README.md` and `mrt-fix-validation/README.md`) and the handover `docs/superpowers/handover/2026-10-04-native-4k-feedback-bugs.md`. Compare renderer changes with the same preset, audio, frame count, render size, clock/RNG and artifact identity; passing unit tests are not a fidelity verdict.
- **Native 4K device ownership:** targeted actual-core jobs own `emulator-5582` (launch metadata in the recovery worktree's `build/native-4k-current-main/emulator/launch.json`); the corpus owner controls `emulator-5580`, its processes and `.worktrees/quad-lines-follow-ups` — do not restart, kill, install into or reconfigure them. Physical TVs need the user's authorization for the task (the AM9 at `192.168.51.53` and the Ugoos AM6 at `192.168.50.80` have been authorized); **never wake a TV remotely**, and stop when it sleeps. Always pass an explicit `adb -s <serial>`; several devices are attached.
- **Do not commit:** `local.properties`, keystores, APK/AAR outputs, `build/`, raw diagnostics (see `.gitignore`).

## Formatting and linting

Follow the repository's configured formatting and lint rules. Review automatic formatting changes and avoid unrelated churn. Fix violations rather than disabling checks to obtain a passing result.

- No formatter or linter is configured: no `.editorconfig`, `.clang-format`, ktlint/detekt, `lint.xml`, pre-commit or Python lint configuration outside `third_party/`. CI does not run Android Lint. Match the surrounding style (Java: 4-space indent).
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
| `tools/check-patch-series.sh` | full series applies to a clean export of the submodule's `HEAD` (so the submodule must be at the pinned commit) | Verified: "all 29 patches apply" on `main`; the 32-patch series was verified with the same steps against `e0b0a967` |
| `tools/projectm-host-tests.sh [--gtest_filter=…]` | patched projectM GTest suite (build in `build/projectm-host`); needs CMake, Ninja, C++ compiler, Homebrew googletest | Verified on macOS: 179/179 on `main`, 204/204 with 0030–0032 |
| `python3 -m unittest discover -s .github/scripts/tests -v` | release tooling | Verified: 74 tests OK (Python 3.13.12) |
| `core/src/test/native/run_native_tests.sh` | engine tests, GL fade overlay, patched-projectM regressions (ASan/UBSan); needs a C++17 compiler, JDK (`jni.h`), CMake, EGL/GLES dev libs on Linux (macOS uses OpenGL) | CI; not validated in this pass |
| `./gradlew testReleaseUnitTest` (CI) / `./gradlew testDebugUnitTest` (PR template) | app and core JVM tests | not validated in this pass |
| `./gradlew assembleRelease` / `./gradlew :core:assembleDebug` / `./gradlew assembleProfile` | APK + AAR; patch application through CMake; profile build | CI runs `assembleRelease`; not validated in this pass |
| `tools/gen-preset-index.py --check`, `tools/check-presets.py` | asset checks | CI; not validated in this pass |
| `python -m pytest tools/preset-lab/tests` (`-m native` needs the native worker; see `tools/preset-lab/README.md`) | Preset Lab | CI (Preset Lab workflow); not validated in this pass |
| `mkdocs build --strict` (after `pip install -r docs/site-requirements.txt`) | user guide | CI (User guide workflow); not validated in this pass |
| `./gradlew -PpresetLabDeviceTest :app:assembleDebug :app:assembleDebugAndroidTest`, then `adb -s DEVICE shell am instrument -r -w -e live_audio true nl.neerdael.projectmtv.presettest.test/com.example.projectm.visualizer.MusicCategoryInstrumentation` | music-category behavior on a TV ([development guide](docs/user-guide/development.md)) | needs a TV; not validated in this pass |

**What to run when:**

- JNI, `native-lib.cpp`, transitions, skip list: native tests, JVM tests, a build, and a TV check for rendering/audio/frame rate.
- projectM patches: `check-patch-series.sh`, `projectm-host-tests.sh`, native tests, `:core:assembleDebug` log, TV before/after; complete the PR template's *projectM patches* checklist. Shader translation changes: `PresetShaderTranslationTest` (generated GLSL plus composite shaders rendered through the engine on macOS CGL; render cases skip without a GL context) and, where useful, translating the bundled presets' shaders before and after and compiling both with `glslangValidator` as GLSL ES 3.00.
- Presets/textures: `check-presets.py`, regenerate `presets.idx`, consider the genre bundle.
- UI, settings, remote keys: JVM tests plus a D-pad journey on a TV (open panel, sub-panels, Back/Menu, auto-hide); refresh setup screenshots with `-PsetupScreenshotTest` when visuals change.
- Audio and track titles: a TV with a verified music app (Spotify, SoundCloud, SmartTube, Milkbeat); include pause/resume.
- Public core API: build `:core:assembleRelease` and build Milkbeat against it (`-PprojectmCoreRepo=<dir> -PprojectmCoreVersion=<version>`, see [docs/RELEASING.md](docs/RELEASING.md)); not validated in this pass.
- After TV work: clear `debug.projectmtv.*` properties and restore app settings.

## Generated artifacts and release preparation

A successful tested merge to `main` triggers the versioned APK/core AAR release and Milkbeat update. Routine PRs must not manually bump the base version/code/commit. Follow `docs/RELEASING.md` for a planned new release line.

| Workflow (file) | Trigger | What it does |
|---|---|---|
| Android CI/CD (`android.yml`) | push to any branch, pull request, manual | `native-tests`: release-tooling tests, preset index/preset checks, Mesa, `run_native_tests.sh`. `apk`: `release_version.py`, signing, `testReleaseUnitTest`, `assembleRelease`; artifacts `apk`, `core-aar`, `mapping` (30 days). `release` (only when publishing): `release_notes.py generate`, `publish_release.py publish`. `milkbeat`: `publish_release.py milkbeat`. Runs queue; none is cancelled |
| PR release notes (`release-notes.yml`) | PR opened, synchronized, reopened, edited, ready for review | `release_notes.py validate` on the PR body |
| User guide (`docs.yml`) | PR or `main` push touching `docs/user-guide/**`, `docs/site-requirements.txt`, `mkdocs.yml`, the workflow; manual | `mkdocs build --strict`; deploys to GitHub Pages from `main` |
| Preset Lab (`preset-lab.yml`) | every push and PR; manual | Preset Lab tests incl. native rendering under xvfb; rejects tracked audio/raw captures |

- **Versioning (`.github/scripts/release_version.py`):** publishing happens only for `refs/heads/main` on `push` or `workflow_dispatch`. Version = `baseVersionName` patch + (first-parent ordinal since `baseVersionCommit` − 1); the code advances in step from `baseVersionCode`. Other builds get a `-ci.<run>` suffix and file names `…-ci.<run>-<sha>.apk/.aar`. Base values today: 2.2.0 / 38 / `da4fe0ed`; the latest tag is `v2.2.6`.
- **Signing secrets (names only):** `SIGNING_KEYSTORE_BASE64`, `SIGNING_STORE_PASSWORD`, `SIGNING_KEY_ALIAS`, `SIGNING_KEY_PASSWORD`. A publishing build without the keystore fails; PR artifacts use a temporary debug key.
- **Publication:** GitHub Release `v<version>` with `projectM-TV-<version>.apk`, `projectM-TV-core-<version>.aar`, stable-named `projectM-TV.apk` / `projectM-TV-core.aar`, `projectM-TV-<version>-mapping.txt` and `checksums.txt`. Notes come from merged PRs' `## Release notes` sections plus a CI footer.
- **Downloader code:** read by `release_notes.py` from the README blockquote `` > **Install on your TV with the Downloader app: code `4821216`** `` (exact regex; changing its format breaks release-note generation). The code is an AFTVnews short link to `releases/latest/download/projectM-TV.apk`; who manages the short link is not recorded in the repository.
- **Milkbeat:** `publish_release.py milkbeat` (token secret `MILKBEAT_TOKEN`) sends `repository_dispatch` `projectm-core-release` with the version to `johnneerdael/Milkbeat`, unless Milkbeat's latest release already names this core version or newer.
- **Committed generated files:** `core/src/main/assets/presets.idx`, `core/src/main/assets/preset-genres/`. Not committed: APKs, AARs, `build/`, raw diagnostics. `RELEASE_NOTES.md` is a manual archive (last entry 2.1.5) and is not used by CI.

## Documentation map

| Source | Role |
|---|---|
| `README.md` | Product overview, settings tables, permissions, install (canonical Downloader blockquote), troubleshooting, developer build/test |
| `docs/user-guide/*.md` + `mkdocs.yml` | User guide source, published by the User guide workflow to https://johnneerdael.github.io/ProjectM-TV/ (`docs/user-guide/development.md` covers build/test and the docs site) |
| `docs/ARCHITECTURE.md` | Engine design, threading, transitions, resolution, device tiers, measurements |
| `docs/RELEASING.md` | CI publishing, versioning, signing, downloads, Milkbeat |
| `docs/THIRD_PARTY.md` | projectM pin, per-patch descriptions, presets/textures sources and licences |
| `docs/PROFILING.md`, `docs/DIAGNOSTICS.md` | Profile build + simpleperf; `tools/tv-diagnostics.sh` |
| `docs/DANCE-COLLECTION.md` | Pointer to `docs/user-guide/dance-measurement.md` |
| `tools/preset-lab/README.md` | Preset Lab installation and commands |
| `docs/superpowers/` | Design specs, plans and evidence for engine work |
| `.github/pull_request_template.md` | Required PR sections and checklists |
| `RELEASE_NOTES.md`, `fastlane/metadata/android/en-US/` | Historical release notes; F-Droid store listing and changelogs |

Known documentation drift (2026-10-04, not yet fixed): README says it describes the app "as of version 2.1.5" while releases reach v2.2.6; `docs/ARCHITECTURE.md` §5 describes embedding `core/` as a Gradle module, while `docs/RELEASING.md` describes Milkbeat consuming the released AAR; the committed Dance bundle's `app_patches_sha256` does not match the current patch series (computed with Preset Lab's digest function, not by running the import check).

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
- Preserve every worktree after merge. The user's explicit rule forbids removing any Git worktree unless asked; merge completion is not removal authorization. Delete a branch only when repository policy and explicit user constraints permit. Preserve unrelated branches and uncommitted changes.
- Report the outcome concisely: what changed, relevant validation, PR link, Codex review disposition, and merge confirmation.
- If a real blocker prevents completion, report the current branch, worktree, PR, completed checks, exact blocker, and next required action. Describe the task as blocked, not completed.
