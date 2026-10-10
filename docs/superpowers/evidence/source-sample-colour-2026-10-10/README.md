# Nonlinear direct sample-to-RGB response

This checkpoint propagates independent sampled-lane changes through supported
nonlinear source colour math. It constructs no display frames and performs no
equation/shader execution or image inspection.

## Fixed 100-preset coverage

All 100 original presets export and retain structured descriptions, unchanged
source hashes and execution-unknown inventories. Exact names and coefficients
are recorded in `sample-response-census.json`.

- 78 presets have at least one resolved direct sample gain component.
- 59 have positive direct sample gain coefficients, compared with 35 previously
  covered by constant affine sample mixtures: 24 additional presets.
- 61 have at least one complete 3-by-4 sampled RGBA-to-RGB ceiling matrix.
- One preset now has positive sampling-motion-to-RGB dimension coefficients,
  in two default/scenario records: the AdamFX sphere/oval preset below.

Partial components, complete matrices and positive coefficients are distinct
counts. They are source interpretation coverage, not whole-preset visual/mood
accuracy or typical reaction strength. All 100 outputs validate the JSON Schema.

## Two motivating presets

`AdamFX 2 Geiss - Mash-Up Sphere Xibit Graffiti Warp me Oval Interprise.milk`
samples moving low-quality noise and uses it in a clipped image-blend mask.
The direct nonlinear response now propagates that movement into raw RGB
coefficients of approximately `[0.06011719, 0.06011719]` per uploaded texture
dimension, separately for each RGB lane. Actual width/height, fixed `[0,1]`
texels and declared sampler/clock/domain premises remain inputs. This does not
establish that the worst-case ceiling is reached or that the effect visibly flashes.

`goody - woven beads (ps2-0).milk` has supported direct sample products after
the float-width projection correction. Its positive-motion sites 4/5 occur inside
the coordinates of outer lookups, so no direct RGB-motion coefficient is credited.
Their next required calculation is the nested lookup-gradient chain. Keep this
case unresolved rather than interpreting absence from the direct matrix as zero
influence.

## Predictor correction and controls

Twelve new controls cover powers, zero-touching roots, products, clipped masks,
nonlinear motion propagation, thresholds, nested lookup exclusion, singular
products, float-width conversions and integer casts.
Eight original controls failed before implementation. Two additional float-width
controls exposed an unresolved vector dependency being mistaken for zero scalar
gain. The fix projects ordinary float-to-float scalar/vector conversions through
the existing typed first-lane/broadcast/truncation rules; unresolved vector,
integer/bool and quantized sample-dependent paths retain null ceilings.

Independent review ran 77 focused tests including the original Grind traversal
budget control and found no actionable issues. Budget limits remain unchanged.
The prepared full suite passed 2,959 tests and 92 subtests in 170.53 seconds;
strict MkDocs and diff whitespace checks passed.
Direct matrices vary one sample lane at a time with all other inputs/coordinates
fixed. Row sums bound simultaneous independent lane changes; they are not signed
Jacobians or minimum response. Domain/finite-input premises and default/scenario
identities remain explicit. No AAR or authored preset source was changed.

Local preserved outputs under `build/preset-corpus/`:

- `source-sample-colour-red.log`
- `source-sample-colour-adamfx-2026-10-10/`
- `source-sample-colour-goody-2026-10-10/`
- `source-sample-colour-goody-casts-2026-10-10/`
- `source-sample-colour-2026-10-10/`
- `source-sample-colour-suite.log`
- `source-sample-colour-docs.log`

See `SOURCE_APPEARANCE.md` and its HLSL lerp reference for the exact export
semantics. Native runtime fidelity, image prominence, nested coordinate gradients,
feedback evolution and whole-screen mood remain separate gates.
