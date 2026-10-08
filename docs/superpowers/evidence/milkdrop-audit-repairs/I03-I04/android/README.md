# Android cross-compilation qualification — release guard defect

No device execution was performed. These binaries reproduce the **unsafe raw proposals** under actual release evaluator flags and are evidence artifacts, not accepted candidates.

Metadata: `build/audit/i12-workers/candidate-native/source/core/.cxx/RelWithDebInfo/49z2z644/arm64-v8a/compile_commands.json`. The TreeFunctions.c command targets aarch64 Android API21, NDK27.3.13750724, PRJM_F_SIZE8, RelWithDebInfo -O2 followed by evaluator -O3/-ffast-math. `manifest.json` preserves the original command, complete flags, metadata hash and binary hashes. `commands.json` contains every cross-compile/link invocation; `compiler.txt` identifies the compiler.

`cross_compile_android.py` copies those flags verbatim except source/include/output paths. The scalar observer is deliberately compiled at O2 without fast-math so comparisons remain meaningful. libc++ is linked statically; Android libc/libm remain platform dynamic dependencies. Binaries: `baseline/scalar-controls`, `I03/scalar-controls`, `I04/scalar-controls`.

After staging to a task-owned emulator, invoke baseline as `scalar-controls I03 baseline` and `scalar-controls I04 baseline`; invoke candidates as `scalar-controls I03` and `scalar-controls I04`. Baseline intentionally skips previously undefined modulo casts and MIN/-1. Parent owns device execution; this preparation does not connect to devices.

## Proven emitted-code defect

The Android NDK compiler optimizes differently from Apple clang17. The earlier Apple host tests passing with fast-math do not qualify Android release semantics.

I03: both / and /= retain input-numerator finite checks, but **remove result finite checks**. In `I03/TreeFunctions.ll`, prjm_eval_func_div's suppressed branch `%27 = fdiv fast double %23, %16` flows directly into its result phi/store; no post-division classification remains. The finite overflow control `1e308/.000001` can therefore escape as Infinity instead of required zero. pow/^ and ^= similarly emit `call fast @llvm.pow.f64` and select/store its result without classification. `pow(1e-300,-2)` and `pow(-.000001,-.5)` lose required overflow/invalid suppression.

I04: % and %= **remove both isfinite input checks**. The emitted functions use only four ordered range comparisons before fptosi. NaN makes those comparisons false, reaching an invalid float-to-int conversion. Signed-min/-1 and finite range guards survive. This violates the proposed protective contract.

Full function excerpts are in `guard-ir-excerpts.txt`; full IR and ARM64 assembly are retained for each role. This is an emitted-code finding; candidate Android numeric outputs have not yet been observed.

Do not integrate the raw patches with current release flags. A narrowly scoped evaluator compile-policy correction such as disabling finite-only assumptions needs its own exact-flags compiler/scalar qualification and explicit review of restored general NaN handling. A custom bit-classification helper alone is insufficient evidence: its checks also need qualification against arithmetic marked nnan/ninf. No canonical compiler policy was changed here.
