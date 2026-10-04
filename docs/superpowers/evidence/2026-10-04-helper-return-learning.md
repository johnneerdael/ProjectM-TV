# Unconditional return boundaries

The recorded hardcore_stars functions have a return followed by an unreachable
second return. Requiring the only return to be the final statement rejected
this valid execution boundary. Helpers now execute through the first top-level
unconditional return, including its expression, and skip the trailing statements.
The same boundary is applied to transitive effect scans: dead writes cannot
create a false arithmetic sequencing conflict or visible/audio dependency.

Regression fixtures cover different return values, live/dead global writes,
uninitialized and nonfinite dead reads, dead loops, calls inside a live loop,
and a dead global write alongside a caller read. Scalar and batched interpreters
agree with the expected values. Conditional returns remain unresolved rather
than incorrectly choosing the later return. Returns inside blocks/loops still
need explicit control-flow modelling.

Two predictions were frozen before running the unchanged published core2.2.4
on the owned API34 emulator. Returning .25 before .75 yields RGB8 [64,64,64];
writing g=.3 before return and g=.9 afterward yields RGB8 [76,76,178] for
the specified composite output. Both match all 30 frames with zero byte error.
Remote AAR/library/DEX/clock-helper hashes were rechecked against runtime identity.

Rechecking four historical source witnesses does not make any entire preset
complete: uninitialized reads and effect-order ambiguity remain. Preserve those
records as unresolved. This verifies the return boundary, not full appearance
accuracy or branch/loop-dependent control flow.

Evidence: `tools/milk-analyzer/fixtures/helper-return-native-proof-2026-10-04.json`
and `tools/milk-analyzer/fixtures/helper-return-source-proof-2026-10-04.json`.
