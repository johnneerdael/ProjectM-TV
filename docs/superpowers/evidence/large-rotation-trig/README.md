# Large warp rotation: production correction

Investigation base: `dd59a791fd2af6b7ad2fffcb389e0bc178905959` (published2.3.16),
projectM4.1.7 plus patches0001–0050. The supplied handoff is
`projectm-tv-aar-large-rotation-trig-2026-10-07/report.md` in Downloads.

The unchanged witness is `EoS_Phat_PeterP_Sentinel_Aware_6 EoS edit slice into your beautiful love.milk`,
SHA256 `591567f0029068f4f1f7ec3b50d7a8fabd8c1658ece6c981a7f60cfd6f3317ea`.
Its per-pixel equations end with `rot=10000000` after `zoom=.9999;sy=-.99`.
The handoff's isolated GLES vertex probe reports both sin/cos zero, including highp.
Active-program and hue/feedback controls isolate the rotation path; total
cross-thread random counts do not establish a random-binding defect.

Patch0051 follows MilkDrop2 `milkdropfs.cpp`'s `sinf(fRot)`/`cosf(fRot)` after float
conversion. CPU libm avoids GPU trig range reduction and an inaccurate rounded
2pi modulus for very large angles. It changes only the internal mesh/vertex shader,
not authored equations, assets, custom shader trig or the C/Java/JNI interface.
The vertex gains one float (56 to60 bytes) and one attribute (six to seven).
No performance improvement is claimed; per-pixel CPU trig needs device measurement.

## Verified checkpoint (2026-10-07)

- RED: production mesh draw/readback on Apple M4 Pro CGL with the old series:
  `rotation=10000000 UV axis=0 actual=0.501961 expected=0.735156`.
- GREEN: real legacy/custom warp draws with both per-frame and per-pixel input,
  signed/moderate/large/max-finite float controls, varying per-vertex rotation,
  nonfinite input recovery, and four feedback frames pass on macOS CGL and the
  task-owned API34 ARM64 GLES3 emulator (`emulator-5630`, Apple M4 Pro translator).
  Nonfinite controls verify no GL error and unchanged equation state, not image fidelity.
- `tools/check-patch-series.sh`: all51 patches apply to a clean pinned export.
- `tools/projectm-host-tests.sh`:261/261 pass.
- Initial ASan/UBSan projectM regression run:28/28 pass. The expanded rotation test
  separately passes; the final full native runner is still pending.
- `./gradlew :core:assembleDebug :app:assembleDebug testDebugUnitTest`: BUILD SUCCESSFUL.

Raw build/test logs are ignored under `build/large-rotation/`. No published artifact
or original-preset appearance claim is made by these numerical controls. Linux
Mesa, physical-TV timing/captures, full Native AAR original-hash retest and authored/
native high-resolution paths remain pending. Final Codex review, CI, merge,
publication and Milkbeat update are required before completion.

## Documentation assessment

Evaluated README, user-guide troubleshooting/development/settings and the linked
Pages source, ARCHITECTURE, THIRD_PARTY, RELEASING, PR template and existing engine
regression documentation. Updated README, troubleshooting, development,
architecture, patch attribution and AGENTS for the rotation behavior and internal
layout. Installation, UI/settings, public APIs, release/version rules and historical
predictor scores are unaffected. Strict MkDocs validation remains pending.
