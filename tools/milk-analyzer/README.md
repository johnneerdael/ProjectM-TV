# Source-based MilkDrop analyzer

Semantic sources and implementation mapping: `REFERENCES.md`.

## Audience scoring review

The current review goal is to score the complete shipped corpus and generate
All/Chill/Normal/Party collections for a ProjectM-TV debug build. The accepted
contract is in `docs/superpowers/specs/2026-10-04-preset-audience-review-design.md`
at the repository root. Full-corpus scoring is not complete yet.

`audience_policy.py` defines inclusive intensity bands: Chill 0–30, Normal 25–75,
Party 70–100. Five-point judgment tolerance is a validation setting, separate
from category membership. `audience_ranking.py` spreads collection-relative
ranks over 1–100 while preserving ties and missing values; those ranks do not
replace absolute intensity. `intensity_calibration.py` fits a research model to
interval-valued judgments; training agreement is not accuracy evidence.

The independent numeric predictor models equations, source drawing, feedback,
warp and composite fields. Portable mode rejects unresolved numeric domains.
Explicit Apple runtime profiles cover measured zero-stretch NaN interpolation
and NaN texture-coordinate addressing; they are not portable GPU guarantees.
The shader coordinate profile applies only at texture sampling and does not
invent final colors for unresolved NaN expressions. Zero-base power domains
remain among the calculations requiring further work.

Run the analyzer tests with:

```bash
build/preset-lab-venv/bin/python -m pytest tools/milk-analyzer -q
```

The full-corpus numerical backend uses the unmodified published ProjectM-TV
`:core` AAR, including the app's patches. `CoreBackendRunner.java` hosts its
existing `ProjectMJNI` interface in an independent EGL pbuffer and supplies an
asset archive. No analysis API is added to the library. The runner reads the
default presentation framebuffer, since core may return with a private read
framebuffer bound. Pin and verify AAR/native-library/input identities before
using results for scoring. The pinned initial artifact is release v2.2.4 with
SHA-256 `75e8cbb9ce4ab9340ac9514c16812bbf79e5b3dfa8f29db22d653c601323ce60`.

`core_corpus.py` uses a shared published asset archive and a small deterministic
selection-index overlay per preset. It validates the deployed AAR, native
library, runner, clock helper and PCM hashes before starting. RGB fields stream
to numerical descriptors; renderer logs use separate files. Each result is
written atomically and only complete finite scores with the same run identity
are reused. Unscored entries retain diagnostics and require `--retry-unscored`
after investigation. The model at `profiles/audience-model-v1.json` preserves
the development candidate's weights and archival provenance; each native run
pins its actual scoring code separately. It is not a calibrated accuracy claim.

```bash
build/preset-lab-venv/bin/python tools/milk-analyzer/core_corpus.py \
  --aar build/core-audience-analysis/published/projectM-TV-core-2.2.4.aar \
  --model tools/milk-analyzer/profiles/audience-model-v1.json \
  --runtime build/core-audience-analysis/published \
  --pcm build/milk-analyzer/audience-ten-2026-10-03/running.f32 \
  --output build/core-audience-corpus
```

The runtime directory contains the D8-converted published JNI class/runner,
the runner-side clock helper and the unchanged extracted library. A validated
five-preset pilot and resume check precede the complete run. The PCM fixture
is local test input, not distributed with this repository.

## Complete review export and debug build

`audience_export.py` verifies every preset path/hash against the published AAR
and requires a finite matching score for the entire corpus. Before writing
assets it recomputes scores from the pinned model, saved features and flash
contributions. The model hash, measurement duration and correspondence-derived
features must agree. Direct uniform/stationary observations remain explicit
exceptions to unavailable optical-flow features. It emits the agreed
overlapping groups, a separate relative-rank table and checksummed metadata.
The unchanged core receives Chill through `ambient`, Normal through `pop`, and
Party through `dance`; those aliases are displayed as the requested review names.

Audit partial or complete data without starting a render:

```bash
build/preset-lab-venv/bin/python tools/milk-analyzer/score_audit.py \
  --run build/core-audience-corpus \
  --output build/core-audience-corpus/score-audit.json
```

The report distinguishes missing, unresolved, arithmetically invalid and verified
records. `ready` is false until every corpus entry verifies. Arithmetic agreement
does not establish perceptual accuracy. The duplicate published-core coordinator
is stopped; the shared full-corpus owner uses `followup/quad-lines`. Selected
frame pairs from that baseline must not be treated as continuous measurements
for acceleration or flashing-rate features.

```bash
build/preset-lab-venv/bin/python tools/milk-analyzer/audience_export.py \
  --run build/core-audience-corpus \
  --aar build/core-audience-analysis/published/projectM-TV-core-2.2.4.aar \
  --output build/core-audience-review-assets
./gradlew :app:assembleDebug -PaudienceReview=true
```

The review flag selects the pinned published AAR, generated debug assets and
the separate app ID `nl.neerdael.projectmtv.audiencereview`. The menu shows only
the available All/Chill/Normal/Party groups. A separate line below the preset
name displays intensity and relative rank. Production updater checks are
disabled in this review app. Ordinary builds retain existing categories and
their core dependency. The review APK's asset merge is blocked until the
complete export and AAR/asset checksums verify; incomplete exports are not a
smaller substitute for the requested full collection.

Read preset equations and shaders without audio playback, a GPU context, or
reference images. This is research tooling under development. It does **not**
yet produce a validated appearance prediction or replacement Dance ranking.

The native reader exports projectM's typed EEL/HLSL representation and records
parser/build provenance. Syntax coverage and appearance accuracy are separate:
the refreshed corpus parse completed 9,510 of 9,606 presets in 47.4 seconds, while the
blind appearance-validation streak remains **0**.

The user has authorized full-corpus scoring, native numerical execution for
incomplete interpreter cases, and AI video inspection to learn correct behavior.
This supersedes the earlier pause on visual validation. Verified behavioral
coverage of executable code remains unmeasured; parsing and supported lowering
do not establish it. Preserve unsupported/unparsed source in coverage reports,
identify the backend for each score, and distinguish diagnosis or development
agreement from independent audience-fit validation.

## Source coverage audit

Instrumentation priority: `source_inventory.py` assigns every original code and
configuration token a source-bound ID, physical byte spans and one accounting
owner. It preserves native CR/LF line grammar and numbered-source assembly while
retaining duplicate/gapped/unsupported source. Ownership is exhaustive and
disjoint; altered payloads fail revalidation against the original bytes.

