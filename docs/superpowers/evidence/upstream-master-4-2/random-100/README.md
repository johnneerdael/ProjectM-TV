# Exact random sample and original regression controls

Current integration update (2026-10-07): main PR #50 merged as `dd59a791` and published **v2.3.16**. Its verified unchanged AAR SHA256 is `08e5a1c9c3df1433407769ace6e8fc379566d50402258eef98fe948cb5f708cd`. Custom-pack app/JNI changes are being integrated; historical patch 0050 is ported as current 0010. The v2.3.15 matrix below remains an immutable completed checkpoint. It does not certify the new renderer or latest baseline; fresh source/runtime/image validation and final review/CI remain required.

Completed v2.3.15 checkpoint: all six private workers build and payload checks pass. Final GPU validation passed: all 2,036 source runs, 509 unchanged-AAR runtime runs and 48 image-proof replays are verified. See [the completed evidence](../fidelity-final/README.md); final-head review/CI/release remain separate repository gates. The final baseline is verified official **v2.3.15**, source `43023889ec38cf1250f3bfcaaf079a840acbdf76`, AAR SHA256 `fa4bdd657a592b41eeef7d75c82982bf1fecf5404b99aba8ebba5c56f6a91327`. Older b1/v2.3.11 artifacts remain historical evidence.

The unbiased sample ranks all 9,606 exact UTF-8 filenames by `SHA256(ASCII("12345") + NUL + UTF8(filename))`, then by UTF-8 filename to break a hash tie. Take the first 100 without consulting source features, renderer success or previous images. `sample-preview.json` records that selection before new pixel results; it is not a final release-bound protocol. The final selection additionally includes every required bundled filename from `../patch-regressions/regression-presets.json`, plus midgit. Preserve the inventory's optional historical controls, synthetic fixtures, external witnesses and unresolved aliases as separate evidence; never label them rendered.

The final inventory has 351 required bundled presets. Four overlap the random sample, giving a union of **447** bundled presets. The separately recovered original 0021 external witness adds one supplemental fixture. Source-bound activation profiles give the owner 17-preset Native matrix Standard/Medium/High 4K, and two additional native issue witnesses Standard 4K. The nine source-proven historical q2160 controls in `q2160-profile-evidence.json` also require Standard 4K; one already belongs to the owner matrix, adding eight profile instances. Parser controls otherwise stay at 1080p. This is **2,036 source-repeat jobs** and **509 separately labeled released-AAR runtime rows**, not an indiscriminate all-profile matrix over all presets. The profile assignments are derived from inventory reasons before rendering and frozen in the protocol.

Every source job renders frames **0–479**, seed **12345**, clock **frame/30.0**, the same frozen 16-second unsigned mono PCM, mesh 48×32, and the frozen reference canvas and Native Trails setting for its profile. The 1080p and Standard 4K profiles use reference 1024×768 and Standard (0); Medium/High 4K use reference 1280×720 and Medium (1)/High (2). Every job disables auto changes, beat cuts and blank skipping, uses category `all` and CLASSIC transitions without soft cuts, and selects one exact eligible preset. Source comparisons require both same-role repeats and cross-role equality for every full-resolution, top-down **RGB8** frame, with zero tolerance. Alpha is explicitly excluded. Missing, failed, unstable, changed-artifact or unverified jobs cannot pass.

Unchanged released-AAR jobs invoke production JNI and **do not call the private bridge**. Their clock/RNG remain real and uncontrolled; every-frame hashes establish recorded runtime output, not fixed-seed equality with the source workers. The summary keeps source equality and unchanged-release runtime verification separate. Neither artifact class is silently substituted for the other.

`EveryFrameHashes.java` reuses one full RGBA readback buffer already owned by the worker, one RGBA row, one RGB row and one SHA256 object. It uses GLES-portable RGBA/unsigned-byte readback, reverses row order and excludes alpha while hashing. Ordinary source jobs retain only a bounded 480-line hash stream and manifests. Positive proof predeclares the first three random presets, midgit, the first native owner control and the external witness: frame 120/479 PNG replays must reproduce the entire original 480-frame sequence and decode to those exact RGB hashes. Released-AAR images are captured during the representative original real-clock jobs and stay separately labeled. `witness` reruns the first differing pair and retains its first-divergence PNG, accepting the replay only if its entire hash sequence matches the original run. This measures output, not app FPS; measure the first job's actual wall time before planning run duration.

## Frozen release and regression inputs

Supply a root-verified release manifest, after publication/download verification:

```json
{
  "schema": "projectmtv-verified-release-v1",
  "status": "verified",
  "release_tag": "<actual published tag>",
  "source_commit": "43023889ec38cf1250f3bfcaaf079a840acbdf76",
  "engine_commit": "<exact 4.1.7 gitlink>",
  "includes_prs": [44, 49],
  "aar_path": "<unchanged official AAR path>",
  "aar_sha256": "<verified official SHA256>",
  "ordered_patches": [{"name": "<patch filename>", "sha256": "<patch SHA256>"}]
}
```

Keep the complete ordered patch manifest, not the one-row illustration. The baseline source producer must match this source/gitlink/patch list. The candidate must use the pinned 4.2 engine and incorporate the released source history; candidate patch count is recorded, not assumed to remain three. Both source workers must have a verified private RNG reset after seed setup. Historical constructor resets are accepted only against their recorded source hash; corrected common-JNI resets are recorded separately. A diagnostic producer may alter only the recorded seed-reset bridge, with every parent source rehashed.

The final selection is generated in the run directory only after the released AAR's entire preset catalog matches the 9,606 filename/SHA inventory. It also freezes the regression inventory, exact worker APK/AAR identities, corrected bridge provenance, PCM bytes, helper sources and settings. Changing any frozen input requires a new work directory. The external witness is now recovered exactly. Both possible bundled ORB alias matches are required controls; the historical original is not claimed identified. The inventory preserves this distinction.

