# Helper state, scope and assignment ordering

This work proceeds independently of the shared corpus run. It improves the
mathematical source model and checks specific calculations against the unchanged
published ProjectM-TV core 2.2.4 AAR.

## Source semantics added

Shader helpers now preserve global-variable updates across explicitly sequenced
calls and statements. A helper's return value may be discarded without discarding
its state updates. Parameters and block-local variables retain lexical scope,
including when a local has the same name and initial value as a global.

Transitive read/write analysis follows helper calls, including nested helpers.
Loops register shared writes hidden inside calls as loop-carried state. Conditional
updates remain separate per pixel, and branch updates feed subsequent loops.
Execution effects needed for loop/domain checks are preserved in the caller.

Conflicting reads/writes in arithmetic operands, constructor arguments and
conditional/logical expressions remain unresolved where sequencing is not yet
established by the model. Effectful index expressions and unsupported loop
global/local shadow aliases remain explicit gaps.

## A defined ordering rule learned and implemented

A focused review found an indexed assignment whose RHS helper changed its
destination index. Evaluating the helper first would select the wrong element.
The published core on the isolated emulator used the original index.

[GLSL 3.30 §5.8](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.3.30.pdf)
and [GLSL ES 3.00 §5.8](https://registry.khronos.org/OpenGL/specs/es/3.0/GLSL_ES_Specification_3.00.pdf)
specify destination-expression evaluation before the RHS. The lowerer now
captures destination indices before evaluating the RHS, rather than leaving
that defined behavior unknown. Array, vector and nested-helper tests predict
`[9,2,1]` for the review's example. Compound assignments also retain captured
indices when the RHS only changes the index; conflicting mutations of the
stored value remain guarded.

The original probe committed two possible outputs while its model was unresolved.
The subsequent specification-based prediction is recorded separately; it is not
retroactively counted as a blind prediction pass.

## Independent native checks

Created the task-owned `projectmtv-learning-api34` AVD at
`build/milk-analyzer/android-learning/avd-home`, running as `emulator-5582`.
Other emulators, devices and corpus jobs were not modified. Its local process
identity is recorded in `emulator-process.json` and must be revalidated before
future operations. It uses the already installed API34 ARM64 default image.

The AAR and extracted ARM64 library are unchanged. A separate runner clock helper
and published JNI class supply numerical captures in a GLES3 pbuffer. Library,
runtime, PCM, source and capture hashes are retained with the renderer identity.

Three analytic predictions were frozen before native observation: sequential
shared updates, nested parameter shadowing and writes hidden inside a loop.
All 30 frames of each fixture match the expected RGB8 values with zero byte
error. The separate destination-index observation yields `[230,51,26,255]`,
consistent with the specification-based calculation.

An initial attempt used an overlong PCM fixture and terminated after capture
with `PCM exceeds frame schedule`. Its capture/log are retained as an aborted
attempt and excluded from successful results. The successful fixtures use
exactly 30 frames of PCM.

## Impact and verification

Rechecked 17 recorded global-write gap uses across 14 distinct presets/sections;
all 14 sections now lower completely. These counts describe those witnesses,
not a new whole-corpus appearance percentage.

The complete analyzer suite passes 562 tests and 33 subtests. A focused code
review returned no remaining Important findings after checking assignment
ordering, nested destinations, swizzles and indices changing in loops.

Evidence:

- `tools/milk-analyzer/fixtures/helper-state-source-recheck-2026-10-04.json`
- `tools/milk-analyzer/fixtures/helper-state-native-proof-2026-10-04.json`
- `tools/milk-analyzer/fixtures/helper-index-order-native-observation.json`

These are numerical state/interaction checks. They do not establish complete
feedback prediction, calibrated mood scores or the random-preset visual benchmark.