```bash
build/preset-lab-venv/bin/python tools/milk-analyzer/source_inventory.py \
  --presets core/src/main/assets/presets \
  --output build/milk-analyzer/current/source-ownership-census.json
```

The full census reproduces all 17,219,002 code and 6,240,357 configuration tokens
across 9,606 files. Per-file inventory fingerprints are retained; complete token
spans/IDs are regenerated deterministically when needed rather than storing a
large redundant token dump.

`behavior_evidence.py` validates evidence-record/proof bindings against actual
files: artifact paths/hashes, statement identity, profile, review record and closed
domain status. Stale, missing, conditional or malformed records fail closed.
The review decision remains a trusted workspace artifact; this validator does
not prove a theorem or establish applicability at an actual source use. It
returns `coverage_credit_granted: false`. Per-use obligation validation and the
strict >80% reducer are still required before reporting behavioral coverage.

Prioritize missing calculations by the number of distinct presets needing them.
`gap_priority.py` ranks known parsing/lowering gaps from the audit below. Section
uses and affected source tokens break ties; repeated frames cannot inflate the
priority. It retains source witnesses, dependency overlaps and counts of presets
with only that known gap. Those counts describe potential structural progress,
not presets proven predictable. Behavioral obligations still need enumeration.

```bash
build/preset-lab-venv/bin/python tools/milk-analyzer/gap_priority.py \
  --details build/milk-analyzer/current/source-coverage-audit.presets.jsonl \
  --output build/milk-analyzer/current/gap-priority.json
```

The immediate instrumentation scope is source inventory, frequency-ranked gaps
and comparable before/after support snapshots. The larger validation plan also
describes future certification, forecast integration and calibrated scoring;
those are separate work, not prerequisites for this small reporting layer. The end
goal remains source-only prediction for automatic classification and preference
driven preset generation; rendered observations validate forecasts independently.

The small reporting layer is implemented. After an interpreter change, refresh
the source audit and gap report, then save a uniquely named snapshot and compare
it with the previous one:

```bash
build/preset-lab-venv/bin/python tools/milk-analyzer/progress_report.py snapshot \
  --audit build/milk-analyzer/current/source-coverage-audit.json \
  --gaps build/milk-analyzer/current/gap-priority.json \
  --output build/milk-analyzer/progress/change-001-after.json

build/preset-lab-venv/bin/python tools/milk-analyzer/progress_report.py compare \
  --before build/milk-analyzer/progress/baseline-2026-10-03.json \
  --after build/milk-analyzer/progress/change-001-after.json \
  --output build/milk-analyzer/progress/change-001-report.json
```

Snapshot files cannot overwrite an existing baseline. The comparison writes a
companion `.md` report and JSON with exact preset lists for resolved and introduced
gaps, counts of presets gaining/losing their last recorded gap, and source-token
and percentage-point changes. Overlapping gaps do not imply independent gains;
unchanged totals cannot hide individual regressions. Changed corpus, metric
definitions or token denominators make snapshots non-comparable. Reader/model
provenance changes are reported because they are expected during development.
No earlier comparable snapshot exists yet; the initial baseline establishes the
starting point rather than claiming historical improvement.

The 9,097 files passing the current structural checks have **not** been shown to
have complete runtime semantics or accurate appearance forecasts. Prediction
readiness is unassessed across the corpus. Known integration gaps, including
source-driven shader randomness and remaining motion-vector precision/coverage, are not yet mapped
into this per-preset ranking. Add detectable runtime gaps to it as those checks
are implemented; the current count is not an exhaustive count of missing logic.

`motion_vectors.py` now models placement, fractional/capped grids, previous-map
sampling, minimum trail length and the native Y projection. Feed executed
`frame['main']` values to `SourcePipeline.step(motion_state=...)`; it draws vectors
on previous feedback before warp and retains the last active frame's RG16F map.
First-frame vectors are skipped. Activation without a previously initialized map
remains unresolved. Custom warp motion outputs follow the generated output,
including explicit preset overrides. Failed frames do not advance the map.

The post-warp scene drawer requires `motion_vectors_prewarped=True` when the
pipeline handled active vectors (including its first-frame skip). Canonical
unsmoothed line coverage is an explicit approximation. GPU precision and desktop
line smoothing remain unverified. Equation initialization preserves the legacy
`bMotionVectorsOn` fallback and explicit `mv_a` override.

The source census at `build/milk-analyzer/current/motion-vector-source-census.json`
finds 734 presets initially enabling vectors and 2,487 referencing motion controls
in main equations, with 2,869 distinct candidates. Initial controls can change
during equations; a reference does not prove an active effect. These counts
prioritize the feature, not certify complete appearance predictions.

`milk-shader-random` executes copied native constructor and random-uniform math
without GL or rendered inputs. `shader_random.execute_ledger` requires the actual
post-mix C-rand seed and an ordered list of `construct`/`load` events, including
idle/fallback instances and loaded stages whose random uniforms are unused.
Each construction consumes 184 draws; each load consumes 28. Bind a load by event
index, shader ID, float32 time and recorded profile, then pass its bank through
`SourcePipeline.step(stage_uniforms={'warp': ..., 'composite': ...})`.

The bank includes preset/frame vectors and all 24 rotation matrices. The native
mat4-to-mat3x4 upload drops the translation column; restoring it would predict
different geometry. Native CPU bodies and GLM headers are hash-bound in the
result. This uses host libc/compiler behavior and does not establish Android
equivalence or infer the full engine lifecycle. Shader/compiler fallback and
production-profile stream binding remain separate requirements.

`build/milk-analyzer/current/shader-random-source-census.json` finds 3,025 distinct
source candidates across 3,160 shader sections. `rand_frame` appears in output/
effect dependency graphs for 2,729 presets, and `rand_preset` for 375 (overlapping).
These are conservative potential dependencies from active lowered shader graphs;
426 presets have an incomplete dependency inventory. Visibility, amplitude and
native compile fallback are not established by the census. Random dependence
alone does not establish flashing.

Audience matching targets colour variety, flashing intensity/area/cadence, motion
speed and smoothness, complexity/density, structure and causal bass response.
Combine these into editable gentle/chill, party and psychedelic preferences.
A colourful preset can be calm, and complex geometry need not flash. No audience
classification is validated by implementing the motion-vector path alone.

