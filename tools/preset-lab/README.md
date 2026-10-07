# projectM Preset Lab

An independently installable local tool for measured preset fingerprints and reusable matching. Its bass-response selection commands describe the historical Dance experiment. The app now ships the predictive preset engine beta; use `tools/milk-analyzer/beta_score.py` with the published ProjectM-TV:core AAR and `beta_export.py` for the current All / Chill / Normal / Intense bundle. Broad genre matching remains experimental.

Install in a dedicated environment from the ProjectM-TV checkout:

```sh
python3 -m venv build/preset-lab-venv
build/preset-lab-venv/bin/python -m pip install './tools/preset-lab[test]'
```

Inventory preserves exact filenames and the existing memory weights. It rejects missing/unindexed assets and unsafe paths, and records independent content identities for presets and textures.

```sh
build/preset-lab-venv/bin/preset-lab inventory --presets core/src/main/assets/presets --index core/src/main/assets/presets.idx --textures core/src/main/assets/textures > build/preset-inventory.json
build/preset-lab-venv/bin/python -m pytest tools/preset-lab/tests -q
```

Machine-readable results go to stdout; errors go to stderr. Exit status 2 indicates invalid arguments, and 1 indicates an operation failure. User music and generated frames stay outside the app's tracked assets.

Build and verify the native worker (requires CMake, a C++17 compiler, SDL2, native OpenGL, ffmpeg and ffprobe):

```sh
build/preset-lab-venv/bin/preset-lab doctor --repo . --work build/preset-lab > build/preset-lab-doctor.json
```

The worker builds a private copy of the pinned projectM engine and app patches. Its synthetic clock and fixed subsystem seeds leave the Android engine untouched. Doctor compares fresh waveform, noise and random-texture shader runs for exact repeated frames and an identical pre-intervention prefix. Framebuffer discard is a no-op on Apple OpenGL 4.1 and when the configured desktop declarations lack the optional GL4.3 hint (including the pinned GLAD3.3 Linux build). Android/GLES workers retain the real GLES3 discard API. Desktop timings do not establish TV performance.

