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

## Bootstrap and maintain this file

Repository guidance below was checked against the source and workflows on 2026-10-04. Maintain it when architecture, commands, dependencies or constraints change. Read the source of truth before repeating historical measurements; `docs/ARCHITECTURE.md` contains older verification tables and does not establish current device coverage.

Keep regular committed and pushed checkpoints. Back up ignored measurement data with source/input identities, checksums and explicit partial coverage. Honor session-specific device permissions and never remove worktrees when the user has prohibited removal.

## Repository overview

ProjectM TV visualizes audio played by another Android TV app; it is not a music player. The app uses Java framework Views, with C++17 JNI and patched projectM 4.1.7. Android API 21+, GLES 3.0 and Leanback are required; phones/touch are not supported. `app/build.gradle` defines installed ID `nl.neerdael.projectmtv` and Java namespace `com.example.projectm.visualizer`. `core/build.gradle` defines `nl.neerdael.projectm.core`, ARMv7/ARM64 and the reusable AAR.

`MainActivity` owns audio, controls and track display; `VisualizerView`/`VisualizerRenderer` in `:core` own GL rendering. Both modules have debug/release builds; `:app` also has a profile build. Milkbeat consumes the released core AAR; its integration is described in `docs/RELEASING.md`.

## Codebase navigation and knowledge tools

Use the module map below and `docs/ARCHITECTURE.md`. No `.codegraph/`, `.code-review-graph/graph.db` or `graphify-out/graph.json` is present in this task checkout; use ordinary file/content search. Do not assume a generated graph or add indexing merely to satisfy documentation.

`tools/projectm-patches/` is the source of engine changes; `third_party/projectm` is a pinned submodule, not an independently maintained production backend. CMake applies patches in lexical order while holding `core/.cxx/projectm-patches.lock`.

## Design and user experience

Use Android framework Views and `app/src/main/res/layout/activity_main.xml`; no AndroidX, Compose or Material dependency is declared. Reuse `values/{colors,dimens,styles,themes}.xml`, overlay drawables, `OptionRow` and `TrackCorner`. Preserve D-pad focus, visible focus backgrounds, marquee behavior and overscan margins. Main/Track display/Advanced panels have distinct Back navigation. See `docs/user-guide/controls.md` and `settings.md`; exercise remote journeys for UI changes. Do not introduce touch/phone support incidentally.

## Use existing platform and dependency APIs

Check existing code and the resolved dependency version before adding an implementation. Use maintained platform primitives for sensitive operations; verify newly used APIs against official documentation.

| Need | Existing choice / source of truth |
|---|---|
| TV UI, preferences, scheduling | Framework Views, SharedPreferences, Handler/HandlerThread; Java sources in `app` and `core` |
| Audio | Android `audiofx.Visualizer`, `PlayerSessionFinder`; `MainActivity` |
| Native rendering | EGL/GLES3, static patched projectM, JNI; `core/src/main/cpp/CMakeLists.txt` |
| JVM tests | JUnit 4.13.2; module Gradle dependency declarations |
| Offline analysis | NumPy/OpenCV; `tools/preset-lab/pyproject.toml`, pinned CI versions in `requirements.lock` |
| User guide | MkDocs 1.6.1; `docs/site-requirements.txt` |

The Android Gradle plugin is 8.12.0 (`build.gradle`) and wrapper is 8.14.2 (`gradle/wrapper/gradle-wrapper.properties`). Python analysis requires 3.11+; CI uses 3.14. Do not confuse the wrapper's bundled Kotlin with an app Kotlin dependency.

## Performance and resource use

Keep GL work on the GLSurfaceView render thread, including `VisualizerRenderer.release()`. Audio Visualizer calls run on `MainActivity`'s AudioCapture HandlerThread; JNI accepts waveform bytes, with native PCM analysis bounds. Preserve `VisualizerView` pause/resume pacing and Choreographer ownership. `QualityController.RENDER_HEIGHT_CAP` is 1330; device/memory-dependent floors and caps come from `DeviceProfile` and `QualityController` rather than historical documentation tables.

Use `docs/PROFILING.md` and `DIAGNOSTICS.md` for workload/device measurements. Rendering fixes require per-fix captures and relevant TV measurements. Do not wake a TV remotely; respect authorized devices and clear `debug.projectmtv.*` after tests. Rooted hardware is not assumed.

