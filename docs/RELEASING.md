# Builds & Releases

## What CI does (`.github/workflows/android.yml`)

| Trigger | Result |
|---|---|
| Any push or pull request | Native engine tests, JVM unit tests + release APK and core library AAR, downloadable from the workflow run (**Actions → run → Artifacts → `apk`** / **`core-aar`**), named `projectM-TV-<version>-ci.<run>-<sha>.apk` and `projectM-TV-core-<version>-ci.<run>-<sha>.aar` |
| Push to `main` where `versionName` has no tag yet | Everything above, plus tag `v<versionName>` and a **GitHub Release**, marked as latest, with `projectM-TV-<version>.apk` (also as `projectM-TV.apk`) and `projectM-TV-core-<version>.aar` (also as `projectM-TV-core.aar`), using the top section of `RELEASE_NOTES.md` as the description |

CI builds show their origin in the app menu, e.g. `v1.8-ci.42`.

## Publishing a release

1. In `app/build.gradle`, bump `versionCode` (+1) and `versionName` (e.g. `1.9`).
2. Add a new section at the top of `RELEASE_NOTES.md`, ending with a `---` line.
3. Merge to `main`. The release appears under **Releases** within a few minutes.

Pushing `main` again without changing `versionName` doesn't create another release.

The fixed names make one link always download the newest stable release: https://github.com/johnneerdael/ProjectM-TV/releases/latest/download/projectM-TV.apk and https://github.com/johnneerdael/ProjectM-TV/releases/latest/download/projectM-TV-core.aar (GitHub's `releases/latest` skips drafts and pre-releases).

The core AAR is the `:core` module (`nl.neerdael.projectm.core`: projectM engine, native libraries for `armeabi-v7a`/`arm64-v8a`, bundled presets). It is versioned with the app's `versionName`; there is no separate core version.

## Milkbeat follows each core release

[Milkbeat](https://github.com/johnneerdael/Milkbeat) uses the core AAR straight from these releases. By default (`projectmCoreVersion=latest` in its `gradle.properties`) it uses `releases/latest/download/projectM-TV-core.aar`, the newest stable release. Its CI looks up the latest tag and builds against that exact version, which it names in the Milkbeat release notes.

After every release, the `Rebuild Milkbeat with this core` job sends Milkbeat a `projectm-core-release` repository dispatch. That rebuilds Milkbeat's `main` and publishes a new Milkbeat release with the new core.

To test an unreleased core in Milkbeat, build it here (`./gradlew :core:assembleRelease`), copy `core/build/outputs/aar/core-release.aar` to `<dir>/download/v<version>/projectM-TV-core-<version>.aar`, and build Milkbeat with `-PprojectmCoreRepo=<dir> -PprojectmCoreVersion=<version>`.

## One-time setup: Milkbeat token

**Status:** `MILKBEAT_TOKEN` added on 2026-10-02. Without it, the job only warns and Milkbeat isn't rebuilt.

1. Create a [fine-grained personal access token](https://github.com/settings/personal-access-tokens/new) with access to `johnneerdael/Milkbeat` only and the repository permission **Contents: Read and write** (needed to send a repository dispatch).
2. Add it to this repository as the Actions secret `MILKBEAT_TOKEN`.
