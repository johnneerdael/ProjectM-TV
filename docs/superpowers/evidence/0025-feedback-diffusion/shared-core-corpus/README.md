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

The peer TV pilot's latest report had seven of eight full/selected equality
checks pass, with one baseline Echasketch mismatch. The new Mac-emulator epoch
needs its own reviewed pilot before treating its corpus as stable. Never merge
failed or cross-device protocols into successful coverage.
