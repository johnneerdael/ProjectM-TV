# Typed literal vector colour projection

Source appearance constant folding now projects single vector members through
existing typed parts, preserving nested swizzles, int-vector truncation and
explicit float32 conversion. Input/sample and unexpanded projections abstain;
nonfinite results and memo/depth budgets remain guarded. Discarded unknown alpha
does not block knownRGB. No effect obligations or source control are removed.

Seven authored controls precede implementation for constructor/nestedswizzles,
integer conversion, literal vector arithmetic, sample uncertainty, discarded
alpha and localnative-uniformshadow. The latter was already preserved correctly
by lexical lowering; this repairs the opaque source-colour descriptor rather
than native binding. Independent review has no findings and ran172focused
vector/appearance/uniform/wave controls, including additional rounded-zero
conversion checks. The complete prepared suite passes2322tests and92subtests
in137.22seconds. Strict MkDocs and whitespace checks pass.

Samefixed100originals:100computed,zero newconstant-RGBelements andno earlier
descriptor loss. No practicalcoverage or appearance gain is claimed for this
sample. Source/record/modelhashes and compact comparison are in census.json.
Full source/programs remain in the hash-bound pairedbatch. This is a correctness
checkpoint, not an accuracy ceiling or classification/reconstruction proof.

No native/preset changes, audio/frame/image execution, devices or sharedcorpus
were used. Qualifiedfull published2.3.33AAR/source31 remains the reference.
Existing47numeric output and overall-look/mood validation gates remain separate.

Raw paired batch: `build/preset-corpus/source-vector-colour-2026-10-10/batch-000001.zip`

SHA256: `26727efb0c5946a0b95da9a6e76a3f694abff16a2f7a1e08176f031dc09e2de3`.
ZIPCRC and all100original source bytes/hashjoins verified. Mean sourceexport
0.30589694s,sum30.589694s;no performanceclaim.
