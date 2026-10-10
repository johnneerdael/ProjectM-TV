# Conditional shape fill prominence envelopes

The new `fill_envelope` complements existing exact constant fan integrals with
conditional material/radius ranges. It does not execute source programs,
render a pixel field or inspect images. Untextured finite vertex domains use
native constant conversion or modulo-cell residual bounds with the established
float32 margin. Possible crossings retain the full finite modulo range;
missing domains and textured materials retain independent gaps.

For nonnegative fan endpoint alpha, clipping is concave. Interpolated clipped
lower endpoints give a valid lower mean, while min(mean of upper endpoints,1)
gives an upper mean. RGB-times-alpha uses the existing barycentric second
moments, clipped lower vertex values and unclipped upper values. A separate
maxRGBupper*alphaMeanUpper cap can tighten the upper side. These inequalities
remain valid with or without source-RGB clipping and do not misinterpret
clipped interpolation as linear. Source-alpha scaling and factor0..1range
are described in the primary
[OpenGL ES reference](https://raw.githubusercontent.com/KhronosGroup/OpenGL-Refpages/main/es3.0/glBlendFunc.xml).
Target `CustomShape.cpp` line401 sets source-alpha blending; original MilkDrop2
fan/source-alpha behavior is referenced in `vis_milk2/milkdropfs.cpp`.

Known effective sides and finite native radius endpoints give nominal squared
polygon-area bounds. A signed range crossing zero has lower area0. Nonnegative
area/material products do not assume temporal/parameter extrema coincide.
Instance sums count overlaps repeatedly. Border/texture/clipping/rasterization,
destination/storage, later shaders and feedback are separate. Incoming term
bounds are not measured brightness or on-screen response. They can be loose.

Eleven test-first controls cover known moments, dynamic alpha/radius, signed
radius, cross-vertex covariance, alpha wrapping/clipping, partial RGB gaps,
texture uncertainty, unbounded radius and repeated overlap. All11failed before
implementation. Producer focused199tests pass; independent review passed181
fill/value/material/appearance tests and found no actionable issue.

On the unchanged100source sample:
-57shape area envelopes across35presets; three dynamic area envelopes in two
 presets are new beyond the constant geometry results.
-48shape mean-alpha envelopes across30presets; nine shapes in five presets
 are new beyond the exact material-point results.
-23area-weighted alpha envelopes across15presets; six shapes in three presets
 are new beyond exact point-integral support.
-35shape RGB mean envelopes across21presets, and20RGB-integral envelopes
 across12presets. Counts overlap and do not measure visual/mood accuracy.

All100presets export with matching original source bytes/hashes. ZIP CRC passes.
The preset operations total35.21seconds, maximum1.76seconds for one preset on
this host; sample timings are not a whole-corpus guarantee. `census.json` keeps
per-preset ranges, comparison counts and source/parser/model/engine identity.

Raw paired archive:
`build/preset-corpus/source-fill-envelopes-2026-10-10/batch-000001.zip`
SHA256 `b6b57feaa49857f0f063238dfb03e837798461c80f64b5d478583494bc03e0c8`.
Source34is conditional matching-source analysis for the observed latest2.3.36
full AAR bytes. Published-AAR runtime qualification remains pending separately.
No native engine, authored preset, shared corpus or device was changed.

Final prepared suite: **2,541tests and92subtests pass in149.35seconds**.
Strict MkDocs and whitespace checks pass. These are source-rule regression
checks, not a whole-preset brightness, motion or mood accuracy measurement.
