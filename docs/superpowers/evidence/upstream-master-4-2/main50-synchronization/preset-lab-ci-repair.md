# Private desktop discard fallback

Required reviewed-build run [37598901848](https://github.com/johnneerdael/ProjectM-TV/actions/runs/37598901848), for reviewed head `b805d661`, passed Android release/JVM, Linux EGL/GLES native sanitizer controls and strict documentation. Its Preset Lab job failed to compile `CopyTexture.cpp` and `BlurTexture.cpp`: the pinned desktop GLAD3.3 declarations do not provide `glInvalidateFramebuffer`.

The private analysis hook already omits this optional hint on Apple OpenGL4.1. It now also preserves attachment contents when desktop declarations lack GL4.3. It includes desktop GLAD before deciding that fallback, while guarding Android and configured GLES builds. Android retains its real GLES3 discard function. Production engine patches, renderer sources and AAR bytes are unchanged; the frozen emulator workers keep their own recorded hook/source copies.

Compiled regression: the desktop GL3.3 case fails before the repair with an undeclared discard function; GL4.3 passes and keeps the real call. Afterward both pass. The existing Android NDK compile test additionally rejects a discard macro shim and invokes the GLES3 function. All nine worker-build controls pass.

The complete Preset Lab suite passes **167 tests**, using the newly built real host worker. Doctor reports healthy: waveform, noise and random-texture shader cases repeat exactly and preserve the pre-intervention prefix on Apple M4 Pro/OpenGL4.1. This is host analysis coverage; desktop timings do not establish TV performance. The new full Linux CI run remains required.

Frozen-input audit after the root hook edit passes for the ongoing v2.3.16 comparison: release, workers, APK/AAR payloads, helper sources, assets, PCM and profile identities remain unchanged. Original failed CI compiler logs remain under ignored `build/upstream-rebase/main50-ci-backend/`.

## Separate host-control build

The next reviewed run [37600865252](https://github.com/johnneerdael/ProjectM-TV/actions/runs/37600865252), at `41ae1394`, passed the repaired Preset Lab backend doctor and source-adapter compilation. It then exposed the same absent discard declaration in `tools/projectm-host-gl-shim.h`, used by `tools/projectm-host-tests.sh` during production feedback/lifecycle validation. Android/JVM, Linux native sanitizer and documentation jobs passed again.

The host-control shim now uses the same optional desktop fallback and Android/GLES guards. Compiled tests independently exercise both headers: the old host GL3.3 branch fails with the missing declaration; all four desktop 3.3/4.3 cases and both real NDK GLES-header controls pass afterward. The third shim, `macos_gl.hpp`, is included only in Apple native-test builds and needs no Linux change.

All **170 Preset Lab tests** pass with the real host worker, and all **329 host engine controls** pass. See [full suite output](preset-lab-host-shims-tests.txt). Production Android sources and the ongoing fidelity protocol/workers remain unchanged. A reviewed CI run of the updated head is still required.
