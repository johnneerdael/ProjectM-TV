# Source prediction and native validation loop

Current target: fresh batches of three previously untested random presets, with
100/100 behavioural grades for all three in one batch. Complete each batch before
repairing gaps. Use 60 frames per preset, report each outcome, and keep generation
outside this goal. The sections below retain earlier checkpoints as history;
the final batch-goal section supersedes their acceptance thresholds.

Historical target: ten consecutive fresh randomly selected presets, each achieving at
least 80/100 agreement for full visible behaviour: structure, motion, colour,
flashing and feedback. Any failed comparison resets the streak. Diagnose the
missing calculation/context, add a focused correction and regression evidence,
then evaluate new random presets. Do not substitute audience-score agreement.

Reuse the existing mathematical source forecaster and semantic analyzer imported
from `feat/preset-audience-scoring` at4cd38ad9. Preserve production beta rankings,
models and their provenance. Do not use saved native scores or captures as forecast
inputs. Freeze source, model, input/profile, predictions and score rubric before
capture. Keep diagnosis reruns separate from fresh-case acceptance.

The explicit behavioural rubric is in ignored `build/visual-loop/protocol.json`:
five equally weighted categories, four observable claims each. Each earns5for a
supported match,2.5for a partial match,0for mismatch/unknown. Require total>=80,
no critical contradiction and a matching capture/source/profile. This is an
operational descriptive-agreement grade, not a calibrated perceptual probability
or proof about every possible input/time/random state. Retain quantitative
source-field/observed-field diagnostics separately; pixel similarity alone cannot
satisfy full-behaviour acceptance.

Native validation uses unchanged published standard core2.3.4 AAR via its exact
JNI class/library and assets, on task-owned emulator5596. The renderer host is
256x144 GLES3,30fps,48x32mesh. The declared18-second PCM schedule contains quiet,
melodic, kick-driven and silence phases. Actual random realization remains an
external input; representative source random inputs are explicit. No shared
corpus/device is operated. All raw frames/audio remain under ignored build/.

Initial engineering work: port the existing source modules without replacing
production rank/model code, prepare CPU math adapters for the same41-patch engine,
fix their missing quad-line geometry/state dependencies, freeze one random case,
then render and compare it. Prepared adapters must finish before dependent tests.
Preserve older-profile failures; do not rewrite expectations simply to claim a
passing suite. Current source-forecast controls:27tests and16subtests pass after
the waveform adapter repair. Broader imported tests still require profile
reconciliation; no blanket compatibility or appearance claim is made.

Archive each prediction and outcome; when ten consecutive fresh cases pass,
audit the frozen artifacts, random sequence, five category scores and final model
revision. Follow repository validation, documentation and PR/review workflow for
retained code changes. Do not mark the goal complete before the streak is proved.


## User-directed60-frame profile update

The user shortened each prediction/reference run to60frames at30fps. The current
acceptance window is therefore2seconds, with no descriptor warmup and the fixed
quiet input prefix. Preserve the older18-second runs as diagnostics; restart the
acceptance streak rather than combining the two profiles. Case001was already
observed and is excluded from fresh short-window acceptance. Current new-profile
results: case002100/100,case00390/100; provisional streak2/10. The latter retains
brightness/overlay-attribution misses. These are frozen behavioural-rubric grades,
not calibrated accuracy probabilities. Later changes and other music remain
unassessed by this deliberately shortened window.

Checkpoint update: four short-window passes now recorded (100,90,97.5,100).
Case004retains a flash-event-count miss; case005shows close broad colour, glow and
flash correspondence. Current goal remains incomplete at4/10.


## Critical failure and required repair gate

Case008failed on deterministic trajectories/layout; broad theme agreement was
insufficient. User instruction: before any fresh run, fix the gap and retest that
exact preset to90or higher. The512-point/resampling correction passes24controls
and the isolated diagnostic retest scores100. Preserve before/after artifacts;
restart fresh acceptance at0/10from case009. No diagnostic rerun counts as fresh.


## Superseding three-preset batch goal

The user now requests batches of three never-before-attempted random presets,
completed under one unchanged predictor before addressing any batch gaps. Repeat
until a fresh batch grades100for3/3or the userstops; preset generation is excluded.
Keep60frames and per-preset reports. Round001cases010–012grades97.5,100,90; the
three-case perfect gate is not met. Source/model hashes were unchanged across the
batch. Gaps: coherent flash counts and contour-transition timing.

