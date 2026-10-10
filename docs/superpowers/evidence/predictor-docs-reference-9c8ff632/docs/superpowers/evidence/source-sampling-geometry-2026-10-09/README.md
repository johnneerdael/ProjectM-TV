# Static texture sampling geometry

`source_sampling.py` separates supported two-dimensional texture lookups into a
constant 2-by-4 matrix over native UV columns plus spatially uniform offset
programs. It exports offset audio routes/time curves and, for a single invertible
basis, inverse feature placement, handedness and local feature-area ratio.
This is nominal source algebra, not GPU execution, a scene graph, final screen
motion or an appearance certificate. Native/unknown stage maps stay null.

Warp mesh xy and original zw remain distinct; composite aliases both to xy.
Reference: source31 MilkdropShader.cpp573–580, original MilkDrop2.25c
vis_milk2/plugin.cpp3486–3491 and the creator's
[authoring guide](https://www.geisswerks.com/milkdrop/milkdrop_preset_authoring.html),
warp/composite and texture sampling sections. The guide distinguishes distorted
warp coordinates from original UV, and explains wrap/clamp outcomes. Iñigo
Quilez's articles could not be fetched (HTTP403); no mathematical rule here is
attributed to unseen material. The target remains patched source31 and the full
published2.3.33 AAR, not an unpatched library.

For lookup `s=M*p+b`, an isolated feature at s appears locally at
`p=M^-1*s-M^-1*b`. Thus `(uv-.5)*2+.5` yields half-width features around the
centre, with area ratio .25 in the coordinate basis. This does not determine
visible repeated-copy counts: sampling wrap/filter, masks/weights, clipping,
source content, mesh, history and later stages matter. Mixed bases and singular
maps retain known coefficients but do not invent an inverse. Spatial int casts,
dynamic scales, nonlinear operations, image offsets and interpolated vertex
colour offsets abstain.

16 sampling controls pass, including independent inverse point checks, negative
orientation, shear, basis distinction, audio/time offsets and unsupported maps.
The combined focused suite passes252 tests; strict MkDocs and whitespace checks
pass. The complete prepared analyzer suite passes2216tests and92subtests in
133.12seconds. Independent correctness review has no findings and independently
re-ran all16sampling controls; basis/type/guard and conditional-inverse scope
were checked.

Fixed100 originals:100computed,1146 live RGB sample sites,676supported maps,
666invertible maps.89presets have a supported/invertible map;61have a
nonidentity map (436such maps). There are no repeated stage/site/sampler keys.
One preset has supported offset audio routes and one has nonconstant offset time
curves.422sites have unsupported nonlinear/dynamic forms and48are not2D;
one mixed-basis map has no single-basis inverse. Sum per-preset time30.690844s,
mean.30690844s. These counts establish extraction coverage, not wholepack or
reconstruction accuracy. Frozen records/source/model hashes are in census.json.

Raw source/JSON batch:
`build/preset-corpus/source-sampling-geometry-2026-10-09/batch-000001.zip`

SHA256: `457fb1c4beaa45553424bd150152fa34819eff1cb75e760c52eaa68acf5b4862`.
ZIP CRC and all100 original source bytes/hashes were verified. No preset, native
engine, device or shared corpus was changed. No image, shader or equation
execution fed these descriptions. Existing47 numeric export is unchanged; the
requested independently recognizable-look milestone remains unmet.
