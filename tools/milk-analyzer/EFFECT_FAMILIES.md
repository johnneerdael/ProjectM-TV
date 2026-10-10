# Static effect-family export

Policy `source-effect-families-v1`; semantic record schema1. Experimental feature
branch `feat/predictor-static-output-bounds`, separate from the shipped collections.
This export recognizes mathematical program mechanisms from native-parsed `.milk`
equations and typed shader dependency graphs. It does not execute equations,
waveforms, shader fields, feedback frames, a renderer, or an AI model.

## Run

Use the prepared Python environment and exact source31 parser:

```sh
build/preset-lab-venv/bin/python tools/milk-analyzer/effect_family_export.py path/to/preset.milk --output ~/Downloads/ProjectM-TV-static-single
```

Omit the source argument to process the bundled pack, or supply a directory.
The default output is `~/Downloads/ProjectM-TV-static-effect-families`. Results
retain each preset's relative filename under `results/`. The existing paired
archive writer produces a ZIP every100 completed attempts and a final partial
ZIP. Each ZIP includes exact `.milk` bytes, the matching JSON and a hashed manifest.
There are no audio, FPS, frame-count or resolution arguments on this path.

```sh
build/preset-lab-venv/bin/python tools/milk-analyzer/effect_family_export.py --output ~/Downloads/ProjectM-TV-static-effect-families
```

The default parser is `build/preset-corpus/source31/adapters/milk-native-reader`.
`--reader` can identify another prepared copy, but its reported engine must match
the supported exact source31or source34identity. Source34matches the
current published2.3.34/35/36math-source line; published-runtime qualification
remains independently pending. `--profile gles300` is the
default; `glsl330` is also a declared interpretation context. Neither option
proves a shader actually compiled or ran on a GPU.

Results resume only under the same input/model/parser/profile identity. Edits
require a new output folder. Do not modify code or adapters while a run is active.
`--cache` can share a separately identified cache; default is output/cache.
Cache hits reuse a verified record without parsing or analyzing again. Cached
records must match their content digest. Model identity is checked against both
import-time inventories before cache lookup, preventing already-loaded old code
from being stamped with new disk hashes. Supported use is a fresh process after
edits with dependencies fixed before import; these parent snapshots do not
authenticate arbitrary dependency modules preloaded and edited before either
parent import. A parser timeout or an unexpected
per-preset error retains a null analysis record and permits remaining cases to run.

## Saved offline compile evidence

Supply `--compile-manifest path/to/manifest.json` to the batch exporter. It
consumes saved CPU translation/offline GLSL compile results; it does not invoke
a compiler, equation evaluator, GPU or renderer. Existing
`corpus_worker.compatibility_for` and `shader_compat.check_shader` can prepare
reports with explicitly declared sampler/texsize inputs. Preparation itself is
source parsing/translation/compilation, never shader execution. Freeze tool and
source identities and retain the descriptor assumptions; injected declarations
are not proof that textures actually load or bind in a later native run.

The manifest is a JSON object with schema_version1, kind
`source-offline-compatibility-set`, explicit profile, engine/archive identity,
compiler_inputs translator/validator SHA256, false native_driver_verified and
runtime_texture_bindings_verified, a nonempty binding_assumptions string,
`presets` keyed by full-file preset SHA256, and record_sha256 over the object
without that hash field. Each preset value maps warp/composite to the complete
existing check_shader report. Missing preset/stage entries remain unresolved.
The seal checks integrity; it is not producer authentication.

Accepted/rejected reports retain native-profile and input-loading conditions.
Source, request, stage, profile, engine/archive and compiler identities must
match. Runtime-certification claims, malformed/status-contradictory results and
stale source are rejected. Manifest file bytes join run/cache identity and must
stay unchanged before/after each preset, including the last result. Direct API
`export_preset(..., compile_manifest=manifest)` accepts the same sealed object;
choose this or direct compatibility, not both. Provenance includes
`offline_compile_evidence` with assumptions and matching manifest identity.

## Direct API

```python
from effect_families import analyze_families
record = analyze_families(parsed_source, profile="gles300", compatibility=None)
```

`parsed_source` is the existing native reader payload with values, sections and
parser_inputs. Apply its declared case-insensitive settings policy as
`forecast.read_source` does. Exact preset bytes supply `preset_sha256`.
Optional `numbered_source` text supplies original key and physical line evidence.
Without that text, section hashes and graph paths remain available.

`compatibility` accepts the existing source-bound warp/composite compatibility
records. Bound rejection suppresses the rejected custom stage and selects its
native fallback. Missing/stale evidence retains conditional source mechanisms;
it does not establish an active custom shader. Unsupported lowering or complexity
remains explicit in `unknowns`.

## Semantic record

The result contains these fields:

