# Nominal backward-sampling displacement

The source descriptor now joins uniform affine transport to per-step sampling
displacement in aspect-corrected source coordinates. With centred p=A*(u-.5),
B=R*diag(1/(z*sx),1/(z*sy)), and h=(R*diag(1/sx,1/sy)-I)*(.5-c)-d,
displacement is(B-I)*p+h. For uniform UV in[0,1]^2, nominal RMS squared is
h² + ax²*norm(col0(B-I))²/12 + ay²*norm(col1(B-I))²/12. Constant-control
coefficients and mean h need no grid/time/frame evaluation in the producer.

Varying domains use spectral-norm and triangle bounds for R*D-I and centre/
stretch/translation. Procedural warp contributes at most sqrt2*2*abs(warp)*
float32(.0035) in this basis before/after rotation. The envelope does not imply
simultaneous oscillator peaks. Texel alignment is explicitly excluded; the
consumer adds A*texelUV separately. Backward sampling is not arbitrary forward
feature motion or screen speed. Native precision, interpolation, transitions,
wrapping/clipping, content and later shaders remain separate; no mood is scored.

Native/reference order is the previously pinned source34 vertex shader /
PerPixelMesh.cpp and original MilkDrop2.25c milkdropfs.cpp1870–1929. No native
or preset source changed. Reciprocal scale validation remains active for W0.
All input domains preserve earlier uniformity/purity guards.

Independent review found a predictor cancellation bug in expanded centre
arithmetic, shared with the existing uniform warp recipe. For identity controls,
cx=1e20/dx=.03 produced mean-.53 and RMS².2809, contradicting its own.03bound;
neutral centre/dx1e-20 erased translation. Four failing controls preceded the
fix. Shared exact-fraction factored centre products/sums now preserve these
translations with finite/nonzero serialization guards. This is a nominal
predictor repair, not evidence of an AAR defect or native rounding equivalence.
None of the fixed100sample's existing recipe centre coefficients changed.

Fifteen displacement tests cover identity, fixed zoom/translation, aspect /
rotation/stretch/centre quadrature controls, time-varying and reflection bounds,
procedural contribution, domain guards and cancellation witnesses. Two further
recipe regressions cover the shared fix. Independent final review passed65
combined displacement/radial/transport/recipe tests and found no remaining
issues. Test-only source quadrature and parameter points check analytic math;
no rendered image or such samples feed the producer.

All100original source exports complete with exact byte/hash joins and ZIP CRC.
25gain displacement bounds;21have constant-control RMS recipes,15with nonzero
affine coefficients.70unknown,5disconnected. These are component counts, not
whole-preset activity/appearance accuracy. Preset-operation times total
35.181843seconds, maximum1.739468seconds; sample host timing is not a corpus/
hardware guarantee. `census.json` preserves exact names/hashes and descriptors.

Raw paired archive: `build/preset-corpus/source-warp-displacement-2026-10-10/batch-000001.zip`.
SHA256 `69e9c8b6d7ffb2a5885843a9d6baec57c12127c9ac80f8cc7e65f8df8b24204e`.
Reader SHA256 `754e4f4129db585cb4f7d5bee915d6bb24ac10ab25901ee7ef0832ce50744afc`.
Matching source34targets published2.3.36bytes; runtime qualification remains
separate/pending. No shared device/full corpus was operated. Motion intensity,
flashing, full feedback evolution and mood accuracy remain unresolved work.

Final prepared suite: **2,620tests and92subtests pass in146.89seconds**.
Strict MkDocs and whitespace checks pass. These verify interpretation rules,
not whole-preset visual or mood accuracy.
