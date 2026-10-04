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
- Android debug and release core/APK builds and JVM tests pass with JDK 21 and the installed SDK/NDK.
- Full native runner and both JNI rendering-policy controls pass. The macOS GLES transition overlay is skipped without EGL/GLES libraries; Linux CI passes it.
- Persistent ASan/UBSan CTest build: all 15 groups pass on macOS OpenGL.
- Patched upstream engine suite: 243/243 tests pass.
- Preset index/content checks, `git diff --check` and MkDocs strict build pass.

## AM6 actual-core validation

Authorized awake Ugoos AM6, Android 9, Mali-G52, OpenGL ES 3.2; Android supports `armeabi-v7a` on this device. Two new test-only worker packages used unchanged locally built baseline/fixed production core AARs, with their packaged ARMv7 library bytes verified against the AAR. Existing player audio and production app settings were untouched. Both jobs used the exact preset, 1280×720, the same 705600-byte generated 110/440 Hz unsigned mono signal, 30 FPS pacing and complete packaged presets/textures. Production random choices and real clock remain enabled. Worker-only changes select distinct package IDs, include ARMv7 and capture the first three frames. See [source/artifact identities and complete capture manifests](am6/summary.json) and [the capture-only source diff](am6/worker-capture.diff).

Both jobs completed 480 frames, 480 per-frame GL checks, preset identity checks and clean core/EGL release. All 11 PNGs per job were decoded and verified against the recorded RGB and PNG hashes. Captures retained here are [baseline frame 0](am6/baseline-frame-000.png), [fixed frame 0](am6/fixed-frame-000.png), [baseline frame 120](am6/baseline-frame-120.png) and [fixed frame 120](am6/fixed-frame-120.png). They show rendered output; independently chosen images and clocks prevent treating their pixel differences as a controlled fidelity measurement.

The complete paced render loop, including PNG encoding/readback, took 19.819 s baseline and 19.977 s fixed: effective rates 24.22 and 24.03 frames/s. These are worker-window rates with capture overhead, not on-screen app frame-rate measurements or evidence of a performance improvement.

The same direct blur ownership control was cross-compiled against each core's Android static engine libraries and run on the AM6 without sanitizers. [Baseline](am6/baseline-bindings.txt) fails on first allocation (`read=0/2 draw=0/3`); [fixed](am6/fixed-bindings.txt) passes all ten Blur1/Blur3 first/same/resize/scaled controls and constant-colour readbacks. [Executable hashes and exits](am6/bindings.json) identify those runs. Both full-preset jobs can return zero GL errors on Mali because framebuffer zero is a valid EGL pbuffer. The binding assertion exposes the underlying target loss that macOS reports as error 1286; absence of a GLES error alone would miss it.

After validation, both task-only worker apps and native-control files were removed and the originally empty preset override was restored. No TV wake command was sent, and the existing player was not stopped or reconfigured.

## Limits

The host controls use Apple M4 Pro OpenGL 4.1; the AM6 checks use locally built Android core AARs. Neither is an observation from a published AAR. The bundled JPEG decoder still produces the pre-existing SOIL2 left-shift UBSan warnings; isolated TGA regressions avoid that unrelated defect. Full authored-preset numerical accuracy, equivalence to MilkDrop and TV frame-rate effects are not established by these controls. Analyzer guards and the shared corpus baseline remain unchanged. Final GitHub review/check results are recorded in the PR. The AM6 check covers one preset and GPU, not the entire library or other TV models.
