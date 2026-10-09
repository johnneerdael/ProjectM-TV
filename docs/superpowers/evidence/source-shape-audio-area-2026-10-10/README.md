# Source audio-dependent polygon area

Shape elements now export `audio_area_response`. The existing constant-affine
basis analyzer proves radius `b+k·a` for declared current EEL band inputs, then
source algebra expands nominal polygon area `c*(b+k·a)^2`, where
`c=n*sin(2*pi/n)/8`. The export includes the symmetric cross-term matrix,
band gradient, original radius program and independent material factors.

For four sides and `rad=.2+.1*bass`, the per-aspect area polynomial is
`.02+.02*bass+.005*bass^2`, and its derivative is `.02+.01*bass`.
This quantifies nominal size response without audio/frame simulation. It does
not establish clipped area or perceived bass response. Bounds, narrowing,
trig/raster precision, material, overlap and later composition remain explicit.

Twenty test-first controls cover independent area expansion, cross terms,
straight-line aliases, nonlinear/state/time abstention, init audio snapshots,
unknown sides, texture/dynamic material separation, constant radius,
coefficient/derivative overflow, finite float32 conversion domains and native
EEL division guards. The producer's focused set passed 175 controls; independent
review passed 205. The prepared full suite passed 2,383 tests and 92 subtests
in 148.57 seconds. Strict MkDocs and whitespace checks pass. These validate
source-math rules, not whole-preset mood or appearance accuracy.

All same 100 originals export. Fifteen presets contain 27 supported affine
audio-radius shapes; eight of those presets also have known alpha contribution
factors. Thirty-four presets have supported constant-radius shapes. The groups
can overlap. No unknown visible-strength field is promoted to a measured score.
The compact `census.json` records exact filenames/hashes, coefficients, unknowns
and unchanged source joins.

Raw paired batch:
`build/preset-corpus/source-shape-audio-area-2026-10-10/batch-000001.zip`,
SHA256 `1d07b99c8108b0f083140869ebb20efbb82b850e97cbd1fced0c30198c402631`.
ZIP CRC and the original source bytes match the preceding frozen export.

The retained shape projection follows prepared source31 `CustomShape.cpp:252`
and original MilkDrop2.25c `vis_milk2/milkdropfs.cpp:2396`. Source-first control
loading retains the established EEL guards and initialization policy. Native
library code and authored presets are unchanged. The numeric 47-field export
remains separate; no device or duplicate numerical corpus was operated.

This source checkpoint used the qualified v2.3.33 AAR/source31 reference. The
complete v2.3.34 AAR has now been found locally and hash-verified; migration
qualification is separate from the calculations recorded here.
