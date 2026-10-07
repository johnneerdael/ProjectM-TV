# Upstream master rebase validation evidence

Current status: synchronized with main through #49 and **all release-bound validation gates passed** on 2026-10-07. The authoritative baseline is ProjectM-TV **v2.3.15**, source `43023889`, unchanged AAR SHA256 `fa4bdd657a592b41eeef7d75c82982bf1fecf5404b99aba8ebba5c56f6a91327`. The candidate renderer is `c3872be3`, with nine patches against upstream `6f6480746`. All 509 fixed-seed preset/profile comparisons (2,036 source runs), all 509 unchanged-AAR runtime runs and all 48 image-proof replays pass. Every full-resolution RGB frame 0–479 matches across both source engines and repeats. The task-owned API34 ARM64 host-GPU emulator reports Apple M4 Pro/GLES3.0. See the [complete evidence and authentic figures](fidelity-final/README.md), [frozen workflow](random-100/README.md) and [required regression inventory](patch-regressions/README.md). Final-head Codex review, required CI, merge and publication remain separate repository gates.

The physical-TV matrix below is **historical v2.3.11 evidence**, retained with its original identities. The reset-only midgit rerun subsequently matched all 32 sampled captures at1080p/4K in two repeats, confirming the private RNG initialization cause. It does not certify the resumed v2.3.15/random-plus-regressions gate. Final CI, final-head Codex review, merge and publication remain pending.

## Historical released baseline for the TV matrix

Historical verified release: ProjectM TV v2.3.11, source `b1bb994d`, published core AAR SHA256 `3bc37560a87000ec7ac446895fee8ad09e93b5c83a601014b5fc396bd1f3e6d6`. Downloaded unchanged and verified against release checksums and GitHub asset digest. The source baseline below contains all 44 ProjectM TV patches and is not stock libprojectM, but instrumentation makes its binary distinct from the published AAR. Separate unchanged-AAR workers preserve all 9,686 packaged assets and their ARMv7 native library bytes; baseline and candidate each passed a 480-frame Oscilloscope runtime control with preset, GL and cleanup checks. Their real clock/RNG prevents deterministic image certification. The [44-patch/all-preset source impact inventory](patch-impact/README.md) covers all 9,606 presets without visual certification.

## Protocol and scope

AM6, Android 9, ARMv7 userspace, Mali-G52 / OpenGL ES 3.2. The pinned 4.1.7 baseline is ProjectM TV `b1bb994d` with 44 patches; the candidate worker is `9f131997` with upstream master `6f6480746`, evaluator `22fb0cfd` and three consolidated patches. These are instrumented actual-core AARs, not byte-identical production APKs. Each worker APK embeds its exact recorded AAR bytes and the same 9,606-preset asset bundle.

Four unchanged presets × two render sizes × two engines × two repeat runs: 32 jobs. Every job renders 480 frames with matching synthetic PCM, seed 12345, frame/30 logical clock, mesh 48×32, line reference 1024×768 and Standard trails. Eight captures per job are fixed at frames 120, 150, 180, 210, 239, 300, 390 and 479. Native trails is inactive at 1080p and uses an active 1280×720 canvas at 4K, as required by the production size gate.

The [comparison runner](compare_actual_core.py) freezes the entry script and imported helper hashes, exact worker/preset/PCM identities and the device fingerprint. It checks the captured Android user and wakefulness before each install/render, never wakes the TV, acquires the shared device-session lock and restores the original debug preset after each job. [Guard tests](test_comparison_guards.py) cover sleep/user changes and helper mutations.

## Verified results

All 32 manifests, 256 PNG hashes and decoded RGB hashes were reverified from disk. All 15,360 per-frame GL and preset checks passed; each job confirms one eligible preset, one switch, core release and EGL destruction. All 16 same-engine repeat groups match exactly at every capture. These controls do not establish whole-corpus equivalence or compatibility on a GLES 3.0-only physical driver.

| Preset | Size | Matching old/new capture hashes | Maximum sampled RGB MAE (0–255 byte scale) |
|---|---|---:|---:|
| Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk | 1080p | 0/8 | 2.659 |
| Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk | 4k | 0/8 | 4.453 |
| midgitstraights of majillaen - featy sweet.milk | 1080p | 0/8 | 34.999 |
| midgitstraights of majillaen - featy sweet.milk | 4k | 0/8 | 36.367 |
| Jc - Geometry 101.milk | 1080p | 7/8 | 0.008 |
| Jc - Geometry 101.milk | 4k | 7/8 | 0.003 |
| Mig_Oscilloscope022 b.milk | 1080p | 8/8 | 0.000 |
| Mig_Oscilloscope022 b.milk | 4k | 8/8 | 0.000 |

## Historical interpretation and subsequent resolution

The historical cross-role results above used different private shader RNG initialization. The old worker reset the stream from seed 12345 in its constructor; the new constructor no longer did so, and the shared LabBridge omitted the reset. A compiled actual-bridge regression established and corrected that ordering. A reset-only midgit intervention subsequently matched all 32 selected captures at 1080p/4K in two repeats. Historical artifacts and values above remain unchanged.

The final release-bound API34 validation supersedes the open fidelity investigation: Midgit, Acid Mandala, Geometry 101, Oscilloscope and every other required preset/profile case match all 480 RGB frames in both source repeats. A distinct random-texture discrepancy required production patch 0009 to restore exact legacy premultiplication; its causal before/after proof remains separately retained. The user waived physical-TV revalidation for this migration. Neither the old TV measurements nor the final emulator equality establish a causal performance change or universal device coverage.

Serialized engine timings measure onDrawFrame plus glFinish over the 360 post-warm-up frames, excluding captures/PNG transport. They are physical-TV engine costs, not application FPS; the historical worker text still says emulator. Repeat timings vary substantially (for example, Acid 4K baseline means 58.2/106.0 ms and candidate means 218.9/58.8 ms), so no causal speedup or slowdown is inferred. PSS does not account for all GPU allocation.

Live production-profile smoke separately rendered Acid Mandala at 1920×1080 at roughly 30 FPS in both builds, with audible Milkbeat playback. The tracks changed between runs; this is not a matched-audio image/performance comparison. The three-line unreleased-master/pin label fits the settings panel.

The canonical protocol and verified summary are retained in the task build directory under `build/upstream-rebase/tv-frozen-comparison-v3/`. Its protocol digest is `4a725949b1af2c4ea7e50b6ccd53e30d76c489f9620e8174ce3bbda909c3d408`. Raw captures and task-owned binaries remain untracked; historical evidence/producer identities are unchanged.