| Field | Meaning |
|---|---|
| `schema_version`, `analysis_policy`, `basis` | Schema1, versioned interpretation policy and source-symbolic evidence basis |
| `preset_sha256`, `parsed_source_sha256` | Exact `.milk` bytes when supplied; parsed values/sections/parser identity |
| `profile`, `compatibility_sha256`, `stages` | Declared target and source-bound actual/conditional stage selection |
| `families` | Multiple mechanism descriptors; a preset can contain several |
| `visual_description` | Separate versioned structured baseline/colour/audio-control descriptor; see `SOURCE_APPEARANCE.md` |
| `unknowns` | Unsupported live forms, unresolved stages and explicit complexity limits |
| `analysis_work` | Deterministic symbolic-work counts and declared finite budgets |
| `uses_shader_execution`, `uses_equation_execution`, `uses_rendered_images` | All false |
| `appearance_prediction_complete` | False; a mechanism is not a complete visual scene |
| `mood_labels`, `genre_labels` | Empty; no assumed audience mapping is applied here |
| `limitations` | Scope and interpretation boundaries |
| `record_sha256` | Canonical JSON digest with this key omitted |

Each family descriptor has `mechanism`, `stage`, `component`, `status`,
`parameters`, `input_dependencies`, `conditions`, `contribution`, `appearance`
and `evidence`. Evidence records source section/hash, graph path, reason, and
original numbered keys/physical lines where supplied. Locations identify the
section containing a recognized mechanism, not an exact highlighted token span.
Parameter values can be null when the expression is dynamic or unproven.
Dependencies use the parser/IR's names, including packed shader uniforms;
preserve those names and their original stage context.

The CLI wraps this in an envelope with `export_kind: preset-effect-families`,
`status`, `preset`, `analysis`, `provenance`, `cache_key`,
`uses_rendered_reference: false` and `appearance_accuracy_verified: false`.
The corpus writer adds `run_identity` and exact relative preset metadata.
Failures use `analysis: null` with an explicit error type and reason; they are
not records asserting that no effects exist.

## Recognized constructions

| Mechanism | Source evidence | Intended interpretation |
|---|---|---|
| Polar radial sampling | Contributing angular and reciprocal/log radial coordinates in the same sample | Tunnel/depth candidate, conditional on sampling, content and projection |
| Periodic radial glow | Contributing saturated inverse-radius falloff around a repeating cell centre | Repeated glow generator in its mapping plane; final spots/particles/coverage are not certified |
| Radial feedback transform | Complete contributing radial scaling of previous-frame sampling | Feedback zoom; radial zoom alone does not identify a tunnel |
| Angular mirror fold | Reflection and periodic wrapping on the angular dependency | Kaleidoscope construction; report proven sector count where possible |
| Radial twist | Paired spatial rotation/curve coordinates with radial phase | Swirl construction; unrelated trig calls are insufficient |
| UV/image/gradient advection | Displacement reaches a later contributing sample | Flow; distinguish procedural, image-driven and gradient mechanisms |
| Complex quadratic recurrence | Both lanes of the same loop-carried complex state reach output/control | Julia/Mandelbrot style only when initial state and parameter roles are proven |
| Iterated spatial fold / Mandelbox recurrence | Loop-carried box reflection; stronger sphere and affine construction where proven | Fractal/folding mechanism, not a guaranteed fractal-looking image |
| Nonlinear feedback map | Contributing nonlinear complex/folding map of previous-frame sampling | Temporal feedback construction |
| Built-in/custom wave, radial curve/band | Active primitive configuration and symbolic position construction | Wave/ring/curve mechanism; preserve dynamic mode and visibility conditions |
| Dot cloud / repeated shapes | Point submission or instance-dependent shape geometry | Particle-like primitive; no independent particle simulation claim |

Detection traces contributing data and consumed lanes. Unused helpers, overwritten
coordinates, unrelated loop slots, zero contributions and statically disabled
components must not provide effect evidence. Branch and opacity conditions remain
attached to contributing mechanisms. Equivalent temporaries/helper names do not
change a mechanism. Unsupported stateful EEL loops/memory and unrecognized live
forms remain unknown. A shared DAG is normalized without expanding it into an
exponential tree; finite work/term budgets abstain rather than silently truncate.

## Consumer boundaries

This record is separate from the unchanged47-field simulated feature record.
Join records by exact preset SHA256, then check source/model/context compatibility.
The semantic export is not a scene graph, palette, executable shader, pixel-level
reconstruction, visual accuracy score, flash certificate or audio-reactivity
magnitude. Use it to select mechanism candidates and explain their source causes.
Use declared numerical evidence when a decision needs activity, flashing, palette,
motion speed or response strength. Moods/genres/age preferences remain explicit
downstream assumptions, never facts inferred from a family name.

For a Rust/wgpu adaptation, choose an original implementation of a supported
mechanism, preserve proven parameters and dependencies, and provide explicit
defaults for unknown resources/conditions. Do not pretend these descriptors
uniquely recover authored composition or certify native4K performance.

The source research cites primary authoring/math references and exact bundled
positive/negative witnesses in
`docs/superpowers/research/2026-10-09-static-effect-families.md`.


## Measured cost

On this Apple M4 Pro/48GiB macOS host with Python3.14,100 fixed content-hash-
selected bundled presets took25.61s total cold (mean.256s, median.243s, p95.351s,
maximum.548s), including parsing, detection and cache writes. The cached pass
took.704s total,7.04ms mean, with100cache hits. Peak process maxRSS was106.69MiB.
This is a static-work timing sample, not classification precision/recall or a
whole-pack duration guarantee. It contains no simulation/audio/frames. Preserve
`fixtures/static-effect-family-benchmark-2026-10-09.json` for its exact inventory.
