# Compiled point-sampler feedback correction

Production patch0030 now uses the raw previous flip for nearest-filtered warp descriptors and the compensated texture for bilinear descriptors. Input placement P1 is selected only with active compensation and compiled point-main descriptors; other warps retain the existing hybrid/P2 path. The descriptor flag is cached at shader initialization and may conservatively include optimized-away helper reads.

Packed-state and mixed-routing renderer tests failed before this change and passed afterwards. The complete native suite passes193 tests. Physical application and reversal against baseline29 passed, and all15 changed sources match the compiled candidate source. See `production-patch-proof.json`. These are host component/source checks, not Android-core fidelity or physical-TV cost results.

Patch-context blank lines retain their required leading space. `git -c core.whitespace=-blank-at-eol diff --check` passes; source whitespace should be checked on the applied tree.

Prior broad64 measurements describe790aaa24, not this correction. A new actual-core Android AAR and matched candidate epoch must establish its runtime results.
