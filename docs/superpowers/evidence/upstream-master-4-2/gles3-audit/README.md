# GLES 3.0 source audit

Read-only assessment, 2026-10-06. Local ProjectM-TV revision: `4b15c4e6`; upstream pin: `6f64807467e312034883a4389e6aa80a675458bc` with the three migration patches. GitHub main was `347fca385b2e689bda1e758ab2f55856c3a191ef` with 47 historical patches; pending PR #49 head was `25a3ff425592698b3f7835487345af2f1803cc81`. Main patches 0045–0047 and PR #49 were inspected separately, not assumed integrated. Recheck the final merged/ported source.

**Source conclusion:** no unguarded GLES 3.1/3.2 command or shader-language requirement was found. **Runtime conclusion:** the unchanged current 4.2 AAR completes a strict 480-frame smoke on the API 34 host-GPU emulator reporting GLES 3.0. API 36 host-GPU initialization fails in its program-binary encoder; generic 3.0 device compatibility still has a float-framebuffer caveat.

## API and shader floor

The call audit covers 97 distinct GL names in engine/API/JNI C++ and headers. The [official Khronos XML registry](https://github.com/KhronosGroup/OpenGL-Registry/blob/main/xml/gl.xml) places 96 at GLES 2.0/3.0. `glColorMaski` is GLES 3.2, but `Framebuffer::MaskDrawBuffer` uses it only in the desktop `#else`; GLES calls `glColorMask`. Added calls in main 0045–0047 and pending #49 stay within 3.0. The machine audit records names, locations, guards and source hashes.

| Path | Inspected policy |
|---|---|
| Android configuration | GLES enabled; JNI links GLESv3; app advertises ES 3.0 |
| GLAD loader | Minimum GLES 3.0 and GLSL ES 3.00; desktop minimum GL 3.3/GLSL 3.30 |
| Native preset shaders | `#version 300 es`, HLSL target `Version_300_ES` |
| Copy/blur/lines/feedback/transitions/sprites/JNI fades | GLES variants use 300 es |
| Desktop guards | Indexed color masking, program point-size and line smoothing remain desktop paths |

Instancing, VAOs, MRT/draw buffers, sampler objects, map-buffer ranges, framebuffer blits/discards and program binaries are 3.0 APIs. Generated GLAD declarations for 3.1/3.2 do not themselves require those runtime versions. The standalone loader fixture checks the version gate with fake query functions; it is not a real GLES rendering test.

## Capability caveat: motion-vector UV framebuffer

`MilkdropPreset.cpp` creates `GL_RG16F` UV storage and attaches it when motion vectors are visible. The [ES 3.0 specification](https://registry.khronos.org/OpenGL/specs/es/3.0/es_spec_3.0.pdf), table 3.13, printed page 131, makes RG16F filterable but not mandatory color-renderable. Allocation/sampling legality does not establish framebuffer completeness.

[EXT_color_buffer_float](https://registry.khronos.org/OpenGL/extensions/EXT/EXT_color_buffer_float.txt) adds RG16F color renderability on GLES 3.0. [EXT_color_buffer_half_float](https://registry.khronos.org/OpenGL/extensions/EXT/EXT_color_buffer_half_float.txt) describes half-float rendering support and completeness checks. The inspected UV path has no explicit capability/fallback check. This is a device-capability gap rather than evidence that every engine path needs a 3.1/3.2 API. FeedbackDetail uses ordinary color attachments and checks its FBOs; it does not add a separate RGBA16F requirement.

Record float-color extensions and actual small RG16F MRT completeness, then exercise a motion-vector preset. Oscilloscope with motion vectors off does not cover the UV target.

## Observed emulator failure: program binaries

The root-owned API 36 ARM64 TV emulator reports GLES 3.0/GLSL ES 3.00 on Google(Apple)/M4 Pro host graphics. Emulator version is 37.1.11. The unchanged current 4.2 AAR preflight fails before frame 0 with GL_INVALID_OPERATION; PID 3470 identifies `GL2Encoder.cpp:s_glGetProgramBinary:5044`, rejecting a buffer smaller than serialized program metadata. No captures were produced.

The engine queries binary length and allocates that size before retrieval. [Khronos’ GetProgramBinary reference](https://registry.khronos.org/OpenGL-Refpages/es3.0/html/glGetProgramBinary.xhtml) defines the API in ES 3.0 and requires sufficient buffer size. The optional cache returns when no bytes are written but leaves the observed GL error pending. Its source is inherited from historical patch 0002; baseline failure must be measured, not assumed.

[Current AOSP gfxstream encoder](https://android.googlesource.com/platform/hardware/google/gfxstream/+/refs/heads/main/guest/GLESv2_enc/GL2Encoder.cpp) matches the logged line: length and retrieval separately serialize guest/host program metadata. The [Android 14 goldfish encoder](https://android.googlesource.com/device/generic/goldfish-opengl/+/refs/heads/android14-release/system/GLESv2_enc/GL2Encoder.cpp) forwards host length and raw binaries without that wrapper. These are source comparisons, not proven installed-image commits. They justified testing a fresh API 34 image with the same host GPU and unchanged artifacts. That test subsequently passed as recorded below.

The API 34 run reports zero binary formats and float-color extensions. A binary-export round trip therefore remains untested on this backend; motion-vector coverage should still verify the actual UV target. Keep strict GL checking. A portable optional-cache failure path may merit a later fix, but no AAR/shader/cache changes were made by this audit.

The local emulator help and [Android’s supported GPU modes](https://developer.android.com/studio/run/emulator-acceleration) list `host`/`auto` as hardware paths. `angle` and `angle_indirect` are deprecated; SwiftShader/swangle/lavapipe are software paths and cannot silently substitute for GPU validation.

## Bounded GLES 3.0 runtime result

The root-owned fresh API 34 AVD `Upstream42FidelityAPI34`/emulator 5624 uses the same host GPU and reports GLES 3.0/GLSL ES 3.00, M4 Pro/Metal 4.1. With the unchanged current migration AAR SHA-256 `c57c823d18e5e33c0fcb4c779e41eece0a3d613cf95092351a86a4332c864075`, Oscilloscope at 1920×1080 completed 480 frames, 480 strict GL checks, 480 preset-name checks, eight captures and successful core/EGL cleanup. The manifest is `build/upstream-rebase/emulator/api34-preflight-oscilloscope/manifest.json`; its digest and capture hashes are in `audit.json`.

`GL_EXT_color_buffer_float` and `GL_EXT_color_buffer_half_float` are advertised. `GL_NUM_PROGRAM_BINARY_FORMATS` is zero; the optional cache does not exercise binary export on this backend. No engine/shader/AAR change or relaxed GL check was used. This is a real-clock, single-preset smoke on a GLES 3.0 driver, not deterministic cross-engine fidelity, binary-cache round-trip coverage, a direct motion-vector FBO test or final post-#49 integration validation.

## Evidence boundaries

`audit.json` contains complete call/source/overlay hashes and the failed preflight manifest/log hashes. Downloaded authoritative specs/XML and AOSP source are retained under ignored `build/upstream-rebase/gles3-audit/`. The ES table was rendered and visually checked. No device command, restart, production change, AAR mutation or Git mutation was performed.

This establishes a source-level 3.0 floor and the bounded API 34 runtime result, with identified capability/runtime limits. It does not certify final post-#49 integration, all GLES 3.0 drivers, preset fidelity or performance.
