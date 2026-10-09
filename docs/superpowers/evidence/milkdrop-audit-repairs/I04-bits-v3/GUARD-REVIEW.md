# V3 exact ARM64 guard review

The recorded source is compiled with final -O3 -ffast-math and no finite-only override. Both mod and mod_op load argument values after ordered evaluation, clear sign bits through non-fast LLVM fabs intrinsics, bitcast to integers and OR magnitudes. Unsigned OR<2^31-representation is sufficient to admit both finite magnitudes below2^31, though some valid pairs (e.g.1 and2) miss that fast path and use the unchanged wide path.

mod32 casts are only in blocks27/30 after entry admission; divisor-zero rejection in27 precedes srem32 in30. Strict magnitude admission excludes signed-minimum, so both srem32 and llvm.abs.i32(poison-on-minimum) are safe. The wide path starts35; finite/range/sign branches35/39/41/45/47 dominate fptosi64 in51. Divisor-zero51 and signed-minimum/-1 rejection55 dominate srem64 in59.

mod_op corresponds to common cast/divisor/remainder blocks25/25/28; wide entry33, casts49, zero49/minimum53, remainder57. No fptosi or srem executes on an unadmitted input. Full existing76 remainder+12alias cases pass on host and actualARM64; all20 baseline boundary observations (9 NaN-policy-sensitive) match. Tests/IR do not imply Native cost acceptance or unverified-platform support.
