# Six-area audit delivery checkpoint

Date: 2026-10-08. Branch: `feat/predictor-visual-loop`.

## Disposition

- **31 I and two M:** independently reviewable library handoffs saved and ranked by investigation criticality in `/Users/jneerdael/Downloads/projectm-library-audit-handoffs-2026-10-08/INDEX.md`. All 33 IDs, file hashes, ranks 1–33 and original audit hash were rechecked. Conditional lexical candidates are not runtime-confirmed affected presets.
- **D01:** corrected `draw_borders` attribution to distinguish MilkDrop2 rotated fans from the target library's eight-triangle mesh. No border math changed; M02 remains library-owned.
- **U01:** in progress. Supported operators and a two-target coordinator have source-unit controls, but full `forecast_source` integration and published-AAR high-resolution qualification remain required. Its high-resolution guard is retained.
- **P:** zero confirmed entries in the frozen audit. This does not prove the predictor has no bugs.

## Understood U01 operations

`authored_canvas.py` reproduces the positive half-away integer canvas decision, bottom-to-top float32 block reduction, stored RGBA8 downsample, bilinear presentation and block/channel headroom-limited zero-mean residual. `detail_pipeline.py` keeps authored recurrence separate from native warp/geometry and composites the native target. Authored and native motion vectors consume the previous authored UV map with distinct target-size trail minimums. The authored warp is evaluated before current geometry; native detail combines before native geometry. Blur-before-motion versus delayed blur follows shader texture dependencies.

Main initialization can have different reported pixel dimensions from the first frame: for native 1920×1080 under physical 4K, initialization reports 1280×720, then a scale-2 detail canvas reports 960×540. Custom contexts have no registered pixel-dimension inputs. Scene warp raster extent is separate from scene/EEL extent. Native line and dot styles use explicit reference dimensions; zero reference selects the authored canonical GL path.

Medium/High gain changes preserve authored state. Standard/positive-detail changes rebuild authored feedback from native **pre-composite** feedback, preserve the same-size UV map and skip the first motion-vector draw while retaining blur history and equation/frame counters. Failed paired stages roll back both numerical pipeline states. GPU resource failure/fallback and live render-size changes are not certified by these controls.

Primary reference: original MilkDrop2.25c source at `/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code`. Native two-target extensions are deliberately retained from the exact 14-patch TV source at `build/visual-loop/source-pr57/production-engine`; do not replace them with literal MD2 rendering. Original MD2 has no authored/native two-target detail layer. Native 4K policies and intentional fixes must survive library handoffs.

## Validation

Full prepared analyzer suite: **1,565 tests and 92 subtests passed in 79.72 seconds**. Explicit adapter paths used source49 baseline, source50 clock/v2.3.16, source51/v2.3.17, source2321, source2322 and source-pr57/v2.3.25. Strict `build/docs-venv/bin/python -m mkdocs build --strict` passed. Tests are mathematical/source controls, not rendered appearance or classifier certification.

Latest published full AAR downloaded and checksum verified: **v2.3.27**, release commit `120547f3fafe475c86ffc3392fb94389841d08f0`, AAR SHA-256 `17f17cd4914bc68d64229c3840f703c2b9c47465744f4aa92d36b52984116325`. This checkpoint does not claim runtime qualification of that new artifact. Exact component hashes and delivery identities are in [checkpoint.json](checkpoint.json).