`forecast.py` now composes source equations, per-vertex warp, common/per-stage
uniforms, builtin/custom waves, shapes, motion vectors, blur, feedback and final
composite under an explicit domain. `read_source` freezes the original bytes and
binds parser output to the actual reader binary. `forecast_source` consumes
source-generated audio, source-bound stage evidence, initial RGBA/hue state,
equation seed and optional random lifecycle/noise bank. Missing bindings remain
errors; named shape images without a resolved material registry are not silently
replaced with previous main.

Textured shapes receive the previous feedback surface after motion-vector
drawing, before warp, rather than the newly warped/drawn image. Source inputs and
domain dictionaries are copied to prevent callbacks changing them mid-run.
`retain_surfaces=False` and `on_frame` allow streaming measurements without
retaining all framebuffer arrays. Results include source/audio/domain/model and
binary identities; `status: computed` means the declared model executed, while
`appearance_accuracy_verified: false` remains explicit.

Renderer time remains double for hue and builtin-wave math, with narrowing at
native expression boundaries; EEL and shader inputs retain their separate float
conversions. The CPU waveform adapter was corrected to use the renderer's double
time and JSON double parsing. Numerical tests cover a long-clock case that the
previous float adapter got wrong.

`build/milk-analyzer/current/forecast-case002-source-check.json` records a
source-only integration run for the already-viewed `437.milk`: 30 frames at
128x72/30 FPS computed in 10.81 seconds, with no native rendered input. Its state,
RNG lifecycle and profile are declared fixture inputs, not inferred production
startup. This is one-case throughput, not a corpus runtime or accuracy estimate.
Named image registry, input lifecycle/target binding, descriptor extraction and
calibrated appearance validation remain unfinished.

`descriptors.py` measures the source forecast's predicted fields numerically.
`forecast_source` now returns a descriptor report even when surfaces are streamed
and discarded. It includes spatial/temporal hue diversity, coloured fraction,
saturation, encoded-RGB luma/contrast, brightness and chromatic change area,
coherent brightening/darkening transitions and sampled brightness periodicity.
Settings and warmup are explicit through `descriptor_settings` and
`descriptor_warmup_frames` in the domain.

Visible motion uses brightness-normalized optical flow on the source prediction,
with backward correspondence, residual and texture-support checks. Speed and
acceleration use viewport-relative units. Warp query displacement is separate:
a moving coordinate map over a uniform colour does not establish visible motion.
Unsupported correspondence yields null motion speed, not a calm/slow label.
The report records aggregation definitions and sampled frequency resolution/
Nyquist limits. It does not certify physical luminance, absence of flashing
outside the window, fractal structure or causal bass response. Mood assignment
remains null pending calibrated thresholds and descriptor validation.

Numerical fixtures distinguish three-colour/grey/black palettes, full-screen
brightness pulses, equal-luma colour switches, known textured translations and
geometric displacement without visible texture. The authored full-forecast
controls in `build/milk-analyzer/current/source-descriptor-controls.json` test a
steady palette and a declared two-Hz brightness oscillator without native frames.

`source_bass.py` now predicts causal bass response with matched source forecasts.
`predict_bass_response` repeats the control exactly, verifies pre-intervention
warmup, then applies declared `bass`/`bass_att` schedules while preserving PCM,
waveform, spectrum, other bands, time, state, random inputs and materials.
`vol`/`vol_att` are recomputed with native float32 `.333f` from the changed bands;
they are dependent inputs, not independently held constants. Invalid/no-change
interventions and control drift cannot yield a response measurement.

The response report includes mean RGB difference over the whole predicted screen,
affected area above 8/255, local intensity, 95th-percentile and maximum response,
delay from actual input onset and the complete time trajectory. Feedback response
after the pulse remains visible. A short strong effect is retained in the maximum
even when the robust percentile is zero. Multiple doses reveal thresholds or
saturation; a single dose is not extrapolated into a universal reactivity score.
Baseline surfaces are stored in a temporary memory-mapped file and variants are
streamed, avoiding simultaneous in-memory histories for every run. This is a
source-model counterfactual, not validated native screen response or a final Dance
ranking. Prediction/native calibration and causal structure evidence remain
separate from these measurements.

The already-viewed `437.milk` short source check is recorded in
`build/milk-analyzer/current/source-bass-case002-check.json`: 15 frames at 64x36,
three band-dose schedules, exact repeated control, computed in 19.44 seconds.
Maximum affected areas were 15.4%, 29.3% and 54.6% for additive band doses .25,
.5 and 1.0. These are predicted changes above the declared threshold, not native
observations, perceptual agreement percentages or a production ranking.

`materials.py` adds named image inputs to the source forecaster. The CPU image
bridge uses the pinned SOIL2 stb decoder and SOIL's integer alpha multiplication,
preserving row order and RGBA bytes without GL or rendered frames. All 74 bundled
images decoded; the largest is 2500x1250. File/pixel, decoder and implementation
identities are retained in
`build/milk-analyzer/current/named-material-inputs.json`.

Construct `MaterialBank(paths, decoder=..., noise_bank=...)` from explicit files
and pass `materials=bank` to forecasts or bass experiments. It combines optional
procedural inputs, rejects ambiguous case-insensitive stems, resolves named
shader/shape samples and preserves generated `texsize_*` uniform spelling.
Known named shapes use texture aspect 1.0; previous-main shapes retain viewport
aspect. Sampler qualifiers retain point/linear and wrap/clamp behavior. Corrupt
images and sizes requiring unsupported rescaling remain unresolved. Random
texture choices, target maximum-size/NPOT behavior and missing placeholder state
are not inferred. Appearance accuracy and audience suitability remain unverified.

Run from the worktree root, using the parser snapshot identified by its summary:

```bash
build/preset-lab-venv/bin/python tools/milk-analyzer/coverage_audit.py \
  --presets core/src/main/assets/presets \
  --summary build/milk-analyzer/current/summary.json \
  --output build/milk-analyzer/current/source-coverage-audit.json
```

The audit inventories original lexical tokens, rather than optimized EEL AST
nodes or shader trees with expanded engine headers. Numbered code values,
configuration assignments and unclassified rows have separate stage totals.
Blank lines, comments and section headers are excluded. Disabled source,
duplicate keys, numbering gaps, failed parses and unsupported component indices
remain in the inventory. Each unit records source lines and its source hash.
This deliberately measures source volume, not semantic complexity, visibility
or visual influence. Repeated simulated frames cannot increase these counts.

