# Production GL controls — uncompiled proposal

`shader_input_controls.cpp` and the isolated CMakeLists.txt are prepared for the parent to compile/run. No configure, compile, GL/device or Git operation was performed in this preparation. Source labels remain proposals until actual parent output confirms them.

The current production entry point is **MilkdropShader::LoadVariables**; this tree has no Shader::SetPerFrameVariables method. Renderer::Shader supplies the actual setters. Tests call production HLSL LoadCode/LoadTexturesAndCompile, LoadVariables, query the bound GL program's _c3/_c4/_c12 values and draw that actual translated composite. No replacement uniform setter or cloned color shader is used.

Reuse `core/src/test/native/projectm-regressions/CMakeLists.txt` and gl_context.hpp. The requested tools/projectm-regressions path does not exist here. The isolated wrapper adds that source directory EXCLUDE_FROM_ALL and adds only shader-input-controls as the requested build target; canonical CMake/helpers are untouched. Use a pre-patched, identity-bound PROJECTM_SOURCE. Parent can configure this directory, build target shader-input-controls, then run it with fixture/proof directories or select only its named CTest. Do not build/test every included existing target incidentally.

## Executed paths proposed

- Real production PCM receives576 mono uint8 silence samples128, updates once at1/30 seconds/frame0, and exports FrameAudioData. Existing relative-band fallback produces1 rather than injected0; actual vol/volAtt should be.999. This audio object is bound through the production shader and drawn. The original comma scalar is computed independently as.3333×treble, not substituted into production audio.
- Coherent finite injected triples cover unequal/equal/bass-only/mid-only/treble-only/zero cases. These are explicitly injected binding controls, not PCM execution. Test output identifies them separately. Raw current volume fields and original comma scalar are logged alongside live GL uniform values.
- Real EEL writes vol/vol_att and bass/mid/treb, records q1/q2 and a q6 execution counter. Two same-frame shader rebindings must leave immutable audio values intact and q6 exactly1. This distinguishes shader binding replay from equation execution. It is a focused LoadVariables test, not proof of complete prepared geometry replay.
- One compiled live mip program is rebound across square, landscape, portrait, Native/reference3840×2160→1280×720 and Native/no-reference3840×2160 profiles. Required _c12 components must track declared canvas dimensions; nonsquare height must not silently become width. Same-frame rebinds must preserve the tuple.
- Every finite explicit-oracle sibling is read through the production PresetFileParser, transpiled/compiled through MilkdropShader and actually drawn. Live versus scalar-oracle color expectations use declared finite fields; explicit oracles are not original Windows output. Fixtures are parsed for their actual composite code and EEL block; this direct shader harness does not execute the full preset's warp/geometry lifecycle.

## Compiled-path proof

Renderer::Shader detaches/deletes shader objects after linking, so post-link glGetAttachedShaders cannot reliably recover source. The proposed GLAD observer records each actual glShaderSource submission and captures actual attached shader compile status at glLinkProgram before forwarding the real link once. It then requires the bound program's successful link and both recorded vertex/fragment stages, retaining submitted GLSL under the supplied proof directory. A fallback/error is a failure. On a binary-cache path without source/link observation, this control fails explicitly; cached program validation needs a separately source-bound cache identity. CGL does not use the GLES-only program-binary cache.

Required live uniform locations must be active: _c3/_c4 for volume controls and _c12 for mip controls. Explicit constant-oracle shaders can legitimately optimize those uniforms away, so they require compilation/output proof but not inactive uniform lookup. Capture is immediately after the actual production binding and before the draw; retain program and source identity in parent evidence.

## Reporting and image limits

The GL output target is intentionally16×16 RGBA8 and every pixel is checked against finite uniform-driven color with one-byte conversion tolerance. The test binds READ_FRAMEBUFFER and COLOR_ATTACHMENT0 explicitly. Native/reference3840×2160 cases are **render-context/uniform-reporting profiles**, not actual full4K presentation or authored/native target allocations. Parent still owns Native4K screenshots, actual target dimensions/status, ABI/source/artifact identities, PCM/clock/seed transport and final output binding.

The harness sets feedbackDetailAlpha0 to exercise same-frame shader-uniform reuse admission, without constructing a detail layer. This does not prove authored feedback's allocation/replay lifecycle or qualify visibility/pressure cleanup. Random-frame inputs are unused by the scalar diagnostics; production LoadVariables can still update them. Do not generalize scalar uniform stability to random matrices/geometry or compare render-program object IDs across separate engines.

No shipping performance claim follows from test-only GL source observers/readbacks; they deliberately add instrumentation work. Current stereo/mono transport, all-band volume and reference-reporting policies remain unchanged. Native validation remains open until the parent executes and records the relevant gates.
