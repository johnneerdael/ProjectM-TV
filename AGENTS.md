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

Maintain repository-specific guidance in the same isolated worktree and PR whenever architecture, commands, dependencies, documentation or constraints change. Read current source/manifests and CI rather than treating historical documentation as current implementation. Validate commands before claiming they pass; distinguish recorded evidence, prerequisites and unverified coverage. Do not install tooling solely to fill this file. Changes here follow the documentation, validation and Codex review gates below.

## Repository overview

ProjectM TV visualizes another app's music on Android TV; it is not a player. `:app` provides framework Java/XML UI, player-session audio capture, track metadata and optional updates. `:core` provides Java/JNI, C++17/GLES3 rendering, projectM and packaged presets/textures, and is released as an AAR for Milkbeat.

- Installed app ID: `nl.neerdael.projectmtv`; app namespace/source package: `com.example.projectm.visualizer`; core namespace/package: `nl.neerdael.projectm.core`.
- Android API 21 minimum, compile/target API 34; manifest requires Leanback TV, audio output and OpenGL ES 3.0, with no touchscreen/microphone requirement. Packaged native ABIs are `armeabi-v7a` and `arm64-v8a`.
- `app/build.gradle` defines `debug`, R8-shrunk `release`, and release-derived `profile` (`.profile` app ID, debug signed). Debug properties `-PpresetLabDeviceTest` / `-PsetupScreenshotTest` use `.presettest` / `.setuptest` IDs. Core has debug/release variants; no product flavors are declared.
- Startup: `ProjectMApplication.onCreate` → `ProjectMCore.init`; `MainActivity` hosts `VisualizerView` / `VisualizerRenderer`. Embedders feed unsigned-byte audio and settings through public `ProjectMJNI`.
- `third_party/projectm` pins projectM v4.1.7 (`e0b0a967`) plus recursive projectm-eval. Ordered local fixes live in `tools/projectm-patches/`; the playlist library is disabled. Preserve upstream attribution in patch headers and `docs/THIRD_PARTY.md`.

## Codebase navigation and knowledge tools

Use the placement table below and the public core Java classes to navigate. `docs/ARCHITECTURE.md` explains threading and historical regressions, but its v1.9 toolchain, defaults and test counts include obsolete entries; verify against current source and CI. No `.codegraph/`, `.code-review-graph/graph.db` or `graphify-out/graph.json` exists in this task checkout. Use available native file/content search, or `rg` when shell is the available search interface; do not generate or commit a graph without a task requiring it.

## Design and user experience

Follow the project's established design system and platform conventions. Reuse existing theme tokens and components. Preserve accessibility, keyboard/focus behavior, responsiveness, and supported input methods. Avoid introducing decorative styles or changing appearance incidentally during a refactor.

The UI uses framework Views, not AndroidX/Compose: `app/src/main/res/layout/activity_main.xml`, `values/{themes,styles,colors,dimens}.xml`, `OptionRow.java`, `TrackCorner.java` and `AudioMeterView.java`. `Theme.Leanback` is a local fullscreen framework theme. Preserve 48 dp horizontal / 27 dp vertical overscan margins, visible focus, transport content descriptions, marquee behavior and nonoverlapping track/settings overlays.

Keep the `docs/user-guide/controls.md` contract: Right/Next/Fast-forward cuts to random; Left/Previous/Rewind returns to previous; Up/Down/Info redisplays track info; Center/Enter/Menu opens settings; Back exits. In settings, Up/Down moves focus, Left/Right changes a row value without leaving it, Center activates, Back returns/closes, Menu closes; inactivity hides the panel after 10 s. Click listeners exist for rows/buttons and Enter is handled, but broad touch, keyboard and screen-reader coverage has not been established. Validate remote/focus changes on an approved device.

## Use existing platform and dependency APIs

Before implementing a component, parser, formatter, scheduler, transport, or similar utility:

1. Check existing project code for a suitable implementation.
2. Check the declared and resolved dependencies for a supported API.
3. Verify the API and recommended usage against the version in use and official documentation.
4. Implement a custom alternative only when the existing options are absent or unsuitable, and record the reason in the PR.

