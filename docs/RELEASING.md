# Builds & Releases

## Automatic publishing

The **Android CI/CD** workflow tests and builds pushes to `main`. **Reviewed PR validation** runs the full suite for eligible PRs targeting `main`. Each successfully tested merge to `main` publishes a stable GitHub Release with its signed APK, Native core AAR, public release notes and SHA-256 checksums, then triggers Milkbeat's core update. Routine PRs need no version bump or manual release command.

| Trigger | Result |
|---|---|
| Feature-branch push, or PR targeting another branch | No builds |
| PR targeting `main`, awaiting current review or unresolved findings | Lightweight review gate only; full builds wait |
| Reviewed, ready PR targeting `main`, with all findings resolved | Release tooling, native/JVM, Preset Lab and documentation checks; APK and one Native core AAR artifact with a `-ci.<run>` version suffix |
| Successful merge/push to `main` | Stable APK/Native core AAR, GitHub Release, PR notes, current download details, checksums and Milkbeat dispatch |
| Manual run on `main` | Publishes an unreleased commit or verifies an already complete release; the same commit keeps its version |

Main publishing runs queue instead of canceling previous builds. Obsolete PR validation runs are canceled when a new revision arrives or review eligibility is lost. Versions are tied to source history rather than workflow order: the first first-parent commit after `baseVersionCommit` maps to `baseVersionName`/`baseVersionCode`, and each later commit advances both. The historical 2.1 line started at **2.1.5 / code 37**, and the 2.2 line at **2.2.0 / code 38**. The user-planned Native checkpoint starts the **2.3.0 / code 49** line, anchored to `8b70620339018cfaf5ac05acdb4ea8104dc2eb59` (main before this checkpoint). The first first-parent commit after that anchor receives the base triple; later commits advance it. This is a deliberate minor-release-line change, not a routine PR version bump. Direct pushes containing several commits can leave version gaps; failed builds leave their version unpublished.

CI fetches full tag history and rejects conflicting tags, inconsistent retry metadata and invalid Android codes. An older retry does not replace a newer release as latest. Missing release signing fails a publishing build; PR artifacts may use a temporary debug key.

## Review gate

A ready, mergeable PR targeting `main` needs at least one completed review of its **latest head commit**, identified by an exact 40-character SHA match. Either a submitted Codex code/security review, Codex's authenticated completion summary/comment identifying that commit, or an approving/comment-only review from another repository owner, member or collaborator qualifies. An author self-review, arbitrary comment, reaction, stale review or dismissed review does not qualify. Codex completion summaries and legacy comments must carry a full 40-character SHA; abbreviated text alone cannot qualify the PR or satisfy an outstanding Codex request. A submitted Codex review must contain its code/security review body and provide the full SHA through its API `commit_id`; empty review records created by unrelated bot replies do not count. If Codex publishes only abbreviated text without a submitted review, Codex-only qualification remains pending until unambiguous full-SHA evidence is available. A current or ambiguously abbreviated Codex summary still showing work in progress keeps the gate closed even when another review has finished.

All review threads, including outdated threads, must be resolved. Outstanding review requests, any pending review exposed by the API, authorized `@codex review` or `@codex security review` requests awaiting subsequent completion, and outstanding changes-requested decisions also block builds. An explicit Codex command requires a completion for the current head, even when a human has also reviewed it; completions for older commits never clear the request. After a new push, retained commands require a new current-head Codex completion. Codex request commands use the comment's latest update time (creation time only if no update time is available), so editing an old comment into a review command requires a new completion after that edit. A comment-only follow-up does not clear a changes-requested decision: the reviewer must approve or the decision must be explicitly dismissed. Express blocking findings as review threads or a changes-requested review; free-form issue comments do not have a GitHub resolution state.

GitHub hides another reviewer's private draft review and its unpublished comments from the controller. The gate cannot detect arbitrary unrequested private drafts. Request the reviewer on the PR to keep the gate closed until submission; published unresolved threads and changes-requested decisions remain blocking signals.

