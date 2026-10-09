# Test and predict presets

A preset can fail quietly in many ways: a shader falls back to a default, an equation block is left out, a texture is missing, or the picture is black until the music gets loud. This page covers the tools for catching those failures, from a quick static check to predicting what a preset will draw before rendering a frame.

## 1. Try it on a TV

The fastest real test is your TV:

1. Zip the preset and its textures and upload them as a [custom preset pack](../custom-packs.md). **Custom** is selected automatically.
2. Play music in a verified player and watch the preset: cold, then again after a minute of music. Feedback presets can take several seconds to build up.
3. Press **Center** to see the preset's name, and open **Advanced** to check the render size and Native trails state in Diagnostics.

### Watch the log on a TV

With developer options and ADB enabled on the TV:

```sh
adb logcat -s projectM-Native
```

| Line | Tells you |
|---|---|
| `LOAD preset='…' ms=… … weight_mb=… … programs_compiled=…` | The preset loaded, how long it took, how many shader programs were compiled, its texture memory |
| `Preset code left out (<preset>): <reason> (line N, column M)` | An equation block failed to compile and was dropped, as MilkDrop would. The rest still runs |
| `Preset load failed (<preset>): <reason>` | The file could not be parsed; the preset is skipped |
| `SKIP preset='…' reason=…` | The preset was added to this TV's skip list (unreadable, failed to load, too slow, or black twice) |
| `OUTPUT …` | Brightness range and how much of the picture changed while the preset played |

A shader that fails to translate or compile does not stop the preset: its stage silently uses projectM's default shader. If a preset looks plain or "wrong", suspect its shader first and check it against the [translation table](shaders.md#what-translates-and-what-does-not).

A preset that is skipped as *black* or *too slow* is recorded on the TV's skip list; reset it under **Advanced › Skipped presets**.

## 2. Static checks

`tools/check-presets.py` runs in CI on the bundled presets in `core/src/main/assets/presets` (it takes no path argument; to check your own presets, copy them into that folder in a checkout, and never pass `--remove` there casually, because it deletes failing presets). It reports presets that:

- **cannot react to music**: no `bass`, `mid`, `treb`, `vol` or `*_att` in any per-frame, per-pixel, wave, shape or shader code, *and* the main waveform is hidden (`fWaveAlpha` ≤ 0.01 or `wave_a = 0` in code), *and* no custom wave is enabled;
- use an **excluded texture** (images with text, logos or people);
- use a **texture that is not bundled**. A texture counts only if its sampler is declared *and* used, directly or through `#define`.

`tools/gen-preset-index.py` estimates each preset's extra memory: every referenced image at its decoded size, random slots at the largest bundled image, and a 32 MB allowance for very large shaders (over 4.2 KB or with two or more loops).

## 3. Preset Lab: render and measure

