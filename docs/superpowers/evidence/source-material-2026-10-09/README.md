# Source shape-material checkpoint

`source_material.py` exports centre/perimeter/border vertexRGBA, source values and
channel programs, native integer style flags, gradient/blend context and unresolved
texture requests. It reuses the qualified primitives.colour_modulo function;
no frames, images, audio or equation/shader programs are executed. Constant folding
and colour conversion operate only on source literals.

Centre and perimeter RGBA interpolate through the polygon triangle fan; border
colour is separate. Partial/dynamic channels remain null. Modulo conversion is
float32 Euclidean256/255 before texture/blend/storage, not simple saturation.
It can wrap negatives positive or exceed1slightly. final_palette_verified=false
and visible_colour_contribution=null preserve downstream/material uncertainty.

Blend flags use defined int32 truncation/nonzero tests. A numeric style.9 is0,
not a truthyflag. Border enabling compares raw double source alpha to the float32
literal.0001f, exported as border_enable_threshold. Thus equation.0001 is enabled,
configured float32.0001 equal is disabled, and negative alpha stays border-disabled
even when colour wrapping produces positive vertex alpha.

Texture roles distinguish untextured gradient, namedimage request, previousmain
fallback and unresolvedstyle. Actual asset hash/binding remains null/false.
Named lookup can fail; texturezoom/angle source values/programs are retained.
Native/authored history/context still matters. Additional audio routes cover
perimeter/border colour, perimeteropacity and texturecontrols; known untextured
texture and disabledborderRGB paths do not masquerade as live responses.

Native references: source31 CustomShape.cpp95–124/201–215/228–289/393–451,
Renderer/Color.hpp135–149. Original MilkDrop2.25c milkdropfs.cpp2371–2420 has the
same fan/sourcealpha blending with packedbytecolour conversion; that older packing
is not substituted for the current qualified floatmodulo policy. No engine patch
or newly alleged AAR bug is involved.

216 focused appearance/family/export controls pass. Independent final material
review ran124appearance tests with no findings. StrictMkDocs and whitespace checks
pass. Final prepared full suite:2180tests and92subtests pass in131.06seconds. This
is source-data correctness, not finalpalette/image or reconstruction certification.

Fixed100 census:100computed,53presets with125shape materials;35presets/64shapes
have known centre and edgeRGB. There are zero namedimage requests in this sample,
so synthetic controls—not this census—cover that route. Sum elapsed28.764474seconds,
mean.28764474seconds. Exact source/model identities and compact material records
are in census.json; rawprograms remain in the paired batch and are bound by hashes.
No whole-pack coverage or mood/image accuracy percentage follows from this sample.

Raw batch:
build/preset-corpus/source-material-2026-10-09/batch-000001.zip
SHA25603c2ed8590b7d170874b2ce8635a628a1020fb15f6358396123c02eb7d0ba8f0.
The full published2.3.33AAR/byte-equivalent31source remains the reference; no device,
shared corpus or fresh runtime capture was operated. Existing47numeric output is unchanged.

Recognizable approximation from JSON remains unverified. Feedback transfer,
finalshader material/palette effects and visible contribution/motion still need
work before the requested notification gate is satisfied.
