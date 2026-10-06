# Focused Native trails validation

Use a dedicated, task-owned Android emulator or a physical TV authorized for this task. Do not use the corpus owner's
`emulator-5580` or reuse another task's work directory. Physical GPU performance
and compatibility cannot be inferred from an emulator.

`presets.txt` selects the known darkening, clipping, motion-vector, blur and chaotic
witnesses from the Native 4K handover, plus midgit and Hexcollie controls. This is
focused regression coverage, not a repeat of the full 9,606-preset corpus.

Create a Python environment using `tools/preset-lab/requirements.lock`. Initialize
submodules, supply `local.properties` and use the repository's JDK/SDK/NDK versions.
Run the scripts from the repository root.

```sh
python -m pytest tools/native-trails tools/core-corpus -q
python tools/native-trails/build_validation.py --commit BASELINE_SHA --policy native --role baseline-native --work build/native-trails/workers
python tools/native-trails/build_validation.py --commit CANDIDATE_SHA --policy native --role candidate-native --work build/native-trails/workers
python tools/native-trails/run_validation.py run --device OWNED_EMULATOR --workers build/native-trails/workers --presets tools/native-trails/presets.txt --work build/native-trails/focused
```

For an upstream rebase comparison, use `--role rebase-baseline` and
`--role rebase-candidate` in a new work directory. Their worker packages are
`nl.neerdael.projectmtv.corpusrebasebaseline` and
`nl.neerdael.projectmtv.corpusrebasecandidate`; the existing corpus packages remain
separate. The builder records the private Gradle package allowlist transformation
and the resulting package in its identity. Historical role/package assignments
and frozen runner protocol contracts are unchanged. A migration with a different
patch series needs a separately recorded bounded comparison protocol; the old
runner's prefix/+1-patch provenance gate cannot validate that migration.

The builder defaults to `--abi arm64-v8a`. For a TV running 32-bit Android (check
`adb -s DEVICE shell getprop ro.product.cpu.abilist`), build both comparison roles
with `--abi armeabi-v7a`. The selected ABI is recorded in the build identity;
the production APK/core continue to include both supported ABIs.

The builders refuse existing role directories. Each build exports a committed
revision and resolves that revision's engine and evaluator gitlinks into private
checkouts, even when the live submodules are at another revision. It composes
Preset Lab deterministic engine instrumentation with the actual core, then records
the exact pins, ordered patch hashes, transformations and compiled AAR/APK identities.
Private line-reference controls let authored, old Native and new Native share a
frozen harness. Production settings go through the additive public JNI API.
Instrumented AARs are test artifacts, not byte-identical release binaries.

The current engine is based on unreleased projectM 4.2 master, pinned to
`6f6480746`. Its private constructor clock starts at zero before preset loading;
its public `projectm_set_frame_time` API receives the logical clock before both
normal and framebuffer render calls. Historical 4.1.7 snapshots retain their
private clock hook and their own source/patch identities. Clock instrumentation
changes create a new instrumentation identity; rebuild workers into a new work
directory rather than reusing an earlier frozen protocol.

The runner freezes PCM, clock (`frame/30`), seed, source, artifact, driver and
preset identities. It refuses changed inputs, uses an exclusive lock, restores
its debug preset property, verifies all eight full-resolution PNG/RGB hashes,
and checks instance/context cleanup. `--profiles` can select profiles from the
frozen protocol without redefining its inputs. Inspect every completed row;
never treat an exited runner or a partial progress file as successful coverage.

Compare every selected hash for `native_before` / `native_off`, `authored` /
`authored_repeat`, and `standard` / `standard_default`. Inspect authored / old
Native / Standard / Medium / High full frames and crops. The retired capped AAR
is a historical download only; the owner no longer requires it as a supported
candidate or an identity gate. Brightness and image-error figures are diagnostics;
near-black and chaotic presets require particular care. Every enabled 4K profile
must report its active1280×720 canvas, rather than shader/resource fallback.

Frame timings measure `onDrawFrame` plus `glFinish` over 360 frames, excluding PNG
encoding and transport. They are serialized engine timings on the emulator, not
TV app FPS. Guest process PSS does not measure all host GPU texture memory.

For an uninstrumented published-AAR smoke, first build the existing
`tools/core-corpus/android-worker` with the checksum-verified released Native AAR,
`-PcorpusApplicationId=nl.neerdael.projectmtv.corpuspublished`, then run:

```sh
python tools/native-trails/run_validation.py smoke --device OWNED_EMULATOR --apk WORKER_APK --aar RELEASED_NATIVE_AAR --work build/native-trails/published-smoke
```

This smoke uses the real clock and does not prove deterministic identity or
brightness fidelity. Keep it separate from the instrumented comparison.

## Android user scope and historical captures

New runs capture `am get-current-user` once, reject invalid IDs, and freeze the numeric `user_id` in schema-2 protocols. Installation, package lookup, instrumentation, run-as, private request/output paths and cleanup use that same ID. The summary verifier checks the frozen user scope. Do not change users mid-run or edit a frozen protocol to resume under a different user; choose a new work directory.

The completed `focused-v1` measurements used the verified user-0 emulator before this scope was recorded. Their schema-1 protocol and capture identities remain immutable. Historical verification requires the original checksum-pinned runner source explicitly; it does not pretend that the updated runner produced those captures. Recover that source from the recorded commit, then use a fresh summary output:

```sh
mkdir -p build/native-trails/legacy-validator
git show a8a75f4435c80c46aaa99274f6007ac285170eeb:tools/native-trails/run_validation.py > build/native-trails/legacy-validator/run_validation.py
python tools/native-trails/summarize_validation.py --work build/native-trails/focused-v1 --out build/native-trails/summary-legacy-verified --legacy-runner build/native-trails/legacy-validator/run_validation.py
```

The verifier checks the source SHA256, labels this as historical user-0 compatibility, and keeps its original unscoped-runtime limitation explicit. It refuses unknown schema-1 producers and refuses a legacy-source argument for schema 2. The archived original validators also preserve the broad Mac protocol's source identities; changing a verifier is not a new brightness measurement.
