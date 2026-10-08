# I25 / I30 — retain floating color precision

**Disposition: retain current float attributes for geometry and display. No engine patch or global byte conversion.** Actual production attributes/replay, a valid completed-grid source-byte replay and48 repeated Native4K capture jobs qualify this owner decision. Dynamic stock values near byte thresholds and Android composite-grid byte replay remain explicit future compatibility gates.

Original MilkDrop2 truncates equation RGBA×255 before geometry interpolation, and packs already-produced float display coefficients before interpolation/blending. Current projectM deliberately preserves fractions. Restoring byte packing globally would discard sub-byte alpha and systematically lower ordinary fractional coefficients; raw borders/composite signals also have distinct finite domains. See [source design and arithmetic](README.md).

## Executed proof

[Production CGL results](production-cgl-controls.txt) and [observer source](producer_attributes.cpp) instantiate actual CustomShape/CustomWaveform, VideoEcho and FinalComposite. Thirteen geometry roles qualify emitted RGBA, fill/edge/border/Native endpoints, pass counts and once-only equation replay. Four display cases qualify actual gamma.75/.9/1 and echo.5 vertex gains/pass counts. The composite control captures the completed real color/noncolor buffers and indices, draws current output, quantizes only completed colors before GPU interpolation, replays the same program/topology, then restores exact bytes. It does not floor fragments or quantize corners prematurely.

| Completed-grid source comparison, CGL64×64 | Image |
|---|---|
| Current float producer | [Current](production-proof/composite-float-current.png) |
| Original byte packing on the same completed grid | [Byte replay](production-proof/composite-vertex-byte-oracle.png) |

[Replay metrics](composite-replay-results.json): RGBMAE.501058 and6157different channels. This is source CGL evidence, not Android Native4K grid replay or Windows rasterization. PNGs are lossless transcodes of captured PPMs; decoded pixels are verified unchanged.

## Native4K evidence

[Results](native-results.json) and [identity](native-identity.json) bind frozenac3/current27, actual instrumented AAR/private APK, API34ARM64/GLES3/hostGPU, output3840×2160/Standard1280×720, commonPCM/seed12345/mesh48×32/30FPS. All24 repeat groups and384 selected PNG/RGB checks pass. Every480frame run passes GL/name/cleanup/finalREAD framebuffer0 checks. Native bytes and all stock assets remain unchanged;22labelled fixtures are appended.

Six geometry pairs compare current fractions against explicit original-byte input coefficients on identical Native geometry/styles. All six have small visible differences. The sub-byte alpha fixture retains a nonzero producer versus original byte0; no universal visibility or affected-stock count follows.

| Native4K sub-byte alpha | Image |
|---|---|
| Current float alpha.003 | [Current](native-captures/colourpolicy-audit-colour-i25-shape-subbyte-alpha-float-current-current-0/frame-239.png) |
| Original byte0 coefficient | [Byte input](native-captures/colourpolicy-audit-colour-i25-shape-subbyte-alpha-byte-source-oracle-current-0/frame-239.png) |

Gamma.75/.9 versus191/255 and229/255 is pixel-identical on this RGBA8 backend despite different uploaded coefficients. Echo-half with uniform white input gives meanRGB255; the labelled254/255final-gain surrogate gives254. That surrogate uses a different pass path and is not an echo per-pass/interpolation/feedback or cost oracle. Actual VideoEcho .5/.5 attributes are separately captured by the producer test.

| Native4K echo-half, uniform white | Image |
|---|---|
| Current float contributions | [255](native-captures/colourpolicy-audit-colour-i30-echo-half-float-current-current-0/frame-239.png) |
| Uniform-white original-byte final-gain surrogate | [254](native-captures/colourpolicy-audit-colour-i30-echo-half-uniform-gain-oracle-current-0/frame-239.png) |

The actual hue_shader Native probe and unchanged39/va ultramix originals repeat, but do not substitute for an Android completed-grid byte replay or establish dynamic stock source-double coefficients.

## Owner followup and limits

Retain fractional/sub-byte/HDR attribute policy and all window, interpolation, dot-density, style, gamma-boundary, tint and replay fixes. No shipping rendering work is added and no performance improvement is claimed. If byte-exact compatibility becomes a separate product requirement, capture dynamic source doubles and exact completed grid values on the target backend, then isolate conversion after each original producer stage and qualify Native4K feedback/performance before adding a versioned option. Do not lower FBO precision globally.

Physical-TV timing, whole-corpus prevalence, Windows output and hidden shipping arrays remain unmeasured. [Audio provenance correction](../AUDIO-PROVENANCE.md) applies to frozen manifest prose; actual queried576-tail input is preserved.
