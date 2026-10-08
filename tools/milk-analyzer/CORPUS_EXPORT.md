# Run the complete preset export without AI

The corpus runner executes the existing mathematical source simulator and writes
its version1 **47-field feature record** for every successfully computed preset.
It requires no AI service, API key, browser, Android device or native frame capture.
It does construct simulated pixel fields and computes their numerical descriptors.

## One command on the prepared Mac

```sh
./tools/run-preset-corpus.command
```

Defaults: all bundled `.milk` files, **60 frames at 15fps, 854×480**, two isolated
workers, five-minute per-preset deadline, 100 completed cases per ZIP. Output:

```text
~/Downloads/ProjectM-TV-preset-corpus-15fps-480p/
  run-manifest.json
  progress.sqlite
  progress.json
  inputs/
  results/<original subdirectories>/<original stem>.json
  batch-000001.zip
  batch-000002.zip
  ...
```

Running the same command again resumes automatically. Successful, unsupported,
failed and timed-out cases are terminal for that run and are not repeated. Changed
code, binaries, source files, assets or input settings require a **new output folder**;
the runner refuses to blend incompatible evidence into an old run.

A ZIP appears after each 100 completed attempts, not only after 100 usable records.
Each contains `batch-manifest.json`, `presets/<original name>.milk` and
`results/<matching stem>.json`. Original Unicode names/subdirectories and exact
source bytes are retained. Each manifest records source/result hashes and status.
A final partial ZIP is flushed at normal completion or CtrlC. Completed individual
JSON files are available immediately, even before a group reaches 100.

## Inspect or smoke-test before the full run

```sh
./tools/run-preset-corpus.command --check
./tools/run-preset-corpus.command --limit 3 --batch-size 3 \
  --output ~/Downloads/ProjectM-TV-preset-corpus-smoke
```

Use a different folder for a limited run. Removing `--limit` changes the frozen
inventory; it cannot resume that limited folder as the entire corpus.

Options also include `--workers`, `--timeout`, `--equation-timeout`, `--seed`,
`--presets`, `--textures`, `--binaries`, `--validator` and `--pcm`. `--pcm` accepts
normalized little-endian float32 mono 44100Hz samples of exactly the requested
length; it does not decode M4A/WebM/MP3. Worker concurrency is a runtime setting,
not a reason to change the underlying simulated input semantics.

## Inputs and meaning of15fps

This run simulates **15 state updates per second**, not a 30fps engine with every
other measurement discarded. Sixty updates cover four seconds of declared audio
(59 measured intervals span about 3.93 seconds). Per-frame feedback, RNG and
frame-based equations can therefore behave differently from a 30fps player.
Do not relabel these records as native 30fps fidelity or no-flash certificates.

The default signal is fixed kick/chord/hat synthetic PCM with a declared seed.
Audio is quantized through the existing unsigned 8-bit JNI-equivalent ingress
conversion, then the pinned CPU PCM/FFT/audio functions execute at actual 1/15
intervals. The native audio window retains its existing clipping semantics;
15fps does not mean it processes all 2,940 samples as one FFT window. This is one
controlled context, not evidence for every music genre, listening level or song.

Equation RNG starts from the identified cold-thread seed. Shader random uniforms
use an explicitly declared deterministic MT stream/lifecycle, not a claimed
Android/bionic C-rand sequence. Procedural noise uses the identified source
functions and fixed declared seed. Bundled named textures are decoded through the
pinned source decoder. Random image slots choose an explicitly declared stable
asset by a hash policy; the first filtered binding wins and the slot persists
across both shader stages. These are actual simulation inputs and all appear in
provenance. They do not claim an arbitrary production load picks the same image.
Missing images/prefix matches remain unsupported rather than silently replaced.

The simulator uses the declared Apple GLES numerical/raster profile modeled by
this predictor. It runs on the CPU; that declaration does not certify an arbitrary
GPU. The run is pinned to the source corresponding to the full published 2.3.29
AAR and the current predictor code. It never substitutes an unpatched upstream
library and never renders through a bare `libprojectM` reference binary.

## Results, failures and unknowns

Each JSON is a corpus envelope containing original preset name/path/hash,
`run_identity`, simulation parameters, status, stage, elapsed time and
`feature_record` on success. A computed record has exactly 47 keys; some values
can legitimately remain null with support/unknown reasons. A parser, shader,
resource or mathematical failure has `feature_record:null`, an explicit error
and stage. A worker crash or deadline is likewise preserved. No failure becomes a
fake zero-reactivity preset or a fabricated47-value success.

Progress separates completed attempts from computed records and reports counts
by status. Inspect the failed records before interpreting corpus completeness as
classification coverage. Fixes/retries go into a new run folder so old sealed
archives stay reviewable. No automatic AI diagnosis or correction is performed.

## Recovery and resources

Only one controller can own an output directory. Results and ZIPs are written
atomically; archives are CRC/hash checked. Resume reconciles a ZIP written just
before its SQLite update, refuses changed/corrupt files and never silently
replaces a sealed archive. CtrlC stops only this runner's worker process groups;
unfinished presets remain pending for the next invocation. Keep the run folder,
including input snapshots and SQLite files, together while resuming. Recovery
covers interrupted processes; it does not guarantee survival of abrupt power loss.

Memory and duration depend on shader/geometry complexity. Two workers are the
conservative default; increasing workers can reduce throughput if RAM or CPU
contention dominates. The first bounded real pack smoke case took about 48 seconds
for 60 frames, not a corpus-wide average or ETA guarantee. Some presets reach the
deadline and produce explicit timeout results. Expect the total corpus to be a
long job; incremental batches prevent waiting for the whole corpus before review.

The run retains compact numerical JSON, not simulated RGB videos or native
captures. Disk use is still cumulative for thousands of records/ZIPs. Source and
texture inputs are read-only; neither app/library binaries nor authored preset
files are changed. Do not modify the predictor/adapters during an active run.

## Prerequisites and implementation

The launcher targets this prepared macOS/Linux checkout. It locates
`build/preset-lab-venv/bin/python`, source29 adapters and `glslangValidator` and
provides an actionable error if missing. It does not secretly download a different
engine. See the analyzer README for source-bound adapter setup; those prerequisites
are needed once on another machine. No AI is needed for execution or recovery.

Controller: `preset_corpus.py`; isolated worker: `corpus_worker.py`; deterministic
inputs: `corpus_inputs.py`; durable outputs: `corpus_store.py`. The existing
predictor export is documented in [EXPORT_CONTRACT.md](EXPORT_CONTRACT.md).
