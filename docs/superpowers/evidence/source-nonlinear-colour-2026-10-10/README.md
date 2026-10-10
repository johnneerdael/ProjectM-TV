# Nonlinear source colour ranges

The additive `nonlinear_texture_colour_bounds` record propagates conditional
unit-RGBA sample domains through scalar products, dot products, clamps, constant
powers/roots, comparisons and interpolation. It uses symbolic source expressions;
no image, audio, time/frame sample, shader or equation execution feeds the result.
The declared sample range is an input premise, not an observed texture/storage proof.

Finite native Q-upload domains are checked before outer clamps. Unsupported lanes
retain explicit unknown reasons; independently known RGB lanes survive. Complete
RGB boxes require all three lanes. Local projection has a 4,096-node/depth-64
budget. Value bounds give no sensitivity, continuity, visible flashing, whole-loop
contraction, persistence, calibrated mood or appearance credit.

Pinned projectM lowering inserts absolute values for applicable powers/roots,
but its literal exponent-one exception preserves the sign. Do not replace these
rules with generic shader expectations. The original MilkDrop2.25c source loads
`data/include.fx` in `vis_milk2/plugin.cpp:1403`; that external include is absent
from the supplied original code checkout. The separately supplied MilkDrop3
Milkdrop2 include at `code/resources/Milkdrop2/data/include.fx:122` uses lum
weights .32/.49/.29, also present in the pinned projectM header. Their sum is1.1;
this is not a normalized luminance definition or proof of identical compilers.

Review found that a bad red-channel upload discarded valid green/blue constants.
A failing exact regression preceded per-lane recovery. Independent follow-up
review found no further actionable issues;44 focused nonlinear/value/feedback
checks and187 integrated source-appearance checks pass.

## Fixed sample evidence

All100 original presets retain structured descriptions, exact source/hash joins,
paired JSON bytes and ZIP CRC. The model bounds69 stage RGB boxes (39warp,
30composite) across56presets;13stages across12presets retain partial bounds.
It exports228 known channel ranges. Compared with the preceding affine model,
35previously unavailable complete stage boxes occur across29presets.23presets
previously had no complete stage box at all: total preset coverage rises33→56.
These are colour-range counts, not resolved-feedback or classification counts.

Sum of per-preset export times39.113654seconds; maximum2.411822seconds on this
host. The comparison reuses the sealed offline source34 compile manifest;
source34 matches the latest published2.3.36 AAR bytes under the declared context.
Published full AAR SHA256:
`a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3`.
Published-AAR numerical runtime qualification remains pending independently.
No native engine, authored preset, shared device or full corpus was changed.

Raw archive:
`build/preset-corpus/source-nonlinear-colour-2026-10-10/batch-000001.zip`.
SHA256 `c203fd099c9a10314c13b688c1f0384d616520dfddc5eeac46406f4470393ad6`.
Exact reader, engine/patch, manifest and model hashes are in `census.json`.

## Validation

The prepared complete analyzer suite passes **2,727tests and92subtests in
156.95seconds**. Strict MkDocs and whitespace checks pass. These validate
source interpretation rules and export integrity, not whole-preset mood or
visual accuracy. Logs are retained under `build/preset-corpus/` as
`source-nonlinear-colour-suite.log`, `source-nonlinear-colour-focused.log`,
`source-nonlinear-colour-docs.log` and the preserved failing partial-lane control
`source-nonlinear-colour-partial-red.log`.
