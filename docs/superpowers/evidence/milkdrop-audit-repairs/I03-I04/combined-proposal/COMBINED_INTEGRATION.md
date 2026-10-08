# I03/I04 combined integration candidate

Preparation only. No canonical engine, patch series, CMake, existing test, helper, Git, build, GPU or device operation was changed or run by the preparing agent. Historical Android 89/89 I03, 76/76 I04 and 20/20 boundary artifacts remain frozen. They qualify isolated candidates and the source-option policy, not this newly combined ordered patch.

## Reviewable deliverables

- `combined-I03-I04-finite-guards.patch`: one next-number-ready engine patch against the actual ac3 current27 source. It edits only vendored evaluator `TreeFunctions.c` and the evaluator's own `CMakeLists.txt`. Root assigns the next canonical number after proof; no routine version bump.
- `eel_arithmetic_test.cpp`: real compiler/evaluator API controls, 89 I03 +76 I04 +20 boundaries +13 new integrated aliases/side-effect/mixed-operation cases. This file is prepared for canonical native-test placement after root review.
- `canonical-target.cmake`: proposed target/CTest fragment for that placement.
- `integration/CMakeLists.txt`: ignored wrapper linking the actual full projectM/evaluator from a root-owned patched source checkout. It does not compile copied I03/I04 evaluator trees or substitute arithmetic functions.
- `verify_compile_scope.py`: inspect actual generated commands and require the finite-only override after fast-math for exactly TreeFunctions.c.
- `combined-preparation-identity.json` and `combined-baseline-flag-evidence.json`: exact base/candidate text and existing frozen compiler identities.

## Arithmetic scope

I03 recovers finite division and negative-power results only inside the current `fabs(value)<COMPARE_CLOSEFACTOR` suppressed region. Zero/negative-zero divisors, zero negative-power bases, invalid negative fractional powers and overflow there remain zero. Preserve argument invocation order, live variable pointers, assignment storage and aliases. Ordinary branches retain their source arithmetic. Recovering a value can alter authored loop/draw/control workloads downstream; existing resource limits must remain. No speed or whole-corpus claim follows.

I04 returns absolute integer remainder only when both finite operand magnitudes are strictly below2^31. It keeps the current widened signed result outside that original bounded source domain. Guard invalid/out-of-range casts before conversion and signed minimum/-1 before executing remainder. New zero definitions for previously undefined C paths are protective policy, not original Windows parity. The helper handles float/int32 and double/int64 formats, but the prepared canonical production test explicitly requires the shipping double format; supplemental float qualification remains its separately identified existing packet.

## Explicit compiler and wider nonfinite scope

TreeFunctions.c receives `-fno-finite-math-only` after existing evaluator flags for Clang, AppleClang and GNU, in the same directory defining projectM_eval. All other evaluator sources keep their flags. Release/RelWithDebInfo Clang keeps O3/fast-math; GNU keeps its selected Ofast/O3 policy. Debug receives the harmless finite-only option. No pragma/bit classifier, app-only source property, platform-specific `/fp` policy or blanket strict-math setting is added.

The override applies to this whole translation unit. In addition to new repair guards, it restores the pre-existing source-authored `pow/pow_op isnan(result)?0:result` and `invsqrt isnan(value)?0:value` guards that Android fast-math removed. Outside tiny-base scope, invalid fractional power and NaN exponent now resolve to zero; invsqrt(NaN) resolves to zero. That is an explicit additional behavior. It is not merely I03 finite recovery, not a generic nonfinite clamp and not original parity. Outside power overflow remains Infinity; outside division NaN/Infinity still propagates in the declared20 controls. Other nonfinite optimization differences across the TU are not comprehensively certified by these examples.

MSVC is excluded from the override; its fast-math behavior remains unqualified, not declared safe. Apple/Android isolated options have historical evidence; GNU support is proposed but not newly executed here. External system evaluator binaries do not inherit vendored CMake policy. Renderer positive GLSL powers, transported nonfinite/authored equation values, JNI settings and all Native styles/replay/ownership remain untouched.

## Real control behavior

Variables a/b/q are registered through the real evaluator before compilation; runtime values are assigned through actual pointers. The previous89/76/20 case definitions are preserved in the new source. The13 new cases independently assert q and a/b storage, including each operand side effect exactly once, RHS mutation of the previous argument/lhs alias, pow argument effects and combined remainder/division expressions. They do not test a copied numeric implementation. The source links production mutex callbacks from projectM rather than defining local no-op evaluator callbacks.

