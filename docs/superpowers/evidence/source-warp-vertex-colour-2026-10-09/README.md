# Source-bound warp vertex colour

The native warp vertex shader supplies `_vDiffuse` as capped float32 main-frame
decay in RGB and one in alpha. `source_feedback.py` now resolves consumed lanes
when analysing constant-affine warp transfer. Dynamic/nonfinite decay stays
unknown, alpha remains known, and unused colour factors do not multiply authored
custom output. The contract does not substitute composite inputs or claim an
observed GPU binding.

Source references: prepared source31
`src/libprojectM/MilkdropPreset/PerPixelMesh.cpp:374` and
`Shaders/PresetWarpVertexShaderGlsl330.vert:96`. The full published v2.3.33 AAR
remains byte-identical to qualified source31's published AAR; no native code or
preset changes were made.

Four authored controls cover constant RGB decay, dynamic RGB uncertainty,
alpha-only use and the upper cap. The initial bare `decay` shader control was
invalid under the reader and was replaced with supported `_vDiffuse.rgb`;
its compile rejection is not credited as a decay test. Independent correctness
review has no remaining findings. Focused appearance/family/export suite:
236 tests pass. The complete prepared analyzer suite passes 2,200 tests and
92 subtests in 127.68 seconds. Strict MkDocs and whitespace checks pass.

The same fixed 100 original presets yield 100 computed records, still 22 known
warp transfers (13 fixed, 9 custom) and 78 unresolved transfers. This change has
no demonstrated transfer-coverage gain in that sample. Summed per-preset time:
29.236261 seconds, mean 0.292363 seconds. Source/record/model hashes and compact
binding outcomes are in `census.json`. Original source bytes and ZIP CRCs were
verified in the paired batch:

`build/preset-corpus/source-vertex-colour-2026-10-09/batch-000001.zip`

SHA-256: `ef77d44277a50be9dd2acb553fe912a93f610a6028c9af410c73da4618b641b8`.

No images, equation/shader execution, devices or shared corpus were used.
These results do not certify reconstruction, overall appearance or mood accuracy.
The recognizable-look milestone remains unmet.
