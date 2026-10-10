# Nonlinear source lookup time-speed bounds

This checkpoint adds nominal partial-time ceilings for supported nonlinear
sampling coordinates. It constructs no frames and executes no equations or
shaders. Its purpose is source-only movement and flashing math under explicit
fixed-input premises, not a claimed visible intensity or mood score.

## Source math and target

For `uv.x + .02*sin(8*uv.y + 3*time)`, the chain rule yields a partial-time
ceiling of `.06` UV units per source second. Spatial coordinates and every other
input are fixed; the nominal sine derivative has magnitude at most one.
[Microsoft's HLSL sin reference](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-sin)
specifies radians. Original MilkDrop2 `milkdropfs.cpp` lines 3946–3975 wraps the
shader clock at 10,000 seconds and supplies it separately from audio/frame/FPS.
These derivatives exclude wraps/resets and native quantization, retaining the
same distinction in the typed source graph.

Latest published release was checked as v2.3.36, commit
`90b5bf9d9f60a13e9e271cc021a7d1133aa8fb3d`. Full core AAR digest is
`a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3`;
the local previously pinned v2.3.34 full AAR has exactly those bytes. Source34
adapters and the source-bound GLES300 compile manifest remain the declared source
target. This digest check is not new AAR runtime or whole-preset visual validation.

`source_sampling_motion.py` reuses scalar coefficient projection and response
calculus. No warped-UV box is supplied; unbounded spatial coefficients, sampled
coordinate chains, discontinuities and active quantized uploads remain guarded.
Original-domain preflight preserves invalid zero products and clears candidate
default/scenario rates. Non-affine inverse feature velocity and total lookup speed
remain null. Existing linear-filter RGB gradient coefficients consume the new
partial-axis ceilings with actual uploaded dimensions as separate inputs.

## Qualification and coverage

Eleven controls cover sine ripples, both axes, zero partial-time motion, RGB
propagation, scenario audio amplitude, invalid/discontinuous/image-driven maps,
unbounded UV gain and independently computed coordinate differences. Six positive
controls fail before implementation and pass after it.

The exact-profile Grind control then exposed a traversal regression. Qualification
was stopped before repair. Review identified a vacuous dependency walk in
`coefficient_envelope` when the selected-input taint set was empty. The conditional
walk is now skipped only for an empty set; active quantized taint keeps its check.
No traversal budget was increased or numeric cache added. All 36 focused controls
pass; independent review passes 42 controls including exact-profile Grind and
reports no remaining actionable issue.

Fixed 100-preset source export: all records computed, all retain structured
descriptions and pass JSON Schema, with unchanged exact source identities and
execution-unknown inventories. Forty-one presets gain previously unknown
partial-time axis bounds across 148 default/scenario lookup rows. Four presets
gain positive ceilings; other new bounds are zero components with the declared
other inputs fixed. Twenty presets gain raw-RGB gradient coefficients, with one
gaining a positive coefficient. Exact affected names, hashes and before/after
axes are in `sampling-time-census.json`.
The prepared full suite passes 3,051 tests and 92 subtests in 186.95 seconds;
strict MkDocs and diff whitespace checks pass. These validate interpretation
rules and preserved source descriptors, not full visual or mood accuracy.

Local outputs:

- `build/preset-corpus/source-nonlinear-sampling-time-red.log`
- `build/preset-corpus/source-nonlinear-sampling-time-focused.log`
- `build/preset-corpus/source-nonlinear-sampling-time-fixed-2026-10-10/`
- `build/preset-corpus/source-nonlinear-sampling-time-fixed-suite.log`
- `build/preset-corpus/source-nonlinear-sampling-time-docs.log`

A zero partial-time rate does not prove stillness or no flashing: native warp,
audio, persistent state and texture history can move or change the picture.
Positive ceilings need not be reached. Full feedback, screen prominence and
Chill/Normal/Intense calibration remain separate work. No engine patch is added.
