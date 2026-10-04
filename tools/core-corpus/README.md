# Actual Android core corpus validation

These workers call the production `ProjectMJNI` API from the Android core AAR,
with its three native implementation units and complete packaged assets. They
do not call libprojectM directly. The independently downloaded published
v2.2.1 AAR is the source/asset anchor because its release commit is the recovery
baseline, `5681852f9497f320e57b8a5dd40c076d0f5a6b18`.

Published AAR SHA256:
`4c960385cd0afb7007ed08f99e0e04836c243f950e61f3e6e5dc4d9e77c8a440`.
Release: <https://github.com/johnneerdael/ProjectM-TV/releases/tag/v2.2.1>.

`build_core_aars.py` creates isolated source archives and instrumented baseline
and candidate core AARs. The baseline contains patches 0001–0024; the candidate
adds the exactly recovered 0025 series. Both use the same private shader RNG
and logical frame clock. Instrumentation diffs, native compilation units,
asset hashes and AAR/library hashes are recorded in each `source-identity.json`.
These laboratory AARs are distinct from the unmodified published binary.

The worker APKs embed those AARs. Framework Instrumentation creates a GLES3
pbuffer and calls core initialization, public settings, unsigned-byte audio,
render and release APIs. A separate lab bridge exposes only seed, clock and
reference dimensions. Every job runs in a fresh process. Its one-member skip
mask preserves the full packaged index and checks the requested preset name
through all 480 frames. Real prewarming is paused through the production
memory-pressure API.

## Scan protocol

`run_corpus.py` freezes the 9,606 preset files, textures, index, worker APKs,
core AARs, source identities, runner and summary source before device access.
Seven profiles run twice for every preset:

- Baseline classic 1182×665, followed by a baseline repeat.
- Candidate classic 1182×665 with compensation disabled.
- Baseline and candidate 2364×1330 with reference 1024×768.
- Baseline and candidate 3840×2160 with reference 1024×768.

The complete scan is 134,484 fresh-process jobs. Each simulates 16 seconds at
30 fps with identical unsigned-8-bit mono PCM: four seconds of warm-up and
twelve measured seconds. Production core receives 1470 samples per frame and
retains its normal latest-512-sample input. Logical time is `frame / 30.0`.

Eight frames are captured: 120, 150, 180, 210, 239, 300, 390 and 479.
Each 4-second/12-second metric uses five selected frames. Image error is RGB
MAE after area reduction to 1182×665. Brightness, centre RGB, saturation and
Laplacian sharpness are also retained. Captured-frame identity does not prove
the hash of every simulated frame, and sampled means are not whole-window
means. Real-clock published-AAR smoke results are separate from deterministic
fidelity comparisons.

Failures, timeouts, reported shader fallbacks, unstable repeats and off-path
mismatches remain unclassified. Near-black authored references have undefined
brightness ratios. Metric triggers identify cases to inspect; they are not
perceptual acceptance thresholds. Degradations still require authored-size
controls and preset/source analysis before a merge recommendation.

## Run and resume

Create metadata containing baseline/candidate objects with `package`,
`apk_path`, `apk_sha256` and `source_identity` fields. Install only the dedicated
`nl.neerdael.projectmtv.corpusbaseline` and `corpuscandidate` worker APKs.
Then run from the feature worktree:

```bash
build/preset-lab-venv/bin/python tools/core-corpus/run_corpus.py init --work build/core-corpus/screen-v3 --metadata build/core-corpus/runner-metadata.json
build/preset-lab-venv/bin/python tools/core-corpus/run_corpus.py run --work build/core-corpus/screen-v3 --limit 1 --keep-all-captures
build/preset-lab-venv/bin/python tools/core-corpus/run_corpus.py run --work build/core-corpus/screen-v3 --max-jobs 100
build/preset-lab-venv/bin/python tools/core-corpus/run_corpus.py status --work build/core-corpus/screen-v3
build/preset-lab-venv/bin/python tools/core-corpus/run_corpus.py summary --work build/core-corpus/screen-v3
```

Default device is the approved `192.168.51.53:5555`, private ADB server port
5038. The runner refuses a sleeping device and never sends a wake command.
One user-wide lock prevents concurrent corpus sessions on that device.
It verifies installed APK bytes, restores the original debug preset property,
and force-stops only its own worker packages during cleanup. Production app
preferences are not written.

SQLite commits every job before deleting owned transient captures. Temporary
authored reference frames are bounded to the current group. Checkpoints export
JSONL jobs, coverage JSON and per-preset CSV; failed jobs retain diagnostics.
`--keep-all-captures` is intended for a bounded pilot, not the full corpus.
Existing jobs resume without rerendering; `--retry-failed` explicitly retries
failed jobs. A changed runner, artifact or source identity requires a new work
directory. Keep old databases as evidence rather than rewriting their protocol.

Synthetic checks:

```bash
build/preset-lab-venv/bin/python -W error -m unittest discover -s tools/core-corpus -p 'test_*.py' -v
build/preset-lab-venv/bin/python -m unittest discover -s docs/superpowers/evidence/0025-feedback-diffusion/corpus-screen -p 'test_summarize_screen.py' -v
```

The older desktop corpus and diagnostic helpers remain supplementary research.
Their rendered rows cannot substitute for this actual-core baseline.
