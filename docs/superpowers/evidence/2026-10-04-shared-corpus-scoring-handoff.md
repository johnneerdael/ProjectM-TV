# Shared corpus: inputs needed to complete the audience review build

Audience branch: `feat/preset-audience-scoring`.
Shared corpus owner: `followup/quad-lines`.
The duplicate published-core corpus coordinator is stopped. Do not restart it.

## Existing coverage

The stopped 9,606-file inventory has 144 scored records, three originally
unresolved records, and 9,459 missing records. `score_audit.py` recomputes all 144
existing scores successfully against their pinned model and measurements.
Separate diagnoses now produce finite values for all three unresolved presets:

| Preset | Diagnostic score(s) | Measured motion-transition support |
|---|---|---|
| `$$$ Royal - Mashup (249).milk` | 74.80676144 | 54.04% |
| `$$$ Royal - Mashup (28).milk` | 20.00770025 / 22.25905155 | 17.27% / 17.83% |
| `$$$ Royal - Mashup (29).milk` | 13.70576475 / 13.18608791 | 2.23% / 2.23% |

These are separately identified measurements after the local-contrast fix, not
rewrites of the original run. Two repeated cases agree within five score points.
Sparse correspondence and a finite point score do not establish perceptual
accuracy. Original failures, full diagnostic captures, hashes and numerical
descriptor reports remain available. Evidence is in
`fixtures/sparse-core-motion-remeasurement.json` and
`fixtures/targeted-sparse-core-repeat-proof.json` under `tools/milk-analyzer/`.

## Continuous measurements required by the current model

The inspected selected-capture schedule contains eight isolated adjacent frame
pairs. It has no three consecutive frames, so it cannot provide consecutive
velocity changes. It also leaves most transitions unobserved, so counting its
flashes as the full interval would be incorrect. Do not fill missing terms with
zero, concatenate separated pairs as a movie, or refit weights to conceal the
missing measurements.

If the shared owner supplies audience measurements, record the following with
an explicitly new immutable protocol when necessary. This is a handoff request,
not authorization to modify that owner's branch, running jobs or pilot evidence.

1. Retain the complete measured display-frame sequence, or compute and retain
   equivalent descriptors on **every** measured frame. A practical transfer
   format is RGB8 at a declared small analysis viewport; 128×72 is the current
   audience model's viewport. Avoid uploading full-resolution videos merely
   to calculate these statistics.
2. Preserve exact time/frame indices, warmup boundary, dimensions, orientation,
   resampling operation and quantization. Use continuous 30fps measurements for
   the current model, with 360 measured frames after the declared warmup.
3. Feed top-origin, normalized RGBA fields into `DescriptorStream`, adding
   `time=frame_index/30`. Keep unknown correspondence explicit. If transmitting
   frames, the host can accumulate descriptors without retaining videos.
4. Record the four feature values: coherent brightening-plus-darkening
   transitions per measured second; median speed in viewports/second; mean
   acceleration in viewports/second²; matched brightness-change P95. The last
   three are in `descriptors['motion']`; flash counts and the paired-luma-area
   product are in `descriptors['flashing']`.
5. Preserve `frames_measured`, settings, motion-support fraction and the complete
   descriptors. Uniform/stationary observations must be direct per-frame
   observations, rather than inferred from failed flow. Their special handling
   is documented in `core_corpus.py` and `score_audit.py`.
6. Join records by exact original preset filename **and** SHA-256. Record
   requested/current preset names, load/fallback failures, model identity,
   PCM hash, core library identity, instrumentation identity, GL renderer,
   resolution and descriptor implementation hashes. Keep baseline and candidate
   roles separate. A successful wrapper draw is not proof that custom shaders
   compiled instead of falling back.
7. Different drivers, PCM, initial feedback and viewport settings require
   explicit comparison/calibration evidence. Instrumented baseline/candidate
   artifacts are distinct from the unchanged published AAR. Do not relabel
   their records as measurements from the exact published release.

This does not require rendering the whole collection before source predictions
can be used. Source predictions may provide records under their own declared
inputs and interpreter identity; native numerical measurements supplement gaps
and verification. Both need complete inputs for the selected score model.

## Output and build boundary

The review asset export checks every file against the published AAR, requires
complete finite scores, recomputes their arithmetic and uses these inclusive
bands: Chill 0–30, Normal 25–75, Party 70–100. Relative ranks are separate.
The app code uses a separate debug application ID and displays the intensity
and relative rank of the current preset. The full requested build remains
pending until all 9,606 scores and their provenance are available and verified.

Useful entry points:

- `tools/milk-analyzer/descriptors.py`: streamed measurement calculations.
- `tools/milk-analyzer/profiles/audience-model-v1.json`: pinned provisional model.
- `tools/milk-analyzer/score_audit.py`: model/feature/descriptor arithmetic audit.
- `tools/milk-analyzer/audience_export.py`: complete review asset export.
- `docs/superpowers/specs/2026-10-04-preset-audience-review-design.md`: build contract.
