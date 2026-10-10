# Procedural oscillatory bands and colour causality

Form/family code10 adds raw straight sine/cosine bands from a constant-affine
phase in a single native UV basis, and radial oscillations from the native
radius lane alone. The descriptor exports a signed phase-gradient normal,
nominal raw-generator spacing, phase programs and uniform phase motion/audio
controls. Formula identities are generators, not layer counts or final objects.

For sin(kx*u+ky*v+b), spacing along the phase normal is2*pi/hypot(kx,ky).
Radial spacing is2*pi/abs(kr) in native radial varying units. Unknown/mixed
bases, dynamic spatial frequencies, non-affine or image-driven phases and
unusable known domains abstain. Native radius is a supplied interpolated varying;
no exact analytic circle or final screen orientation is inferred. Masks, tint,
thresholds, products, native rounding/projection and feedback stay separate.

## Corrections and controls

A negative control exposed coordinate-only sine displacement misclassified as
a colour band. Colour-data traversal now stops at sampled textures, preserving
shared expressions also reaching RGB/masks. Exact binary-rational ranges for
constant-affine sin/cos/saturate sums prune known complete clipping and
constant-dominating min/max masks, while partial/unknown masks remain conditional.
Known singular phase offsets such as1/0, pow(0,-1)and log(0)abstain. The native
abs lowering retains sqrt(-1)as usable. Established invalid native Q-upload
envelopes remain guarded. These checks apply to existing periodic radial glows,
which had the same coordinate-only/full-clipping attribution gaps.

The independent review also found an older temporary swizzle cache bug. It was
fixed separately in43981603 before qualification; historical exports remain
preserved. See the adjacent source-nonlinear-lane-cache evidence. No native
engine, AAR, authored preset or shared device was changed.

Twenty-eight new band controls, three added glow-causality controls and one
lane-identity regression contribute to the focused288checks. Independent final
review found no remaining actionable findings. All2,777tests and92subtests
pass in159.38seconds. Strict MkDocs and whitespace checks pass.

## Exact fixed100 sample

All100 structured exports retain exact source/hash joins, paired JSON bytes
and ZIP CRC. There are no changed source-gap records, new budget failures or
changes to numeric nonlinear RGB boxes. All four previous radial-glow forms
remain valid. One raw band form is newly recognized: Zylot - The Sound plays
the Sights.milk, SHA2560249bbafb6c102809c90bfd82a92f9df620040a19b7c08360fd09d881cbfeeac,
with planar shader-UV phase gradient(10,0)and raw spacing0.6283185307179586UV.
This is limited new family coverage, not a whole-preset appearance pass.

A second uncached independent source export recomputed all100presets. Every
analysis record, including per-lane domains and hashes, matches the first run.
This is repeatability evidence after the cache repair, not visual correctness.
First run per-preset time sum39.266447seconds, maximum2.426758seconds on this
host; no hardware/corpus performance guarantee. Exact counts and hashes are
in census.json and repeat-check.json.

First raw ZIP SHA256:
3acdb9fbd48beaaadb7fc77ec8dddc2b2b90414a1aa01f41f70f41f495296495.
Repeat raw ZIP SHA256:
043c18c4967def534a51650c53a3d3742bd773b28f7fa87f59b843584259bcad.
Paths: build/preset-corpus/source-bands-2026-10-10/batch-000001.zip and
build/preset-corpus/source-bands-repeat-2026-10-10/batch-000001.zip.

Latest release rechecked as2.3.36at90b5bf9d9f60a13e9e271cc021a7d1133aa8fb3d.
Its full AAR hash matches our verified source34 artifact:
a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3.
The static producer uses its pinned patched source reader and sealed offline
compile manifest; no image/audio/time sample or equation/shader execution feeds
this source descriptor. Published-AAR numerical runtime qualification remains
separately pending. Mood and full-appearance accuracy remain unverified.

## Primary references and attribution

[The Book of Shaders shaping functions](https://thebookofshaders.com/05/)
explains spatial sine scaling and additive time phases. Spacing/gradient and
causal clipping deductions here are our nominal mathematical inference.
[Geiss preset authoring](https://www.geisswerks.com/milkdrop/milkdrop_preset_authoring.html)
provides native shader-coordinate/feedback context. Its shader sin/cos return
sentences are swapped in the inspected version; the predictor follows actual
intrinsic semantics and source, rather than copying that documentation typo.
Original MilkDrop2.25c plugin.cpp3484–3493 binds rad/ang/UV aliases;
plugin.cpp2281builds aspect-scaled vertex radii. Pinned source34
MilkdropShader.cpp570–582 binds the target aliases; FinalComposite.cpp320
normalizes the composite radius to the corner scale. These are distinct target
units/projections, not proof of cross-engine circle equality. Native4K/authored
canvas behavior is preserved; no renderer code is changed.

The narrow colour-only recognizer has limited sample prevalence. Original
source contains many oscillatory maps in per-pixel transforms and texture
coordinates, often with varying frequencies. Quantifying those maps and their
uniform audio/state controls is the next useful extension; counting them as
colour stripes would inflate coverage with false appearance implications.
