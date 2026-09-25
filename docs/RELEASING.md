# Builds & Releases

## What CI does (`.github/workflows/android.yml`)

| Trigger | Result |
|---|---|
| Any push or pull request | Native engine tests, JVM unit tests + release APK, downloadable from the workflow run (**Actions → run → Artifacts → `apk`**), named `projectM-TV-<version>-ci.<run>-<sha>.apk` |
| Push to `main` where `versionName` has no tag yet | Everything above, plus tag `v<versionName>` and a **GitHub Release** with `projectM-TV-<version>.apk`, using the top section of `RELEASE_NOTES.md` as the description |

CI builds show their origin in the app menu, e.g. `v1.8-ci.42`.

## Publishing a release

1. In `app/build.gradle`, bump `versionCode` (+1) and `versionName` (e.g. `1.9`).
2. Add a new section at the top of `RELEASE_NOTES.md`, ending with a `---` line.
3. Merge to `main`. The release appears under **Releases** within a few minutes.

Pushing `main` again without changing `versionName` doesn't create another release.

## One-time setup: signing key

Android only installs an update over an existing app if both are signed with the same key. Without a key configured, every CI build gets a throwaway debug key and would need an uninstall first.

1. Create a key (keep the file and passwords somewhere safe; losing them means users must reinstall):
   ```bash
   keytool -genkeypair -v -keystore projectm-release.jks -alias projectm \
     -keyalg RSA -keysize 4096 -validity 10000
   ```
2. Add four repository secrets (**Settings → Secrets and variables → Actions → New repository secret**):

   | Secret | Value |
   |---|---|
   | `SIGNING_KEYSTORE_BASE64` | `base64 -i projectm-release.jks` (macOS) or `base64 -w0 projectm-release.jks` (Linux) |
   | `SIGNING_STORE_PASSWORD` | keystore password |
   | `SIGNING_KEY_ALIAS` | `projectm` |
   | `SIGNING_KEY_PASSWORD` | key password |

3. To build locally with the same key, export the same values (with `SIGNING_KEYSTORE_PATH` pointing at the `.jks` file) before running `./gradlew assembleRelease`.

**Note:** installs from Android Studio or `install.sh` (debug key) can't be upgraded by CI builds (release key) or the other way round. Uninstall once when switching; this resets the app's settings.
