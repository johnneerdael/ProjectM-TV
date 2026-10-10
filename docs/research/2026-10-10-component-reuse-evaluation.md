# Component reuse evaluation for the preset predictor

Date: 2026-10-10. Predictor checkpoint: `2c96284f` on
`feat/predictor-static-output-bounds`. The original predictor goal remains paused.
This evaluation tests ways to incorporate existing components into our tool.
It does not replace the predictor, change its dependencies or modify the AAR.

## Decision

**First select substantial work from our graph/gap inventory for bounded
SymPy/Z3 adapters; do not adopt either for the toy controls alone.**
Use compiler analysis infrastructure selectively for complex shader functions.
Reuse MilkDrop-specific fixtures and pattern ideas where they add coverage.
The experiments demonstrate reusable capabilities; neither development-time
savings nor end-to-end predictor speedup has been measured after integration.

| Component to incorporate | Work it can carry for us | Priority and integration point |
|---|---|---|
| SymPy algebra/differentiation | Correlated expression simplification, exact nominal derivatives, polynomial identities | First: optional pure-real fallback/refinement in `source_control_bounds.py` over existing `Field`/exported graphs. Preserve native operations separately. |
| Z3 proof queries | Branch feasibility, relational bounds, candidate loop/state invariant proofs and counterexamples | First: extend restricted `equation_domains.py` proofs and source domain checks. Prove candidate invariants using initialization + transition, not sampled frames. |
| SPIR-V Tools control-flow/def-use APIs | Function call graphs, definitions/uses, dominators, loop structure, selected SSA and dead-code passes | Next: auxiliary compiler-backed analysis in complex shader lowering. Keep native HLSL/GLSL binding/source joins authoritative. |
| Stims dataflow and shader-pattern code | Dependency fixpoint methods, random-call dependency handling, pattern vocabulary, source fixtures | Useful now as implementation reference/test input. Adapt host storage/audio semantics; do not import its phase policy or heuristic defaults. |
| Slang differentiation/uniformity passes | Derivative generation for larger pure functions and control flow, uniformity propagation | Useful targeted follow-up once pure function export is stable. Texture reads require explicit derivative models; not a global bound generator. |
| Naga IR/validator analysis | Typed expression/statement graphs, uniformity, resource-use information and serialization | Useful for a Rust consumer or auxiliary shader graph. GLSL440/Vulkan input and SPIR-V translation need a qualified bridge from our GLES300 target. |
| Crab relational domains/fixpoint solver | Loop/state inference with intervals, congruences and relational domains | Keep for larger state programs if bounded Z3 queries become a bottleneck. Requires CrabIR lowering and EEL arithmetic adapters. |
| SPIRV-Cross reflection | Existing JSON/C API for shader resources and active interfaces | Small supporting addition to the SPIR-V route; inventories only, no behaviour-score claim. |
| eel-wasm and milkdrop-preset-utils | Parser/source mapping, independent fixtures, preset field/sampler handling | Test/reference reuse; lower immediate benefit because we already parse exact native language and export typed graphs. |

## Completed experiments

### Existing predictor graph → SymPy

A small adapter consumed our existing `center_source_expressions` JSON, not a
new language parser. For `sin(bass)^2 + cos(bass)^2`, our independent-interval
calculus reports an absolute response ceiling about 4; SymPy reduced the nominal
derivative to zero in about 11 ms. This shows a practical way to tighten loose
correlated bounds using established algebra.

The prototype rejects casts, native narrowing, samples and execution sequences;
four negative controls pass. It accepts only a small pure scalar operation set.
This is a nominal real-number refinement, not a native floating-point rewrite.
Symbols do not invent audio ranges or persistent-state values. A zero real
derivative must not silently become a claim of zero GPU quantization change.

A broader follow-up uses the actual exported centre expressions from all 2,000
presets: 2,956 shapes contain 5,912 axis expressions. Of these, 2,515 fit the
small pure scalar operation/depth subset, and 251 depend on current audio bands.
170 of those axes have an existing unresolved response for a contributing band.
SymPy generates derivatives for all 251 axes in 0.196 seconds with no one-second
query timeout. **It resolves zero previously unknown constant derivatives with
this adapter.** This demonstrates broad derivative availability, not new final
range bounds. A single trig identity is readily handled locally and does not
by itself justify a substantial integration. A worthwhile next experiment can combine
derivatives with source/state domain proofs on recurring difficult formulas.

### Z3 mathematical and floating-point queries

