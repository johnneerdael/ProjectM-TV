# Read-only report: retained policies and conversion boundaries

Investigated **I07, I15, I21, I25, I26, I27, I28, I30 and I31** against the patched worktree. No files were edited, no builds/tests were run, and no devices or GL contexts were touched.

The alternate MilkDrop2 files under `/Users/jneerdael/Scripts/milkdrop2/src/vis_milk2/` are byte-identical to the original 2.25c reference for `milkdropfs.cpp`, `plugin.cpp` and `md_defines.h`. MilkDrop3 was not inspected; its mention below comes from the existing patch header.

Static corpus investigation covered **9,606 `.milk` files**. The counts below identify source conditions, not rendered-impact frequencies.

| ID | Recommended disposition |
|---|---|
| I07 | Retain both-channel analysis; explicitly document mono TV immunity |
| I15 | Retain visibility minimum pending demonstrated regression |
| I21 | Retain projectM’s 16-mode extension |
| I25 | Retain documented float-color precision policy; qualify its compatibility cost |
| I26 | Retain all-band volume; do not restore the original comma-expression defect |
| I27 | Retain height-derived mip value |
| I28 | Retain existing blur safety correction |
| I30 | Document/defer byte-exact diffuse compatibility; investigate separately from framebuffer precision |
| I31 | Safe narrow repair: change **gamma-only** epsilon to `.001f`; preserve echo epsilon |

## I07 — Stereo band averaging

**Confirmed source difference.** [PCM.cpp:65](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/Audio/PCM.cpp:65) averages the two channel spectra before all three loudness calculations. Original [plugin.cpp:9516](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/plugin.cpp:9516) performs its band analysis from the left waveform only.

The upstream commit `494269ef50479afeda1278dd0adc1002e5acfab3`, **“Audio: use both channels for beat detection (was left-only)”**, expressly fixes right-weighted content under-reacting. This is already present in upstream pin `6f6480746`, rather than introduced by a TV patch.

The handoff witness is consistent: current band sum `(1+3)/2=2`; at frame ≥50, prior long average 1 and steady 30 Hz, updated long average is approximately `1.008`, giving `2/1.008≈1.984127`. Original left-only analysis gives 1.

**Native4K relevance:** TV [FeedAudio:1870](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/core/src/main/cpp/native-lib.cpp:1870) submits `PROJECTM_MONO`; [PCM.cpp:33](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/Audio/PCM.cpp:33) duplicates mono into both channels. Thus this particular difference is inactive for the current TV capture path, regardless of output resolution.

**Unchanged original witness:** `Sjadoh - Fortune Teller.milk`, SHA256 `60d9ae2f5adb14e3cd6beb99da7643e33ba103178aae84d152305cfc67e2b088`, line42: `zoom=zoom +0.313*(0.60*sin(bass)+0.40*sin(bass));`. It is a simple stereo-host geometry witness. A mono Native4K screenshot should demonstrate preservation, not a fabricated stereo difference.

**Regression/diagnostic:** immutable spectrum sums and prior averages; channel swap, right-only signal, equal-channel mono and full stereo PCM through the unchanged analysis pipeline. Do not use mutable EEL `vol` as the oracle. Reverting would reintroduce right-channel under-reaction and affect stereo AAR consumers.

## I15 — Motion-vector minimum

**Confirmed source difference.** [MotionVectors.cpp:62](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/MotionVectors.cpp:62) explicitly increases the minimum to prevent smoothed lines disappearing:

```text
hypot(1.25/width, 1.25/height)
```

Original [milkdropfs.cpp:1299](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:1299) uses `1/width`. The basic visibility adjustment predates TV patches; consolidated0001 adds diffusion-aware scaling through [FeedbackDiffusion.cpp:119](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/FeedbackDiffusion.cpp:119).

| Dimensions | Current threshold | Original threshold |
|---|---:|---:|
| 256×144 | .0099596139 | .00390625 |
| 1280×720 | .0019919227 | .0007812500 |
| 3840×2160 | .0006639743 | .0002604167 |

**Important qualification:** these are thresholds. For exactly zero displacement, both implementations assign **each component** `(min,min)`, so normalized segment length is `sqrt(2)*min`. The handoff must not describe the threshold as that zero-displacement segment length.

**Actual static trigger:** a narrower corpus scan found **98** presets with positive motion alpha/counts, `mv_l=0`, and no main equation assignment to motion alpha/length/counts. This forces the minimum branch wherever a valid UV map is available.