For the 9,606-preset snapshot, there are 23,459,359 inventory tokens: 17,219,002
code/unclassified tokens and 6,240,357 configuration tokens. Native-compatible
parsing accounts for 99.71% of the code tokens. Entire shader sections that lower
without an unknown account for 95.88% of original shader tokens; partial sections
receive no lowering credit. These differ from the earlier section-count metrics.
952 code/unclassified tokens are not reached by the supported numbered-source
loader (including unsupported component indices) or belong to unclassified rows.
Cache source/reader identities must match,
and reconstructed numbered source must match the cached section before it can
receive parsing credit. Missing caches remain uncovered in the same denominator.

The summary and per-preset JSONL contain `verified_behavior_percent: null` and
an ineligible visual gate. **Neither parsing nor complete lowering provides
behavioral verification.** The missing evidence list covers source-to-reference
and fixture mapping, per-use state contexts, numeric domains/termination,
materials/uniforms/start state, complete chain integration and differential or
analytic verification under declared profiles. The audit itself reads no audio,
renders or reference images. Its input, corpus and implementation hashes make
the inventory reproducible; they do not attest to mathematical correctness.

## Effective rendering stages

`stage_resolution.resolve_stages` selects fixed warp, custom warp, default
composite, custom composite or the legacy echo/gamma/filter path. Selection
uses native numeric-prefix parsing and version rules: files below version 200
disable shaders; version 200 uses shared `PSVERSION`; later files use separate
levels. The native constructor defaults both levels to 2. Shader code omitted
at a positive level selects fixed warp/default composite rather than legacy
gamma. Reader activity metadata now follows those same defaults.

Custom-stage decisions require matching shader-source identity, target profile
and engine archive in offline compatibility evidence. Missing/stale evidence
and native process failures remain unknown. Offline acceptance/rejection stays
conditional on actual descriptor, driver and link behavior; math/domain errors
do not trigger a fallback. A census of 9,606 presets identifies 1,779 legacy composite
paths and 1,833 fixed warp paths for the desktop profile; custom stages without
the current targeted compiler evidence remain unknown in this census.

`SourcePipeline.from_source` connects those decisions to numeric execution.
Fixed warp applies live decay capped at 1 and preserves sampled alpha. Custom
warp receives the same decay vertex diffuse when supplied. Default composite
samples pre-composite feedback with the native half-texel offset and opaque
output alpha, bypassing legacy gamma/echo/filters. Legacy display uses file-level
controls, explicit render time and four explicit hue offsets; similarly named
per-frame equations do not override these static values in the pinned renderer.

`legacy_composite.py` implements overscan, triangle-interpolated corner shades,
clamp/linear texture sampling, echo zoom/orientation, additive gamma redraws and
native brighten/darken/solarize/invert blend order. Framebuffer quantization
occurs after each blend. Negative echo orientation retains C++ remainder rules.
Missing random inputs and invalid/unwritten display domains remain unresolved.
The 4,096-redraw budget is an explicit computation limit, not a native limit.
These source/math fixtures do not establish GPU precision or visual accuracy.

`composite_mesh.py` now supplies the native 32×24 nonuniform composite mesh,
duplicated central seams, quadrant-specific triangle diagonals, normalized radius,
angular fixups, half-texel UVs and interpolated hue diffuse. Pass `render_time`
and explicit `hue_offsets` to `SourcePipeline.step` for composite colour inputs;
polar inputs are derived automatically, while missing hue inputs remain unknown.
The composite corner mapping differs from legacy VideoEcho. The pinned colour
method does not scale these values using the file's `fShader` control.

`milk-composite-inputs` executes unchanged native mesh/hue CPU bodies with minimal
state views and the GL buffer-upload tail omitted. Three profile comparisons
match positions/UVs and all 3,960 indices exactly; polar error is below 6×10⁻⁸
and colour error below 1.2×10⁻⁷. A separate barycentric check against native
physical vertex positions/indices has maximum error 3.7×10⁻⁷ on 64 queries.
These are numerical checks, not GPU/reference-image or appearance validation.
Angular seam ownership and raster subpixel/rounding remain explicit limits.

## Current interpretation

- Execute native EEL equations with explicit state, q/register resets and shared
  memory. Retain native numeric precision and nonfinite values in the export.
  Programs may share an explicit component scope, so init/frame code shares its
  local variables and `megabuf` while other components retain separate locals.
- Load main and custom-shape defaults from the file and run their initialization,
  frame and instance equations automatically. Preserve native positive-only
  boolean flags, numeric-prefix parsing, float32 storage and range fallbacks.
  Main Q and shape T values reset from saved initialization defaults while custom
  locals persist. Disabled wave/shape initializers still run in native order.
  Explicit seeds make equation randomness repeatable within the pinned host
  execution profile; this does not establish cross-platform random equivalence.
- Execute per-pixel equations in native row order with a separate persistent
  context. Load external read-only inputs before main equations, copy Q after
  main equations, then preserve Q/custom/memory changes across mesh vertices.
  Native frame and pixel aspect conventions remain distinct. Time/audio/aspect
  inputs retain native float32 storage before entering double-precision EEL.
- Derive warp coordinates and polar fields automatically from those equation
  outputs, float32 vertex storage and native triangle interpolation.
  Supply deterministic shader time/audio/oscillator/mip and saved-Q uniforms
  from render state; shader random vectors/matrices remain unresolved.
- Lower supported shader operations into a typed expression graph, preserving
  assignment order, conditional colour paths, swizzles, sampler identity,
  coordinates, and texture history. Inline helpers with a single terminal return,
  default arguments and separate local/global bindings.
  A local declaration without an initializer remains pending until read: assigning
  it before use is supported; a possible uninitialized read stays unknown.
- Track initialization per component, including values assigned progressively
  through loops. Swizzles and narrowing casts consume only their selected
  components; native widening casts define zero padding. Dynamic vector-index
  writes retain scalar casts, per-lane selection and bounds checks, including
  writes later overwritten. Single matrix-component access preserves HLSL row
  and column order. Matrix row writes remain unresolved.
- Keep array storage separate from its element type, preserving constant-expression
  lengths, initialized elements, component validity, dynamic indexed writes,
  helper arguments and loop-carried state. Indices retain native integer truncation
  and explicit bounds checks. Branches check only selected lanes; an overwritten
  out-of-bounds write cannot disappear. Unwritten elements/components remain
  unknown rather than zero. The explicit storage budget is 4,096 elements and
  is not a native language limit. Side effects inside index expressions remain
  unresolved. Native array constructors retain element boundaries; invalid flat
  grouping and partial initializers do not become usable arrays.
