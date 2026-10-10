# Uniform affine feedback transport envelopes

The source descriptor now connects supported control envelopes to per-step
feedback scaling. In aspect-corrected coordinates, the inverse uniform affine
sampling matrix is z*diag(sx,sy)*transpose(R); singular scales are abs(z*sx),
abs(z*sy), area abs(z*z*sx*sy), and reflection parity sign(sx*sy). This is the
affine component, not the procedural-warp Jacobian, screen-space geometry or
visible speed. Native zoomexp must convert to1; nonzero sign-definite finite
native zoom/stretch endpoints and finite reciprocals are required.

Source order follows current source34 PerPixelMesh.cpp, native warp vertex
shader and original MilkDrop2.25c milkdropfs.cpp lines1870–1929. The creator's
[authoring guide](https://www.geisswerks.com/milkdrop/milkdrop_preset_authoring.html)
explains static zoom as repeated per-frame image movement. The target preserves
patched native semantics and aspect-corrected coordinates, not an upstream
renderer or physical-screen certificate.

All ten control rows retain independent source domains, rates and continuity,
even if aggregate transport is unknown. Uniformity requires pure scalar
operations and readonly frame/configuration inputs. Per-vertex spatial/state,
random/memory and opaque inputs cannot prove one affine transform. Review found
a dependency-free rand hole and a retained-row false uniformity flag; failing
controls were added before both fixes. Per-frame random expressions also
abstain pending explicit phase provenance. Exact binary-rational endpoint
products are outward-rounded for serialized bounds; independently bounded
correlated controls may produce conservative ranges.

Fifteen focused controls cover varying time/audio zoom, expansion/contraction,
negative stretch/reflection, zero crossings, spatial/state/random controls,
radial zoom, underflow/overflow, disconnected mesh, neutral float32 conversion
and independent row retention. Independent final review passed34transport/
recipe controls and found no remaining actionable issue.

The same100source presets all export with exact original-byte/hash joins and
ZIP CRC.25have bounded uniform affine components, including4with varying
controls;70remain unknown and5disconnected. Per-axis counts: X12expansion,
6contraction,6neutral,1neutral-crossing; Y12expansion,4contraction,8neutral,
1neutral-crossing. This is component coverage, not complete recipe or mood
accuracy. Compared with the earlier9complete uniform recipes, the aggregate
claims differ; do not present25as whole-map reconstruction coverage.

Preset-operation time totals35.51621seconds, maximum1.733351seconds on this
host. No rendered frame, audio/time sample, shader or equation execution was
used. Sample timings are not whole-corpus/hardware guarantees. `census.json`
preserves exact names/hashes, all rows and aggregate unknown reasons; these
reasons overlap across controls. No source preset, native library or shared
device was changed; the numerical47-field export remains separate.

Raw paired archive: `build/preset-corpus/source-warp-transport-2026-10-10/batch-000001.zip`.
SHA256 `4c73ee0fb4740f04a5aaf125e4d13dcb1df59d05c93068903c65b10ed3e049db`.
Reader SHA256 `754e4f4129db585cb4f7d5bee915d6bb24ac10ab25901ee7ef0832ce50744afc`.
Matching source34targets latest published2.3.36fullAAR bytes; published-runtime
qualification remains independently pending. Whole-preset visual movement,
flashing, feedback evolution and mood accuracy remain unresolved work.

Final prepared suite: **2,589tests and92subtests pass in145.54seconds**.
Strict MkDocs and whitespace checks pass. These are interpretation-rule
checks, not whole-preset visual or mood accuracy.
