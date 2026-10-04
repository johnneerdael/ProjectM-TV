# Fixed-point main sampling and feedback

Earlier feedback controls showed one-byte filtering differences accumulating
into eight-byte edge drift. Direct RGBA8 sampling into RGBA32F isolated the
arithmetic: twenty float readbacks across 2×2 and 4×3 textures match the
independently computed fixed-point formula exactly when converted to float32.

`unorm_sampler.sample_unorm8` now implements that explicit numerical profile:
16-bit normalized address conversion, integer half-texel offsets, repeat/clamp
handling, high-word bilinear products and UNORM8 conversion. It validates finite
coordinates, declared origin/filter/wrap, supported dimensions and actual byte
texels. It is not a float/sRGB/cube/3D sampler model or a universal GPU rule.

SourcePipeline and forecast domains accept main_sampling_profile, defaulting to
portable. The fixed profile requires quantize=True and applies only to main
feedback lookups, fixed warp and default-composite main sampling. Float motion
maps, blur/external sampling remain separate. History records the selected
profile. Original profile and data validation tests remain passing.

Fresh controls used explicit four-bit warp/composite geometry and the fixed main
sampler. Predictions were frozen before capture against unchanged published
core2.2.4 on the owned API34 emulator. Horizontal displacement .15625 and vertical
displacement .09375 both reproduce every RGB8 pixel across thirty frames each,
including the previously problematic faint-edge accumulation. These are distinct
controls; earlier failed predictions are preserved rather than relabelled.

This verifies the bounded chain on the recorded renderer. It does not establish
equivalence across other GPUs/formats or complete accuracy for arbitrary presets.
Evidence: `tools/milk-analyzer/fixtures/fixed-sampler-feedback-proof-2026-10-04.json`
and the sampler readback fixture from the prior learning step.

Primary algorithm reference: [SwiftShader SamplerCore](https://swiftshader.googlesource.com/SwiftShader.git/+/f7c42b049e6bf0e0e0ba1489a3866cbdf3ab88e2/src/Pipeline/SamplerCore.cpp).
The installed driver revision is not inferred solely from that source reference.
