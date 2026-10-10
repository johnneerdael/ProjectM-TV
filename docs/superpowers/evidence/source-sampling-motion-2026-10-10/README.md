# Affine sampling motion and conditional texture-gradient rates

The source export now adds lookup-axis rates and inverse fixed-feature motion to
supported affine sampling maps. It also relates constant affine sample RGB weights
to bilinear worst-case per-texture-dimension rate coefficients. Texture dimensions
and fixed `[0,1]` texel contents are explicit premises, not silently supplied values.

## Fixed 100-preset sample

All 100 original presets completed with the pinned source34 reader, unchanged
sealed compile manifest and declared scenario. Exact names and records are in
`sampling-motion-census.json`.

- 83 presets have at least one resolved default lookup-rate component.
- Two have positive lookup rates: `AdamFX 2 Geiss - Mash-Up Sphere Xibit Graffiti Warp me Oval Interprise.milk`
  and `goody - woven beads (ps2-0).milk`.
- 83 have an inverse feature-speed ceiling; only the first positive-lookup preset
  has a positive inverse ceiling, approximately 0.141421 UV basis units/second.
- 21 have at least one bilinear dimension coefficient. All supported coefficients
  in this sample are zero; zero are positive.

These counts include partial components and static values. Do not promote them
to whole-image stationarity or mood. The two positive lookup cases have colour
paths outside the affine RGB mixture model, so output RGB rate propagation is
still unresolved. That specific gap prioritizes nonlinear sample-to-RGB response.
Texture history, native mesh movement and other time/audio/state terms stay separate.

## Validation and correction

Ten focused controls cover inverse feature velocity, sinusoidal speed ceilings,
RGB weight scaling, singular maps/domains, scenario identity, nearest exclusion,
inverse equation consistency and two helper lookups with distinct weights.
Seven original controls failed before implementation. One numeric expectation
was corrected to compare with the actual native-rounded authored coefficient,
rather than the decimal literal 0.02.

Independent review found a traversal-budget regression in original Grind. The new
raw coordinate-domain preflight was running before detecting supported candidates.
The unchanged original budget control failed before repair and passed after
candidate checks moved earlier. No traversal limit was increased. Review reran
54 focused controls including Grind with no remaining actionable findings.

Local preserved outputs under `build/preset-corpus/`:

- `source-sampling-motion-red.log`
- `source-sampling-motion-budget-red.log`
- `source-sampling-motion-2026-10-10/`
- `source-sampling-motion-suite.log`
- `source-sampling-motion-docs.log`

All 100 source-appearance records validate the current JSON Schema. Strict MkDocs
and diff whitespace checks pass. Source math and domain controls do not establish
native runtime or visual qualification; no AAR or authored presets were changed.
The prepared full suite passed 2,947 tests and 92 subtests in 168.78 seconds.

See `SOURCE_APPEARANCE.md` for exact inverse/product formulas, units, fixed-input
premises and Microsoft's bilinear filtering reference. Native sampler policies
remain distinct from legacy anisotropic/mipmap selection.
