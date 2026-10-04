# Warp raster interpolation and original UVs

The queried Android emulator reports four subpixel bits. The composite correction
alone did not explain accumulated motion/feedback error. The warp mesh also needs
its actual raster vertex locations, and the uv_orig varying is interpolated from
that mesh rather than necessarily equalling ideal pixel-centre UV coordinates.

`spatial.interpolate_mesh` now accepts explicit raster_subpixel_bits and viewport.
It derives the regular native clip-space vertices, snaps window coordinates,
and interpolates unchanged attributes using those physical intervals. Degenerate
boundary intervals select an adjacent nonzero cell for endpoint queries; GPU seam
ties remain unverified. Apple NaN interpolation preserves the same raster geometry.
The omitted-option path is unchanged.

`scene_warp.warp_fields` returns original_uv as well as warped UV and polar fields.
With explicit raster bits it interpolates source mesh positions into that channel.
`SourcePipeline.step` accepts finite viewport-sized warp_original_uv for _uv.zw,
and forecast domains forward warp_subpixel_bits and the source-derived channel.
Tests cover hand-calculated nonuniform raster intervals, invalid domains, original
UV transfer and end-to-end forecasting; review probes cover 400×400 meshes and
tiny/single-axis viewports.

A fresh motion-feedback control changed its displacement to .1875 and froze a
30-frame prediction under explicit four-bit warp/composite geometry. It still
fails the one-byte tolerance, with maximum eight-byte error and two faint edge
pixels differing later in the run. The failure is preserved and is not counted
as a prediction pass or proof that feedback accumulation is fixed.

A separate original-UV gradient control was frozen before capture. All 30 native
frames match within one RGB8 byte. That supports the bounded coordinate path on
the recorded renderer, not universal GPU precision or whole-preset accuracy.

Evidence: `tools/milk-analyzer/fixtures/warp-raster-proof-2026-10-04.json`.
Local source/prediction/captures: `build/milk-analyzer/android-learning/`, cases
`motion-raster-heldout` and `warp-original-uv-heldout`.
