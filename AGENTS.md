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

Maintain repository-specific guidance when architecture, dependencies, commands or documented behaviour changes. Verify facts against the current worktree and resolved dependencies. Preserve the contributor and mandatory workflow rules. Keep extended reasoning in the linked documentation. Record unverified commands and environmental limits explicitly.

## Repository overview

ProjectM TV visualizes other apps’ music on Android TV; it is not a music player. The Java framework UI is in :app; reusable rendering/audio Java APIs, JNI, native projectM and assets are in :core. Installed ID: nl.neerdael.projectmtv; app namespace: com.example.projectm.visualizer; core namespace: nl.neerdael.projectm.core. Both modules declare minSdk21/compileSdk34; app targetSdk34. The manifest requires Leanback and GLES3 and does not require a touchscreen or microphone. The engine is the pinned third_party/projectm submodule plus tools/projectm-patches; current developer docs identify upstream4.1.7. Verify versions from build files rather than historical architecture text.

## Codebase navigation and knowledge tools

Start at app/src/main/java/com/example/projectm/visualizer/MainActivity.java, core/src/main/java/nl/neerdael/projectm/core/{ProjectMCore,VisualizerView,VisualizerRenderer,ProjectMJNI}.java and core/src/main/cpp/native-lib.cpp. docs/ARCHITECTURE.md and docs/PROFILING.md contain design/history and device procedures; some historical architecture version/toolchain statements are stale. No .codegraph, .code-review-graph or graphify-out index exists in this worktree; use ordinary file/content search. tools/milk-analyzer/README.md describes the source predictor and evidence formats; tools/preset-lab/README.md describes the rendering lab.

## Design and user experience

Use the existing framework Activity/View widgets, OptionRow and TrackCorner. Theme.Leanback in app/src/main/res/values/themes.xml derives from Android’s fullscreen black theme; it is not an AndroidX Leanback dependency. Preserve D-pad Left/Right preset changes, Up/Down/Center/Menu panel navigation and Back behaviour documented in docs/user-guide/controls.md. Reuse theme/resource conventions and maintain focus/accessibility rather than changing appearance during internal work. Touch/keyboard journeys require explicit verification; TV remote behaviour is the established interface.

## Use existing platform and dependency APIs

Before adding utilities, inspect project code, declared/resolved dependencies and version-matched official APIs. Prefer supported APIs or a small wrapper; document why a custom implementation is necessary. App/core use Android framework APIs and JUnit4.13.2, with no AndroidX/Compose dependency declared. AGP8.12.0 is in build.gradle; Gradle8.14.2 is pinned with checksum in gradle/wrapper/gradle-wrapper.properties. Preset Lab Python dependencies are pinned in tools/preset-lab/requirements.lock; package requirements are in pyproject.toml. MkDocs1.6.1 is pinned in docs/site-requirements.txt. The Milk analyzer intentionally preserves pinned EEL/shader semantics using source adapters; these are not generic replacements for available parsers.

## Performance and resource use

VisualizerRenderer owns GL work; use GLSurfaceView.queueEvent for context-dependent operations. VisualizerView and MainActivity coordinate pause/resume/release. native-lib.cpp owns command/audio handoff and background preset preparation. Preserve framebuffer feedback, audio capture, cached/prepared presets, adaptive resolution, skip rules and cancellation/resource ownership. Use docs/PROFILING.md for representative TV comparisons; desktop/emulator evidence does not establish TV performance. Do not invent fps/memory budgets or broad equivalence from a single control.

## Dependencies, state, and lifecycle

MainActivity persists settings in SharedPreferences. ProjectMCore/View/Renderer and JNI divide app state from rendering ownership; there is no declared external DI framework. TrackWatcher/TrackListenerService manage media sessions and notification access; Updater/UpdateFileProvider own optional update flow. Preserve initialization order, GL-thread release, observer cleanup and preset/audio handoff. Lifecycle, audio or state changes require corresponding JVM/instrumentation/device checks. No database migration framework is declared.

## User-facing text and localization

Use app/src/main/res/values/strings.xml and existing resources. This worktree has only the values resource directory and no translated values-* folders; no all-locales policy is inferred. Preserve labels, focus hints, accessibility descriptions and formatting. Update the user guide when settings or setup text changes.

## Code structure and modularization

