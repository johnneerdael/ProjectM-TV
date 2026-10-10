# Typed source dependency projection repair

The frozen 2,000-preset audit identified 156 presets with `component projection
exceeds type`. This was a predictor dependency-traversal defect, not evidence of
a native library bug. All authored presets, compiler proofs and engine patches
remain unchanged.

## Cause and semantics

`_project` and member traversal stripped casts before selecting lanes. A scalar
cast/assignment into `float3` therefore appeared scalar when `.g` or `.b` was read.
The repaired path applies the existing typed `ShaderFields.parts` model first:
broadcast valid lanes, truncate unconsumed lanes and retain numeric conversions.

[Microsoft's HLSL component reference](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-per-component-math)
describes component access, swizzles and first-component scalar access. Original
MilkDrop2 `plugin.cpp` lines 3598–3670 prepares the authored HLSL wrapper and
delegates language compilation to D3DX; it does not replace vector conversions
with expression-equation rules. The unchanged source34 patched translator and
GLES300 offline validator accept both the scalar-broadcast and shortened-vector
controls. No GPU or reference images are needed for this source dependency fix.

## Review findings and performance repair

Nine initial regression controls fail before repair. Review caught a false
positive in the first repair: a full-width `float2` swizzle still followed a
discarded third lane in the cast's source vector. Full-width converted projection
and traversal now respect typed parts, including normalization after truncation.
Integer/boolean and float32 upload nodes are retained. Explicit scalar casts
consume the first source lane without rebuilding an endless scalar-cast chain.
Opaque matrix/cross-lane and loop paths retain their earlier dependencies.

The accurate traversal then exposed budget regressions in the exact pool profiles
for Grind 237 and 342. A source237 diagnostic attributed 138,356 visits to nested
multiplier-subtree searches. A per-subtree cache was insufficient. The final
condition lookup collects one budget-charged causal DAG per output, retains
strong node identities, and computes descendants of unknown multipliers once.
Shared masked/unmasked paths retain the prior existential condition. No partial
facts are cached after failure. Calls outside an analysis cache use the original
identity traversal, closing a separate review control.

The post-repair diagnostic for 237 records 161,307 field visits and no budget
failure; this is one profile, not a universal headroom claim. Both 237 and 342
retain their structured descriptions without raising the 250,000-visit limit.

## Qualification

- 23 new projection/mask controls; 122 focused controls pass.
- Independent final review passes 116 checks including Grind 191/237/342.
- Exact 156-case recheck: projection gaps **156→0**, no new source gaps and no
  lost structured descriptions. All 156 records validate the JSON Schema.
- Original 100 controls: all remain structured/schema-valid, with unchanged
  preset hashes and no new source interpretation gaps.
- Full prepared analyzer suite: **3,090 tests plus 92 subtests pass** in 175.77
  seconds. Strict MkDocs and diff whitespace checks pass.

Full source hashes and per-case before/after dispositions are in `comparison.json`.
The frozen 2,000-case baseline stays immutable. This focused recheck does not
relabel the whole pool as a new measured checkpoint and does not supply visual
or mood accuracy. Restored effect dependencies support colour/movement/flashing
analysis, but visible intensity and full feedback evolution remain separate.

Local artifacts:

- `build/preset-corpus/source-projection-casts-red.log`
- `build/preset-corpus/source-projection-casts-complete-shortening-red.log`
- `build/preset-corpus/source-projection-casts-budget-red.log`
- `build/preset-corpus/source-projection-casts-2026-10-10/final-results-run/`
- `build/preset-corpus/source-projection-casts-final-controls-100-2026-10-10/`
- `build/preset-corpus/source-projection-casts-final-suite.log`
- `build/preset-corpus/source-projection-casts-budget-2026-10-10/profile.json`
- `build/preset-corpus/source-projection-casts-budget-2026-10-10/profile-mask-flow.json`

Earlier incomplete/failed repair snapshots are preserved and receive no pass
credit. No duplicate full-corpus render or new AAR/runtime qualification was run.
