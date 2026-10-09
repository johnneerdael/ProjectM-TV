# Typed source timing and literal arithmetic

This change resolves nominal affine-time phases selected from constructed
vectors, nested swizzles and supported componentwise arithmetic. A shader using
`float2(time*2+.25,bass).x` now supplies a two-radians-per-second phase;
the unrelated bass component does not hide it. The palette control predicts a
pi-second cycle without executing equations, shaders or frames.

Review exposed related pre-existing constant-domain defects. A failed float32
narrowing could fall back to its original finite double value, an overflowing
uniform conversion could throw out of source analysis, and shader arithmetic
could falsely cancel overflowing values and remove a feedback dependency.
Regression controls precede each repair. Explicit scalar source casts remain
typed, and authored float arithmetic, compound updates and increments carry
`numeric_domain=shader-float32`. Literal folding preserves that domain while
untagged EEL arithmetic stays double-valued. Nonfinite conversions stay unknown.
Runtime field evaluation and native code are not patched by this change.

Independent review found no remaining necessary issue and passed 276 focused
controls. The producer's broader focused set passed 284 controls after exporting
the arithmetic-domain and explicit-cast metadata; the additive export review
passed 187 focused controls. The final prepared full suite passed 2,352 tests
and 92 subtests in 144.52 seconds.
Strict MkDocs and whitespace checks pass.

The same fixed 100 originals all produce exports. No new timing coverage is
claimed. Two descriptors receive small target-constant corrections: Rovastar's
Blue Shining offset and goody's woven beads transfer gain. Two radial-grid IDs
also change because their typed expression identity now includes arithmetic
domain metadata; their geometry parameters do not change. The metadata changes
90 complete descriptors. No previously known
timing field becomes unknown. See `census.json` for source/model/parser hashes,
the exact changed fields and source-byte joins. This is ingredient coverage and
source-math validation, not whole-preset appearance or mood accuracy.

The raw paired batch is
`build/preset-corpus/source-vector-time-export-2026-10-10/batch-000001.zip`,
SHA256 `ac936fee16de87300d239ce1273874f2b07ab09e834978c3a62a2b094f61976d`.
ZIP CRC and all original source bytes match the preceding frozen batch.

References: [HLSL component math and swizzles](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-per-component-math),
the prepared source31 `vendor/hlslparser/src/GLSLGenerator.cpp`, and original
MilkDrop2.25c `vis_milk2/plugin.cpp:3351` (shader profile selection and original
shader compilation path). These establish source-language context; no new
MilkDrop2 runtime comparison or GPU rounding/optimization proof is claimed.

The qualified full published v2.3.33 AAR/source31 remain pinned. The v2.3.34
artifact acquisition is pending; this change does not relabel prior AAR evidence.
No device, captured-image classifier or duplicate numerical corpus run was used.
