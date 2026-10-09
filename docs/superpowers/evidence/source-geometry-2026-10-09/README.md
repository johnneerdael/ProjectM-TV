# Source custom-shape geometry and lifecycle

This checkpoint adds `elements[].geometry`, policy `source-custom-shape-footprint-v1`.
For a constant radius and sides, the qualified renderer's nominal regular-polygon
area coefficient is n*r²*sin(2pi/n)/8; multiply by renderContext.aspectY=min(1,H/W)
for its unclipped viewport-area fraction. The containing-circle width is |r|*aspectY
and height is |r|. Signed radius uses the native float32 conversion. Sides truncate
in the defined int32 conversion domain and clamp3…100. Summed instance area counts
overlap repeatedly. Visible coverage, prominence and mood scores remain null.

Reference geometry: prepared source31 CustomShape.cpp195–210/228–259 and original
MilkDrop2.25c vis_milk2/milkdropfs.cpp2347–2380/2400–2405. Both construct the same
regular-polygon fan with source center/radius/aspect and native side limits. The
estimates exclude float32 trig/raster edges, clipping, border width, opacity
conversion, textures, blending, feedback and final composition. Authored low-res
and Native4K engine policies remain unchanged; no engine patch was made.

Prerequisite source-analyzer fixes:

- Configured instance count owns the draw loop; equation num_inst writes do not.
- Main frame config/audio/init-Q and shape per-instance config/audio/main-Q/init-T
  reload correctly. Mutable initialized custom locals and shared registers become
  previous-state inputs; later frame assignments can reestablish constants.
- Init audio/time captures use init:<section>:<variable> identities and do not
  become current-frame audio routes. Plain EELvol/vol_att are local names; shader
  packed volume lanes remain aggregate codes7/8.
- Native EEL_if assignments merge environments for both branches.
- Compound assignments update destinations and participate in write inventories.
  Native guarded division retains eel_divide for unknown denominators; known
  |denominator|<.00001 produces0, as the qualified evaluator does.
- Nested assignment/reference-alias arithmetic remains explicitly unresolved
  rather than being folded as value snapshots. No appearance credit is assigned.

Lifecycle references: PerFrameContext.cpp144+, ShapePerFrameContext.cpp86–134,
CustomShape.cpp104/119–148/195, original MilkDrop2 milkdropfs.cpp2483–2528. Original
T writeback is commented out at2360–2369. Source31 evaluator TreeFunctions.c296–309
uses nonzero if truth;567–586/746–765 define guarded division. Preserve this target
policy rather than substituting another evaluator's epsilon behavior.

Focused appearance/family/export suite passes177tests. Independent final source-metadata review has no findings; it ran the same177
focused tests. Prepared complete suite:2141tests and92subtests pass in128.76seconds.
StrictMkDocs and whitespace checks pass. These are formula/source controls, not
renderer/image certification or calibrated audience matching.

The fixed100 source census gives100computed conditional descriptions,53presets
with shape geometry records and34presets with known nominal area coefficients:
54known shapes out of125recorded shapes. All exact source/model hashes and per-shape
values are in `census.json`. Sum per-preset elapsed28.761553seconds; mean.28761553.
The previous23switch-site presets remain23. This is source-only sample coverage,
not whole-pack coverage or a simulated47-field result. No images/audio/frames ran.

Raw paired batch:
`build/preset-corpus/source-geometry-2026-10-09/batch-000001.zip`
SHA256 `1ccccc43d862179631d7fe681689468eaff507eec5b58e222aa1eb8dcbaf26db`.
Published reference remains full2.3.32AAR, byte-equivalent31. No device, shared
corpus, native bug report or fresh appearance capture was involved.

Remaining work: clipped/overlap/opacity contributions, motion and feedback
interaction, then calibrated mood/preference matching. Geometry is useful baseline
size information; it does not grant Chill eligibility or a visible flash strength.

The before/after source inventories match exactly. Ten of100presets changed
parameters or audio-route traits through the lifecycle/math corrections; see
`descriptor-changes.json`. This measures changed interpretation, not an image
accuracy improvement.

Current documented contract + three matched known-geometry source/JSON examples:
`/Users/jneerdael/Downloads/ProjectM-TV-source-geometry-contract-2026-10-09.zip`.
CRC and every listed file hash pass;78,344bytes, SHA256
`03af1df0d3154d0478d448df9da2c6663d9ef7adc1dbeb88e87cc4b218db9486`.
The previous frozen ten-preset review is unchanged. JSONSchema remains a documented
shape contract; no installed formal JSONSchema validator was run.
