# Conditional shape material change and local flash mechanisms

The source export now relates shape RGB/opacity time variation to incoming and
blended colour variation. It constructs no display frames and consumes no images.
The math and scope are documented in `tools/milk-analyzer/SOURCE_APPEARANCE.md`.

## Fixed sample result

All original 100 sample presets completed using the pinned source34 reader and
unchanged compile/scenario inputs. Exact names and records are in `activity-census.json`.

- 11 presets contain possible local discontinuity sources: 19 shape modulo
  records and three border draw-gate records, with overlapping presets.
- 27 presets have at least one resolved incoming material rate component.
- 25 presets have a shape part with all three incoming RGB rate ceilings resolved.
- Only one preset has a supported positive rate: `InCUbuS - Our Destiny.milk`,
  border RGB ceilings approximately `[0.508600, 0.669800, 0.865600]` per source-time second.
  Other supported components are zero; do not count them as reactive effects.

These are local source quantities at fixed barycentric coordinates, geometry and
destination. They do not certify actual flashes, screen prominence, feedback
evolution or a mood. Possible envelope crossings do not prove events are reached.

## Numerical reasoning and controls

Product-rule bounds retain independent RGB and alpha interpolation. A transparent
centre does not remove centre RGB when edge alpha is nonzero. Source-alpha-over
adds an alpha-rate term under an explicit fixed destination RGB `[0,1]` premise.
Clamped alpha remains nonexpansive. Native modulo-cell stability is required;
upload/packed-byte/storage quantization stays outside continuous nominal rates.

Nine new controls exercise slow colour, opacity, over/additive blending,
transparent-centre interpolation, texture exclusion, modulo crossings, border
draw gates, derivative checks across 65 times and five barycentric fractions,
and overflowing ceilings. Six initial tests failed before implementation; the
overflow control separately exposed and corrected Fraction-to-float overflow.
Independent focused review ran 46 tests successfully with no actionable findings.

The prepared full analyzer suite passed 2,928 tests and 92 subtests in 167.09
seconds. Strict MkDocs and diff whitespace checks passed.
All 100 output records validate against the current source-appearance JSON Schema.

Local run outputs:

- `build/preset-corpus/source-shape-activity-red.log`
- `build/preset-corpus/source-shape-activity-2026-10-10/`
- `build/preset-corpus/source-shape-activity-suite.log`
- `build/preset-corpus/source-shape-activity-docs.log`

References compare the original MilkDrop2 blend factors and packed-byte channels
with the current patched core's native floating modulo conversion. No native
patch was added. Latest GitHub release was rechecked as v2.3.36, commit
`90b5bf9d9f60a13e9e271cc021a7d1133aa8fb3d`; published full-AAR digest matches the
local verified artifact:
`a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3`.
This source checkpoint is not new AAR runtime or visual qualification.

Next source target: partial time variation through shader RGB transfer, holding
texture values explicit, then combining geometry/coverage and feedback terms.
The low positive-rate coverage is an open extraction gap, not a verified limit.
