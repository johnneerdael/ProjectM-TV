# Build and test

ProjectM TV embeds projectM 4.1.7 with the app's patch series. The Android app, offline analyzer and documentation site have separate build dependencies.

## Android app

Clone the repository with its submodules and follow the [developer build instructions](https://github.com/johnneerdael/ProjectM-TV#for-developers).

```sh
./gradlew assembleDebug
./gradlew testDebugUnitTest
core/src/test/native/run_native_tests.sh
```

The native runner also builds the patched projectM engine with ASan/UBSan and checks shader macro preprocessing, contextual identifiers such as `sample`, postfix expressions, numerical shader output and custom waveform audio bounds. It also compiles the affected shader sections of 16 unchanged bundled presets, with their file hashes checked at configure time. It also checks random-image alias identity, requested sampler modes, shared slots and numerical samples against isolated known-value textures. It requires CMake and a JDK; the GL tests use EGL/GLES development libraries on Linux or the OpenGL framework on macOS.

Production releases are signed by CI. See [Builds and Releases](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/RELEASING.md) for the release process and signing setup.

## Offline preset analysis

[Preset Lab](https://github.com/johnneerdael/ProjectM-TV/tree/main/tools/preset-lab) is independently installable. It uses a private copy of the pinned engine and patches; its synthetic clock and seeds do not modify the Android renderer.

```sh
python3 -m venv build/preset-lab-venv
build/preset-lab-venv/bin/python -m pip install './tools/preset-lab[test]'
build/preset-lab-venv/bin/preset-lab doctor --repo . --work build/preset-lab
```

The package README documents native compiler, SDL2, OpenGL and audio-tool dependencies. [The Dance measurement article](dance-measurement.md) describes the protocol and exports.

## Test on a TV without replacing the release

```sh
./gradlew -PpresetLabDeviceTest :app:assembleDebug :app:assembleDebugAndroidTest
```

This builds **ProjectM TV · Preset test**, package `nl.neerdael.projectmtv.presettest`. Install its app and test APKs on your development TV, grant its requested Record audio permission, then run:

```sh
adb -s DEVICE shell am instrument -r -w -e live_audio true nl.neerdael.projectmtv.presettest.test/com.example.projectm.visualizer.MusicCategoryInstrumentation
```

The test checks category application, eligible counts, navigation containment, fallback and live audio delivery. Omit the live-audio argument for emulator testing without music. Results verify operation; they do not prove every selected preset's strength on every GPU.

## Documentation site

The site uses MkDocs and the same dark Read the Docs layout as the Milkbeat guide. Markdown in `docs/user-guide/` is the source for these pages.

```sh
python3 -m venv build/docs-env
build/docs-env/bin/pip install -r docs/site-requirements.txt
build/docs-env/bin/mkdocs serve
build/docs-env/bin/mkdocs build --strict
```

The User guide workflow validates the site and deploys main-branch documentation to GitHub Pages. Documentation changes do not require an APK release or a version bump.