The **PR review gate** workflow reads trusted `main` code and dispatches **Reviewed PR validation** on `main`. An unprivileged **PR review signal** relays review events through `workflow_run`; PR/comment/main-push events prompt trusted-main rechecks; a five-minute schedule also checks thread resolution and Codex comment updates because thread resolution has no native Actions trigger. Scheduled runs can be delayed by GitHub. The gate records a `Reviewed PR builds` status on the PR head, remaining pending until eligibility and the full suite pass. Configure the `main` ruleset to require this status from GitHub Actions, retain resolved-thread enforcement, and require the branch to be up to date. The completed-review minimum is enforced by the gate; the separate GitHub approving-review count remains zero so Codex completion can satisfy this policy.

Validation builds an immutable test merge of the reviewed head and current `main`. It rechecks review eligibility and both revisions before starting and after all jobs finish. Android/native tests, Preset Lab and the documentation build must actually succeed; skipped jobs cannot produce a passing status. A new main revision requires a new test merge and validation. PR code receives no signing/publishing secrets or write-capable repository token, and cannot access build caches (`cache-mode: none`, enforced by GitHub's scoped cache token). Publishing and Pages deployment run only in the main pipeline, after all builds pass.

When all builds succeed but the final review check becomes ineligible, the status stays pending. Once review eligibility recovers for the same revision, the controller automatically starts fresh validation; scheduled rechecks do not mark those successful builds as failed. A preflight error that starts no build jobs also keeps the gate pending and retryable; the next eligible controller check dispatches fresh validation. Skipped jobs following a successful preflight remain a failure, and this retry path cannot report success without actual builds. Actual failed validation is not automatically retried every five minutes. Fix the PR and obtain a new review, rerun its failed validation workflow, or run **PR review gate** manually with `pr_number` and `retry_build=true`. A manual validation dispatch still has to pass preflight; selecting a feature branch in the manual build workflows skips the builds.

The lightweight **PR release notes** validator continues to check PR text before review. It does not compile or publish artifacts.

## Writing PR release notes

Use `.github/pull_request_template.md` and `AGENTS.md`. Include a substantive `## Release notes` section describing concrete changes, their effects and material limits for app users. Keep it aligned with the final diff. Put tests and implementation process in `## Validation`, outside public notes.

For changes with no user-visible effect, use an `Internal` subsection and explain the change. A bare “No user-visible changes”, `N/A`, empty bullets or `TODO` placeholders fail validation. The **PR release notes** check runs again when the PR body is edited. CI checks structure; reviewers check factual accuracy and writing quality.

The workflow collects merged PR sections since the previous reachable version tag. Historical PRs before this automation use their existing change descriptions without validation/checklist/badge sections. Direct commits use their actual descriptions. The generator does not invent claims or use an external AI service.

CI appends install/download information. The canonical Downloader code comes from the install blockquote in `README.md`; update it when the code changes. Notes include stable/latest and versioned APK/core URLs, checksums, the user guide and the comparison link. `RELEASE_NOTES.md` remains a human-readable archive rather than being copied into unrelated releases.

## Versions and tagged builds

`app/build.gradle` holds literal `baseVersionName`, `baseVersionCode` and `baseVersionCommit` values. Keep them unchanged for routine PRs. For a planned major/minor line change, update all three together: the desired first version, a code above the latest released code, and the current `main` commit before that change. Tests verify the sequence.

CI passes `PROJECTM_RELEASE_VERSION` and `PROJECTM_RELEASE_VERSION_CODE` to Gradle. Local builds default to the baseline. To reproduce a tagged release's version metadata after checking out that tag and fetching tags:

```bash
python3 .github/scripts/release_version.py --repo . --sha HEAD \
  --event workflow_dispatch --ref refs/heads/main --run-number 1 \
  --output /tmp/projectmtv-version-output --env /tmp/projectmtv-version-env
set -a
. /tmp/projectmtv-version-env
set +a
./gradlew assembleRelease
```

Signing still requires the configured release key; locally debug-signed builds cannot update an installed stable release.

## Downloads and core library

The Downloader code shown in README and the fixed APK URL serve the newest stable build:

- [Latest APK](https://github.com/johnneerdael/ProjectM-TV/releases/latest/download/projectM-TV.apk)
- [Latest Native core AAR](https://github.com/johnneerdael/ProjectM-TV/releases/latest/download/projectM-TV-core.aar) (canonical integration download)

New releases attach `projectM-TV-<version>.apk`, `projectM-TV-core-<version>.aar`, `projectM-TV-<version>-mapping.txt` and `checksums.txt`, plus the fixed APK/core names above. The canonical versioned and fixed-name core files contain the same Native-capable AAR built with the APK. It contains the public Java/JNI API, native ARMv7/ARM64 libraries and presets, and shares the app version. There is one `:core` module and one published core artifact; separate capped and `core-native` artifacts are retired for new releases.

The app uses Standard Native trails and always-automatic resolution up to the detected panel size. Target FPS and live memory headroom determine the current size; fixed-resolution selection and the manual RAM limiter are removed. GPU, memory and picture limits still apply; publication does not establish universal device performance or fidelity acceptance.

Build with `./gradlew :core:assembleRelease`; the optional legacy spelling `-PprojectmCoreRenderingPolicy=native` remains accepted. `-PprojectmCoreRenderingPolicy=capped` now fails with a migration message, as does `-DPROJECTMTV_RENDERING_POLICY=capped` for direct CMake configuration. `RenderingPolicy.NAME` remains `native` and `RenderingPolicy.NATIVE_ENABLED` remains `true` for consumers. The release workflow stages `core/build/outputs/aar/core-release.aar` once under the canonical filename and records a checksum for every published APK, AAR and mapping filename.

Historical published releases and tags remain immutable, including releases with a capped canonical core and separate Native aliases. A retry verifies completeness, tag ownership and versioned/alias digest agreement where GitHub provides digests, then returns without replacing assets or checksums. Retired local Native aliases are not required for that retry. A pre-existing draft containing retired `core-native` assets is rejected for maintainer reconciliation rather than published with a mixed schema.

The release APK is shrunk, optimized and obfuscated by R8, so Java stack traces from it show short class and method names. Each release also attaches `projectM-TV-<version>-mapping.txt` (CI builds keep it in the `mapping` artifact). F-Droid rebuilds the same source reproducibly, so the mapping fits its APK too. Restore the names with the SDK's `retrace` tool:

```sh
retrace projectM-TV-<version>-mapping.txt crash.txt
```

`retrace` is in the Android SDK command-line tools (`cmdline-tools/latest/bin`). Native crashes (`Fatal signal`) are not affected.

Publication creates or resumes a draft, uploads every artifact, then publishes it. A retry verifies the tag points to the expected commit and leaves a complete published release unchanged.

## Milkbeat follows each core release

[Milkbeat](https://github.com/johnneerdael/Milkbeat) follows the latest stable Native-capable core through the unchanged canonical artifact name `projectM-TV-core-<version>.aar`. Its workflow pins the resolved version and names it in Milkbeat's release notes. ProjectM-TV sends a `projectm-core-release` dispatch after publication. A core already named by Milkbeat's latest release does not trigger a duplicate rebuild.

`MILKBEAT_TOKEN` must be a fine-grained token with Contents read/write on `johnneerdael/Milkbeat`, stored as a ProjectM-TV Actions secret. It was configured on 2026-10-02. A missing token fails the update job visibly; rerun a failed update job after fixing its configuration.

For an unreleased Milkbeat-compatible core, build `./gradlew :core:assembleRelease`, copy the AAR to `<dir>/download/v<version>/projectM-TV-core-<version>.aar`, and build Milkbeat with `-PprojectmCoreRepo=<dir> -PprojectmCoreVersion=<version>`.
