# Predictor memory/error repair — 2026-10-09

Confirmed predictor defects: evaluation closure cycles retained borrowed arrays
and sampler closures until cyclicGC; repeated equivalent branch contexts
recomputed/cached predecessor graphs independently. Weak-reference and duplicate
sampling regressions failed before their fixes. Neither is an AAR defect.

The old saved Royal255worker exitedSIGKILL(-9), and macOS reported severe memory
compression pressure four seconds later. The report listed Python footprints
34.72/95.53/30.43GiB without an individual Python kill reason or confirmed
workerPID mapping. The user lost the controller's terminal traceback. Therefore
neither the exact controller exception nor the individual SIGKILL cause is
proven. An empty `MemoryError()` reproduces the old blank stop message, but this
is a diagnostic demonstration, not attribution proof. User subsequently deleted
the prior corpus folder by intention; it was not recreated or imported.

## Changes and controls

- Finally releases evaluator-owned caches/contexts and local input/callback
  references without mutating caller inputs or invalidating returned storage.
- Exact lane sequences share immutable state contexts; explicit loop updates
  keep separate epochs. on_sample observes uncached evaluations, not every
  native texture instruction. Production texture callbacks are pure lookups.
- Fatal reports include exception types and persist unique timestamp/PID JSON
  tracebacks; diagnostic failures cannot replace original exit1.
- Worker groups have a declared monitored memory budget (default6GiB).
  Darwin uses physical footprint, Linux resident+swap. Process enumeration has
  a2s timeout and failure stops the controller. Only owned groups are measured
  and killed; MemoryLimitExceeded retains an explicit error/null feature record.
  Sampling at1s can overshoot: this is not a hard OS quota or a universal bound.

Cleanup-only Royal255retest stopped at the diagnostic6GiB guard after43.8s.
After context reuse, its exact60-frame/15fps/854×480 simulation computed all47
feature objects in315.22s at an observed2.74GiB peak. This exceeds the standard
300s deadline; it is not credited as a default-timeout pass. A3-frame128×72
comparison retained exact equality of all47feature objects while peak cached-node
counts fell from6141to1879in one warp evaluation. No AI/native images were used.
All derived inputs were recreated under the isolated diagnostic build directory
using the same declared synthetic policy; no user corpus output was overwritten.

The two-worker tiny-memory guard smoke ended both workers explicitly and sealed
a paired ZIP with null feature records. The normal-budget two-worker smoke and
resume are recorded by the producer; failed records are not fabricated scores.
Independent review cleared lifecycle, state epoch and monitoring/diagnostic
findings after regressions. Final prepared suite/build results are recorded in
this task's PR. No full-corpus restart is performed by this task.

## Restart

Use a new output identity with the repaired model and start with two workers.
`--timeout600` accommodates the observed315s case; source-domain/resource errors
remain explicit. User data is not recovered after deletion. Keep the repaired
worktree plus its shared `predictor-visual-loop` environment/adapters. No main
merge of experimental predictor code is requested by this repair.

Final validation: **1,651 tests and92subtests pass**; strictMkDocs anddiff checks pass. Normal-budget smoke computes two47-field records; resume reportszero pending and unchanged sealed outputs.
