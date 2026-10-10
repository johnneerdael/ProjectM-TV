# Nominal native warp recipes

Fixed native controls can transform feedback on every frame even when parameter
variation is zero. The new source-only recipe retains zoom/stretch/oscillator/
rotation/translation/aspect/texel order, float32 control conversion and explicitly
supplied renderer aspect and texel offsets. It models uniform zoomexp=1 controls;
radial/dynamic/singular/nonfinite inputs remain unknown. Negative uniform zoom
follows the current signed-power policy. Affine identity and area ratio describe
only that component, never displayed motion or full nonlinear map area.

Four native warp waves expose factor and phase coefficients rather than sampled
frames. Accepted custom shaders and default/rejected legacy shaders have distinct
spatial Y signs; unresolved nonzero-warp selection remains unknown. Independent
review found that branch omission in the first implementation; three failing
regressions were added before fixing it. Final focused19controls and independent
162recipe/appearance tests pass. Nominal floating arithmetic, GPU precision,
mesh interpolation, transitions and visible feedback content remain separate.

Reference sources: source34 production-engine PerPixelMesh.cpp (controls,
rotation, factor uniforms), PresetWarpVertexShaderGlsl330.vert (operation order),
MilkdropShader.cpp and MilkdropStaticShaders.cpp.in (selected vertex branch).
Original MilkDrop2.25c vis_milk2/milkdropfs.cpp lines1870–1929 establishes intended
order and projection-Y convention. Current source recipes preserve patched target
behavior instead of replacing it with an assumed upstream renderer.

The unchanged100source sample completes with exact original-source/hash joins
and ZIP CRC. Complete recipes:6uniform affine and3uniform procedural-wave warp;
5meshes disconnected,86unknown. Six supported affine components are nonidentity.
Unknown reasons:41zoom,11rotation,9translationX,4centerX,1zoomexp not uniform;
3radial zoom exponents;17unresolved nonzero-warp branch selections. These are the
first reasons encountered per case, not exhaustive dependency-gap inventories.
No visual inspection, equation/shader execution or audio/time sampling was used.
Preset-operation time totals35.605506seconds, maximum1.731405seconds on this host;
these are sample timings, not corpus/runtime performance guarantees.

`census.json` preserves exact names, hashes, recipes, reasons and producer identity.
Raw paired archive: `build/preset-corpus/source-native-warp-2026-10-10/batch-000001.zip`.
SHA256 `8ee1dd05891e45800e88cb05f5c14b7ba1b80a6c8bad842126075d1cbc7b7bb8`.
Reader SHA256 `754e4f4129db585cb4f7d5bee915d6bb24ac10ab25901ee7ef0832ce50744afc`.
Latest published2.3.36 identity was rechecked through GitHub: full AAR SHA256
`a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3`.
The matched source34 adapter is explicit; published-runtime qualification remains
pending independently. No authored preset, native engine, shared device or full
corpus was changed. Mood and actual appearance accuracy remain unverified.

Final prepared suite: **2,574tests and92subtests pass in145.14seconds**.
Strict MkDocs and whitespace checks pass. These verify source rules, not
whole-preset appearance or calibrated mood accuracy.
