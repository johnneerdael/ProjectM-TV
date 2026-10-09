# I26 / I27 — retain corrected shader inputs

**Disposition: retain all-band shader volume and height-aware mip reporting. No engine patch.** Actual compiled-program/uniform/source controls and34 repeated Native4K jobs qualify these bounded policy decisions. They preserve upstream improvements and TV reference reporting.

I26 original comma expressions evaluate only treble×.3333, including attenuated volume. Current immutable audio fields use (bass+mid+treble)×.333. Equal bands also differ; mono channel equality does not remove this frequency-band defect. I27 original mip_y repeats width; current derives height and then computes the mean. Native output3840×2160 is distinct from the Standard1280×720 shader reference canvas.

## Compiled source and binding proof

[Actual CGL results](production-cgl-controls.txt), [test source](shader_input_controls.cpp) and compiled-proof/ capture production HLSL translation, real submitted GLSL/compile/link status, live _c3/_c4/_c12 readback and16×16 scalar output. Real mono PCM and coherent injected finite fields are distinct roles. Equal/unequal/bass-only/mid-only/treble-only/zero bindings, EEL writes versus immutable audio, square/landscape/portrait/reference reporting and repeated bindings pass. No substituted uniform setter or fragment-only imitation is used.

The matched ARM64 production archive input trace under [I21](../I21/arm64-input/target-trace.jsonl) records all eight finite audio fields from the same common576-tail/lab-clock source pipeline. It is a separate CPU source producer, not inspection of hidden JNI arrays.

## Native4K evidence

[Main results](native-results.json) and [identity](native-identity.json) bind frozenac3/current27, instrumentedAAR/privateAPK, API34ARM64/GLES3/hostGPU, Native3840×2160/Standard1280×720, seed12345/30FPS/mesh48×32/commonPCM. Thirty480frame runs pass per-frame GL/name/cleanup and finalREAD framebuffer0 checks;15 repeat groups and240 PNG/RGB checks pass.

Live volume output and the fixture overwriting EEL vol/bands are selected-RGB identical. Live mip output matches the explicit1280×720current tuple exactly. The original comma and duplicated-width explicit models differ visibly. These coefficient siblings are clearly labelled source oracles, not Windows captures or fresh PCM analysis.

| Native4K I27 reference reporting | Image |
|---|---|
| Current height-aware tuple | [Current](native-captures/shaderpolicy-audit-shader-I27-live-current-0/frame-239.png) |
| Original duplicated-width tuple at the same declared canvas | [Source tuple](native-captures/shaderpolicy-audit-shader-I27-1280x720-duplicate-oracle-current-0/frame-239.png) |

## Full-preset I26 source witness

Four additional [Cope runs](stock-volume/native-results.json) compare the unchanged Red Liquid Fire preset against a full sibling changing only one authored shader line from vol to (treb×.3333). All other preset bytes, renderer/audio/material/clock/settings remain common. [Replacement/hashes](stock-volume/oracle.json) identify the exact change. Both roles repeat selected RGB exactly; peak selected RGBMAE30.550332.

| Red Liquid Fire Native4K | Image |
|---|---|
| Retained all-band shader input | [Current original](stock-volume/native-captures/shaderstock-Cope---The-Neverending-Explosion-of-Red-Liquid-Fire-current-0/frame-239.png) |
| Original comma scalar on the current native pipeline | [Shader-scalar surrogate](stock-volume/native-captures/shaderstock-audit-shader-stock-cope-original-comma-volume-current-0/frame-239.png) |

This restores only the original scalar operator, using current band analysis. It is not the complete original Windows audio/shader/raster pipeline. The Royal23 original also repeats in the main packet; no full source-corrected Royal ratio claim is made. No stock mip witness exists in the inspected corpus; finite diagnostics carry I27's evidence.

## Limits and owner followup

Retain immutable all-band inputs, actual float coefficients and the existing Native reference-canvas policy. Returning to the comma or width-copy defects is rejected as a compatibility default. No shipping work or measured performance improvement is added. Physical-TV timing, Windows output, hidden shipping arrays and an affected-preset census remain unmeasured. Any future compatibility selector needs a separate consumer/API decision and explicit input-stage contracts; do not change mutable EEL variables or global volume modulation to mimic shader-only defects.
