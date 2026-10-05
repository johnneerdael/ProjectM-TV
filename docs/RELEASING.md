# Builds & Releases

## Automatic publishing

The **Android CI/CD** workflow tests and builds every push and PR. Each successfully tested merge to `main` publishes a stable GitHub Release with its signed APK, Native core AAR, public release notes and SHA-256 checksums, then triggers Milkbeat's core update. Routine PRs need no version bump or manual release command.

| Trigger | Result |
|---|---|
| Feature push or PR | Release tooling tests, native/JVM tests, APK and one Native core AAR artifact with a `-ci.<run>` version suffix |
| Successful merge/push to `main` | Stable APK/Native core AAR, GitHub Release, PR notes, current download details, checksums and Milkbeat dispatch |
| Manual run on `main` | Publishes an unreleased commit or verifies an already complete release; the same commit keeps its version |

Runs queue instead of canceling previous builds. Versions are tied to source history rather than workflow order: the first first-parent commit after `baseVersionCommit` maps to `baseVersionName`/`baseVersionCode`, and each later commit advances both. The historical 2.1 line started at **2.1.5 / code 37**, and the 2.2 line at **2.2.0 / code 38**. The user-planned Native checkpoint starts the **2.3.0 / code 49** line, anchored to `8b70620339018cfaf5ac05acdb4ea8104dc2eb59` (main before this checkpoint). The first first-parent commit after that anchor receives the base triple; later commits advance it. This is a deliberate minor-release-line change, not a routine PR version bump. Direct pushes containing several commits can leave version gaps; failed builds leave their version unpublished.

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
