# Root-free automatic memory policy: focused AM6 witness

Recorded 2026-10-08 in the workspace; device log timestamps are 2026-10-07 and are retained without timezone conversion. This is a focused allocation/FPS/playback witness, not whole-corpus performance or image-fidelity certification.

## Change and controls

On nominal 4 GB+ devices, remove the total-RAM/5 reserve floor. Use Android threshold + 128 MiB, retaining 64 MiB recovery hysteresis, rendering-growth estimates and resize overlap. Smaller devices retain the existing conservative reserve. No root code, process-cleanup capability, additional setting, permission or runtime dependency ships.

The old-policy control and candidate were built from the same task worktree based on `0b6e4281`. The control substitutes only the original `RenderMemoryBudget.java` from that base through an ignored validation-only Gradle init script. The candidate uses the changed policy. Both use release rendering bytes and separate profile application IDs: `nl.neerdael.projectmtv.memorybaseline` and `.memorycandidate`.

[Artifact identities](artifact-identities.json) records APK and native-library SHA256 values. Both ABIs' native-library hashes match exactly between roles. Original and changed reserve bytecode were inspected separately before saving the role APKs. The standard release AAR and profile APK also built successfully for both ARM ABIs.

## Device and inputs

- Awake user-authorized rooted Ugoos AM6, Android 9, 32-bit; explicit ADB endpoint `192.168.50.80:5555`, captured Android user 0.
- Mali-G52/GLES 3.2; detected panel 3840×2160. Total memory from ActivityManager: 4,055,408,640 bytes (3,867.5 MiB).
- Pinned bundled preset: `suksma - dotes hostile undertake - fake rivals real(1).milk`.
- Auto, remembered start 1080p, 30 fps cap, Standard trails, 7-second transition allocation setting. Automatic switching, blank/slow skipping and updater disabled in the task-owned role apps.
- Live Milkbeat v0.9.46 audio; process PID 6633, UID 10081, session 649. Playback commands were not sent. PCM, track positions, renderer clock and random seed were not frozen, so the roles are not an exact audio/image comparison.
- Root was used only by the external validation harness to prepare isolated app preferences; the installed policy uses ordinary `ActivityManager.getMemoryInfo()` and requires no root. A shell-only Java diagnostic queries that same API without allocating a stress workload. The first diagnostic attempt failed because its standalone main lacked a Looper; the corrected diagnostic completed. No product source depends on it.

## Observations

| Observation | Old policy | Revised policy |
| --- | --- | --- |
| Android pressure threshold | 144 MiB | 144 MiB |
| Reserve plus recovery margin | approximately 837.5 MiB | 336 MiB |
| Sampled available memory, including pre-launch | 1,131.1–1,271.8 MiB | 1,073.6–1,341.4 MiB |
| Observed ladder sequence | 1080→1260→1440→1800→1440 | 1080→1260→1440→1800→1440 |
| Slow sample at 1800p | about 21 fps | about 21 fps |
| Active audio-output snapshots checked | 7 | 8, including resume |
| Audio output | frames progressed, buffers nonempty, zero recorded underruns | frames progressed, buffers nonempty, zero recorded underruns |

Both roles reached 1800p and lowered to 1440p for FPS. This witness demonstrates the preserved performance downshift and playback continuity during these observations; it does **not** demonstrate a higher sustained resolution on this preset. The policy regression test separately demonstrates moderate measured headroom permitting an upward step that the old reserve rejects, while still rejecting an unsafe immediate 4K allocation.

The candidate was left for the normal app and resumed; rendering and audio capture resumed at 1440p with nonzero audio. Later FPS samples were 27.9, 29.6 and 26.8; do not describe that resume as perfectly stable 30 fps. No low-memory pressure was deliberately induced on the user's TV. Unit tests cover genuine pressure, unknown samples and preserved/recreated/pending allocation rules.

## Captures

The clean captures below show both role apps rendering the same pinned preset at the requested initial 1080p setting, approximately eight seconds after launch. They were taken separately from the 90-second sampling journeys, after suppressing the unchanged first-launch notification-access prompt in the test apps only. They are display witnesses; varying live audio/time/random inputs preclude a fidelity claim.

| Old policy | Revised policy |
| --- | --- |
| ![Old-policy AM6 capture](baseline.png) | ![Revised-policy AM6 capture](candidate.png) |

## Validation and restoration

- `./gradlew :core:testReleaseUnitTest :app:testReleaseUnitTest`: 74 core + 63 app tests, zero failures/errors/skips. New tests were observed failing under the original reserve before the implementation change.
- `./gradlew :app:assembleProfile :core:assembleRelease`: successful for armeabi-v7a and arm64-v8a. Existing Java 8/JDK21 and upstream C++ warnings remain.
- `bash core/src/test/native/run_native_tests.sh`: engine/policy/JNI controls and 34 ASan/UBSan projectM regressions pass. Host transition-overlay GL test skips because EGL/GLES development files are unavailable.
- `uv run --with-requirements docs/site-requirements.txt --no-project mkdocs build --strict`: passes.
- Six local review personas reported no actionable findings. GitHub Codex review, CI, merge and publication remain separate gates.
- Original empty `debug.projectmtv.preset` restored; normal `nl.neerdael.projectmtv` activity restored while awake. Only the task-owned validation packages were force-stopped. Milkbeat's process remained PID 6633 and active audio output was verified. No unrelated app was stopped by the harness.

Raw logs, per-snapshot memory/media/AudioFlinger/process dumps, APKs, validation-only scripts, bytecode and capture hashes remain ignored under `build/memory-policy-validation/` in this task worktree. Its `SHA256SUMS` ledger identity is `c8c0d7cca90736b0f2205830a588885fd18912d1341644a86f4bc8b6f05b052f`. The ledger covers the captured files at this checkpoint; later verification files require a new ledger identity. Keep these artifacts with the worktree rather than implying the committed summary contains every raw dump.
