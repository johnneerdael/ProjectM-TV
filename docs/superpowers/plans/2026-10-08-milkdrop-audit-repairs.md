# MilkDrop audit repair plan

**Goal:** Resolve every one of the 33 supplied findings, either with a verified safe fix or with an evidence-backed decision document and before/expected captures for the owner.

**Architecture:** Keep upstream changes in the ordered TV patch series. Investigate each finding against current main and both identical MilkDrop 2 references, separately tracking MilkDrop 3. Preserve Native 4K, authored feedback, prepared replay, live controls and all earlier compatibility repairs.

**Scope:** `/Users/jneerdael/Downloads/projectm-library-audit-handoffs-2026-10-08`; 31 I findings and two M findings. Lexical matches are candidates, never confirmed affected counts.

## Constraints

- Playback target: 3840×2160 Android TV, Native Standard trails; evaluate Medium/High where affected.
- Use matched small canvases for source-stage isolation, then actual Native 4K acceptance. Record authored/output/viewport/reference sizes separately.
- Keep the 15 existing patches, preset/texture bytes, instance ownership, GL-thread ownership and prepared geometry replay.
- Implement only fixes with no demonstrated performance or fidelity regression. Document tradeoffs for owner disposition.
- Preserve original audit and all frozen/shared workers; use task-private builds and packages.
- No release version bump. Follow repository review, CI, merge and publication gates.

## Per-finding work cycle

- [ ] Freeze input/source/artifact hashes and current branch baseline; verify all 9,606 candidate-inventory bytes.
- [ ] Trace each ID from original source to patched production code and current predictor, including historical improvements.
- [ ] Execute an independent failing source-stage regression before the fix; include unaffected, boundary, Native replay and nonfinite controls relevant to that ID.
- [ ] Add the smallest ordered patch for a safe repair; update predictor contract where applicable without rewriting historical identities.
- [ ] Capture a strongly affected unchanged original preset, isolated before/after at Native 4K with matching PCM, seed, clock, lifecycle and rendering settings. Label source-derived expected views accurately; never claim original D3D screenshots without an actual original renderer.
- [ ] Measure matched 4K engine timings and resources. Retain performance/fidelity tradeoffs in the decision report instead of applying them silently.
- [ ] Update the ledger and evidence, user guide/architecture/provenance and AGENTS as needed; commit/push coherent checkpoints.
- [ ] Run relevant patch/native/host/JVM/Android/docs checks; obtain final-head Codex review, CI and merge; verify automatic release.

## Completion audit

Require all 33 ledger entries to link either a validated implemented repair or a complete owner decision record. Each record includes source reasoning, corpus trigger assessment, actual captures, an expected appearance explanation and performance/fidelity limits. Pending validation, weak screenshots, source-only assertions and lexical counts do not satisfy completion.
