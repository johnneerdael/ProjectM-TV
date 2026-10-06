# Read behaviour from source, without inspecting images

The predictor's primary classification path is a mathematical program analysis,
not an image classifier. Source-field simulation remains a separately named optional
mode. A missing feature means its extraction/proof has not been implemented; it
does not authorize a hidden rendered-frame fallback or a zero score.

## How to obtain the remaining data

| Required data | Source calculation | What must remain explicit |
|---|---|---|
| Motion | Execute equations in native phase order; track shape/wave vertices; derive warp transport from the inverse texture-query map; compute velocity, acceleration and jerk | Visibility/salience, topology changes, texture transport, native projection and sampling domain |
| Pulses/flashing | Follow reachable final colour expressions and discontinuous branches; calculate temporal differences and supported affected regions; combine injection, warp, filters and composite | Small/colour-only pulses, moving-edge crossings, event timing, audio/RNG/state domain and incomplete area coverage |
| Bass reactivity | Trace actual band dependencies; execute matched counterfactual inputs with all other inputs/state/RNG held fixed; calculate geometry/colour/region changes | Dose/latency, volume derived from bands, waveform/spectrum consistency and nonlinear response |
| Palette | Evaluate supported final colour functions at isolated declared points or bound them analytically; calculate chromatic support, hue entropy, warm/cool and circular hue changes | Sparse queries are not screen-area proofs; grey has no hue; arbitrary feedback/material inputs cannot be invented |
| Feedback | Represent the recurrence and prior state; prove restricted linear gains, injection bounds and transport; extend to supported nonlinear operators incrementally | Decay alone does not prove persistence or calmness; unknown recurrence paths stay unknown |
| Structure/style | Analyze reachable geometry, coordinate transforms and procedural functions; calculate symmetry, curvature, repetition and supported multiscale motifs | An instruction count or function name is not an appearance tag; textures/composition can break symmetry |

For `C(t)=a+b*sin(omega*t)`, elementary derivative bounds supply maximum colour
change directly from source. For a moving primitive `p(t)`, its derivatives describe
geometry; visible motion additionally requires evidence that the primitive affects
the output. For a feedback query `W(p)`, even a time-independent nonidentity W moves
old content at every update. Estimating `dW/dt` alone would incorrectly call it still.

The restricted recurrence `F_next=d*F_previous∘W+J` has amplitude half-life
`ln(.5)/(fps*ln(d))` for a justified scalar linear gain0<d<1. Nonlinear shaders,
clipping, injection, blur and composition can invalidate that interpretation.
Require the recurrence proof instead of assigning this number from `fDecay` alone.

Numerical isolated queries can validate supported equations without assembling an
RGBA image. Arbitrary image-feedback programs need an explicit state representation
or conservative bounds; source text alone does not identify missing initial images,
random selections, future audio, driver-undefined arithmetic or subjective liking.
No general claim that every possible program can be classified exactly is made.

## Reference hierarchy and authored intent

1. Use the creator's documentation and original MilkDrop source for authored
   conventions and intent. Code comments can express intent while implementation
   contains a bug; record both instead of calling every observed defect deliberate.
2. Use the beta projectM authoring guide as a navigable mathematical reference,
   cross-checking precise implementation claims.
3. Use the exact published ProjectM-TV source/policy and unchanged AAR for the
   target engine. Compatibility fixes need their own versioned semantics; they do
   not retroactively become original MilkDrop behaviour.

The supplied local references are pinned in
`fixtures/authoring-guide-math-references-2026-10-07.json`:

- [projectM beta authoring guide source](https://github.com/projectM-visualizer/projectm-visualizer.org/tree/a7036b8f90046513dd2dc0be09a99879f0556cd9/content/1.docs/3.preset-authoring)
  at commit `a7036b8f`; local checkout is `~/Scripts/projectm-visualizer.org`.
- [Original MilkDrop2 source](https://github.com/projectM-visualizer/milkdrop2/tree/f05b0d811a87a17c4624170c26c93bac39b05bde/src)
  at commit `f05b0d81`; local checkout is `~/Scripts/milkdrop2`.
- The original `src/vis_milk2/milkdropfs.cpp` SHA-256 is
  `68749d31bb6b3020ca89b1e7630fd704e58a5de8dd6275c9f5ea005c6586a7d9`,
  matching the user's separately supplied original2.25c source file byte-for-byte.

These are source references, not proof of old D3D device-register history, Windows
compiler precision or current GPU behaviour.

## Verified mathematical details worth retaining

| Topic | Reference evidence | Predictor implication |
|---|---|---|
| Phase ordering | Beta rendering-process guide; original frame/loading paths | Main init, waves, shapes, then per-frame/pixel/draw/composite have distinct scopes and resets |
| Feedback versus display | Guide stores feedback before post-processing; original final rendering code | Display gamma/echo/filters must not contaminate the next feedback state |
| Brighten | Original `milkdropfs.cpp:4282` performs invert, square, invert | Component transform is `1−(1−c)²=2c−c²`, not the literal mathematical square root |
| Darken / solarize / invert | Original blend operations; current controlled filter model | `c²`, `2c(1−c)`, `1−c`, with storage/quantization between actual passes |
| Live legacy controls | Original `milkdropfs.cpp:4147` reads evaluated echo/gamma; filter reads at4282+ | Original expression controls exist; old projectM static reads are an engine mismatch repaired in TV2.3.15 |
| Gamma with echo | Original code at4218+ adds redraws controlled by gamma inside the echo branch | The gamma-only drawing branch is skipped, but gamma still affects echo output |
| EEL square root | Original `asm-nseel-x86-msvc.c:468` applies `fabs` then `fsqrt` | EEL `sqrt` uses absolute input; shader sqrt retains its separate language/domain semantics |
| Blur adjustment | Original `GetSafeBlurMinMax` at1551 says to push bounds apart but subtracts at both endpoints | Preserve the historical defect separately; TV0046 implements coherent corrected intervals and explicit defaults |
| Warp transport | Guide's texture-coordinate transformations; original nested CPU pow path | Read transform order, signs, projection and feedback recurrence; do not infer motion solely from lexical `time` |

The source forecaster's current target remains published TV2.3.15. The unreleased
4.2 rebase needs a separately identified semantic profile even when its intended
renderer result is unchanged.

## Guide contribution candidates

Verified clarifications are tracked separately from unproven visual inferences.
The focused contribution is open as [projectM website PR3](https://github.com/projectM-visualizer/projectm-visualizer.org/pull/3)
against the author's beta guide branch, with a successful website build and
independent source review:

- Correct the decay section's composite-version selector to the warp-version
  selector, consistent with its own warp description and current stage policy.
- Replace the literal square-root claim for Brighten with its actual three-pass
  polynomial, distinguishing the historical comment from the operation.
- Explain that original MilkDrop legacy gamma/echo/filter variables are expression
  controls; label projectM implementation-version differences rather than presenting
  static-only behaviour as universal.
- Explain gamma's additive redraw role in the echo branch.
- Add EEL's absolute-input square-root convention without generalizing it to HLSL.

Do not overwrite the existing guide checkout or its unrelated changes. Use a focused
worktree/contribution, cite source lines and controls, and keep TV-only policies
separate from original/upstream contracts. Broader claims about blur history,
texture modes or all-platform precision need their own matching evidence.
