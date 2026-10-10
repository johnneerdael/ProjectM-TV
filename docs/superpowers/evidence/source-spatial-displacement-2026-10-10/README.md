# Separate spatial native-control displacement envelopes

This source-only checkpoint bounds supported pure controls that vary across the
native mesh. It constructs no frames, executes no equations/shaders and observes
no audio/image history. The uniform affine/radial descriptors remain unchanged.

## Provenance and math

Native reset x/y/radius/angle inputs receive explicit provenance tags. Only those
tags permit coordinate domains; frame variables with the same names and
persistent/shared inputs receive no mesh boxes. Authored coordinate changes remain
their actual expressions. Source34 `PerPixelMesh.cpp` lines 282–313 resets native
inputs before evaluating per-vertex code and reading its outputs. Original
MilkDrop2 `milkdropfs.cpp` lines 1839–1845 provides the corresponding reset order.

Coordinate x/y span `[0,1]` under positive valid native aspects. Float32-outward
endpoint padding covers nominal sqrt2 radius/pi angle limits; target libm or
intermediate accuracy beyond the padding remains an explicit premise. Each of
the ten control expressions must have a finite converted source envelope. Positive
radial powers, stretch/reciprocal/warp-scale guards remain; random/memory effects,
cross-vertex state and unsupported domains are excluded.

The existing radial-factor and displacement triangle algebra is factored into
shared domain helpers. Pointwise varying control domains bound the native operator
and centre term, then the nominal original-area RMS. No fake uniform rows, affine
matrix, exact mesh area, Jacobian/fold count or temporal smoothness is introduced.
`spatial_native_lookup_transport` separately composes the envelope through supported
shader UV response; uniform transport stays unchanged.

## Controls, review correction and preserved evidence

Fixed sample: ten presets gain bounded spatial displacement and five gain
separate composed lookup bounds. Combined ordinary/spatial native lookup coverage
grows 22→27. All 100 structured descriptions, original source hashes and
execution-unknown inventories are preserved. Exact affected names and remaining
domain reasons are in `spatial-displacement-census.json`.

Fourteen controls cover spatial zoom/rotation, independent grid/aspect RMS,
lookup integration, poles/zero crossings, frame-name provenance, authored x writes,
padded native endpoints and state/random/shared exclusions. Initial controls fail
before implementation. The float32 pi endpoint control exposed a too-narrow bound.
Review then found `sin(k)` masking a cross-vertex persistent input: its envelope was
finite but its scope unsupported. The new exact control failed before the projector
was changed to reject unqualified per-pixel snapshots regardless of surrounding
bounded functions.

Independent final review ran 55 focused controls including exact-profile Grind and
found no remaining actionable issues. No traversal limit or authored source changed.

Final qualification passed 3,026 tests and 92 subtests in 176.16 seconds. All 100
records retain structured descriptions and validate the JSON Schema. Strict
MkDocs and diff whitespace checks pass.

Local outputs under `build/preset-corpus/`:

- `source-spatial-displacement-red.log`
- `source-spatial-displacement-2026-10-10/`
- `source-spatial-displacement-suite.log`
- `source-spatial-displacement-docs.log`

No AAR/native code was changed. These conservative source envelopes retain
interpolation, rounding, texel alignment, history and visible intensity/mood as
separate work; unsupported state is not a newly established native engine bug.
