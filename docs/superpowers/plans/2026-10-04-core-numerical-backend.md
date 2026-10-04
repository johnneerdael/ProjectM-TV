# Published Core Numerical Backend Plan

Use inline execution. The user specified the published ProjectM-TV core AAR
unchanged and authorized native numerical measurements plus AI video diagnosis.

## Verified backend

- [x] Pin core v2.2.4 and verify the release SHA-256.
- [x] Load its exact published JNI class and native library in
  `tools/milk-analyzer/CoreBackendRunner.java`.
- [x] Supply an independent EGL pbuffer and asset fixture without installing an app.
- [x] Read presentation framebuffer0; core may leave a private read framebuffer bound.
- [x] Verify 30 constant-color frames with zero byte error.
- [x] Verify 30 FPS time progression with runner-side clock interposition in
  `core_backend_clock.cpp`; AAR code remains unchanged. Maximum color-byte error1.
- [x] Render three real 420-frame presets, including a waveform and an independent
  interpreter domain failure. Selected preset names match requested names.

Evidence: `tools/milk-analyzer/fixtures/published-core-v2.2.4-verification.json`.
The three runs took 3.93–12.30 seconds each. Their serial renderer-only
extrapolation is about22 hours for9606 files, not a guaranteed completion time.

## Corpus runner

- [ ] Stream frame fields to avoid storing whole videos for every preset.
- [ ] Reuse the published asset archive with small selection overlays; avoid
  transferring the texture pack once per preset.
- [ ] Write one atomic resumable result per corpus SHA-256. Preserve load, GL,
  transport and measurement failures with diagnostics; do not replace failed cases.
- [ ] Freeze scoring parameters and record the AAR/library/audio/renderer identities.
- [ ] Diagnose every remaining unscored entry and verify finite score coverage
  against the exact published corpus inventory.
- [ ] Commit/push verified checkpoints regularly on feat/preset-audience-scoring.

## Review build

- [ ] Generate inclusive overlapping All/Chill/Normal/Party indexes from scores.
- [ ] Adapt app labels/index aliases to the unchanged core's existing category API.
- [ ] Show the current preset's intensity and collection-relative rank distinctly.
- [ ] Build a separate debug review APK with the pinned published AAR and complete
  generated collection; verify groups, coverage and artifact contents.
- [ ] Deliver the artifact for human evaluation. Measurement completeness does not
  itself certify audience-fit accuracy.
