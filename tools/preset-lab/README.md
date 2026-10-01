# projectM Preset Lab

An independently installable local tool for measured preset fingerprints and reusable genre matching. Implementation is in progress; inventory, music ingestion, static tracing and deterministic native-rendering checks are available now. Automatic matching follows the approved plan.

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

The worker builds a private copy of the pinned projectM engine and app patches. Its synthetic clock and fixed subsystem seeds leave the Android engine untouched. Doctor compares fresh waveform, noise and random-texture shader runs for exact repeated frames and an identical pre-intervention prefix. Framebuffer discard is a no-op on Apple OpenGL 4.1, so desktop timings do not establish TV performance.

The bundled JSON parser is [nlohmann/json 3.11.3](https://github.com/nlohmann/json/tree/v3.11.3), under the included MIT license. Resolved Python dependencies are recorded in `requirements.lock`.

Ingest the initial music corpus:

```sh
build/preset-lab-venv/bin/preset-lab corpus --audio /Users/jneerdael/Desktop/audio --work build/preset-lab/audio > build/preset-lab-corpus.json
```

The flat-folder aliases `folk`, `hiphop` and `r&b` map to Folk / Acoustic, Hip-Hop and R&B / Soul. M4A album artwork is excluded. Audio is resampled to 44,100 Hz; mono gain is preserved, stereo is averaged, and detected phase cancellation uses the left channel with an explicit flag. Full mixes and aligned stem-removal variants share one gain (at most 1, reduced only to keep the largest variant peak below 0.95). No variant receives independent peak normalization.

The corpus records source hashes, valid excerpt offsets, spectral balance, onset density/regularity, dynamics and available stems. Initial excerpts are within-track evidence. Optional manifests accept `tracks` containing `id`, `path`, `genres`, `excerpts`, and `stems` (drums, bass_instrument, melody, vocals, other). Stem files must have aligned sample counts. Missing stems never become invented source-response scores.

Inspect static audio dependencies:

```sh
build/preset-lab-venv/bin/preset-lab trace 'core/src/main/assets/presets/shifter - neon pulse (reactive).milk'
```

Tracing follows the engine's first-key and numbered-section rules, assignment overwrites, conditionals, persistent frame state and scoped q1–q32/t1–t8 transfers. It distinguishes waveform sample values from spectral bands and records source lines and visible impact classes. Unsupported shader helper/control syntax and shared memory/register flows produce explicit incomplete-analysis reasons. Static reachability is not a measured response strength; controlled rendering supplies that evidence.
