# MilkDrop interpretation: research handoff

Snapshot: 2026-10-04. Interpreter worktree: `.worktrees/preset-genre-analyzer`, branch `feat/preset-audience-scoring`. This is a research index, not a claim of complete language coverage or visual accuracy.

Latest targeted recheck: all 371 previously blocked presets were re-read with the
current reader/interpreter. 315 retain source blockers; 56 now pass these checks.
This recheck does not search the other 9,235 files for new regressions. Its count
is relevant to source interpretation, unlike the unrelated stopped 144-score
numerical experiment. Remaining blockers are often invalid/undefined source or
binding/translation context, not absent functions. See
`tools/milk-analyzer/fixtures/remaining-source-blockers-2026-10-04.json` and full
witnesses in `build/milk-analyzer/remaining-gap-recheck-2026-10-04/gap-priority.json`.

## Highest-frequency recorded unresolved families

The refreshed source audit finds 371 of 9,606 presets with known structural gaps,
down from 490 in the previous audit (119 fewer). The other 9,235 pass these checks;
they are not proven behaviourally predictable. Families overlap. Do not sum their
counts or infer appearance accuracy from them.

| Family | Recorded affected presets | Research needed |
|---|---:|---|
| Uninitialized shader reads | 116 | Trace component initialization and native execution. Separate actual undefined values from interpreter binding errors. Do not invent a deterministic result for undefined GPU behaviour. |
| Target parse unavailable | 82 | Remaining witnesses include 16 shader failures, 53 projectM equation-assembly rejections and 13 sections rejected by both assembly modes. Preserve original source; do not silently repair it. |
| Native GLSL array initializer layout | 56 | Trace HLSL array types/constructors through projectM's translator, and establish compilation versus fallback. |
| Sampler-state/binding context | 51 | Source lowering still needs explicit native binding/compatibility evidence; the two reported families overlap completely. |
| Same-name initializer binding | 49 | Establish exactly which local/global value an initializer reads in the emitted GLSL and native backend. |
| Source outside numbered loader | 20 | Establish actual projectM loading behaviour for unnumbered/unsupported sections before interpreting author intent. |
| Arithmetic/comparison effect order | 3 | Diagnose writes/reads across operands against actual native sequencing or undefined behaviour. |

The original sampler-state/dynamic-sampler families each affected 51 presets. They are now substantially diagnosed as native preprocessing/binding compatibility issues; they are not 102 independent missing calculations. Remaining work is integration and broader regression coverage, not assuming authored sampler states control filtering.

Since that full audit, a targeted investigation identified 16 texture-size
declaration binding errors within the uninitialized family. They now lower
completely after matching native uniform rebuilding. The full 371 total above
is the dated audit count, not a newly recomputed total after this fix. Recurrent
uninitialized `rs` origins occur in 39 recorded presets, all with explicit
`0 * rs`. These sections now lower under the pinned generated mult0 rule for
literal-zero products of plain storage. Matrix/texture/index/helper effects and
later live reads stay unresolved. See `2026-10-04-zero-storage-learning.md`.

## Remaining language and maths topics

These are explicit interpreter limitations; corpus prevalence has not yet been measured for every topic.

- General user-helper `out`/`inout` arguments: copy-in/copy-out, aliases, swizzles, arrays and call order. The intrinsic `modf` output is already implemented separately.
- Control flow: `break`, `continue`, branch/loop-dependent helper returns, loop-condition side effects and conditional/logical assignment effects.
- Expression effects: side effects inside index expressions and unsafe/unsequenced arithmetic or comparison updates.
- Matrix semantics: whole-row writes, overfilled constructors and rectangular bare products where the native translator lacks a helper.
- Unsupported bitwise unary expressions: establish accepted types and actual translation before adding numerical semantics.
- Texture projection (`tex2Dproj`) and gradient sampling: homogeneous division, derivative selection, stage availability and actual sampler policy.
- General mipmapped LOD/bias sampling: current work only handles the pinned backend's non-mipmapped base-level samplers; it does not implement an arbitrary mip chain.
- Numerical domains and precision: undefined/nonfinite results, GPU rounding/fused operations and transcendental differences. Defined behaviour must be distinguished from platform-dependent behaviour.

