# Build and test

ProjectM TV is an Android app (`:app`) and an engine library (`:core`). The engine builds projectM from the pinned submodule and applies the [patch series](engine/patches.md) at configure time.

## Build the app

Requirements: JDK 21, Android SDK platform 34, NDK 27.3.13750724, CMake 3.22.1, and a `local.properties` file with `sdk.dir`.

```sh
git clone --recursive https://github.com/johnneerdael/ProjectM-TV.git
cd ProjectM-TV
./gradlew assembleDebug          # debug APK
./gradlew assembleRelease        # release APK + core AAR
./gradlew assembleProfile        # release build that profilers can attach to
```

In an existing clone, run `git submodule update --init --recursive`. Never commit edits inside `third_party/projectm`: engine changes are new patch files in `tools/projectm-patches/`.

## Run the tests

| Command | Covers |
|---|---|
| `./gradlew testDebugUnitTest` | App and core JVM tests: settings, automatic quality, custom-pack import, upload server |
| `core/src/test/native/run_native_tests.sh` | Native engine tests and patched-projectM regression controls under ASan/UBSan, with real GL (macOS OpenGL or Linux EGL/GLES) |
| `tools/projectm-host-tests.sh` | projectM's own GoogleTest suite with the patches applied |
| `tools/check-patch-series.sh` | The patch series applies cleanly to the pinned commit |
| `tools/check-presets.py`, `tools/gen-preset-index.py --check` | Bundled presets react to audio, reference only bundled textures, and match the index |
| `python -m pytest tools/preset-lab/tests` | Preset Lab |
| `python3 -m unittest discover -s .github/scripts/tests -v` | Release tooling |

[Validation and evidence](engine/validation.md) describes what the native controls check, including the legacy compatibility controls for `fShader` shading and mode-1 waveforms ([BrainStain investigation](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/superpowers/evidence/brainstain-dark-output/README.md)).

## Test on a TV without replacing the release

A debug build cannot update a production installation (different signing key). Separate test builds install side by side:

| Gradle property | Package | Use |
|---|---|---|
| `-PpresetLabDeviceTest` | `nl.neerdael.projectmtv.presettest` | Mood/category instrumentation and live-audio checks |
| `-PsetupScreenshotTest` | `nl.neerdael.projectmtv.setuptest` | Setup journeys: resolution, Native trails, custom-pack upload and restart |

```sh
./gradlew :app:assembleDebug :app:assembleDebugAndroidTest -PsetupScreenshotTest
adb -s SERIAL shell pm grant --user USER nl.neerdael.projectmtv.setuptest android.permission.RECORD_AUDIO
adb -s SERIAL shell am instrument --user USER -w -e setup_case resolution \
  nl.neerdael.projectmtv.setuptest.test/com.example.projectm.visualizer.MusicCategoryInstrumentation
```

Other cases: `native_trails`, `custom_pack` followed by a cold `custom_pack_restart`, and `custom_pack_qr`. Find `USER` with `adb shell am get-current-user`. These check settings, navigation, uploads and completed frames, not preset appearance or performance.

### Profiling and diagnostics

- Pin one preset for measurements: `adb shell setprop debug.projectmtv.preset '<filename prefix>'`, and clear it afterwards.
- `tools/tv-diagnostics.sh <tv-ip>:5555 --no-install --duration 180` collects logs and frame statistics ([DIAGNOSTICS.md](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/DIAGNOSTICS.md)).
- CPU profiling with the profile build and simpleperf: [PROFILING.md](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/PROFILING.md).

## Use the engine in another app

Every release publishes the engine as an Android library, `projectM-TV-core-<version>.aar`, plus a stable alias `projectM-TV-core.aar`. [Milkbeat](https://github.com/johnneerdael/Milkbeat) uses it this way and is rebuilt automatically when a new core is released.

The public API lives in `nl.neerdael.projectm.core`:

| Class | Role |
|---|---|
| `ProjectMCore.init(context)` | Call once from `Application.onCreate`: indexes presets and copies textures |
| `VisualizerView` + `VisualizerRenderer` | The GL surface and its renderer |
| `ProjectMJNI` | Audio input (`addWaveform`), preset navigation, settings such as transitions and `setNativeTrails` |
| `QualityController` | Automatic resolution from frame rate and live memory headroom; `setResolutionMode` for fixed or Native sizes |
| `DeviceProfile`, `DisplayInfo` | Device tier and physical panel detection |

Engine defaults differ slightly from the app's: for example, blank-preset skipping is off in the core and switched on by the app. `ProjectMJNI.getVersion()` reports the upstream numeric projectM version (`4.2.0`), not the release version. Releasing and publishing are described in [RELEASING.md](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/RELEASING.md).

## Offline preset tools

- [Preset Lab](https://github.com/johnneerdael/ProjectM-TV/tree/main/tools/preset-lab): offline rendering, static audio tracing and bass-response screening with a private desktop build of the engine.
- [milk-analyzer](https://github.com/johnneerdael/ProjectM-TV/tree/main/tools/milk-analyzer): source parsing, equation-domain proofs, shader lowering and the mood scorer.

See [Test and predict presets](authoring/testing.md) for what each tool can tell you.

## This documentation site

The site uses MkDocs with the Material theme. Its source is `docs/user-guide/`; GitHub Pages serves the static build.

```sh
python3 -m venv build/docs-env
build/docs-env/bin/pip install -r docs/site-requirements.txt
build/docs-env/bin/mkdocs serve          # preview at http://127.0.0.1:8000
build/docs-env/bin/mkdocs build --strict
```

Reviewed pull requests build the site, and every merge to `main` publishes it after the full test suite passes. Screenshots on these pages come from the released app on an Android TV emulator, playing music through Milkbeat.

## Contributing

Changes go through a pull request to `main`. A PR runs the full build only after a completed review of its latest commit, with all review threads resolved. Every PR needs a `## Release notes` section written for people using the app (see the PR template). Each successfully tested merge publishes a new versioned APK and core library automatically.
