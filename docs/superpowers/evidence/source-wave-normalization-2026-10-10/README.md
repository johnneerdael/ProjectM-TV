# Built-in waveform normalization boundary size

The fixed 2,000 sample contains 65 existing `wave_material` records reporting a
possible normalization threshold crossing. The activity exporter previously
omitted that mechanism from its flashing hazard list.

Current source34 `MilkdropPreset/Waveform.cpp` lines 320–350 and original
MilkDrop2 `vis_milk2/milkdropfs.cpp` lines 2819–2841 clamp float RGB to `[0,1]`,
then, when brightening is enabled, divide by the maximum component only if it is
greater than float32 `.01`. At the nominal boundary `max(C)=T`, the limiting
difference is `C*(1/T-1)`. Channel envelopes cap `C` by `T`, and exact rational
arithmetic rounds the positive ceiling outwards. A known final alpha weights the
bound while the same alpha, geometry and destination stay fixed.

`wave_material.normalization_boundary_difference` and activity hazard
`builtin_wave_normalization_gate` expose this model. It is not native float32
event certification, a frame difference, full changing-alpha blend model, screen
coverage or visible flash frequency. Enclosing component ranges do not prove
that a simultaneous boundary is reached. Unknown brighten flags, alpha, volume
modulation and native channel domains retain nulls; disabled/no-crossing cases
do not become flash-safe verdicts.

Seven controls pass, including the independent seam difference for RGB
`(.01,.004,.002)` with fixed alpha `.4`, and unknown-alpha/volume/enable cases.
The exact 65 affected sources retain structured output and validate the schema;
all 65 have raw nominal RGB ceilings, 44 also have fixed-alpha blend ceilings.
That bounded replay completes in 9.37 seconds with saved source-bound compiler
proofs. No full-corpus rerender is performed. The original 100 controls retain
structured/schema-valid output; three add this hazard.

63 of the 65 affected presets had no prior activity hazard in the saved full
sample. Combining that immutable 221-preset census with these exact 65 rechecks
gives 284 presets with at least one possible flash mechanism. This is a derived
census, not a new whole-pool replay or 284 observed flashes. Other mechanisms,
correlated channel ranges, timing and final visibility remain unresolved.

Complete source names/hashes and coverage are recorded in `coverage.json.gz`.
Source reader/selection/scenario/model identities and all terminal comparisons
are preserved under
`build/preset-corpus/source-remaining-budget-2026-10-10/wave-normalization-65/`.
The prepared full suite and independent review are sealed in `checkpoint.json`.
The suite passes 3,142 tests plus 92 subtests in 183.51 seconds; independent review
passes 34 focused waveform/activity controls. Strict MkDocs and diff whitespace
checks pass. These validate the declared source math, not whole-preset fidelity.
No shader/equation/audio execution, images, presets or AAR changes are involved.
