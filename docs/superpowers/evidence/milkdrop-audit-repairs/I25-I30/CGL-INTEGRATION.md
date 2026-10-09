# Actual production CGL controls — prepared, not built or run

`producer_attributes.cpp` supplements the earlier Color-only source controls. It instantiates the real CustomShape, CustomWaveform, VideoEcho and FinalComposite classes, reads their actual uploaded attributes at draw submission, and executes a completed-vertex byte replay for shader composition. No production/private-class changes or test doubles are used.

No compilation, CGL context, GPU, device or executable check was performed during preparation. Static API/signature inspection is not a successful build. Root execution is still required before calling these controls passing or including them as acceptance evidence.

## Integration

Reuse the existing `core/src/test/native/projectm-regressions` CGL harness and its current patched `PROJECTM_SOURCE`. Its macOS force-include shim, GLAD declarations, static-engine options, C++17 and OpenGL linkage are needed. Add a temporary target only in a root-owned isolated harness; this packet changes no CMake file:

```cmake
add_executable(owner-colour-attributes
    "${REPO}/build/audit/colour-precision-policy/producer_attributes.cpp")
target_compile_features(owner-colour-attributes PRIVATE cxx_std_17)
target_compile_definitions(owner-colour-attributes PRIVATE GL_SILENCE_DEPRECATION)
target_include_directories(owner-colour-attributes PRIVATE
    "${REPO}/core/src/test/native/projectm-regressions"
    "${PROJECTM_SOURCE}/src/libprojectM"
    "${PROJECTM_SOURCE}/src/libprojectM/MilkdropPreset"
    "${PROJECTM_SOURCE}/vendor"
    "${PROJECTM_SOURCE}/vendor/projectm-eval/projectm-eval/api")
target_link_libraries(owner-colour-attributes PRIVATE
    libprojectM::projectM "${REGRESSION_OPENGL_FRAMEWORK}")
```

Set REPO to the actual worktree and compile against the qualified source identity, not an old cached source tree. The existing harness declares the macOS framework and shared force-includes; an independent target must reproduce those declarations. This source intentionally uses desktop read-buffer mapping, not an assumed GLES-compatible observer.

Future invocation, after root builds the target:

```text
owner-colour-attributes PACKET_DIR OUTPUT_DIR geometry
owner-colour-attributes PACKET_DIR OUTPUT_DIR display
owner-colour-attributes PACKET_DIR OUTPUT_DIR composite
```

The optional `all` mode runs the three groups. Use absolute packet/output paths to keep every produced artifact in the owned evidence directory. Compile/run outside isolated Native timing intervals.

## Actual geometry observations

The geometry group parses each actual owner fixture with PresetFileParser, initializes PresetState, then constructs and compiles real CustomShape/CustomWaveform objects. It uses production GeometryTargets with authored64 and Native128 targets, a64-square line reference and fixed unit aspect. It requires the actual production Native line shader to be usable; a silent fallback is not accepted as successful Native quad coverage.

Draw hooks observe glDrawArrays, glDrawElements and glDrawArraysInstanced. They query the bound VAO's actual RGBA layout and map its actual VBO. Shapes/custom-wave meshes use colour attribute1. Native LineRenderer uses instanced endpoint colour attributes4/5 (positions occupy0–3), so those endpoint colours are captured separately. Element draws use the real index buffer; array offsets and attribute strides are respected. No stored geometry is recomputed to substitute for an emitted producer.

Controls cover both current/byte-source-oracle siblings for all six I25 cases and the raw border HDR probe. Every submitted fill/edge/border/wave RGBA is compared with the explicit material coefficients; source-oracle coefficients use the independent bounded `int(channel*255)&255` formula. Native dot alpha scaling is applied after source quantization, preserving current style policy. Thin/pass counts are checked. Test-only EEL register counters establish shape init/frame once, and wave init/frame once plus two point executions, despite both target replays.

Outputs include per-draw target/primitive/instancing/RGBA CSVs and actual authored/native top-down lossless RGB PPMs. Pixel equality is admitted; attribute qualification is independent of final RGBA8 storage. PPMs may be converted losslessly for display without relabeling them as original Windows captures.

## Actual legacy display observations

The display group instantiates VideoEcho directly with actual white texture input, fShader0, zoom1/orientation0 and fixed source context. Cases cover gamma.75, gamma.9, gamma1 and echo alpha.5. It records all four uploaded RGBA vertices for every actual pass and checks expected pass counts and floating gains. An independent display formula multiplies the emitted float coefficient by255, truncates and masks to produce byte/normalized expectations in a separate CSV.

This does not replace VideoEcho with scalar code or simulate echo using an unrelated shader. It captures the actual .5/.5 echo base contributions. The earlier uniform-gain image surrogate remains specifically limited and is not used as the producer assertion here.

## Valid completed-grid byte replay

The composite group uses the actual FinalComposite path with `ret=hue_shader`, actual TextureManager/ShaderCache and fixed time/hue offsets. It rejects shader fallback by requiring a linked program with live vertex_color at location1.

Immediately before the real indexed draw, after production ApplyHueShaderColors has completed:

1. Read the actual completed colour VBO, position/UV/radius-angle attributes and real indices.
2. Export each completed float RGBA and its independent byte result, plus unchanged topology.
3. Perform the real production draw into the current target.
4. Replace only each completed vertex's colour with its normalized byte coefficient, bind a separate equal-size output target and call the same real indexed draw using the same program/uniforms/VAO/indices.
5. Restore the exact production colour bytes and previous draw/array bindings; assert all non-colour buffers and indices remain unchanged.

This quantizes after float corner interpolation has produced each vertex but before GPU interpolation. It does not quantize corner shades first or floor hue_shader in a fragment shader. Output files are `composite-float-current.ppm`, `composite-vertex-byte-oracle.ppm`, completed-vertex CSV and index CSV.

Composite overscan may produce finite channels slightly outside[0,1]. The replay therefore admits a finite float-times255 product only when its truncating conversion is within int32, then applies the original low-byte mask. It does not clamp, invent0/abs, or execute undefined conversion. The ordinary geometry fixture oracle remains within[0,1]. A nonfinite/out-of-range completed producer fails explicitly.

The replay isolates original byte packing on the current qualified grid. It is not a recreation of a different original grid, original hue arithmetic, Windows rasterization, transitions or fullscreen presentation. Final stored pixels may coincide; producer differences and topology evidence are retained regardless.

## Actual API gaps and remaining gates

- Shape/wave evaluated double colour contexts and producer meshes are private; there is no public production accessor. Constant owner fixtures are away from cast thresholds, so their known input coefficients support bounded comparisons. Dynamic stock colour values near a byte boundary need separately identified source instrumentation to capture the double value before the current float cast/modulo; uploaded float RGBA alone cannot reconstruct that lost input.
- There is no public FinalComposite colour/index accessor. The observational GL draw hook captures completed buffers without changing class layout or shipping APIs. Replay writes are confined to runtime test-owned GPU buffers and restore production data before returning.
- The source has been signature-reviewed but is uncompiled/unexecuted. Driver/link/read-map assertions may reveal a real harness gap; report it rather than claiming a pass or silently falling back.
- The standalone geometry targets64/128 exercise real authored/Native style replay, not a physical Native4K or Android JNI run. Root still needs matched final-output Native captures, source/artifact identity, actual sizes/style/gain, and backend-specific qualification.
- These controls add buffer mapping, CSV/PPM output and an extra oracle draw; never use them as timing or workload evidence.

No I25/I30 completion, affected stock census or original-renderer equivalence claim follows until the root actually executes and validates the relevant acceptance gates.
