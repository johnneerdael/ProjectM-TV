# Remote checkpoints of supplementary native evidence

The original direct patched-projectM scan is stopped. It includes TV engine patches 0001–0025 but bypasses the `projectm-tv:core` wrapper, so its results are **supplementary evidence only**, not the requested core-backed corpus baseline. Preserve its immutable protocol and existing records. Run only the finite `--once` backup for this stopped scan; do not restart its renderer or launch a monitor waiting for 9,606 records. `corpus_checkpoint.py` uses a separate clean worktree at `.worktrees/quad-lines-corpus-backup` on `evidence/quad-lines-corpus-2026-10-04`; it never merges, releases, removes worktrees, or changes app code.

The existing 413-preset archive is reused after archive/member checksum verification. Only additional checksum-valid terminal rows are packaged. Each batch preserves both native repeat records, all retained per-frame/full-stream hashes and metrics, three thumbnails, manifests, worker jobs, stderr and band traces. Explicit failed, timed-out and nondeterministic rows remain in coverage. Incomplete presets are skipped. Missing or corrupt evidence appears in the monitor's integrity issues.

New archives under `corpus-checkpoints/incremental/` contain at most 25 MiB each, with individual files below 100 MiB. Each immutable archive declares its exact covered preset keys and every member's byte count/SHA256. Its adjacent JSON records the archive SHA256. The inherited 413-preset archive predates the smaller batch limit.

The monitor verifies the live protocol/inventory, completed record checksums, provenance and complete successful native repeats before packing. It commits each batch only in the backup worktree, pushes that commit, then confirms origin advertises the exact HEAD. `remote_verified_presets` advances only after this acknowledgement. A failed push leaves a retryable local commit; the next cycle retries it before packing more presets. No credentials or Git authentication output are written to logs. If a process dies after publishing an archive but before its commit, the dirty-worktree guard stops automatic processing. Verify that archive and sidecar, commit only those checkpoint files in the backup worktree, then restart the monitor; never discard the uncommitted evidence or include unrelated files.

Run checks before starting:

```sh
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/corpus_checkpoint.py --self-test
```

Create the backup worktree once from the already pushed follow-up branch. Keep it after completion:

```sh
git worktree add -b evidence/quad-lines-corpus-2026-10-04 .worktrees/quad-lines-corpus-backup followup/quad-lines
```

From the owned follow-up worktree, back up existing terminal supplementary records once:

```sh
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/corpus_checkpoint.py --once
```

`build/follow-ups/corpus-checkpoint-monitor/status.json` gives process ID, confirmed remote HEAD/count, local count, integrity issues, and partial/final remote coverage. Save `launch.json` and `monitor.log` there when launching the finite backup. Archives, adjacent metadata and status identify the evidence role as `supplementary-direct-patched-projectm-not-projectmtv-core`. A finite backup can finish successfully while full 9,606-preset coverage remains false.

The script also has a ten-minute periodic mode, but it is not authorized for the stopped direct-worker scan. Establish a separate immutable protocol and validated core-backed source before considering such a monitor.

To restore, fetch the evidence branch and verify each archive's adjacent checksum plus `checkpoint-manifest.json` member hashes. Extract archives into a separate checkout, preserving their original `build/follow-ups/corpus-baseline/` paths. Never overwrite a newer live scan with older evidence. The initial archive includes the immutable inventory/protocol and full source-family classification. Run `corpus_audit.py` after restoration or final completion; remote file coverage does not replace the final scientific audit.
