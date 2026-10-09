# TreeFunctions.c finite-only override proposal

Preferred scoped candidate: retain the ordinary I03/I04 source proposals and append `-fno-finite-math-only` **only to TreeFunctions.c**, after existing evaluator `-ffast-math`. No custom classification helper or whole-library flag change is needed. Canonical files, devices and Git were not touched.

`../TreeFunctions-finite-source-property.patch` proposes a source COMPILE_OPTIONS property in core's CMake after the projectM subdirectory creates projectM_eval. TARGET_DIRECTORY applies the source property in that target's actual directory scope. [CMake documents this scope mechanism](https://cmake.org/cmake/help/v3.22/command/set_property.html). A standalone configure with the actual bundled CMake3.22.1 and NDK27.3 proves TreeFunctions.c receives `-ffast-math -fno-finite-math-only` in that order while Scanner.c retains only `-ffast-math`; ../cmake-scope/scope-proof.json records generated commands. This fixture proves option scope/order, not a canonical core build.

## Emitted Android release code

Exact Android flags from i12-workers/candidate-native/source are preserved in manifest.json and commands.json. Only TreeFunctions.c adds the final override. NDK IR retains `reassoc nsz arcp contract afn`, removes nnan/ninf, and preserves:

- I03 numerator/exponent and computed-result classification, including overflow/invalid suppression.
- I04 input classification before fptosi, finite range limits and signed-MIN/-1 protection.
- Existing outside-suppressed-region NaN-to-zero guards in pow and pow_op.
- Existing NaN-to-zero guard in invsqrt.

Complete IR/assembly and guard-ir-excerpts.txt are retained. Other evaluator sources keep exact previous flags. This does not disable reassociation, reciprocal transforms, contraction or approximate-function permissions; it withdraws finite-only assumptions in the one file containing these arithmetic guards.

## Scalar execution and boundaries

Apple clang17 fast-math with the source-only override and UBSan/float-cast-overflow: I03 proposal89/89, I04 proposal76/76, and20/20 outside-boundary controls for baseline and both proposals pass. Baseline finite-domain failures remain28/89 for I03 and19/52 for I04;24 unsafe baseline modulo conversions are deliberately skipped. See ../results-fast-math-finite.json and logs. The expanded I04 suite additionally tests exact2^31 exclusion and NaN/Infinity divisors.

Apple raw-fast-math outside-boundary controls also pass20/20 because that compiler preserved these existing guards. This does not conceal the Android difference: baseline NDK -ffast-math removes the existing pow/pow_op and invsqrt NaN guards; the source-only override restores them. Android numeric execution has not been performed here.

**Additional release behavior to review:** `pow(-1,.5)` and power-assignment forms outside the tiny-base region change Android's unguarded NaN result to the source-authored0. `pow(2,NaN)` similarly restores0; `invsqrt(NaN)` restores0. These are explicit protective policies already written in source, not tiny-finite I03 fixes. They must be disclosed and tested as an additional acceptance boundary. Ordinary finite pow(2,3)=8, outside overflow pow(2,1024)=Infinity, division NaN/2=NaN and Infinity/2=Infinity remain declared controls. No new universal invalid-arithmetic normalization is introduced; other unchecked bitwise/loop conversions remain outside scope.

## Parent execution

Binaries: baseline/scalar-controls, I03/scalar-controls, I04/scalar-controls. Invoke baseline with `I03 baseline` or `I04 baseline`; candidates with I03 or I04. Invoke each with `boundaries` to execute the20 outside-region controls. Refreshed original-flags binaries under ../android support the same arguments for comparison; those are negative qualification artifacts and not accepted candidates. Hashes, compiler identity and commands are preserved in each directory's manifest.json.

## Cost and limits

I03 adds one division/pow and classification only within the previously suppressed branch; I04 adds bounded conversion/finite checks per remainder. Restored outside-region pow/invsqrt guards add classification where NDK previously removed it. TreeFunctions.c may lose other finite-only optimizations, although remaining fast-math flags are retained; no runtime timing or whole-corpus equivalence claim is made. Original Windows arithmetic, Android runtime, both-ABI core integration and focused downstream visual evidence remain separate gates.
