# Source control motion checkpoint

The user wants notification only when source-only JSON supports a recognizable
approximate reconstruction by an independent program. That milestone remains
unverified: composition, palettes/materials, screen motion and feedback still need
work. This checkpoint provides named source-control curves, not an image generator.

`source_motion.py`, policy source-time-control-curves-v1, describes constants,
a*time+b drift and single b+A*sin/cos(w*time+p) oscillations. It exports original
signed coefficients/programs, nominal ranges, periods/frequencies and maximum
absolute control derivative in source units per source-time second. It uses the
existing bounded typed phase/literal helpers and neutral affine-time parameter
extractor; shader timing's previous rate API remains available. Zero amplitude
and zero phase rate produce constants without periodic metadata. Unsupported
state/audio/nonlinear/composed curves remain unknown. Visible motion speed and
activity/mood confidence stay null; no shader/equation/frames/images execute.

Feedback controls explicitly apply each feedback step. A constant rotation.02
has zero control derivative yet can rotate sampled feedback each step. FPS,
native warp-time math, composition and visible texture matter for image speed.
Native mesh families and curves share mesh_warp; legacy_ids identifies the earlier
shader_mesh_warp alias, with mechanisms/evidence retained and no double layer count.

Review exposed a source-analyzer caller bug: full main-frame locals were passed
into per-pixel EEL despite a separate native evaluator. The fix restricts copies
to native bindings, loads readonly inputs before main frame execution and Q after,
and reloads ten warp controls/coordinates per vertex. Writable per-pixel Q/readonly
state remains namespaced unknown across vertices. Main locals such as k are not
copied. Native references: PerPixelContext.cpp16/75–104, MilkdropPreset.cpp428–432
and PerPixelMesh.cpp289–298; original MilkDrop2 state.cpp227–228 allocates separate
per-frame and per-vertex VMs. No engine patch/behavior change was made.

193 focused appearance/family/export controls pass. Independent final caller-boundary
review has no findings. StrictMkDocs and whitespace checks pass. Final prepared
complete suite:2157tests and92subtests pass in136.37seconds. These controls do not
establish full-preset image fidelity or reconstruction readiness.

Fixed100 source census:100computed conditional descriptions;98presets with control
records;20presets with known nonconstant time curves (11linear,44sinusoidal).
Other controls:776constant,405unknown. Constants are not counted as moving/quiet
images. Sum per-preset elapsed28.689071seconds, mean.28689071seconds. Exact source/
model identities and all control values are in census.json. No whole-pack coverage
or calibrated mood claim follows from this sample.

Raw paired batch:
build/preset-corpus/source-motion-2026-10-09/batch-000001.zip
SHA2563f14753eee4939cb08039214de822f38a41605fb9563ef50eb644ae70aaa1902.
Publication reference is full2.3.33AAR, byte-identical32/31; no runtime capture,
shared corpus or device operation was performed. Existing47numeric export is unchanged.

Next required work remains feedback recurrence/composition/material descriptions,
clipping/opacity/overlap contributions, spatial motion and calibrated preferences.
Source math/data improvements alone do not meet the user's reconstruction milestone.
