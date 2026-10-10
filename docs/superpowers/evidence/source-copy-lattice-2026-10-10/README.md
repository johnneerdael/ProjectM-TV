# Affine repeat-coordinate preimages

`copy_lattice` derives periodic coordinate preimages from existing supported
sampling inverses. For a repeat lookup M*u+b, a source feature s has candidate
positions inv(M)*(s+n-b), where n is an integer pair. Inverse columns generate
the lattice; fundamental area is1/absdetM and reciprocal density isabsdetM.
This is coordinate geometry, not a visible feature count or scene certificate.
The primary [OpenGL ES wrap reference](https://raw.githubusercontent.com/KhronosGroup/OpenGL-Refpages/main/es3.0/glTexParameter.xml)
describes repeat-coordinate behavior. The existing pinned-native sampler
policy and matrix extraction supply target wrap/basis semantics.

Clamp sampling supplies no periodic lattice. Missing wrap context stays
conditional, preserving its predicate. Singular/mixed/nonfinite maps remain
unknown. Native mesh-before-shader UV is retained, so shader-basis inverses
are not physical-screen inverses. Masks, filter/LOD, colour coefficients,
source content/history and feedback can hide/change recognizable copies.

Fixed affine time offsets supply exact nominal origin velocity -Minv*b'.
Other known offset-rate bounds use the componentwise triangle bound
norm(abs(Minv)*[Dx,Dy]). Missing input rates retain unknown speed. Positive
product underflow and nonfinite results do not create a stationary estimate.
Actual visible copies and motion remain null, and no mood is inferred.

Fourteen controls cover scale, reflection, shear/preimage reconstruction,
clamp, singular/mixed warp bases, native mesh ordering, affine/oscillating/
audio offsets, conditional wrap, nonfinite/underflow and dead alpha samples.
Eleven tests failed before the descriptor existed; the underflow regression
also failed before its guard. Producer focused176tests pass; independent
review passed33lattice/sampling tests and found no actionable issue.

The unchanged100source sample supplies322lattice sites across79presets:
254sites across63presets have declared repeat wrapping;68sites across43
presets are conditional on wrapping. These groups overlap. Only one sample
preset/site has density>1; the other maps often have unit density. Thus broad
extraction does not imply broad visible tiling or a repeated-layer count.
167sites across73presets have known origin-rate estimates; only one has a
nonzero origin speed. Native mesh motion and other stages remain separate.

All100exports succeed with exact source byte/hash joins and ZIP CRC. Their
preset-operation times total35.03seconds, maximum1.74seconds on this host;
sample timing is not a corpus/hardware guarantee. No time/audio/frame samples,
shader/equation execution or captured image was used. `census.json` records
exact sites, conditional statuses and source/parser/model/engine identity.

Raw paired archive:
`build/preset-corpus/source-copy-lattice-2026-10-10/batch-000001.zip`
SHA256 `7a8f2a7532d1f36d6ce704f9ffaf701957c95e825bee3098b82eba776906aefa`.
Source34is the explicit matching-source adapter for observed latest2.3.36
full AAR bytes; published-AAR runtime qualification is pending independently.
No native engine, authored preset, shared device or full corpus was changed.

Final prepared suite: **2,555tests and92subtests pass in142.85seconds**.
Strict MkDocs and whitespace checks pass. These are source-rule checks,
not whole-preset appearance/motion or mood accuracy.
