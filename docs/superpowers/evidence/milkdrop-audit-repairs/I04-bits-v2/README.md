# I04 bits-v2: separate surgical qualification

This is the frozen all-integer refinement, separate from the already executed v1 and finite-only-flag alternatives. No compilation, IR capture, GPU/device or Git operation was run by the preparing agent. Do not overwrite delivered versions while root workers run.

V2 patch SHA256: `9dd800abf251780e26718c8abdeab2dff4e62b2fff34447323edd136cf0693f8`.
Candidate TreeFunctions.c SHA256: `6fab98928753f7393248993b95ff51aee15fb822136e6296ecebfedc0f823af2`.
Read-only frozen v1 engine TreeFunctions.c: `5fa8431278690af12b8d83f221cd2cc3eebe9cdd2fdc20abe79a9ed237e6adcd`. That v1 contains floating range predicates, not v2's integer-limit masks. Identify each built worker from its actual source hash; a preparation directory name alone is insufficient.

## Historical evidence and refinement

Historical Apple clang17 fast-math+UBSan passed64/64 I04 bit controls; I03 bit recovery failed24/89 and is excluded. Historical NDKclang18 O3/fast-math IR retains integer input masks, cast-range and minimum/-1 guards before casts/remainder in double and supplemental float. This history justifies independent qualification; it does not certify the current76 controls, both ABIs or this refined source.

The historical/v1 helper combines bit classification with floating range comparisons. Its emitted NDK IR may speculatively calculate floating comparisons before final rejection while the masks still protect fptosi. That is a cast-safety proof in that pinned output, not a strict no-input-FP-operation proof. V2 uses only integer magnitude/sign predicates for finite, cast-range and original bounded-domain checks. No input fabs/comparison/arithmetic is written before casts. The original bounded threshold2^31 and current cast limits2^31/2^63 are exact IEEE bit encodings. Positive cast limit is rejected, exact negative signed minimum is allowed, and minimum/-1 is guarded before srem. fabs is applied only to the finite converted remainder in the bounded original domain.

The memcpy representation copy avoids strict aliasing. Supported formats/size/radix/mantissa/exponent are asserted; matching floating/integer byte layout is an explicit pinned-target assumption. This is not a universal portability or MSVC qualification. Operand-producing expressions still follow existing evaluator rules before the helper receives values; this does not repair every upstream nonfinite operation.

## Scope preserved

Only TreeFunctions.c headers/private remainder helper and its two call sites change. Evaluator CMake and release flags are untouched. Current27 div/div_op/pow/pow_op/invsqrt bodies remain exact baseline. No I03 finite recovery or wider NaN guard restoration is requested. Existing outside-region compiler policy remains authoritative, including nonfinite behavior compiled under fast-math. This avoids attributing the failed combined tiny/ordinary pow cost to an unrelated I04-only mechanism, but requires its own cost proof.

## Real-evaluator controls and twenty-boundary contract

`eel_i04_bits_test.cpp`, `CMakeLists.txt` and `compare_boundaries.py` are identical to the delivered bits test/comparator source. Direct assertions cover76 I04 cases plus12 aliases/preservation cases. All20 boundary cases emit actual q/a/b observations;11 unaffected cases also retain direct expectations. Nine power/invsqrt NaN-policy cases are OBSERVE rows, because demanding finite-flag restoration zeros would silently widen this bit-only candidate. Baseline and candidate must use the same exact compiler/options.

An isolated boundary test returning zero is NOT the complete20-case preservation gate. Root must run the comparator on baseline and candidate logs; it requires all20 case sets and matching q/a/b results/classes, including sign of infinity/zero. NaN payload equality is not certified. No old20/20 finite-policy result substitutes for this comparison.

## Root-owned integration commands

Start from a root-owned full current27 engine with ONLY the v2 patch applied. Do not apply on top of v1 or the finite-only alternative, and do not mutate frozen workers. Use a new build directory:

```sh
cmake -S build/audit/arithmetic-proposal/i04-only/bits-v2 -B build/audit/arithmetic-proposal/i04-only/bits-v2/host -G Ninja -DREPO_ROOT="$PWD" -DPROJECTM_SOURCE=/absolute/path/to/frozen/v2/full/engine -DCMAKE_BUILD_TYPE=RelWithDebInfo -DSANITIZERS=OFF -DENABLE_FAST_MATH=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build/audit/arithmetic-proposal/i04-only/bits-v2/host --target eel-i04-bits-controls -j 8
python3 build/audit/arithmetic-proposal/verify_compile_scope.py build/audit/arithmetic-proposal/i04-only/bits-v2/host/compile_commands.json --baseline
build/audit/arithmetic-proposal/i04-only/bits-v2/host/eel-i04-bits-controls I04
build/audit/arithmetic-proposal/i04-only/bits-v2/host/eel-i04-bits-controls aliases
build/audit/arithmetic-proposal/i04-only/bits-v2/host/eel-i04-bits-controls boundaries > build/audit/arithmetic-proposal/i04-only/bits-v2/v2-boundaries.log
python3 build/audit/arithmetic-proposal/i04-only/bits-v2/compare_boundaries.py /absolute/path/to/same-compiler/current27-baseline-boundaries.log build/audit/arithmetic-proposal/i04-only/bits-v2/v2-boundaries.log
```

The compile-scope helper's `--baseline` option here means require the unmodified evaluator fast-math flags and no finite-only override; the source itself is the v2 candidate. C++ assertion flags remain test-only strict math. Android integration uses the established NDK27.3 Android21/c++_static/GLES discovery options and the same target. Root owns both ABI builds/runtime and scoped device operations. Supplementary float format proof is separate from the production double controls.

## Exact emitted-code safeguard gate

The helper defaults to printing reviewable argv, and executes only with root's explicit option:

```sh
python3 build/audit/arithmetic-proposal/i04-only/bits-v2/capture_release_ir.py build/audit/arithmetic-proposal/i04-only/bits-v2/host/compile_commands.json build/audit/arithmetic-proposal/i04-only/bits-v2/host-ir --execute
```

Run separately for actual pinned NDK command files. It preserves actual source/compiler/flags, emits LLVM IR and assembly into new paths and records hashes. It refuses finite-only/strict-math evaluator flags. This is a prepared helper, not executed evidence.

Review both mod/mod_op: integer input sign/magnitude checks must reject nonfinite/out-of-range representations before fptosi; valid negative signed minimum must remain admitted; zero divisor and minimum/-1 checks must dominate srem; bounded positivity must remain restricted to magnitudes below2^31. An optimizer may combine redundant finite tests into stronger integer cast-range predicates; verify equivalent rejection/control dominance rather than counting only a particular mask spelling. No input fcmp/fabs should precede validated casts in v2's path. A lost guard, poison-producing speculative cast, unqualified intrinsic or changed outside policy is a failure; do not conceal it with expected-value tolerances.

After scalar/IR/ABI proof, freeze source/APK/native/preset/PCM/compiler/flags and rerun isolated runtime remainder/ordinary/suppressed-power cost fixtures. Keep constructor/source counters out of timed roles. No acceptance, performance, Windows parity, whole-corpus or shipping-hidden-state claim follows from this preparation.
