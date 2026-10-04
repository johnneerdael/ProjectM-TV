# Midgit framebuffer diagnosis — 2026-10-05

The unchanged `midgitstraights of majillaen - featy sweet.milk` (SHA-256 `d4cd997dedc57ab34c7247fee1ba94d4061528d12d16cde5a468145fb216ebba`) reproduced PR #30's full-render error 1286 on main `6244a3ec`, projectM `e0b0a967` plus patches 0001–0040. The earlier [random-binding evidence](../random-texture-bindings/README.md) remains historical.

## Cause and correction

The preset's warp shader reads blur, so blur updates happen after the warp. `BlurTexture::AllocateTextures` calls `Framebuffer::SetSize` on first use or resize. That method unbinds both framebuffer targets. `BlurTexture::Update` saved the caller's read/draw bindings **after** allocation and therefore restored zero. Subsequent waveform and border draws failed with `GL_INVALID_FRAMEBUFFER_OPERATION` (1286). In this headless macOS context, framebuffer zero reports `GL_FRAMEBUFFER_UNDEFINED` (33305); the original render target reports `GL_FRAMEBUFFER_COMPLETE` (36053). See [the allocation trace](allocation-trace.txt). Instrumentation consumes errors to locate them, so its terminal error is not a pass/fail result; use the uninstrumented before/after reports.

Patch 0041 captures both caller bindings **before** allocation and retains the existing restoration after blur. No authored preset, shader, random policy, Java/JNI API, blur dimensions or filter weights change. [Khronos framebuffer-status documentation](https://wikis.khronos.org/opengl/GLAPI/glCheckFramebufferStatus) defines the status values used in this diagnosis.

## Regression evidence

- [Before](regressions-before.txt): both new real-GL controls fail on the original 40-patch engine. The blur control restores zero instead of its separate caller read/draw targets; the full preset fails on frame 0 with error 1286.
- [After](regressions-after.txt): both pass with 0041. Blur1 and Blur3 preserve distinct targets on first use, unchanged size, resize, scaled blur and repeated scaled blur. All exposed blur levels preserve a constant RGB source within two byte values. The exact preset renders four frames with a size change from 128×96 to 192×128 and successful output readback, using two isolated TGA images.
- The original bundled-image diagnostic also changes from [midgit error 1286](bundled-before.json) to [all three presets error-free](bundled-after.json). Shader-pair bindings and full-preset image selection are separate production-random observations; comparing their selected images does not establish matching appearance.
- [Source identity and structured summary](results.json) record the baseline, patch and preset hashes, GL profile and measured scope.

## Reproduction

Run `core/src/test/native/run_native_tests.sh` for the integrated ASan/UBSan controls. A persistent diagnostic build can be configured after applying the complete patch series:

```sh
cmake -S core/src/test/native/projectm-regressions -B build/framebuffer-regressions -DPROJECTM_SOURCE="$PWD/third_party/projectm" -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_FLAGS=-DMILKDROP_PRESET_DEBUG
cmake --build build/framebuffer-regressions -j 4
ctest --test-dir build/framebuffer-regressions --output-on-failure
```

The optional bundled-image diagnostic is `build/framebuffer-regressions/random-texture-regressions presets build/new-preset-fixtures`; the fixture directory must be new. It preserves its JSON even if full rendering fails. macOS requires OpenGL access; Linux uses headless EGL/GLES with `EGL_PLATFORM=surfaceless`.

## Additional local validation

- All 41 patches apply to a clean export of the pinned submodule.
- Android debug core/APK builds and debug JVM tests pass with JDK 21 and the installed SDK/NDK.
- Persistent ASan/UBSan CTest build: all 15 groups pass on macOS OpenGL.
- Patched upstream engine suite: 243/243 tests pass.
- Preset index/content checks, `git diff --check` and MkDocs strict build pass.

## Limits

These are host source-bound controls on Apple M4 Pro OpenGL 4.1, not observations from a published Android AAR. The bundled JPEG decoder still produces the pre-existing SOIL2 left-shift UBSan warnings; isolated TGA regressions avoid that unrelated defect. Full authored-preset numerical accuracy, equivalence to MilkDrop and TV frame-rate effects are not established by these controls. Analyzer guards and the shared corpus baseline remain unchanged. Dedicated TV validation and final GitHub review/check results are recorded in the PR when available.
