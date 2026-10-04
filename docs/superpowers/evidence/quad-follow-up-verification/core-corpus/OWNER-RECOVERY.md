# Explicit owner-epoch recovery

The original369263 protocol records the historical emulator PID92211 and its launch receipt SHA. After that process died, the same owned AVD/data/config was restarted as actual PID20334. Preserve the original receipt/logs. Do not replace the original protocol or fabricate the old PID.

`owner_bridge.py` loads the unchanged frozen `run.py` in an isolated new process. It replaces only volatile ownership validation with an explicit verified epoch: actual live PID/command/ownedAVD/qemu, original receipt chain, same guest fingerprint/ABI, actual guest GPU/GL identity, original renderer source/APK/core/harness/instrumentation/PCM/inventory checksums and render configuration. The renderer methods, requests, frame/preset/audio pathways and cache keys remain unchanged. Old records retain their original provenance. New records reference the actual epoch receipt under `owner-epochs/<actual-pid>/`.

Run three exact canonical controls before resuming: Royal480, Matrix240 and Echasketch480. These are separate probe records, not counted as corpus coverage. Their selected native hashes must match the authenticated original baseline pilot. Any source/AVD/driver/input discrepancy stops recovery.

```sh
build/preset-lab-venv/bin/python -m unittest discover -s docs/superpowers/evidence/quad-follow-up-verification/core-corpus -p test_owner_bridge.py -v
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/core-corpus/owner_bridge.py probe --work build/follow-ups/core-corpus/measurements-core-emu-baseline-v1
```

After source checkpointing and three verified probes, resume the exact frozen scan through the bridge with `scan --work <absolute-dataset> --roles baseline --serial emulator-5580 --reviewed-pilot-sha256 ba49e6f7796480f0190731f980ccb39847ddf2b22c8c4f155c9e35210e0cee82`.

`supervise_baseline.py` uses a separate watcher lock and the renderer's real host lock, refuses altered frozen inputs, and restarts only an absent matching scanner while the same owned emulator remains live. It never restarts the emulator or fabricates completion. Stop the supervisor before an intentional scanner pause. Separate stdout/stderr logs preserve future failure details. The independent completion notifier still requires complete9606×2 baseline jobs and verified remote ACK.
