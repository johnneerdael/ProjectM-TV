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

## First hardware matrix

The corrected emulator reports the Apple M4 Pro renderer. Each of the **48 jobs**
renders all 480 frames, with eight native captures. Four presets run at
1182×665, 2364×1330 and 3840×2160 on baseline29/candidate30, twice each.
All jobs succeed, all repeats are byte-identical, and near-reference candidate
outputs match the baseline. The near-reference profile retains the core's
normal 1024×768 reference setting; it is not the exact no-reference classic
ground truth required for final spec acceptance.

| Preset | Size | 12 s image MAE before→after | Candidate / near-reference luma |
| --- | --- | --- | --- |
| Royal 191 | 1330 | 0.3793→0.0212 | 0.332 |
| Royal 191 | 2160 | 0.3986→0.0214 | 0.329 |
| Acid Mandala | 1330 | 0.0710→0.0743 | 0.860 |
| Acid Mandala | 2160 | 0.0754→0.0562 | 0.880 |
| Fed quadratrail | 1330 | 0.0042→0.0018 | 0.771 |
| Fed quadratrail | 2160 | 0.0020→0.0027 | 0.521 |
| I Like Cartoon | 1330 | 0.1917→0.2341 | 0.902 |
| I Like Cartoon | 2160 | 0.1986→0.1896 | 0.932 |

`first-matrix-analysis.json` retains both windows and brightness, centre RGB,
saturation and sharpness separately. `first-matrix-jobs.jsonl.gz` retains exact
job/result identities. The four cases are deliberately difficult; they do not
estimate a corpus-wide failure rate. These results remain mixed and do not
justify merge acceptance.

## Overwrite-state regression

An independent real-driver component test exposed inherited blending in the
diffusion pass: a uniform RGBA source with red=128 and alpha=128 rendered red=64
instead of 128. The filter must overwrite its target, not multiply source
colour by alpha again or retain prior target contents. Explicitly disabling
blending makes the regression pass; the full host suite is **190/190**.
`alpha-red.txt` and `alpha-green-suite.txt` preserve RED→GREEN evidence.

This is a renderer contract correction. The production main surfaces use RGBA colour attachments; blur levels use RGB.
This is not evidence that the Acid Mandala or Fed brightness regressions are
fixed. New actual-core comparisons must verify its effect separately.
