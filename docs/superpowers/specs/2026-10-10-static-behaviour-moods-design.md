# Static behaviour evidence for activity classification

Approved objective: apply the incorporated analysis machinery to flashing,
movement speed and effect prominence so source-only Chill / Normal / Intense
classification improves. Preserve the current predictor worktree and branch.

## Deliverables and architecture

Extend the existing typed source/activity description, not the frame-analysis
collection builder. Derive component motion and brightness-transition records
with explicit units, intervals, source/model/context hashes, contributing code
paths and unresolved causes. Join geometry, alpha/material and final composite
transfer to estimate how prominently a component can affect the display.

Combine these records into a versioned static behaviour prediction with a1–100
activity score/range and overlapping bands: Chill1–30, Normal25–75, Intense70–100.
Keep assumed preference weights separate from mathematical evidence. Unknown
contributors retain their possible impact; they cannot become zero. No renderer,
image classifier, optical flow or full-corps native capture is used for extraction.

Use SymPy to simplify/differentiate qualified scalar programs, Z3 to prove
predicate/range/state claims, and compiler metadata where it recovers otherwise
unqualified function/resource structure. Their native-format, phase, source and
binding guards remain authoritative. Do not substitute inspection IR semantics
for our patched ProjectM-TV target. Existing AAR-derived source readers remain
pinned. Compare equations/projection/storage rules with supplied MilkDrop2 source
and the local/official authoring guide when needed.

## Required behaviour

1. Flashing: quantify periodic/discontinuous and fast smooth brightness changes,
   contrast/opacity and spatial extent. Retain reachability, simultaneous-event,
   sampling and native-byte/modulo caveats. Reject dead/impossible branches using
   qualified domain proofs. A possible high-frequency mechanism is not a measured
   visible flash.
2. Motion: report screen-normalized geometry and transport rates, including
   constant per-feedback-step rotation/zoom/translation/stretch. FPS is explicit.
   Separate forward content motion, sampling-map displacement, deformation, audio
   partial response and temporal derivatives. Uniform content/disconnected paths
   do not inherit apparent motion simply because coordinates change.
3. Prominence: account for viewport/aspect, clipping, alpha, area/overlap and
   composition attenuation/gating. Preserve lower/upper intervals and distinct
   source contribution versus guaranteed visible contrast. Offscreen/transparent/
   disconnected components cannot drive an intense classification.
4. Scoring: consume the new evidence automatically in static exports and provide
   reasons for each band, rejected/ambiguous candidates and missing contributors.
   Preserve existing outputs/basis and keep source estimates distinct from sampled
   feature statistics and native/visual certification.
5. Validation: freeze positive/negative mathematical controls before implementation,
   source fixtures and unchanged fixed2000 cohort before measurement. Compare
   before/after quantified facts, classifications/abstentions, effect size and
   processing cost. Retain failures and exact source hashes. Include the existing
   historical human labels only as a frozen independent check, not weight fitting.

## Acceptance and completion

Completion requires all three dimensions connected to classification, actual
source-case improvements on the fixed cohort, no transparent/tiny/disconnected
false Intense or unresolved-flash false Chill in controls, consistent JSON/schema/
cache identity, prepared suite and source-only paired export verification.
Tests alone or a reporting wrapper around unknown fields cannot complete this
goal. If important behaviour/scoring remains unsupported or validation cannot
establish useful classification, keep the goal active and prioritize the frequent
root causes. Do not claim a visual-accuracy percentage without relevant evidence.

No main merge, engine patch, authored-preset edits or duplicate render corpus is
authorized by this phase. Commit/push tested increments and package engineering
AAR defects separately in Downloads if actually reproduced.
