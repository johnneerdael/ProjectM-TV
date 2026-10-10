# Possible temporal jumps from nearest texture lookup

The source export now recognizes possible nearest-texel jump mechanisms when a
declared nearest, nonmipmapped base-level lookup has positive supported nominal
time-motion and a possible direct RGB/nested-coordinate route. It constructs no
frames and does not inspect images.

## Fixed sample result and next priority

All 100 original presets retain structured descriptions, unchanged hashes and
execution-unknown inventories. `nearest-activity-census.json` records the result.

**Zero presets match this restricted detector.** The sample contains 1,134 lookup
records, including 149 with declared nearest filtering. All three positive
default affine lookup-time records use linear filtering, so there is no intersection.
The existing 11 presets with local shape jump hazards remain unchanged.

This is not a flashing-coverage gain or proof that nearest sites do not move.
Native mesh transport, non-affine mappings, audio/state changes and image history
are outside this detector's current motion input. Those paths are the next
priority; more local helper patterns alone will not close this sample's gap.

## Controls and scope

Seven controls cover moving/stationary/dead lookups, direct jump ceilings,
bilinear exclusion, oscillating motion, nested RGB routes and clamped addressing.
Four initial controls fail before implementation; three negative controls already
pass. Independent review ran 39 focused controls including original Grind's
budget control and found no actionable issues.

Direct jump ceilings sum independent RGBA-to-RGB gain columns over the `[0,1]`
input box. Nested or unsupported magnitudes remain null. Constant texels, equal
neighbours, masking, clamping and rounding can suppress actual jumps.

Only nominal constant drift with repeat addressing gets grid-crossing coefficients
per uploaded W/H. Those describe long-run grid-boundary crossings between clock
resets/wraps, not distinct sampled values or visible flashes. A small fast
oscillation can recross one boundary often despite a small speed ceiling, so
oscillatory/clamped cases do not borrow the drift formula.

Prepared suite: 2,975 tests and 92 subtests passed in 170.09 seconds.
All 100 source-appearance records validate the JSON Schema. Strict MkDocs and
diff whitespace checks pass. Latest GitHub release rechecked as v2.3.36, full-AAR
SHA256 `a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3`,
matching the existing verified artifact. No AAR/native code or authored preset
changed; this does not constitute new native runtime certification.

Local outputs under `build/preset-corpus/`:

- `source-nearest-activity-red.log`
- `source-nearest-activity-2026-10-10/`
- `source-nearest-activity-suite.log`
- `source-nearest-activity-docs.log`

`SOURCE_APPEARANCE.md` documents the exact contract and primary nearest-filter
references. Possible local mechanisms must not become automatic Party labels
or empty-evidence Chill certification.
