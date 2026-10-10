# Nested lookup motion chains

This source-only checkpoint composes inner sample variation, UV response,
bilinear texture gradients and direct RGB response. It constructs no display
frames and performs no image inspection or equation/shader execution.

## Fixed 100-preset sample

All original presets export with unchanged hashes, structured descriptions and
execution-unknown inventories. Exact names and polynomials are recorded in
`nested-sampling-census.json`.

- 47 presets have at least one resolved direct sample-to-coordinate gain component.
- 26 have positive coordinate gains.
- One has positive supported nested lookup-motion-to-RGB paths:
  `goody - woven beads (ps2-0).milk`.
- Eight chain records cover four default paths and four declared-scenario paths.
- No path/term budget report occurs in this sample.

The gains quantify source coupling, not actual image prominence or mood. The
chains identify paths through two or three samples. Actual uploaded W/H values
remain inputs; constant texel contents can produce zero variation despite a
positive ceiling. Paths are explicitly nonexhaustive and do not certify a total
sampling-motion or whole-image rate.

## Model and controls

Coordinate responses use the existing coefficient projection and bounded
calculus, extended with one-lane response mode. Native aspectXY `[0,1]` is an
explicit positive-finite-viewport premise supported by source34 `ProjectM.cpp`
lines 675–676 and the original MilkDrop2 aspect binding. Native upload ranges stay
bounded; sample-dependent quantization retains an unknown response.

Each chain multiplies nonnegative per-lane gain ceilings and base-level bilinear
W/H factors. Coefficients remain exact Fractions until outward finite export.
Distinct paths sum conservatively. Cycles, nearest/mipmap/unresolved filters,
singular arithmetic and unknown active gains receive no smooth chain credit.
The 64-site/4096-term guards retain incomplete outcomes; traversal limits remain
unchanged.

Nine controls cover UV gain matrices, two/three-level dimension polynomials,
nonlinear offsets, nearest exclusion, singular domains, absence of nesting,
sample-dependent native narrowing and explicit nonexhaustive scope. Seven
original controls failed before implementation. Independent review ran 41 focused
controls including original Grind's traversal-budget regression and found no
actionable issues.

Prepared full suite: 2,968 tests and 92 subtests passed in 171.02 seconds.
All 100 source-appearance records validate the current JSON Schema. Strict MkDocs
and diff whitespace checks pass.

Local outputs under `build/preset-corpus/`:

- `source-nested-sampling-red.log`
- `source-nested-goody-2026-10-10/`
- `source-nested-sampling-2026-10-10/`
- `source-nested-sampling-suite.log`
- `source-nested-sampling-docs.log`

See `SOURCE_APPEARANCE.md` for the export contract, exact example formula and
shader/filter references. No AAR/native code or authored preset was changed.
Texture history, direct coefficient/colour time changes, native mesh motion,
unsupported/non-affine roots and final composition remain separate contributions.