**Strong unchanged witness:** `Rovastar - Parallelogram Bin 2.milk`, SHA256 `f9d50349cd553c96ebfb395bcbd715246c63333a218057a6cf4ce746a252d86e`, lines55–63: 64×48 vectors, `mv_l=0`, `mv_a=1`; line72 hides the built-in wave. Its nonfinite axis equations require care, but the vector grid samples interior positions.

**Native4K relevance:** motion vectors draw in native feedback and again in authored feedback when detail is active; the authored draw explicitly uses canvas dimensions and disables line references/diffusion, [MilkdropPreset.cpp:262](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/MilkdropPreset.cpp:262). Both passes require qualification. At zero displacement the unscaled current minimum produces component offsets about **2.55 horizontal pixels /1.43 vertical pixels**, versus original **1/.5625** at16:9.

**Recommendation:** retain; document the visibility/aspect tradeoff. Compare actual unchanged-preset Native4K captures, plus a finite zero/small-displacement map at256×144 and a second aspect ratio. Test long segments, alpha0 and diffusion fallback separately. Shrinking the minimum can remove vectors and change accumulated feedback; lower vertex count is not involved.

## I21 — Extended waveform modes

[Waveform.cpp:99](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/Waveform.cpp:99) preserves truncated signed remainder modulo16 and live factory rebuilding. [WaveformMode.hpp:6](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/WaveformMode.hpp:6) names the extra spectrum/Milkdrop2077 modes. Original [milkdropfs.cpp:2852](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:2852) uses `NUM_WAVES=8`.

Thus mode8 is current SpectrumLine versus original Circle; mode9 is current extended Wave9 versus original Spiral. Current0007 and `UPSTREAM_PATCH_VALUE.md` expressly retain the16-mode extension.

**Corpus refinement:** four static mode8 candidates exist, but both Rovastar Parallelogram files assign `wave_a=0`. The remaining two have alpha4.1 and no `wave_a`/`wave_mode` equation assignment:

- `suksma - i'll go ahead and get the salad bar nz+.milk`, SHA256 `d300f7f3b57f6c32d29e44cbfef313efe8cb504006dafe3102b0b8ea618805f2`.
- `3D function draw template [flexi's learning by doing session 05] nz+ nglumbrephonle hsdv el norte.milk`, SHA256 `b44d1513c9230630b8006fd8498c665925be457b89dcdae04c4238fb98626fc3`.

Use the first as the unchanged Native4K screenshot witness, confirming factory8 before attributing appearance.

**Recommendation:** retain extension; do not globally reduce modulo. A repair would remove supported waveform shapes and interfere with existing live-control work. Factory controls should cover0–15,16/17, negative values and changing modes without re-evaluating prepared geometry. A finite mode8 diagnostic should show spectrum versus circle at matched dimensions. No new framebuffer or memory allocation is implied by retention.

## I25 — Shape/custom-wave color fractions

The difference is explicit intentional upstream policy: [Color.hpp:109](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/Renderer/Color.hpp:109) explains its omission of8-bit truncation “to avoid limiting ourselves to8 bits.” Current shapes and waves consume this policy at [CustomShape.cpp:209](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/CustomShape.cpp:209) and [CustomWaveform.cpp:212](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/CustomWaveform.cpp:212). Consolidated0001 preserves it through geometry replay.

Original [milkdropfs.cpp:2388](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:2388) and [2699](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:2699) multiply evaluated **double** colors by255, truncate and mask. Therefore `.5→127/255`, `.123456→31/255`.

**This is producer attribute conversion before interpolation/blending. RGBA8 output cannot substitute for that conversion.** Native dot alpha scaling adds another later boundary that should remain unchanged.

**Actual static witnesses:** narrow scans found469 enabled, positive-radius, fractional-color shapes without shape equations and37 enabled fractional-color custom waves without wave equations.

Strong combined witness: `EVET - Transfiguered Bliss 1.milk`, SHA256 `3980cc69745e54aa8d14f5acd92f8aefc2882259514b4aed8b8eaebf4da53f17`:

- wave0 enabled,512 samples, opaque; line73 red `.3`;
- shape0 enabled,100 sides, radius `.054279`; line127 red `.270001`, line132 outer green `.050001`;
- neither producer has equations overriding these values.

**Recommendation:** document/retain precision policy unless actual focused captures justify a compatibility change. A global `Color::Modulo` replacement is unsafe: it changes unrelated consumers, negative/fractional wrapping and narrowing order. A future byte-compatible path must act at the original producer boundary, preserve alpha-multiplication order and double inputs, define only supported finite/int-representable domains, and replay prepared colors identically in authored/native passes.

