# Nonlinear source feedback colour sensitivity

This checkpoint summarizes raw warp colour sensitivity without executing
equations, shaders or rendering frames. It extends the existing affine-only
colour operators using the already-derived sampled RGBA Lipschitz matrices.

## Math and source boundary

Each raw RGB row sums its nonnegative derivative ceilings across all four sampled
RGBA columns and independent main/blur sites. The maximum row sum bounds the RGB
infinity-norm change for independent input changes in the RGBA infinity norm.
Correlations may tighten the result but cannot increase this ceiling. For example,
`.25*pow(GetPixel(uv),2)` has gain bounded by `.5` on the declared unit sample
domain; an unscaled square has gain bounded by `2`.

`maximum_fixed_coordinate_feedback_sample_gain` holds sample coordinates fixed.
The stronger `maximum_previous_image_colour_gain` additionally requires all active
colour sample coordinates to have a valid image-independent domain proof, main
sampling to be base-level nonmipmapped nearest/linear with repeat/clamp addressing,
no active blur-to-image transfer and no clip/discard. Every active external colour
lookup is also checked: an external lookup addressed by feedback colour would add
an otherwise omitted response path. Unknown/partial rows stay unresolved.

The native frame-wrap selector chooses repeat or clamp; both nominal filters are
nonexpansive for identical coordinates. Unknown addressing receives no credit.
Source34 `MilkdropShader.cpp` lines 502–506 emits `float4(ret.xyz,1.0)`; this
checkpoint retains all four input alpha columns but the raw shader output alpha
is fixed. Original MilkDrop2 `plugin.cpp` lines 3496 and 3627–3634 instead uses
the supplied `_vDiffuse.w`. This distinction is documented rather than overwritten.
Original `milkdropfs.cpp` lines 3913–3934 selects point/linear and repeat/clamp
sampling independently. No renderer changes are made.

Geiss's [authoring guide](https://www.geisswerks.com/milkdrop/milkdrop_preset_authoring.html)
explains that warp results are baked into feedback while the composite displays
the frame, and custom shaders incorporate the former decay/gamma effects. Thus
composite gain is not silently substituted for recurrent warp gain here.

`sufficient_raw_warp_colour_contraction` tests whether the complete previous-image
bound is below one. False is failure of that sufficient test, not proof of
amplification or instability. Stored framebuffer evolution, later drawing,
storage/rounding, native trails and full feedback persistence are not certified.
Default and declared-scenario records remain separate. These are source operator
facts, not observed flashing or Chill/Normal/Intense assignments.

## Controls and fixed sample

Twelve initial controls failed before implementation. The final sixteen controls
cover nonlinear products/powers, independent sites, gain above one, blur input
versus image transfer, nested main/external coordinate paths, input alpha,
singular/threshold/unbounded response, scenario amplitude, independently computed
colour pairs, clip/incomplete writes and missing/mipmap/addressing descriptors.
Sixty focused controls pass. Independent review passes 46 controls including
exact-profile Grind, probes actual authored discard paths, and reports no
remaining actionable findings. No traversal or normalization budgets change.

All 100 fixed source records remain structured, compute successfully and validate
the JSON Schema, with unchanged source identities and execution-unknown inventories.
Forty-four presets have complete fixed-sample gain bounds, including 34 whose old
affine feedback envelope was unknown. Five further presets have partial RGB rows.
Ten meet the stronger previous-image operator guards. Their exact names, hashes,
matrices, default/scenario results and exclusions are in
`feedback-sensitivity-census.json`.
The full prepared analyzer suite passes 3,067 tests and 92 subtests in 183.09
seconds. Strict MkDocs and diff whitespace checks pass. Interpretation-rule and
export checks do not establish whole-preset appearance or mood accuracy.

Remaining frequent exclusions in this sample are active blur-to-image transfer
and valid image-independent coordinate domains. They are explicit missing proof
obligations, not new native library bugs. The source-only model still does not
certify screen prominence or full visible/mood accuracy.

Local qualification outputs:

- `build/preset-corpus/source-feedback-sensitivity-red.log`
- `build/preset-corpus/source-feedback-sensitivity-2026-10-10/`
- `build/preset-corpus/source-feedback-sensitivity-suite.log`
- `build/preset-corpus/source-feedback-sensitivity-docs.log`