- Distinguish ordinary uninitialized globals from actual uniforms and texture
  bindings. Native reader-generated texture-size declarations now carry the
  actual uniform qualifier. Apply the generator's native
  `ReplaceUniformsAssignments` transformation before exporting shader trees.
  Assignments create function-local replacements without initializing other
  packed components; a first assignment's right side reads the original uniform.
  Unwritten components remain unknown. Preserve independent helper-local state.
  Unrewritten uniform increments and same-name initializers remain unresolved.
- Preserve the pinned renderer's DX9 compatibility lowering: `sqrt`, `rsqrt`,
  `log`, `log2`, and ordinary `pow` apply `abs` to their relevant input. A literal
  exponent of one makes `pow` return the signed base. Floating remainder and
  `fmod` follow the generated GLSL `mod` operation. Vector casts zero-extend when
  the generator requires more components.
- Retain native floating constants alongside the exact decimal text emitted by
  projectM's `String_FormatFloat`; evaluate emitted literals rather than assuming
  the parser's binary32 value survives shader translation unchanged.
- Preserve native square-matrix linear products for bare `*` and `*=`, distinct
  from component-wise HLSL intent. Arithmetic scalar-to-matrix casts create a
  diagonal matrix; declaration/explicit-constructor helpers fill rows and pad
  remaining cells with zeros. Matrix resizing copies overlapping coordinates
  and fills new cells from an identity matrix. Track the shader-wide constructor
  registry: a registered matrix-copy helper ignores its matrix arguments, and
  can zero other matching declaration initializers. Scalar and batched numeric
  fixtures cover these differences; GPU rounding/FMA equivalence remains unproved.
- Track pre-composite feedback, the distinct main/blur ages, motion vectors drawn
  onto previous feedback, and vertical flips applied to main sampling.
- Evaluate the source's full warp vertex operation order, native mesh triangle
  interpolation, texel-centre sampling, addressing and sampler binding policies.
  Preserve prefixed main-sampler history; keep unbound frame wrap symbolic.
- Extract supported affine RGBA-to-colour transfers from typed shader expressions
  and compose them on explicit spatial fields. Mathematical fixtures demonstrate
  wrapped repeated layers that scalar decay cannot locate. Nonlinear or multiple
  distinct-coordinate transfers remain unresolved by this reduction.
- Compute the native six-pass blur kernels, size rounding, first-pass vertical
  flip, progressive range encoding and first-level edge darkening on explicit
  physical framebuffer fields. This still needs full shader/drawing integration;
  GPU precision, quantization and dithering remain validation concerns.
- Evaluate supported nonlinear shader expressions across full coordinate grids,
  with separate lane/component axes and per-lane conditional/logical guards.
  Vector/matrix operations and texture callbacks preserve types, coordinates and
  history; invalid selected domains remain unresolved.
- Execute supported `for`/`while` loops with float32 state, native counter scope,
  per-lane stopping, nested loops and helper calls. Pre/post increment and
  decrement retain their returned and stored values. Loop outputs share one
  execution; conditional loop branches sample only their active lanes. Empty or
  unused loops cannot hide nontermination from the mathematical evaluator.
  Limits are 1,024 iterations per loop and 16,384 combined nested steps per
  evaluation. Exceeding a limit raises an unresolved result; these computation
  budgets are not native limits or proofs that arbitrary inputs terminate.
- Compose these expressions in `SourcePipeline` across warp, explicit source
  drawing, blur and composite stages. The displayed composite is separate from
  next-frame feedback; the two blur ages and physical texture orientation are
  retained. Failed evaluation does not advance the stored history.
- Trace source-derived sampling coordinates with stage, sample-site, texture
  history and selected output lanes, including loop iterations. Compute local
  inverse-Jacobian feature transport, periodic seam-aware stencils, exact repeated
  affine maps and separable wrapped fixed-point candidates. Local contraction is
  distinct from brightness gain or a proved global nonlinear attractor.
- Obtain actual procedural noise buffers through a CPU-only bridge to the pinned
  native generator. Packed-word hashes, physical dimensions, seed and upload
  channel order are explicit. `NoiseBank` supplies texture-size uniforms and
  2D/3D sampling to the shader pipeline without rendered reference inputs.
- Export exact native PCM waveform alignment, FFT and relative/smoothed bands
  through `milk-audio-inputs`, without a graphics context. A720frame same-PCM
  check matches all six previously recorded native band traces exactly.
- Execute all16built-in waveform geometry modes using unchanged pinned math
  bodies compiled in an isolated namespace with data-only state views. Native
  smoothing tails, loop closure and mode-specific domains persist. Original,
  adapted and adapter hashes accompany the outputs. `source_builtin_wave`
  joins audio/main equations to geometry, projection, colour/opacity and static
  draw flags. Line/point raster coverage and full drawing integration are pending.
- Execute custom-wave init/frame/point equations through the native evaluator
  with separate contexts, persistent locals, frame Q/T copies and point-to-point
  Q/T carry. Preserve mutable-main point inputs versus external frame audio inputs.
  Native sample counts, spectrum stride and stereo forward/backward smoothing
  feed each point. `source_custom_waves` applies native projection, float storage,
  colour modulo, geometry smoothing and static line/dot/thick settings.
- Rasterize supported unsmoothed lines with canonical diamond-exit coverage,
  half-open endpoints and per-fragment colour interpolation; points use square
  coverage and centre clipping. Draw source shapes/outlines, custom waves, builtin
  waveform, centre darkening and borders in native order. Native drivers may use
  bounded alternative raster rules; bit-identical coverage remains unproved.
- Convert explicit shape-equation outputs into native polygon fans, with aspect,
  projection, centre/perimeter colour interpolation and texture coordinates.
  Source alpha blending, colour wrapping, shared-edge fill ownership and per-draw
  framebuffer storage are implemented. Outer/inner border fans follow native
  geometry and draw order. Outline/wave drawing, complete scene
  loading and native rasterization precision are still incomplete.
- Analyze declared affine feedback reductions. A two-age recurrence retains its
  separate coefficients; its characteristic-root result applies to the
  unsaturated linear model, not arbitrary clipped or spatial feedback.

`ShaderFields.complete` means the implemented lowering encountered no unsupported
construct. It does not establish complete runtime compatibility, numeric domains,
texture contents, appearance, or prediction accuracy. The exported native report
continues to report `semantics_complete: false`.

