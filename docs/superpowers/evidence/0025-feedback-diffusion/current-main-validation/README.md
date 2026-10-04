# Current merged renderer versus native diffusion

The runtime pair uses actual `projectm-tv:core` Android AARs, not a direct
libprojectM worker. Baseline source is merged PR #23, `0625587f`, with patches
0001–0029. Candidate source is `5c8b0a27`, with those exact prerequisites plus
0030. Both compile and link the three production core native units and use the
same private clock/RNG observer. `actual-aar-proof.json` verifies identical
core ELF bytes inside each AAR and its corresponding instrumentation APK.
`diffusion-compile-proof.json` records the candidate's actual compiled
`FeedbackDiffusion.cpp` unit.

The first bounded control is Royal Mashup 191 at 2364×1330: four successful
fresh-process JNI jobs, each rendering 480 frames and retaining sixteen native
captures. Both baseline and candidate repeat with identical selected-frame
hashes. The emulator initially selected SwiftShader; these results are labelled
software-renderer diagnostics and are separate from the corpus owner's Apple
M4 Pro renderer. No authored-fidelity or hardware-performance verdict follows.

`software-pilot-jobs.jsonl.gz`, `software-pilot-proof.json` and the immutable
`software-pilot-protocol.json` preserve exact identities, raw checksums and
results. Lossless raw backup lives at
`/Users/jneerdael/Scripts/Projectm-TV-recovery-2026-10-04/current-main-validation/software-pilot-raw.zip`.
Its SHA256 is `3c22c4355c495195bb0631cfc764a469ac2bda282179be7dc8d85d207559d299`.
The backup contains all four jobs and 64 native captures, not only summaries.

Independent test verification: **189 native unit tests pass** after all thirty
patches are physically present in the isolated source tree. macOS's existing
host-only invalidation shim is used because its OpenGL headers lack that
discard hint; it is not used in Android core builds or runtime rendering.
The JVM command succeeds with unchanged tests reported up-to-date.

Setup correction: the first standalone `git apply` invocation inherited the
enclosing worktree and skipped the scratch-path diffusion hunk. It was repeated
with `GIT_CEILING_DIRECTORIES`, and actual diffusion source/test inclusion was
asserted before the 189-test run. The successful AAR builds use isolated-source
patch application and compile-proof checks, independently of that host setup.

The owned targeted emulator is `emulator-5582`. Its GPU configuration was
corrected to explicit host graphics, with Vulkan disabled for native host
OpenGL, and it was restarted only after the first four jobs completed. The
corpus owner's emulator-5580, worktree and processes remain untouched.
Further hardware-renderer controls and native-4K comparisons are in progress.
