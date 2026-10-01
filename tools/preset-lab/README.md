# projectM Preset Lab

An independently installable local tool for measured preset fingerprints and reusable genre matching. Implementation is in progress; the inventory command is available now. Native rendering and automatic matching follow the approved plan.

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
