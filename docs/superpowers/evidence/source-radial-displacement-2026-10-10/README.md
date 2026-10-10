# Radial zoom composed into native feedback displacement

This source-only checkpoint connects the existing positive radial-zoom envelope
to the native displacement calculation, then to supported shader lookup response.
It constructs no frames and observes no image contents or audio histories.

## Proof and target semantics

The static mesh radius is `hypot(x*aspectX,y*aspectY)` with mesh positions in
`[-1,1]^2` and positive native aspects no greater than one. The nominal radius
therefore lies in `[0,sqrt(2)]`; authored per-pixel `rad` writes do not replace
that buffer. Source34 `PerPixelMesh.cpp` lines 187 and 334 consumes that radius
for the CPU nested zoom power after native float conversion. Original MilkDrop2
`milkdropfs.cpp` lines 1877–1892 applies radial zoom before stretch.

Let radial inverse scale h(p) lie in the proved interval. For fixed-frame rotation
R and inverse stretch S, `(R*S*h(p)-I)*p` has a uniform pointwise operator ceiling
from rotation, maximum diagonal magnitude and diagonal deviation. Its RMS is
bounded by that ceiling times the uniform-square RMS radius. Centre/translation
and procedural warp retain separate triangle terms.

All ten native controls must be uniform with finite native endpoint domains.
Positive radial power, reciprocal/stretch, warp-scale/speed and underflow/overflow
guards remain. Signed stretch is allowed away from zero; no new negative-zoom
power policy is introduced. Exact affine coefficients stay on the exponent-one
branch. Radial records carry interval bounds rather than exact integrals.

## Controls and review

Fixed 100-preset coverage: native displacement bounds grow 26→35, including nine
new radial cases. Default composed shader-lookup displacement grows 16→22, adding
six presets. Eight presets have separately identified scenario transport results;
the nearest-feedback hazard group remains three. All original source hashes,
100 structured descriptions and execution-unknown inventories are preserved.
Exact affected names are in `radial-displacement-census.json`.
Remaining source displacement reasons: 35 unresolved affine/radial domains,
17 with other controls lacking uniformity, and eight with incomplete finite endpoint
domains. These are interpretation gaps, not newly established native defects.

Eleven controls cover positive curved zoom, independent grid/aspect/time/parameter
comparisons, spatial-control refusal, negative/singular/overflow domains, affine
preservation, invalid warp scale, neutral zoom and dynamic signed stretch/centre.
Two positive controls failed before implementation; negative/affine controls
already passed. The obsolete blanket unsupported-exponent case was removed from
the older displacement parametrization and replaced with radial-domain controls.

Independent review ran 40 focused controls including exact-profile Grind and found
no actionable issues. The existing radial descriptor is reused rather than
recomputed. No traversal limit or authored preset source changed.

Final qualification: 3,012 tests and 92 subtests passed in 176.05 seconds.
All 100 exports remain structured and validate the current JSON Schema. Strict
MkDocs and diff whitespace checks pass.

Local preserved outputs under `build/preset-corpus/`:

- `source-radial-displacement-red.log`
- `source-radial-displacement-2026-10-10/`
- `source-radial-displacement-suite.log`
- `source-radial-displacement-docs.log`

See `SOURCE_APPEARANCE.md` for units and export details. These nominal sufficient
RMS bounds exclude texel alignment, radius/power/native rounding, interpolation,
history, forward motion, actual prominence and mood. No AAR/native code changed.
