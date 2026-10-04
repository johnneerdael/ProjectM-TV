# Texture-size declarations and uninitialized reads

A diagnostic pass over the 116 uninitialized-read witnesses distinguishes
origins instead of treating them as one missing function. Recurrent names include
rs39, back14, uv3 in14 and several rewritten uniform banks. Sixteen sections read
authored texsize_* globals. These were a reader binding discrepancy: native
targetTranslate removes `float4\s+texsize_.*` through the rest of the line and
rebuilds texture-size uniforms from descriptors. The reader retained the authored
globals as uninitialized storage.

The reader now matches native texture-size removal and rebuilding. It preserves
leading qualifier spillover and every real reference across the deleted span.
Comment removal is applied to the full source before reference collection so
commented declarations or deleted-tail comments do not create phantom sampler
bindings. Texture-size inputs require the real material/viewport bank; no image
dimensions are fabricated.

All 16 targeted source sections lower completely under the correction. Two
predictions were frozen before capture against the unchanged published core2.2.4
on the owned API34 emulator. An authored main texture-size declaration yields
RGB [.5,.5,1] under the explicit 128×72 viewport bank; a same-line ret=.7 statement
removed by native preprocessing yields black. Both match all 30 frames with zero
RGB8 error. Tests also cover multiple declarations, qualifier spillover and
commented names affecting frame-wrap binding order.

This closes a concrete interpretation discrepancy, not complete preset appearance
or material availability. The last full structural census remains the dated 371
snapshot until another full census is performed. Targeted witnesses are counted
as individual files, including related/duplicated shader sources.

Evidence: `tools/milk-analyzer/fixtures/texsize-binding-source-proof-2026-10-04.json`
and `tools/milk-analyzer/fixtures/texsize-binding-native-proof-2026-10-04.json`.
The broader origin diagnostic is local at
`build/milk-analyzer/uninitialized-diagnosis-2026-10-04/report.json`.

Next high-frequency question: many rs reads occur in `0*rs`; others are dead
intermediate expressions. Establish exact generated shader semantics and effect
dependencies before deciding which reads can be proven irrelevant. Preserve
genuinely undefined live values as unresolved.
