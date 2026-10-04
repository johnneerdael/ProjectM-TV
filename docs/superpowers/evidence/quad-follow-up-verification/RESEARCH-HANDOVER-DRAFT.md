# Research handover draft — provisional

Prepared 2026-10-04T11:43:58.849033+00:00; inspected source HEAD `53e93671e0c0082fe1275555e65c3ff2f978f8c0` on `followup/quad-lines` in `/Users/jneerdael/Scripts/Projectm-TV/.worktrees/quad-lines-follow-ups`. This is a read-only research inventory plus one new draft file. No device operations, ZIP, code change, commit or push were performed for this handover.

**Do not treat this as corpus completion, a final ROI decision, or a final issue list.** [PR #23](https://github.com/johnneerdael/ProjectM-TV/pull/23) remains a draft. The actual-core baseline is live; final candidate/core comparison is incomplete. Prepare the Downloads ZIP only after the full actual-core comparison, investigation of changed cases, and ROI decision. Keep unresolved research even if the decision is to stop further implementation.

## Start here and preserve ownership

Read `core-corpus/PROTOCOL.md`, `RUNNER-V2.md`, `COVERAGE-HANDOVER.md`, `OWNER-RECOVERY.md`, `SHIELD.md` and this directory's `README.md`. Relative paths in this document refer to this evidence directory unless explicitly rooted at repository level. The original user evidence is under `/Users/jneerdael/Scripts/Projectm-TV/docs/superpowers/evidence`, outside the owned worktree; preserve it unchanged.

Use only physical device `192.168.51.53` (ADB serial `192.168.51.53:5555`), which identifies as AM9 PRO, Mali-G310, Android 14. Never wake a device. If it is asleep, stop physical work. SHIELD/Tegra verification is deferred and requires later access/authorization. The separately approved local emulator is task-owned `emulator-5580` with owner PID 20334 at this snapshot; revalidate `mac-emulator/launch.json` and the ownership epoch before use. Do not replace it, disturb the live baseline, modify the frozen baseline runner, remove any worktree, or operate another device. Keep the dedicated corpus package separate from Milkbeat/production app. This draft does not authorize new device operations.

## Current evidence and what PR23 actually fixes

| Patch / work | Evidence-backed scope | Limit |
|---|---|---|
| 0025 | Shader errors survive standard handlers; compiled vertex shader deleted when fragment compilation fails. Driver lifetime and RED/GREEN tests retained in `proofs/`. | Does not solve feedback fidelity. |
| 0026 | Implicit warp main reserves unit0; explicit clamp/wrap and point/linear aliases retain bindings. Matched sampler controls and 396 supplementary jobs retained. | 30/33 presets byte-identical in component sweep; three changed cases require authored-reference assessment. |
| 0027 | Preset load/expression/factory error stage/path messages preserved. | Diagnostics alone do not establish compatibility. |
| 0028 | Fresh colour history transparent black; local clear framebuffer preserves attachments across context recreation. | CGL proof is not attribution that the historical Mali Echasketch outlier is fixed. |
| 0029 | First compile the existing per-frame program; only rejection triggers legacy record/comment joining retry. | No preset rewrite or general shader/init/pixel/custom-stage rewrite. |

`161.milk` and `430.milk` recover in **four actual-core JNI jobs** (two repeats each) on Mali-G310, with exact selected native captures. `core-corpus/diagnostic-presets/per-frame-fallback/actual-core-recovery.json` records scope: ten selected captures per 240-frame/eight-second job; authored-reference fidelity and corpus coverage remain pending. Four healthy controls (Royal191, Echasketch, Matrix, Mood Rings) repeat exactly and match candidate28 at **16 selected frames each** (`core-corpus/diagnostic-presets/per-frame-fallback/healthy-controls29.json`); this is eight jobs, not a full-stream/corpus guarantee. Their full 480/selected equivalence was independently checked for candidate28 in `core-corpus/physical-candidate28/REPORT.md`.

The stopped direct-engine scan's652 records are supplementary on `evidence/quad-lines-corpus-2026-10-04`; never resume it as actual-core validation. PR23's host/component test counts reflect successive source snapshots; final packaging must capture current tested HEAD and truthful final PR body instead of merging historical counts into a new claim.

## Live baseline snapshot — refresh before any final claim

At 2026-10-04T11:43:58.849033+00:00, `build/follow-ups/core-corpus/measurements-core-emu-baseline-v1/baseline-progress.json` reported **2584/9606 terminal baseline pairs**, 2558 successful and 26 failed; completion was false. Committed `STATUS.md` is older and is not live status. The checkpoint state reported **5057 remotely acknowledged baseline jobs**, remote HEAD `55ea3d33709437754e101c2e20d9013c29198387`, no listed integrity issues, complete baseline/corpus remote coverage false. These are asynchronous snapshots, not an audit or evidence of final remote coverage.

Authoritative baseline protocol SHA256: `369263c90d7089ebfebb6fcf3609b5f2554899e26bf7ef321cad1800f36b8180`; source `a59b4e5`, patches 0001–0024. Require `baseline-completion-index.json`, independently passing final audit, all 19212 baseline job keys, and acknowledged remote completion before claiming baseline completion. The expected baseline jobs are **19,212** (9606×2); full baseline/candidate corpus is 38,424 jobs.

Prepared `build/follow-ups/core-corpus/measurements-core-emu-candidate29-final/protocol.json` has identity `29d5f5aafdc56b6f32fb39532a5bbf2d9ed2dfd5ca00b0b0d3e9f3af5be4679b`. Presence of a prepared protocol is not a completed pilot or candidate corpus. The final comparison must use the final tested candidate APK/core identity and runner v2, prove input equivalence to historical baseline signatures, and preserve all original baseline paths/provenance.

## Reproduction contract

Actual-core claims require backend `production-projectm-tv-core-ProjectMJNI-EGL-GLES3`: optimized Android `projectm-tv:core` through production JNI, GLES3 pbuffer instrumentation. Do not substitute direct patched-projectM, a host renderer or thumbnails for this oracle. Private logical clock/RNG instrumentation is identical across roles; its binaries are not byte-identical production AARs and do not establish production RNG parity. Record APK, embedded/runtime core ELF, ordered patches, observer, driver, source preset and texture hashes.

The core protocol renders 2364×1330 at synthetic 30 fps, seed12345, bass-0.30, 120 warm-up +360 measurement frames. Feed every 1,470-byte unsigned PCM block through `ProjectMJNI.addWaveform` and preserve the wrapper's 576-sample tail handling. Long input is 705,600 bytes, SHA256 `14a59e75249dee0dd15d74487688c248c6a4a4b24a843b6d6f612ccc5c408dbc`; short 240-frame input is its 352,800-byte prefix, SHA256 `38a09d906e93452d4af5ebea36fcdc684a8383eacbd162d2d61b4ed3fbd2674c`. Inventory identity `d49b515691b3d5fbaf2d15e0c51db3c0a13de1c0019baee75dd090fea8604919`; textures `6dca293df2fc003f6b4f1d05f2ad0108283e16f18e92d76530e28adf3580d08d`.

Selected indices: 120,121,150,151,180,181,210,211,238,239,300,301,390,391,478,479. Render all 480 frames even in selected mode. Native RGB8 hashes use GL bottom-to-top rows after stripping alpha. APK 256×144 bilinear thumbnails are a separate oracle; selected hashes say nothing about unread frames. Capture current preset identity/PCM/switch count on every frame. Keep failures and attempts explicit; rendering success does not observe custom-shader compilation acceptance.

Host fidelity research uses **classic GL lines at 1182×665** as authored-size comparator, repeats twice, normally 30 fps with 4 s warm-up/4 s window; long research uses 4 s + 12 s. Match the exact PCM file and worker/instrumentation identity, because changing duration changes seeded signals in historical scripts. Include authored size-band controls **1166×656 and1200×675** (±1.4%), same-size classic/quad controls, relevant 1330/2160 sizes, and motion samples. Historical JPEG92 metrics and modern lossless PNG/NPZ metrics are different oracles. Inspect structure, movement, colour, contrast and detail; 10% is a rough diagnostic guide, never a hard acceptance gate. Never label an unknown changed preset degraded before authored-reference and visual verification.

## Open cases: facts, hypotheses, next discriminating work

| Case | Observed fact and evidence | Hypothesis / unresolved decision |
|---|---|---|
| Royal191 / native feedback fidelity | `results-diffusion-long.json`: repeated 50-job long sweep; at 4K diffusion image error 0.40424→0.01422 while luma ratio 0.3708 and sampled motion 0.000296 versus reference 0.018938. Original regression sheets and current native captures retained. | Uniform diffusion improves one scalar while losing motion. Full reference-loop nearest probe leaves luma≈3×; linear probe again suppresses motion. No production fix accepted. Verify original MilkDrop and actual-core authored controls; measure ROI/fidelity before further architecture work. |
| Uniform diffusion controls | `results-diffusion-focus.json`: 168 jobs, 24 comparisons, 20 lower mean image errors, four higher (Flexi/Cartoon at 1330, Nuclear/rce at 2160), exact repeats. Float intermediate/control-read experiments partially explain some changes; Nuclear's undisplaced read alone does not. | Do not ship based on median. Review all losses and wider corpus/families. Penattrition base/nz+ are different sources; base 4K long-window luma ratio 0.724. Mobile cost/renderability unmeasured. |
| Reference-grid feedback loop | Corrected attached-FBO probes and positive full-frame gradient controls pass; off-gates unchanged. `results-reference-feedback*.json` says experimental/not accepted. | Early viewport/texture-target probes are invalid. Closest sampling, actual MilkDrop loop, texture reads and long-window fidelity/cost still need separation. Do not promote nearest/linear probes. |
| ORB - Toffie Grider | Classic1182, classic1080 and quad1080 converge nearly uniform yellow in 64 s runs; pre-quad and current classic full streams match. Stock projectM4.1.7 full streams also match at 30/60 fps; both shaders compile. Border-off is black; raw-canvas and blur-offset-off still settle. | Border-driven fixed point is plausible, not proven as an authored defect. Original MilkDrop reference remains unverified. User's perceived static image cannot be blamed on PR14/quad lines from these experiments. |
| Remaining load/fallback failures | `baseline-failure-observations.json` records source hashes, jobs and stage categories.161/430 now recover; other failures remain unexplained. Royal492 includes one output-transfer failure and a successful repeat. | Separate genuine parser/compile/fallback faults from transport, timeout, owner death and nondeterminism. Preserve attempts; do not treat failed pair as candidate regression. Final corpus may reveal additional cases. |
| SHIELD/Tegra | Deferred; available physical evidence is Mali-G310. | No Tegra compatibility claim; test later only with user-authorized access and no wake. |

Historical recommendations need correction: the original PoC called Royal191 “fixed” from image error, superseded by measured motion loss. Shifter q-load whiteness and Hexcollie differences are strongly size/feedback-sensitive in recorded controls; they are not confirmed engine regressions. The old thin-wave +21% energy and thick-wave 16–29% lit-share claims came from rounding blurred composite output; corrected point-sampled/linear measurements do not support those faults. `I Like Cartoon` low-size discrepancy is located in main-wave feedback injection, but the blanket classic-at-unit-scale candidate was rejected (10/21 improve, 11/21 worsen). Do not revive disproven measurement claims.

## Minimum executable handover

Keep repository-relative structure. Include `tools/preset-lab/src/preset_lab`, its project dependency metadata, the evidence scripts and co-located imports, build scripts/patches, exact preset/texture bytes for selected issues, PCM files, worker JSON identities, and required test instrumentation sources. Worker JSON executable paths are local; recreate workers from pinned source before uncached renders on a new machine. `build_reference_worker.py`, `build_float_worker.py`, `build_original_worker.py`, `build_upstream_worker.py`, `build_sampler_worker.py` and `build_deterministic_baselines.py` explain identities; retain corresponding scratch patches separately from shipping 0001–0029.

From the owned repo root, the following offline export does not touch devices (output is outside immutable dataset):

```sh
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/core-corpus/audit.py --work build/follow-ups/core-corpus/measurements-core-emu-baseline-v1 --families build/follow-ups/corpus-family-review/preset-index.json --output build/follow-ups/core-corpus/handover-baseline-audit.json
```

After baseline finishes and the owner coordinates the next device block, use `run_v2.py` for new candidate protocols; `prepare`, `pilot`, then `scan --roles candidate --reviewed-pilot-sha256 EXACT_REVIEWED_REPORT_SHA`. Read full protocol before execution: `run_v2.py` validates/touches a device even for prepare. Never run it just to inspect saved evidence. Use exact current APK/protocol paths, not obsolete candidate28 identifiers.

Supplementary reproduction commands from the repo root (write owned scratch outputs; do not execute during this draft task):

```sh
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/measure.py diffusion-focus
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/analyze_diffusion.py
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/long_window.py
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/orb_lifetime.py
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/orb_lifetime.py --ablations
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/orb_lifetime.py --upstream
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/reference_gradient_control.py
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/reference_probe.py
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/reference_probe.py --linear
```

## Final ZIP inventory — not yet packaged

Include a final handover, final tested source/PR snapshot, final ROI decision/rationale, issue table with observed facts versus hypotheses, exact reproduction commands/dependencies and complete SHA256+byte manifest. Include final baseline/candidate audit and comparison exports, input equivalence, pilot checks, driver/APK/core/source/observer identities, preset/source-family index, failure/attempt classifications, checkpoint acknowledgement and restoration instructions. Each confirmed unresolved issue needs exact preset+textures+PCM, relevant raw metrics/logs, matching baseline/candidate/reference frame PNGs, size-band images, native capture hashes, and at least a short motion strip/GIF or lossless adjacent-frame pair. A contact sheet alone cannot establish motion.

For Royal191 include `results-diffusion-long.json`, attached nearest/linear reports and positive gradient controls, plus `diffusion-long/jobs/$$$ Royal - Mashup (191).milk-{c665,q1330,q2160,diff1330,diff2160}-<worker>-r{1,2}/five.npz` and matching metrics/PCM/native checksums. Generate labelled current lossless images from these arrays during final packaging; original `sheet-royal-mashup-191-milk-f2.jpg`/`f4.jpg` supplies historical context only. Include matched actual-core Royal sheets/records, clearly different from the direct-engine research.

For ORB include `results-orb-lifetime.json`, `results-orb-ablations.json`, `results-orb-upstream.json`, exact worker metadata and at least 4/8/16/32/64 s PNGs from classic665, quad1080, prequad665 and upstream665 at 30/60 fps; include ablations and full-stream hashes. Original MilkDrop reference is a named missing artifact, not replaceable by stockprojectM.

For uniform diffusion/fidelity research include focus/float/original-read/long reports, named source presets and matched lossless frame samples for Flexi, Cartoon, Nuclear, rce, penattrition and AcidMandala. Include original user folders' README/results/scripts/census, relevant patch sources and selected mechanism sheets. Preserve invalid experiments only with explicit INVALID labels and explanations. Include sampler proofs and0025–0029 regression controls as resolved context, not unresolved issues. Include161/430 original bytes, diagnostics, actual recovery image/manifest, healthy control hash report and final fidelity verdict when available. Failures without frames need failure logs/stage/path/identity; a missing image must be explicit.

Keep huge raw datasets out of the compact ZIP when a **checksum-verified, acknowledged remote checkpoint** covers them. Core checkpoints live on `evidence/quad-lines-core-corpus` under `core-corpus/remote-checkpoints/<protocolSHA>/batch-*.zip` with adjacent JSON archive hashes and per-file/chunk manifests. Include exact remote commit, protocols, archive list/checksums and restore code; no moving-branch-only links. The snapshot remote commit is `55ea3d33709437754e101c2e20d9013c29198387` and will be obsolete by final packaging. Verify downloads/archives, restore into a new scratch destination using `checkpoint.restore_files(backup_checkout, protocol_hash, destination)`, then audit restored identities and all retained-file hashes. Do not overwrite live data. Adjacent archive JSON and `checkpoint-manifest.json` are required; shared 8 MiB blobs must be concatenated by alias and full-file checksum verified.

The separate stopped direct-renderer checkpoint branch remains supplementary. Do not claim current feedback/original-user raw arrays are remotely covered merely because core checkpoints exist: inventory and back up any uncovered selected research before linking remotely. Approximate locally inventoried logical sizes: diffusion-focus 978 MB, diffusion-long 227 MB, ORB lifetime 66 MB, attached nearest 22 MB, attached linear 20 MB, low-control 52 MB. Exact duplicate hardlinks preserve paths; logical size differs from disk blocks. Avoid bundled binaries/scratch build trees if pinned-source rebuild plus verified checkpoint suffices; never delete originals or worktrees as part of packaging.

## Source checksum inventory for this draft

This table hashes read files, not their interpreted correctness. Refresh final manifest after corpus/candidate/ROI completion; dynamically advancing status/remote JSON are excluded. Paths prefixed `ORIGINAL/` resolve beneath `/Users/jneerdael/Scripts/Projectm-TV/docs/superpowers/evidence`; all other paths resolve beneath this evidence directory.

| Source path | Bytes | SHA256 |
|---|---:|---|
| `README.md` | 17586 | `e2d4ee8ae85162a45889d9dfe1a028984aa60a3ca8b41e3109e29205a349102c` |
| `core-corpus/PROTOCOL.md` | 9068 | `627b84dcf0d48061788ffe23268b07753b905bbfb2666bb20360ef79b87c60e0` |
| `core-corpus/RUNNER-V2.md` | 1588 | `7e28570e14a2af1617b615fa55ca664c9e08eed2b4d230ce802600822826ae8f` |
| `core-corpus/COVERAGE-HANDOVER.md` | 3248 | `b13d54ad45fa5fd0c305895335232d88b588f86f88449a388b1c58b275fcc52d` |
| `preset-sets.json` | 9450 | `d38f904e7b501a1cea40945ed736b57bc71a492527b0f846c3054f1ae89d9a04` |
| `results-diffusion-focus.json` | 30305 | `671f2a31d2fd72c6240f6a4d83016eafcb0d54fdaff3ee0a6ea0266374daf3f1` |
| `results-diffusion-long.json` | 8989 | `25444ef568936958c3e1433b0d9caf8bf6c98458bb08a20e8f5fda98efab7edb` |
| `results-diffusion-float.json` | 9262 | `4c9b953e7b9433b2f80369c1d8c41ed4faee95bd95baba90e1c24fb765e8c9c2` |
| `results-original-read.json` | 3059 | `cd06faa5cdd224a9ab12d1bb620291bb2a1c9fb03fbf9fc84d3d348863918f7b` |
| `results-orb-lifetime.json` | 431364 | `7dfe0632588cad3ade3966236bbc38fb24dba85fcccda1910eeb46135069c3da` |
| `results-orb-ablations.json` | 287437 | `9566afdd6beb3fccf085e775107f390e3df838b1eaa937308d20b65f3f7c1314` |
| `results-orb-upstream.json` | 144531 | `c61475fa97ac0b514588ea74a7adb73d668e05e6a4b78aaa7e14afd7db64062e` |
| `results-reference-feedback.json` | 1825 | `cb8617a0867c7fb7d279975022baaf463fc58432e3d98ac56ec4fc98c0f5099a` |
| `results-reference-feedback-linear.json` | 1832 | `df6391a2b00a48d5ea4ca514298d3ce0549b2a8ed62aeac8557854a2278519ab` |
| `results-reference-gradient-control.json` | 2874 | `24f508c50d9f36c449c5953bb7da74fe64948aff58b97e1706759262be956e1f` |
| `results-reference-feedback-linear-gradient-control.json` | 2872 | `5ebf79a72e273289833a6149c3ad0df7426ffe54e56d2ff0e2e834582b2b2969` |
| `core-corpus/baseline-failure-observations.json` | 16523 | `dc205a0c51d3fc3a9a6e00bcd962bde737d4b1e388cdcdbc9c433ed4ffc11b32` |
| `core-corpus/diagnostic-presets/manifest.json` | 7845 | `3edff33beae2e6729628a60f0316edf21dc14f4dc7a513848b880d5758cee512` |
| `core-corpus/diagnostic-presets/per-frame-fallback/actual-core-recovery.json` | 1557 | `2523d1be84e9a967088ceb50f510bfe9bb17b6d6b7cc031dad3098dc50a6beec` |
| `core-corpus/diagnostic-presets/per-frame-fallback/healthy-controls29.json` | 2461 | `276249baedb896eaeb47886ccd9aa3bb8a194a82723bcf1d1b384b8e6cc5db32` |
| `core-corpus/physical-candidate28/image-manifest.json` | 1296 | `9d5a42733e5ccff4f6d0f067eacb991b15fee9c30233c75e5a529eee0ad8ac95` |
| `proofs/sampler-presets/manifest.json` | 19313 | `6a4938837dd3b1fcfa3f64e61d3bab6a9ebdb760cbcb49517fe82c7280fcfc84` |
| `ORIGINAL/0022-feedback-diffusion-poc/README.md` | 14440 | `d67a46541a73e6c608761cfd2f55e1d15be36cc0dfac596214f9bf19a49a160e` |
| `ORIGINAL/0022-feedback-diffusion-poc/results.json` | 215169 | `00cc84edb8e3fb423ce3a0676b693f50ebd9d89858279bddb961c0a4f8771bb9` |
| `ORIGINAL/0022-feedback-diffusion-poc/raw.json` | 1721465 | `219a6d5547d1d8fa9268396463ba36807fd3f2231ef0e64ddd53e490e0e60e05` |
| `ORIGINAL/0022-feedback-diffusion-poc/run.py` | 6127 | `4412d0ecbb4d573c519be16dd7805a214c9cb1815e2ab469ed0e17467cc9876b` |
| `ORIGINAL/0022-regressions-191-hexcollie-matrix/README.md` | 8755 | `d419f42e806103cb24f6f616c26676bf2683b70c779953baf92213c821e77502` |
| `ORIGINAL/0022-regressions-191-hexcollie-matrix/results.json` | 61841 | `8bc09b9ff5867c9e24c66c145e61bfef063c497b7e769731199d67cde0cc1202` |
| `ORIGINAL/0022-regressions-191-hexcollie-matrix/raw.json` | 579961 | `6d84316c263f27debc15e17a24f5ff7ac20cad7c0ed1aacd67b9f2c95f37ca6d` |
| `ORIGINAL/0022-regressions-191-hexcollie-matrix/run.py` | 6428 | `71dd925573b0b06c674f38b03a945667a0310b8511596dd48b333e5f4ed61d50` |
| `ORIGINAL/shifter-qload-acid-mandala-4k/README.md` | 13225 | `e16b6d4ce06eb123d44a9fbd6be6870327c600c7e69e8401b1a513b9f19e070f` |
| `ORIGINAL/shifter-qload-acid-mandala-4k/results.json` | 236416 | `12091971e37b375bb2ea2c26228c7c3f95816a9a70d720f318114f040d25a29b` |
| `ORIGINAL/shifter-qload-acid-mandala-4k/raw.json` | 851665 | `29a36b1e2b0e243fb0accff1d88fd2ad456960e6f6e514af88fd1af29907dafc` |
| `ORIGINAL/shifter-qload-acid-mandala-4k/run.py` | 5793 | `4242b227794297b22e3f9565bbcf284fd316acedfb30a1a3af05a66d19ccfc6d` |

Final packaging remains pending. No unseen changed preset is classified as degraded here.