The bundled JSON parser is [nlohmann/json 3.11.3](https://github.com/nlohmann/json/tree/v3.11.3), under the included MIT license. Resolved Python dependencies are recorded in `requirements.lock`.

Ingest the initial music corpus:

```sh
build/preset-lab-venv/bin/preset-lab corpus --audio /Users/jneerdael/Desktop/audio --work build/preset-lab/audio > build/preset-lab-corpus.json
```

The flat-folder aliases `folk`, `hiphop` and `r&b` map to Folk / Acoustic, Hip-Hop and R&B / Soul. M4A album artwork is excluded. Audio is resampled to 44,100 Hz; mono gain is preserved, stereo is averaged, and detected phase cancellation uses the left channel with an explicit flag. Full mixes and aligned stem-removal variants share one gain (at most 1, reduced only to keep the largest variant peak below 0.95). No variant receives independent peak normalization.

The corpus records source hashes, valid excerpt offsets, spectral balance, onset density/regularity, dynamics and available stems. Initial excerpts are within-track evidence. Optional manifests accept `tracks` containing `id`, `path`, `genres`, `excerpts`, and `stems` (drums, bass_instrument, melody, vocals, other). Stem files must have aligned sample counts. Missing stems never become invented source-response scores.

Numbered files such as `ambient2.webm` remain in Ambient. WebM/Opus inputs are decoded through the same audio-only path. The supplied Ambient references are Eno (`ambient.m4a`), Roach (`ambient2.webm`), Lustmord (`ambient3.webm`), Gas (`ambient4.webm`) and Basinski (`ambient5.webm`), in that order. Preserve the title/test-scenario annotations with the supplied manifest:

```sh
build/preset-lab-venv/bin/preset-lab corpus --audio /Users/jneerdael/Desktop/audio --manifest tools/preset-lab/src/preset_lab/profiles/reference-corpus.json --work build/preset-lab/audio > build/preset-lab-corpus.json
```

These annotations describe the user's expected test coverage; the tool stores them separately from measured audio features. They do not create subgenre categories.

Inspect static audio dependencies:

```sh
build/preset-lab-venv/bin/preset-lab trace 'core/src/main/assets/presets/shifter - neon pulse (reactive).milk'
```

Tracing follows the engine's first-key and numbered-section rules, assignment overwrites, conditionals, persistent frame state and scoped q1–q32/t1–t8 transfers. It distinguishes waveform sample values from spectral bands and records source lines and visible impact classes. Unsupported shader helper/control syntax and shared memory/register flows produce explicit incomplete-analysis reasons. Static reachability is not a measured response strength; controlled rendering supplies that evidence.

## Measure bass response on screen

Run the same numerical test on every preset, using the actual projectM engine to execute preset equations, shaders and feedback:

```sh
build/preset-lab-venv/bin/preset-lab bass-screen --repo . --work build/preset-lab/bass-screen
```

Use repeatable `--preset 'Exact filename.milk'` to test a subset, or `--priority 'Exact filename.milk'` to check a candidate first while still scanning the full library. `--worker /absolute/path/to/preset-lab-worker` reuses an existing build. The command updates `ranking.json` after each preset and resumes by reusing completed measurements. Invalidated inputs are rendered again automatically.

Each experiment renders an identical carrier twice, then adds bass noise bursts at three amplitudes (0.05, 0.15, 0.30). The noise carrier covers 20–250 Hz; the kick envelope adds modulation sidebands. All runs share four seconds of identical warmup and twenty seconds of measurement. The bass bursts have a 10 ms attack, 120 ms decay and one-second spacing. Output gain is not independently normalized.

For each pixel, `d = mean(abs(RGB_bass - RGB_control)) / 255`. Screen magnitude is `M = mean(d)` across the entire image. Affected area is the fraction of pixels where `d > 8/255`; local intensity is the mean difference within that area. This gives a tiny bright element proportionately less credit than a full-scene effect. Color, brightness, geometry and shader changes all contribute. Identical intrinsic animation contributes zero.

The ranking score is the average, across the three amplitudes, of the 95th-percentile screen magnitude during measurement. Results also expose mean magnitude, affected area, first-pulse magnitude and response delay. A large sustained divergence caused by bass feedback can score highly even if immediate kick impact is small; inspect the separate first-pulse measurement when beat punch matters. Scores are pixel differences, not accuracy percentages or musical probabilities.

A non-repeatable control, a changed pre-bass image prefix, a rendering failure or a compatibility warning produces `unknown` with no score. These checks cover the actual tested conditions. They do not prove response for all possible songs, timings, starting states, resolutions or GPU backends. The static parser is not required to understand every shader construct for this measurement.

## Historical Dance selection (not runnable with the current bundle)

The earlier Dance experiment selected the highest-ranked measured bass-response presets from cached results. Collection size was separate from the strongest-response tier; selecting 500 did not label all 500 equally strong. It preserved master memory weights and excluded unknown, stale, incomplete and non-finite measurements.

The legacy `bass-select` CLI implicitly reads this checkout's bundled schema-1 catalog. The current app bundle is schema 2 and has no schema-1 `presets` catalog, so that CLI cannot select or import a Dance collection from the current checkout. Removing `--import` does not make it compatible. The historical command is therefore not offered as a runnable example here. Reproducing that old experiment requires a matching historical schema-1 checkout and its measurements.

For the current All / Chill / Normal / Intense beta bundle, use the published-AAR scoring and `beta_export.py` workflow in the [analyzer README](../milk-analyzer/README.md). Verify the committed current bundle with:

```sh
python tools/milk-analyzer/beta_export.py --check --bundle core/src/main/assets/preset-genres
```

## Verify on a TV without replacing its installed release

Build a separate debug app (`nl.neerdael.projectmtv.presettest`, labelled “ProjectM TV · Preset test”) and its framework instrumentation:

```sh
./gradlew -PpresetLabDeviceTest :app:assembleDebug :app:assembleDebugAndroidTest
```

Install both APKs on the test device, grant the test app its requested RECORD_AUDIO permission, and run:

```sh
adb -s DEVICE shell am instrument -r -w -e live_audio true nl.neerdael.projectmtv.presettest.test/com.example.projectm.visualizer.MusicCategoryInstrumentation
```

The live test checks category application, member count, random-selection containment, fallback and live audio delivery. It saves Intense as the separate test app's collection. Omit `-e live_audio true` for emulator testing without music. Live audio/output motion establishes operation on that device; it does not replace the controlled bass-effect measurements or prove every selected preset on every GPU. Omit `-PpresetLabDeviceTest` when building the normal debug app.

The Preset Lab CI workflow runs synthetic/fake-worker tests, bundle integrity checks and real rendering fixtures on headless Mesa. Local Apple GPU and TV test evidence remains distinct from CI results.
