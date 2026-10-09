# I12 — Stateful per-pixel physical traversal

Candidate0026 evaluates legacy per-pixel programs in original physical bottom-to-top order, retaining X ascending and writing each node's original attribute slot. Compiled custom traversal is unchanged; failed custom uses legacy. The no-equation fill keeps its current contiguous order. No Q/local/register/global-memory reset is introduced, and no extra equation, vertex, buffer or pass is added. Same-node inputs/values, CPU trig, negative powers, released static cache/upload policy and prepared replay remain intact.

The original mapping is established independently by plugin.cpp's ascending raw grid, support.cpp's negative-height projection, and legacy emitted-Y flip. This mapping is not extended to the absent original custom VS.

## Executable proof

Actual EEL→production vertex attributes prove every node's carried Q/local/register/global-buffer placement on8×8 mesh over two frames. Q copies once per frame; ordinary/local and memory recurrence continue. Legacy top-left ordinal73/dx.073 fails baseline ordinal1/.001 and passes candidate. Compiled custom positive order remains unchanged; failed custom follows legacy. Prepared replay neither reexecutes equations nor changes attributes; stateless dx=x*.001/dy=y*.001 stays identical. [RED](source-red.txt) · [Normal50/50](source-normal50.txt). Fresh26-patch application passes.

## Original and remaining qualification

The exact unchanged primary candidate is `shifter - neon pulse.milk`, SHA256 `605d80e5c1480be3fd21ef57cbd2780cbff192f06be5b6a4268ddf2d80aafcf2`. Its coy/cox recurrence detects descending y rows and feeds dx/dy before updating oy/ocoy/q1. Per-frame warp0 removes oscillator-Y as a competing effect. Ten lexical candidates remain an unconfirmed impact list.

Its startup `1/tic` needs a declared finite/warm timing context; do not infer original Windows appearance from an undefined startup. Twelve final-output Native4K runs now pass: original, finite legacy and compiled-custom control, each before/after with two repeats and480 frames. All eight selected RGB captures repeat exactly; custom is identical before/after. The finite fixture resets q1 each frame and advances it once per node to drive dx, producing the expected opposite row-dependent shear. This is the strong visual diagnostic. [Finite before](legacy-before-4k.png) · [source-corrected after](legacy-after-4k.png).

The unchanged original uses surface initialization clock0 and subsequent `(frame+1)/30`, with manifest capture times corrected by1/30; this finite warm first timestep avoids undefined startup1/tic without editing preset/native bytes. The original is dark: max selected full-frame RGB MAE .127004 on0–255, at frame180. Its large changed-pixel counts include small channel rounding/feedback changes and must not be sold as a dramatic visual improvement. [Original before](original-before-4k.png) · [after](original-after-4k.png) · [metrics](i12-original-image-metrics.json) · [repeat results](native-results.json).

Focused cost is qualified: three isolated ABBA cycles/12 runs give mean4.902315ms before versus4.776064ms after,−2.575%; per-cycle changes+1.105%,−5.573%,−3.294%. No consistent slowdown is observed in this witness; no universal speedup or physical-TV FPS claim follows. All selected RGB frames in timing runs match the original witness by role. No extra equation, pass, target or buffer is added. [Cost results](cost-results.json) · [isolated log](i12-isolated-timings.txt).

The exploratory first12-run batch overlapped compiler preparation and measured+3.023% overall, including one+17.554% cycle. It is retained with its limitation, not silently discarded. The second batch ran after builds and source-test jobs finished, with no concurrent task compilation. Final combined integration remains pending. Captures are source-derived GLES results, not original Windows screenshots.
