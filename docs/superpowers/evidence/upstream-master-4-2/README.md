# Upstream master rebase: focused physical-TV validation

Status: four-witness instrumented source checks completed; the material midgit image difference is under investigation. The user's latest completion gate requires at least 100 randomly chosen presets with the same fixed seed and zero pixel changes, using the verified released ProjectM TV source baseline alongside unchanged-AAR runtime checks. The sample will be frozen with selection seed 12345 and render seed 12345; failures cannot be replaced. Midgit remains an additional required regression witness. These preliminary controls do not satisfy that gate. PR #46 remains a draft. Final CI, final-head Codex review, merge and publication are pending.

## Authoritative released baseline

Latest verified release: ProjectM TV v2.3.11, source `b1bb994d`, published core AAR SHA256 `3bc37560a87000ec7ac446895fee8ad09e93b5c83a601014b5fc396bd1f3e6d6`. Downloaded unchanged and verified against release checksums and GitHub asset digest. The source baseline below contains all 44 ProjectM TV patches and is not stock libprojectM, but instrumentation makes its binary distinct from the published AAR. Separate unchanged-AAR workers preserve all 9,686 packaged assets and their ARMv7 native library bytes; baseline and candidate each passed a 480-frame Oscilloscope runtime control with preset, GL and cleanup checks. Their real clock/RNG prevents deterministic image certification. The [44-patch/all-preset source impact inventory](patch-impact/README.md) covers all 9,606 presets without visual certification.

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

## Interpretation and open investigation

Subsequent harness investigation found that the old worker resets its private shader RNG from seed 12345 in the ProjectM constructor, while the new worker's constructor no longer does so. The shared LabBridge also omitted that reset, so the new worker used the fallback shader seed. This makes the matrix's cross-role results unsuitable for judging matched-seed fidelity. The bridge now resets the shader stream after configuring the seed; a regression compiling the actual bridge and hook fails before this correction and passes afterward. Old artifacts and captures remain preserved. Corrected, separately identified TV reruns are pending; the harness correction alone does not prove that all pixel differences disappear.

Oscilloscope captures match across engines at all selected frames. Geometry 101 matches at seven of eight captures per size; the remaining differences are small. Acid Mandala has localized differences that grow with feedback; the 1080p pilot analysis found no source support for blaming the per-pixel coordinate fix in this preset, and precision/rasterization remains an unproven explanation. Midgit differs materially (maximum sampled RGB MAE about 35–36 bytes/channel), so texture selection/decoding and blur/rendering behavior require source-grounded investigation before readiness.

Serialized engine timings measure onDrawFrame plus glFinish over the 360 post-warm-up frames, excluding captures/PNG transport. They are physical-TV engine costs, not application FPS; the historical worker text still says emulator. Repeat timings vary substantially (for example, Acid 4K baseline means 58.2/106.0 ms and candidate means 218.9/58.8 ms), so no causal speedup or slowdown is inferred. PSS does not account for all GPU allocation.

Live production-profile smoke separately rendered Acid Mandala at 1920×1080 at roughly 30 FPS in both builds, with audible Milkbeat playback. The tracks changed between runs; this is not a matched-audio image/performance comparison. The three-line unreleased-master/pin label fits the settings panel.

The canonical protocol and verified summary are retained in the task build directory under `build/upstream-rebase/tv-frozen-comparison-v3/`. Its protocol digest is `4a725949b1af2c4ea7e50b6ccd53e30d76c489f9620e8174ce3bbda909c3d408`. Raw captures and task-owned binaries remain untracked; historical evidence/producer identities are unchanged.