Place app UI/settings/update code under app/src/main; reusable APIs and native renderer under core/src/main; JVM tests under each module’s src/test and device tests under app/src/androidTest. core/src/main/assets/presets and preset-genres hold shipped presets/indexes; generate/check the master index with tools/gen-preset-index.py. Change projectM through tools/projectm-patches/*.patch, never commit modified submodule sources. Keep offline lab/predictor code in tools/preset-lab and tools/milk-analyzer; generated caches/raw audio/captures stay under ignored build/. Documentation sources are docs/user-guide and mkdocs.yml; release tooling is .github/scripts. No arbitrary file-size limit is imposed.

## Repository-specific constraints

Core public APIs and the AAR are consumed by Milkbeat; verify consumers before changing Java/JNI/native compatibility. Android CMake uses C++17, GLES3/EGL and ARMv7/ARM64. Preserve preset filenames, authoritative memory weights, asset checksums and upstream/licence attribution in docs/THIRD_PARTY.md. Do not commit user audio/raw captures, credentials, build caches or patched third_party sources. Scope review builds separately: -PaudienceReview=true is Debug-only, uses a hash-pinned published AAR and complete score assets; it refuses incomplete exports and cannot be described as production-ready until those inputs exist.

## Formatting and linting

Follow existing Java/C++/Python/XML conventions; no standalone formatter/type-check configuration was found for the analyzer. Run git diff --check for changed files. Android lint tasks are available through AGP but were not validated during this documentation bootstrap. CI checks preset indexes with tools/gen-preset-index.py --check and tools/check-presets.py. Do not disable checks or introduce unrelated reformatting.

## Building and testing

Use JDK21 as CI does, SDK platform34, NDK27.3.13750724 and CMake3.22.1; retain the Gradle wrapper. Clone submodules recursively. ./gradlew testDebugUnitTest runs app/core JVM tests and passed during the 2026-10-04 bootstrap. Gradle reported a stale checked-in sdk.dir but resolved the SDK through the environment; keep any local path correction uncommitted. APK/AAR build tasks are ./gradlew :app:assembleDebug and :core:assembleRelease. Full native/Android assembly has not been freshly validated by this bootstrap; do not call it passing from documentation alone. Native tests: bash core/src/test/native/run_native_tests.sh (CMake/JDK and host GL/EGL prerequisites). Release tooling: python3 -m unittest discover -s .github/scripts/tests -v. Analyzer: build/preset-lab-venv/bin/python -m pytest tools/milk-analyzer -q, after building its CMake source adapters per its README. Preset Lab: python -m pytest tools/preset-lab/tests -m "not native" -q; native marks need a verified worker. Device test/build and permission steps are in docs/user-guide/development.md. Use an explicitly authorized serial/owned emulator; do not operate other agents’ devices. Raw interpretation coverage is not visual accuracy or a complete intensity ranking.

## Generated artifacts and release preparation

.github/workflows/android.yml (Android CI/CD) runs native/JVM/release-tool tests and builds APK/AAR artifacts. Successfully tested main revisions publish through release_version.py, release_notes.py and publish_release.py, then the milkbeat job dispatches the core update. Signing secrets are required for publishing; never expose their values. Version floors/code/base commit live in app/build.gradle and are unchanged for routine PRs. Outputs originate in app/build/outputs/apk/release and core/build/outputs/aar; CI attaches versioned and stable assets/checksums. README’s install blockquote owns the Downloader code. Preserve core/src/main/assets/presets.idx and generated genre indexes through their documented generators. Experimental predictor fixtures record source/runtime hashes; do not silently splice incompatible measurements or label missing results as ranked.

## Documentation map

README.md is the default project/install entry point; docs/RELEASING.md and .github/pull_request_template.md define release workflow. docs/user-guide/*.md plus images/styles and mkdocs.yml generate https://johnneerdael.github.io/ProjectM-TV/. docs/site-requirements.txt pins the site tool. .github/workflows/docs.yml validates PRs and deploys main changes through Pages. build/docs-env/bin/mkdocs build --strict was validated in this worktree; output is ignored build/user-guide-site. docs/ARCHITECTURE.md and docs/PROFILING.md cover history/performance; docs/THIRD_PARTY.md covers attribution. tools/milk-analyzer/README.md and dated docs/superpowers/evidence explain experimental predictions and limits. A user guide/Pages site exists and must be evaluated for affected changes.

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
