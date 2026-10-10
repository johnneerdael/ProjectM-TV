# Stims dependency component adoption

The small Stims predecessor-source fixpoint method is adapted into
`tools/milk-analyzer/source_stims.py`. It supplements the existing native typed
graphs with **may-dependencies of main private scalar state**. It does not
substitute values into those graphs, tighten bounds, prove nonzero derivatives,
or certify a visible audio response. ProjectM's parser, loading policy, causal
slice and storage boundaries stay authoritative.

## Reuse and target boundaries

Reference: [Stims dataflow implementation](https://github.com/zz-plant/stims/blob/36e902704cab7a3c39bfc0a6b2bf587d8ba7e291/packages/milkdrop-toolchain/src/preset-dataflow.ts)
and its independently authored dataflow fixtures, pinned at
`36e902704cab7a3c39bfc0a6b2bf587d8ba7e291`, under the Unlicense. The adaptation
uses a bounded finite worklist rather than importing the whole VM or its
eight-round cross-program policy.

Each explicit previous-frame local edge closes over that local's final field
and initial dependencies. Initial audio keeps distinct `init:*` inputs; Q uses
the main init snapshot each frame. Custom and per-pixel Q/local mutations never
become main predecessor edges. Shared registers, memory aliases, loops,
native expression-pointer aliases and random-stream/call-count ancestry remain
unqualified. Unsupported/nonfinite arithmetic does not acquire an absence proof.
The existing dead-branch and overwrite slicing is reused.

Fifteen pytest controls pass, including the native reset/init isolation cases,
negative-sqrt audio ancestry, unsupported memory and pointer aliases, long-chain
closure and budget refusal. Four independently rewritten supporting EEL controls
exercise epsilon equality, sequence return values, unselected assignments and
negative sqrt. Their source lineage is retained in
`tools/milk-analyzer/fixtures/stims-supporting-source-controls.json`.
The earlier 14 controls plus existing effect-family and Q-boundary suites passed
106 tests; the additional comparison-order control then passed in the 15-test
Stims suite. The controller runs final combined integration checks separately.

## Measured source-only contribution

The first frozen completed census uses all **9,606 unchanged source presets**.
There are no thrown terminal failures: 2,461 records have source may-dependencies
and 7,145 retain explicit partial uncertainty. These are the **pre-RNG-guard**
model's terminal classifications, preserved with its exact hashes in
`full9606-manifest.json.gz`; they are not final-guard full-pack classifications.

| Endpoint category | Presets gaining current-audio ancestry | Outputs | Band paths |
|---|---:|---:|---:|
| Native main render-control fields | 470 | 1,275 | 2,496 |
| Main Q snapshots, potential shader/mesh inputs | 549 | 2,346 | 4,834 |
| Private temporaries | 934 | 5,243 | 12,227 |

Categories overlap: the combined total is 1,349 presets, 8,864 output variables
and 19,557 band paths. These counts describe main-frame source endpoints.
Custom shaders, per-pixel overwrites, opacity and later composition may discard
them. Q counts do not prove an authored shader consumes each lane. Private
temporaries are not counted as drawn controls.

For example, `$$$ Royal - Mashup (316).milk` reads `dx_residual`/`dy_residual`
into `dx`/`dy` before updating those locals later in the frame. Closure exposes
their `bass_att` ancestry through `bass_thresh`; their scalar magnitude and
unqualified initial values remain unknown. This is an actual newly explained
source path rather than a numeric response estimate.

The census took **221.90 seconds** wall time with four source workers, including
native parsing and process overhead. Dependency analysis accumulated **33.97
worker-seconds**, averaging **3.536 ms/preset**, maximum **44.97 ms**. This is
component cost, not end-to-end predictor speedup. The runner freezes one reader
executable per worker and each source input per request. A preliminary aborted
run that copied the executable anew per preset is retained outside qualification;
macOS launch overhead motivated the lifecycle change.

## Final guard qualification

The final component adds an explicit unknown for random-stream and cross-phase
conditional call-count dependencies; it does not borrow Stims' RNG host model.
It was tested against the **unchanged seeded 2,000 sample** using the exact source
inventory from the solver census. All 2,000 complete: 1,491 partial and 509 source
may-dependency records. The final sample has 279 presets with newly exposed
current-audio ancestry, 1,978 output variables and 4,460 band paths; its separate
endpoint counts are in `finalguard-fixed2000-endpoint-counts.json`.

Final sample cost is **46.24 seconds** wall time, **6.834 worker-seconds** of
dependency analysis, **3.417 ms** mean and **43.90 ms** maximum per preset.
Explicit unknown annotations differ on 560 presets. A canonical comparison of
all added-audio dependency sets against those presets' saved full-pack rows
finds **zero dependency-set differences**. No numeric bounds or appearance
predictions change. The final guard has not been rerun across the entire pack.

The original sample summary's comparison mistakenly treated output-array order
as a dependency difference, reporting 100 cases. It is preserved unchanged.
`finalguard-fixed2000-comparison-audit.json` records the corrected order-independent
comparison and both original row hashes; the runner regression control covers
reordered outputs, changed uncertainty and a real dependency change. This was a
comparison-only audit of saved rows, not a preset rerun.

## Supporting component decisions

[eel-wasm's expression fixtures](https://github.com/captbaritone/eel-wasm/blob/4bae490f6e0e397264a0269de69d47a59079b0d5/packages/compiler/tools/testCases.ts)
provide useful independent native-quirk regression ideas. Its parser/runtime and
x87/WASM arithmetic model are not imported. Supporting fixture reuse adds
coverage and no additional bounds or corpus predictions.

[milkdrop-preset-utils](https://github.com/jberg/milkdrop-preset-utils/blob/ba5a4e445300be0dad5e43a6d7f2638c6f02b7f8/src/index.js)
provides a useful default-table counterexample: its main `mv_a=1` and shape
`border_a=.1` differ from our target constructor defaults of zero. The fixture
pins these differences so foreign host defaults are not silently adopted.
Neither its text parser nor its defaults replace the native reader.

Precision tools were inspected separately; the controller owns their exporter
and actual backend experiments. No precision-tool result is claimed by this
Stims evidence. No equation/shader execution, source rendering, framebuffer
comparison, visual simulation or device work occurred here.

## Reproduce

```sh
build/preset-lab-venv/bin/python -m pytest tools/milk-analyzer/test_source_stims.py -q
build/preset-lab-venv/bin/python tools/milk-analyzer/source_stims_validate.py --reader build/preset-corpus/source29/adapters/milk-native-reader --output build/stims-final-qualification --sample-manifest build/preset-corpus/source-z3-fixed2000-2026-10-10/manifest.json --prior-rows build/preset-corpus/source-components-stims-frozen-reader-full9606-2026-10-10/rows.jsonl.gz --workers 4
```

Use a new output path for each frozen run. Evidence manifests retain every
source hash, reader/model identity and terminal row. Gzipped manifests decompress
to the exact originals; row files retain their original hashes. `validation.json`
records adapter, runner and supporting-fixture identities at the original guard
checkpoint. The subsequent public-entrypoint repair is recorded below.

## Public-entrypoint cache repair

The combined export found a lifecycle bug absent from the census: after the
ordinary family analysis closed its `_CACHE` scope, the public dependency
entrypoint lowered the next phase without a structural-identity cache. Comparing
branches then recursively expanded shared DAG nodes rather than interning them.
The exact `Flexi - alien web bouncer [39].milk` request remained CPU-bound for
over five minutes before the owned export was stopped. Its traceback is retained
in `build/preset-corpus/source-components-final-controls100-2026-10-10.log`.

The public entrypoint now owns a cache when none exists, reuses an existing
caller-owned cache, and resets its own token in `finally`. Semantic-budget
exhaustion returns an explicit unresolved supplement rather than failing the
whole export. Shared-DAG call-count, context ownership, exception cleanup,
budget failure and the exact preset controls fail before the repair and pass
afterward. The Stims suite now passes **20 tests**.

The repaired exact case has preset SHA256
`01c261905b54396702c9894c3752c6016511b5be5f9ea86f2c04fd22dfa2f576`,
reader SHA256
`754e4f4129db585cb4f7d5bee915d6bb24ac10ab25901ee7ef0832ce50744afc`,
and the declared GLES300 profile. With the original source-bound compile manifest,
input scenario and SymPy/Z3 workers, standalone dependency analysis completes in
**32.97 ms** and the combined export in **0.672 seconds**. Its dependency records
match exactly across standalone and caller-cache contexts; the export is computed
while dependency uncertainty remains partial. `public-cache-repair.json` retains
the exact source, engine, manifest, scenario and repaired adapter identities.

Repaired adapter SHA256:
`5aea56ca6a708951f5c3991f6439eaeb41b3bb3e999874dcb0b1f1f58e9f792b`.
The archived 9,606-preset and final 2,000-preset censuses already supplied the same
cache scope explicitly, so this repair does not require another source corpus
run. Their original hashes and classifications remain intact; they did not prove
the previously broken standalone entrypoint. Broader combined-export and final
suite qualification follows separately in the controller's evidence.
