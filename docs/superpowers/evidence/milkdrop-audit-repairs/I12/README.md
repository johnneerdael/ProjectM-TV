# I12 — Stateful per-pixel physical traversal

Candidate0026 evaluates legacy per-pixel programs in original physical bottom-to-top order, retaining X ascending and writing each node's original attribute slot. Compiled custom traversal is unchanged; failed custom uses legacy. The no-equation fill keeps its current contiguous order. No Q/local/register/global-memory reset is introduced, and no extra equation, vertex, buffer or pass is added. Same-node inputs/values, CPU trig, negative powers, released static cache/upload policy and prepared replay remain intact.

The original mapping is established independently by plugin.cpp's ascending raw grid, support.cpp's negative-height projection, and legacy emitted-Y flip. This mapping is not extended to the absent original custom VS.

## Executable proof

Actual EEL→production vertex attributes prove every node's carried Q/local/register/global-buffer placement on8×8 mesh over two frames. Q copies once per frame; ordinary/local and memory recurrence continue. Legacy top-left ordinal73/dx.073 fails baseline ordinal1/.001 and passes candidate. Compiled custom positive order remains unchanged; failed custom follows legacy. Prepared replay neither reexecutes equations nor changes attributes; stateless dx=x*.001/dy=y*.001 stays identical. [RED](source-red.txt) · [Normal50/50](source-normal50.txt). Fresh26-patch application passes.

## Original and remaining qualification

The exact unchanged primary candidate is `shifter - neon pulse.milk`, SHA256 `605d80e5c1480be3fd21ef57cbd2780cbff192f06be5b6a4268ddf2d80aafcf2`. Its coy/cox recurrence detects descending y rows and feeds dx/dy before updating oy/ocoy/q1. Per-frame warp0 removes oscillator-Y as a competing effect. Ten lexical candidates remain an unconfirmed impact list.

Its startup `1/tic` needs a declared finite/warm timing context; do not infer original Windows appearance from an undefined startup. Whole-original Native4K before/expected/repeats, finite ordinal diagnostic, custom unchanged control, focused cache-locality costs and final combined integration remain pending. Source checks are not final visual or performance certification.
