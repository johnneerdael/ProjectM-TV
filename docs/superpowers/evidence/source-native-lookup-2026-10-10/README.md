# Native feedback displacement propagated into shader lookups

This source-only checkpoint composes the existing uniform native displacement
envelope with constant-affine authored warp lookups. It constructs no frames,
executes no equations/shaders and observes no texture contents.

## Fixed 100-preset coverage

All original presets export with unchanged hashes, structured descriptions and
execution-unknown inventories. `native-lookup-census.json` names the affected presets.

- 15 presets have at least one bounded native-to-lookup displacement.
- 14 have positive displacement ceilings.
- Three have possible nearest-main feedback jump records:
  `suksma - amental ruiner broach2.milk`,
  `suksma - n19 3 layer overlap opt 3 flx nz+ loqo yes joe rogan, chimps are crazy, but what about bonobos.milk`,
  and `suksma - god might as well2 - rst filled to the brim with atheistic hate nz.milk`.

The underlying native displacement envelope covers 26 presets, but authored
lookup consumption/maps restrict composed coverage to 15. A positive ceiling
does not prove actual movement, a texel crossing, visible flashing or a mood.
These records address a contribution missed by zero authored lookup-time rates:
native controls transport the sampled previous image every feedback step.

## Math, domains and tests

For native aspect-corrected RMS bound D and mesh-UV lookup columns Mx,My,
the lookup RMS ceiling is `D*(norm(Mx)/aspectX+norm(My)/aspectY)`. Positive finite
renderer aspects remain caller inputs. Column norm squares use exact Fractions;
finite square-root conversion rounds outwards. This is a conservative uniform-area
RMS bound, not a pointwise jump ceiling, temporal derivative or forward screen speed.

Original-UV-only and composite lookups bypass the contribution. Mixed warp/original
maps use only mesh-UV columns. Shader offsets cancel in the same-frame comparison.
Known-invalid coordinate diagnostics and unresolved/singular native domains retain
null bounds. Texel alignment, rounding, interpolation, wrapping, history and later
passes remain separate. External textures alone do not establish repeated feature
motion, so nearest feedback hazards are restricted to main-image sampling.

Twelve controls cover constant/dynamic zoom, identity, translation/scaling,
original/mixed UV, singular native/shader domains, nearest-main versus external
textures, independent grid/aspect RMS checks and extreme norm inputs. Seven original
controls failed before implementation; the known-invalid shader-offset control
separately exposed a missing guard and was repaired using existing coordinate
diagnostics. Independent review ran 43 focused tests including original Grind's
budget control and found no actionable issues. Traversal limits remain unchanged.
The prepared full suite passed 2,987 tests and 92 subtests in 170.50 seconds.

All 100 source-appearance records validate the JSON Schema. Strict MkDocs and
diff whitespace checks pass. Original MilkDrop2 and the local authoring guide
were checked for the per-frame transform order; see `SOURCE_APPEARANCE.md`.

Local outputs under `build/preset-corpus/`:

- `source-native-lookup-red.log`
- `source-native-lookup-2026-10-10/`
- `source-native-lookup-suite.log`
- `source-native-lookup-docs.log`

No AAR/native code or authored preset was changed. Non-affine maps, unresolved
native controls, actual prominence and whole-screen intensity remain open work.

Remaining composed-lookup blockers in this sample: unsupported constant-affine
extraction affects 228 lookups across 70 presets; unresolved native displacement
domains affect 211 lookups across 52 presets. Groups overlap. These are reporting
inputs for prioritisation, not evidence of new native renderer bugs.
