# Procedural radial glow generators

`source_forms.py` recognizes contributing scalar
`saturate(gain/length(frac(mapping)-cell_centre))` constructions, including optional
per-axis abs. New familycode9 and element.procedural_forms preserve distinct
canonical generator formulas, raw mapping/gain/centre programs and available
phase motion/audio routes. Identical repeated formulas may deduplicate: record
count/IDs are not drawing layers, usage multiplicity or particles. Final masks,
tint/inversion, feedback, precision and composition remain separate.

Positive gain gives a nominal saturation-core radius in generator-cell units.
An interior cell centre with an unclipped disk gives area pi*gain² per cell;
clipped disks retain null area. Inverse-radius tails extend outside that core.
This is not visible pixel coverage. Fully saturated cells and source-proven dead,
alpha-only, nonspatial or rank-one mappings do not claim a varying2Dgrid.
Unknown/nonlinear mappings retain explicit dimensionality conditions. Reciprocal
zero-distance, GPU rounding/interpolation/subnormal and final visibility are not
certified; actual screen coverage/motion stay null.

References: Microsoft's [frac](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-frac)
and [length](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-length)
references define unit-cell fractional range and vector magnitude. Source31
GLSLGenerator.cpp1217–1219 maps frac to fract; original MilkDrop2.25c plugin.cpp3437
compiles authored HLSL through D3DX. Target remains the qualified full published
2.3.33AAR/source31 policy; no native/preset change or image observation was used.

Two predictor errors were found and fixed before this checkpoint. Tolerance-SVD
rank wrongly erased a highly anisotropic but nonsingular map; exact row minors
of exported nominal coefficients now establish rank, without a GPU precision
claim. An EEL name set wrongly treated shader uniforms x/y as coordinates; the
spatial guard now requires typed native shader _uv/_rad_ang varying bases.
Both errors have red-then-green controls. Canonical-form dedup semantics are
explicit in the model, contract and guide and have a regression control.

15 new form controls pass;55 combined forms/sampling/polar controls pass. The
complete prepared analyzer suite passes2255tests and92subtests in137.01seconds.
Strict MkDocs and whitespace checks pass. Independent correctness review has
no remaining findings and independently re-ran the55focusedcontrols, checking
namespace, rank, raw geometry, canonical dedup and conditional claims.

Same fixed100originals:100computed, four distinct generators across two presets,
xtramartin454 and Bdrv yin315 Ocean of Light. All four have nominal unclipped
core-area formulas, while affine mappings remain unknown because their actual
planes use polar/nonlinear transformations. No earlier descriptor was lost.
Exact filenames/source/record/model hashes and compact generator records are in
census.json; full programs/routes remain in the hash-bound raw paired batch.
These are extraction facts, not a wholepack or overall-look accuracy percentage.
Mean per-preset source export.30797179s,sum30.797179s. No performance claim follows
from a single timing checkpoint.

Paired source/JSON batch:
`build/preset-corpus/source-radial-grid-qualified-2026-10-09/batch-000001.zip`

SHA256: `e691f35be3bab0db687a8ded750a1f524fc137cf9729ea49a1f522312ae9e4f9`.
ZIP CRC and all100 original source bytes/hash joins were verified. Earlier
pre-fix runs are retained in source-radial-grid and source-radial-grid-final folders.
No audio/frame/image execution, devices or shared corpus were used. Existing47
numeric output remains unchanged. Full recognizable-look reconstruction and
calibrated mood/preference matching remain unverified.
