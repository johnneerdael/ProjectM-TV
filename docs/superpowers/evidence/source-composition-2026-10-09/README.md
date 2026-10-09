# Logical source composition checkpoint

The user reconstruction-notification gate remains unmet. `source_composition.py`
adds logical pipeline context, not a complete scene/material graph or an actual
feedback recurrence solution. No frame/audio/shader/equation execution occurs.

Normal main feedback follows previous-main→warp→drawings/filters→retained-main;
normal display follows retained-main→orientation/diffusion exactcopy→composite→display.
Candidate drawing order is shapes0…3, customwaves0…3, then builtinwave, with
motion vectors on previous main and darken-center/borders after drawings. Candidate
configuration and retained display element IDs are separate: an RGB-independent
composite can hide drawings that the engine still puts into its feedback buffer.

Source sampler records retain stage, sampler/canonicaltexture, logicalsource role,
coordinate/extraargument program hashes in this compact census, intrinsic/LOD,
source site/path and sampling policy. Full DAGs remain in the raw paired batch.
Native fixed/legacy stages record implicit main reads; unresolved stages retain
nullread lists. Blur age, detail/diffusion/render settings and runtime bindings
are unresolved. The record universally retains possible stale-composite influence
when warp discards/incomplete writes preserve old backing pixels. Source selection
and domain/termination conditions remain explicit; no certified visible layer or
recurrence claim is made.

Native references: prepared source31 MilkdropPreset.cpp90–382 for normal/detail,
blur/drawing/flip/composite flow; original MilkDrop2.25c milkdropfs.cpp1137–1139
for drawing order. This is published2.3.33's byte-equivalent31 engine contract,
not a modified native library. Native4K/authored-canvas branches remain conditional.

Review reproduced a shared typedconstant dead-slice bug. _number now folds typed
scalars before representation casts and preserves uniform vector/base conversion;
int(.8)=0 removes dead reads/families, int1.8 retains them, and summed/vectorzero
controls pass. Explicit scalar shader float casts narrow tofloat32 before constant
acceptance, so float16777217−16777216 becomes0. Plain EEL literals/arithmetic retain
doublevalues. Mandelbox/fold controls stay green; dead data loops keep execution
uncertainty. These are source-interpreter fixes, not new AAR bug findings.

205 focused appearance/family/export controls pass. Independent final conversion
review has no findings. StrictMkDocs and whitespace checks pass. Prepared complete
analyzer suite:2169tests and92subtests pass in135.98seconds. Tests are not appearance credit.

Fixed100 census:100computed composition records, two with unresolvedstage reads,
77with blur-history reads and1172sampler occurrences. Occurrences are per-stage
source sites, not unique visible effects. Sum elapsed28.741169seconds,
mean.28741169seconds. Exact sources, model hashes and compact composition rows
are in census.json; each composition hash binds the original full record. No
whole-pack coverage or reconstruction-readiness percentage is claimed.

Raw paired results:
build/preset-corpus/source-composition-2026-10-09/batch-000001.zip
SHA2568b66f651edfbf8d3a282cac7f7b4b201120267747599678687642ef2a0bd5b33.
No devices, shared corpus, new runtime captures or AAR engine changes were involved.

Next: quantify supported warp/feedback transfer and resolve useful material/palette
and contribution information. Source edges alone do not meet the user's requested
recognizable approximate look from JSON.