[Preset Lab](https://github.com/johnneerdael/ProjectM-TV/tree/main/tools/preset-lab) renders presets offline with a private copy of the patched engine, a synthetic clock and fixed seeds.

- `preset-lab trace <preset>` follows the preset's code statically: numbered-line rules, overwrites, conditions, persistent state and q/t transfers. It shows which outputs can depend on which audio inputs. Reachability is not response strength: a bass term can be overwritten, saturate or affect something invisible.
- `preset-lab bass-screen` renders an identical carrier signal twice, then adds bass bursts at three strengths, and measures the per-pixel difference against the control. A non-repeatable control makes the result *unknown*, not "not bass-reactive".

Desktop rendering timings do not predict TV performance.

## 4. Source analysis

The [milk-analyzer](https://github.com/johnneerdael/ProjectM-TV/tree/main/tools/milk-analyzer) tools read a preset with the engine's own parser and shader translator, without rendering:

- **Stage selection:** which warp and composite stages actually run, from the version keys. Many surprises are a shader that never runs because `MILKDROP_PRESET_VERSION` is missing, or a legacy stage requested by `PSVERSION_WARP=0`.
- **Q proofs:** conservative interval proofs of what values a q variable can take. For `martin - ludicrous speed.milk`, the analyzer proves that `q29` stays within 0…7 after initialization, frame resets and its bounded increment. It follows that a composite branch on `int(q29)%4` covers exactly four cases. A q variable that no code ever writes is proven to be exactly 0 in the shader.
- **Implicit globals:** uninitialized shader globals, which read 0 on GLES.
- **Shader lowering:** whether each shader section translates and compiles as GLSL ES 3.00.

Passing all of these means the preset will *run*; it does not certify how it will *look*.

## 5. Predicting a preset from its source

The **source forecaster**, being developed on the [predictor branch](https://github.com/johnneerdael/ProjectM-TV/tree/feat/predictor-visual-loop/tools/milk-analyzer), reads a `.milk` file and simulates its equations, geometry, shaders and feedback mathematically. Its prediction does not consume the reference engine's captured images. Captures are used afterwards to check the forecast. This remains research code, separate from the [measured moods shipped in the app](../predictive-collections.md).

### How are you measuring “97% accurate”?

**Here, behavioural accuracy means agreement with 20 frozen observable claims.** A score of **97.5/100**, or **97.5% of the available claim credit**, measures how closely one forecast matched those claims under the declared test conditions. It is an operational accuracy measure: it does not mean 97.5% of pixels matched or a future prediction has a calibrated 97.5% probability of being correct.

Keep three quantities separate:

| Quantity | What it answers |
|---|---|
| Per-preset agreement score | How closely did this prediction match its 20 claims? |
| Average agreement score | How closely did the predictions match on average, across the stated sample? |
| Gate pass rate | How many predictions met the chosen threshold and critical checks? |

**An 85% pass rate does not contradict 97% average accuracy.** For illustration, assume no critical failures and a sample with 85 scores of 100 and 15 scores of 80:

```text
average agreement = (85×100 + 15×80) / 100 = 97/100
pass rate at a ≥95 gate = 85/100 = 85%
pass rate at a ≥80 gate = 100/100 = 100%
```

Changing the gate changes the pass rate; it does not change the predictions, their grades or the 97/100 average. This illustration is not our recorded audit distribution. The actual audit results and their denominators are given below. Likewise, **85/88 ≈ 96.6%** in that audit is a conditional pass rate, not its average accuracy.

Neither a high agreement score nor a high pass rate establishes the percentage of MilkDrop programs fully understood, pixel identity, or a guarantee for an unseen preset.

### What is compared, and when?

Each comparison follows a recorded sequence:

1. **Declare the context.** Record the preset and texture hashes, predictor version, exact published ProjectM TV core AAR/library, audio, clock, random inputs, viewport, mesh and frame schedule. Source adapters are identified separately from the published AAR. Claims apply to that context.
2. **Predict before capturing.** The source simulator computes its numerical fields and writes 20 observable claims. The prediction, claims, input identities and timestamps are sealed with hashes before reference captures are examined. A batch's predictions are frozen before its captures; the model stays unchanged during the batch.
3. **Run the reference.** The unchanged published Android core is invoked through JNI with the matching declared inputs. Captured RGB frames, frame metadata and artifact identities are retained. The reference is a named ProjectM TV engine, not every GPU or the original Windows MilkDrop renderer.
4. **Compare numbers and behaviour.** Automated checks compare numerical descriptors and event lists. Recorded visual assessments compare layout, trajectories, palette and retained layers across paired sequences. The qualitative assessments are AI-assisted judgments, not a calibrated perceptual metric or a blinded human-panel study.
5. **Grade and preserve the result.** Save the per-claim evidence, arithmetic, unknowns, critical failures and seals. Later fixes receive separate retests; they do not overwrite the original score or count as fresh random successes.

The predictor reuses engine components for parsing, equation evaluation and numerical input preparation. Agreement therefore checks the forecast against that engine; it cannot independently rule out an error shared by both implementations. Investigating original MilkDrop intentions is a separate source/reference comparison.

### The 20-claim rubric

Each preset has four claims in each category. The actual statements are written for that preset before capture; this table describes their scope, not a fixed list of effect labels.

| Category | Examples of observable claims | Maximum points |
|---|---|---:|
| Structure | Where forms appear; symmetry; overlapping or repeated layers | 20 |
| Motion | Direction and trajectories; median and upper-tail motion speed | 20 |
| Colour | Palette relationships; mean brightness and saturation | 20 |
| Flashing | Brightening/darkening events, their timing and peak brightness step | 20 |
| Feedback | How retained imagery moves, persists and builds layers | 20 |

A supported claim earns **5 points**, a partial match **2.5**, and a mismatch or unknown **0**:

```text
score = sum of the 20 claim grades
maximum = 20 × 5 = 100
```

The numerical policy used in the cited audit and later example is:

```text
abs(observed − predicted) ≤ 0.05 × abs(predicted)
```

A predicted zero requires exact zero; the policy has no hidden absolute-error floor. This 5% allowance applies to numerical estimates. It does not shift flash events between frames, change event counts or excuse a critical geometry/trajectory contradiction. An unobservable motion estimate earns no credit; a black picture is not automatically proven motionless.

Some claims combine two numerical checks. For example, matching median speed but missing the upper-tail speed can earn 2.5 of that claim's 5 points. The historical ≥95 gate additionally requires no critical partial match, mismatch or unknown. A later gate requiring every score to be 100 would reject a 97.5, even though the older ≥95 gate might accept it. Always quote the gate as well as the score.

### A real 97.5/100 example

In the saved core **2.3.25** comparison, *“suksma - no god here, cosmic tear”* received **19 supported claims and one partial claim**:

```text
19 × 5 + 1 × 2.5 = 97.5
```

Its predicted 95th-percentile motion speed was **0.937682** normalized viewport units per second; the reference measurement was **0.996511**. Horizontal flow is normalized by image width and vertical flow by image height before its magnitude is calculated. The upper-tail descriptor is the 95th percentile of the per-transition pixel-speed 95th percentiles, rather than one pooled percentile of every pixel in every frame. The relative difference was **6.27%**, beyond the declared 5% allowance. Median speed passed, so the combined motion claim received partial credit. The original 97.5 remains recorded, and the round received no perfect-streak credit. See the [saved example and numerical failure](https://github.com/johnneerdael/ProjectM-TV/blob/b3737a564f4b937bd33959e17bb61dbe4eb11304/tools/milk-analyzer/fixtures/core2325-random3-round007-2026-10-08.json).

That is a reproducible explanation of the grade. It is not a claim that the whole picture was exactly 2.5% wrong.

### The historical 100-preset audit: keep the denominator

The audit selected presets from a seeded permutation of the complete **9,606-preset library**, without filtering for predictability. It retained all 100 selected entries, including failures. All **2,000 claims** were frozen before **6,000 reference frames**. The 20 claims for one preset are related observations, not 20 independent presets.

| Measure | Result | Meaning |
|---|---:|---|
| Predictions completed | 88/100 | Coverage in this sample and context |
| Presets passing the ≥95 gate | **85/100 = 85%** | Pass rate with unresolved predictions included |
| Pass rate among completed predictions | 85/88 ≈ 96.6% | Conditional rate; excludes the 12 unresolved cases |
| Mean score over all selected presets | **86.95/100** | Unresolved predictions retain zero credit |
| Mean score among completed predictions | 98.8068/100 | Conditional mean, not a pass rate |
| Perfect rubric scores | 71/100 | All 20 claims matched; not pixel identity |

The score distribution was 71 at 100, eight at 97.5, six at 95, two at 90, one at 65 and 12 at zero. The arithmetic is inspectable:

```text
(71×100 + 8×97.5 + 6×95 + 2×90 + 1×65 + 12×0) / 100 = 86.95
8695 / 88 = 98.8068  (completed predictions only)
```

This was a **core 2.3.11** checkpoint, before the projectM 4.2 rebase: **60 frames at 30fps, 256×144, 48×32 mesh**, one declared audio/random context and an API34 ARM64 emulator using Apple M4 Pro GLES. It did not meet the requirement that every one of the 100 presets score ≥95. The 12 source-domain gaps are historical outcomes, not a statement of today's remaining backlog. See the [frozen audit summary](https://github.com/johnneerdael/ProjectM-TV/blob/b3737a564f4b937bd33959e17bb61dbe4eb11304/tools/milk-analyzer/fixtures/visual-loop-round010-2026-10-06.json) and [full report, selection and provenance limits](https://github.com/johnneerdael/ProjectM-TV/blob/b3737a564f4b937bd33959e17bb61dbe4eb11304/docs/plans/2026-10-06-predictor-random100-audit.md).

### What the score does not establish

Broad claims can agree while fine detail differs. The audit report explicitly retains a case with mean absolute RGB8 error **48.88 on the 0–255 channel scale** despite agreement on larger forms and aggregate claims. Pixel errors are separate diagnostics; they are not converted into “100 minus error = accuracy.” This is why a 100/100 rubric score is narrower than a pixel-perfect match.

The score also does not validate aesthetic quality, a music genre, a viewer's preference, no flashing for all future audio, longer timelines, 4K detail or another driver. Successful parsing/loading alone gives no appearance credit, and the unchanged JNI does not directly expose every stage's custom-versus-fallback shader identity. Those are separate qualification questions.

The research branch’s **47-field export** is another separate result: it stores features and provenance for downstream scoring, with explicit unknown values. Completing a source-only corpus simulation—even thousands of presets at 60 frames/15fps/480p—does not add new reference comparisons or establish a new visual-accuracy percentage.

A useful result statement reports both closeness and acceptance: **“Mean behavioural agreement was 86.95/100 across all 100 selected presets, or 98.8068/100 among the 88 completed forecasts; 85/100 passed the ≥95 gate in the declared core 2.3.11 context.”** For a current accuracy claim, publish a new frozen comparison against the current engine, along with coverage, score distribution, critical misses and the same context details.

### What source analysis cannot settle

The audit’s twelve unresolved predictions illustrate why a source forecast sometimes has to abstain:

- **Undefined GPU arithmetic:** `pow` of a negative base or of zero to a non-positive power, division by zero, and coordinates that become infinite or NaN. GLSL leaves the result to the driver (`TonyMilkdrop - RGB.milk`, `141 nz.milk`, `$$$ Royal - Mashup (452).milk`).
- **Random choices:** the selected `randNN` images and noise realization must be supplied as declared inputs. Shader text alone does not identify an arbitrary production load's choices.
- **Future audio:** a preset that reacts to a breakdown cannot be predicted without the music.
- **Chaotic feedback:** some presets amplify tiny differences until two runs diverge.

A cautionary example: `325.milk` was predicted numerically correctly, but the written *explanation* was wrong. The q32 variable is never written, so it is 0, which removes the main feedback term, and the result clamps to black. Check the proof of which q variables are untouched before explaining an effect.

## Aurora: a preset designed to be predicted

The *Aurora Ownership* SOL and LUNA presets were written for this project to test one engine feature, and designed so that their behaviour could be forecast before rendering. They make a good template for modern presets.

```ini
MILKDROP_PRESET_VERSION=201
PSVERSION_WARP=2
PSVERSION_COMP=2
[preset00]
fDecay=.90
fGammaAdj=1
fWaveAlpha=0
warp=0
per_frame_init_1=env=0;kick=0;q8=1.0;q9=0.4;q10=0.055;q11=0.3;
per_frame_1=kick=max(.78*kick,min(1.5,max(0,(bass-.95)*1.6)));
per_frame_2=env=.92*env+.08*min(2,max(0,bass_att));
per_frame_3=q1=kick;q2=env;q3=min(1.5,max(0,mid));q4=min(1.5,max(0,treb));
per_frame_4=q5=min(1,max(0,bass-bass_att+.08)*2.4);q6=time*.65;
per_frame_5=zoom=1;rot=0;warp=0;dx=0;dy=0;decay=.90;
```

What makes it predictable:

- **Bounded envelopes.** Every audio input passes through `min`/`max`, so `kick` stays within 0…1.5 and `env` within 0…2 whatever the music does.
- **Palette in init.** `q8`–`q10` are set once in `per_frame_init`, so they are the same every frame (q resets to its post-init value).
- **Explicit motion.** `per_frame_5` sets every motion variable each frame, including `warp=0`, so nothing depends on defaults.
- **A forecastable core.** Shape 0's per-frame code is `rad=.74+.12*q1`, so the core's radius ranges from 0.74 to 0.92: a 24.3% larger diameter and 54.6% larger area at full kick. On the test audio, the computed `kick` spans 0.152871 to 1.5. The render matched the forecast with a worst relative error of **0.076%**, including exact timing of flash events.

The rest of the preset uses most block types (it has no per-pixel or wave/shape init code):

- shape 0 shows a named image, a projectM extension;
- shapes 1–2 are additive halo rings with thick outlines;
- shape 3 has 12 instances orbiting by `instance`;
- wave 0 is a 256-point dotted ring with per-point colour;
- wave 1 is a spectrum ring;
- the warp shader rotates and zooms the feedback, and clears a box under the core so stale history cannot hide a wrong texture;
- the composite adds rays, blur glow, mist and a vignette.

[Full source](https://github.com/johnneerdael/ProjectM-TV/tree/feat/predictor-visual-loop/tools/milk-analyzer/witnesses/patch-0010-aurora).
