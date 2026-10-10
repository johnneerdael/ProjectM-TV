# Nominal source-time switch schedules

Control curves now include nonexhaustive time_switch_events. Supported affine-
time sinusoidal comparisons yield period, nominal2/periodcontact cadence, duty
fraction, signed phase and supported event offsets. Negative amplitudes reverse
comparisons; swapped sides and negative time slopes are preserved. Complete
scalar comparison/constant-branch controls can supply jump size; inner sites
retain timing with whole-control transfer unresolved. Tangent/outside thresholds,
equal branches and audio/state/nonlinear phases do not get crossing schedules.

Affine real-floor sites yield event interval1/abs(slope); supported scalar
linear transfer can supply scaled jump but absolute levels remain unbounded.
Current source34projectm-eval TreeFunctions.c87/88 aliases EEL int/floor to the
same real floor, confirmed by its negative-floor control(-1.5→-2). Shader int
casts retain conversion semantics and cannot borrow an inner floor jump. Clock
resets/wrap, native rounding, reached branches and sampled frames are excluded.
The schedules do not certify source/frame/display pulse frequency or moods.

The inverse-trig basis is the primary [NIST DLMF4.23](https://dlmf.nist.gov/4.23).
Duty/contact formulas are our source-math derivation; tests independently check
sine/cosine, signed amplitude/phase, swapped predicates, floor aliases/casts,
unreachable/tangent/equal cases, nested scope and finite extreme frequency.
Seventeen new controls and219producer focused tests pass. Independent review
passed87switch/material/temporal/compound controls with no actionable findings.
The internal motion-control scan opt-out prevents recursive timing extraction;
per-analysis caches and2048node/32event limits bound these nonexhaustive scans.

All100original source exports complete with exact source/hash joins and ZIP CRC.
Only3sample presets gain schedules:13control descriptor records carry16threshold
sites and3floor sites. No complete control jump is resolved for these real sample
records. Repeated descriptions may share source sites; these are output-record
counts, not independent visible events. This is a modest timing ingredient gain,
not whole-preset pulse/flashing or classification coverage. Exact names/hashes,
paths, scope and events are retained in census.json; unsupported timing is not
counted as calm/no-flash. Empty event lists remain explicitly nonexhaustive.

No image, audio/time sample or shader/equation execution feeds the producer.
Preset-operation time totals36.980001seconds, maximum2.344628seconds on this host;
sample timing is not a corpus/hardware guarantee. No native/preset/shared device/
full corpus was changed. Existing waveform/shape material conversion and later
feedback/composite remain separate from raw control schedules.

Raw paired archive: `build/preset-corpus/source-time-switches-2026-10-10/batch-000001.zip`.
SHA256 `f511a7ccc8dc883d5caf5fd3fe532b3beb107a9b7a9f4837c2d6166c6c875d46`.
Reader SHA256 `754e4f4129db585cb4f7d5bee915d6bb24ac10ab25901ee7ef0832ce50744afc`.
Matching source34targets published2.3.36bytes; runtime qualification remains
independently pending. Actual appearance and mood accuracy remain unverified.

Final prepared suite: **2,662tests and92subtests pass in148.34seconds**.
Strict MkDocs and whitespace checks pass. These are source-rule checks, not
whole-preset visual/pulse or mood accuracy.
