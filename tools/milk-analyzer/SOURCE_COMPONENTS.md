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

## Solver and recurrent dependency supplements

`--proof-python PATH` enables the pinned Z3 worker alongside or independently
of `--symbolic-python`. Scalar value records gain `solver_refinement`; existing
bounds and native selector domains are preserved. The separate
`main_q_domain_evidence` API requires caller-supplied candidate private-state
ranges and proves both initialization and the ordered frame transition. It
rejects effects, unqualified storage, invalid domains and shared/cross-phase
state; only q1..q32 reload their initial snapshots. See `SOURCE_PROOFS.md`.

The fixed 2,000-source scalar census added zero new bounds and zero >1% reductions.
It produced 514 small enclosure reductions across 307 presets. Its value here is
an explicit proof/counterexample facility, not a measured classification gain.

`--phase-dependencies` adds a top-level `source_dependency_evidence` record.
The Stims-derived monotone fixpoint closes private main-frame predecessor edges
while retaining initialization uncertainty, Q resets, random-stream uncertainty
and shared-memory/phase exclusions. It exposes additional possible audio ancestry
in main source control endpoints for 470 of the full 9,606 presets. Those endpoints
may still be gated or superseded by custom shaders; ancestry is not visible strength.
No bounds or appearance predictions are changed by this component.

```sh
build/preset-lab-venv/bin/python tools/milk-analyzer/effect_family_export.py core/src/main/assets/presets --reader build/preset-corpus/source34/adapters/milk-native-reader --symbolic-python build/source-component-venv/bin/python --proof-python build/source-component-venv/bin/python --phase-dependencies --output build/source-component-export
```

Enabled backend identities and the dependency policy join the cache/run identity.
After all supplemental analysis, source/model/parser identities are checked again
before publishing or caching. A cached default-off result cannot masquerade as
an enabled result.

## Auxiliary shader and precision components

Compiler components are separate opt-in exports. They preserve exact GLES300
source AST evidence and label modified inspection profiles explicitly. Their
function, call, loop, conversion and resource inventories supplement source
understanding; they do not select native branches or assign effects/moods.
SPIRV-Cross, Naga and Slang bridge scopes and exact tool requirements are documented
with the compiler component evidence. No shader is rendered.

`source_precision_export.export_precision_query` exports already parsed pure
scalar Fields into FPCore and FPTaylor requests. A caller must supply finite input
domains and an explicit common binary32/binary64 format. Exact existing literals
and operation order are retained. `run_fptaylor_js` runs a separately supplied
portable bundle under a process deadline with frozen bundle/config bytes and
runtime identity checks. Its portable interval backend rejects trig. FPCore
requests also worked with the separately built Daisy tool. Both reject the
overflow control; neither certifies the actual mixed-format native pipeline.
Herbie-compatible requests are for separately labelled new/adapted effects;
its output must never replace authored prediction arithmetic silently.
See `docs/research/2026-10-10-component-reuse-evaluation.md` and
`docs/superpowers/plans/2026-10-10-source-component-adoption.md`.
