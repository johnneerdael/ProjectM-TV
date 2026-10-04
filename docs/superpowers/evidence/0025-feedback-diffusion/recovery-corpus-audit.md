# Recovery source and corpus audit

Audit date: 2026-10-04. Scope: read-only inspection of surviving worktree, git objects, recovery backups, source snapshots and evidence. No renderer, worker, corpus, or device was run or modified. Only this report was written.

## Source recovery conclusion

The recovered final renderer diff is cryptographically identical to the deleted final series. The initial recovery patch used a different prose header; historical tool `001970-command-0.txt` contains the final header rewrite omitted by the initial reconstruction. Extracting its exact Python string literal (including the leading space before ` docs/superpowers/evidence/...`) and prepending it to the current recovered diff body reproduces:

- Final patch SHA256: `9e3e5a0b4c5cb336d6e592c6cc2b19e8f5a6b2e6266c794209620cca66e98b58`.
- Ordered full25 patch-series SHA256: `44381ce5cd09e605e4393bd5b2de3fe9273d59b916e0f5bb96010107c8b18479`, exactly the supplied deleted final identity.
- Worker source/snapshot identity: `b52b12e82dccfebb9201cbceed164aba0e7295455d1f052f47e4038a84185cc2`, exactly the supplied deleted final identity. This is SHA256 of canonical JSON `{commit:e0b0a967f0ffd7d332106c366668ed271718472b, patches_sha256:44381ce5..., instrumentation_sha256:5bc595dcca2b85a705ad491f8b2636c03968960ade5adea4a253abf79857b93e}`. It identifies prepared sources and instrumentation, not a recovered executable byte hash.

No renderer source edit is necessary to recover those identities. Restore the historical header rather than changing passing product code. The audit performed this reconstruction in memory only and reported the result to the parent. These exact hashes establish recovered patch/source-definition identity, not reconstituted raw measurements or fidelity acceptance.

None of the eight surviving `build/follow-ups/lab-*/engines/*` snapshots containing `FeedbackDiffusion.cpp` is that final adaptive implementation. All use the earlier separable Gaussian nine-tap kernel; none contains `tapCount` or `DiffusionWarpEligible`. The original/safe/float/reject/reject-safe snapshots share only the two CMake files with the recovered ten-file patch. They remain older research evidence.
Compared explicitly against `lab-diffusion-original/engines/4530e91c2c8073c16dabbd4e56310a55d001ad124671b52229f1231441086824`, recovery changes:

- `FeedbackDiffusion.cpp/.hpp`: adaptive three/four equal-weight taps, cached GL uniform locations, delayed allocation after successful optional-shader compilation, diagnostic failure fallback, scale-change return/cache invalidation, cap warning, load-time sampler/undisplaced/peak-sharpening gate.
- `MilkdropPreset.cpp/.hpp`: coupled vector activation, hybrid input/output placement, prior diffusion texture reuse, resize/scale/injected-image invalidation, load-time gate state.
- `MotionVectors.cpp/.hpp`: minimum length follows reference scale only while diffusion is usable.
- `Renderer/Shader.cpp`: delete successfully compiled vertex shader if subsequent fragment compilation throws.
- `FeedbackDiffusionTest.cpp`: exact second moments on both axes, tap means/covariance, motion minimum and gating coverage.

Surviving original engine variants are `e03b0b5f...`, `e8d40059...`, and `4530e91c...`; their patch identities are `54eb357434f93baa645b911181c5c63ac7a647392704b235515128bc3d7798c6`, `a3a365c9ce649824a28ed980ba3ae251c1e597f9413753710f432027cd539e20`, and `29c5d58f2945a9cbe81608cbd8499465f94b649a47ce774e1f989e8af698dfb4`. Original sampler variants alter additional MilkdropShader/PresetState sampler routing. The `repo-*` directories contain pristine source plus separate patch sets; their source checkout itself has not had those patches applied.

Read-only git inspection found final `0025-feedback-diffusion-compensation.patch` only in recovery commit `d5ac3f5`. The `poc/diffusion-compensation` branch contains older `0022-feedback-diffusion-compensation.patch`, SHA256 `60fbf851b35775804c3e48ac96459e553d80d5b0589f9e7c63bf1edb4e16d91f`, without adaptive taps/gating. `clean-main-2026-10-03`, `evidence/quad-lines`, `evidence/quad-lines-corpus-2026-10-04`, and `followup/quad-lines` contain no final diffusion patch. Before historical header restoration, the recovery patch SHA256 was `cfb11e7f28535383799a7a78ed50f7f043168bac540151d2efb3a3bb4262dc1a` and matched `/Users/jneerdael/Scripts/Projectm-TV-recovery-2026-10-04/recovered-product/manifest.json` and its adjacent backup patch.

