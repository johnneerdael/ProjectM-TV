# Focused blocked-set reduction: unused pure initializers

The user narrowed current work to the known 315 source blockers. Renderer
precision work is preserved as a checkpoint; it is not the priority for this
blocked-set task.

One recurring source pattern computes a local k1 from unwritten global back,
then never uses k1. The interpreter rejected that unused calculation and thus
the entire preset, although the calculated value does not affect output.
Entry-point lowering now recognizes unused, side-effect-free scalar/vector
local initializers. It preserves an unwritten local binding rather than inventing
a value or modifying source, and excludes only the irrelevant initializer.

Liveness includes later declarations in the same statement. The purity check
examines aggregate elements as well as constructor arguments; user-defined
helpers and transitive outputs, textures, indices, arrays/matrices and implicit
output variables are not skipped. Helper bodies remain conservative because
their return expression is lowered separately. Loop initializers cannot be
discarded because their counters are referenced by the condition/increment
outside the initializer statement list.

Review caught an aggregate-helper mutation being lost in an early version.
Regression tests reproduced it, and the corrected element walk preserves the
mutation. Existing indexed initializers remain represented for domain accounting;
this change does not claim to certify unused index domains universally.

Fresh source re-reading and lowering of all 315 known blocked presets confirms
15 clear their last recorded structural blocker and 300 remain. No new full
9,606-file regression census or complete visual-accuracy claim is made. The
remaining uninitialized family falls from60 to45; other families are unchanged.

Two frozen, blocker-relevant native controls against unchanged published2.2.4
verify the ignored dead read and a retained helper mutation inside an aggregate.
Both match all 30 RGB8 frames with zero maximum error. All667 analyzer tests and
35 subtests pass at this checkpoint.

Evidence: `tools/milk-analyzer/fixtures/focused-blockers-300-2026-10-04.json` and
`tools/milk-analyzer/fixtures/dead-initializer-native-proof-2026-10-04.json`.
Full blocked-set witnesses:
`build/milk-analyzer/focused-315-dead-init-final-2026-10-04/gap-priority.json`.
