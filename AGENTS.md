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

On the next implementation task, inspect the ProjectM TV repository and populate the repository-specific sections below in the same isolated worktree and PR as the requested work. Repeat this discovery whenever relevant context is missing or has changed. This is part of the task and does not require a separate request to edit `AGENTS.md`.

1. Read existing instructions, `README.md`, the user guide and any Pages sources, `.github/pull_request_template.md`, `docs/RELEASING.md`, `app/build.gradle`, dependency manifests and lockfiles, build scripts, CI workflows, and release tooling. Inspect the actual code structure and entry points. Preserve the contributor rules above while populating the missing context.
2. Replace the repository-specific population instructions with concise, concrete guidance supported by repository files, installed/resolved dependency versions, official documentation, or observed command results. Preserve the section structure when useful; mark genuinely inapplicable sections with a brief reason.
3. Describe the project's purpose, supported platforms, current architecture, and identifiers. Record exact paths, commands, variants, environment prerequisites, documentation location, and important invariants. Distinguish verified facts from unresolved details and recorded technical debt.
4. Validate commands before describing them as working. If the environment prevents validation, state the missing prerequisite and the unverified command explicitly. Do not add dependencies or tooling solely to fill this file.
5. Preserve useful existing project rules while replacing instructions that conflict with the mandatory workflow or documentation precedence below. Do not import assumptions from another repository or copy its framework versions, package names, file budgets, or device requirements.
6. Maintain the populated guidance whenever a task changes architecture, commands, dependencies, documentation, or constraints. Keep it concise and actionable; put extended explanations in linked documentation.

Do not stop at proposing customization. Complete the applicable population work as part of implementation. A populated `AGENTS.md` is subject to the same validation, PR, and Codex review requirements as any other change. Until discovery is complete, these sections are instructions to populate, not claims about the current implementation.

## Repository overview

ProjectM TV produces an Android APK and a core AAR consumed by Milkbeat through the automatic release/update workflow described above. These are supplied contributor facts; verify their implementation during repository discovery.

Populate with the app purpose, application ID and namespaces, primary languages/frameworks, projectM upstream/fork relationship, supported Android versions and device types, build variants, and important entry points. Identify the app/core boundary and Milkbeat integration. Record exact build tasks rather than assuming Milkbeat’s stack or flavor names apply here.

## Codebase navigation and knowledge tools

Populate with the source/module map, architecture documentation, and existing code search or knowledge graph tools. Record when generated indexes must be refreshed and whether their outputs are committed. If a graph tool such as graphify is already configured, record its verified commands and freshness rules; otherwise use ordinary code search and do not assume a graph exists.

## Design and user experience

Follow the project's established design system and platform conventions. Reuse existing theme tokens and components. Preserve accessibility, keyboard/focus behavior, responsiveness, and supported input methods. Avoid introducing decorative styles or changing appearance incidentally during a refactor.

Populate with the actual UI toolkit and design system, theme/component locations, TV remote and D-pad focus/navigation contracts, supported layouts, accessibility requirements, approved visual patterns, and official references. Verify any additional touch/keyboard support; do not assume Jetpack Compose or Material 3 is used.

## Use existing platform and dependency APIs

Before implementing a component, parser, formatter, scheduler, transport, or similar utility:

1. Check existing project code for a suitable implementation.
2. Check the declared and resolved dependencies for a supported API.
3. Verify the API and recommended usage against the version in use and official documentation.
4. Implement a custom alternative only when the existing options are absent or unsuitable, and record the reason in the PR.

Prefer configuration, composition, or a small wrapper to copied library source or overlapping dependencies. Use maintained implementations for security-sensitive primitives.

Populate with a compact table of common needs, preferred APIs/dependencies, their source of version truth, and important constraints. Keep version information current rather than copying versions from another project.

## Performance and resource use

Avoid blocking work on latency-sensitive threads, unnecessary polling, duplicate requests, unbounded concurrency, and background work that outlives its owner. Honor existing cache, cancellation, visibility, lifecycle, and resource-release contracts. Back performance claims with measurements and state what was not measured.

