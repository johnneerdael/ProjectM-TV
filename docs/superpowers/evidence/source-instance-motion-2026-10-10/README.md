# Source shape-instance motion specialization

The new `instance_motion` descriptor specializes the original native iteration
index in existing EEL control graphs, then reuses known geometry, centre-path
and vertex-motion rules. It does not run equations, shaders, time/audio samples
or rendered frames. Supported literal arithmetic, nominal double sin/cos,
native guarded division and known branches simplify after substitution.
Incoming custom state and audio stay unresolved inputs.

Native references: `CustomShape.cpp` lines195–198 and
`ShapePerFrameContext.cpp` lines85–120 in the prepared source34engine.
Original MilkDrop2.25c `vis_milk2/milkdropfs.cpp` lines2508–2509 sets the
instance/count before the shape equation phase. The original authoring guide
also documents instanced shapes and index0through count-1:
[MilkDrop authoring guide](https://www.geisswerks.com/milkdrop/milkdrop_preset_authoring.html).
The patched engine's exact reset/order is the target; no native repair or
preset modification is made here.

Compact rows preserve native indices, supported source centres/harmonic
matrices and known speed bounds. Processed/known counts differ deliberately.
An aggregate speed requires every configured instance to be processed with a
known finite bound. Partial budget stops keep finished rows but no group bound.
Limits1024instances,262144substitution-node visits and depth64are tool budgets,
not a claim that native execution clamps counts. Parent and per-instance
symbolic caches stay separate.

Fifteen controls cover offsets, rotated circles, literal trig, EEL tolerant
branches, guarded division, unknown state/audio, local index writes, native
projection overflow, varying sides and partial/oversized budgets. Twelve tests
failed before the feature existed, then passed. Producer focused201tests pass;
independent review passed159instance/appearance tests and24vertex-motion tests.

The unchanged fixed100sample processes35groups across19presets, containing
6207instances. Only two ellipse paths in one preset become known;6205paths and
all new group-speed bounds remain unknown. This is a small practical coverage
gain, not broad mood or appearance progress. Existing non-instance motion
outputs retain their meaning. Audio/state and more complex time formulas still
need further interpretation; eliminating `instance` alone does not solve them.

The100preset operations total32.96seconds, maximum1.21seconds for one preset
on this host with the frozen source reader/model. These measured sample costs
are not a whole-corpus or hardware performance guarantee. No visual simulation
or native rendering was invoked. `census.json` records compact per-group results,
known rows, source/model/parser/engine hashes and original-source joins.

Raw paired archive:
`build/preset-corpus/source-instance-motion-2026-10-10/batch-000001.zip`
SHA256 `e39ccddd01a2ff45bbb8511160964206f7d0a0f8b75865791d999199881a11ca`.
ZIP CRC and all100full-file hashes match the preceding EEL-equality batch.
Source34matches the observed v2.3.36full AAR bytes; unchanged-AAR runtime
qualification remains a separate pending gate. No shared device was operated.

Final prepared suite: **2,479tests and92subtests pass in142.40seconds**.
Strict MkDocs and whitespace checks pass. These are source-math regressions,
not final appearance, visible movement or mood certification.