Baseline I04 execution must use the `baseline` argument to skip24 unsafe cast/minimum-overflow cases. Baseline failures are expected for the repaired math; do not execute those undefined paths merely to produce RED. C++ assertion code receives its own `-fno-fast-math` so NaN/Infinity expectations are not optimized away; that test-only option does not change evaluator/compiler objects. The twenty boundary controls are mandatory evidence of restored outside-region guards and retained overflow/ordinary behavior, not optional checks hidden in release prose.

## Root-owned host integration proof

Provide a root-owned full patched projectM source checkout derived from current27 and apply the combined patch there. Do not mutate the frozen retained worker checkout or execute `prepare.py/prepare_safe.py` over historical evidence. The wrapper must consume the actual engine's vendored evaluator. Replace the source placeholder with that concrete candidate path:

```sh
cmake -S build/audit/arithmetic-proposal/integration -B build/audit/arithmetic-proposal/integrated-host -G Ninja -DREPO_ROOT="$PWD" -DPROJECTM_SOURCE=/absolute/path/to/root-owned/full/candidate/engine -DCMAKE_BUILD_TYPE=RelWithDebInfo -DSANITIZERS=OFF -DENABLE_FAST_MATH=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build/audit/arithmetic-proposal/integrated-host --target eel-arithmetic-controls -j 8
python3 build/audit/arithmetic-proposal/verify_compile_scope.py build/audit/arithmetic-proposal/integrated-host/compile_commands.json
build/audit/arithmetic-proposal/integrated-host/eel-arithmetic-controls all
ctest --test-dir build/audit/arithmetic-proposal/integrated-host -R '^eel-arithmetic-' --output-on-failure
```

The target calls no GL or renderer API; CMake links the actual projectM library and its evaluator. A sanitizer build is a separate directory with SANITIZERS=ON; run the same four families with ASAN_OPTIONS=detect_leaks=0. The controls require production double format8. No tests were run during this preparation.

Configure an original27 source baseline in a different build directory, inspect flags with `verify_compile_scope.py ... --baseline`, then run `eel-arithmetic-controls I03 baseline`, `I04 baseline`, `boundaries` and `aliases`; retain failure logs and compiler identities. Baseline math/guard failures are observations about that concrete compiler policy, not Windows x87 rendering proof.

## Root-owned Android integration proof

Use the same full candidate engine, NDK27.3.13750724 and an explicit Android GLES discovery target:

```sh
cmake -S build/audit/arithmetic-proposal/integration -B build/audit/arithmetic-proposal/integrated-arm64 -G Ninja -DCMAKE_TOOLCHAIN_FILE=/Users/jneerdael/Library/Android/sdk/ndk/27.3.13750724/build/cmake/android.toolchain.cmake -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android21 -DANDROID_STL=c++_static -DREPO_ROOT="$PWD" -DPROJECTM_SOURCE=/absolute/path/to/root-owned/full/candidate/engine -DGL_LIBS='-lEGL -lGLESv3 -llog' -DCMAKE_BUILD_TYPE=RelWithDebInfo -DSANITIZERS=OFF -DENABLE_FAST_MATH=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build/audit/arithmetic-proposal/integrated-arm64 --target eel-arithmetic-controls -j 8
python3 build/audit/arithmetic-proposal/verify_compile_scope.py build/audit/arithmetic-proposal/integrated-arm64/compile_commands.json
```

Root owns scoped push/run on its task device after hashing executable/source/patch/compiler/commands. Use an owned diagnostic directory and run all four groups; no shipping export or APK change is needed for scalar execution. This is a prepared integration route, not a claim that Android CMake/link/runtime succeeded. If linker/parser regeneration issues arise, resolve within the root-owned full engine/harness; do not replace the real evaluator with a copied standalone tree and reuse old results.

## Gates before canonical adoption

Require combined198-case host/ARM execution, actual per-source flags, guarded emitted IR/assembly under release options and all relevant existing native/JVM controls. Recheck bounded finite visual witnesses on final engine/AAR identity as separate source/JNI roles, preserving previous replay/resource controls. Align predictor/native versioned contracts if behavior is adopted. Root reviews restored guards and undefined-domain policy explicitly before acceptance. Existing frozen results, patch-application preparation and this source packet are not acceptance, performance or affected-preset evidence.
