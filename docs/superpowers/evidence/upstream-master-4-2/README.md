# Upstream master rebase: focused physical-TV validation

Status: rendering checks complete; the material midgit image difference is under investigation. PR #46 remains a draft. Final CI, final-head Codex review, merge and publication are pending.

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

Oscilloscope captures match across engines at all selected frames. Geometry 101 matches at seven of eight captures per size; the remaining differences are small. Acid Mandala has localized differences that grow with feedback; the 1080p pilot analysis found no source support for blaming the per-pixel coordinate fix in this preset, and precision/rasterization remains an unproven explanation. Midgit differs materially (maximum sampled RGB MAE about 35–36 bytes/channel), so texture selection/decoding and blur/rendering behavior require source-grounded investigation before readiness.

Serialized engine timings measure onDrawFrame plus glFinish over the 360 post-warm-up frames, excluding captures/PNG transport. They are physical-TV engine costs, not application FPS; the historical worker text still says emulator. Repeat timings vary substantially (for example, Acid 4K baseline means 58.2/106.0 ms and candidate means 218.9/58.8 ms), so no causal speedup or slowdown is inferred. PSS does not account for all GPU allocation.

Live production-profile smoke separately rendered Acid Mandala at 1920×1080 at roughly 30 FPS in both builds, with audible Milkbeat playback. The tracks changed between runs; this is not a matched-audio image/performance comparison. The three-line unreleased-master/pin label fits the settings panel.

The canonical protocol and verified summary are retained in the task build directory under `build/upstream-rebase/tv-frozen-comparison-v3/`. Its protocol digest is `4a725949b1af2c4ea7e50b6ccd53e30d76c489f9620e8174ce3bbda909c3d408`. Raw captures and task-owned binaries remain untracked; historical evidence/producer identities are unchanged.
