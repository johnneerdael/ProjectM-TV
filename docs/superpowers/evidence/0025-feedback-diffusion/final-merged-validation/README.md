# Final merged-renderer checkpoint

This records the **pre-dual-AAR-policy** renderer at `0e3f948e8cf0244b1f27c846bcb5b8b9fc3a26a0`. The user accepted a bounded research checkpoint with separate capped and Native core artifacts. This evidence does not validate the later policy implementation, promise universal picture fidelity, or establish a TV performance gain.

## Source and protocol

| Role | Source | Ordered patches | ARM64 ELF SHA256 |
|---|---|---:|---|
| Baseline | `f435dd7c58ea1f16d9d182ecfc5632b77f5b6f98` | 35 | `3de97d4ef16c261df6b514ce23bd8b0501c8b958dcfe3a814e742ce2f1b151db` |
| Final merged renderer | `0e3f948e8cf0244b1f27c846bcb5b8b9fc3a26a0` | 36 | `a5338e329f71dd1154adf9f0dc3da7185882f3de46ea1803016aaa7a92611285` |
| Classic reference | Baseline35 with one private line-reference setter changed to `0,0` | 35 | `73e3d972d22414679c2e1592499aa843864ede3aed164e3b5e21378eebc7233c` |

The workers call production core JNI through instrumented actual-core APKs/AARs. Their private logical clock/RNG makes comparisons reproducible; these are not shipping bytes or a claim of production RNG parity. APK/AAR ELF identities were checked. The final APK SHA256 is `aed73b16568f6ec159d7d1f450f1b9996798ea8b7877a4c03d71faf75602bdc6`; its AAR SHA256 is `9ceac11905d3dd73acf32495454d1aaede8fc0a5d3f7a0ca25593c31852eb985`.

The fixed64 selection was sampled from 5,114 successful, source-hash-verified receipts in a **partial older baseline24** corpus, seed 20261004. Those receipts selected coverage only; their pixels did not enter primary comparisons. Lexical source groups guided sampling and are not causal shader classifications. Newly recovered translator/evaluator presets are absent or underrepresented.

- One Apple M4 Pro Android emulator GPU stack; no TV fidelity or frame-rate measurement.
- Fixed bass stimulus, render seed 12345, 30 fps, 120 warm-up plus 360 measurement frames; all 1470 PCM bytes delivered per frame.
- Baseline/final at 2364×1330 and3840×2160, classic35 at 1182×665, two fresh-process repeats per case.
- Eight selected captures: 120,150,180,210,239,300,390,479. Primary image metrics use the 256×144 lossless thumbnails, **not full-native1182 image MAE**.
- 640 current jobs:574 new plus 66 verified current baseline35/classic35 rows reused through input and artifact receipts. No previous `1b2c2663`, historical 790 candidate or private FP16 rows entered the primary final candidate.

## Direction and magnitude

Primary closeness combines mean native-luma absolute error and thumbnailRGB MAE against current classic35. Opposing directions are *mixed*; a 1e-9 numeric epsilon defines ties. This is not a perceptual threshold. Means use five captures for the 4 s window and all eight for the 12 s window; they are sampled arithmetic means, not time integrals.

| Render height, 12 s window | Closer | Farther | Mixed | Tied |
|---|---:|---:|---:|---:|
|1330 |28 |8 |18 |10 |
|2160 |30 |10 |14 |10 |

Direction counts alone hide magnitude. Against baseline35 at2160, paired thumbnail-error changes have median **17.084% reduction**, but the median absolute reduction is **0.001482 normalizedRGB error** (0.1482 percentage points). Paired native-luma error changes have median **0.571% reduction**. At1330, corresponding relative medians are 8.531% and 6.022% reductions. Medians of relative changes are not percentages of aggregate medians.

Against the earlier overwrite-fixed `790aaa24` candidate, recent median changes are much smaller: at2160 the median thumbnail-error change is about **0.57% higher** over63 defined ratios; one zero-error denominator is undefined. Native-luma error has median 0% change. The independent parent calculation includes that neutral0/0 case as 0%, giving 0.5583%. Both reports preserve their definitions. All 128 sampled baseline35 and classic35 native-hash vectors match their historical29 equivalents, and 790 errors were recomputed against the **same current classic35** images. Nevertheless, these are different complete source contexts; the comparison is not isolated proof about one routing change.

Large tails remain. Against baseline35 at2160, astral nz+ increases thumbnail error by 0.0845 and native-luma error by 0.1197; Mig068 increases them by 0.0433 and 0.0486. DiskWasher lowers thumbnail error by 0.2158; Heaven Liquid lowers it by 0.1105 and native-luma error by 0.1390. The per-case arrays and outlier lists preserve both signs, low-reference-luma bands and near-zero denominators.

The 1/5/10% bands in `effect-sizes.json` are **arbitrary screening labels**, not noise bounds or acceptance rules. Exact selected-frame repeats establish stability for this seed/signal; they do not measure sensitivity to slight render-size changes. The proposed ±1% classic-reference size controls and any later ±2% or newly recovered witness controls remain planned follow-up. They are not a gate on the accepted checkpoint and must not be described as completed measurements.

## Audit and preservation

The independent audit verified 640 successful rows, 320 exact selected-frame repeat pairs, 307,200 frame/name/PCM records, 5,120 selected native hashes, 8,464 retained-file hashes and current APK/AAR ELF identities. The new epoch retained no fullRGB files; 144 rawRGB files remain in verified reused control jobs. Unread pixel frames were not hashed.

Android numeric PIDs recycled: 630 distinct numbers represented 640 unique PID/instrumentation-start timestamp pairs. All 320 repeat pairs used different PIDs. The provider force-stopped the dedicated package before and after every new job. Instrumentation timestamps are not OS process-birth timestamps; global numeric-PID uniqueness is not a freshness requirement.

The complete source/render-proof closure is preserved outside the worktree:

- Archive: `final-merged0e3-full64-63090f27b855.zip`, 1,248,983,080 bytes, 10,054 files.
- Location: `/Users/jneerdael/Scripts/Projectm-TV-recovery-2026-10-04/current-main-validation/`.
- SHA256: `8f566047c6eea16ac61a2cf445206a50750dd0b668b52d7333340a4335fd559f`.
- All ZIP member CRCs verified; source/raw measurements preserved. Includes current/reused rows, images, signals, protocols, workers, APK/AAR artifacts, compiled source/patches and audit/effect reports.

This publication copy includes compact reports, protocols and three hash-verified visual sheets. Original 256×144 PNG pixels were pasted unchanged into the sheets; frames 239/479 are illustrative subsets of the eight-frame summaries. `publication-copy-manifest.json` records copied-file hashes. Historical 1b2 and 790, private precision and source29 evidence retains its original scope elsewhere; none is silently relabelled as this final epoch or the later dual-policy build.