Historical source-generation provenance remains in `/Users/jneerdael/Scripts/Projectm-TV-recovery-2026-10-04/parent-tool-index.json`, `product-command-index.json`, `parent-tool-inputs/`, and `replay-reviewed/`. For example, `replay-reviewed/001738-renderer.py` adds the final hybrid `diffuseAtOutput = Active() && !motionVectorsDrawn` behavior. These are replayable mutation instructions. Together with the exact `001970` header reconstruction, their recovered final patch body reproduces the original series/snapshot hashes above; the original binary and raw measurements remain missing. `acid-diagnosis/SOURCE-RECOVERY.json` separately records each research file hash and last generating tool line; it explicitly says original workers, frame hashes, raw JSON/CSV/PNG were not recovered.

Current recovered product file hashes, recorded independently from the patch:

| File relative to projectM | SHA256 |
| --- | --- |
| `src/libprojectM/MilkdropPreset/CMakeLists.txt` | `4d33d736d205864b479785e583acd91dff89c870b52e107d7e965d2467a0819e` |
| `src/libprojectM/MilkdropPreset/FeedbackDiffusion.cpp` | `200ca53a0e43493555ce4c19bf95a79df834164f1aa4936a9351c67d6c846b3c` |
| `src/libprojectM/MilkdropPreset/FeedbackDiffusion.hpp` | `d9fb03d530aeef77969870d599e643253d49d773aa8eb0b5060e7eb37408a22b` |
| `src/libprojectM/MilkdropPreset/MilkdropPreset.cpp` | `64d784118150674f2d84408fa5d6217bfb8874420ca31abb4738c9230b5f681a` |
| `src/libprojectM/MilkdropPreset/MilkdropPreset.hpp` | `7cb7e3b7ec00009603113ea180ca6ea19cea4d3331859bd1263d85343dfc4f72` |
| `src/libprojectM/MilkdropPreset/MotionVectors.cpp` | `582d91c4d424cd4073f0801eedc29e08b78b5786e19071baa8df7af32176339a` |
| `src/libprojectM/MilkdropPreset/MotionVectors.hpp` | `3659a20f01dbd42be68f3c916f629924521de857ab2ada095c43ea6156158e42` |
| `src/libprojectM/Renderer/Shader.cpp` | `5d8244d1fd744c6afae38e4764561ea3ba818d28b1b6aa0e78d9db5c2100b9b5` |
| `tests/libprojectM/CMakeLists.txt` | `184ddab2f0359409e4401e8e8d1304eedb4d3fe47fcf5531ba2d63366d36d3be` |
| `tests/libprojectM/FeedbackDiffusionTest.cpp` | `770184b1de7de110b219ff862aab2ffd323869086d190855057897cdf3667111` |

## Frozen desktop corpus identity and actual coverage

All paths in this section are under `/Users/jneerdael/Scripts/Projectm-TV/.worktrees/quad-lines-follow-ups/`.

The current `build/follow-ups/corpus-baseline/protocol.json` digest recomputes exactly as `db30e933df242896ab72e5889623a1c48ca0e4ff2fd0a2ec42c9d8e2f061587f`. Its worker is direct patched projectM, not `projectm-tv:core`:

- Engine pin: `e0b0a967f0ffd7d332106c366668ed271718472b`.
- Ordered patch digest: `839ea69b6a5b5fd94afa1b5d140c621b7af2b6dad7c53c849487d37bc4bb786d`.
- Private RNG instrumentation: `254db5d7418da6162c8db449ed400df19e9b6391ba405c0d20a0e19c3a005ef8`.
- Snapshot/build ID: `354fe220e27baf67a7b16d4487ca5cd29929b19e6b34e7ac5ac45dd345c34305`.
- Actual binary: `build/follow-ups/lab-deterministic-baseline/native-build/<ID>/preset-lab-worker`, SHA256 `b0ed95f95c9268b52503ffa3c35dd3a8b30485f50fea0edab047b9fe7e688b91`.
- Frozen runner SHA256 `25531beaf7547f7877405d145a642f14c311bdf5ea24d63c58b53bca9455efd6`; worker API SHA256 `bd385fe5d4c8191cf47b1ffd5f624de3d0b833ec2216c594b8cb369075bf944e`. Both current files and worker executable still match.

