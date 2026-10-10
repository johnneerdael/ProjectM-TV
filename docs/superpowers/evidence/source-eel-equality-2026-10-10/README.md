# Source EEL equality tolerance repair

Root cause: source EEL `equal` and `_equal` lowered into the same `equal` node
as shader equality, then `_number` compared values exactly. Values made known
by earlier source assignments could therefore select the wrong conditional
branch. Example: `k=.000009;x=if(equal(k,0),.2,.8)` predicted x=.8; the corrected
source model predicts x=.2, matching the evaluator's strict tolerance rule.

The EEL lowerer now emits `eel_equal`. Known finite operands fold as
`abs(a-b)<0.00001`; exactly the boundary is false. Shader `equal` keeps exact
typed semantics. Unknown/nonfinite operands are not guessed. The exported
source-control DAG keeps `eel_equal` explicit for downstream consumers. The
shader-only scalar/grid numerical backends reject it instead of pretending
to execute EEL. Threshold-presence reporting recognizes its dependency but
no exact crossing or visible flash is invented.

Reference sources:
- Prepared source34 `vendor/projectm-eval/projectm-eval/TreeFunctions.c`,
  lines433–445; COMPARE_CLOSEFACTOR at116. Its build cache uses
  `PROJECTM_EVAL_FLOAT_SIZE=8` (double).
- Original MilkDrop2.25c `ns-eel2/asm-nseel-x86-msvc.c`, line1628 onwards:
  subtract, absolute value and comparison against the close factor.
  `ns-eel-int.h` line56 defines NSEEL_CLOSEFACTOR as0.00001.
  Reference root: `/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/`.

Ten controls cover both sides of the strict boundary, authored assignment and
branch selection, shader equality, unresolved export and nonfinite operands.
Four controls failed before the fix. The producer's262focused controls pass;
independent review passed238and additionally checked `_equal` lowering and
numerical consumer rejection. No native code or preset was changed; this is
a predictor defect, not a ProjectM-TV AAR issue.

The unchanged fixed100 originals were exported under the explicit source34
reader without native equation/shader execution or frame inspection. Their
source bytes and full hashes join the preceding vertex-motion batch exactly.
`census.json` records descriptor differences, exported operator counts,
model/parser/engine identity and raw ZIP hashes. These comparisons measure
source-semantic changes, not visual or mood accuracy. New AAR runtime
qualification remains pending independently.

Final prepared suite: **2,464 tests and 92 subtests passed in141.70seconds**.
Strict MkDocs and whitespace checks pass. The source comparison changes the
explicit EEL operator semantics in24of100descriptors; it does not prove24
changed visuals. No captured images or mood-label tuning were used.
Raw ZIP SHA256:
`4beb96e899f0f46ede5f68471bab164e907e762e3e26af66df55e5fdfe3d4d28`.