`milk-shader-translate` copies the pinned native CPU preparation/translation
bodies into the build directory and links the unchanged parser/generator archive.
Data-only views supply the header and explicit GLSL330/GLES300 profile; sampler
and texture-size declarations are explicit inputs. The bridge creates no GL
context and links no OpenGL framework. `shader_compat.check_shader` validates its
generated fragment source with `glslangValidator`, recording binary/source hashes
and compiler diagnostics. Rejection predicts fixed warp or default composite
according to the native stage's exception handler, conditional on the supplied
profile/descriptors and successful fallback initialization. Driver compilation,
linking, material loading and numeric behavior remain separate checks.

A source-only probe revisited all 436 shader sections previously blocked by uniform
writes. 413 now lower completely; 23 retain possible uninitialized reads, with some
overlapping array/helper gaps. All 436 translated fragments pass offline GLSL330
compilation; 435 pass GLES300. `EVET - Spiracology 2.milk` has a GLES-only mixed
float/int expression rejection under these explicit declarations. These results
are stored in `build/milk-analyzer/current/uniform-rewrite-compatibility.json` and
do not count toward appearance validation or the behavioral percentage gate.

The matrix update resolves all 82 sections previously blocked by bare matrix
multiplication. Their generated fragments pass offline GLSL330 and GLES300
validation under explicit reader-derived descriptor declarations. Mathematical
fixtures verify product order, diagonal casts, zero padding, coordinate-based
resize and shader-wide constructor effects. The source-only results are in
`build/milk-analyzer/current/matrix-compatibility-probe.json`; native driver,
full runtime-domain and appearance verification remain outstanding.

The array update revisits 80 blocked sections: 23 now lower completely, 56 have
initializer layouts rejected by both offline target compilers, and one retains
uninitialized-read uncertainty. Desktop accepts 24 translated fragments; GLES
accepts 23, including the previously identified target-specific difference.
Results are in `build/milk-analyzer/current/array-compatibility-probe.json`.
Desktop and GLES also differ on integer values in float-array constructors;
offline profile checks remain necessary. A native unsized-array helper fixture
crashes the isolated translator process. `shader_compat` reports process failure,
timeout or invalid output as unknown, with no predicted fallback. This is separate
from an established syntax rejection and leaves the pinned engine untouched.

Unsupported bitwise unary expressions, conditional/logical assignment effects,
unsequenced arithmetic/comparison updates, helper output arguments,
loop-condition side effects, `break`/`continue`, branch/loop-dependent helper returns,
unresolved array sizes/initializer layouts, index-expression side effects,
non-writable matrix row assignments and same-name initializer
binding differences,
projected/gradient sampling and general mipmapped LOD/bias sampling, overfilled matrix constructors, and
rectangular bare matrix products without a native GLSL helper remain
explicitly unresolved. An unresolved statement also makes the returned shader
result unknown; a discarded expression cannot silently hide lost state changes.
The numeric evaluator raises on absent symbolic inputs, unsupported operations,
or nonfinite domains/conversions. Its binary32 arithmetic is not guaranteed to
match GPU rounding, fused operations or transcendental functions bit for bit.

`tex2Dbias` and `tex2Dlod` preserve packed-coordinate XY and evaluate their W
selector under the pinned native sampler policy. Those samplers use non-mipmap
minification filters at base level zero, so finite LOD/bias changes do not create
visible texture changes by themselves. Missing/nonfinite selectors and unproven
sampler policies remain unresolved. Four frozen high-frequency texture controls
match the published core's RGBA8 output across 30 frames each; all 14 historical
source witnesses lower completely. This verifies the bounded sampling behaviour,
not complete appearance prediction. See
`fixtures/texture-lod-native-proof-2026-10-04.json` and
`fixtures/texture-lod-source-proof-2026-10-04.json`.

Plain sampler aliases follow native declaration rebuilding, including removal
of the declaration's remaining line and preservation of preceding qualifiers.
This closes 67 of 83 historical shader parse witnesses; 63 lower completely.
Sampler-state initializers remain governed by their separate compatibility gate.
See `fixtures/sampler-alias-source-proof-2026-10-04.json`; these source checks
do not establish whole-preset appearance accuracy.

Helpers stop at their first top-level unconditional return. Unreachable trailing
arithmetic, reads and shared writes are excluded from evaluation and transitive
effect analysis. State changes before the return remain visible to callers.
Branch/loop-dependent returns still require path-aware lowering and stay
unresolved. Two frozen native controls match all 30 frames each; the four
historical duplicate-return presets still have other unresolved domains/effects.
See `fixtures/helper-return-native-proof-2026-10-04.json` and
`fixtures/helper-return-source-proof-2026-10-04.json`.

Sequenced helper global writes now survive calls, parameter/local shadowing,
branches and loops. Transitive helper writes become loop-carried state; unsafe
shared-read/write ordering remains explicit. Destination indices are captured
before assignment RHS evaluation according to the GLSL330/GLES300 target rules.
All 14 distinct recorded helper-global-write witness sections now lower. Three
analytic helper-state fixtures matched the unchanged published core on an
isolated API34 emulator with zero RGB8 error across all30 frames each. See
`fixtures/helper-state-source-recheck-2026-10-04.json` and
`fixtures/helper-state-native-proof-2026-10-04.json`. This does not establish
whole-preset appearance accuracy.

`modf` now returns a signed fractional value and writes the floating integral
part to output storage without reading its old value. Output writes survive
local/global loops, aliases, swizzles and array cells. Function-call arguments
follow the GLSL target's left-to-right rule; unsafe operand and compound-value
conflicts remain unknown. All nine recorded source witnesses lower completely.
Four published-core emulator fixtures match all30 frames each with zero RGB8
error. The pinned translator accepts scalar calls but rejects vector calls;
numerical vector semantics and runtime compatibility stay separate. Evidence:
`fixtures/modf-source-proof-2026-10-04.json` and
`fixtures/modf-native-proof-2026-10-04.json`.

Sampler-state values are not applied as native filtering directives. Accepted
custom stages may supply explicit runtime sampler bindings; the model then uses
TextureManager's name-based policy. Source-matched rejection selects fallback
instead of interpreting that custom shader. The offline bridge now also copies
native sampler-reference lookup, catching malformed identifiers that AST-based
lookup misses. All51 saved state witnesses reject in the pinned GLES300 check.
Two initial local-declaration predictions failed and led to this correction;
two new correctly delimited sources match the published emulator with zero RGB8
error across all30 frames each. See
`docs/superpowers/evidence/2026-10-04-sampler-runtime-learning.md` for details and
the preserved failures.

