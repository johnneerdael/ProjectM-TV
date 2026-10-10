# Enzyme component runtime validation — 2026-10-10

Enzyme works as an isolated LLVM derivative backend for unchanged pure MilkDrop
helper bodies exported through Slang C++. The runtime is an evaluation oracle for
functionality we could adapt into the predictor; **making Enzyme a primary
integration library is not the recommendation**. This qualification establishes **zero
new predictor range bounds and zero changed mood classifications**. Enzyme
produces derivative programs; it does not establish their lifetime input domains,
continuity, visibility or native GLES equivalence.

The original objective remains source-only flashing, motion and prominence for
Chill / Normal / Intense. No predictor Python module, preset, renderer, image,
audio/frame sequence or Android artifact was changed by this evaluation.

## Runtime identity and bridge

- Official shallow repository: `EnzymeAD/Enzyme`, pinned commit
  `3eb77c40fc8e40e0e6f5a2765f82fb4fafe1a86d`; repository working tree unchanged except the
  untracked external `evaluation/` directory.
- LLVM / Clang **21.1.8**, installed Homebrew toolchain under
  `/opt/homebrew/opt/llvm@21`; Slang **2026.19** from the already prepared
  official binary distribution.
- Built `ClangEnzyme-21.dylib` and `LLVMEnzyme-21.dylib` with the matching LLVM CMake
  package and compiler. Both runtime paths generated derivatives successfully.
  Clang plugin SHA256: `cbed5456666ea13e9179b95fd35cef439c007499b52fe6c77a2cab4f4a7481b0`.
- Host: Apple M4 Pro, macOS15.8. C++17, `-O2 -ffp-contract=off -fno-fast-math`.
  These flags do not turn derivative IR into a native rounding proof: generated
  derivative instructions include fast arithmetic annotations.
- Source/runtime/evidence lives in
  `/Users/jneerdael/Scripts/source-analysis-evaluation/enzyme/`.
  LLVM/Slang dependencies remain outside the project; no global configuration was
  changed or predictor dependency installed.

