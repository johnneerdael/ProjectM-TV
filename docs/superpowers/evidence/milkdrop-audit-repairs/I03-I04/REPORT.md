# Isolated arithmetic proposals — I03 and I04

All outputs live in `build/audit/arithmetic-proposal`. Canonical patches, evaluator sources, tests, CMake, helpers and docs were not edited. No Git, GL, GPU or device operation was performed. The copies use the current patched worktree evaluator, not the unchanged published AAR. No original Windows evaluator executable was run.

**Subsequent Android compiler finding:** raw proposals fail their protective contract under actual NDK release flags. Android -O3/-ffast-math removes I03 result finite guards and I04 NaN guards, unlike the passing Apple host builds. See `android/README.md`, emitted IR/assembly and exact cross-compile metadata. Cross binaries are prepared but not executed. Do not integrate these raw patches until the compiler policy/implementation is qualified.

**Scoped alternatives:** `android-safe/README.md` compares precise pragmas and memcpy-based bit classification. Pinned NDK bit checks survive for both double and supplemental float formats, but Apple clang fast-math removes I03 bit checks (24/89 failures). Android runtime checks remain pending. Neither raw proposals nor compiler-sensitive alternatives are integration-approved by this preparation.

**Preferred compiler-scoped candidate:** `android-finite/README.md` and `TreeFunctions-finite-source-property.patch` qualify TreeFunctions.c-only -fno-finite-math-only after -ffast-math. Required Android IR guards survive while other fast-math flags remain. Apple host I03/I04 controls pass89/89 and76/76;20 outside-boundary controls pass. It restores pre-existing pow/pow_op/invsqrt NaN guards that Android release flags previously removed, an explicit additional behavior requiring review. Android runtime remains unexecuted.

## Compiler/evaluator execution

Run `python3 build/audit/arithmetic-proposal/prepare.py`, then `python3 build/audit/arithmetic-proposal/run.py` from the worktree root. `--fast-math` and `--no-sanitize` select additional qualification modes. The checked-in Scanner.c and Compiler.c are compiled directly; no parser regeneration, surrogate arithmetic-only evaluator or graphics library is involved. Registering a/b before compiling, then setting them through the API, exercises runtime evaluation rather than constant folding. Assertions cover expression outputs, assignment storage, aliases and argument side effects.

Apple clang 17, arm64 Darwin, O2, double evaluator: baseline I03 fails 28/89 controls; proposal passes 89/89. Baseline I04 fails 19/48 defined controls; proposal passes 64/64 including 16 protective controls excluded from baseline because executing undefined casts or MIN/-1 would invalidate the comparison. Literal handoff witnesses and runtime variable controls both execute through the real compiler/evaluator. Both proposals also pass with `-ffast-math`, with and without UBSan/float-cast-overflow. See `results.json`, `results-fast-math.json`, `results-fast-math-unsanitized.json` and per-role logs. Evaluator Release/RelWithDebInfo defaults ENABLE_FAST_MATH to ON; Android NDK/compiler and exact release flags still require separate qualification.

## I03 proposal

`I03-proposal.patch` changes only /, /=, pow/^ and ^= (their intrinsic aliases reach the same functions). Within the existing suppressed region, compute a result only for nonzero finite inputs and retain it only when finite. All outside-region behavior, comparisons, boolean thresholds and cotangent guards remain intact. Preserve operand evaluation order and assignment pointer semantics.

Executed witnesses: `1/.000001` and `pow(.000001,-1)` change 0→1000000; negative small divisors and integer-power negative bases recover signed finite results. `1e-300/1e-300` changes 0→1. Existing zero, negative-zero, invalid negative fractional powers, nonfinite suppressed inputs and formerly suppressed overflow stay zero. Outside-region overflow remains Infinity (`1e308/.0001`; `pow(.0001,-100)`). Exact `.00001` threshold and `.0001` ordinary controls agree.

