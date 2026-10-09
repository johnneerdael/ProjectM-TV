# Source-only Android I16 lifecycle preparation

This private worker is a copy of `tools/core-corpus/android-worker`, with a separate `projectmtv-core-lifecycle-v1` protocol. No canonical worker, normal verifier, product API or renderer source is changed. Preparation has not been compiled or run. The root agent owns building, device execution, review and qualification.

## Production path exercised

`ProjectMJNI.init` runs once. Each public surface/frame/release method runs on the instrumentation thread with its owning actual GLES3 RGBA8 pbuffer context. After 240 completed frames, `EglSurface.close()` unbinds and destroys the actual old context/surface, terminates its display and releases the thread. The production core is not released or initialized again. Its published preset/counter are checked while no context exists. A new unshared context is created, then production `onSurfaceCreated()` and `onSurfaceChanged()` run. `native-lib.cpp:2062` invokes `DestroyEngineLocked(false)` before creating a new engine, abandons old GL names, and resumes the published preset on the next frame. Reload must increment the public counter from 1 to 2. A successful run has exactly 480 completed-frame serials, including both generations.

The fixed global frame clock stays `frame/30`, and each PCM block remains `frame*1470` in the same 705600-byte signal. Neither seed nor clock is reset after recreation. Engine/preset state resets at recreation. `generationFrameOrdinal` is the worker's zero-based completed-draw ordinal within each context generation, not a claim about the preset equation's internal `frame` value or shader random stream. Compare RGB only between matching fixture, source, artifact, schedule, global PCM/frame, dimensions and generation. Never compare recreated generation2 pixels to an uninterrupted normal run and label that pixel agreement or drift.

All 480 draws call `glFinish` before strict GL checking and before any next-frame event. It proves submitted GPU work completed; this protocol is not a normal rendering-cost measurement. Every capture explicitly binds read framebuffer0 and restores the previous read binding. GL initialization, event requests/recreation, every draw, capture and final production release retain strict checks. No failure is converted to a warning. The normal corpus verifier retains its one-load invariant unchanged.

## Fixed schedule

| Before frame | Action |
| --- | --- |
| 120 | Production memory-pressure request after completed frame119; next draw applies the flush request. |
| 180 | Replace pbuffer with reduced dimensions, preserve EGL context, call production size callback. |
| 210 | Restore original pbuffer dimensions with the same context. |
| 240 | Destroy/recreate actual EGL context while core alive, then production surface callbacks; expect second preset load and state reset. |
| 300 / 330 | Request mesh24×16 / restore48×32 through existing `setMeshSize`. |
| 360 / 390 | Request High / restore Standard through existing `setNativeTrails`. |
| 420 | Unbind retained context/surface for at least50ms with no draw/audio/clock advancement; rebind and call size callback. |

The startup prewarm pause runs at fixed clock0; the explicit pressure event runs at clock4. Both remain effective through the final fixed clock below16s, so no wall-dependent refreshes are scheduled. The default/custom feedback fixtures initialize the prior UV field before pressure and recreation. Their authored enable/disable cadence resumes from fresh state after recreation. `onMemoryPressure` sets the pool-flush flag and pauses prewarming; its call plus safe subsequent draws is proof of the production pressure path, not proof that memory exhaustion or a nonempty pool occurred. Native logcat is retained for the actual pause/flush lines where applicable.

The requested mesh dimensions are traced through production settings application; no public mesh getter or hidden UV accessor is added. Trails status is recorded every frame. At the default720p, native trails remain inactive and this is only a trails-setting/resume check. To qualify active canvas/detail changes, run a separate fixed profile above1330p (for example2560×1440 reduced1920×1080), freeze its dimensions, and require actual status reporting `canvas`, not an inactive/fallback status. Do not relabel a720p run as active native detail qualification.

## Root build and binding recipes (not executed here)

1. Add every `.milk` in `build/authored-followup/fixtures` to this private worker's `app/src/main/assets/presets/` and regenerate its `presets.idx` from the sealed AAR index plus exact new fixture rows. Preserve every original AAR asset byte. Use only this private source for the lifecycle APK. Retain the Gradle build log and exact source hashes.
2. Build with the repository wrapper, an explicit SDK configuration, and the existing sealed instrumented33-patch AAR:

```sh
./gradlew -p build/authored-followup/android-lifecycle-prep/android-worker :app:assembleDebug --console=plain -PcoreAar=/absolute/path/build/authored-followup/workers/candidate-native/candidate-native.aar -PcorpusApplicationId=nl.neerdael.projectmtv.corpuslifecycle
```

3. Reuse the frozen PCM from the normal authored follow-up jobs. Do not regenerate a subtly different signal. Prepare a driver JSON from an actual owned5640/user0 API34 normal manifest with the exact `fingerprint`, `sdk`, `glVendor`, `glRenderer`, `glVersion`, `glShadingLanguageVersion`, and explicit `ownedSerial="emulator-5640"`, `androidUser=0`.
4. Bind explicit final artifact/input paths. The binder checks the original JNI and asset bytes against the sealed AAR, fixture contents and index additions against the fixture directory, exact source/helper hashes, observed driver identity and PCM size/hash. It refuses an existing binding. Replace absolute example paths with the actual owned artifacts:

```sh
python3 build/authored-followup/android-lifecycle-prep/bind_lifecycle.py --core-identity /absolute/path/workers/candidate-native/identity.json --aar /absolute/path/workers/candidate-native/candidate-native.aar --apk /absolute/path/android-worker/app/build/outputs/apk/debug/app-debug.apk --fixtures /absolute/path/build/authored-followup/fixtures --pcm /absolute/path/frozen/audio.u8 --driver-identity /absolute/path/driver.json --output /absolute/path/lifecycle-binding.json
```

5. Install that exact APK for numeric user0 on the owned emulator5640. The controller does not install or mutate unrelated packages; it checks installed base-APK SHA256 before running. Launch each fixture in a fresh instrumentation process and fresh host output directory. The controller holds the same core-corpus session lock, restores the prior forced-preset property, stops only the lifecycle package for user0 and removes only its unique staging directory. Success removes the unique pulled/verified private job; failure retains it for diagnosis.

```sh
python3 build/authored-followup/android-lifecycle-prep/run_lifecycle.py --binding /absolute/path/lifecycle-binding.json --preset 'audit followup uv default-feedback.milk' --output /absolute/path/lifecycle-default-720-r0
```

Repeat for `audit followup uv custom-feedback.milk`, then independently repeat each same frozen profile if comparing same-protocol images. To run the higher detail profile, append `--width 2560 --height 1440 --reduced-width 1920 --reduced-height 1080` and use a separate profile/output. No driver/fixture/source/helper changes are permitted during a frozen run.

6. Reverify archived outputs with the separately named verifier:

```sh
python3 build/authored-followup/android-lifecycle-prep/verify_lifecycle.py /absolute/path/lifecycle-default-720-r0 --binding /absolute/path/lifecycle-binding.json
```

## Remaining gates

Compile/source review of private worker and helper scripts; frozen exact APK/PCM/driver binding; actual owned5640/user0 runs of both feedback fixtures; strict manifests and native logs; boundary-image review and optional identical-protocol repeats; active native-detail status verification for the higher profile; final root qualification record. This pbuffer JNI protocol cannot certify Activity Home/return, real audio reattachment, true memory pressure/exhaustion, physical-TV performance or whole-corpus fidelity. No such results are claimed by preparation.