Prefer configuration, composition, or a small wrapper to copied library source or overlapping dependencies. Use maintained implementations for security-sensitive primitives.

| Need | Existing API / source of truth | Constraint |
| --- | --- | --- |
| UI, audio, media metadata, scheduling | Android framework API 21–34; module Gradle files | Guard newer APIs; no AndroidX runtime dependency is declared. Reuse `PlayerSessionFinder`, `TrackWatcher`, `OptionRow`. |
| Rendering and engine | GLES3 / EGL and patched projectM v4.1.7; `core/src/main/cpp/CMakeLists.txt`, gitlinks | One `libprojectmtv.so` statically links projectM; preserve GL-thread ownership and ordered patches. |
| Unit tests | JUnit 4.13.2; `app/build.gradle`, `core/build.gradle` | JVM Android stubs return defaults; these tests do not establish device behavior. |
| Build / documentation | AGP 8.12.0 (`build.gradle`), Gradle 8.14.2 (wrapper), MkDocs 1.6.1 (`docs/site-requirements.txt`) | Use pinned tooling; Preset Lab is separate Python tooling with `pyproject.toml` / `requirements.lock`. |

No Gradle dependency lockfile is present. Check resolved dependencies when introducing API usage; do not infer transitive versions from these declarations.

## Performance and resource use

Avoid blocking work on latency-sensitive threads, unnecessary polling, duplicate requests, unbounded concurrency, and background work that outlives its owner. Honor existing cache, cancellation, visibility, lifecycle, and resource-release contracts. Back performance claims with measurements and state what was not measured.

Only the GL thread may create, resize, draw or release the projectM handle. Other JNI requests use atomics/mutex-protected buffers and apply on subsequent frames. `VisualizerRenderer.StatsListener` callbacks run on the GL thread; hand UI changes back to the main thread. Native production units are `native-lib.cpp`, `snapshot_fade.cpp`, `preset_prewarm.cpp`.

`VisualizerView` requests GLES3, preserves its EGL context on pause, uses `SurfaceHolder.setFixedSize` for render dimensions, and uses `Choreographer` for divided-vsync pacing. `MainActivity` owns the audio HandlerThread and player-session `Visualizer`; never attach to session 0. Waveform input is unsigned 8-bit mono, not 16-bit stereo. Pause stops audio watch/polling, view pacing, UI refresh, track watching and updater scheduling; destruction releases audio and queues GL release. Context recreation handles a release that could not execute.

Preserve `QualityController.RENDER_HEIGHT_CAP = 1330` for Auto and numeric fixed modes. This branch's explicit Native sentinel is `NATIVE_HEIGHT = -1`, gated by physical panel height and memory limits; old numeric heights above the cap migrate to a capped choice, not Native. Native diffusion is an unaccepted feature under investigation, not evidence to raise the default cap. Memory pressure must preserve music playback: the engine pauses prewarming and quality handles pressure without resetting unrelated settings.

For rendering changes compare the same preset, audio, frame count, render size, clock/RNG and artifact identity; preserve before/after captures and brightness/colour/sharpness separately from image MAE. `docs/PROFILING.md` documents `assembleProfile`, `STATS` logs and simpleperf; `docs/DIAGNOSTICS.md` documents TV sweeps. Those device/profile commands have not been revalidated in this discovery. Host/emulator results do not prove TV GPU performance, thermal behavior or full-corpus fidelity.

Current actual-core baseline29/candidate30 evidence and metadata live in `docs/superpowers/evidence/0025-feedback-diffusion/current-main-validation/`. Use its source identities, AAR/ELF/APK proofs and job protocols; older direct-libprojectM/desktop or differing RNG rows are supplementary only. The first four-preset hardware matrix is mixed and does not establish acceptance. Do not treat passed native unit tests as a renderer-fidelity verdict.

## Dependencies, state, and lifecycle

Follow the existing dependency injection and ownership model. Prefer explicit dependencies and testable boundaries. Preserve instance identity, initialization timing, lifecycle, cancellation, and cleanup when refactoring. Keep migrations focused on the task and avoid creating duplicate services, caches, clients, or background workers.

