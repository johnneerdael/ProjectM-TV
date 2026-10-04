# Fractional returns, output storage and call ordering

The source model now understands `modf` as a two-result operation: its return
is the signed fractional part, and its output argument receives the integral
part as a floating-point value. The output's old value is not read. Local/global
variables, swizzles, array cells and input/output aliases retain their state.
Output writes are registered in loops and in read/write conflict analysis.

The pinned HLSL parser table declares both arguments as inputs. The pinned
`GLSLGenerator.cpp` instead emits a scalar wrapper with an `out float` parameter.
The analyzer applies that semantic correction without modifying the native core
or silently initializing uninitialized storage. Unwritten vector components
remain unknown; constant and non-writable output targets are rejected.

[GLSL ES 3.00 §8.3](https://registry.khronos.org/OpenGL/specs/es/3.0/GLSL_ES_Specification_3.00.pdf)
defines the signed fractional and integral results. Its §6.1.1 specifies that
function arguments are evaluated once from left to right, before function
execution and output copying. The analyzer therefore preserves a `modf` update
read by a later argument of the same call. It does not generalize this to
unestablished arithmetic or compound-value ordering. Multiple user-helper output
arguments remain separate work.

The numerical model supports componentwise vector calculations. The actual
pinned wrapper accepts only scalar calls: offline GLSL330 and GLES300 checks
accept the scalar fixture and reject the float2 fixture. Runtime stage selection
still requires source-bound compatibility evidence and uses fallback where
appropriate. Vector language understanding is not evidence of native acceptance.

## Verification

Reparsed all nine distinct preset/section witnesses from the saved `modf` gap
inventory. All nine now lower completely. These are source interpretation
results, not nine appearance-validation passes or a whole-corpus percentage.

Four analytical predictions were frozen before execution on the owned API34
`emulator-5582`, using the unchanged published ProjectM-TV core 2.2.4 AAR:

- Positive input and integral output.
- Negative input and sign-preserving fractional output.
- Local output storage carried across loop iterations.
- An updated output value consumed by a later function argument.

Every RGB8 value in all 30 frames of each fixture matches the expected values
with zero byte error. Runtime/renderer, original source and capture identities
are retained in `tools/milk-analyzer/fixtures/modf-native-proof-2026-10-04.json`.
Source witnesses and scalar/vector compiler checks are retained in
`tools/milk-analyzer/fixtures/modf-source-proof-2026-10-04.json`.

Focused tests also cover negative zero in the binary32 reference calculation,
floating integral values beyond signed integer range, aliases, unwritten
components, invalid outputs, local/global loops and unresolved compound writes.
A review found that local compound-value conflicts were missing from the guard;
scalar/swizzle/array counterexamples now remain unknown and the recheck passed.

Native byte agreement is limited to the four defined fixtures and this renderer.
It does not certify GPU signed-zero behavior generally, full feedback evolution,
mood scores or random-preset visual accuracy.