Regression: direct attribute readback for `.5`, `.123456`,0/1/exact fractions; independently shape center/edge, outline and wave colors; blended gradient with known feedback. Screenshots may show small changes that feedback amplifies; no measured improvement or universal visual superiority is established.

## I26 — Shader `vol`/`vol_att`

Original [milkdropfs.cpp:3970](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:3970) contains a comma expression. Its value is the **treble operand alone**, multiplied by`.3333`. Current [PCM.cpp:100](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/Audio/PCM.cpp:100) computes the all-band mean using`.333`, bound from immutable audio data by [MilkdropShader.cpp:225](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/MilkdropShader.cpp:225).

- `(1,2,3)`: original `.9998999834`; current `1.9980000257`.
- **Equal bands are not unaffected:** `(1,1,1)` gives original `.3332999945`; current `.9990000129`. Correct the handoff’s proposed equal-band unaffected control.

A comment-stripped scan with active shader versions found **96** presets containing `vol`/`vol_att`; no local `float vol` shadow declarations appeared in that scan. Shader execution/optimization is still unqualified.

**Strong unchanged witness:** `Cope - The Neverending Explosion of Red Liquid Fire.milk`, SHA256 `ec4a844e75a8c8a8d4a41890495841b670960186988f29797799929a3b5d34d8`, warp line280: `noise2 += noise3*vol;`, followed by a live noise/color contribution. Noise identity and RNG must be frozen.

**Recommendation:** retain all-band mean; explicitly document source incompatibility with the original defect. Do not change mutable EEL variables or volume modulation to emulate this shader-only defect. A finite composite `float3(vol/4,vol_att/4,0)` with injected immutable bands is the decisive diagnostic; use bass-only/mid-only/treble-only,zero and equal bands. Native4K changes geometry/canvas handling, not this scalar contract. Retention adds no rendering cost; reversal broadly changes audio responsiveness.

## I27 — `mip_y`

Original [milkdropfs.cpp:3950](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:3950) repeats width for both axes. Current [MilkdropShader.cpp:190](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/MilkdropShader.cpp:190) derives each from its corresponding shader canvas dimension.0001 additionally preserves the reference-sized shader canvas above the reference area.

At256×144, original tuple is `(8,8,8)` versus current approximately `(8,7.169925,7.584963)`. With an actual1280×720 authored canvas, current is approximately `(10.321928,9.491853,9.906891)`.

**Corpus:** the complete scan found **no `mip_x`, `mip_y` or `mip_avg` tokens**, including the average dependency absent from the handoff’s narrow trigger.

**Recommendation:** retain height-derived value. No suitable unchanged corpus screenshot witness exists. Use a finite composite exposing all three uniforms at square and nonsquare sizes, then capture that diagnostic at Native4K while recording actual shader canvas dimensions. Repeating width would reintroduce a dimension-reporting defect; physical3840×2160 is not automatically the shader canvas. No performance benefit from reversal is supported.

## I28 — Near-equal blur ranges

Original [milkdropfs.cpp:1551](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:1551) says to push close bounds apart but sets both sides to `avg-.05`. At`.5/.5`, both become approximately`.4499999881`; subsequent reciprocal normalization has a zero denominator.

Current [BlurTexture.cpp:354](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/BlurTexture.cpp:354) expands to approximately `[.4499999881,.5500000119]` and uses coherent `[0,1]` defaults for unsupported normalization. [0005 header](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/tools/projectm-patches/0005-blur-range-interval.patch:1) explicitly identifies this as safety correction, not a backport of an already-fixed reference.

**Corpus refinement:** seven of eight supplied candidates actively sample a blur level carrying/inheriting a collapsed range. `EVET - Scanazoic --- Isosceles edit.milk` collapses level3 but only samples levels1/2, making it a poor visible witness for this finding.

**Strong unchanged witness:** `Cope - The Cloud.milk`, SHA256 `9c93b7182617fc543a329b094067136fde5e67a6ccf78047d350dc7c7f90ad9c`, lines68/71: `b1n=b1x=1`; warp line283 actively consumes `GetBlur2`. No blur equation override was found.