Exact patch set is saved in `build/follow-ups/repo-deterministic-baseline/tools/projectm-patches/`: patches0001–0024 are byte-identical to recovery, plus `0025-shader-failure-handling.patch` SHA256 `b9460b0d17a53f30675938efc92707258c18ed84479695cd51cf1617a792db85`. This baseline contains no diffusion. Its patch25 also changes shader exception diagnostics and adds failure tests, beyond the recovered diffusion patch's fragment-failure cleanup. Do not call it the recovery baseline's exact series.

Protocol:2364×1330,30fps,seed12345,reference1024×768,controlled float PCM `bass-0.30`,4s warm-up +4s window,240 frames,2 repeats. PCM SHA256 `f31d76c4a6fb286768d01c37cc6951f2e83dc46bb42b46e286bc88e808525c1b`; texture digest `0ed4c77cf33b443b50089f755009f5d44a91bf59d7f64b011d0935c8662a3c0d`; corpus digest `edeb5fd8091ec76c8ce6300172e66de633678f04776f48a6ccc5f6be2c0b27c0`. All9606 individual preset bytes match `inventory.json`.

Actual read-only coverage differs from stale `progress.json`:

| Evidence | Current protocol | Obsolete initial protocol |
| --- | ---: | ---: |
| Terminal row records | 652 successful | 3 failed |
| Repeat records | 1305 successful | 6 failed |
| Fully paired rows | 652 exact repeats | 3 failed pairs |

All655 row payload hashes/keys and all1311 repeat payload hashes validate. Every successful repeat observed240 frames; all row thumbnails exist. One current repeat is unpaired: `runs/36c2c445fa920010be143b857410e7edd0bbf08f4a57918e1d8830cf43e7d161/repeat-1.json`. The initial protocol `41c1f1465fb1fdb423b1c701da53ba93b5e485324ca71dee1d2de5d4c2f16514` differs in runner hash. Its failed filenames are `2009 4th of July with AdamFX n Martin - into the fireworks E.milk`, `161.milk`, and `430.milk`; these are not current-protocol failure coverage. `progress.json` says649 terminal/646 successes+3 failures and is stale relative to the652 current successful rows. Coverage remains partial:652/9606 successful paired presets.

Only native hashes and streaming metric summaries plus three256×144 thumbnails at zero-based120/180/239 are retained. These can support matched aggregate brightness/colour/motion and thumbnail comparisons. They cannot reconstruct full-resolution MAE, every native frame, or a12-second/native4K corpus baseline. Initial and current protocol rows must never be merged as one cache.

## Reusable fidelity evidence and exclusions

The accepted private RNG uses `analysis_hooks.hpp` Park–Miller state and `build_worker.py` replaces MilkdropShader's process-global `rand()` calls with that private generator. Instrumentation identity includes builder and every native source file, not only the hooks header. Copying three files does not by itself prove the whole instrumentation identity. Candidate and baseline must agree on engine/evaluator pin, transformations, PCM bytes, settings, readback and protocol; changed patches require a distinct worker identity.

| Existing evidence path under `build/follow-ups/verification/` | Verified identity/count | Appropriate reuse |
| --- | --- | --- |
| `sampler-impact-private-rng/raw.json`, `jobs/*/five.npz`, manifests/jobs |396 successful jobs:33 presets ×classic1182×665/scaled2364×1330/native3840×2160 ×before/after ×2 repeats; private RNG254db…; baseline839ea… and sampler-fixed55a7dc… | Strongest sparse direct-projectM controls and retained matched frames. Reuse baseline side for matched direct candidate comparisons after verifying source/PCM/protocol; separate sampler-fixed side. |
| `reference-feedback-attached/raw.json`, `jobs/*/five.npz` |20 jobs on Royal191; RNG254db…; patch digestec2c7eeb…; 540/classic/reference/1330/2160 sizes | Reference-grid research controls only; not final adaptive diffusion. Distinct engine identity even with switch off. |
| `reference-feedback-linear-attached/raw.json`, `jobs/*/five.npz` |20 jobs on Royal191; RNG254db…; digest08dc4fc5… | Separate linear reference-grid experiment; same limits. |
| `reference-gradient-control/`, `reference-feedback-linear-gradient-control/` | Private RNG254db… | Positive attachment/gradient controls for reference-grid research; do not treat as corpus baseline. |
| `diffusion-focus/`, `diffusion-long/`, `diffusion-float/`, `original-read-slot-safe/` |168/50/24/40 successful manifests respectively; old instrumentation5bc595… | Preserve as older Gaussian P1 diagnostic evidence. Useful for selecting regressions and understanding mechanisms, never pooled with254db… or reported as final recovered adaptive results. |