Investigation confirms all41engine patches match the CPU archive patch-series
hash. Its lab instrumentation allowed an equationRNG seed override. The source
driver used12345, whereas production eval uses fixed0x4141f00d. Changing only the
source equationseed reduces case012RGB MAE0.15987→0.10398against the same saved
reference, but does not yet resolve every discrepancy. A frozen analytic equation
RNG diagnostic through the unchanged AAR is being used to check sequence/context.
These diagnostic controls do not count as fresh acceptance or generator testing.

The production-seed correction is now guarded by an explicit cold-thread profile
and matching engine/patch-series identity. The native equation RNG control matched
all 60 frames exactly in RGB8 through the unchanged published AAR. Direct ADB
execution with file readback succeeded after streaming transport failed; the
owned emulator remains live. Independent MT19937 draws match the CPU trace across
33 shape instances and 60 frames. 36 focused controls pass. Preserve native evidence
in `fixtures/visual-loop-equation-rng-repair-2026-10-05.json`. Remaining contour and
flash gaps still require diagnosis before claiming the round is repaired.

Documentation assessment: README and Pages predictive-collections guidance still
describe the unchanged shipped beta scorer and its 2.3.3 corpus provenance, so no
runtime claims or scores were changed there. Analyzer README and this research
plan now describe the superseding batch goal and seed policy. No docs-site source
or release-tooling behavior changed.

Two additional independently frozen 60-frame diagnostic controls localize the
remaining case012 mismatch. A changing asymmetric gradient through GetBlur3
has mean RGB8 error 0.2915 and maximum 2. The exact authored shape1 equations,
33 instances and matching audio, isolated from feedback, have mean RGB8 error
0.04631 and maximum 17 (local raster edges). Both use the unchanged published
AAR and matching viewport. These controls did not reproduce a large orientation
or random-order defect. Small-error amplification through authored feedback
remains a hypothesis, not established root cause. Retain exact control source,
frozen predictions and native hashes in
`fixtures/visual-loop-feedback-localization-2026-10-05.json`.

Further source inspection identifies a real unmodeled path: JNI enables the
patched quad-line renderer at a 1024x768 reference, but the forecast used canonical
GL lines. The named GLES profile now models hard-edge mitered strips and the
1/64-pixel GL-Y tie bias for custom/builtin waves and shape outlines. A curved-line
control matches the published AAR within one RGB8 level on all 60 frames; 45
focused controls pass. Case012 now predicts flash counts 1/0, matching native,
and peak luma jump 0.8194 versus 0.8207. Mean motion is 0.2392 versus 0.2297.
Later contours still differ; do not grant fresh-case credit to these diagnostics.
The exact native preset repeat is pixel-identical on all 60 frames. Larger-than-
reference canvases, antialiasing and motion-vector quads remain explicit gaps.

Round002 (cases013–015) completed under unchanged model180a6101: 92.5,100,82.5.
All source predictions/descriptions were sealed before native capture. The latest
GitHub release page reconfirmed2.3.4 and the live guest artifact hashes matched.
Case013 underpredicts brightness and motion; retain the gap without an invented
root cause. Case015 gets the fourfold arrangement and movement but misses palette
and brightness. A native reload changes cyan/green/yellow into red/purple under
the same file/PCM/clock. PresetState initializes composite hue offsets from
random_device; the source driver supplied zeros. This is an unbound-input issue,
not proof of a shader operator bug. Preserve the original grade; no retrospective
palette relabelling or native-pixel fitting is permitted. Next work: represent
native hue realization/uncertainty correctly, and isolate case013 texture/feedback.
Evidence: `fixtures/visual-loop-round002-2026-10-05.json`.

Post-round controls: preserve native quad-strip vertex order when reflecting GL
Y into top-row coordinates. The corrected side/miter sign keeps the triangle
diagonal and varying interpolation faithful to the shader. A curved gradient
control agrees within1RGB8level on60frames;46focused tests pass. The isolated
builtin wave from case013 has mean RGB8 error0.00135but70pixel positions differ
by more than1level, with maximum191. This rules out a large waveform mismatch,
not all sparse coverage errors or their effect after feedback. Do not claim
case013 repaired. Evidence: `fixtures/visual-loop-quad-order-control-2026-10-05.json`.

The subsequent native-clip correction localizes case013's gap: normalized-screen
rounding occurred before quad expansion, while the shader expands native clip
coordinates first. Preserve original coordinates for builtin/custom waves and
pass offsets. The repaired diagnostic predicts luma0.14057/native0.14144,
motion0.17554/native0.17636 and flash peak0.01220/native0.01237; trajectories and
central recess now agree closely. Isolated-wave large pixel differences drop
70→14;52focused controls pass. Preserve original round grading. See
`fixtures/visual-loop-native-clip-repair-2026-10-05.json`. Case015's randomized
hue realization remains a separate unresolved input obligation.
