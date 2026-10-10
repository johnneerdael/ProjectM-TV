# Main-frame Q bindings in source shader analysis

The source model now binds q1..q32 to _qa.._qh scalar lanes from main-frame
source equations. Source34 PerPixelContext.cpp98–106 snapshots these values
before pixel Q writes; MilkdropShader.cpp336–344 uploads frameQVariables through
float4 uniforms. PerFrameContext.cpp167 reloads init Q snapshots before each
frame. Original MilkDrop2.25c milkdropfs.cpp493/675/4004–4007 confirms pool/copy
intent. Shader-local shadows remain local. No equation/GPU execution occurs.

Supported constants narrow after double expression evaluation. Dynamic Q stays
an explicit narrow source field, with upload role, source expression and named
input dependencies; known nonfinite uploads remain unknown, never zero-filled.
The contract is unobserved runtime binding. Audio routes preserve existing
q_bridge_expressions and native_uniform_role provenance; Q-mediated scalar gain
remains unqualified across the float32 upload boundary.

Initial integration lost Q route provenance; the existing regression caught
it and was repaired before qualification. A first fixed100run also erased the
structured description for original flexi - grind my glitch up[191] after the
shared traversal budget exhausted. Preserve that run at build/preset-corpus/
source-q-uniforms-2026-10-10 and its failed suite log. Reusing per-analysis
packed-read scans fixes repeated work without raising MAX_FIELD_VISITS250000.
The original now takes244399visits with a complete descriptor in its focused
control; its remaining budget margin is small, not a scalability guarantee.

Two earlier expectations change for verified source reasons, not by deleting
hard fixtures. Original xtramartin454has no q32assignment and multiplies its
entire warp colour by q32, whose snapshot is0; its gradient no longer contributes.
A separate explicitly labeled byte-copy test with q32=1 retains the.044gradient
response check. The original source is unchanged. Likewise, an unassigned _qa
bank is known zero; an explicitly audio-dependent Q matrix remains unresolved.
These follow native initialization/copy semantics, not arbitrary input defaults.

Eight new Q controls cover32lane mapping, post-double float32 upload, pixel
mutation, init reload, dynamic/audio provenance, overflow, local shadow and
original Grind budget preservation. Existing advection/sampling/polar controls
retain originals and separate diagnostic controls. Independent final review
passed62targeted regressions after the fixes, with no actionable findings.

Repaired100source export has exact byte/hash joins and ZIP CRC, and all100
structured descriptions remain available.91presets expose Q contracts:2272
constant lanes and640symbolic lanes. Warp colour-transfer support27→28;
composite remains9. Feedback support remains23, so this is primarily a source
provenance/correctness improvement, not a large numeric or mood coverage gain.
Census preserves exact names/hashes and nonzero/symbolic lane details. Constant
zero lanes are implicit in this compact census but complete in the raw archive.

Source-operation time totals38.512631seconds, maximum2.361235seconds on this
host; no corpus/hardware guarantee. No authored preset/native engine/shared
device/full corpus was changed. Dynamic coefficient gain, full feedback,
visible motion/flashing and mood/appearance accuracy remain unresolved work.

Raw repaired archive: `build/preset-corpus/source-q-uniforms-repaired-2026-10-10/batch-000001.zip`.
SHA25602c040fdca76bc427cf710f022d42af0f42d5c8a889c74589c9f8f90c8c0611e.
Reader SHA256754e4f4129db585cb4f7d5bee915d6bb24ac10ab25901ee7ef0832ce50744afc.
Saved compile-manifest file SHA25601e97e69283242d039ad2925e1845b41aa81a96418c758e12a086ca3a899e32f.
Matching source34targets published2.3.36bytes; runtime qualification remains
independently pending. No visual or mood accuracy is credited here.

Repaired final prepared suite: **2,688tests and92subtests pass in154.61seconds**.
Strict MkDocs and whitespace checks pass. Preserve the earlier3failure suite
and first100budget miss separately; no failure was rerolled or credited as
visual accuracy. These checks do not certify whole-preset appearance/moods.
