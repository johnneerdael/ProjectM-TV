# Nominal shape fill contribution

The source-only appearance export now joins known custom-shape geometry and
materials in `elements[].fill_contribution`. It integrates alpha and the
incoming source-alpha-weighted RGB over the unclipped regular polygon fan.
This provides conditional contribution coefficients without frame simulation.

Each triangle has one centre and two equal perimeter RGBA vertices. The mean
alpha is `(a0+2*a1)/3`; the mean RGB times alpha is
`((a0+a1)*C+(a0+3*a1)*P)/6`. The second expression follows barycentric second
moments and includes colour/alpha covariance. Multiplying average colour by
average alpha gives a wrong result even for an ordinary fading gradient.

Multiply these means by the existing per-aspect polygon-area coefficient.
Instance sums count overlap repeatedly. Textured fills, unknown/out-of-domain
alpha and individual unknown RGB channels abstain. Dynamic radius can retain
known material means while area integrals stay null. Borders are excluded.
There is no displayed-colour, clipping, union coverage, final prominence or
automatic mood claim; `visible_screen_contribution` remains null.

The same fixed 100 originals all export successfully. Of 53 presets containing
125 shape elements, 25 presets gain known mean alpha, 12 gain known alpha-area
coefficients (17 shape elements), and seven gain complete RGB-area coefficients
(10 shape elements). These groups overlap and measure ingredient coverage.
The compact `census.json` records the exact preset hashes, per-shape values,
unknowns, parser/model identities and unchanged source-byte joins.

Eleven test-first controls include known opaque/fading fills, independent
polynomial triangle integration, instance sums, partial channels, texture
uncertainty, dynamic radius/alpha, border separation and out-of-domain alpha.
The focused producer and independent review each passed 155 controls.
The final prepared full suite passed 2,363 tests and 92 subtests in 144.56 seconds.
Strict MkDocs and whitespace checks pass. These are source-math checkpoints,
not whole-preset visual accuracy or reconstruction certification.

The raw paired batch is
`build/preset-corpus/source-shape-contribution-2026-10-10/batch-000001.zip`,
SHA256 `42449ca9ee52da19802441dfdacfa5f312e25d4bc3c16c31e022cb5da78965f5`.
ZIP CRC and all original source-byte joins match the preceding frozen export.

Native attribution: prepared source31 `CustomShape.cpp:242` supplies centre
and perimeter RGBA, `:401` selects source-alpha blend factors, and `:438`
draws the untextured triangle fan. The original MilkDrop2.25c
`vis_milk2/milkdropfs.cpp:2350–2431` uses the same fan and blend principle;
its packed 8-bit vertex conversion is not substituted for the TV engine's
established floating modulo policy. The nominal integration excludes raster
precision, storage and later composition. See the
[Khronos blend reference](https://wikis.khronos.org/opengl/Draw_Buffer_Blend)
for the source/destination blend terms.

The full published v2.3.33 AAR/source31 stay qualified and pinned. The v2.3.34
download remains pending; this addition makes no new-AAR runtime claim. No
device, captured-image classifier or duplicate numerical corpus was operated.