For the current corpus, use actual `projectm-tv:core` through production JNI as documented in `docs/superpowers/evidence/quad-follow-up-verification/core-corpus/PROTOCOL.md`; direct-engine host experiments are supplementary. Preserve protocol identities, repeat renders, classic 1182×665 reference hashes and authored size-band controls. Brightness/thumbnail error alone does not establish fidelity or settings labels.

## Dependencies, state, and lifecycle

Dependencies use direct constructor/context ownership; no dependency-injection framework is declared. `MainActivity` persists settings in SharedPreferences and marshals render changes to GL. `Updater` is application-scoped through `get()` and attaches/detaches its UI listener; preserve its pause/scheduling and APK verification contracts. Audio state belongs to the audio thread; release the Visualizer and stop callbacks on lifecycle transitions. `ProjectMCore`/`ProjectMJNI` are the app/core boundary. Core changes involving initialization, prewarm, memory pressure or context recreation need relevant JVM/native and actual-core checks. No database migration framework is configured.

## User-facing text and localization

Resources live in `app/src/main/res/values/strings.xml`; only the base `values` locale directory is present. Some existing dynamic labels are Java literals in `MainActivity`; there is no declared translation automation or all-locales policy. Prefer existing resource mechanisms for new user-facing text, preserve placeholders and content descriptions, and keep guide/README terminology aligned with visible controls. Do not claim full localization coverage.

## Code structure and modularization

| Responsibility | Location |
|---|---|
| TV activity, audio/session search, track overlay, updater | `app/src/main/java/com/example/projectm/visualizer/` |
| App UI/manifest/assets | `app/src/main/{res,AndroidManifest.xml}` |
| Reusable renderer/JNI/quality/device API | `core/src/main/java/nl/neerdael/projectm/core/` |
| Native engine, prewarm and snapshot fade | `core/src/main/cpp/` |
| projectM changes | Ordered patches in `tools/projectm-patches/` |
| JVM, native and app instrumentation tests | Module `src/test/` and `app/src/androidTest/` |
| Presets, textures, generated index/category assets | `core/src/main/assets/` |
| Offline analyzer | `tools/preset-lab/` |
| Release tooling/tests/workflows | `.github/scripts/`, `.github/scripts/tests/`, `.github/workflows/` |
| User guide / evidence / architecture | `docs/user-guide/`, `docs/superpowers/evidence/`, `docs/ARCHITECTURE.md` |

Split code by actual responsibility/consumers; no fixed file-size budget is configured. Keep generated build products and user audio/raw captures out of Git. Preserve byte-exact preset/evidence inputs when whitespace is meaningful.

## Repository-specific constraints

Change projectM via patch files, never commits inside `third_party/projectm`. Preserve patch attribution and series order. The submodule is 4.1.7 at `e0b0a967` with projectm-eval nested below it; see `docs/THIRD_PARTY.md` for LGPL and asset provenance. `tools/check-presets.py` protects the curated corpus and texture exclusions; `tools/gen-preset-index.py --check` checks the generated index.

Preserve `ProjectMJNI` names/signatures and `core/consumer-rules.pro` when changing the published AAR; audit downstream Milkbeat use for deliberate API/ABI changes. No separate incompatible-API migration procedure is documented: make the compatibility decision explicit in the PR rather than assuming consumers update safely. NDK ABIs and minimum SDK are defined in `core/build.gradle`.

## Formatting and linting

No standalone formatter or lint ratchet configuration was found in the inspected module/tool manifests. Match surrounding Java/C++/Python style; run `git diff --check`. Android lint is available through Gradle, but this documentation-only/tooling change does not establish a clean project-wide lint baseline. CI runs release-note validation, index/preset checks, native/JVM tests and Preset Lab tests; use the relevant checks below without unrelated formatting churn.

## Building and testing

Run commands from the isolated repository root. Android builds require JDK 21 (CI), SDK platform 34, NDK 27.3.13750724 and CMake 3.22.1; configure SDK via `local.properties` or the normal Android SDK environment. Initialize recursive submodules before native builds. The local wrapper was verified as Gradle 8.14.2 on JDK 21.0.11.

