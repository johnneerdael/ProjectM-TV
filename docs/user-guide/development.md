# Build and test

ProjectM TV embeds **ProjectM TV Engine**, our extensively modified fork of projectM based on upstream version 4.1.7, with the ordered patch series in `tools/projectm-patches/`. The Android app, offline analyzer and documentation site have separate build dependencies.

The published core AAR shares the app's release version. `ProjectMJNI.getVersion()` retains its existing meaning: the upstream projectM version, not the identity of the patched build. Record the release version, source revision and artifact checksum for reproducible engine comparisons. See the [patch inventory and upstream attribution](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/THIRD_PARTY.md).

## Android app

Clone the repository with its submodules and follow the [developer build instructions](https://github.com/johnneerdael/ProjectM-TV#for-developers).

```sh
./gradlew assembleDebug
./gradlew testDebugUnitTest
core/src/test/native/run_native_tests.sh
```

The native runner also builds the patched projectM engine with ASan/UBSan and checks shader macro preprocessing, contextual identifiers such as `sample`, postfix expressions, numerical shader output and custom waveform audio bounds. It also compiles the affected shader sections of 16 unchanged bundled presets, with their file hashes checked at configure time. It also checks random-image alias identity, requested sampler modes, shared slots and numerical samples against isolated known-value textures. Blur regressions preserve separate read/draw targets on first use and resize, check constant-colour output at normal and reference-scaled sizes, and fully render the unchanged `midgitstraights of majillaen - featy sweet.milk` with isolated TGA images. It requires CMake and a JDK; the GL tests use EGL/GLES development libraries on Linux or the OpenGL framework on macOS.

Feature-branch pushes do not start CI builds. A ready PR targeting `main` starts the full build suite only after a completed Codex or human review of its latest commit, with all review threads resolved and no outstanding review requests or changes requested. The gate requires full commit-SHA evidence; abbreviated Codex completion text alone cannot unlock builds. GitHub hides private draft reviews from automation: request a reviewer to keep the gate closed until submission. The review gate periodically rechecks thread resolution; GitHub may delay scheduled runs. Production releases are signed by CI. See [Builds and Releases](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/RELEASING.md) for the release process and signing setup.

## Core rendering policies

The single `:core` AAR uses Native rendering. Build it with:

```sh
./gradlew :core:assembleRelease
```

The legacy `-PprojectmCoreRenderingPolicy=native` spelling remains accepted. The
retired `capped` build is rejected. Canonical `projectM-TV-core.aar` and versioned
core downloads now contain Native bytes; there is no separate capped publication.
The Java/JNI API remains additive. Standard trails is the new core default above
1330p, with `ProjectMJNI.setNativeTrails(-1/0/1/2)` for Off/Standard/Medium/High.
The shared QualityController is automatic up to the detected panel size, with
FPS and live memory headroom as inputs. Legacy fixed-resolution/static-RAM
settings normalize to Auto. See [Builds and Releases](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/RELEASING.md).

## Offline preset analysis

[Preset Lab](https://github.com/johnneerdael/ProjectM-TV/tree/main/tools/preset-lab) is independently installable. It uses a private copy of the pinned engine and patches; its synthetic clock and seeds do not modify the Android renderer.

```sh
python3 -m venv build/preset-lab-venv
build/preset-lab-venv/bin/python -m pip install './tools/preset-lab[test]'
build/preset-lab-venv/bin/preset-lab doctor --repo . --work build/preset-lab
```

The package README documents native compiler, SDL2, OpenGL and audio-tool dependencies. That private host renderer supports historical research; the current beta collections use the **published ProjectM-TV:core AAR through JNI**. See [Predictive collections](predictive-collections.md) for scoring, export and verification commands.

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

The read-only User guide build workflow validates the site as part of reviewed PR validation and the main pipeline. The main pipeline publishes the site after all validation builds pass. A manual **User guide** run on `main` also builds and publishes it without another APK/AAR release. Both publishing paths use the same deployment queue and skip runs whose source is older than current `main`. Every successfully tested main merge also publishes the APK and core AAR, including documentation-only merges; routine changes do not manually bump versions.

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

## Shader literal precision

The native runner checks finite float32 constants by comparing their bits after
formatting and reparsing, including negative zero, boundary values, randomized
values and a comma-decimal locale. It also renders a one-frame warp/composite
control and directly compiles 95 unchanged, hash-checked preset shader sections.
The render control reads normalized framebuffers as RGBA bytes, then exports RGB
when saving a capture. This uses the portable GLES readback format; desktop OpenGL
can accept RGB-only reads that Linux GLES drivers reject. Validate GL readback
changes with the Linux EGL/Mesa tests as well as macOS CGL.

Source-analysis adapters rebuilt against the current engine record
`float_literal_policy` and `float_formatter_sha256`; the reader’s `renderer_literal`
values use the production formatter. Rebuild adapters when the engine patch series
changes. Historical fixtures retain their historical engine identity.

Nonfinite shader literals are rejected by the generator rather than emitted as
identifiers such as `inf`. Runtime nonfinite arithmetic and driver precision remain
separate questions. These checks do not establish every preset’s visual fidelity
or physical-TV performance.
