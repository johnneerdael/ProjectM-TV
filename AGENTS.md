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

## Maintain this file

Keep the repository-specific sections below accurate. Update them in the same worktree and PR whenever a task changes architecture, commands, dependencies, documentation, or constraints, and repeat discovery when relevant context is missing or stale. Record only facts verified from repository files, official documentation, or observed command results; mark anything else as unverified. Keep entries concise and link to docs for detail. Maintaining this file is part of the task and needs no separate request; changes to it go through the same validation, PR, and Codex review as any other change.

## Repository overview

ProjectM TV produces an Android APK and a core AAR consumed by Milkbeat through the automatic release/update workflow described above.

- **Purpose:** music visualizer for Android TV built on [projectM](https://github.com/projectM-visualizer/projectm) (open-source MilkDrop) with 9,606 bundled *Cream of the Crop* presets. It visualizes audio another app plays; it is not a player. Leanback launcher, landscape only, requires OpenGL ES 3.0 (`app/src/main/AndroidManifest.xml`).
- **Repository:** `johnneerdael/ProjectM-TV`, default branch `main`. The local `origin` URL may still use the old name `johnneerdael/projectm-android-tv`; `gh repo view` resolves it to `johnneerdael/ProjectM-TV`.
- **Modules** (`settings.gradle`): `:app` (application) and `:core` (Android library, the engine).
- **Identifiers:** application ID `nl.neerdael.projectmtv`; app namespace and Java package `com.example.projectm.visualizer` (unchanged when 1.9.7 changed the app ID); core namespace and package `nl.neerdael.projectm.core`; native library `libprojectmtv.so`.
- **Toolchain:** compileSdk/targetSdk 34, minSdk 21, Java 1.8 source/target, NDK `27.3.13750724`, CMake 3.22.1, AGP 8.12.0, Gradle wrapper 8.14.2, JDK 21 in CI. ABIs: `armeabi-v7a`, `arm64-v8a` (`core/build.gradle`).
- **Languages:** Java using framework APIs only (no AndroidX, for APK size and cold start on low-end boxes); C++17 engine in `core/src/main/cpp/` (`native-lib.cpp`, `snapshot_fade.cpp`, `preset_prewarm.cpp`) bound through the JNI class `ProjectMJNI`.
- **projectM:** submodule `third_party/projectm` at tag `v4.1.7` (commit `e0b0a967`) with nested submodule `vendor/projectm-eval`, plus the patch series in `tools/projectm-patches/` (32 patches), applied by `core/src/main/cpp/CMakeLists.txt` at configure time and linked statically. Each patch's purpose and upstream source: `docs/THIRD_PARTY.md`.
- **Build types** (`app/build.gradle`, no product flavors): `debug`; `release` (R8 minify and resource shrinking; release key when `SIGNING_KEYSTORE_PATH` is set, else the debug key); `profile` (release code, debug-signed, ID suffix `.profile`, profileable via `app/src/profile/AndroidManifest.xml`). `debug` with `-PpresetLabDeviceTest` becomes `.presettest`, with `-PsetupScreenshotTest` `.setuptest` (no documented workflow for setuptest).
- **Entry points:** `ProjectMApplication` (calls `ProjectMCore.init`), `MainActivity` (launcher, overlay UI, remote keys, audio), `TrackListenerService` (notification listener for track info), `Updater` and `UpdateFileProvider` (opt-in auto-update, the only network code).
- **App/core boundary:** `:core` holds the native engine, projectM build, preset/texture/index assets, `ProjectMJNI`, `ProjectMCore`, `VisualizerView`, `VisualizerRenderer`, `QualityController`, `DeviceProfile` and `DisplayInfo`. `:app` holds UI, audio capture (`PlayerSessionFinder`), track titles and the updater.
- **Milkbeat:** CI attaches `projectM-TV-core-<version>.aar` (and `projectM-TV-core.aar`) to each release, then `.github/scripts/publish_release.py milkbeat` sends a `projectm-core-release` repository dispatch to `johnneerdael/Milkbeat` with the version, unless Milkbeat's latest release already names it. `docs/ARCHITECTURE.md` §5 also describes embedding `core/` as a Gradle module. Milkbeat's own build is not verified from this repository.

## Codebase navigation and knowledge tools

- No `.codegraph/` or `graphify-out/` exists in this repository (checked 2026-10-04), and no generated code index is committed. Use ordinary code search (`git grep`, `rg`); exclude `third_party/` and `core/src/main/assets/presets/` (about 9.6k files).
- Architecture reference: `docs/ARCHITECTURE.md` (threading rules, render pipeline, transitions, resolution, device tiers, audio source, auto-update).
- Largest files: `core/src/main/cpp/native-lib.cpp` (about 2,000 lines) and `MainActivity.java` (about 1,200 lines).
- Committed generated data: `core/src/main/assets/presets.idx` (regenerate with `tools/gen-preset-index.py` after adding or removing presets; CI runs `--check`) and `core/src/main/assets/preset-genres/` (imported or verified by `tools/import-preset-genres.py` from a Preset Lab bundle).

## Design and user experience

Follow the project's established design system and platform conventions. Reuse existing theme tokens and components. Preserve accessibility, keyboard/focus behavior, responsiveness, and supported input methods. Avoid introducing decorative styles or changing appearance incidentally during a refactor.

- **Toolkit:** Android framework Views with one XML layout (`app/src/main/res/layout/activity_main.xml`) and custom views (`OptionRow`, `TrackCorner`, `AudioMeterView`). No Compose, Material, AndroidX or Leanback library. `Theme.Leanback` is a local style derived from `@android:style/Theme.Black.NoTitleBar.Fullscreen` (`res/values/themes.xml`).
- **Tokens:** reuse `res/values/colors.xml` (`overlay_panel`, `accent`, `text_primary`/`secondary`/`tertiary`, ...), `dimens.xml`, `styles.xml` (`Overlay.*` text styles) and drawables such as `bg_option_row`, `bg_overlay_panel`, `bg_pill`.
- **Input:** the D-pad remote is primary; touchscreen and gamepad are declared not required. `MainActivity.onKeyDown` and `docs/user-guide/controls.md` must agree: Right/Next/Fast forward random preset, Left/Previous/Rewind previous preset (hard cuts), Up/Down/Info show the track, Center/Enter/Menu open the panel, Back exits; with a panel open, Back returns to the main panel or closes it and Menu closes it.
- **Focus:** `OptionRow` is a focusable settings row: up/down moves between rows, left/right changes the value, center cycles it or runs an action. Track display and Advanced slide over the main panel. Panels hide after ten seconds without input.
- **Layout:** landscape; panels stay within the 48 dp / 27 dp overscan-safe margins; hidden overlay views are set to `GONE`; marquees restart only when text changes (`docs/ARCHITECTURE.md`, *Overlay UI*).
- **Accessibility:** icon-only buttons carry `contentDescription` (e.g. "Previous preset"); do the same for new ones.
- Rendering changes need before/after TV captures (PR template).

## Use existing platform and dependency APIs

Before implementing a component, parser, formatter, scheduler, transport, or similar utility:

1. Check existing project code for a suitable implementation.
2. Check the declared and resolved dependencies for a supported API.
3. Verify the API and recommended usage against the version in use and official documentation.
4. Implement a custom alternative only when the existing options are absent or unsuitable, and record the reason in the PR.

Prefer configuration, composition, or a small wrapper to copied library source or overlapping dependencies. Use maintained implementations for security-sensitive primitives.

| Need | Preferred API | Version truth | Constraints |
|---|---|---|---|
| GL surface and thread | `GLSurfaceView` via `VisualizerView` (ES 3, `setPreserveEGLContextOnPause(true)`) | compileSdk 34 | Only the GL thread touches the projectM handle |
| Visualization | projectM C API (`projectm_*`) from `native-lib.cpp` | submodule `v4.1.7` + patch series | Change projectM only through patches |
| Equation evaluation | projectm-eval inside projectM | nested submodule | Pre-generated parser; no flex/bison |
| Audio | `android.media.audiofx.Visualizer` on the player's session (`PlayerSessionFinder`) | framework | No session 0, no playback capture (`docs/ARCHITECTURE.md`, *Audio source*) |
| Track titles | `NotificationListenerService` + media session (`TrackWatcher`) | framework | Needs notification access |
| Settings | `SharedPreferences` `projectm_settings` | framework | Keep stored values backward compatible |
| Half-rate pacing | `Choreographer` + `RENDERMODE_WHEN_DIRTY` | framework | |
| Updates | `HttpURLConnection` in `Updater`, `UpdateFileProvider` | framework | Off by default; disabled for F-Droid installs |
| JVM tests | JUnit 4.13.2 | module `build.gradle` | `unitTests.returnDefaultValues = true` |
| Docs site | MkDocs 1.6.1, `readthedocs` theme | `docs/site-requirements.txt`, `mkdocs.yml` | |

Adding a dependency (especially AndroidX) needs a recorded reason: the app intentionally uses framework APIs only, and F-Droid rebuilds must stay reproducible.

## Performance and resource use

Avoid blocking work on latency-sensitive threads, unnecessary polling, duplicate requests, unbounded concurrency, and background work that outlives its owner. Honor existing cache, cancellation, visibility, lifecycle, and resource-release contracts. Back performance claims with measurements and state what was not measured.

- **Threads** (`docs/ARCHITECTURE.md`, *Threads*): the GLSurfaceView GL thread (`THREAD_PRIORITY_DISPLAY`) renders, loads presets, measures output and draws the transition overlay. Other entry points only write atomics or mutex-protected buffers. Audio capture runs on a `HandlerThread` (`THREAD_PRIORITY_AUDIO`) feeding `ProjectMJNI.addWaveform`; a native worker indexes and prefetches presets; `PresetPrewarmer` compiles upcoming presets on a background thread with its own EGL pbuffer context into a program binary cache (capped at 8 MB).
- **Lifecycle:** `MainActivity.onPause` pauses `VisualizerView` (EGL context preserved) and the updater; `onTrimMemory` reaches `QualityController` and the engine's memory-pressure path. Prewarming and the framebuffer texture pool back off under low memory.
- **Frame pacing:** full rate renders continuously; half rate (the default, 30 fps at 60 Hz) uses a `Choreographer` callback on every second vsync. Render size uses the hardware scaler (`SurfaceHolder.setFixedSize`); *Auto* levels come from `QualityController` and `DeviceProfile` tiers.
- **Budgets:** none established in the repository. Published figures (README appendix, `docs/ARCHITECTURE.md`) are NVIDIA SHIELD measurements, not targets.
- **Measuring:** install the `profile` build next to the release app, pin one preset with `debug.projectmtv.preset`, keep render height and audio equal, alternate release and profile runs, and read `VisualizerRenderer: STATS fps=` and `projectM-Native` `LOAD`/`PREWARM`/`TRANSITION` lines. CPU profiles: simpleperf per `docs/PROFILING.md`. Sweeps: `tools/tv-diagnostics.sh <tv>:5555 --sweep` (`docs/DIAGNOSTICS.md`).
- Per-vertex equations run on the CPU and usually limit low-end ARM boxes; *Detail* (mesh size) controls that work.

## Dependencies, state, and lifecycle

Follow the existing dependency injection and ownership model. Prefer explicit dependencies and testable boundaries. Preserve instance identity, initialization timing, lifecycle, cancellation, and cleanup when refactoring. Keep migrations focused on the task and avoid creating duplicate services, caches, clients, or background workers.

- No DI framework. `ProjectMCore.init(context)` runs once from `ProjectMApplication` and starts the native worker; `ProjectMJNI` is a static facade over one native engine; `MainActivity` creates `QualityController` and `TrackWatcher` directly and gets the `Updater` singleton from `Updater.get`.
- The projectM handle is created, used and released on the GL thread (`VisualizerRenderer`); context loss resumes the current preset.
- Persistence: `SharedPreferences` `projectm_settings`, the skip list (`ProjectMCore.skipListFile`), downloads under `no_backup/`. No database or schema migrations; keep old preference values readable (e.g. the former "4K" resolution maps to "Native").
- Changes to threading, init or teardown need the native engine tests (commands, context loss) and a device run.

## User-facing text and localization

Use the project's established resource or localization mechanism for user-facing text. Follow its locale ownership and translation workflow; do not invent an English-only or all-locales policy.

- `app/src/main/res/values/strings.xml` holds only `app_name`; there are no `values-*` locale directories and no translation workflow. UI text is English, written in `activity_main.xml` and Java. Follow the surrounding pattern; debug test variants override `app_name` with `resValue`.
- User-facing docs write menu paths as *Settings › Advanced › Setting*.

## Code structure and modularization

Place code according to its responsibility and actual consumers. Reuse shared code when appropriate without creating speculative abstractions. Split oversized or mixed-responsibility files along meaningful boundaries. Preserve behavior during refactors and remove obsolete code.

| Responsibility | Location |
|---|---|
| UI, audio capture, track titles, updater | `app/src/main/java/com/example/projectm/visualizer/` |
| Resources (layout, colors, styles, drawables) | `app/src/main/res/` |
| Profile-build manifest | `app/src/profile/AndroidManifest.xml` |
| App JVM tests / instrumentation | `app/src/test/java/...`, `app/src/androidTest/java/...` (`MusicCategoryInstrumentation`) |
| Engine Java API (JNI, view, renderer, quality, device tiers) | `core/src/main/java/nl/neerdael/projectm/core/` |
| Native engine and its CMake (applies patches) | `core/src/main/cpp/` |
| Presets, textures, index, genre bundle | `core/src/main/assets/` |
| Core JVM tests | `core/src/test/java/nl/neerdael/projectm/core/` |
| Native host tests (fakes, GL overlay, patched-projectM regressions) | `core/src/test/native/` |
| projectM source (never commit inside) / patches | `third_party/projectm/` / `tools/projectm-patches/` |
| Preset, patch and device tools | `tools/` (`tools/preset-lab/` is a separate Python package) |
| Release tooling and tests | `.github/scripts/`, `.github/scripts/tests/` |
| Docs / user guide / store metadata | `docs/`, `docs/user-guide/`, `fastlane/metadata/android/` |

JNI functions are bound by name (`Java_nl_neerdael_projectm_core_ProjectMJNI_*`); renaming `ProjectMJNI` or its package needs matching native changes. No file-size limits are established.

## Repository-specific constraints

Preserve the release/version rules above. Treat the core AAR’s interface and compatibility with Milkbeat as an integration boundary; verify the actual API and consumers before changing it. These constraints cannot waive the mandatory documentation evaluation rule below.

- **Integration boundary:** `ProjectMJNI` and the core AAR are what Milkbeat consumes. `core/consumer-rules.pro` keeps `ProjectMJNI`'s native methods through R8. Which other core classes Milkbeat uses is unverified here; check Milkbeat before changing public `nl.neerdael.projectm.core` APIs. No procedure for incompatible changes is documented: treat one as breaking, coordinate the Milkbeat update, and state it in the release notes.
- **projectM changes only through patches** in `tools/projectm-patches/`, never by committing inside `third_party/projectm`. Patches apply in order to a clean export; `tools/check-patch-series.sh` verifies the series. Each patch header explains the change and credits any upstream commit/PR. `docs/THIRD_PARTY.md` lists every patch and must be updated with each new one.
- **Regenerating a patch:** apply and stage the earlier patches (`git -C third_party/projectm add -A`), edit, then `tools/regen-projectm-patch.sh <patch-file-name>` rewrites the patch from unstaged `src/` and `tests/` changes, keeping its header. It does not cover `vendor/projectm-eval` (a nested submodule); diff those files with `git -C third_party/projectm/vendor/projectm-eval diff --src-prefix=a/vendor/projectm-eval/ --dst-prefix=b/vendor/projectm-eval/`.
- **projectm-eval parser:** `Scanner.c`/`Compiler.c` are pre-generated and the build sets `CMAKE_DISABLE_FIND_PACKAGE_FLEX`/`BISON` for reproducibility. Apple's flex 2.6.4 skeleton differs from the committed one, so for a `Scanner.l` change apply only the flex-to-flex delta to `Scanner.c`.
- After pulling a patch change, reset the submodule (`git submodule foreach --recursive git checkout -- .`) so the CMake configure reapplies the series.
- **Preset equation loading (patches 0029–0032):** rejected equation code is retried in MilkDrop's legacy form (numbered lines joined, line comments removed); a lone `.` reads as 0; blocks that still do not compile are left out with an initialization warning, logged by `native-lib.cpp` as `Preset code left out`, instead of failing the preset. Parse errors still fail the load (`Preset load failed`).
- **Reproducible builds:** F-Droid rebuilds and compares the APK. Keep `-ffile-prefix-map`, JDK 21, `dependenciesInfo` disabled and pre-generated parser sources; avoid build-path or timestamp dependence. The external F-Droid recipe hardcodes the current release line (unverified from this repository).
- **Presets and textures** are distributed as CC0 (`docs/THIRD_PARTY.md`). `tools/check-presets.py` (CI) rejects non-reactive presets and excluded or missing textures; keep `presets.idx` current. The app's code is LGPL 2.1, matching projectM.
- **Local and tracked files:** `local.properties` is git-ignored (copy it into new worktrees); `build/reports/problems/problems-report.html` is tracked despite the `build/` ignore rule, so do not commit Gradle's incidental rewrites of it. Preset Lab user audio and raw captures must stay untracked (CI enforces this).

## Formatting and linting

Follow the repository's configured formatting and lint rules. Review automatic formatting changes and avoid unrelated churn. Fix violations rather than disabling checks to obtain a passing result.

- No formatter or linter is configured: no `.clang-format`, `.editorconfig`, Android Lint configuration, Checkstyle or Spotless, and CI has no lint step. Match surrounding style (4-space indentation in Java and C++).
- `core/src/main/cpp` compiles with `-Wall -Wextra -Wno-unused-parameter`; keep new code warning-free.
- Docs: `mkdocs build --strict` (CI *User guide*). PR body: `python3 .github/scripts/release_notes.py validate --event-file <event.json>` (CI *PR release notes*).

## Building and testing

Choose validation that exercises the changed behavior. Compilation alone does not establish functional correctness. For UI or integration changes, exercise relevant user journeys and error paths when the environment supports them. Record baseline failures and environmental limitations honestly.

For release tooling changes, the required check is:

```bash
python3 -m unittest discover -s .github/scripts/tests -v
```

Verified on macOS on 2026-10-04 unless marked otherwise:

| Check | Command | Result / notes |
|---|---|---|
| Submodules (fresh worktree) | `git submodule update --init --recursive` | Required before any build |
| Patch series | `tools/check-patch-series.sh` | "all 32 patches apply" |
| Native engine tests | `JAVA_HOME=<JDK 21> core/src/test/native/run_native_tests.sh` | Engine tests pass; projectm-regressions 2/2; GLES overlay test skipped on macOS (no EGL/GLES pkg-config); CI runs it on Linux with Mesa |
| Android build | `./gradlew :app:assembleProfile :core:assembleRelease` (JDK 21) | BUILD SUCCESSFUL; needs `local.properties` with `sdk.dir` (copy from the primary checkout) and NDK `27.3.13750724` |
| JVM unit tests | `./gradlew testReleaseUnitTest` | BUILD SUCCESSFUL; the CI step (the PR template lists `testDebugUnitTest`) |
| User guide | `mkdocs build --strict` (after `pip install -r docs/site-requirements.txt`, e.g. in `build/docs-venv`) | Builds without warnings; CI runs it in `docs.yml` |
| Patch series from a fresh clone | `git clone --recurse-submodules …` then `./gradlew :core:assembleDebug` | BUILD SUCCESSFUL; the CMake configure applies the whole series to the pinned submodule |
| Preset Lab | `python -m pytest tools/preset-lab/tests` | When `tools/preset-lab/` changes; CI runs it (unverified locally) |
| Preset assets | `tools/gen-preset-index.py --check`, `tools/check-presets.py` | When presets or textures change; CI runs them (unverified locally) |

**Host projectM unit tests** (patch changes): `tools/projectm-host-tests.sh` builds and runs projectM's GTest suite. The equivalent manual configure, which also uses the pre-generated parser like the Android build, was verified:

```bash
cmake -S third_party/projectm -B build/projectm-host -G Ninja -DCMAKE_BUILD_TYPE=Debug \
  -DBUILD_TESTING=ON -DENABLE_SYSTEM_PROJECTM_EVAL=OFF -DENABLE_PLAYLIST=OFF \
  -DCMAKE_DISABLE_FIND_PACKAGE_FLEX=ON -DCMAKE_DISABLE_FIND_PACKAGE_BISON=ON \
  -DGTest_DIR="$(brew --prefix)/lib/cmake/GTest" "-DCMAKE_CXX_FLAGS=-include $PWD/tools/projectm-host-gl-shim.h"
cmake --build build/projectm-host --target projectM-unittest
build/projectm-host/tests/libprojectM/projectM-unittest   # 197 tests passed
```

It needs the patches applied in `third_party/projectm` (an Android CMake configure or a manual `git apply` loop) and Homebrew `googletest`.

**On a TV** (rendering, preset loading, audio, performance, lifecycle): ask before using shared test TVs; other sessions may be using them. The rooted Ugoos AM6 at `192.168.50.80:5555` runs Android 9 with 32-bit userspace (`armeabi-v7a`). Install the `profile` build next to the release app (`docs/PROFILING.md`), pin a preset with `adb shell setprop debug.projectmtv.preset '<name prefix>'` (at most 91 bytes; an ambiguous prefix picks the first non-skipped match, so confirm with the `BENCHMARK preset=` log line), read `adb logcat -s projectM-Native` (`LOAD`, `Preset load failed`, `Preset code left out`), and clear the property afterwards. Category and live-audio checks: `MusicCategoryInstrumentation` on the `presettest` build (`docs/user-guide/development.md`). Milkbeat integration is exercised only by Milkbeat's own build after the release dispatch.

## Generated artifacts and release preparation

A successful tested merge to `main` triggers the versioned APK/core AAR release and Milkbeat update. Routine PRs must not manually bump the base version/code/commit. Follow `docs/RELEASING.md` for a planned new release line.

| Workflow (file) | Trigger | Does |
|---|---|---|
| Android CI/CD (`android.yml`) | Push to any branch, PR, manual | Release-tooling tests, preset checks, native tests; JVM tests, `assembleRelease`, APK/core AAR/mapping artifacts. On `main` with release metadata: GitHub Release, then Milkbeat dispatch |
| User guide (`docs.yml`) | PR/push to `main` touching `docs/user-guide/**`, `docs/site-requirements.txt`, `mkdocs.yml`, the workflow; manual | `mkdocs build --strict`; deploys to GitHub Pages from `main` |
| Preset Lab (`preset-lab.yml`) | Push, PR, manual | Preset Lab tests, untracked-audio check, native rendering tests under Xvfb |
| PR release notes (`release-notes.yml`) | PR opened/edited/synchronized/reopened/ready | Validates the `## Release notes` section |

- **Versions:** `.github/scripts/release_version.py` maps the first first-parent commit after `baseVersionCommit` to `baseVersionName`/`baseVersionCode` (currently `2.2.0` / 38) and advances both per commit; CI passes `PROJECTM_RELEASE_VERSION`/`PROJECTM_RELEASE_VERSION_CODE` to Gradle. Non-release builds get the versionName suffix `-ci.<run>` (`VERSION_SUFFIX`) and `-ci.<run>-<sha>` artifact names.
- **Signing:** secrets `SIGNING_KEYSTORE_BASE64`, `SIGNING_STORE_PASSWORD`, `SIGNING_KEY_ALIAS`, `SIGNING_KEY_PASSWORD`; a publishing build without them fails. `MILKBEAT_TOKEN` (Contents read/write on Milkbeat) drives the dispatch.
- **Publication:** `release_notes.py generate` builds notes from merged PR `Release notes` sections and appends install details; `publish_release.py publish` uploads `projectM-TV-<version>.apk`, `projectM-TV.apk`, `projectM-TV-core-<version>.aar`, `projectM-TV-core.aar`, `projectM-TV-<version>-mapping.txt` and `checksums.txt` to a draft release, then publishes it.
- **Downloader code:** owned by the install blockquote at the top of `README.md` (currently `4821216`); CI reads it from there.
- Nothing generated by releases is committed. `RELEASE_NOTES.md` is a manually maintained archive.

## Documentation map

The mandatory documentation evaluation rule below applies to every change; use this map to find the affected sources.

| Source | Role |
|---|---|
| `README.md` | Overview, canonical Downloader install blockquote, features, troubleshooting, developer build/test |
| `docs/user-guide/*.md` + `mkdocs.yml` | User guide, published by `docs.yml` to https://johnneerdael.github.io/ProjectM-TV/ (site built into `build/user-guide-site`) |
| `docs/ARCHITECTURE.md` | Design, threading, preset pipeline, measurements |
| `docs/PROFILING.md`, `docs/DIAGNOSTICS.md` | Profile build and simpleperf; `tools/tv-diagnostics.sh` |
| `docs/RELEASING.md` | Release automation, versions, signing, Milkbeat |
| `docs/THIRD_PARTY.md` | projectM version, every patch, preset/texture licences |
| `docs/DANCE-COLLECTION.md` | Pointer to `docs/user-guide/dance-measurement.md` |
| `RELEASE_NOTES.md` | Per-version change archive |
| `tools/preset-lab/README.md` | Preset Lab usage |
| `.github/pull_request_template.md` | PR sections and checklists |
| `fastlane/metadata/android/en-US/` | App title, descriptions, images and changelogs (fastlane layout) |
| `docs/superpowers/` | Design specs, plans and evidence from past work |

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
- Remove only this task's clean worktree after confirming all intended work is pushed and merged. Delete its branch only when repository policy permits. Preserve unrelated worktrees, branches, and uncommitted changes.
- Report the outcome concisely: what changed, relevant validation, PR link, Codex review disposition, and merge confirmation.
- If a real blocker prevents completion, report the current branch, worktree, PR, completed checks, exact blocker, and next required action. Describe the task as blocked, not completed.
