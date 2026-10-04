# Non-mipmap texture LOD and bias

The pinned renderer registers wrap/clamp × linear/nearest samplers in
`Renderer/TextureManager.cpp`. `Renderer/Sampler.cpp` assigns the same non-mipmap
filter to GL_TEXTURE_MIN_FILTER and GL_TEXTURE_MAG_FILTER. The native GLSL
generator maps tex2Dlod to textureLod with packed XY/W and tex2Dbias to texture
with packed XY/W. Base-level filtering therefore applies for these sampler
settings; arbitrary mipmapped samplers are not covered.

The interpreter now preserves XY, evaluates W, and explicitly records the
base-level-only sampling effect. Missing or nonfinite selectors remain unresolved.
Both evaluators require mipmapped=False and base_level=0 before accepting that
two-argument sample graph, including imported graphs. A regression first showed
that missing/nonzero base-level metadata could previously bypass this check.

This matters for audio sensitivity: bass in an ineffective LOD selector must not
be scored as visible bass response. A numerical regression varies bass from .1
to 4 while preserving identical sampled output.

Four predictions were frozen before execution against the unchanged published
ProjectM-TV core 2.2.4 AAR on the owned API34 emulator. The warp shader generates
high-frequency red stripes; fixed composite coordinates select a black stripe.
Bias and explicit LOD at -8 and +8 all yield RGB8 [0,64,191] for 30 frames, with
zero maximum byte error. Averaging a mip chain would change red, making this
more informative than sampling a uniform texture. Source/runtime/capture hashes
and render settings are preserved in the native-proof fixture.

All 14 historical source witnesses (13 bias, one LOD) lower completely in the
targeted recheck. This does not prove their entire visual behaviour. General
mipmapped filtering, projected coordinates and derivative/gradient sampling
remain separate work.

Reference: [OpenGL 3.3 core texture filtering rules](https://registry.khronos.org/OpenGL/specs/gl/glspec33.core.pdf).