Five proof/counterexample controls completed within roughly 0.4–3.3 ms each:
bounded persistent-state induction, an unbounded mutation counterexample,
correlated zero divisor and finite float32 clamp bounds, plus a float32 identity
counterexample. The bounded recurrence proof uses real arithmetic; the clamp and
rounding counterexamples use Z3's explicit float32 operations. Keep those models
distinct. Results `unknown`/timeout must remain abstentions.

Z3 finds that `(1+x)-x` is zero for float32 `x=16777216`, despite the real-number
identity being one. That control demonstrates why the adapter must preserve
numeric domains and operation order. The generic proof examples are not yet
automatically lowered from our EEL state programs; that adapter remains work.

### Exact translated shaders → glslang/SPIR-V Tools

Used the first 32 exact presets in the fixed seeded 2,000 sample and their saved
source-bound compiler requests. All 50 authored shader sections:

- parse into glslang ASTs with the original GLES300 source;
- compile to inspection SPIR-V after an explicitly recorded ES300→ES310 version
  change and automatically assigned inspection interface locations/bindings;
- pass the selected SPIR-V normalization passes.

AST + SPIR-V compilation totals 3.21 seconds, about 64 ms per section, including
process startup; this timing excludes the subsequent normalization passes.
Exact GLES300 SPIR-V generation was rejected because that frontend requires
ES310+. The inspection version/bindings must not be passed off as native runtime
observations or certified target equivalence.

The useful components are the existing `DefUseManager`, control-flow graph,
dominators, loop descriptors and explicitly selected normalization passes.
Source inspection confirmed these APIs in the pinned checkout. No new
hand-written SPIR-V parser is necessary. Their optimizer internals are not a
stable external API; pin the dependency/version and isolate the wrapper.

Aggressive merge-return/inlining/SSA/dead-code processing increases instruction
records across these sections from 41,150 to 68,270: helpers are expanded at call
sites and their branch protections remain. Therefore the experiment does not
establish a smaller graph or faster predictor. Retain function summaries and
expand only calculations whose dependencies require it.

An installed SPIRV-Cross binary also exported JSON input/output/sampler reflection
for an inspected module. Its auto-assigned bindings are inspection identities,
not the AAR's actual texture units.

### Stims components and fixtures

Compiled and ran source dataflow for the same 32 presets in 145 ms total, with
no thrown exceptions; three presets report parsing errors (memory assignment,
while syntax and statement-sequence syntax). This is much lighter work than our
complete numeric/source report, so it is not a fair speed ratio.

Ran its own focused suites: 34 dataflow tests and 76 expression/shader/syntax
tests pass. Twelve custom controls compare its summaries with our current output.
The valuable reusable work includes fixpoint dependency propagation, overwrite
tracking, random-stream dependency ideas and independently authored fixtures.

Controls/source inspection identify policies that need adaptation:

- Stims feeds custom Q writes back into main-frame dependencies; our engine's
  main Q reload and custom phase boundaries require isolation.
- Its Q accumulator summary differs from our main-Q init reload.
- A constant false branch retains an audio dependency in its dataflow summary;
  our causal slicing excludes the dead branch.
- `sqrt(-1)` is zero in its function table; our pinned evaluator uses
  `sqrt(abs(x))`, producing one.
- Initialization audio is described as silent by its dataflow model; our
  snapshots remain distinct declared inputs without assuming silence.
- Its shader pattern layer tolerates/degrades unsupported expressions, whereas
  our numerical descriptions must retain explicit uncertainty.

These are adapter requirements, not reasons to discard the implementation work.
Its memory taint summaries could be useful as a coarse dependency layer, but do
not infer values or precise cell aliasing. Its full flash-guard consumes frame
sequences/timelines, so it is outside source-only scoring; pure colour conversion
helpers and fixtures may still be reused under declared colour-space premises.

## Remaining candidates: inspected scope, no runtime benchmark claimed

- **Slang:** inspected its autodiff/loop and uniformity implementation and guide.
  It generates derivative programs, which we would still have to bound over input
  domains. Hardware texture operations need custom derivative/reference models.
  `TreatAsDifferentiable` emits trivial zero derivatives and must never be used
  to hide a missing response. No Slang binary/build test was performed.
- **Naga:** inspected public typed IR, `FunctionInfo.global_uses`, expression
  uniformity and serialization features. These save Rust graph/validation work.
  We do not gain EEL frame orchestration or effects/mood labels from them. No
  Naga build/acceptance benchmark was performed.
