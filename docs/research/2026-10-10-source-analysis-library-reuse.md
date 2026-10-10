# Reusing open-source shader and MilkDrop analysis tools

Research date: 2026-10-10. Scope: source-only effect/audio behaviour extraction,
not rendering or replacing the patched ProjectM-TV engine. Findings below are
from official project documentation; integration/coverage gains are proposals,
not measured outcomes. Existing pending motion qualification stays frozen.

Follow-up: [component evaluation](2026-10-10-component-reuse-evaluation.md)
records pinned source inspections and actual bounded experiments. It prioritizes
SymPy/Z3 adapters, selective compiler analysis and Stims fixture/pattern reuse;
the exploratory recommendations below are superseded by that evaluated sequence.

## Main finding

Useful components exist. There is no need to independently rebuild every parser,
control-flow representation, solver or differentiator. None of the inspected
tools documents a turnkey source-only MilkDrop mood classifier or a complete
feedback-to-recognizable-image predictor. Distinguish syntax/type/dependency
recovery, numerical bounds and effect interpretation.

| Candidate | Existing capability | Relevant use | Boundary |
|---|---|---|---|
| [Stims milkdrop-toolchain](https://github.com/zz-plant/stims/tree/main/packages/milkdrop-toolchain) — TypeScript | Milk preset/EEL AST and IR, shader analysis, `analyzePresetDataflow`, sampler classification and GLSL/WGSL conversion | Independent source dataflow comparison, language fixtures and missing lowering patterns | Its renderer/VM semantics are not automatically our patched AAR semantics; unknown-function defaults and f32 GPU lowering need exact controls |
| [glslang](https://github.com/KhronosGroup/glslang) + [SPIR-V Tools](https://github.com/KhronosGroup/SPIRV-Tools) — C++/CLI | GLSL/ESSL AST, SPIR-V generation, use-definition/control-flow infrastructure, dead-code and constant propagation | Feed our engine's exact translated shader into a standardized program representation; audit live RGB, UV and audio dependencies | Compilation is static work, but generated compiler code is not proof of native-driver arithmetic or final appearance; source maps/bindings and evaluation obligations must survive |
| [Naga](https://github.com/gfx-rs/wgpu/tree/trunk/naga) — Rust | WGSL/SPIR-V front ends, validated typed IR, conversion and graph output | Rust consumer-side effect analysis and later wgpu adaptation | GLSL input is GLSL440+ Vulkan semantics; no direct legacy HLSL front end. SPIR-V route or qualified normalization needed |
| [Slang](https://github.com/shader-slang/slang) — C++/API | HLSL-like compilation, reflection, IR, automatic forward/backward derivative-code generation | Reduce hand-written derivative rules for pure shader functions; investigate uniformity analysis | Global resources/texture reads are nondifferentiable by default. Custom texture derivatives/substitutes required. Generated derivatives still need domain bounds and are not flash/discontinuity guarantees |
| [SPIRV-Cross](https://github.com/KhronosGroup/SPIRV-Cross) — C++/C | Resource reflection, JSON reflection, shader-language conversion | Uniform/sampler/stage-resource inventory and bridging | Reflection describes bindings/types, not what a tunnel looks like or how strongly bass moves pixels |
| [Crab](https://github.com/seahorn/crab) — C++ | Abstract domains, interval/congruence/relational analysis, fixpoint and interprocedural solvers | Persistent EEL state and loop invariants; reduce overly loose independent intervals | Requires an adapter to CrabIR and exact EEL numeric semantics; not a shader visual analyzer |
| [Z3](https://github.com/Z3Prover/z3) — native with Python APIs | Arithmetic/bitvector/IEEE floating-point constraints | Prove selector ranges, branch feasibility and counterexamples for bounds | Resource limits/unknown must abstain; trig/texture/feedback needs explicit modeling. GPU transcendental/rounding behaviour is not supplied by the solver |
| [SymPy](https://docs.sympy.org/latest/tutorials/intro-tutorial/calculus.html) — Python | Symbolic differentiation, algebraic simplification, limits/integration | Pure real formula derivatives, oscillator identities and polynomial geometry | Real algebra cannot erase casts, singularities, side effects or native f32 behaviour |
| [eel-wasm](https://github.com/captbaritone/eel-wasm), [projectm-eval](https://github.com/projectM-visualizer/projectm-eval), [milkdrop-preset-utils](https://github.com/jberg/milkdrop-preset-utils) | Existing EEL/preset parsing/compiler infrastructure | Independent language fixtures and parsing reference | Execution APIs alone do not predict source behaviour; keep our patched evaluator policy authoritative |

## What is actually difficult

1. **Language recovery:** types, casts, branches, loops, arrays, functions and live
   output slices. Compiler IR can help substantially here.
2. **State and phase order:** initialization, per-frame resets, Q/T bridges,
   custom-shape/wave persistence and audio normalization. These are MilkDrop
   host semantics; shader compilers do not define them.
3. **Continuous response versus jumps:** derivatives describe smooth sections;
   thresholds, modulo, `floor`, integer casts and draw gates need separate event
   and range reasoning.
4. **Textures and repeated feedback:** the shader reads an image produced by
   earlier drawing/passes, then transforms it again on future frames. A parser
   exposes the equation but does not supply its unknown input image or prove
   its evolving prominence/palette.
5. **Meaningful effect descriptions:** recognizing coordinate recurrence,
   symmetry, colour transfer, injection and transport, then determining which
   dominates the screen. This layer still needs qualified application analysis.

Shader parsing is not the sole hardest part. Feedback plus state/phase contracts
is the main remaining cross-system problem. This is an inference from inspected
tool scopes and the predictor's explicit unknowns, not a universal impossibility
claim or a measured percentage.

## Recommended next experiment

**Prioritize two small source-only comparisons before another broad custom
compiler effort:**

- Inspect/pin Stims' standalone `milkdrop-toolchain` and compare its dataflow on
  fixed controls and exact existing difficult presets. Credit only proven
  matching semantics. Audit its implementation rather than importing author
  fidelity labels as evidence.
- Use installed glslang + SPIR-V tools on the exact current engine-translated
  GLSL. Capture unoptimized and explicitly qualified normalized representations,
  compare live audio/RGB/UV dependency claims against our current typed graph,
  and preserve casts, discarded code/effects, sampler identities and unknowns.

Measure compile acceptance, source/binding join correctness, disagreements,
newly resolved real gaps and analysis time on a bounded selection. Avoid rewriting
the predictor or introducing a new runtime dependency until that comparison
shows a useful improvement. Follow with a solver/abstract-domain spike on common
persistent-state gaps, not a generic whole-engine proof attempt.

The current Mac already has glslang16.6.0, `spirv-dis` and `spirv-opt`; no new
large toolchain is necessary for the first SPIR-V spike. Slang/Naga/DXC, SymPy
and Z3 were not found in the prepared analyzer environment. That is a local
availability check, not a global installation assertion.

## Important verified tool limits

- glslang's official README deprecates its HLSL front end from April2026. Use its
  maintained GLSL/ESSL route for engine-generated GLSL rather than basing a new
  legacy-HLSL parser on the deprecated path.
- [Slang autodiff documentation](https://shader-slang.org/slang/user-guide/autodiff.html)
  explicitly describes hardware texture sampling substitutes/custom derivatives
  and nondifferentiable global resources. Differentiation alone is not source-only
  global sensitivity or a reachable flash proof.
- DXC's documented command-line target is Shader Model6+, whereas MilkDrop2's
  historical D3DX pixel shaders are a different language/compiler contract.
- Stims' flash analysis is separately advertised as measured warnings/governor
  logic; do not assume its `flash-guard` replaces our source-only analysis without
  inspecting its inputs.

Additional primary references: [SPIR-V def-use API](https://github.com/KhronosGroup/SPIRV-Tools/blob/main/source/opt/def_use_manager.h),
[Stims toolchain API](https://raw.githubusercontent.com/zz-plant/stims/main/packages/milkdrop-toolchain/README.md),
[DXC](https://github.com/microsoft/DirectXShaderCompiler).
