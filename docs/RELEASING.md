# Builds & Releases

## Automatic publishing

The **Android CI/CD** workflow tests and builds every push and PR. Each successfully tested merge to `main` publishes a stable GitHub Release with its signed APK, core AAR, public release notes and SHA-256 checksums, then triggers Milkbeat's core update. Routine PRs need no version bump or manual release command.

| Trigger | Result |
|---|---|
| Feature push or PR | Release tooling tests, native/JVM tests, APK and core AAR artifacts with a `-ci.<run>` version suffix |
| Successful merge/push to `main` | Stable APK/core AAR, GitHub Release, PR notes, current download details, checksums and Milkbeat dispatch |
| Manual run on `main` | Publishes an unreleased commit or verifies an already complete release; the same commit keeps its version |

Runs queue instead of canceling previous builds. Versions are tied to source history rather than workflow order: the first first-parent commit after `baseVersionCommit` maps to `baseVersionName`/`baseVersionCode`, and each later commit advances both. Initially, this means **2.1.5 / code 37**, then **2.1.6 / code 38**. Direct pushes containing several commits can leave version gaps; failed builds leave their version unpublished.

CI fetches full tag history and rejects conflicting tags, inconsistent retry metadata and invalid Android codes. An older retry does not replace a newer release as latest. Missing release signing fails a publishing build; PR artifacts may use a temporary debug key.

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
- [Latest core AAR](https://github.com/johnneerdael/ProjectM-TV/releases/latest/download/projectM-TV-core.aar)

Each release also attaches `projectM-TV-<version>.apk`, `projectM-TV-core-<version>.aar` and `checksums.txt`. The core is the `:core` module: projectM, native ARMv7/ARM64 libraries and presets, versioned together with the app.

Publication creates or resumes a draft, uploads every artifact, then publishes it. A retry verifies the tag points to the expected commit and leaves a complete published release unchanged.

## Milkbeat follows each core release

[Milkbeat](https://github.com/johnneerdael/Milkbeat) follows the latest stable core. Its workflow pins the resolved version and names it in Milkbeat's release notes. ProjectM-TV sends a `projectm-core-release` dispatch after publication. A core already named by Milkbeat's latest release does not trigger a duplicate rebuild.

`MILKBEAT_TOKEN` must be a fine-grained token with Contents read/write on `johnneerdael/Milkbeat`, stored as a ProjectM-TV Actions secret. It was configured on 2026-10-02. A missing token fails the update job visibly; rerun a failed update job after fixing its configuration.

For an unreleased core, build `:core:assembleRelease`, copy the AAR to `<dir>/download/v<version>/projectM-TV-core-<version>.aar`, and build Milkbeat with `-PprojectmCoreRepo=<dir> -PprojectmCoreVersion=<version>`.
