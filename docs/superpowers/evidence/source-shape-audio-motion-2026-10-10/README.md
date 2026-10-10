# Shape-centre response to current audio bands

`audio_center_response` adds a two-axis/six-band matrix of nominal source
coordinate Lipschitz ceilings, using the existing scalar response calculus.
Columns are bass/mid/treble and their attenuated variants; other inputs remain
fixed. Expressions preserve signed source formulas, while gain ceilings are
absolute. Init snapshots and persistent state stay distinct from current bands.

The NDC centre mapping `(2*x-1,1-2*y)` converts each band column to twice its
Euclidean norm. This is not physical pixels or movement per second. Optional
declared domains supply independent x/y value enclosures; twice their box
diameter bounds two possible centres. Neither simultaneous reachability nor a
temporal path is asserted. Native projection/casts, clipping, visibility,
changing time/state/other controls and feedback remain separate.

Nine numerical controls cover affine gains, nonlinear declared bass bounds,
independent pairs, init/current input separation, unknown state, discontinuity,
known overflow and disconnected-band zero. A reviewer found outward rounding
could overflow after the pre-round finiteness check. The exact authored
expression regression failed before repair by breaking the whole JSON report.
The shared norm helper now checks both before and after `nextafter`, keeping
unrepresentable ceilings null. Interrupted run evidence is preserved at
`build/preset-corpus/source-shape-audio-motion-before-overflow-fix-2026-10-10/`;
only the repaired model is credited.

The focused motion/area/trajectory/vertex controls pass 71 tests. Final suite,
100 control exports and a compact fixed-2,000 census are recorded in
`checkpoint.json` when complete. The census stores only centre-response records,
source IDs and work counters rather than duplicating full multi-gigabyte exports.
It reuses exact saved compiler proofs and the source34 parser. No shaders,
equations, audio simulations or images execute, and no authored presets or AAR
changes are made.

Final qualification passes 3,151 tests plus 92 subtests in 213.16 seconds;
independent final review passes 48 focused controls. All 100 controls retain
structured/schema-valid output. The identical fixed 2,000 census finishes in
260.39 seconds with all reports structured. 1,220 contain shape response records;
73 have at least one positive per-band centre response ceiling, increasing to
97 under declared domains. 650 have a conditional two-state centre-distance
enclosure, including stationary/zero cases. These figures are partial element
coverage, not whole-preset movement or visible-response accuracy.
