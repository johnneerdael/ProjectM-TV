# Source prediction and native validation loop

Current target: iterate three-preset batches until all three achieve at least
95/100, then iterate ten-preset batches until all ten achieve at least95/100.
After that, predict a randomized100-preset set as the final improvement audit.
Complete each batch under one frozen model before repairing its gaps. Use60
frames per preset and report each outcome. Generation stays outside this goal.
Preserve prior predictions and grades; diagnostic reruns do not silently replace
fresh acceptance evidence. The sections below retain earlier checkpoints as
history; this staged95+ objective supersedes their acceptance thresholds.

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

Source-type audit finds another adapter defect: native RenderContext.time is
float, while both CPU wave/composite state substitutes declared double. Include
the pinned engine header directly and preserve float hue arithmetic. Correct the
older tests that asserted the substitute's double semantics. 66 focused tests and
19 subtests pass; the long-clock regression now matches native float semantics.
Case013's two-second diagnostic is unchanged by this separate type repair.
Evidence: `fixtures/visual-loop-float-context-repair-2026-10-05.json`.

User selected matching declared random inputs for future reference comparisons.
Use an explicit new test profile, retain earlier inputs/results, and keep the
published AAR unchanged. An opt-in test-host supplies entropy seeds and a separate
declared random stream per core thread; background shader-worker resets must not
disturb renderer inputs. Input logs are numerical inputs/attribution, not rendered
reference images. Verify source-generated hue/noise/shader inputs with bounded
controls before using this profile in a fresh three-preset round.

Matched-input controls now verify the profile: all3728renderer C-random inputs
match an independent MT19937 lower31-bit stream;368worker draws are isolated.
The exact source hue initializer with entropy12345matches native colours within
1RGB8level on60frames. Noise initially failed because the native clock count is
microseconds, and resize recreates it on first draw rather than at engine creation.
The corrected clock count's low32seed3567620661matches HQnoise within1RGB8level.
Preserve both failed attempts. The original case015 program under matching inputs
has meanRGB8error0.563and closely aligned palette, layout and progression.
82focused tests and19subtests pass. No fresh acceptance credit; new three-preset
round still required. Evidence:
`fixtures/visual-loop-declared-random-inputs-2026-10-05.json`.

## Published2.3.5 migration (2026-10-06)

The user switched the target to canonical Native core2.3.5 at release910e837b.
Merge that released revision and use all42patches in the CPU backend. Retain the
clean production source separately from the lab-instrumented archive source;
neither substitutes for the publishedAAR renderer. Source RNG adapters now copy
0042's exact per-frame random cache logic and verify0-versus28draw consumption.
Keep explicit historical41and new42profile identities; high-resolution/detail
forecasting remains unsupported and must not silently use the old model.

The newAAR and ARM64 library hashes are verified. Owned5596 was authoritatively
stopped; only that dedicatedAVD was restarted. Newguestnamespace isolates235from
oldruntime. Smoke advances60frames and reports Standardinactive144p. The actual
42source forecaster's hue control matches235within1RGB8level. Initial malformed
black smoke remains preserved as a failed fixture-format attempt.

Round003cases016–018 had only234source computations when target changed; no
reference images were captured. Withdraw them from acceptance and retain results.
017timed out: read-only request inspection finds124,200shape evaluations and
about4million scalar captures over60frames, noEELloops or per-vertex program.
This supports a trace-cost explanation, not a proved language gap or runtime
profile. Do not blindly repeat it. The next truly unused queue entries are019–021.
Evidence: `fixtures/visual-loop-release235-migration-2026-10-06.json`.


## First complete published2.3.5 batch

Round004 cases019–021 completed with model eba811b5 unchanged. Frozen claims
and all104 source/binary/input identities were independently checked; all three
predictions were sealed before the first native capture. Each reference completed
60 frames with serial delta60, one indexed preset, no skipped preset and no
captured shader-error lines. Standard trails remained inactive at144p.

Behavioural grades: Space Voyage97.5,18717.5,Hyperspace65. The perfect three-case
gate is not met. Space Voyage retains fine accumulated-detail differences.187
misses a broad transient dark-red fan around frame20, a critical contradiction.
Hyperspace predicts the initial flash/white field and later warm sectors but
underestimates flash amplitude and late contrast. Twelve claims for187 and four
forHyperspace were explicitly unassessable before capture and earn no credit.
Low average pixel error must not hide these misses. Numerical claim tolerances
are not calibrated; the grades remain the explicit operational rubric.

Preserve these original predictions and grades. Investigate custom-shader input/
feedback behaviour for187, legacy feedback forHyperspace, and point raster/detail
forSpace Voyage before a fresh round. Environment-only launch failures were
retained: unsupervised children terminated and the default Python lacked NumPy;
the validated existing analyzer environment completed all three forecasts. No
predictor change was made to recover those launches. Full60frame data stays
under ignored build; compact claims, grades, metrics and artifact identities are
in `fixtures/visual-loop-round004-2026-10-06.json` under tools/milk-analyzer.