- **Crab:** inspected rational/integer CFG domain examples and interval/fixpoint
  APIs. Relational domains may preserve correlations our independent intervals
  lose. Actual EEL double arithmetic, casts and nonstandard functions still need
  explicit transfer functions. No Crab build was performed.
- **DXC:** useful maintained HLSL frontend but documented Shader Model6+ route;
  our native translator already covers the legacy source contract. A secondary
  frontend may help selected functions, but adds less immediate value than the
  available GLSL frontend for current source graphs.
- **Daisy/FPTaylor:** additional precision-analysis candidates inspected through
  primary docs. They can bound roundoff under declared formats/domains, useful
  after nominal symbolic refinement. They require additional language/runtime
  adapters and GPU transcendental assumptions. No local acceptance test yet.
- **Herbie:** valuable for discovering numerically stable formulas in new preset
  generation; its purpose is changing arithmetic, so keep it outside authored
  prediction paths unless analysing a separately labelled adaptation.

## Incorporation sequence and acceptance

1. Add a **bounded, optional symbolic maths adapter** to our existing source
   graphs. Use it for pure supported unresolved/loose formulas, cache by typed
   graph + assumptions + backend version, retain original arithmetic obligations,
   and feed generated derivatives back into our qualified range calculus.
   Keep a separate-process time limit; no full-preset simplification by default.
2. Add **solver-assisted proofs** to current domain/invariant analysis. Prove
   initialization and inductive transition, preserving resets/phase isolation.
   For float parity, use explicit formats/rounding; for nominal real proofs,
   label the scope. Preserve counterexamples, timeouts and unsupported operations.
3. Use **SPIR-V/compiler summaries** where current graph lowering lacks functions,
   branches, loops or resource information. Begin as an auxiliary audit. Require
   exact source joins and preserve numeric conversions, effects and sampler data;
   do not silently change production profiles or replace source tokens with
   optimized-away behaviour.
4. Import/port **selected Stims fixture and pattern ideas** with attribution and
   target-policy adapters, retaining our existing parser and host semantics.
5. Evaluate Slang/Crab/Naga implementations only against the concrete remaining
   cases that their components address; avoid a new general framework first.

Measure new supported *calculations*, counterexample quality, lost predictions,
end-to-end analysis cost and affected preset count on the unchanged 2,000 pool.
A green compiler or a library's own tests alone does not prove a new prediction.
Development-effort savings are plausible but not quantified before integration.

## Step-by-step adoption gates

Keep the original goal paused while agreeing and testing these additions one at
a time. Adapter effort affects planning, not eligibility: a component with more
integration work stays a candidate when it can address more important gaps.
Do not declare an addition successful merely because it compiles or its own
library tests pass.

| Step | Concrete first addition | Evidence to collect before deciding the next step |
|---|---|---|
| 1 — SymPy | Import our already parsed pure scalar graph, obtain simplified derivative formulas, and pass them back to our existing domain calculus. Start with repeated-input/trig/polynomial correlations. | Frozen synthetic algebra controls and counterexamples; exact affected preset names/count; tighter nonzero or zero *nominal* response bounds; no lost cast/domain obligations; total per-preset and worst-case processing cost. |
| 2 — Z3 | Add bounded proof requests for branch feasibility and candidate persistent-state/selector invariants, preserving phase resets and explicit numeric models. | Before/after unresolved cases, initialization and transition proofs, mutation counterexamples, timeout/unknown counts, solver cost and exact typed-model provenance. |
| 3 — compiler infrastructure | Add an auxiliary shader analysis view backed by glslang AST / SPIR-V def-use, dominators and function summaries. Apply normalization only where needed. | Source/resource joins, function/loop dependency recovery, agreements/disagreements with current live RGB/UV slices, numeric/conversion preservation, graph growth and analysis cost. Inspection-profile differences remain explicit. |
| 4 — Stims components | Adapt selected dependency/fixpoint/memory-taint and shader-pattern implementations; import useful fixtures with lineage. | Each adapted policy tested against our engine contract; new supported live paths or effect descriptors; dead/overwritten/disabled controls; no borrowed Q/init/audio policies; exact corpus gains. |
| 5 — Slang | Generate derivatives for the remaining substantial pure shader functions/control flow that steps 1–3 do not handle efficiently. Provide explicit texture derivatives only for a declared sampling model. | Compiler acceptance and generated derivative semantics on exact functions; additional bounded calculations; discontinuity/texture negatives; numerical estimates versus independently derived controls; integration/runtime cost. |
| 6 — Crab | Lower common persistent-state/loop fragments to relational abstract domains and use their inferred invariants as candidates for proof. | New relational bounds compared with the step2 solver; stable recurrence/init/reset evidence; precision versus widening/timeout; EEL numeric transfer-function controls. |
| 7 — Naga | Export qualified shader programs into its Rust typed IR and consume expression uniformity/resource-use data. | Acceptance on selected exact difficult programs; preserved numeric/call/resource mappings; incremental coverage beyond step3; Rust consumer usefulness and overhead. If a Rust consumer is needed sooner, promote this step. |
| Supporting — SPIRV-Cross | Attach resource/interface reflection to step3. | Stable source-bound inventories, correct alias/profile distinction and no inferred visual score. |
| Supporting — precision tools | Apply Daisy/FPTaylor to important real/native discrepancies after nominal algebra; use Herbie only for separately labelled new/adapted effects. | Explicit numeric format/transcendental/overflow assumptions, independently checked error bounds and no rewriting of authored prediction semantics. |