There is no DI framework or database. Construction/ownership is explicit: `MainActivity` owns view, quality controller, audio thread and track watcher; `Updater.get` is a process singleton using application context with detachable activity listeners. `ProjectMCore.init` is idempotent and retains the application AssetManager; native startup indexes assets and copies textures before the first preset.

Preferences are framework `SharedPreferences` named `projectm_settings`; preserve existing keys, defaults and migration semantics. Native skipped names persist in `files/skipped_presets.txt`; textures in `files/textures`; updater files in `no_backup/update-download` and `no_backup/updates`. Do not reset production preferences or replace its installed app during test setup. Changes to these paths/ownership require startup, pause/resume, context-loss, permission-denial, pressure and persisted-setting coverage appropriate to the boundary.

## User-facing text and localization

Use the project's established resource or localization mechanism for user-facing text. Follow its locale ownership and translation workflow; do not invent an English-only or all-locales policy.

`app/src/main/res/values/strings.xml` is the only strings/locale resource set. Existing menu text and some accessibility descriptions are also inline in Java/XML; there is no documented translation pipeline. Reuse resource identifiers and move new reusable user text into `strings.xml` without inventing an all-locales requirement. Preserve transport descriptions, track truncation/marquee and locale-independent machine diagnostics (`Locale.US` in renderer `STATS`). Preset/author names are asset identities and must not be translated.

## Code structure and modularization

Place code according to its responsibility and actual consumers. Reuse shared code when appropriate without creating speculative abstractions. Split oversized or mixed-responsibility files along meaningful boundaries. Preserve behavior during refactors and remove obsolete code.

| Responsibility | Location |
| --- | --- |
| TV UI, audio session discovery, media metadata, APK update | `app/src/main/java/com/example/projectm/visualizer/`, `app/src/main/res/` |
| Embeddable engine API, quality/device/display logic, GL view | `core/src/main/java/nl/neerdael/projectm/core/` |
| JNI/native orchestration, fade and prewarm | `core/src/main/cpp/` |
| Upstream engine modifications | `tools/projectm-patches/*.patch`; never commit changes inside `third_party/projectm` |
| Bundled presets, textures and genre indexes | `core/src/main/assets/{presets,textures,preset-genres}/`, `presets.idx` |
| JVM / native / device tests | `app/src/test/`, `core/src/test/`, `app/src/androidTest/` |
| Offline analysis and actual-core workers | `tools/preset-lab/`, `tools/core-corpus/` |
| Documentation / release tooling | `docs/`, `mkdocs.yml`, `.github/scripts/`, `.github/workflows/` |

Match package names and existing explicit helper patterns. Keep internal utilities scoped to their consumers and preserve public core names. No repository file-size budget is established. CMake generates native build/configuration output; projectm-eval uses its pregenerated parser with Flex/Bison discovery disabled for reproducibility.

## Repository-specific constraints

Preserve the release/version rules above. Treat the core AAR’s interface and compatibility with Milkbeat as an integration boundary; verify the actual API and consumers before changing it.

- `ProjectMJNI` native method names/signatures bind to `Java_nl_neerdael_projectm_core_ProjectMJNI_*` in `native-lib.cpp`; `core/consumer-rules.pro` keeps them under R8. Preserve `System.loadLibrary("projectmtv")`, both packaged ARM ABIs and public core API semantics. Deliberate incompatibility needs an explicit consumer assessment, coordinated Milkbeat validation and documented migration in the reviewed PR; no formal API-versioning policy is currently documented.
- Change upstream projectM through numbered patch files generated against the pinned tree plus earlier patches. CMake applies the series under `core/.cxx/projectm-patches.lock`; never commit the patched submodule state or reset another agent's checkout. `tools/regen-projectm-patch.sh <filename>` rewrites an owned patch from prepared submodule changes; it is not a routine read-only check.
- Preserve the 9,606-preset index and genre bundle consistency. CI rejects nonreactive presets, missing textures and excluded text/logo/people textures. Regenerate the index when its inputs change, and evaluate genre manifests when presets change. Licensing/attribution sources are `LICENSE`, `LICENSES/` and `docs/THIRD_PARTY.md` (projectM LGPL 2.1; bundled preset/texture distribution CC0 as qualified there).
- User rule: **never remove any Git worktree unless explicitly asked**, including this task's worktree after merge. Preserve checkpoint commits/pushes through the personal `johnneerdael` account and unrelated branches/data.
- Native4K device rule: only physical TV `192.168.51.53` is approved, and **never remotely wake it**. Targeted tests own `emulator-5582`; the corpus owner controls `emulator-5580`, its processes and `.worktrees/quad-lines-follow-ups`. Do not restart, kill, reconfigure, install into or otherwise touch the corpus owner's environment. Always select the intended ADB serial/server; do not use ambiguous device-wide commands.

