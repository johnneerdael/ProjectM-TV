# Offline corpus exporter verification — 2026-10-09

The runner exports the existing 47-field forecast record from 60 actual state
updates at 15fps, 854×480. It uses CPU equation/audio/texture adapters prepared
from the exact v2.3.29 release source; no AAR-rendered frames, AI inference or
other agents' corpus/devices are involved. Source/artifact identities are saved
beside this report. This is exporter validation, not full-corpus accuracy evidence.

## Verified results

- Full prepared analyzer suite: **1,618 passed, 92 subtests passed** (97.17s).
- Focused runner/storage/input/native15/source29 suite: **40 passed**.
- Strict MkDocs build and `git diff --check` passed.
- Storage controls used 205 temporary cases: ZIP groups 100/100/5, matching
  source/result names and hashes, crash-after-ZIP recovery, locked ownership,
  terminal failures, corrupted output and changed input rejection.
- Current-code end-to-end resource run: four synthetic fixtures, 60 frames at
  15fps and 64×36. Constant composite, filtered random-image and 3D noise cases
  computed 47-key records. A missing texture remained unsupported with null
  record. Archives contained three/one paired cases. Resume reported zero
  pending and did not rerun terminal cases.
- Current-code 854×480 control: 60 frames at 15fps completed, exactly 47 feature
  keys, source/result pairing and ZIP CRC/hash checks passed; 58.06s wall time
  while the regression suite also ran. This is not a throughput average.
- Earlier bounded bundled-preset smoke: `$$$ Royal - Mashup (1).milk` computed
  at 854×480 in 47.54s. `(10)` reached its explicit 120s deadline and was
  archived as a timeout, without a fabricated feature record or automatic retry.

## Independent review

Initial review found escaped worker descendants, an input-preparation crash
identity window and incomplete integrity freeze checks. All three were corrected
and regression-tested. Independent follow-up passed three focused controls and
cleared the important findings. Periodic and pre-commit integrity checks stop
changed-input runs and leave affected presets pending.

Atomic writes/recovery cover interrupted processes, not a guarantee against
power loss. Custom inputs with dormant unsupported resources can still require
qualification; no default-bundled impact was demonstrated. Unsupported, error,
timeout and computed counts remain separate. Unknown feature values remain null.
No claim that every preset will compute successfully or that 15fps predicts
native30fps state identically is made.

## Local artifacts

- `build/preset-corpus/source29/`: prepared immutable source and eight adapters.
- `build/preset-corpus/smoke-final/`: resource integration results and two ZIPs.
- `build/preset-corpus/smoke-final-480p/`: complete requested-size control/ZIP.
- `~/Downloads/run-preset-corpus.command`: task launcher into this worktree.
- `~/Downloads/ProjectM-TV-preset-corpus-INSTRUCTIONS.md`: runnable instructions.
- `~/Downloads/ProjectM-TV-preset-corpus-examples/`: checked example archives.

Runtime instructions: [CORPUS_EXPORT.md](../../../../tools/milk-analyzer/CORPUS_EXPORT.md).