## Integration understanding still requiring work

- Automatic shader random lifecycle assembly, including actual seed, preset loading, fallback instances, other consumers and texture selection. Explicit Android/bionic replay now supports reseeding while preserving shader state. Two CPU-observed published-core lifecycles reproduce 60 random-colour frames exactly; background reseeding occurs during rendering. Whole-event replay still needs to detect or model mid-event interleaving. Lexical shader random references occur in 3,205 presets (overlapping families, not verified live dependencies). See `2026-10-04-core-random-lifecycle-learning.md`.
- Remaining motion-vector/warp feedback raster coverage and precision. Explicit warp and composite subpixel grids now preserve actual original-UV interpolation. Separate UV controls pass, while a fresh feedback control still misses by eight RGB8 bytes; see `2026-10-04-warp-raster-learning.md`.
- Accumulated warp/blur/composite feedback error over time. Correct individual expressions do not prove correct evolving appearance.
- External texture availability, loading/rescaling and native failure/fallback behaviour.
- Calibration of smooth motion, flashing, colour diversity and activity descriptors against actual behaviour. This is separate from structural code coverage.

## Avoid duplicating recent work

Already implemented with targeted evidence: `exp2`, `log10`, `reflect`, reduction binding for `all`/`any`, helper global writes/local scopes/loop-carried state, destination-index capture, and scalar `modf` output/call sequencing. Some mathematically supported overloads still fail the pinned native shader compiler.

Plain sampler alias declarations now follow native removal/rebinding, including deletion of trailing code on the declaration line and preservation of leading qualifiers. See `2026-10-04-sampler-alias-learning.md` and its source-proof fixture.

`tex2Dbias` and `tex2Dlod` base-level interpretation is implemented: 14 recorded source witnesses lower, and four controlled native fixtures match their frozen predictions. General mipmapped sampling remains outside that claim.

Read the dated reduction, helper-state, modf and sampler-runtime evidence alongside their fixtures before proposing changes.

## Reproducible inputs

- Full historical priority index, including preset names, source/preset hashes, section names and line numbers: `build/milk-analyzer/source-gap-audit-2026-10-04/gap-priority.json`.
- Compact historical snapshot: `tools/milk-analyzer/fixtures/source-gap-summary-2026-10-04.json`.
- Interpreter: `tools/milk-analyzer/shader_fields.py`, `field_math.py`, `grid_math.py`, `pipeline_fields.py`, `stage_resolution.py` and `sampling_policy.py`.
- Native parsing/translation adapters and tests: `tools/milk-analyzer/`.
- Published reference artifact: `build/core-audience-analysis/published/projectM-TV-core-2.2.4.aar`, SHA-256 `75e8cbb9ce4ab9340ac9514c16812bbf79e5b3dfa8f29db22d653c601323ce60`.
- Official MilkDrop source available locally: `/Users/jneerdael/Scripts/MilkDrop3`; evaluator: `/Users/jneerdael/Scripts/projectm-eval`. Native MilkDrop and our patched projectM can differ; record which runtime each conclusion applies to.

## Task to give another AI

Choose one unresolved family. Supply (1) precise semantics grounded in native source or a language specification, (2) minimal source examples with expected numerical results, (3) distinctions between defined behaviour, undefined behaviour and native rejection/fallback, (4) proposed interpreter changes and regression tests, and (5) affected source witnesses with hashes. Freeze predictions before executing reference probes. Do not use rendered appearance to silently alter the interpretation, guess missing values, or infer whole-preset accuracy from a small fixture. Do not start another full-corpus rendering run or operate shared devices/emulators.

Best independent starting task: general user-helper `out`/`inout` semantics. The original high-frequency families are better treated as compatibility/initialization investigations than a list of absent intrinsics.
