# Quad batching integration — 2026-10-09

Implemented on `fix/predictor-corpus-batching` in the isolated worktree
`.worktrees/predictor-corpus-batching`, based on `b3737a56`. The active original
corpus and its code remain unchanged. Original authored assets/native producers
and the47-field export schema are unchanged.

Two regression controls failed against the original implementation because
strips/vectors invoked per-quad full-frame raster calls. The fix batches generated
quads while retaining independent vector endpoints and original triangle/blend
order. A reviewer found a skipped-quad finite-framebuffer validation regression;
a dedicated test reproduced it, then the guard was restored once per active
quad frame. Finite no-op behavior is retained. No important review issues remain.

## Verification

- New regression/equivalence tests:19passed, covering16open/closed,
  additive/alpha, quantized/unquantized and retained-window combinations, allocation
  counts, independent vector endpoints, input ownership and skipped-quad validation.
- Full prepared analyzer suite: **1,637 passed,92subtests passed** (99.01s).
- Strict MkDocs build and `git diff --check` pass.
- Bounded resource smoke:60frames/15fps/64×36, three47-field successes and one
  explicit missing-texture failure; paired ZIPs of3/1cases pass CRC/source-hash
  checks. Resume has zero pending, retaining terminal outcomes and sealed ZIPs.
- Earlier candidate's three exact480p/60-frame completions remain recorded in
  `full60-results.json`; no additional unchanged timeout run was started.

The first broad test attempt exposed missing new-worktree native adapter links;
it was stopped. Prepared historical adapters were then linked read-only and the
suite rerun with its pinned environment, producing the passing result above.
No source identity guards or tests were weakened to bypass those setup failures.

## Fresh run

The Downloads launcher points to this worktree and chooses
`~/Downloads/ProjectM-TV-preset-corpus-15fps-480p-batched`. Stop the old controller
with Ctrl+C and wait for its partial ZIP/shutdown, then run the launcher with
`--workers 4`. This is a fresh9,606-preset inventory; subsequent launches resume
this new folder. The old output folder is preserved. No full corpus was started
by the implementer. The final preflight checks inventory/settings only.

The old Python environment/source29adapters and historical verification adapters
are shared via local build symlinks from `predictor-visual-loop`. Keep those
prepared dependencies. The implementation is independently committed; main is
not merged and no app/AAR release is cut by this task.
