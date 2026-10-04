# Audience scoring: shared baseline and sparse-field diagnosis

The duplicate published-core corpus coordinator remains stopped at 147 records
(144 scored, three unresolved). The full-corpus owner is `followup/quad-lines`.
This work does not start another corpus run or change that owner's inputs.

## Shared-data compatibility

Seven existing emulator control result files were inspected. Each selected
capture contains eight adjacent pairs at 30fps, but no three consecutive frames.
The original viewport is 2364×1330; retained PNGs are smaller thumbnails.
These measurements can check sampled colour, brightness and pairwise movement.
They do not supply our current model's consecutive velocity changes or complete
flashing transition counts. Unsampled transitions must not become zero counts,
and isolated pairs must not become a continuous movie.

`tools/milk-analyzer/fixtures/shared-core-baseline-compatibility.json` records the
job IDs, original preset hashes, protocol hashes and sampled indices inspected.
It explicitly does not approve importing these controls as complete scores.
The shared instrumented baseline/candidate libraries are separate from the
unchanged published 2.2.4 AAR used by this branch. Driver, resolution, audio and
capture-schedule differences require explicit verification before calibration
or score identities can be combined.

## Sparse-field fix

The existing capture of `$$$ Royal - Mashup (249).milk` had a small central
effect surrounded by black. Four sampled transitions had whole-field luma
standard deviations between approximately 0.0044 and 0.0098, below the 0.02
contrast gate. Bypassing that gate experimentally produced usable forward/backward
consistent flow. The prior rejection was caused by contrast dilution, rather
than proof of absent movement.

The fix checks local contrast in the padded union of visible luma when the
whole-field gate fails. It does not crop, enlarge or rescale the flow input.
Velocity units and affected areas still refer to the full original viewport;
the existing correspondence, residual and support checks remain required.
Insufficient local contrast stays unknown.

A seeded 12×12 textured patch translating one pixel per frame within a 256×128
viewport failed before the fix and passes afterward, recovering 30/256
viewports per second within 25% and supported area below 3%. A faint-noise
control remains unresolved. All 512 analyzer tests and 33 subtests pass.

Offline remeasurement of the existing 420-frame published-core capture recovers
54.04% of measured transitions and gives a provisional intensity of 74.80676144
(Normal and Party). This is estimator evidence, not human agreement or validated
classification accuracy; the large estimated acceleration merits comparison
against independent movement evidence. Its complete descriptors, capture hash
and implementation hash are preserved in
`tools/milk-analyzer/fixtures/sparse-core-motion-remeasurement.json`.

The original failed result and run identity are preserved. This diagnostic is
not inserted into that old corpus as if it used the old descriptor version.
The other two unresolved records need their own evidence. Complete 9,606-preset
scores and the final debug APK remain outstanding.
