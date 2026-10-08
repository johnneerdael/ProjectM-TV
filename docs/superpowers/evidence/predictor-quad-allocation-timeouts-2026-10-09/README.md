# Predictor research: avoid per-segment framebuffer allocation

Date: 2026-10-09. Baseline predictor commit: `82d3db10` on
`feat/predictor-visual-loop`. Classification: predictor CPU performance defect;
no evidence of an AAR defect or incorrect authored presets.

## Confirmed cause

`motion_vectors.py:164` calls `draw_quad_lines` separately for every vector.
`quad_lines.py:128` validates/copies the complete framebuffer, then calls
`primitives.draw_triangles` per quad; that function validates/copies it again.
Custom waves also call the latter once per segment. A 854×480 float32 RGBA
framebuffer is 6,558,720 bytes. For 2,961 vectors, two framebuffer copies per
vector imply about 38.8GB of copied bytes per frame, before validation scans.
The cost is disproportionate to the few pixels actually affected by each line.

Three exact saved corpus timeouts were inspected read-only:

| Original preset | Source SHA-256 | Mechanism |
|---|---|---|
| $$$ Royal - Mashup (103).milk | 08ead3db478aa81c0e29efccc0d9c38bbe69180435123531cbafbf2beb347463 | Enabled 64×48 motion grid; 2,961 in-bounds vectors |
| $$$ Royal - Mashup (113).milk | 5a15da0f2d10a9f4d1221170b47238a676f216204c1933f4cd094d2e200c78e9 | Custom wave quad segments; 8,182 triangle-draw calls in frame 0 |
| $$$ Royal - Mashup (116).milk | 2495ebcc7939854acb7b80398a556ca1505e68dc506a63647fb4df2fad74201d | Custom wave quad segments; 8,187 triangle-draw calls in frame 0 |

Original one-frame profiles and recorded timeout diagnostics support this
attribution. One actual preset frame, including setup, cost 12.44s for 113 and
14.68s for 116. The zero-feedback first frame of 103 does not yet draw motion;
its standalone full-grid draw cost 6.85s. Use frame 1 to include that path.

## Isolated candidate

The patch uses zero-context hunks (`git apply --unidiff-zero` in an isolated
checkout only; do not apply during a frozen run).

`candidate-batch-drawing.patch` gathers the already generated quads into one
triangle call per strip/vector batch. It preserves each vector's independent
endpoints, original triangle order, float32 vertex operations, coverage,
per-triangle alpha blend and quantization. No geometry or shader math is changed.
Existing drawing functions still own copies of the caller's framebuffer.

The isolated candidate reduced the standalone motion draw 6.85s → 0.554s.
Original/candidate output arrays were byte-identical and inputs unchanged.
Two actual 480p frames per affected preset were then run with identical frozen
original audio, assets, clocks and random ledgers. All six display/feedback array
pairs and all 47 feature objects per preset matched exactly. See
`two-frame-comparison.json`. Candidate drawing tests: 80 passed, 8 subtests. Sixteen additional overlapping/
clipped strip controls cover open/closed, additive/alpha, quantized/unquantized
and retained-window coordinates; all are byte-identical and leave inputs unchanged.

This limited comparison does not certify all 60 frames against the old predictor;
old full runs reached the 300s deadline and are not repeated unchanged. Full 60-frame candidate completion results are recorded in `full60-results.json`:
103 completed in87.78s,113 in233.18s and116 in199.46s. All produced47-key records
within the original300s deadline. Preset103 retains six legitimate unknown
feature values;113/116 computed all47. This is not full60-frame equality evidence
against the old timed-out predictor or a native appearance certificate.
Profiling was concurrent with the user's corpus and other host jobs, so timing
ratios are illustrative, not controlled throughput benchmarks or new corpus ETA.

## Native/reference intent

Original MilkDrop2.25c `vis_milk2/milkdropfs.cpp:1239–1384` collects vector
endpoints and submits a row with `D3DPT_LINELIST`; custom waves at 2749 use a
line strip. The release29 production `MilkdropPreset/MotionVectors.cpp:216–248`
submits the quad vector batch as instanced triangle strips. Neither requires
copying a whole framebuffer per CPU-simulated segment. The candidate continues
to target the established ProjectM-TV quad coverage, not MilkDrop2 pixel parity.

## Isolation and reproduction

Live predictor modules, controller, devices, inputs and corpus outputs were not
edited. All research used copies under
`build/preset-corpus/timeout-investigation/{analyzer,optimized}` in the predictor
worktree. Scripts in this folder show one-/two-/60-frame diagnostic setup. They
expect those copied modules and the prepared release29 adapters, original frozen
input folder and Python environment; they are research scripts, not an installed
replacement corpus launcher. Original presets are included unchanged.

The candidate is not installed into the running corpus. A code change alters its
frozen run identity; installation requires a stopped run and a separately
identified output folder or an explicitly implemented/verified migration. Do not
edit live Python modules or rewrite sealed timeout records to make them successes.
The full-corpus source/visual accuracy acceptance gates remain separate.


## Handback status

Root cause confirmed; isolated optimization and focused numerical controls pass.
No production predictor modules or AAR were changed. The candidate remains an
integration task: stop the active run, implement regression coverage in the real
predictor, run the prepared suite, and use a new identified output directory.
Keep old successes/timeouts and sealed archives intact. A verified resume/import
migration would be a separate change; the current runner refuses mixed identities.
The running corpus code hashes were independently confirmed unchanged.