**Deferred:** direct zero division, pow(0,-1), negative fractional pow domains and suppressed overflow are not rolled back to original behavior. Original division assembly directly uses fdiv, while pow/_powop binds host pow; those paths have no current small-input guard. `pow(-.000001,-.5)` is invalid; preserving current zero is a policy boundary. `pow(1e-300,-2)` overflows in double and stays zero. Original x87 precision/rounding versus Android double/subnormal behavior is not established by host tolerance checks. No bit-exact original evaluator promise is made.

**Operation implications:** only the old suppressed branch gains arithmetic: one division or pow plus finite checks. The ordinary branch retains its prior operations. No allocations, repeated argument evaluation, extra vertex/draw/pass or persistent state is added. Recovered values may increase authored loop/draw/control workloads downstream; current resource limits must remain in place. No measured speed claim is made.

## I04 proposal

`I04-proposal.patch` shares one small helper across % and %=, preserving the real compiler's aliases. For finite operands with magnitude strictly below 2^31, return the absolute value of the existing integer remainder. This matches original fabs→fistp signed32→unsigned div under round-toward-zero for that bounded domain. Apply fabs after conversion of the remainder to floating point; no integer abs(INT_MIN) is used.

For finite defined operands outside that bounded source domain, retain the existing widened signed remainder. Checks before casting additionally return zero for NaN, Infinity or out-of-range float→integer conversion. Explicitly return zero for signed MIN/-1 before executing `%`. Those protective zero choices are new definitions for previously undefined C paths, **not claimed original parity**. They should be reviewed as part of integration.

Executed witnesses: every ±5/±2 combination yields +1 in the bounded path; -4%2 stays 0; -5.9%2.9 yields +1 with truncation. Assignment, intrinsic aliases and same-variable alias controls pass. Wider -4294967297%2 remains -1; -5%4294967296 remains -5; INT64_MIN%3 remains -2. INT64_MIN%-1 and invalid casts return 0 without sanitizer violations.

**Deferred:** no conversion to original unchecked unsigned32 casting is proposed for wide or nonfinite values. Original fabs(2147483648) cannot fit signed32 fistp and follows CPU/FPU exceptional conversion semantics; current widened integer -2147483648%3 is defined and yields -2. A hypothetical original masked-fistp integer-indefinite bit pattern is not a verified Windows runtime oracle. Signed repair beyond the bounded domain, alternative invalid-input policies, float evaluator parity and original FPU flags/precision remain separate decisions. Current host tests use production double/int64 only.

**Operation implications:** each remainder operation adds finite/range checks, a signed-minimum guard and bounded-domain fabs checks. It retains one integer remainder and one argument evaluation each. No allocations or graphics work are added. No cost measurement was performed.

## Candidates and finite fixtures

No exact affected original has been confirmed. The handoff's narrow literal inventories contain zero candidates for I03 and I04; this does not exclude dynamic exposure. Research's broader `%` inventory is an exposure inventory, not an affected census.

`390 threx no more warningsce Rumbo Pal Recodo.milk` is a possible I04 witness: shape3 lines698–699 fold positions through x%2 and y%2, with operands derived from gmegabuf/Q. Capture those actual evaluated operands and contributions before treating it as affected. Hash and unchanged lines are recorded in `source-boundaries.json`; no rendering or execution of this original was performed.

`I03-finite-fixture.milk` maps the actual million-valued division/power outputs to two opaque border widths: baseline .02; proposal .1. `I04-finite-fixture.milk` maps q1=-1→green and q1=+1→red. Capture Q values as primary proof. Match a 256×144 authored/output canvas, mesh48×32, fixed declared PCM/time/FPS/progress/seed, zero transitions and Native Standard trails before moving to separately declared Native4K checks. These are newly derived finite fixtures; only scalar expressions were executed here. They are not captured screenshots or original Windows images.

## Integration boundaries

The parent must decide whether to integrate separate ordered TV patches and canonical scalar regressions. Retain all previous TV policies and prepared replay. Requalify Android release arithmetic and downstream finite visual controls before describing user-visible impact. External predictor contracts require corresponding native behavior/version alignment; no predictor source was changed here.
