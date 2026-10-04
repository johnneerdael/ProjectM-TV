# Shared corpus integration

The corpus owner is `.worktrees/quad-lines-follow-ups`. Reuse its actual Android
core baseline rather than launch a second full baseline scan. On 2026-10-04 its
Mac-emulator selected-capture controls rendered 480 frames in 1.67–2.52 seconds
per job on three presets. The user reports 15–20 hours for the shared run.
These are emulator throughput controls, not TV playback FPS measurements.

`source-copy.json` records the exact harness/builder copies from peer commit
`0c4f98b`. Copies build only in the recovery worktree's private scratch area.
The peer worktree, emulator, installed package and corpus outputs are read-only
inputs to this integration. Do not install our candidate on its emulator while
the corpus owner controls it.

Prepare the recovered diffusion candidate with the shared harness:

```bash
build/preset-lab-venv/bin/python docs/superpowers/evidence/0025-feedback-diffusion/shared-core-corpus/build.py candidate --commit cc3ca34
```

The shared baseline is core commit `a59b4e5` with patches 0001–0024. Our candidate
uses recovered source `cc3ca34`, adding exactly recovered patch 0025. The two
core wrappers differ in preset-selection bookkeeping; record that difference
and verify its irrelevance to the one-eligible-preset/no-switch experiment.
Do not claim the entire production core source is byte-identical.

The shared protocol uses `(frame+1)/30`, sixteen bottom-up native captures and
256×144 bilinear thumbnails at 1330. Our earlier TV pilot uses `frame/30`, eight
top-down native captures and 1182-pixel area reduction. These raw rendered
records cannot be pooled. Use the common shared harness and clock for our
candidate so comparison to the shared baseline is valid.

Existing 1330 corpus rows can supply captured-frame brightness, colour and
thumbnail differences. They cannot reconstruct the spec's 1182-pixel image MAE
if only 256-pixel thumbnails remain. Authored-resolution and native-4K evidence
require their respective matched jobs; describe missing metrics explicitly.

The peer TV pilot's earlier report had seven of eight full/selected equality
checks pass, with one baseline Echasketch mismatch. The new Mac-emulator epoch
passes all eight checks; the independently reviewed report SHA256 is
`ba49e6f7796480f0190731f980ccb39847ddf2b22c8c4f155c9e35210e0cee82`.
Never merge failed or cross-device protocols into successful coverage.

## Prepared candidate

The shared-harness build completed successfully. Candidate APK:
`build/follow-ups/core-corpus/candidate-cc3ca3448bc7-0b43830171d9/candidate-core-corpus.apk`.
SHA256: `a4eb41e338fdf8aa1e480abe8f49304c91e1857d5596221f3735aa7a7d646364`.
Embedded core ELF SHA256:
`ab779853fe58e6d55c8a0d0aa6ce47a1ab0c73c2c69d045e538cb2c7c6f9286a`.

`candidate-worker.json` preserves the full build identity.
`compatibility-proof.json` confirms exact equality to the peer baseline for
harness sources, instrumentation identity, engine-instrumentation diff,
core-clock diff and the common twenty-four patches. Both compiled ABIs include
all three actual core native units. The APK has not been installed on the peer
emulator and has not yet produced shared-protocol candidate measurements.

## Live baseline and prepared comparison

The corpus owner started the baseline-only scan on `emulator-5580`, PID 41990,
in `build/follow-ups/core-corpus/measurements-core-emu-baseline-v1`.
Its immutable protocol SHA256 is
`369263c90d7089ebfebb6fcf3609b5f2554899e26bf7ef321cad1800f36b8180`.
The owner supplies remote backup and a verified-completion notifier. Do not
start a competing emulator job, replace its APK, modify its worktree or launch
another baseline/notification watcher.

The exact shared host runner and its 31 passing tests are copied here.
`candidate-protocol.json` prepares our candidate while retaining the baseline
role, device, stimulus, inventory, settings and capture protocol unchanged.
Its SHA256 is
`8875482343c04b8c29deba8638fe12b5dc2bf1124612e7a9d57255ca40a822fe`.
`shared-baseline-readiness.json` verifies matching render-input signatures for
49 already completed baseline rows. Original baseline protocols, row paths and
payload hashes remain explicit; they are not relabelled as new measurements.

After baseline completion and backup verification, run only the missing
diffusion-candidate pilot and candidate scan. Reuse the source baseline rows
by exact `render_input_sha256`. The candidate still needs its own pilot;
the peer's candidate pilot tested different rendering fixes and does not
validate diffusion. The shared owner's emulator lease must be released before
installing our APK. Prepared metadata is not an automatic job queue.