Remaining work includes faithful source geometry/rasterization, external texture
loading and random shader uniforms, complete drawing/blend ordering, all helper/loop/control-flow
semantics, discarded fragments and native precision verification. The numeric
pipeline currently requires explicit coordinates, uniforms, source drawing and
external textures; it is not yet a complete automatic preset simulation. These
must be connected into a complete effect model before retrying
the blind benchmark or changing the published collection.

The refreshed structural pass translates 7,132 of 7,773 active warp stages (91.8%)
and 7,509 of 7,821 active composite stages (96.0%), including syntax-unknown
stages in those denominators. This is about93.9% of active shader stages, not a
percentage of verified executable-code behavior. It does not open the80% gate.
A real corpus shader with a sixteen-iteration loop matched an independent
algebraic result under declared constant-texture/audio/Q inputs, with maximum
absolute error below2e-8. This is numerical evidence for that case and domain;
its complete appearance remains unproved.

The component-state update also matched a corpus shader's HLSL-tree calculation
to an independent algebraic result. A subsequent target-translation audit found
its `ret1=ret1` local initializer has a different binding in emitted GLSL. The
probe now explicitly records that compatibility gap and is not target-runtime
verification. Preserve the distinction between understood authoring arithmetic
and the actual renderer's behavior.

## Regression from the first blind failure

The frozen first prediction missed a dominant beam. Its original prediction and
failure stay unchanged. The preset is now a regression case and cannot count
toward the random-validation streak.

Source tracing identified a rotated inverse-square-root brightness seed, with a
mirrored domain because the renderer generates `sqrt(abs(s))`. Under explicitly
declared constant-texture assumptions, the parsed warp prefix gives the red
recurrence

```text
x[t] = 0.990495*x[t-1] - 0.0297*x[t-2] + j(s)
j(s) = 0.99*(0.018 + 0.008/(sqrt(abs(s)) + 0.2)) - 0.04
```

The source-only regression checks a narrow mirrored seed, rotation of its normal,
and separate feedback coefficients. Renaming temporary variables leaves those
results unchanged. The local unsaturated dominant half-life is about 16.78 frames.
Colour branches, spatial gradients, clipping and actual texture contents are
outside this reduction, so it is not a complete appearance prediction.

Keep the acceptance rule: **100 consecutive randomly selected presets, each
prediction at least 70% accurate**. No new visual trials are running while the
full-chain model is being improved.

On 2026-10-03 the user requested a small diagnostic before the complete model was
ready. The next previously selected random preset, `437.milk`, was predicted and
frozen before rendering. The check recognized its changing colours, horizontal
mirror arrangement, ribbons and dotted accents, but underpredicted the repeated
fan-like feedback layers and reversed the live geometry's vertical placement.
It scored 62.5 points on its frozen descriptive checklist; this is subjective
diagnostic scoring, not a calibrated visual-accuracy percentage. The acceptance
streak remains zero, and this viewed preset is ineligible for a future blind case.

The projection error was traced to the source's inverted orthographic projection;
`geometry.py` now distinguishes native custom-wave and shape position transforms.
Three mathematical fixtures verify that correction without image references. The
remaining repeated-image gap requires actual spatial mesh UV transforms, texture
wrapping, blending and blur over successive feedback frames. The original frozen
forecast and its mismatches remain preserved.

The subsequent source-only mesh trace now finds approximately one-third of the
canvas querying outside the unit square in sampled `437.milk` frames. Native
wrapping redirects these queries to the opposite edges. The shader's `.85`
sample gain and `-.022` bias are extracted from the typed graph rather than
entered as assumptions. This explains a mechanism for the missed layers; it does
not yet prove the complete displayed extent or a revised accuracy score.

A subsequent source-only probe executes the first failed preset's complete warp
and composite expressions with the blur/feedback integration. Under explicitly
simplified inputs (identity mesh coordinates, no source draws, q registers zero,
constant .5 RGBA noise and zero edge darkening), the computed field contains a
full-height blue band and increasing coverage across sixty frames. This recovers
the previously missed shader mechanism without reference images. It does not
establish the complete preset's appearance or count as a new blind pass.

## Numeric field pipeline

`grid_math.py` evaluates typed expressions across an explicit `batch_shape`.
Uniform and field input shapes are distinguished; texture callbacks receive the
selected lanes' coordinates. Conditional and logical guards evaluate only the
needed lanes, preserving domain guards such as `x != 0 && 1/x > 0`.

`SourcePipeline` requires an explicit initial RGBA feedback surface, warp UV
field, equation uniforms and frame wrap value. Drawing, motion-vector and
external texture functions are explicit inputs. It supplies viewport, aspect and
blur-range uniforms, the native composite half-texel UV offset, physical blur
sampling and pre-composite feedback history. Unsupported stages or missing
textures raise rather than becoming black or zero-effect predictions.

This pipeline assumes the supplied drawing functions faithfully implement native
draw order and per-draw storage/blending. It cannot yet load and reproduce every
component from a `.milk` file by itself. `appearance_prediction_complete` remains
false; numerical fixtures are implementation evidence rather than visual scores.

## Viewer preferences

The intended matching descriptors include motion speed/smoothness, flashing,
screen coverage, symmetry, grain/texture, colour, and the mechanism and magnitude
of audio response. Their evidence must distinguish proved code properties,
conditional simulation results and unresolved appearance. Accurate descriptors
can be matched to editable home-TV preferences; a parsed shader or a broad genre
label alone cannot establish audience fit. No revised preference ranking or
production collection is exported from this partial model.

The same verified mechanisms could support personalized preset generation:
deliberate bass-response magnitude, smooth or sharp movement, colour and feedback
controls driven by editable viewer preferences. This is a future application of
the interpreter, with visual quality still to be evaluated; it is not a change
to the current semantic-coverage and blind-validation requirements.

## Third diagnostic and feedback concentration

The user explicitly authorized one visual prediction check after setting the
80% behavioral-understanding gate. The next unviewed preset from the frozen
random list was predicted before rendering. Its grayscale palette, layered
waveforms, glow, broad extent and live line positions matched; the prominent
central vertical concentration was underpredicted. The fixed descriptive rubric
gave87.5points, with live-line peaks within about2pixels of predicted positions.
This is a subjective single-case diagnostic, not a calibrated accuracy percentage
or an accepted streak case. Broader visual trials are paused again.