**Recommendation:** retain0005. Current Native4K blur/reference source policy and caller framebuffer ownership must also remain intact. Capture unchanged current policy versus independently identified finite diagnostic expectations; do not label original zero-interval/NaN output “expected appearance.” Regression should exercise clamp-then-expand order, progressive float32 coefficients, ordinary nested ranges, near-equal ranges and coherent unsupported triplet defaults in storage **and** decoding. Reversal risks invalid shader arithmetic and feedback corruption; retention requires no additional blur passes.

## I30 — Display diffuse byte packing

Original macro [milkdropfs.cpp:41](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:41) truncates `channel*255`. It is applied separately to echo/gamma diffuse at4204/4228/4256 and shader-composite diffuse at4472. Current [VideoEcho.cpp:212](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/VideoEcho.cpp:212) and [FinalComposite.cpp:359](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/FinalComposite.cpp:359) retain float attributes.

For white legacy tint and gamma`.75`, original producer coefficient is`191/255=.749019608`; current is`.75`. This remains separate from render-target precision.

**Corpus refinement:** the handoff’s155 legacy lexical candidates include custom-composite paths. A simpler source filter finds370 legacy/no-echo presets with fractional gamma or live tint and no main gamma/echo override; this remains a static subset. Separately, **1,171** presets have comment-stripped `hue_shader` reads in active composite versions, versus1,202 raw lexical matches.

**Unchanged screenshot witnesses:**

- Legacy: `heavenly eye.milk`, SHA256 `130d1562929f29dac51ae2eaba661f1f07310708efce2ada71890aab0862d90a`, gamma1.5,echo0,tint0, no gamma override. Its fractional gamma pass uses`.5` versus`127/255`.
- Custom composite: `PyroCybin - Computronium [stahlregens gelatine finish].milk`, SHA256 `71450433120e7c01fc82f269226341b462ba1834d83c09c1287d7935eb1d6bf5`, composite line156 `ret *= hue_shader;`. Its mixed-case shader version is also involved in I01; isolate that finding.

**Recommendation:** explicitly document/defer byte-exact diffuse compatibility while keeping the current precision policy and0014 tint correction. If implementing, use a narrowly scoped producer conversion after each original mix/gamma/hue interpolation step. Quantizing the four corner shades before mesh interpolation is **not** equivalent to original per-composite-vertex packing. Do not globally lower shader/FBO precision or change gamma pass count as part of this finding.

Regression: independent legacy echo, gamma-only and custom-hue attributes, finite byte-fraction controls and known unsaturated texture. Risks include systematic downward bias, transition alpha changes and feedback amplification. No measured precision benefit or Native4K speed difference was established here.

## I31 — Gamma-only pass epsilon

The original no-echo path uses `.001f`, [milkdropfs.cpp:4245](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:4245); current [VideoEcho.cpp:212](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/VideoEcho.cpp:212) uses`.0001f`. Original **echo redraws** genuinely use`.0001f`; preserve that branch.

**Safe repair:** change only `DrawGammaAdjustment`’s `gammaAdj-.0001f` to `gammaAdj-.001f`. Preserve live frame gamma,0014 shade calculation, blending, viewport and byte-packing policy.

The handoff’s gamma1.0005 source witness holds: actual float32 `1.000499963760376` produces original1 versus current2 passes.

**Actual corpus trigger:** one static gamma-only source was found using loaded float32 values:

` s u k s m a ` spelling without spaces: **`suksma - type o negative - world coming down.milk`**, SHA256 `1eae0591633d591883bf3dc5340bed937d4ba80ef566ffb8ce668cef3bf919ed`.

It has explicit `PSVERSION_COMP=0`,echo0,tint0,gamma2.001 and no main gamma/echo assignments. Loaded gamma is`2.000999927520752`; float32 subtraction by`.001` gives`1.9999998807907104`, so original2 versus current3 passes.

**Visual qualification:** ideal total float weights agree: current`1+1+.0009999275`; repaired`1+1.0009999275`. RGBA8 storage can erase the small difference, especially with this white shade. **Accept identical actual before/expected screenshots.** Pass count and uploaded weights are the causal oracle; do not invent a brightness improvement.

**Native4K value:** a repair can remove one full-screen pass in the boundary interval, but no timing saving was measured here. Regression should check loaded float32 values around1,1.00005,1.0005,1.0011,2 and2.001; verify echo branch unchanged and custom composites unaffected. Freeze the original preset’s finite/runtime context and capture actual Native4K frames; its more complicated custom waves are not the pass-count oracle.

The shipping0016 opacity and0017 custom-window changes were treated as retained context. No conclusion here admits the separate I19 count hypothesis into the shipping series.