Documentation assessment: shipped README/Pages collection instructions remain
unchanged because this experimental prediction run changes no shipped ranking
or collection. This plan and the analyzer research evidence record the results;
no new production accuracy or compatibility claim is added.

## Round004 diagnosis: dots and equation FPS

The native quad profile draws built-in wave dots as one centered 2px point;
the source used four shifted 1px copies. Correct the explicit 2.3.5 low-resolution
profile while preserving canonical historical drawing and rejecting unsupported
engine/viewport requests. The dot-only diagnostic makes Hyperspace frame 2 match
exactly and lowers 60-frame RGB8 mean error from 2.951 to 0.416.

The clock cadence is 30 Hz but native equation FPS starts at 35, with the JNI
tracker setting 30 only after rendered image 30. A frozen fps/256 shader control
matches all native pixels: red 35 for images 1–30, red 30 for 31–60. Retain
physical PCM/FFT arrays and timestamps and provide that separate equation
context. With the original frozen 63-module model and only FPS input corrected,
187's missing red fan returns; mean RGB8 error falls from 1.130 to 0.0083, maximum
2. Adding the correct context to Hyperspace's dot repair lowers mean RGB8 error
further to 0.112, but residual maximum 23 remains. No diagnostics receive fresh
acceptance credit; original grades stay unchanged. Point-grid snapping and
motion-vector quads remain separate declared gaps.

Evidence: `tools/milk-analyzer/fixtures/visual-loop-dot-fps-repair-2026-10-06.json`.
Analyzer README records the input/drawing contracts; shipped collections and
Pages instructions do not change. Focused drawing/geometry tests pass 35 checks.

Two isolated one-frame point controls identify an 8-bit window-coordinate grid
on the declared Apple emulator. All five finer-grid candidate predictions were
sealed before native capture; only 8 bits match exactly. Add the explicit
`point_subpixel_bits` input, preserving the unsnapped default and rejecting
invalid grid values. Native halfway ties remain unverified. This correction
reduces case019 mean RGB8 error from 1.023 to 0.748; correcting equation FPS
does not change its pixels. Fine feedback differences remain, and no diagnostic
receives fresh credit. Focused drawing tests pass 42 checks and 17 subtests.

GitHub published 2.3.7 during diagnosis. Prepare its unchanged canonical AAR
and real 43-patch archive before the next fresh batch. Patch0043 targets Native
trails geometry preservation; its inactive144p path is distinct from native4K
fidelity. Keep completed 2.3.5 rows pinned, with new 2.3.7 controls and identities
in a separate namespace.

Migration controls now use the real43-patch archive and checksum-verified2.3.7
AAR. All eight CPU binary hashes and54 runtime seal files were independently
checked. Native FPS matches the declared35→30 timeline exactly; a complete
43-adapter source hue forecast matches the newly captured reference within1RGB8
level over60frames. Focused forecast/drawing tests pass99checks and17subtests.
High-resolution/detail paths remain rejected. Preserve43source, lab archive and
published AAR identities separately. Evidence is in
`tools/milk-analyzer/fixtures/visual-loop-release237-migration-2026-10-06.json`.

The next reference release is2.3.8. Its independently downloaded complete AAR is
byte-identical to2.3.7 (SHA4a6a8fef...), and the release changes onlyCI/docs, with
no engine/JNI/patch changes. Keep the verified43source/runtime and record2.3.8
as the fresh reference release; historical controls keep their original labels.
The next unused random queue entries are022–024. Preserve60frames and freeze
all predictions/claims before any fresh native capture. No model changes until
all three are assessed. Keep correctedFPScontext and explicitly declared8-bit
point grid. The remaining fine-detail residuals stay documented.

## Round005: latest identical2.3.8 AAR, three fresh cases

Cases022–024 completed under unchanged cedf001c:92.5,77.5,65. All188 pinned
identities and60 frozen claims were independently checked. Claims precede the
first native capture; each capture advances60frames with inactive144pStandard
trails, one indexed preset and no captured shader errors. Actual per-stage
program selection is not independently certified by absence of error logs.
No case reaches100; the three-perfect gate remains unmet.

022's dominant structure, motion phases, palette and feedback match closely,
with small numerical differences.023 matches ribbons and the dense-to-sparse
phase but misses retained texture and peak-change timing (source51→52 versus
native3→4). Its provisional80 assessment was corrected to77.5 before final seal;
the draft and revision trace are preserved, with original predictions unchanged.
024 matches early boxes but predicts horizontal inner narrowing where native
output develops tall upright loops. Preserve this critical trajectory miss.
Evidence: `tools/milk-analyzer/fixtures/visual-loop-round005-2026-10-06.json`.