A subsequent source-only sampling trace computes the shader's coordinate map
under explicitly uniform main/blur states. For rc values.05,.2,.5,1, its query
scale is1+.03*rc. Inverting that map predicts horizontal contraction, and wrapped
fixed-point analysis finds interior horizontal stationary positions with no
interior vertical stationary position in those declared cases. This supports a
mechanism for a column rather than a stationary point. The source's+.0005 vertex
translation shifts the horizontal positions away from exactly.5.

Under the constant rc=1 affine branch, a feature's horizontal width falls to
about2.9% after120frames. Real rc varies in space/time, addressing branches may
change, and RGB interpolation/drawing/blur affect prominence; the constant-map
calculation is not a global guarantee for the actual preset. No reference image
is an input to this math, and the frozen prediction remains unchanged.

The subsequent source-wave run now obtains input from raw PCM through the pinned
CPU audio engine, executes main EEL and feeds the resulting variables into native
waveform geometry. All720frames of the diagnostic preset produce159smoothed line
vertices plus their source-derived colour and four native copy offsets. This
removes the earlier analytic line-position approximation from the drawing spec;
it does not yet verify hardware rasterization or complete feedback dominance.

Build `milk-audio-inputs` and `milk-wave-inputs` with the existing CMake setup.
The audio request supplies `pcm_path`, `output`, integer `fps` (30/60), `frames`
and `channels` (1/2). The waveform request supplies explicit native-sized audio
arrays, main wave variables, mode and file-level scale/smoothing settings.
Spectrum log-zero and lasso zero-angle domains raise unresolved errors rather
than inventing finite vertices. The source generator changes namespace/includes
only; graphics constructors and GL calls are never executed.

`scene_draw.draw_source_scene` connects geometry to the feedback surface using
the explicit canonical coverage model. Missing texture inputs or pre-warp motion
vector integration remain unresolved. The zero-base/nonpositive-exponent `pow`
domain now raises instead of inheriting NumPy's0^0=1 result. In the third
diagnostic preset this makes the actual black start unresolved. A declared
positive1/255seed allows240source-driven frames to complete, but that alternative
state becomes nearly white; it does not prove the native column's dominance.
This source-only run records its assumptions and does not change the frozen
prediction or count toward visual acceptance.

## Procedural texture inputs

The `milk-noise-inputs` executable receives a JSON request with `seed`, `output`
and builtin texture `names`. It calls the existing archive's protected CPU
generators, writes little-endian packed words and a provenance/hash manifest, and
creates no graphics context. The linked OpenGL library only resolves unused
texture-upload functions in the same archive object.

`NoiseBank(directory)` verifies the buffers, interprets native RGBA/BGRA channel
order and exposes `uniforms()` and `sample()` for `SourcePipeline`. An explicit
upload-format override can model GLES channel interpretation; it does not prove
identical host/Android random-library output. Volume sampling preserves raw
OpenGL XYZ layout and trilinear texel centres. Actual generation—including the
pinned volume smoothing strides—is retained instead of substituting another
implementation's intended output.

The first failed preset's sixty-frame mathematical probe now also runs with
native procedural buffers in place of constant noise. Its computed field still
contains the full-height blue band. Identity mesh coordinates, omitted source
draws and zero Q registers remain explicit simplifications, so this is not a
complete appearance prediction or a blind validation pass.

## Equation execution scopes

`scene_equations.execute_scene` builds these requests directly from the native
source report and explicit audio/time frames. It currently orchestrates main and
custom-shape, per-pixel and custom-wave equations. Active waves require explicit
native-sized audio arrays; their frame and point groups run in native draw order.
Target-incompatible equation sections are rejected. A source-only
check on the first failed preset executed twenty frames and 20,480 shape
instances, with a recorded seed and parser/executor identity. This verifies the
connection to real source code, not a complete visual prediction or blind pass.

`scene_warp.warp_fields` connects its vertex outputs to the spatial pipeline;
`shader_uniforms.source_uniforms` supplies saved frame Q and deterministic native
shader inputs. A twenty-frame mathematical run of the first failed preset now
uses actual source warp transforms, Q values, 20,480 shape instances, border
fills and blur settings rather than the earlier identity/zero-Q/no-draw inputs.
At the recorded module versions it took about 3.3 seconds and calculated a strong
blue band spanning the field's height. The report preserves its exact source
hashes and declared cold-start/host-noise/CPU-rasterization conditions. It uses no
reference images and provides no new visual accuracy score. This known-failure
check can catch future breakage; it does not mean predictor quality regressed.

An execution request can retain the existing string form (one scope per program)
or specify `code` and `scope`:

```json
{
  "programs": {
    "init": {"scope": "main", "code": "counter=5;megabuf(3)=.4;"},
    "frame": {"scope": "main", "code": "counter+=1;q1=megabuf(3)+counter;"}
  },
  "steps": [{"program": "init"}, {"program": "frame", "capture": ["q1"]}]
}
```

The captured `q1` is 6.4. Variable inputs/resets can also reference another
compiled program's live variable using `{"program":"frame","variable":"q1"}`.
This permits native frame outputs and saved initialization defaults to transfer
between contexts without a separate approximate evaluator. Repeated resets
resolve these references each iteration. Component scope and variable resets must follow the
native contexts and execution order; sharing a scope does not automatically
reproduce frame loading or transfers between different per-point contexts.

Custom-wave execution requests retain one output group per `wave_points` step,
with dynamic `sample_count` and captured `points`. Their frame program chooses
the sample count at runtime. Point inputs reset position/RGBA at each point;
Q/T, custom locals, registers and memory keep native ordering and lifetimes.
Sample separation shifts the inputs but is not subtracted from the final count.
Native dots with only one requested sample still skip drawing; invalid array
indices and smoothing domains remain unresolved rather than reading arbitrary
memory. A source-only check of the earlier four-wave preset executes38,400point
equations across20frames and produces959smoothed vertices per wave without images.

## Verification

Build `milk-native-reader` using `CMakeLists.txt` against the pinned, existing
projectM build. Tests default to `build/milk-analyzer/native/milk-native-reader`;
set `MILK_NATIVE_READER` to use another reader build.

From the repository root, with NumPy and pytest installed:

```sh
python -m pytest tools/milk-analyzer -q
```

The fixtures test native parsing/execution and source arithmetic. They never load
rendered reference images or generate a visual comparison score.