| Scope | Command / coverage |
|---|---|
| Android JVM | `./gradlew testDebugUnitTest` locally; CI uses `./gradlew testReleaseUnitTest --no-daemon` |
| APK / AAR | `./gradlew :app:assembleDebug :core:assembleDebug`; CI `./gradlew assembleRelease --no-daemon --stacktrace` |
| Native app/regressions | `bash core/src/test/native/run_native_tests.sh`; ASan/UBSan, JDK/CMake/compiler, Linux EGL/GLES or macOS OpenGL; report skips |
| projectM host GTest | `bash tools/projectm-host-tests.sh`; requires patched submodule, CMake/Ninja/GTest; host evidence does not replace Android |
| Patch application | `bash tools/check-patch-series.sh`; clean export of pinned submodules |
| Release tooling | `python3 -m unittest discover -s .github/scripts/tests -v` |
| Corpus host tools | `build/preset-lab-venv/bin/python -m unittest discover -s docs/superpowers/evidence/quad-follow-up-verification/core-corpus -p 'test_*.py' -q` |
| Preset Lab | `python -m pytest tools/preset-lab/tests`; CI splits `-m 'not native'` and `-m native` under Xvfb |
| User guide | `mkdocs build --strict` with `docs/site-requirements.txt` installed |

The corpus host suite passed 120 tests after the capture-provenance fix. Build commands in the table are declared by source/CI, not a claim of fresh APK/device validation for every docs-only change. Existing virtual environments are task-local prerequisites, not committed dependencies. For Android category/audio journeys, use the separate `.presettest` package and instrumentation command in `docs/user-guide/development.md`; live audio requires an authorized device/music source. Core-corpus pilots and scans have their own protocol/package, not that category instrumentation runner.

## Generated artifacts and release preparation

`Android CI/CD` (`.github/workflows/android.yml`) runs tests/builds on PRs and pushes. Tested main commits publish APK/core AAR and dispatch Milkbeat; `PR release notes` checks PR text. Source-history version calculation lives in `.github/scripts/release_version.py`; publication and `projectm-core-release` dispatch in `publish_release.py`. Baseline version/code/commit in `app/build.gradle` change only for planned release lines. No prerelease policy is introduced here.

APK output is `app/build/outputs/apk/`; AAR is `core/build/outputs/aar/core-release.aar`. CI publishes versioned and stable `projectM-TV.apk` / `projectM-TV-core.aar` aliases, checksums and R8 mapping. Release signing uses configured environment secrets; missing release signing must prevent publication. Milkbeat dispatch needs its configured token; never print credentials. CI appends install details from the canonical README Downloader blockquote.

`tools/gen-preset-index.py` regenerates the committed preset index; CI uses `--check`. Keep `build/`, `.cxx/`, APKs and raw measurement outputs untracked; use checksummed evidence archives/backup branches for large task data. Frozen corpus `run.py` and protocol hashes must not be edited/retagged while a scan is running; new behavior uses a new runner/protocol.

## Documentation map

| Source | Purpose |
|---|---|
| `README.md` | App behavior, install/Downloader blockquote, developer entry point |
| `docs/user-guide/` + `mkdocs.yml` | Guide sources deployed to `https://johnneerdael.github.io/ProjectM-TV/` |
| `docs/ARCHITECTURE.md` | Rendering/audio/UI architecture; distinguish historical verification from current evidence |
| `docs/RELEASING.md` | Version calculation, signing, releases, core AAR and Milkbeat |
| `docs/PROFILING.md`, `docs/DIAGNOSTICS.md` | Device measurements and diagnostics |
| `docs/THIRD_PARTY.md` | Engine/asset attribution and licenses |
| `tools/preset-lab/README.md` | Offline analyzer dependencies/protocols |
| `docs/superpowers/evidence/quad-follow-up-verification/` | Per-fix proof, actual-core corpus protocols, current research limitations |

`User guide` workflow validates MkDocs and deploys main changes with GitHub Pages. Generated site goes to `build/user-guide-site`; edit Markdown/config sources, not generated HTML. Apply the mandatory documentation evaluation rule below to every change, including internal evidence tooling.

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
