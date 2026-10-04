# Fixed-point sampler arithmetic

The current motion feedback control begins with a one-byte edge difference and
later accumulates an eight-byte error. Direct sampler tests isolate this from
MilkDrop equations, line coverage and raster interpolation: a constant uniform
UV samples an RGBA8 texture into an RGBA32F target, then reads floating values.
The owned emulator reports the same ANGLE/Vulkan/SwiftShader renderer as the core
captures. These probes do not modify the published AAR or run a preset corpus.

An independent arithmetic reference based on the published SwiftShader sampler
source matches ten 2×2 float readbacks within 5e-10 (decimal serialization error).
It uses 16-bit normalized coordinate addressing, integer half-texel offsets,
fixed-point bilinear weights, truncated high products and RGBA8 normalization.
The exact-centre sample is about .9999694 rather than ideal 1.0, and tiny UV
changes can disappear at the address precision. Float texture sampling and other
formats have different paths and must not inherit this rule blindly.

A separately sized 4×3 RGBA8 texture was then tested with ten readbacks. Extending
the same integer formula by the explicit dimensions matches within 5e-10 there
too. This is evidence for the sampler arithmetic on the recorded renderer, not
proof that the same SwiftShader source revision is installed or that the entire
feedback discrepancy is fixed. Wrapping, origin conversion and pipeline format
integration still require explicit validation.

The initial probe failed to link against the GLES2 import library because its
VAO calls require GLES3 symbols; it was rebuilt against GLES3 before any readback
was accepted. All accepted probes have successful remote exit status, complete
JSON and source/binary hashes.

Evidence: `tools/milk-analyzer/fixtures/swiftshader-sampler-learning-2026-10-04.json`.
Local probe/reference files remain in `build/milk-analyzer/android-learning/`.

Primary source: [SwiftShader SamplerCore](https://swiftshader.googlesource.com/SwiftShader.git/+/f7c42b049e6bf0e0e0ba1489a3866cbdf3ab88e2/src/Pipeline/SamplerCore.cpp).
