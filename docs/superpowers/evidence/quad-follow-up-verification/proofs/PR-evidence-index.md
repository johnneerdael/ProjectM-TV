# Per-change PR evidence

Each image uses actual engine frames, test output, or measured driver objects. A rendered image is not
used to imply a diagnostic/resource change. PNGs are ready to embed; full source data and hashes remain
alongside them. These artifacts were pushed on `followup/quad-lines` in `9dd8875`.

| Change | Image | Proof and limits |
|---|---|---|
| Preserve shader diagnostics | [Before/after](01-diagnostic-preserved.png) | Standard-handler RED/GREEN with a labeled artificial diagnostic string; not a fabricated driver screenshot. |
| Free vertex shaders on fragment rejection | [Measured object counts](02-vertex-shader-lifetime.png) | Fresh CGL endpoints: 1/16 live leaked shaders before, 0/0 after; no invented intermediate values or memory estimates. |
| Optional diffusion shader fallback | [Load failure and actual fallback frame](03-optional-shader-fallback.png) | Before emits no frame; after pixels and full frame hashes match classic baseline. Research-only until diffusion is promoted. |
| Deterministic CPU-bound transition test | [Failure/pass evidence](04-deterministic-transition-test.png) | Test-only correction; no production FPS improvement or statistical flake-rate claim. |
| Keep explicit warp sampler modes | [Rendered sampler comparisons](05-warp-sampler-binding.png) | Fractional/out-of-bounds fixture; correct aliases provide independent render oracles. Public-API tests and driver traces support the result. |
| Isolate laboratory shader randomness | [Actual repeated-frame differences](06-analyzer-repeat-delta.png) | Analyzer-only change; before repeats drift, after all frame hashes match. Does not alter production randomness. |
| Preserve preset load/compile diagnostics | [Actual RED/GREEN tests](preset-diagnostics/07-preset-diagnostics.png) | Three exception classes retain their owned message through public failure events; six tests fail before and pass after, full host suite169 passes. No preset acceptance/rendering claim. |

The shader/transition/fallback sources are in `manifest.json`, `raw/`, and `allocation-builds.json`.
Sampler and analyzer sources are in their numbered reports and `additional-proof-sources.json`.
The original 46-file export has `artifact-index.json`; later additions have separate source hashes.

Nine matched actual-preset images from the corrected deterministic sampler comparisons are in
`sampler-presets/`, with their source and frame hashes in `sampler-presets/manifest.json`.
Rejected/invalid feedback probes remain labeled experiments and are not production fixes.
