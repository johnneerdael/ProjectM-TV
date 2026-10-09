# ARM64 input producer: separate source diagnostic

This directory prepares a CPU-only Android executable. No compilation, device command, GPU context or draw was run by the preparing agent. Root owns execution on emulator-5640. The shipping APK/AAR and its exports remain unchanged.

## Frozen link identity

Use the existing retained-role static archive recorded in `frozen-link-inputs.json`: source commit `ac3dd034c15dced5423feed3077c15c39580823b`, 27 retained patches, AAR `f62c136ba9f3880d42cbac2c1c170b3ffcedd3246bbf0422cb3ac0faf53c9077`, ARM64 native `af04f342bdd247c9fdaa38a28aed688577061d27276ee0c347f20f15a50eced6`. The projectM archive SHA256 is `1b51e9877fdbfbb6e2a1aaa802430c46c7d489506df8ce6fead21b70c823e483`.

An `llvm-ar` inventory confirmed this archive already includes the four production Audio objects, all waveform factories/modes, evaluator and GLAD objects. The frozen shipping link uses that one archive plus Android GLES/EGL/log/android/atomic/m libraries. The prepared link script reuses it; it does not rebuild or modify engine objects. Archive hashes are checked before a link can execute. Original PCM compile flags, NDK 27.3.13750724 compiler/sysroot and source hashes are retained in the JSON identity.

## Root build and owned-device commands

From the repair worktree, first print the exact reviewable link command:

```sh
python3 build/audit/extended-mode-proposal/arm64-input/build_arm64_target.py
```

Then opt into compilation:

```sh
python3 build/audit/extended-mode-proposal/arm64-input/build_arm64_target.py --execute
```

The new translation unit uses the frozen compiler/sysroot, Android21 target, C++17, O2, PIE, static C++ runtime, section garbage collection and matching static/GLES declarations. These affect only this diagnostic executable; production FFT/libm callers and mode producers are the existing frozen ARM64 object code. `build-result.json` records the executable/source/sink hashes and exact argv after a successful link. Link feasibility is source/archive based until root actually runs the command.

Example owned execution, each command separate:

```sh
adb -s emulator-5640 shell mkdir -p /data/local/tmp/i21-input
adb -s emulator-5640 push build/audit/extended-mode-proposal/arm64-input/arm64-input-producer /data/local/tmp/i21-input/producer
adb -s emulator-5640 push build/audit/dot-diagnostics-audio.u8 /data/local/tmp/i21-input/audio.u8
adb -s emulator-5640 shell chmod 700 /data/local/tmp/i21-input/producer
adb -s emulator-5640 shell /data/local/tmp/i21-input/producer /data/local/tmp/i21-input/audio.u8 /data/local/tmp/i21-input/trace.jsonl
adb -s emulator-5640 pull /data/local/tmp/i21-input/trace.jsonl build/audit/extended-mode-proposal/arm64-input/target-trace.jsonl
```

Record executable and on-device PCM hashes, ABI/Android build fingerprint, architecture and runtime library provenance. Exit1 is setup/failure; exit2 reports an unsupported selected-frame input/geometry domain and must remain a failure with its trace. No install, shipping library replacement or JNI export is required.

## No context and no draw

`PresetState` contains renderer members whose constructors require GL object bookkeeping. `constructor_sink.hpp` supplies local bookkeeping callbacks and intentionally fails shader compilation. It creates no GL/EGL context, calls no resolver/driver, and traps all draw entry points. The sink does not feed audio, change producer arrays, implement FFT or replace waveform formulas. Its counters are recorded; shader failure is a constructor limitation, not shader qualification. The diagnostic never calls `LoadShaders`, `Waveform::Draw`, engine `RenderFrame`, GL readback or a GPU pass. The numerical work is the actual frozen ARM64 `Audio::PCM` pipeline and persistent factory producers.

## Worker clock and frame proof

The frozen worker's instrumented initialization calls `LabBridge.initialize` and `setFrameClock(0)` before `ProjectMJNI.init` and surface creation. The frozen bridge writes `lab::clock_seconds=0`. Frozen `TimeKeeper` constructs with `m_currentTime=0` and calls `UpdateTimers`, which reads that lab clock. Worker startup awaits the index without idle render frames; the main loop sets `frame / 30.0` immediately before each draw. `ProjectM::RenderFrame` updates audio with `SecondsSinceLastFrame()` and `m_frameCount`, which starts at zero and increments afterward.

Therefore this source-instrumented worker has audio clock0 and dt0 for its first completed frame, followed by exact double differences between consecutive `frame / 30.0` timestamps. This producer computes those differences rather than assuming a fixed rounded float 1/30. It passes audio frame labels0..479 to `UpdateFrameAudioData`; the float rendering clock is logged separately. This proof does not apply to an uninstrumented real-clock worker or a process that rendered idle frames before the job. Such roles require their actual timer trace.

## Transport, profile and output

The input is the frozen 705600-byte mono unsigned PCM, SHA256 `14a59e75249dee0dd15d74487688c248c6a4a4b24a843b6d6f612ccc5c408dbc`, in 480 complete 1470-byte blocks. Each block uses the API-returned latest tail, currently 576; 512 is the spectrum-bin count, not the transport tail. `Add(uint8_t,1,count)` preserves the production mono contract.

The declared diagnostic profile is physical3840x2160, authored/reference1280x720, mesh48x32, FPS30, scale1, smoothing0, alpha.8, mystery.25 and centered waveform. It is the common controlled profile, not every original stock preset's settings. Sixteen persistent real factory instances consume each frame's `FrameAudioData`. Every frame/mode JSONL row logs point counts and nonfinite outputs, spectrum pair minimum/nonpositive counts, lasso angle/argument/tan guards, raw bass/mid/treb, their attenuated values, vol/volAtt, exact clocks, transport count and sink activity. Nonfinite numbers are emitted as null with explicit failure counts; no epsilon or invented replacement input hides the failure. All selected image frames120/150/180/210/239/300/390/479 must be finite; early unsupported frames are retained in the trace.

This removes host FFT/libm/architecture differences from this separate source producer. It does **not** read the shipping JNI library's hidden `FrameAudioData`, certify shipping program selection or establish pixel/performance equivalence. Compare it with the clean unchanged-AAR screenshot role under the same transport/profile/clock, while disclosing that ownership distinction. Raw audio bands can support I26 source-input qualification; they do not resolve I26 shader producer semantics on their own.