Populate with the actual rendering/audio paths, render-thread ownership, visibility and pause behavior, frame pacing, resource cleanup, and relevant CPU/GPU/memory/thermal constraints. Record established budgets, benchmark or frame-capture commands, representative preset/audio workloads, device coverage, and measured regression lessons. Do not invent performance targets or claim improvements without evidence.

## Dependencies, state, and lifecycle

Follow the existing dependency injection and ownership model. Prefer explicit dependencies and testable boundaries. Preserve instance identity, initialization timing, lifecycle, cancellation, and cleanup when refactoring. Keep migrations focused on the task and avoid creating duplicate services, caches, clients, or background workers.

Populate with actual dependency injection conventions, state ownership, service scopes, persistence and schema migration rules, sensitive initialization paths, and the validation required when these change.

## User-facing text and localization

Use the project's established resource or localization mechanism for user-facing text. Follow its locale ownership and translation workflow; do not invent an English-only or all-locales policy.

Populate with resource paths, string naming rules, locale update requirements, and formatting/accessibility conventions. Mark inapplicable where appropriate.

## Code structure and modularization

Place code according to its responsibility and actual consumers. Reuse shared code when appropriate without creating speculative abstractions. Split oversized or mixed-responsibility files along meaningful boundaries. Preserve behavior during refactors and remove obsolete code.

Populate with a source/module placement table covering the app, core library, native code and bindings if present, tests, presets/assets, documentation, and release scripts. Record visibility and naming conventions, generated-code boundaries, representative patterns, and any established size limits. Do not impose arbitrary file budgets.

## Repository-specific constraints

Preserve the release/version rules above. Treat the core AAR’s interface and compatibility with Milkbeat as an integration boundary; verify the actual API and consumers before changing it.

Populate with verified public API/ABI compatibility rules, dependency/native-library requirements, supported runtime versions, preset/asset constraints, upstream attribution and licensing requirements, and any protected or generated files. Record the procedure for deliberate incompatible changes. These constraints cannot waive the mandatory documentation evaluation rule below.

## Formatting and linting

Follow the repository's configured formatting and lint rules. Review automatic formatting changes and avoid unrelated churn. Fix violations rather than disabling checks to obtain a passing result.

Populate with exact check/format commands, their working directories, configuration files, target paths, incremental/ratchet behavior, and CI equivalents.

## Building and testing

Choose validation that exercises the changed behavior. Compilation alone does not establish functional correctness. For UI or integration changes, exercise relevant user journeys and error paths when the environment supports them. Record baseline failures and environmental limitations honestly.

For release tooling changes, the required check is:

```bash
python3 -m unittest discover -s .github/scripts/tests -v
```

Populate with the repository’s exact setup, APK and core AAR build tasks, app/core unit and integration tests, native tests if present, device/emulator journeys, and documentation checks. Derive required Android SDK/NDK, JDK, Gradle, native toolchain, variants, and device coverage from repository files and CI. Identify relevant rendering, preset-loading, audio, lifecycle, and Milkbeat integration checks, and when each applies. State unavailable prerequisites and unverified coverage honestly.

## Generated artifacts and release preparation

A successful tested merge to `main` triggers the versioned APK/core AAR release and Milkbeat update. Routine PRs must not manually bump the base version/code/commit. Follow `docs/RELEASING.md` for a planned new release line.

Populate with the exact CI workflow names and triggers, artifact locations, version calculation, signing prerequisites without secret values, publication destinations, Downloader code ownership, canonical README install blockquote, and Milkbeat update mechanism. Record generated outputs, regeneration commands and triggers, and what is committed. Verify release automation from its implementation rather than assuming details.

## Documentation map

Known contributor references are `README.md`, its canonical install blockquote, `docs/RELEASING.md`, and `.github/pull_request_template.md`; verify their current content and roles. Populate with the user-guide location, any Pages/GitHub Pages URL and source paths, other Markdown entry points, documentation build/publishing workflow, and source ownership. State verified absence where appropriate. Do not invent a guide or Pages site. The mandatory evaluation rule below applies before and after this map is populated.

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
