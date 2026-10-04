# Raster subpixel precision and refreshed source gaps

A frozen horizontal motion-vector forecast predicted its initial segment and
coverage but failed the one-byte RGB8 tolerance: maximum error 10/255 over 30
frames, with two additional faint edge pixels in native feedback. A second frozen
control disabled motion vectors and sampled no textures; it amplified composite
UVs with frac(uv*float2(128,72)+.25). That also failed, with maximum error 8/255.
The original failed predictions are retained rather than retrospectively passed.

Independent EGL/GLES capability queries on the owned API34 emulator report
GL_SUBPIXEL_BITS=4 and the same ANGLE/Vulkan/SwiftShader renderer as the captures.
Trying half-precision varyings/positions did not explain the error. Snapping
source mesh vertices to a four-bit window raster grid, while preserving original
attributes, reduces the diagnostic UV control to at most one byte. This explains
why ideal vertex locations can be insufficient even for a linear UV field.

`composite_mesh.make_mesh` now accepts explicit raster_subpixel_bits (supported
4..16). Interpolation uses separate snapped axes, preserving original source
positions, UVs and polar/hue fields. SourcePipeline and forecast domains expose
composite_subpixel_bits, and history records it. The default unsnapped model is
unchanged; GPU rounding/tie rules are not universally inferred from the bit count.

A different shader, frac(uv*float2(79,47)+.37), was predicted and saved before
native capture under the queried four-bit setting. All RGB8 values match exactly
across 30 frames. This verifies the bounded composite interpolation rule on that
renderer. Remaining motion/warp feedback drift is not claimed fixed, and this
does not establish whole-preset appearance accuracy.

Evidence: `tools/milk-analyzer/fixtures/composite-raster-proof-2026-10-04.json`.
The three source/prediction/capture sets and capability probe remain local under
`build/milk-analyzer/android-learning/`. Raw captures are bottom-row-first and
are explicitly reversed before comparison with top-row-first forecast surfaces.

A fresh source-only audit separately re-read all 9,606 presets with current
reader and lowering identities. It finds 371 presets with known structural gaps
versus 490 previously (119 fewer). The other 9,235 pass structural checks, not
behavioural certification. Token parsing is 99.8589%, which is also not visual
accuracy. Largest remaining families: uninitialized reads116, parsing82, array
layout56, sampler context51 and same-name initialization49; counts overlap.

The updated compact index is
`tools/milk-analyzer/fixtures/source-gap-summary-refreshed-2026-10-04.json`.
Full source witnesses remain at
`build/milk-analyzer/source-refresh-2026-10-04/gap-priority.json`.