Reports live beside scripts in `docs/superpowers/evidence/quad-follow-up-verification/results-*.json`. The sparse raw rows retain `five_frames`, per-measurement-frame hashes, `canvas_metrics`, luma, RGB, saturation and sharpness. Confirm exact requested preset hashes, job config, PCM bytes, and original metrics definition before deriving new comparisons. `results-sampler-impact-legacy-rng.json` explicitly records invalid nondeterministic legacy cases. The original-read invalid-slot and reference-feedback invalid viewport/target reports also remain invalid for fidelity conclusions. A small global MAE does not replace brightness, colour, contrast or motion review.

Full-corpus source groups are reusable independently of RNG at `build/follow-ups/corpus-family-review/`: `corpus-features.jsonl`, `preset-index.json`, `feature-memberships.json`, `normalized-shader-families.json`, `representatives.json`, and the shared `corpus_features.py`. Join runtime data by filename AND raw SHA256. Their structural-family corpus digest `6518d522d32091a37979f3de949981796bf9854b06255e8cf67bfe49b895f097` uses a different defined serialization from the runner inventory, not different preset bytes. Group membership establishes source structure, not a family-wide runtime failure.

## Actual core backend status and adoption boundary

`docs/superpowers/evidence/quad-follow-up-verification/README.md` explicitly states the desktop corpus was stopped after the user required `projectm-tv:core`; its652 records are supplementary. `build/follow-ups/core-backend-review/design.md` is the surviving concrete Android harness design. No actual core-backed APK, corpus worker, or immutable rendered protocol exists in this worktree. No `nativeEngineMode`, engine-mode, backend, or core-bridge switch exists in current preset-lab worker/models/measure files.

Proposed exact route is framework Instrumentation→real EGL3 pbuffer/default framebuffer0→production `ProjectMJNI.init`, settings, `addWaveform`, `onDrawFrame`→actual `native-lib.cpp`, `snapshot_fade.cpp`, `preset_prewarm.cpp`→patched projectM→real Android driver. Its lab bridge may expose clock/seed only, never render/load/feed APIs. Preserve the real production modules and their linked symbol/source identities.

Concrete differences needing a new protocol:

- New fresh instrumentation process for EACH preset repeat; core release does not reset all library/prefetch/history state.
- Complete packaged9606 assets/index retained, but per-job skip file leaves exactly one eligible requested preset. Full-name ownership must be checked every frame; rejected target cannot qualify as successful idle/fallback output. A bounded debug-property prefix is unambiguous only with this one-member mask and must be restored.
- Actual `addWaveform(byte[])` receives complete1470-sample blocks at30fps. Convert float input once using documented nearest-even `clip(rint(128+127*x),0,255)` and hash both input/uint8 result; production FeedAudio chooses projectM's max samples. Direct float PCM is a different oracle.
- Public settings: autochange/beat cuts/blank detection off, categoryall, mesh48×32, duration3600, soft cut0, classic transition; actual `onMemoryPressure` pauses real prewarming20s. Verify no prewarm job/reset happens during8s logical run.
- Share logical clock between copied core NowSeconds and engine TimeKeeper, preserving real CPU measurements. Hash original/instrumented sources and exact transformations; private RNG becomes a NEW instrumentation identity.
- Read default framebuffer0 after actual onDrawFrame, with documented RGBA/RGB8/orientation/driver details. Verify pbuffer dimensions/capabilities and zero GL/EGL errors.

The intended pilot needs exact complete repeats for Echasketch RNG, an affected sampler, unaffected preset, ORB and explicit load failure, plus separate lightweight snapshot-transition shader gate. Only after pilot can throughput/ETA/full-corpus schedule be determined. The design uses one sequential instrumentation job on approved serial192.168.51.53; this audit performed no device access. Candidate/baseline APK variants need source, native library, toolchain/ABI/device, assets, transformed PCM, settings and frame protocol identities. No existing desktop row is reusable as an actual-core baseline.

Mac feasibility evidence is `core-backend-review/source-identity.json`, `compile-results.json`, `snapshot-probe-results.json`, and `snapshot-probe.log`: actual native-lib/snapshot compile, but preset_prewarm lacks EGL headers; real Mac CGL rejects SnapshotFade's `#version300 es`. This is not a running core backend. A CGL adapter would require wider EGL/context/scheduling/shader changes than the minimal Android harness. Preserve sparse direct-projectM research separately while the real core backend is implemented by its owner.
