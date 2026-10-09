# I31: identical appearance, measurable lower rendering cost

**The gamma-only epsilon patch has a measured performance benefit in the admitted native-M4 workload. It is retained.** The earlier “practical benefit unproven” status is superseded for this backend and boundary case, not for every preset or physical TV.

The unchanged original is `suksma - type o negative - world coming down.milk`: loaded gamma `2.000999927520752`, echo off, built-in composite. Compare the frozen 34-patch engine with its exact single-patch 0019 ablation. Source inventory comparison confirms that only `VideoEcho.cpp` differs; both roles share the same observation harness. Shipping patches and previous workers/captures are untouched.

## Measured result

Actual output is **3840×2160** on **Apple M4 Pro, OpenGL 4.1 Metal**. “Standard” here means the direct engine profile with 1280×720 line reference, antialiasing on and feedback-detail alpha 0. “Classic” uses reference 0/0, antialiasing off and detail -1. Both use the same preset, exact float32 mono PCM, seed 12345, 48×32 mesh and 30 Hz clock.

| Workload | Completed frame, without → with | GPU elapsed, without → with |
|---|---|---|
| Original, Classic | 2.769 → 2.307 ms (**−16.7%**) | 2.405 → 1.944 ms (**−19.2%**) |
| Original, Standard profile | 2.704 → 2.241 ms (**−17.1%**) | 2.307 → 1.847 ms (**−19.9%**) |
| Gamma 2.0 inactive control, Classic | 2.316 → 2.324 ms (+0.008 ms; interval includes zero) | 1.958 → 1.960 ms (+0.002 ms; interval includes zero) |

Actual executed gamma mesh draws are **3 → 2 per frame** in the original, **2 → 2** in the inactive control. All eight balanced blocks favor I31 in both active profiles. Standard's paired-block 95% bootstrap interval is **−0.476 to −0.451 ms** for completed frames and **−0.470 to −0.450 ms** for GPU elapsed time. Inactive control intervals span zero for those endpoints. CPU submission also falls in the active case; the small inactive-control CPU drift is retained in `analysis.json`, not hidden.

## Method and limits

Eight alternating ABBA/BAAB blocks per active profile and four for the inactive control: **80 timed runs, 28,800 measured frames**, plus 120 warmup frames per run. The four exploratory smoke jobs are excluded. There is no readback, frame hashing, PNG encoding, band-file writing or console output during measurement. Completed-frame time is `RenderFrame` plus `glFinish`; GPU time is the driver’s `GL_TIME_ELAPSED` query. The simple clear probe returned zero, but all ten real-draw probe values and every measured GPU sample are nonzero, with 32-bit timer support. All runs report zero GL errors. Timed binaries and sources are hash-bound in `workers.json`.

Statistics use whole ABBA/BAAB blocks rather than treating thousands of correlated frames as independent observations. Reported intervals are a fixed-seed, 100,000-resample paired-block bootstrap. They quantify this experiment’s variability, not universal hardware confidence.

This establishes a lower rendering cost on the M4 Pro for this narrow gamma boundary. It is **not a claim of 20% higher app FPS, physical-TV performance, all-preset speedup or lower Android memory use**. Removing a fullscreen draw saves work when the branch is active; ordinary gamma values retain their counts. A weaker TV GPU may save more or fewer milliseconds or percentage time depending on its fill rate, bandwidth and CPU bottlenecks; hardware power alone does not determine the gain.

## Appearance and the original source

Eight separate selected-frame verification runs use the same two sources/profiles and are outside the timed jobs. Frames **119, 239 and 479 are byte-identical RGB across roles**, and both repeats match within each role, in both profiles. This is a selected-frame result, not all-frame or Windows pixel certification. It explains why the patch can help without a visible change.

MilkDrop’s source uses `.001f` for the gamma-only pass count (`milkdropfs.cpp:4245`). Its `D3DCOLOR_RGBA_01` macro (`:41`) truncates float colour channels to 8-bit integers. For this witness the extra fractional pass has weight `.0009999275`; even a white channel becomes `int(weight*255) == 0`. Thus the otherwise extra draw contributes zero RGB in that original 8-bit diffuse path. This is a code-derived explanation of the effect, not evidence of the author’s historical intent. Our float-diffuse renderer has its own quantization behavior; the separate current images above validate the admitted appearance.

## Records and replay

- `analysis.json` contains all block means, absolute/percentage deltas and intervals.
- `timed-runs.json.gz` retains every independent per-frame timing/draw record for all 80 scheduled jobs.
- `schedule.json`, `job-summary.json`, `inputs.json` and `workers.json` bind ordering, inputs, sources, harness and binaries.
- `visual-results.json` and `visual-jobs.json` retain selected RGB hashes, repeats and separate verification identities. The corrected observer restores caller read framebuffer, read buffer and pack alignment at each read; its PNGs remain under the task worktree’s `build/i31-benefit/observer-restored-bound-replay/visual/`. The initial observer records are retained under `historical-observer/`. Corrected selected hashes equal those initial hashes; no timed benchmark job was repeated.
- `source-purpose.json` records the independent float/pass/8-bit calculation.
- `requests.json` retains all 80 original full timing requests with explicit retained-file provenance. The input-hash bindings are retrospective checks against preserved requests/files, not invented historical before/after mutation observations. Future private runs additionally check inputs before/after.
- `custody.json`, `source-proof/`, `benchmark.py` and `source_observer.py` bind the fixed source/observer recipe and reproducible analysis. `verify.py` reconstructs the frozen patch chain, validates the complete requests and regenerates all statistics.
- `executed-*.py` retain the initial command layout with documented post-review custody hardening; `prepare.py` ports it to an explicit output directory. `capture_visual.py` emits complete corrected observer receipts, input snapshots and caller-state checks.

First prepare the frozen catalog engine with the neighboring [catalog builder](../patch-visual-catalog/BUILDING.md). Then:

```sh
python3 docs/superpowers/evidence/i31-benefit/prepare.py \
  --repo /path/to/ProjectM-TV --catalog-work /path/to/catalog-host \
  --work /path/to/new-i31-proof
I31_PROOF_REPO=/path/to/ProjectM-TV python3 /path/to/new-i31-proof/run.py smoke
I31_PROOF_REPO=/path/to/ProjectM-TV python3 /path/to/new-i31-proof/run.py benchmark
python3 /path/to/new-i31-proof/analyze.py
python3 /path/to/new-i31-proof/link_images.py
python3 docs/superpowers/evidence/i31-benefit/capture_visual.py \
  --repo /path/to/ProjectM-TV --work /path/to/new-i31-proof \
  --output /path/to/new-visual-output
```

The portable adapter changes only repo-path resolution. New machines/compilers require their own worker/input/runtime receipts. The image verification recipe is archived separately; it links an observer worker against the same private static libraries and reads only the three selected frames. Do not mix its timing with the benchmark.

PR66 closeout validation: the actual guide references are checked by the neighboring gallery verifier. Benchmark verification binds source, complete requests, profiles, controls, inputs, workers and every published statistic. Corrected visual verification binds all eight requests and 24 restored caller-state observations. Native sentinel control fails with the initial read helper and passes with the restored helper. Timing data and analysis remain byte-identical to the original measured records.
