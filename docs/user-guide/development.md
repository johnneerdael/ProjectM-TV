# Build and test

ProjectM TV embeds **ProjectM TV Engine**, our extensively modified fork of projectM based on unreleased projectM 4.2 master, pinned to commit `6f6480746`, with the ordered patch series in `tools/projectm-patches/`. The Android app, offline analyzer and documentation site have separate build dependencies.

The published core AAR shares the app's release version. `ProjectMJNI.getVersion()` retains its existing meaning: the upstream numeric projectM version (`4.2.0`), not the identity of the patched build or proof of an upstream release. Record the release version, source revision and artifact checksum for reproducible engine comparisons. The immutable upstream pin is `6f64807467e312034883a4389e6aa80a675458bc`; this is a development snapshot, not an upstream 4.2 release. See the [patch inventory and upstream attribution](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/THIRD_PARTY.md).

## Android app

Clone the repository with its submodules and follow the [developer build instructions](https://github.com/johnneerdael/ProjectM-TV#for-developers).

```sh
./gradlew assembleDebug
./gradlew testDebugUnitTest
core/src/test/native/run_native_tests.sh
```

The native runner also builds the patched projectM engine with ASan/UBSan and checks shader macro preprocessing, contextual identifiers such as `sample`, postfix expressions, numerical shader output and custom waveform audio bounds. It also compiles the affected shader sections of 16 unchanged bundled presets, with their file hashes checked at configure time. It also checks random-image alias identity, requested sampler modes, shared slots and numerical samples against isolated known-value textures. Blur regressions preserve separate read/draw targets on first use and resize, check constant-colour output at normal and reference-scaled sizes, and fully render the unchanged `midgitstraights of majillaen - featy sweet.milk` with isolated TGA images. It requires CMake and a JDK; the GL tests use EGL/GLES development libraries on Linux or the OpenGL framework on macOS.

Feature-branch pushes do not start CI builds. A ready PR targeting `main` starts the full build suite only after a completed Codex or human review of its latest commit, with all review threads resolved and no outstanding review requests or changes requested. Codex’s thumbs-up reaction on the PR is its approval signal. The gate uses completed review metadata to bind that reaction to the current revision, resolving shortened IDs through GitHub; a completion comment without the reaction cannot unlock builds. GitHub hides private draft reviews from automation: request a reviewer to keep the gate closed until submission. The review gate periodically rechecks thread resolution; GitHub may delay scheduled runs. Production releases are signed by CI. See [Builds and Releases](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/RELEASING.md) for the release process and signing setup.

The native suite also observes effective samplers at actual custom-shape draws,
checks repeat/bilinear samples and named-image qualifiers across instances and
context recreation, and separates blur mentions from actual allocation. Blur
controls exercise the production bounds and progressive float32 uniform producer.
Warp controls execute the shared production vertex source and read transformed UVs
for signed negative unit-exponent zoom and ordinary positive transforms. Native GL regressions inherit
the engine's GL link dependencies; Linux uses the harness-selected EGL target for
context creation. Both ordinary system discovery and explicit EGL/GLES link-flag
overrides are supported without depending on a child-directory imported target. Sampling fixtures allocate storage matching their upload format and check GL errors immediately; unit-slope, binary-exact coordinates keep strict pixel oracles portable across the tested drivers.

## Core rendering policies

Warp UV controls also check CPU-defined negative nested powers, including a
nonunit authored exponent that produces nested exponent one, squares and cubes.
Real-mesh controls verify attribute9 uploads, unchanged equation parameters,
nonfinite preservation, resize and prepared replay. Invalid fractional-domain
sampling observations remain backend-bound; the source predictor must not gain
portable appearance credit from them. See the
[power-domain evidence](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/superpowers/evidence/tulip-negative-zoom-power/README.md).

Legacy compatibility controls check constant-colour output with disabled and
fractional `fShader`, mode-1 waveform opacity and open-strip topology against
MilkDrop 2.25c source expectations. They run in the native suite above. The
[BrainStain investigation](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/superpowers/evidence/brainstain-dark-output/README.md)
records the unchanged preset, exact-AAR reproduction, isolated diagnostic copies
and bounded Android captures. Matching a source predictor is not independent
proof of original MilkDrop appearance.

The single `:core` AAR uses Native rendering. Build it with:

```sh
./gradlew :core:assembleRelease
```

The legacy `-PprojectmCoreRenderingPolicy=native` spelling remains accepted. The
retired `capped` build is rejected. Canonical `projectM-TV-core.aar` and versioned
core downloads now contain Native bytes; there is no separate capped publication.
The Java/JNI API remains additive. Standard trails is the new core default above
1330p, with `ProjectMJNI.setNativeTrails(-1/0/1/2)` for Off/Standard/Medium/High.
The shared QualityController defaults to Auto up to the detected panel size, with
FPS and live memory headroom as inputs. The shared reserve follows Android’s
pressure threshold on nominal 4 GB+ devices (at least 3,584 MiB kernel-visible
RAM), with the conservative percentage reserve retained on smaller devices.
Android handles background-app reclamation; the core has no root or
process-cleanup dependency. Legacy fixed-resolution/static-RAM
settings normalize to Auto. New hosts may explicitly opt into `setResolutionMode(mode, lastAutoHeight)` using 0 for Auto, -1 for Native or a height from `resolutionModes(display)`. Fixed/Native retain memory protection and bypass FPS adaptation and slow-preset skipping; they do not guarantee a fixed actual size under memory pressure. See [Builds and Releases](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/RELEASING.md).

## Offline preset analysis

[Preset Lab](https://github.com/johnneerdael/ProjectM-TV/tree/main/tools/preset-lab) is independently installable. It uses a private copy of the pinned engine and patches; its synthetic clock and seeds do not modify the Android renderer.

```sh
python3 -m venv build/preset-lab-venv
build/preset-lab-venv/bin/python -m pip install './tools/preset-lab[test]'
build/preset-lab-venv/bin/preset-lab doctor --repo . --work build/preset-lab
```

The package README documents native compiler, SDL2, OpenGL and audio-tool dependencies. The private desktop worker and host engine controls preserve attachment contents when their GL declarations lack the optional framebuffer discard hint; Android/GLES keeps the real GLES3 API. Desktop timings do not establish TV performance. That private host renderer supports historical research; the current beta collections use the **published ProjectM-TV:core AAR through JNI**. See [Predictive collections](predictive-collections.md) for scoring, export and verification commands.

## Test on a TV without replacing the release

```sh
./gradlew -PpresetLabDeviceTest :app:assembleDebug :app:assembleDebugAndroidTest
```

This builds **ProjectM TV · Preset test**, package `nl.neerdael.projectmtv.presettest`. Install its app and test APKs on your development TV, grant its requested Record audio permission, then run:

```sh
adb -s DEVICE shell am instrument -r -w -e live_audio true nl.neerdael.projectmtv.presettest.test/com.example.projectm.visualizer.MusicCategoryInstrumentation
```

The test checks category application, eligible counts, navigation containment, fallback and live audio delivery. Omit the live-audio argument for emulator testing without music. Results verify operation; they do not prove every selected preset's strength on every GPU.

## Resolution and Native trails setup checks

Build and install the separate setup app and its test APK on the selected development device:

```sh
./gradlew :app:assembleDebug :app:assembleDebugAndroidTest -PsetupScreenshotTest
```

These builds use package `nl.neerdael.projectmtv.setuptest`. Grant Record audio and stop this isolated app before instrumentation so the case starts cold:

```sh
adb -s DEVICE shell pm grant --user USER nl.neerdael.projectmtv.setuptest android.permission.RECORD_AUDIO
adb -s DEVICE shell am force-stop --user USER nl.neerdael.projectmtv.setuptest
adb -s DEVICE shell am instrument --user USER -r -w -e setup_case resolution nl.neerdael.projectmtv.setuptest.test/com.example.projectm.visualizer.MusicCategoryInstrumentation
```

Use `setup_case native_trails` for the Native trails case. An unanswered permission dialog can pause rendering and time out the completed-generation check; a warm activity can retain menu and focus state. These checks exercise settings, navigation and completed frames, not preset pixel fidelity or performance.

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

## Live preset controls

Native regressions include `dynamic-wave-controls`, `dynamic-display-controls`
and `dynamic-original-presets`. They compare real draw state and pixels with
unchanged static controls, check independent filter blend predictions, preserve
per-frame reset defaults, exercise paired authored/native geometry targets, and
render three unchanged SHA-256-pinned witnesses in Off/Standard/Medium/High paths.
See the [versioned engine policy and evidence](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/superpowers/evidence/live-native-controls/README.md).
Historical predictor/static-engine policies remain historical controls; these
fixes do not regenerate collection scores. Host and emulator checks do not
establish physical-TV performance.

## Custom preset pack validation

The app JVM tests exercise ZIP extraction at exactly 50,000 presets, oversized/invalid packs, cancellation, ignored files, replacement and real HTTP sockets (including idle browser preconnections). Native library tests cover Custom/All membership, scored exclusions, generated storage, duplicate basenames, history, skips and long-name persistence.

Use an isolated Android TV test installation for the full upload journey:

```sh
./gradlew :app:assembleDebug :app:assembleDebugAndroidTest -PsetupScreenshotTest
adb -s SERIAL install -r app/build/outputs/apk/debug/app-debug.apk
adb -s SERIAL install -r app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
adb -s SERIAL shell pm grant --user USER nl.neerdael.projectmtv.setuptest android.permission.RECORD_AUDIO
adb -s SERIAL shell am instrument --user USER -w -e setup_case custom_pack nl.neerdael.projectmtv.setuptest.test/com.example.projectm.visualizer.MusicCategoryInstrumentation
adb -s SERIAL shell am force-stop --user USER nl.neerdael.projectmtv.setuptest
adb -s SERIAL shell am instrument --user USER -w -e setup_case custom_pack_restart nl.neerdael.projectmtv.setuptest.test/com.example.projectm.visualizer.MusicCategoryInstrumentation
```

Resolve `USER` from `adb -s SERIAL shell am get-current-user`. Use a fresh test-app data directory for `custom_pack`; it imports 50,000 synthetic presets and then replaces them with two. It checks the Advanced row with D-pad input, HTTP upload, rendering during import, collection membership, replacement, invalid-ZIP preservation, uploaded PNG pixel output before/after replacement, decoding the rendered QR code to the current upload endpoint and listener closure. The second case checks a cold restart retaining the two-preset pack and Custom selection, and asserts the pack resides in the no-backup directory, and verifies its uploaded image still renders. The full case also checks that normal files storage contains no custom pack. Use `-e setup_case custom_pack_qr` for a shorter screen-layout check: it decodes the displayed code and checks Close is visible/focusable within the display. Screenshots are written to the target test app’s external files directory. These cases do not validate physical-TV GPU performance or arbitrary preset compatibility.

## Warp rotation validation

The native runner includes `warp-rotation-regressions`, ported with historical
patch0051 as current0011. It covers direct and prepared-mesh replay through 4.2
VertexBuffers and evaluates actual
per-frame/per-pixel inputs, uploads the production mesh and reads real legacy and
custom warp draws. It compares UVs for signed, moderate, large and maximum finite
float angles, varying per-vertex equations and four feedback frames. It also
checks recovery after nonfinite inputs without assigning those inputs a defined
image. The direct vertex-source zoom test uses the same updated internal attribute
layout. These controls are separate from original-preset appearance, high-resolution
trail paths and physical-TV performance; record those separately when validating
an engine release.

## Preset validation in CI

The `presets / measurements` release gate verifies the shipped predictive
collection bundle: current preset and texture hashes, retained measurement
provenance, score calculations, collection membership and index weights. It also
runs Preset Lab and Native trails tooling tests, source-analysis checks and
current-engine native rendering regressions. It does not rerender or regenerate
the full collection scores; their published core 2.3.3 provenance remains intact.

The retired historical core-corpus scanner is outside this release gate. Focused
Native trails tools retain its shared signal, session, PNG, worker and engine-pin
components; their compatibility tests can be run with
`python -m pytest tools/native-trails tools/core-corpus -q`.

## Archived corpus evidence

The obsolete bulk AAR/scanner CLI, hard-coded smoke command and frozen-source
transformation controls have been retired. Shared helpers remain available to
focused Native trails validation. Recorded protocols, capture hashes and scoring
provenance remain unchanged; use the original recorded Git revision when
reverifying historical corpus evidence. See `tools/core-corpus/README.md`.