The documented plugin APIs replace `__enzyme_fwddiff` / `__enzyme_autodiff` requests
in LLVM. This experiment uses a **typed float32 forward request**, not a variadic
argument that promotes float inputs to double. The separate `opt` invocation uses
`-load-pass-plugin=LLVMEnzyme-21.dylib -passes=enzyme`. The pinned `enzyme/Enzyme/CApi.h` exports `EnzymeCreateForwardDiff` and
`EnzymeCreatePrimalAndGradient`; those C API functions were inspected but not
directly invoked here. The plugin hooks are the validated integration surface.
[Official usage](https://enzyme.mit.edu/getting_started/UsingEnzyme/) and
[calling conventions](https://enzyme.mit.edu/getting_started/CallingConvention/)
describe the argument/activity and primal-execution contracts.

Slang exports `export __extern_cpp` scalar wrappers to C++; the original helper
bodies are preserved. Only wrappers, derivative requests and neutral attributes
are appended. This is the supported
[Slang CPU export path](https://github.com/shader-slang/slang/blob/master/docs/cpu-target.md),
not an HLSL-to-C++ hand transcription.

## Unchanged source functions and original graphs

| Preset | Preset SHA256 | Preserved helpers |
|---|---|---|
| `flexi - target practice-5-liquid-2-twitch-2.milk` | `4b2ac79def5fff13a4dc86ce42ca68b6463a9ac919759fef01bb845ea3dc17ef` | `sigmoid`, `vortex` |
| `GreatWho + Flexi - Lasershow [bipolar slickery party].milk` | `00596b146a4975cdd28523ae7dfad218da90283f08f89e6a0ed2da233495be2e` | `complex_div` |

The vortex helper-text SHA256
`9ae468083f58f8311b1722a91c83157de2004e58c7c27547ab25afb3c5d1a36f`
exactly matches the existing [saved Slang derivative record](../superpowers/evidence/source-compiler-components/slang-vortex.json).
The scalar vortex wrappers vary domain.x, hold domain.y=.55, position=.5,
motion=(.01,-.02), domainAspect=1, radius=.07, sharpness=50, spin=1 and zoom=4.
The complex wrappers vary numerator.x and hold numerator.y=.2,
denominator=(.7,.3). These explicit helper contexts are **not claims about the
actual preset's changing Q/audio/texture bindings**.

[Original typed graph evidence](evidence/enzyme-validation-2026-10-10/original-typed-graphs.json)
retains the native-reader engine/parser identity, original float32 arithmetic tags,
casts, textures, Q/state and RNG nodes. Full shader native selection remains
`unknown` in that isolated graph inspection because no native compatibility proof
was supplied. The helper bridge does not erase those obligations. For example,
the vortex warp DAG has497 nodes, including143 shader-float32 operations and19
sample nodes; the helper alone does not replace this program.

## Fixed calculus comparisons and retained failures

Twelve functions at twelve fixed scalar inputs produce144 cases. Of139 nominal
smooth-point comparisons,135 agree with independently written analytic chain
rules within the recorded tolerance. Five seam cases explicitly lack a certified
ordinary derivative. Four comparisons remain failed or numerically unqualified;
the denominator is not rerolled. This is **not a visual or general correctness
percentage**.

| Calculation | Enzyme result / limit |
|---|---|
| Polynomial and `sin(60*x)` | Matches independent polynomial and `24*cos(60*x)` derivatives |
| Actual sigmoid | Matches `-3*s*(1-s)`; nominal Lipschitz ceiling.75 can be derived independently |
| Actual vortex x/y | Matches the independent radial/sigmoid/rotation/zoom chain at interior qualified inputs; clamp and overflow failures retained below |
| Actual complex division | Matches derivatives `.7/.58` and `-.3/.58` |
| Five-step nonlinear loop | Matches chain product of `cos(y)+.1`; independently bounded by `1.1^5` |
| Input-dependent integer-trip-count loop | Enzyme generates its derivative without a loop-bound annotation; integer seams remain discontinuous/uncertain |
| Float-to-int cast | Returns local derivative0 away from integer discontinuities; this cannot prove absence of flashing |
| Piecewise branch and saturate | Generates the selected local branch derivative; seam/reachability schedules require separate proofs |
| Opaque external texture | Fails explicitly: no forward derivative found; no fabricated texture derivative |
| Mutable global state | Compiles, but derivative invocation executes the primal: state0→.25 at x=.5, derivative1; no recurrent-state trajectory follows |

Retained source limits:

1. Vortex.x at x=0: float32 arithmetic lands on a clamp boundary while the ordinary
   real expression is slightly outside it; both generated derivatives are≈1,
   versus the guarded nominal analytic0.
2. Vortex.x at x=1: Enzyme returns0, Slang≈1. The same float32 primal can receive
   different derivative tie choices. Neither establishes portable GLES behavior.
3. Vortex.y at x=2.3: the original float32 exponential is finite, but generated
   derivative intermediate arithmetic overflows and returns NaN in both backends.
4. Vortex.y at x=3.2: the original exponential and derivative leave the finite
   float32 domain. A finite saturated output does not rescue this domain.

The initially unannotated Slang baseline refused the input-dependent loop because
it lacked `MaxIters` / `ForceUnroll`. The cause was recorded, then the comparison
used `[MaxIters(4)]` under the explicit tested input domain where int(x)≤4; no loop
arithmetic was rewritten. LLVM scalar-evolution also recovers the symbolic
backedge count `(-1 + %2)`, but its unconstrained constant cap2147483646 is not a
useful declared-source-domain bound.

All point values/derivatives, seam exclusions, failed cases and complete generated
scalar LLVM derivative programs are retained in the
[compact evidence](evidence/enzyme-validation-2026-10-10/summary.json) and
[derivative programs](evidence/enzyme-validation-2026-10-10/derivative-programs.json).
These are evaluations of isolated pure math helpers, not executions of full
shaders, rendered frames or dataframe/audio trajectories.

## Rangeability and actual gain

Enzyme does not emit interval/range proofs here. A derivative returned at a point
cannot become a global brightness, motion or prominence bound. An independently
derived nominal vortex input-axis ceiling is27.66965 under x∈[.43,.73] and the
listed fixed wrapper parameters: bound sigmoid sensitivity by12.5, rotation/zoom
by their nominal operator ceilings and saturate by1. The same chain can be derived
from the already available Slang program; **gain over Slang is0**. The sigmoid.75
and loop1.61051 ceilings are similarly independent algebra, not proof-by-probing.

The concrete additional reusable capability is LLVM derivative generation through
ordinary typed control flow, memory operations and integer-dependent loops,
without requiring a bespoke helper translator or a Slang differentiability
annotation on each function. The actual helpers in this evaluation were already
within Slang's capability. Therefore **additional actual preset bounds and mood
classifications attributable to Enzyme remain0**, and full9606 coverage was not
claimed or measured.

## Observed compile and transport cost

| Operation | Observed cost |
|---|---:|
| Slang pure helper→C++ | 0.109s median,3 runs |
| Clang baseline shared library | 0.196s median,3 runs |
| Clang+Enzyme derivative library | 0.201s median,3 runs |
| Slang derivative→C++ | 0.154s median,3 runs |
| Compile Slang derivative library | 0.203s median,3 runs |
| LLVM `opt` plugin process | 0.025s |
| Persistent math worker | 18.33µs/request,1000 sequential requests |
| Transient math worker | 7.24ms median,10 launches; cold first7.94ms |
| Enzyme derivative via ctypes | 0.565µs/call,20000 calls |

These are observed developer-host times with three compile samples, not a controlled
performance claim or Android cost. Package build time was not instrumented;
configuration took6.18s and the successful plugin build was observed separately.
The low persistent-call cost does not remove source extraction, compilation,
domain-proof or derivative-program range analysis costs.

## Minimal functionality to adapt, rather than a library integration

The concrete candidate is **seed-aware forward Jacobian-vector propagation over
our existing typed helper/loop DAG**, using Enzyme's primal/shadow separation and
activity-gated derivative rules. Produce a nominal derivative *program* and pass
it to the existing range calculator; do not evaluate the authored program as a
frame simulation. This can unify helper differentiation instead of adding a
separate hardcoded formula for each vortex, complex operation or loop.

Pinned implementation references at commit
`3eb77c40fc8e40e0e6f5a2765f82fb4fafe1a86d`:

- `enzyme/Enzyme/InstructionDerivatives.td`: `SelectIfActive` and
  `ForwardFromSummedReverse`, the `FAdd`/`FSub`/`FMul`/`FDiv` patterns around
  lines1199–1227, plus scalar intrinsic rules. These show how a rule catalog
  constructs tangent expressions and avoids introducing inactive contributions.
- `enzyme/Enzyme/AdjointGenerator.h`: `visitPHINode` around1508 and
  `visitSelectInst` around1638 dispatch the corresponding forward shadow flow.
- `enzyme/Enzyme/GradientUtils.cpp`: the PHI shadow construction around6582–6712
  preserves incoming control-flow edges rather than treating loop-carried values
  as independent fresh inputs.
- `enzyme/Enzyme/ActivityAnalysis.h`: the `isConstantInstruction` /
  `isConstantValue` distinction is useful architectural guidance. Do not transplant
  LLVM's alias/type/activity subsystem into a Python `Field` analyzer.

A minimal adaptation would use the existing parser, `Field` node identities and
`LoopPlan` limits, with no LLVM/Enzyme runtime dependency:

1. Add one memoized nominal `(primal, tangent, activity, domain-obligations)`
   transformation for the already supported pure arithmetic/vector operations.
   Reuse existing scalar rules and domain checks; importing a second catalog of
   elementary calculus alone adds no capability over current SymPy.
2. Propagate the same shadow environment through pure fixed-trip-count helper
   loops. Carry per-output tangent expressions through branch/loop joins;
   preserve shared DAG correlations instead of summing unrelated magnitude bounds
   prematurely. Require an existing proved finite trip count and graph budget.
3. Qualify `select` branches with existing predicate/continuity machinery.
   Enzyme's selected local branch derivative is insufficient for a lifetime bound:
   active predicates, changing trip counts, casts, modulo, sampling and persistent
   state remain explicit obligations. Reuse existing event evidence for seams.
4. Feed supported nominal tangent expressions to the existing interval/proof
   calculator and export their source/model/domain identities. Retain original
   float/int/phase metadata and all failed original numeric domains. No derivative
   zero may become a flash-absence or native-byte certificate.

**Decision:** retain this as a concrete bounded adaptation candidate, but **do not
start a production port yet**. The current actual-source comparison demonstrates
zero extra bounds beyond Slang and zero classifier gains. Porting only elementary
rules duplicates working SymPy/range code; porting control-flow/loop machinery
without a source-domain consumer would add another generator of unbounded
programs. First identify a frequent existing helper/loop gap that this exact
transformation can resolve in flashing, motion or prominence. Then require a
before/after source-bound result on that unchanged fixture before expanding it.
No new corpus was run to manufacture that justification.

Engineering estimates, not measured implementation times:1–3 developer days for
a pure DAG/rule adapter and its type/domain controls; another3–5 days for qualified
fixed-loop/branch shadow propagation; another2–4 days for range/export integration
and retained-failure regressions. A full LLVM activity/type/memory port is outside
this minimal candidate. These estimates assume reuse of the current parser,
helper/LoopPlan and range/proof interfaces, not rebuilding a compiler.

The validated external Enzyme plugins remain useful as a **test oracle** for that
future adaptation, including the four retained numerical limits and stateful/
texture negatives. They are not a proposed primary predictor dependency or a
substitute for the primary source-behaviour goal.

For copied/adapted Enzyme implementation or derivative-table text, retain its
Apache2.0-with-LLVM-exceptions license, copyright/attribution notices, pinned source
references and a clear modification notice. The inspected pin has no tracked
`NOTICE` file; preserve any upstream notice requirements if a later pin adds one.
A port would need its own provenance and license entry even if it imports no
binary. Independently deriving elementary calculus rules is a different reuse
choice; do not describe translated upstream implementation as an independent
implementation. No upstream source was copied into predictor modules here.

Reject or retain explicit unknowns for textures without a declared sampling
model, globals without shadow/storage adapters, persistent state/phase inputs,
source domains producing nonfinite primal or derivative arithmetic, discrete
casts and branch seams. Floating-point AD treats primitive derivatives as local
continuous tangents; it is not the literal derivative of a quantized floating-point
map and does not prove native byte/modulo cadence or visibility.

Enzyme's official license is
[Apache2.0 with LLVM exceptions](https://github.com/EnzymeAD/Enzyme/blob/3eb77c40fc8e40e0e6f5a2765f82fb4fafe1a86d/LICENSE).
Keep its license with redistributed plugin bytes. Slang uses its published
Apache2.0-with-LLVM-exception licensing; its existing binary/prelude licenses remain
part of the external tool distribution. No vendored predictor/runtime library was
added.

Reproduction code and binaries are external under `enzyme/evaluation/`; run
`evaluate.py`, compile its recorded `worker.cpp` request program, then run
`finalize.py` and `typed_graphs.py` with the prepared environments. The evaluation
asserts the retained four-case failure set, rather than treating all144 cases as
passing. Download copies include exact inputs, generated programs, identities,
commands/diagnostics, working plugins and the report.
