# Actual Android core evidence

Fresh device measurements on 2026-10-04, approved serial
`192.168.51.53:5555`: Ugoos AM9 PRO, Mali-G310, Android 14. These measurements
use the TV core AAR through its production JNI API. They are distinct from the
older desktop diagnostics and from the AM6 GPU-cost requirement.

## Published binary anchor

The downloaded [v2.2.1 core AAR](https://github.com/johnneerdael/ProjectM-TV/releases/tag/v2.2.1)
matches baseline source `5681852f9497f320e57b8a5dd40c076d0f5a6b18`.
Its SHA256 is
`4c960385cd0afb7007ed08f99e0e04836c243f950e61f3e6e5dc4d9e77c8a440`.
The unmodified published binary completed 480 Acid Mandala frames through the
core API, with correct preset ownership, no reported GL error, and successful
core/EGL cleanup. All eight downloaded capture RGB/PNG hashes match.

`published-smoke-manifest.json`, `published-smoke-capture-verification.json`
and `published-smoke-instrumentation.log` preserve this result. It uses real
time and is explicitly a nondeterministic smoke test, not fidelity ground truth.

## Matched instrumented pilot

`frozen-manifest.json` records all 9,606 assets, common PCM and settings,
matched AAR/APK identities, source instrumentation and runner/summary hashes.
`baseline-source-identity.json`, `candidate-source-identity.json` and
`worker-apks.json` preserve build provenance. The candidate uses the exactly
recovered patch series `44381ce5cd09e605e4393bd5b2de3fe9273d59b916e0f5bb96010107c8b18479`.
Clock/RNG instrumentation is identical on both sides; neither instrumented
laboratory AAR is the byte-identical published binary.

The first full pilot is **Royal Mashup 1**, not Royal 191: fourteen successful
fresh-process jobs, seven profiles repeated twice, each rendering 480 frames.
All seven profiles repeat with identical hashes for all eight captured frames.
The candidate's authored/off output is also byte-identical to the baseline.
`royal-1-pilot-jobs.jsonl.gz` preserves complete job manifests and measurements;
`royal-1-pilot-proof.json` records the checks and payload hash.

| Render size | Window | Baseline image MAE | Candidate image MAE | Candidate / authored luma |
| --- | ---: | ---: | ---: | ---: |
| 2364×1330 | 4 s | 0.004571 | 0.002983 | 0.998086 |
| 2364×1330 | 12 s | 0.004738 | 0.003185 | 0.996255 |
| 3840×2160 | 4 s | 0.005265 | 0.003173 | 1.003694 |
| 3840×2160 | 12 s | 0.005584 | 0.003135 | 1.001830 |

Each metric is a five-frame sample under common 16-second audio. Captured
hash identity is not an all-480-frame proof. The small brightness error rises
in some comparisons despite better image MAE; no size-band acceptance or
population-level gain claim follows from this one preset.

Total pilot wall time was 356.53 seconds, including process startup, rendering,
capture encoding, transfer and validation. Extrapolating this single preset
to all 134,484 repeated-profile jobs would take about **40 days** continuously.
That is a planning estimate, not a measured corpus completion time. These
durations are not FPS benchmarks: capture/readback costs are included.

## Status and continuation

The live resumable database is
`.worktrees/native-feedback-recovery/build/core-corpus/screen-v3/screen.sqlite`.
Whole-corpus validation is incomplete. Known-problem presets are prioritised
before the alphabetical scan. The 1330 default remains unchanged; the evidence
does not yet justify merging the Native feature.

Runner usage and limitations are in `tools/core-corpus/README.md`.
Source checks pass: 24 core-builder/runner tests and 15 summary tests.
