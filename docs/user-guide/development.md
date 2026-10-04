# Build and test

ProjectM TV embeds projectM 4.1.7 with the app's patch series. The Android app, offline analyzer and documentation site have separate build dependencies.

## Android app

Clone the repository with its submodules and follow the [developer build instructions](https://github.com/johnneerdael/ProjectM-TV#for-developers).

```sh
./gradlew assembleDebug
./gradlew testDebugUnitTest
core/src/test/native/run_native_tests.sh
```

The native runner also builds the patched projectM engine with ASan/UBSan and checks shader macro preprocessing, contextual identifiers such as `sample`, postfix expressions, numerical shader output and custom waveform audio bounds. It also compiles the affected shader sections of 16 unchanged bundled presets, with their file hashes checked at configure time. It also checks random-image alias identity, requested sampler modes, shared slots and numerical samples against isolated known-value textures. Blur regressions preserve separate read/draw targets on first use and resize, check constant-colour output at normal and reference-scaled sizes, and fully render the unchanged `midgitstraights of majillaen - featy sweet.milk` with isolated TGA images. It requires CMake and a JDK; the GL tests use EGL/GLES development libraries on Linux or the OpenGL framework on macOS.

Production releases are signed by CI. See [Builds and Releases](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/RELEASING.md) for the release process and signing setup.

## Core rendering policies

The core publishes two AARs with the same Java/JNI interface. Select a policy at build time:

```sh
./gradlew :core:assembleRelease -PprojectmCoreRenderingPolicy=capped
./gradlew :core:assembleRelease -PprojectmCoreRenderingPolicy=native
```

Both commands produce `core/build/outputs/aar/core-release.aar`; copy the first AAR before building the second policy. Normal Gradle and APK builds default to `native`.

- **Capped:** enforces a maximum internal render height of 1330p in the core, including direct JNI surface requests. Larger destination surfaces display the upscaled render. The Native choice and feedback diffusion are absent. If the capped intermediate framebuffer cannot be created, the core skips the frame rather than breaking the cap.
- **Native:** keeps Auto and numeric fixed choices capped at 1330p, with a separate full-panel Native option when panel and memory limits permit it. Eligible above-reference rendering uses feedback diffusion, including Auto at 1330p. Higher resolution can cost more GPU work and memory or change feedback pictures.

The canonical `projectM-TV-core.aar` and versioned `projectM-TV-core-<version>.aar` downloads use **capped**, preserving Milkbeat's default core policy. The explicit `projectM-TV-core-native.aar` and `projectM-TV-core-native-<version>.aar` downloads use **native**. The standard ProjectM TV APK uses the Native-capable core and defaults to Auto. See [Builds and Releases](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/RELEASING.md) for publication and checksums.

These policies are separate build choices, not a claim that feedback compensation preserves every preset or improves TV frame rate.

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

## Shader initialization diagnostics

The [source-analysis tools](https://github.com/johnneerdael/ProjectM-TV/tree/main/tools/milk-analyzer)
check equation ranges and whether shader branches initialize their outputs. They
include the bounded-selector fix from PR #25. These checks do not establish full
visual accuracy.

The engine preserves plain uninitialized scalar/vector shader globals as external
inputs. Inputs with no binding start at zero; explicit bindings remain available to
source-analysis evaluations, and writable copies begin with the chosen input on each
invocation. This gives the affected older presets defined inputs without
changing their source or assignment order. Local variables still require an authored
initialization. The policy does not reproduce arbitrary old Direct3D register history.