Investigate earliest errors and their propagation before another fresh batch.
024 begins with only three1-level channel differences in frame2, then feedback
amplifies them; this is not evidence of an initial90-degree coordinate reversal.
Native custom shaders declare highpfloat but default sampler2D precision, and
blur/primitive fragment shaders declare mediumpfloat. Their actual precision
must be measured with bounded controls, not assumed from the qualifiers alone.
No native patch, full-corpus render or production collection change is requested.

## Bounded precision controls and UNORM repair

The uniform sampler-return control rejects the tested float16-return hypothesis:
the captured two-frame output matches float32 exactly. The driver's low/medium/
high float capability reports all advertise23bits; that is not proof about every
instruction. Independent UV probes favor8-bit polygon coordinates over4, but
neither separate raster4 nor raster8 diagnostic repairs cases023/024. Preserve
those negative results instead of treating a grid choice as a demonstrated fix.

A60-frame uniform half-byte conversion control exposes a genuine source bug:
float32 scaling prematurely rounds the represented value onto a halfway boundary.
Preserve the float32 input value, scale/round in float64 and return normalized
float32. The repaired conversion matches all native control pixels; original
predictions remain unchanged. Case023 meanRGB8error changes36.1358→36.1301;
case024 changes11.4269→11.2045, retaining large feedback/trajectory errors.
This is a correct small repair, not a complete explanation of the failed batch.
Evidence: `tools/milk-analyzer/fixtures/visual-loop-unorm-conversion-repair-2026-10-06.json`.

Derived pass-through controls localize early feedback separately from original
composite output.024's first three feedback frames match exactly.023 initially
differs only within drawn geometry: nine pixels have errors above1RGB8level.
Keeping the measured8-bit triangle grid in pixel space removes every first-frame
difference, including smaller interpolation errors. Add optional
`triangle_subpixel_bits` through primitive/shape/border/quad drawing and forecast
domain; retain canonical defaults.113focused tests and25subtests pass.
Later feedback differences remain, so this does not certify the full preset.

A separate scalar shader control confirms contraction/more precise intermediates
for one expression, but an isolated FMA prototype barely changes024's error
(11.2045→11.2002RGB8). It remains build-only; no production arithmetic profile
is adopted. Scalar temporary boundaries are erased in the existing lowered DAG,
which prevents claiming general storage-boundary-preserving contraction.
The next bounded investigation is2Dlinear filter precision; preserve all frozen
candidate/reference data and do not fit undocumented coefficients to pixels.

The centered sampler-return control matches float32-normalized79/255 and254/255
under signed-error amplification; tested float16 and fixed16 negative-bias models
are rejected. The nearest8filter prototype reproduces its independent candidate
but worsens024 (11.2045→11.4356RGB8), so no sampling patch is adopted from it.
A separately frozen three-frame constant-field blur control is the next boundary
test, distinguishing old warp blur from fresh composite blur.

At the user's request, confirmed AAR defects get separate engineering documents
in Downloads. The first is shader literal round-trip loss: the native translator
uses six significant digits, changing1.0000001192092896 to1. One controlled AAR
frame matches the emitted-literal prediction(64,96,0), while authored float32
semantics predict(128,96,0). The95-preset/99-literal AST inventory proves emission
changes but not each preset's visual impact. The predictor already honors actual
`renderer_literal`, so this is an engine authored-semantics handoff, not a newly
unmodeled predictor gap. Evidence:
`tools/milk-analyzer/fixtures/native-literal-roundtrip-defect-2026-10-06.json`.

Constant-field blur history matches all three native matrices exactly. The
spatially varying seed also matches exactly, but resulting Blur1/Blur2 samples
differ by at most one RGB8 level, predominantly upward along the horizontal
ramp. A build-only fused blur accumulation only slightly reduces this error;
no arithmetic profile is adopted. All22 kernel constants match host-compiled
C++ formulas bit-for-bit, without claiming runtime uniform readback. Evidence:
`tools/milk-analyzer/fixtures/spatial-blur-stage-localization-2026-10-06.json`.
The next useful localization is bounded native pass-level observation through
test-host instrumentation, keeping the published AAR unchanged; another guessed
sampling rule or repeated full-preset render is not justified by these results.

The bounded pass observation now retains twelve native pass readbacks. The final
display is byte-identical to the original control, every recorded state is restored,
and all runtime uniform bits match the frozen CPU predictions. Samplers use unit0,
linear filtering and clamp-to-edge. Zero-input frames match at every pass. The first
difference is frame2's horizontal pass: at most one RGB8 step, with181 negative,
24,431 equal and3,036 positive scalar RGB samples. Subsequent differences therefore
do not originate in a wrong kernel upload or blur-history phase in this control.
Sampling/arithmetic remains unresolved; this is not another confirmed AAR bug.
Attached shader sources were unavailable after linking, so the trace does not
certify runtime shader text. Original full-preset grades remain unchanged.
