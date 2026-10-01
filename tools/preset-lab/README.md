# projectM Preset Lab

An independently installable local tool for measured preset fingerprints and reusable genre matching. Implementation is in progress; inventory and the deterministic native-rendering check are available now. Automatic matching follows the approved plan.

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
