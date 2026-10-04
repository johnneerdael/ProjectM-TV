# Isolated emulator speed probe

Use only the newly owned emulator serial `emulator-5580`, PID92211, API34/default/arm64-v8a AVD under `build/follow-ups/core-corpus/mac-emulator/`. Existing AVDs and physical devices are outside this probe. `launch.json` records headless, host GPU, no-audio, no-snapshot invocation. The helper requires the exact owned PID/AVD plus `ro.kernel.qemu=1` and completed boot; it issues no wake or system-property changes.

`emulator_probe.py` imports the physical runner read-only for pure job construction and artifact validation, and uses its own exact-serial ADB operations. It does not alter the physical runner's guard or dataset. The new protocol copies only the same APK/source/input configuration and canonical480-frame PCM, adds emulator fingerprint and helper/validation-source hashes, and saves under `mac-emulator/speed-probe/`. Different driver results are separate oracles; these timings are Android-emulator throughput, not TV performance.

After checkpointing this helper, run the first compact actual-core control:

```sh
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/core-corpus/emulator_probe.py --tv-protocol build/follow-ups/core-corpus/measurements-core-v4/protocol.json --install --control 0
```

Repeat with `--control 1` and `--control 2` without `--install`. All jobs render2364×1330 for480 frames through actual ProjectMJNI and the installed optimized core ELF. Compact mode retains PNGs, metrics, native selected-frame hashes, actual preset/counter/PCM traces and runtime core/GL metadata. It verifies the requested preset, producer trace checksum and every retained thumbnail. No raw native files are retained. `--mode full` hashes all480 frames while retaining the same selected thumbnails, enabling an independent full-versus-selected driver check. No corpus scan is launched by this helper.

Instrumentation, pull and core-logcat outputs are retained even for failed controls. Existing speed rows cannot be overwritten. Preserve them before installing another role; use the reviewed normal emulator-enabled host runner for the eventual complete pilot.
