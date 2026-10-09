# I28 — retain blur-range safety repair

**Disposition: retain current0005 blur expansion and coherent fallback. No new engine patch.** Production numeric/storage/decode tests and24 Native4K runs qualify this retained policy; original zero-denominator appearance is undefined and is not used as an image oracle.

Original MilkDrop2 and pre-repair projectM both assign avg-minus to minimum and maximum, collapsing narrow/equal/reversed intervals before reciprocal normalization. Expansion is a retained TV safety correction, not an already-safe upstream backport. [Source contract and limits](DESIGN.md) records clamp-then-expand order, progressive float32 coefficients, full-triplet fallback and the original source hashes.

## Executed evidence

The current50/50 [normal](../review-checkpoint/shipping-post-i22-normal50.txt) and [ASan/UBSan](../review-checkpoint/shipping-post-i22-asan50.txt) suites include passing blur-range numeric and real-GL rendering controls. [Exact production test source](production-blur-range-controls.cpp) checks thresholds, nesting, reversed intervals, representable/extreme/nonfinite inputs, progressive scale/bias, actual normalized storage and GetBlur decoding. It compiles the authored stock shader consumers separately; the recorded full-engine composite path is checked, while full-engine warp selection remains a distinct limit.

[Native results](native-results.json) and [identity](native-identity.json) bind sourceac3/current27patches, API34ARM64, hostGPU/GLES3, the actual instrumented AAR/private APK, Native3840×2160 output/Standard1280×720 canvas, seed12345/30FPS/mesh48×32 and frozen mono PCM. Native bytes and stock assets are preserved;11 labelled test presets are appended. The installed APK hash is checked before every row. All480 GL/name checks and cleanup pass perrun; all12 repeat groups and192 selected PNG/RGB checks pass with read framebuffer0.

Actual equal-half, near-quarter and reversed-bound fixtures match their independently supplied finite expanded-bound siblings in every selected RGB frame. Unsupported finite input matches the explicit default-range sibling. The unchanged Cope - The Cloud preset also repeats exactly; no original Windows comparison or affected-corpus claim follows.

| Diagnostic | Retained renderer | Finite coefficient reference |
|---|---|---|
| Equal-half blur bounds | [Expanded/storage-and-decode result](native-captures/blurpolicy-audit-blur-diagnostic-equal-half-actual-retained-current-0/frame-239.png) | [Collapsed decode coefficient only](native-captures/blurpolicy-audit-blur-diagnostic-equal-half-finite-collapsed-decode-oracle-current-0/frame-239.png) |

The black coefficient reference assumes a finite stored sample and applies the original level1 zero-gap decoder coefficient. It does not execute original zero-division storage or establish original GPU output. Safe gradient fixtures write known finite colors without noise/assets/audio geometry; their visible nonblack gradient establishes authored shader activity. Current versus explicit-expanded equality is the bounded safety oracle.

## Limits and owner followup

Retain coherent adjusted bounds for both storage and decoding, all existing blur/reference/FBO controls and pass selection. Restoration of collapsed intervals is rejected by the numeric contract. Retention adds no new work and carries no performance-improvement claim. Physical-TV timing, Windows/D3D appearance, whole-shader nonfinite certification and whole-corpus prevalence remain unmeasured. [Audio provenance correction](../AUDIO-PROVENANCE.md) applies to the stale512 prose in frozen manifests; actual queried tails use576.
