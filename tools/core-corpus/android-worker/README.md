# Actual Android core worker

This standalone Gradle application consumes the supplied **actual** ProjectM TV core AAR, including its JNI library, textures, complete preset asset set and `presets.idx`. It has no Activity, AndroidX dependency or replacement ProjectM implementation. Build from the repository root with its wrapper:

```sh
./gradlew -p tools/core-corpus/android-worker :app:assembleDebug -PcoreAar=/absolute/path/core.aar -PcorpusApplicationId=nl.neerdael.projectmtv.corpusbaseline
```

Use `nl.neerdael.projectmtv.corpuscandidate` for the other variant and `nl.neerdael.projectmtv.corpuspublished` for the exact published-AAR smoke role. The host must force-stop the selected application before **every** job, stage the files through `run-as`, set `debug.projectmtv.preset` to a bounded prefix of the exact target, and start one instrumentation process:

```sh
adb shell am instrument -w -e job /data/user/0/nl.neerdael.projectmtv.corpusbaseline/files/jobs/JOB/request.json nl.neerdael.projectmtv.corpusbaseline/nl.neerdael.projectmtv.corpus.CorpusInstrumentation
```

The JSON request fields are:

| Field | Meaning |
| --- | --- |
| `preset` | Exact asset filename, including `.milk` |
| `seed` | Integer seed passed as Java `long` to the private bridge |
| `referenceWidth`, `referenceHeight` | Paired `0,0` for authored behavior, or both positive for reference dimensions; mixed zero or negative values are rejected |
| `width`, `height` | Positive dimensions of the real RGBA8 GLES3 EGL pbuffer |
| `pcmPath` | Absolute app-private path to exactly 705600 unsigned mono PCM bytes |
| `instrumented` | `true` enables the private seed/reference/frame-clock bridge; `false` is a labeled nondeterministic published-AAR smoke run |
| `expectedPresetCount` | Optional inventory assertion, default 9606 |
| `outputDir` | Optional absolute app-private directory below the request's directory; defaults to `output` beside the request |

All paths must be below the application's private `filesDir`. Use a unique directory per job. An existing `manifest.json` is preserved and rejected. The worker writes a skip mask containing every indexed preset except the target; it leaves the AAR's index and assets unchanged. Asynchronous texture extraction and indexing must finish with exactly one eligible preset within 30 seconds, before any render call.

Only production `ProjectMJNI` initializes the engine, applies public settings, receives the 1470-byte PCM blocks and draws all 480 frames. The core's production audio delivery queries `projectm_pcm_get_max_samples()` and retains that many trailing samples (576 in the pinned upstream4.2 engine; spectrum storage is separately512). Instrumented frames use `frame / 30.0` seconds; smoke frames use the real clock paced toward 30 FPS. The settings disable auto changes, beat cuts and blank skipping, select category `all`, mesh 48×32, preset duration 3600 seconds, soft cuts zero and `CLASSIC` transition mode with `lowEndDevice=false`. Production memory pressure pauses background prewarming for 20 seconds before frame zero and is refreshed every 10 wall seconds; each call is recorded.

Every frame must retain the exact requested preset, one eligible preset, one preset change, applied category `all`, draw framebuffer zero and no GL error. Captures at frames 120, 150, 180, 210, 239, 300, 390 and 479 are lossless full-resolution PNGs of the final output. Capture explicitly binds read framebuffer zero, records both the previous and capture read bindings, and restores the previous read binding. Checking the draw binding alone is insufficient: Native direct rendering can leave an internal feedback FBO bound for reads. The recorded `rgbSha256` hashes top-down RGB8 bytes, with alpha discarded. The host must decode each PNG, verify that hash and calculate its sampled 4/12-second metrics. These eight captures are not hashes or metrics for every frame. Captures stay full size so the host can apply one consistent downsampling method. Reverify archived manifests without the read-binding fields with their frozen historical helper; they cannot certify final-output capture with the current verifier.

The atomic `output/manifest.json` is written after production `ProjectMJNI.release()` while the EGL context is still current, and after EGL destruction. It records `status`, frame count, hashes, captures, driver/device information, preset checks and cleanup errors. Failures, including initialization or release failures, have `status=failed`; process exit alone is insufficient to accept a result. The host pulls the owned job files, verifies them, and removes that job directory before proceeding. The shared extracted `files/corpus-textures` pack can remain across fresh processes. Native crashes require host timeout/crash handling because the Java finally block cannot run.

The private `LabBridge.initialize(long,int,int)` and `LabBridge.setFrameClock(double)` are exported only by the instrumented actual core AAR. They control reproducibility; they do not create, load, render or release a ProjectM instance. No bridge is invoked in published-AAR smoke mode.
