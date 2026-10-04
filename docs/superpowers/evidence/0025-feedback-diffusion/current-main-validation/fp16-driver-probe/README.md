# Mixed RGBA8/RGBA16F driver probe

This separate framework Instrumentation application tests driver capabilities and explicit numeric
readback. It does not use ProjectM or Core and supplies no fidelity or performance evidence.

Build from this directory:

```sh
./gradlew :app:assembleRelease --no-daemon --console=plain
```

The APK is `app/build/outputs/apk/release/app-release.apk`. Its package is
`nl.neerdael.projectmtv.fp16driverprobe`, separate from every Core worker.

`run_probe_once.py` records one invocation on the explicitly leased emulator-5582. It first obtains
the nonblocking owner `measurement.lock` and checks launch SHA, PID 15197, AVD containment, current
process command, port and `ro.kernel.qemu`. It releases the lock in `finally`. The recorded
invocation completed; the script refuses to overwrite `run-manifest.json` or silently rerun.

## Probe

Create a fresh GLES3 EGL pbuffer context. Attach RGBA8 at location 0 and RGBA16F at location 1 of a
2x1 framebuffer. Set both draw buffers and require `GL_FRAMEBUFFER_COMPLETE`. Draw a fullscreen
triangle with blending and dithering disabled:

- Raw output: exact bytes `(17,85,129,255)` in both pixels.
- Half output: red `1/2048` and `3/2048`; green `0.5`, blue `0.99951171875`, alpha `1`.
- Read raw through `RGBA/UNSIGNED_BYTE` and half through `RGBA/FLOAT`.
- Sample the previously rendered half texture at its midpoint with `GL_LINEAR` into a distinct
  RGBA16F target. Require red `1/1024`, distinguishing interpolation from nearest sampling.

Record GL vendor, renderer, version, complete extension strings, framebuffer statuses, actual and
expected numbers, shader logs, and every GL error check. Delete textures, framebuffers, vertex
array, shaders and programs, then destroy the EGL surface/context.

## Recorded result

One invocation passed on Google (Apple), Android Emulator OpenGL ES Translator (Apple M4 Pro),
OpenGL ES 3.0 (4.1 Metal - 89.4). Both framebuffer checks were complete. Raw bytes, half values,
and the filtered midpoint matched exactly. All 18 GL error checks were zero; cleanup completed.

`probe-result.json` holds the explicit numbers and extension strings. `run-manifest.json` identifies
the owned emulator and invocation. `artifact-proof.json` hashes the source, APK, logs and result.
The measurement lease has been released for the separate actual-Core precision comparison.
