# Raw texture-colour mixture checkpoint

source_colour_mix.py adds per-stage nominal affine RGB transfer models using
shared bounded sample substitution and affine math. Each direct sample keeps a
3x4RGBA-to-RGB matrix, site identity, coordinate program and sampler policy.
Native UV gradients and uniform offset programs remain separate. Constant-weight
signed row sums bound direct sample sensitivity with locations held fixed; actual
palette, whole-loop sensitivity, sharpness and persistence remain unverified.

This shares substitution with source_advection.py, preserving opaque sample
values, node/site identity and64sample/4096node budgets. _affine_basis_map now
accepts3output rows while its existing2coordinate-row contract remains default.
Warp-only source vertex colour resolves known consumed lanes; dynamic decay
keeps RGB unknown and alpha1known. Composite hue inputs are never replaced.
Unsupported nonlinear, dynamic-scale and quantized sample colour abstains.

Mixture labels describe all participating coefficient signs, not filter efficacy.
Signed main/blur means main and blur exist with some negative sample weight,
including any other participating texture. Nonnegative main/blur has all sample
weights nonnegative; other mixtures retain a genericlabel. Matching kernels,
history/coordinates, decode ranges, clipping/storage and laterpasses are needed
before interpreting a mixture as spatial sharpening or softening. Cancellation
across different sites does not establish an inactive preset.

13new colour controls pass;87combined colour/uniform/advection/sampling/polar/
form controls pass independently. Tests cover sourcebias, BGRcolumns, uniform
programoffsets, directnorms, dynamic/nonlinear/quantized abstention, nested input
coordinates and vertex-context guards. Original FlexiHueBurst has an affine warp
mix involving main, blur1/blur3 and noise; its nonlinear composite remainsunknown.
The existing main-only feedback-transfer and47numeric exports remain unchanged.
Independent correctness review has no findings. The complete prepared suite
passes2287tests and92subtests in136.88seconds. Strict MkDocs and whitespace
checks pass.

Final fixed100 originals:100computed,36supported stage models across35presets;
164stages retain unknown. Fourteen signed main/blur mixtures,one nonnegative
main/blur mixture and21other models are described. No earlier descriptor was
lost. These are source-model coverage figures, not overall-look or wholepack
accuracy. Mean per-preset source export.31132476s,sum31.132476s; no performance
improvement is claimed from a single timing checkpoint.

Compact source/record/model hashes, numeric matrices and mixtures are in
census.json. Full programs/routes remain in the raw paired batch:
`build/preset-corpus/source-colour-mix-2026-10-09/batch-000001.zip`

SHA256: `356d14a0c5d8de6af0035f190f514e3581caabfca88c771a4bc6f8632f2a4235`.
ZIP CRC and all100 original source bytes/hash joins were verified. No audio/frame/
image execution, devices, shared corpus, engine or preset edits were used. The
reference remains qualified full published2.3.33AAR/source31. Final palettes,
perceived activity, mood fit and independently recognizable reconstruction remain
unverified; the requested notification gate is not yet met.