## Formatting and linting

Follow the repository's configured formatting and lint rules. Review automatic formatting changes and avoid unrelated churn. Fix violations rather than disabling checks to obtain a passing result.

No dedicated Java/C++ formatter, style ratchet or lint workflow is configured. Preserve local formatting and run `git diff --check` from the task root (validated for this guidance edit). Android's Gradle lint is available through AGP but `./gradlew :app:lintDebug :core:lintDebug` has not been run for this task and is not a documented CI gate. Do not invent an established lint result. Native compilation enables `-Wall -Wextra`; release-tooling, preset-index, preset validation, native/JVM tests and documentation build are the concrete CI checks.

## Building and testing

Choose validation that exercises the changed behavior. Compilation alone does not establish functional correctness. For UI or integration changes, exercise relevant user journeys and error paths when the environment supports them. Record baseline failures and environmental limitations honestly.

For release tooling changes, the required check is:

```bash
python3 -m unittest discover -s .github/scripts/tests -v
```

Run commands from the task worktree root. Android prerequisites: recursive projectM/projectm-eval checkout, JDK 21 (CI Temurin; local discovery finds Homebrew 21.0.11), Gradle wrapper 8.14.2, SDK platform 34, NDK 27.3.13750724 and CMake 3.22.1. Configure the local SDK path without committing machine settings. `git submodule update --init --recursive` is setup, not permission to discard existing submodule edits.

| Command | Scope and evidence / prerequisites |
| --- | --- |
| `./gradlew :core:testDebugUnitTest :app:testDebugUnitTest` | Current task succeeds; unchanged tests were up-to-date. This is not a fresh rerun or device test. |
| `./gradlew :core:assembleRelease` | Succeeded for isolated current-main baseline29 / candidate30 scratch builds with the three production native units; identities/proofs in current-main-validation. |
| `bash core/src/test/native/run_native_tests.sh` | CI/PR requirement for native changes; needs C++17 compiler, JDK headers, CMake, and EGL/GLES development files on Linux or macOS OpenGL for real-engine regressions. Runner may skip GL checks; record each skip. Full runner not reexecuted during this guidance discovery. |
| `./gradlew :app:assembleDebug` / `./gradlew assembleRelease --no-daemon --stacktrace` | APK validation / CI APK+AAR release build; not reexecuted during this discovery. Paths: `app/build/outputs/apk/debug/app-debug.apk`, `app/build/outputs/apk/release/app-release.apk`, `core/build/outputs/aar/core-release.aar`. |
| `./gradlew testReleaseUnitTest --no-daemon` | CI release-variant JVM coverage; not reexecuted during this discovery. |
| `python3 tools/gen-preset-index.py --check` / `python3 tools/check-presets.py` | CI asset checks; not reexecuted during this discovery. |
| `python3 -m unittest discover -s .github/scripts/tests -v` | Required for release-tooling changes; not reexecuted during this guidance-only subtask. |
| `build/docs-env/bin/mkdocs build --strict` | Documentation validation after installing `docs/site-requirements.txt` in an owned environment; not run during this discovery. |

`docs/user-guide/development.md` gives the isolated `.presettest` instrumentation build and live-audio category/navigation checks; device commands are unverified by this discovery and require an approved awake device, installed app/test APKs and permissions. Rendering/preset/audio changes need relevant device journeys and matched captures/FPS; ownership/lifecycle changes need resume/context-loss/permission/pressure checks. For unreleased Milkbeat integration, `docs/RELEASING.md` documents a local AAR repository and `-PprojectmCoreRepo` / `-PprojectmCoreVersion`; consumer builds were not independently validated here.

