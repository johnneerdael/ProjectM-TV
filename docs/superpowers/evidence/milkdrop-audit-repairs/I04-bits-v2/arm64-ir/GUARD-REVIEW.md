# Exact ARM64 v2 guard review

Reviewed the captured release IR for both `prjm_eval_func_mod` and `prjm_eval_func_mod_op`. Flags retain `-ffast-math`; no whole-translation-unit finite-math override is added.

For mod, both fptosi operations occur only in block40, reached from block36 after integer magnitude/range/sign checks. Numerator magnitudes above the 2^63 representation (including infinity/NaN) reject at entry; denominator infinity/NaN rejects at entry and its cast range/sign rejects on the branches28/30/34/36. Exactly negative 2^63 remains admitted. Division-by-zero rejection in40 and signed-minimum/-1 rejection in44 precede srem in48.

For mod_op, corresponding cast/divisor/minimum/remainder blocks are38/38/42/46, with the input checks on26/28/32/34. Argument evaluation remains ordered before input loads. The real evaluator preservation tests cover aliases and side effects separately.

Clang represents the input sign-bit clearing as `llvm.fabs.f64` without fast flags, followed by bitcasts and integer comparisons. Do not describe this as literally containing no floating intrinsic. The sign clearing does not justify assuming finite inputs; no fptosi/srem executes before the guards. Output fabs follows the safe integer remainder and is selected only for magnitudes below2^31. Wider signed behavior remains.

Runtime evidence separately passes76 remainder controls and12 preservation controls on actual ARM64; all20 boundary observations match baseline. This review is bounded to the recorded compiler/source and is not a cross-platform or Native-cost acceptance.
