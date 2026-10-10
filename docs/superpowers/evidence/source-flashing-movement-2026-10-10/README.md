# Source flashing mechanisms and movement steps

This checkpoint prioritizes source mechanisms needed for Chill/Normal/Intense
classification. It performs no frame construction, GPU execution or image inspection.

## Fixed 100-preset coverage

All 100 original sample presets export successfully under the source34 reader,
sealed compile manifest and declared audio/canvas scenario. The activity census
contains exact preset names and quantities:

- 23 presets expose known native feedback rotation or positive uniform zoom components.
- 20 presets expose polygon perimeter vertex-speed bounds.
- 39 distinct presets have at least one of those movement quantities.
- Zero presets match the restricted periodic full-composite blackout pattern.

The first two groups overlap. These are mechanism coverage counts, not mood
accuracy or whole-screen movement measurements. Zero blackout matches does not
mean zero flashing: colour jumps, opacity changes, audio thresholds and feedback
interactions require further path analysis. Existing nested time-switch sites
occur in three sample presets (19 exported records), but cannot be promoted to
whole-stage jumps without determining their transfer and visibility.

## Correctness controls and repairs

Twelve activity controls cover source cadence, added background, spatial masks,
constant feedback movement, disconnected paths and known-invalid domains.
Independent review identified three missing controls; all failed before repair:

1. A blackout gate multiplied by `1/0` incorrectly certified zero RGB. The
   original contributing RGB graph is now domain-checked before extracting gates.
2. Unknown `warp=bass` prevented full recipe extraction before singular `zoom=0`
   was checked. All known mesh controls now receive direct domain checks.
3. `rot=2*pi` incorrectly counted a full turn as a large movement step. Effective
   angle now comes from `atan2(sin(rot),cos(rot))`, retaining authored float32 rot.

Unknown domains stay conditional. Finite inputs are insufficient: every contributing
RGB intermediate must be finite. Overall flashing and motion intensity remain null.

## Reproduction and preserved evidence

Activity module: `tools/milk-analyzer/source_activity.py`.
Contract: `tools/milk-analyzer/export-contract/source-appearance.schema.json`.
References and units: `tools/milk-analyzer/SOURCE_APPEARANCE.md`, section
“Flashing mechanisms and feedback movement”.

Local, task-owned snapshots under `build/preset-corpus/`:

- `source-flashing-movement-2026-10-10/`: initial frozen export, retained without correctness credit.
- `source-flashing-movement-repaired-2026-10-10/`: reviewed mathematical repairs; `activity-census.json` copied here.
- `source-flashing-movement-final-2026-10-10/`: same repaired math with explicit finite-RGB-intermediate contract premise.
- `source-flashing-movement-review-red.log`: three failing regression controls.
- `source-flashing-movement-repaired-suite.log`: prepared analyzer-suite output.
- `source-flashing-movement-docs.log`: strict MkDocs output.

Validation: the prepared mathematical checkpoint passed 2,918 tests and 92
subtests in 165.14 seconds. After the explicit finite-intermediate premise and
its contract control were added, 193 focused activity/appearance/warp/switch tests
passed in 10.68 seconds. Strict MkDocs and diff whitespace checks pass. Independent
review cleared the three mathematical repairs and final contract premise.

Published AAR runtime fidelity is a separate gate. Source34 is tied to the
published 2.3.34 patch math; 2.3.34–2.3.36 published AAR bytes match the verified
SHA256 `a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3`.
This checkpoint does not claim new Android runtime or visual certification.
