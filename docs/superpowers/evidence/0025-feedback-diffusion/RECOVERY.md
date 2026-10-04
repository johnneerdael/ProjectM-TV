# Native feedback recovery checkpoint

The active `clean-main-2026-10-03` worktree was deleted while its changes were uncommitted. The recovery branch is `feat/native-4k-feedback-recovery`, in `.worktrees/native-feedback-recovery`. Checkpoints are committed and pushed with the personal `johnneerdael` account.

Recovered product code:

- Explicit Native resolution sentinel, panel/memory guards, legacy numeric-height migration, labels and JVM coverage.
- Patch0025: adaptive diffusion kernel, cached uniforms, shader-failure fallback and intermediate shader cleanup, coupled motion-vector minimum, source-cache invalidation, hybrid placement and mixed-point/GetMain gating.
- Research sources and session-reported findings in `acid-diagnosis/`; its inventory records recovered file hashes and source-edit provenance.

Fresh recovery verification:161 host tests pass;46 core/app JVM tests have zero failures/errors; all25 patches apply. Logs are `build/recovery-host.log`, `build/recovery-jvm.log`, and `build/recovery-patch-series.log`. The JVM run reused matching Gradle cache outputs. Product source and patch copies are also backed up outside worktrees at `/Users/jneerdael/Scripts/Projectm-TV-recovery-2026-10-04/recovered-product/`.

Raw frame PNGs, full measurement JSONs, APKs and desktop worker binaries from the deleted worktree have not been recovered. Recovered reported numbers are labelled as session records, not replacements for those raw files. The phase-beta prototype remains rejected and is not integrated into product code. Recovering code does not establish fidelity acceptance or readiness to merge.

The other agent's corpus setup in `.worktrees/quad-lines-follow-ups` is read-only to this task. Its current baseline covers all9606 presets at2364×1330,30fps,4s warm-up plus4s measurement, with two repeats and controlled bass-0.30. It uses instrumentation SHA `254db5d7418da6162c8db449ed400df19e9b6391ba405c0d20a0e19c3a005ef8`, which differs from the deleted measurements. Reuse its inventory, infrastructure and baseline only with matching protocol/worker inputs; do not combine differing RNG results. Classic-reference, native4K,12s and diffusion-candidate comparisons are additional work. No duplicate corpus run was launched.

Next restore the shared measurement scripts needed by the research probes, align the candidate with the other agent's deterministic corpus protocol, and evaluate gains and regressions across that corpus. Preserve truthful sampler behavior and report brightness/colour separately from image MAE. Auto remains capped at1330. Keep checkpoint commits and pushes as work progresses.