Use the unchanged seeded 2,000 sample for the actual integration comparison.
Reuse saved parser/compiler evidence where its hashes still match. Preserve all
terminal records, unsupported cases and full/partial coverage distinctions;
sample neither only successful presets nor new random replacements.

For every step report four separate outcomes: (1) calculations newly understood,
(2) estimates made tighter, (3) predictions or unknowns changed and why, and
(4) processing cost. A useful addition may be a better counterexample or more
honest unknown, even when it does not increase a headline coverage count.
Recognizable image recreation and mood quality remain separate downstream
validation goals. No percentage improvement is promised from this evaluation.

### Adoption value rule

For each candidate compare the narrowest correct local implementation with a
library adapter. Adopt when it addresses a meaningful recurring gap, when even
a narrow capability would be substantially harder to implement correctly
ourselves, **or when the adapter is genuinely small, useful and low-risk with
little maintenance/runtime cost**. A small observed gain may justify that last
case because the wider 9,606 pack may contain more instances. Do not promise
that larger gain before measuring it. A toy example alone cannot justify a large
integration, but a cheap sound helper need not wait for a major coverage gain.
More adapter work is acceptable when the expected gain is correspondingly larger.
None of the current experiments establishes a production accuracy or speed
improvement yet.

The recommendation is a value-gated experiment order, not an instruction to
install every candidate. Step1 can begin with a small bounded optional adapter;
expand its scope only where it avoids repeated custom maths or demonstrably
improves the output, ideally with input/state bounds from step2. If the small
adapter adds no useful information or disproportionate complexity, defer its
larger integration and promote solver/compiler work. Other components remain
candidates rather than being excluded merely by implementation effort.

## Repositories, evidence and sources

Eight shallow/sparse clones and the isolated Python environment are under
`/Users/jneerdael/Scripts/source-analysis-evaluation/` (about 288 MiB at inspection).
No predictor Python environment or toolchain was upgraded. Exact commits,
binary hashes, tested package versions, scripts and JSON outputs are in
`evidence/`; a compressed copy accompanies this report. Production changes are
not part of this evaluation.

Primary sources:
[Stims toolchain](https://github.com/zz-plant/stims/tree/36e902704cab7a3c39bfc0a6b2bf587d8ba7e291/packages/milkdrop-toolchain),
[SPIR-V Tools](https://github.com/KhronosGroup/SPIRV-Tools/tree/e56740d931256cc464d4d1a76149f69469c33f70),
[Slang autodiff](https://shader-slang.org/slang/user-guide/autodiff.html),
[Naga](https://github.com/gfx-rs/wgpu/tree/14dd4e8f717cd8c4381908895495ea19ef924c35/naga),
[Crab](https://github.com/seahorn/crab/tree/b1eeb1a9402ab0664e962f26f89d923f8514284c),
[SymPy calculus](https://docs.sympy.org/latest/tutorials/intro-tutorial/calculus.html),
[Z3](https://github.com/Z3Prover/z3),
[SPIRV-Cross](https://github.com/KhronosGroup/SPIRV-Cross/tree/aa217aeb6c9f0ace7a0ab233b28807edf45eb165),
[eel-wasm](https://github.com/captbaritone/eel-wasm/tree/4bae490f6e0e397264a0269de69d47a59079b0d5),
[milkdrop-preset-utils](https://github.com/jberg/milkdrop-preset-utils),
[Daisy](https://github.com/malyzajko/daisy),
[FPTaylor](https://github.com/soarlab/FPTaylor),
[Herbie](https://github.com/herbie-fp/herbie).