`tools/core-corpus/run_corpus.py` validates actual-core worker artifact/asset/protocol identities and supports resumable jobs. Follow `tools/core-corpus/README.md` and the newer current-main-validation protocols; do not relaunch a full corpus or combine old baseline24/candidate25 data with baseline29/candidate30. Record GPU, physical/emulated device, clock/RNG, captures and failures; unit-test/build passes alone cannot accept Native4K.

## Generated artifacts and release preparation

A successful tested merge to `main` triggers the versioned APK/core AAR release and Milkbeat update. Routine PRs must not manually bump the base version/code/commit. Follow `docs/RELEASING.md` for a planned new release line.

`.github/workflows/android.yml` (**Android CI/CD**) runs on pushes, PRs and manual dispatch, queues builds, tests native/assets/release scripts and release-variant JVM code, then builds release APK/AAR. `.github/scripts/release_version.py` derives stable versions/codes from first-parent history after the literal base triple in `app/build.gradle`; feature/PR artifacts have CI suffixes. Only eligible main revisions publish through `publish_release.py`; keep routine base values unchanged.

CI signs published releases using `SIGNING_KEYSTORE_BASE64`, `SIGNING_STORE_PASSWORD`, `SIGNING_KEY_ALIAS`, `SIGNING_KEY_PASSWORD`; local signing uses `SIGNING_KEYSTORE_PATH`. Publishing without signing fails; local release builds fall back to a debug key and cannot replace stable installs. Never expose key/password values.

GitHub Releases attach versioned and fixed `projectM-TV.apk` / `projectM-TV-core.aar`, R8 mapping and `checksums.txt`. CI stages `dist/`, `dist-aar/`, `dist-mapping/`; these and Gradle/CMake build outputs are generated artifacts, not source changes. `release_notes.py` gathers merged PR notes and appends artifact/install details using README's canonical Downloader blockquote (currently `4821216`). `release-notes.yml` (**PR release notes**) validates PR bodies including edited bodies. Milkbeat's job uses `MILKBEAT_TOKEN` and sends `projectm-core-release` through `publish_release.py milkbeat`; verify its outcome separately from APK publication.

Commit generated `core/src/main/assets/presets.idx` when asset inputs change (`python3 tools/gen-preset-index.py`, then `--check`), and reviewed genre exports imported by `tools/import-preset-genres.py --bundle <bundle>`. These regeneration commands were inspected but not executed during discovery. Do not stage keystores, APK/AARs, `.cxx/`, `.gradle/`, worktrees or unrelated reports; `build/reports/problems/problems-report.html` and parts of `.idea/` remain tracked technical debt despite ignore rules.

## Documentation map

- `README.md`: app/install/remote/settings overview, canonical Downloader blockquote and developer instructions. Its released-behavior descriptions do not establish acceptance of this Native4K branch.
- `docs/user-guide/`: source for https://johnneerdael.github.io/ProjectM-TV/; `mkdocs.yml` controls navigation/theme/output at `build/user-guide-site`. `.github/workflows/docs.yml` (**User guide**) builds with `mkdocs build --strict` on relevant PRs and main pushes, and deploys main through GitHub Pages.
- `docs/ARCHITECTURE.md`: historical architecture/regression context; reevaluate stale statements when affecting those areas. `docs/PROFILING.md` / `docs/DIAGNOSTICS.md`: matched TV profiling and diagnostics; `docs/THIRD_PARTY.md`: attribution; `docs/DANCE-COLLECTION.md` and guide `dance-measurement.md`: collection protocol.
- `docs/RELEASING.md`, `.github/pull_request_template.md`, `RELEASE_NOTES.md`: release procedure, PR obligations and historical archive respectively.
- `tools/preset-lab/README.md`, `tools/core-corpus/README.md` and `docs/superpowers/evidence/`: analysis setup, actual-core validation and task evidence. Preserve immutable raw identities and distinguish historical records from reproduced measurements. No per-locale documentation ownership process is documented.

Evaluate these sources for every affected change under the mandatory rule below; keep extended research in evidence/docs rather than expanding this file with benchmark transcripts.

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
