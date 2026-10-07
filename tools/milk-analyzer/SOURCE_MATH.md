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

Justin Frankel's WDL EEL2 backends are additionally pinned at
`d30c30b356b2b7fb1654def8dbda90066f43061a` in the same fixture. The supplied
[x64 SSE assembly](https://github.com/justinfrankel/WDL/blob/d30c30b356b2b7fb1654def8dbda90066f43061a/WDL/eel2/asm-nseel-x64-sse.asm#L452-L460)
implements bitwise OR with double-to-signed64 truncation (`cvttsd2si`), OR and
conversion back to double. The corresponding
[AArch64 inline assembly](https://github.com/justinfrankel/WDL/blob/d30c30b356b2b7fb1654def8dbda90066f43061a/WDL/eel2/asm-nseel-aarch64-gcc.c#L390-L399)
uses `fcvtzs`, `orr` and `scvtf`. These are EEL backend operations, not shader
intrinsics. Finite, in-range integer conversion and backend edge cases must be
distinguished; do not infer identical overflow/NaN conversion from equivalent
ordinary inputs.

The published TV target executes its patched projectm-eval implementation,
not these assembly files. Its `TreeFunctions.c` chooses the signed integer width
from `PRJM_F_SIZE` (32 bits for4,64 bits otherwise); the current prepared source49
adapter is built with8. It already executes bitwise OR through that evaluator.
The same separation matters for `invsqrt`: these WDL backends seed the historical
float32 bit approximation while the double projectm-eval implementation uses a
double-width seed. Preserve the target's numerical semantics and reference the
original backend separately. Neither instruction inspection nor CPU execution
alone certifies published-AAR parity for exceptional inputs.

## Exceptional shader arithmetic: precision and consumers matter

The [GLSL ES3.00 specification](https://registry.khronos.org/OpenGL/specs/es/3.0/GLSL_ES_Specification_3.00.pdf)
section4.5.1 specifies IEEE32 storage for `highp` floats and generation of infinities
for applicable highp operations. Nonzero division by zero has an infinity rule,
with a signed-zero qualification. Subnormals may be flushed; NaN generation and
propagation are not universally required. Section8.2 leaves `pow(x,y)` undefined
for negative x, and for zero x with nonpositive y. Do not replace those domains
with NumPy's convenient result or a generic zero/epsilon.

Current source49 `GLSLGenerator.cpp:248–252` emits a `highp float` default for
translated GLES300 custom shaders. The handwritten warp vertex shader starts
with `mediump float`. A rule justified for the former must not silently be applied
to the latter, desktop GL, integer conversions or nonfinite texture coordinates.
The native translator's literal-exponent1 optimization is already modeled;
other exponents still use `pow(abs(base),exponent)` and retain its zero-base limits.

The opt-in `gles300-highp-infinity-v1` scalar/grid policy now carries infinities
through supported basic arithmetic/storage and finite or declared normalized-RGB
consumers. The strict default is unchanged. Source entry points require GLES300;
the handwritten mediump warp and Apple NaN addressing policy remain separate.
Incoming nonfinite inputs cannot be hidden by a zero multiplier. NaNs, ambiguous
zero-division signs, division depending on subnormal flushing, integer conversion,
nonfinite texture/LOD arguments and undefined powers remain unresolved. This is
controlled source math, not bit-identical GPU arithmetic or appearance certification.

Three exact audit sources supply research cases:058 contains reciprocal blur and
normalization paths;086 contains a repeated quadratic map followed by a squared
norm;104 contains blur values raised to an audio/colour-dependent exponent.
The first-step source-field diagnostic localizes058 to composite1/blur2 with a
zero denominator in all36,864lanes;086 to warp dot(zz,zz), overflowing8,282lanes;
and104 to composite pow(0,-0.100000024). With the opt-in policy,058/086 compute
that one source step;104 remains unresolved. These are math controls, not new
visual passes or native defects. Full60-step and authored appearance validation
remain separate. No new native frames or image inspection were used.

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
