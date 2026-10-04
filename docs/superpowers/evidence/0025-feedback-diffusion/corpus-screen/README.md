# Full-corpus screen runner

`screen.py` renders original corpus assets using frozen baseline/reviewed workers. It does not build engines, edit presets, call the TV, or use the historical PNG cache.

The default sparse protocol simulates every one of480frames with the16s bass0.30 PCM and captures indices120,150,180,210,239,300,390,479. Each4s/12s summary uses five selected frames. These are sampled metrics under common16s audio, distinct from historical whole-window means and the historical8s FFT-generated audio. Historical82-preset data can be external validation, never pooled into this protocol.

Seven profiles run sequentially per preset: baseline authored, baseline authored repeat, reviewed authored/off, baseline/candidate1330, and baseline/candidate2160. Authored/off identity and repeat stability refer only to captured raw-frame hashes. Screen gains remain preliminary; changed/outlier cases need active repeats and authored size-band controls.

From the repo root:

```bash
build/preset-lab-venv/bin/python docs/superpowers/evidence/0025-feedback-diffusion/corpus-screen/screen.py init
build/preset-lab-venv/bin/python docs/superpowers/evidence/0025-feedback-diffusion/corpus-screen/screen.py run --limit 3
build/preset-lab-venv/bin/python docs/superpowers/evidence/0025-feedback-diffusion/corpus-screen/screen.py run
build/preset-lab-venv/bin/python docs/superpowers/evidence/0025-feedback-diffusion/corpus-screen/screen.py status
build/preset-lab-venv/bin/python docs/superpowers/evidence/0025-feedback-diffusion/corpus-screen/screen.py export
```

`init`, `status`, and `export` launch no render workers. The author of the runner has not launched renders. Parent review/pilot precedes the full scan.

Use `--presets outliers.txt --repeat 1` for a later repeat round using the same source/worker/config manifest. `--repeat-all` runs two complete seven-profile rounds. `--protocol full` uses the frozen original full-readback executables and separate4s/12s PCM jobs; use a different `--work` directory because protocols cannot mix. `--start` and `--limit` permit a bounded pilot or manual sharding; one writer is permitted per work directory.

Default timeout is60s per job; timeout/failure rows are retained as unclassified. `--minimum-free-gb 4` stops before launching/persisting a job when disk is low. Dimensions,30fps,4s warmup, seed12345, source hashes, texture hashes, worker hashes, capture indices, protocol and runner hash are frozen. Resume refuses changed inputs.

SQLite commits each job atomically. Only the current preset's authored downsampled frames are retained temporarily in one compressed NPZ for MAE comparisons (at most~19MB for the sparse8captures). No PNGs or full-frame sequences are saved. After committing metrics, selected audio-band rows and diagnostics, transient job directories/all-frame band traces are deleted. The authored cache is deleted when that group finishes. Stderr retention is capped at1MiB/job, with full log length/hash and truncation flag. Read-only status/export can run while the writer is active.

For authored luma below0.001, exact luma ratio is null. A finite regularized ratio is retained for inspection, with absolute brightness error and `dark_authored=true`; it must not turn near-black numerical differences into validated brightness regressions.

Compile-stage messages distinguish reported success/failure, no-shader cases and unknown visibility. Successful native exit alone never claims shader compilation passed. First-occurrence keys match native case-sensitive SPACE/equals parsing; shader code stops at the first missing numbered key.

If a missing authored cache must be regenerated and its captured hashes differ, prior comparisons against that reference are invalidated, and the regeneration flag persists. Failed/unstable/off-path-mismatching groups remain provisional. Repeat/off-path flags must be joined across each group before counting preliminary comparisons; they are not acceptance or a merge recommendation.

Synthetic checks (no GPU rendering):

```bash
build/preset-lab-venv/bin/python -m unittest discover -s docs/superpowers/evidence/0025-feedback-diffusion/corpus-screen -p 'test_screen.py' -v
```
