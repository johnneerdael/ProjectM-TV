# Declared audio-domain shape material differences

The exporter now supplements ordinary shape material records with caller-declared
audio value domains. `scenario_material_envelope` uses existing scalar interval
math, float32 endpoint conversion, native modulo policy and consumption gates.
It retains source input names, declared ranges and a scenario hash. Ordinary
`material_temporal`, hazards and time schedules remain separate and unchanged.

Conditional `activity.flashing.scenario_material_jump_bounds` reuses the existing
two-state blend difference ceiling with those extra channel domains. It retains
fixed geometry/barycentrics, destination RGB `[0,1]`, untextured material and
ordinary lifetime-area premises. It does not infer a frame-to-frame jump, audio
derivative, screen prominence or visible flash frequency. Missing bands,
persistent state, unknown texture RGB/alpha and native overflow remain unresolved.

Eight controls pass, including independently checked additive colour differences
and opacity/destination contrast. For `r=r2=.2*bass`, alpha `.5` and bass `[0,2]`,
the incoming red ceiling is about `.2`. For constant RGB `.25` and
`a=a2=.1+.2*bass`, the over-blend difference ceiling is about `.3` for destination
in `[0,1]`. Enumerated independent input/destination pairs remain below that
ceiling. Declared zero alpha excludes fill consumption only in the conditional
model. Large swings keep possible modulo crossings with no invented timing.

The [official authoring guide](https://www.geisswerks.com/milkdrop/milkdrop_preset_authoring.html)
distinguishes immediate bands from damped `*_att` inputs and documents audio-driven
custom shapes. It does not provide a universal upper bound or input time rate.
The declared `[0,2]` audit profile is therefore a caller assumption, not an engine,
genre, track or audience guarantee. Current native colour modulo remains distinct
from original MilkDrop2's packed-byte path.

Qualification uses the identical fixed 2,000 source selection, exact source34
reader, saved compiler proofs and existing scenario hash. Results are stored
locally under `build/preset-corpus/source-remaining-budget-2026-10-10/shape-scenario-2000/`.
No equations, shaders, audio simulations or rendered images execute. The full
latest published AAR remains v2.3.36 with SHA256
`a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3`;
this feature does not alter engine or authored presets.

## Qualified coverage

The frozen 2,000 replay finishes in 267.57 seconds with 2,000 structured reports
and no lost descriptions. A full comparison against a00712e3, removing only the
new conditional fields and record/work hashes, finds zero ordinary semantic
changes. Existing hazards, motion, source inventories and unknowns stay intact;
56 presets retain per-field budget reasons.

1,218 presets export conditional material difference records; 657 have at least
one complete local blended-RGB ceiling. 58 have a matching element/part ceiling
that was incomplete in the ordinary material model. Groups are per-preset unions,
not numbers of visible flashes. `coverage.json.gz` lists exact source names and
hashes; the comparison and summary preserve every terminal case and model/tool
identity. No new mood or full appearance accuracy is established.

The prepared suite passes 3,135 tests plus 92 subtests in 204.52 seconds.
Independent review passes 42 focused scenario/material/modulo/Grind controls.
All 100 control reports retain structured/schema-valid output; 53 contain the
new conditional records. Strict MkDocs and diff whitespace checks pass.
