# Optional source-analysis components

The static analyzer can use a separate pinned SymPy environment to simplify
and differentiate supported source-control programs. Existing native parsing,
ordinary bounds and numeric-domain checks remain authoritative. This is an
opt-in component; normal operation adds no dependency to the analyzer or app.

Prepare a separate environment and install `requirements-source-components.txt`.
The current evaluated environment lives under
`/Users/jneerdael/Scripts/source-analysis-evaluation/python-env/`; this path is
not required by the implementation. Preserve a venv executable path rather
than resolving its symlink to the base Python.

```sh
python3 -m venv build/source-component-venv
build/source-component-venv/bin/python -m pip install -r tools/milk-analyzer/requirements-source-components.txt
build/preset-lab-venv/bin/python tools/milk-analyzer/effect_family_export.py core/src/main/assets/presets --reader build/preset-corpus/source34/adapters/milk-native-reader --symbolic-python build/source-component-venv/bin/python --output build/source-component-export
```

Compile evidence and declared scenarios remain optional independent inputs.
Use the same source-bound compile manifest/profile/scenario for paired exports.
Backend policy/version/worker hash appear in provenance and cache/run identity;
an enabled run cannot reuse a disabled result cache.

## Mathematical scope

`nominal_audio_response.symbolic_refinement` contains an additional derivative
program and bound from the existing scalar-value calculator. A successful
tighter bound retains `baseline_absolute_control_change_per_audio_unit` in the
ordinary response record. Source inputs/intermediates must be finite and the
declared domains must hold. This is real-number source calculus, not GPU or
EEL finite-precision execution.

The first adapter supports scalar input/constant arithmetic, sin/cos, negation
and square. It rejects casts, narrowing, texture samples, execution sequences,
division, discontinuities and phase/storage-qualified inputs. Every original
operand is checked before symbolic cancellation; original response/value-domain
failures are retained. Original input names are reserved before introducing
rational-coefficient enclosures. A simpler derivative cannot erase overflow,
missing numeric contracts or distinguishable phase bindings.

A caller-owned reusable worker has 128-source-node/48-depth and bounded output
budgets. Request writing and response reading share a deadline. Timeout or
transport failure disables that session and kills the worker; it is not retried
for each following control. Unsupported formulas retain baseline output and an
explicit reason. Context exit closes the worker. No equation, shader, audio,
framebuffer or visual inspection is performed.

## Full-pack comparison

```sh
build/preset-lab-venv/bin/python tools/milk-analyzer/source_component_validate.py --reader build/preset-corpus/source34/adapters/milk-native-reader --symbolic-python build/source-component-venv/bin/python --output build/source-component-comparison --workers 4
```

This bounded census compares named mesh controls (including per-frame and
per-pixel equations) and custom-shape audio controls under
unconstrained finite inputs and a separately declared band `[0,2]` profile.
It excludes custom shader fields, drawing prominence and complete behaviour
classification. It keeps all source IDs/hashes, unresolved equations and rows
in gzip JSONL. Summaries distinguish newly bounded results, changes over 1%,
small numerical tightening and unresolved cases. The 1% reporting bucket is a
practical census threshold, not visual accuracy or a correctness tolerance.
No old render corpus or device is operated.

Run optional component tests with `MILK_SYMBOLIC_PYTHON` set to the prepared
worker executable. Without that optional environment, component-dependent tests
are explicitly skipped; default-off tests still run. Complete qualification
must include the component environment and the pinned native adapters required
by the rest of the analyzer suite.

Z3 and compiler-backed source additions are the following planned steps;
installation of their libraries does not mean those capabilities are integrated.
See `docs/research/2026-10-10-component-reuse-evaluation.md` and
`docs/superpowers/plans/2026-10-10-source-component-adoption.md`.