## Build private workers

Run from the repository root with JDK 21, SDK 34 and the existing Gradle wrapper. No production source, original AAR or historical worker is changed. Each private worker uses a new `corpusrandom100{baseline,candidate,released}` package, the producer's ABI, and preserves imported native bytes without stripping.

```sh
python3 docs/superpowers/evidence/upstream-master-4-2/random-100/prepare_worker.py --role baseline --source-identity <released-source-producer/identity.json> --release-manifest <verified-release.json> --work build/random100-workers/baseline --build
python3 docs/superpowers/evidence/upstream-master-4-2/random-100/prepare_worker.py --role candidate --source-identity <updated-4.2-producer/identity.json> --release-manifest <verified-release.json> --work build/random100-workers/candidate --build
python3 docs/superpowers/evidence/upstream-master-4-2/random-100/prepare_worker.py --role released --release-manifest <verified-release.json> --abi arm64-v8a --work build/random100-workers/released --build
```

Pass `--jdk`/`--sdk` for another installed layout. `--validation-only` builds a source harness for offline checks before final integration; its identity has `final_eligible=false` and the final runner rejects it. The preparation copies only Java/test configuration, verifies all AAR assets and selected native libraries in the APK, and retains source hashes and the exact harness diff. Source AAR production/instrumentation remains with the existing producer workflow.

## Separate external fixture overlays

The supplemental workers preserve the supplied AAR and every native byte. They add the recovered 47,750-byte preset, SHA256 `990472f4a5af7fbff629fd2340b14753a7fd1ec7ffc77203267dfdfbf4c8e37e`, only to a private APK. The existing `tools/gen-preset-index.py` API must first reproduce the original index byte-for-byte, then produce an index differing by that single filename/weight. All existing preset/texture bytes stay unchanged. Each identity records original/derived index hashes, the exact index diff, generator hash and source provenance. This is explicitly **not** an unchanged primary asset APK. Its job denominator is 9,607, and it is never used for the 447 bundled certificate.

Repeat each preparation command with `--overlay-inventory docs/superpowers/evidence/upstream-master-4-2/patch-regressions/regression-presets.json` and a distinct `--work` directory. Supplemental package IDs use `corpusrandom100supp{baseline,candidate,released}`. Supply all three resulting identities through `--supplemental-baseline`, `--supplemental-candidate` and `--supplemental-released` when initializing.

## Initialize, bound, resume and verify

`init` and `summary` perform no ADB/device operations. Only explicit `run`, `proof` and `witness` commands contact the selected device. Android GPU emulators and physical TVs are supported; software-renderer fallback is rejected for the GPU-emulator scope. Freeze the observed Android user, API, fingerprint and GL vendor/renderer/API/GLSL tuple. Stop on asleep/user/backend changes without waking the device. Acquire the existing shared device lock, use only owned packages/private job paths and restore the original debug preset property after every job.

```sh
python3 docs/superpowers/evidence/upstream-master-4-2/random-100/run_sample.py init --baseline build/random100-workers/baseline/identity.json --candidate build/random100-workers/candidate/identity.json --released build/random100-workers/released/identity.json --supplemental-baseline build/random100-workers/supplemental-baseline/identity.json --supplemental-candidate build/random100-workers/supplemental-candidate/identity.json --supplemental-released build/random100-workers/supplemental-released/identity.json --release-manifest <verified-release.json> --regression-inventory docs/superpowers/evidence/upstream-master-4-2/patch-regressions/regression-presets.json --device emulator-5624 --user 0 --backend android-gpu-emulator --work build/random100-final
python3 docs/superpowers/evidence/upstream-master-4-2/random-100/run_sample.py run --work build/random100-final --limit-jobs 4
python3 docs/superpowers/evidence/upstream-master-4-2/random-100/run_sample.py run --work build/random100-final
python3 docs/superpowers/evidence/upstream-master-4-2/random-100/run_sample.py run --work build/random100-final --shipping
python3 docs/superpowers/evidence/upstream-master-4-2/random-100/run_sample.py summary --work build/random100-final
python3 docs/superpowers/evidence/upstream-master-4-2/random-100/run_sample.py proof --work build/random100-final --limit-jobs 4
python3 docs/superpowers/evidence/upstream-master-4-2/random-100/run_sample.py witness --work build/random100-final
```

The serial is an explicit example, not an implicit allowlist or authorization to run. `--limit-jobs` bounds new work per invocation without changing the frozen denominator. A separate `init --mode explore --frames 60 --preset-limit 1` creates a noncertifying exploratory protocol. Do not promote it to a final protocol or replace failed presets. Verified jobs are revalidated before resuming; failed attempts remain intact and are not silently overwritten.

`summary.json` reports exact source equality, unchanged release runtime, missing/failing/invalid jobs, first differences and unresolved regression evidence. A green source result certifies only the declared union, frames, seed and backend; readiness also requires the positive proof and separately verified released-AAR runtime rows. It does not certify all 9,606 presets, other ABIs/devices, alpha equality or deterministic shipping output. Final CI/review/merge/publication remain separate repository gates.

## Offline validation

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s docs/superpowers/evidence/upstream-master-4-2/random-100 -p 'test_*.py' -v
```

The seventeen controls exercise deterministic ranking, regression/hash preservation, rejection of an old release, every-frame ordering/integrity, bridge-reset ordering, source/runtime separation, complete job counts, frozen PCM and backend identity, required positive proof, source-proven q2160 coverage and a compiled Java top-down RGB/alpha/GL-error control. GPU execution is required before any pixel-equivalence claim.
