# I25 / I30 retained colour precision — source-only owner packet

**Open: no production controls or screenshots have run. Native appearance and producer qualification remain required.** Retain the existing float colour/fraction/alpha policy. No source patch or global quantization change is proposed. No canonical source, existing helper, git, build, GPU or device was changed or operated.

## Exact source boundary

Original MilkDrop2 `milkdropfs.cpp:2388–2397` (shape fill),2445–2450 (shape border) and2699–2703 (custom wave) packs equation channels by multiplying the double channel by255, casting to int (truncation toward zero), masking with255, then placing the byte in ARGB. Alpha also multiplies the current float alpha_mult before the cast. This packet isolates alpha_mult1 and finite channels in[0,1], safely within the integer range. It does not model undefined/nonfinite conversions, out-of-range wrapping or original geometry-blended transitions.

The original display macro at line41 casts the already-produced diffuse component times255 to int. Legacy echo/gamma/tint products at4204,4228,4256 and shader-composite per-vertex col at4472 pass float values into that macro. Quantization happens before GPU interpolation and blending, independently of the final framebuffer format. Current target storage being RGBA8 does not make the two producer policies equivalent.

Both original2.25c and `milkdrop2/src/vis_milk2/milkdropfs.cpp` are byte-identical (SHA25668749d31bb6b3020ca89b1e7630fd704e58a5de8dd6275c9f5ea005c6586a7d9). Source arithmetic is not a Windows/D3D rasterization result.

## Current producers and retained scope

- CustomShape.cpp center/edge fill converts evaluated channels to float and applies Color::Modulo. The period is256/255; fractional values survive, with normal float/fmod roundoff. Borders use raw float channels in both authored lines and Native line batches. Do not replace this with a byte cast or infer that every shape channel has an unrestricted HDR domain.
- CustomWaveform.cpp builds per-point float colours through Color::Modulo, then preserves the existing colour/geometry smoothing and prepared replay. Native dot alpha scaling and line styles occur afterward. This precision packet changes no window, point count, smoothing, dot-density or one-evaluation policy.
- VideoEcho.cpp writes float mix*tint and gamma*mix*tint colours; gamma-only writes gamma*tint. Preserve white tint when fShader0, gamma-only.001 versus echo.0001 epsilon, signed echo orientation, pass/blend behavior and all prior repairs.
- FinalComposite.cpp forms float corner shades, then bilinearly computes each grid vertex's float colour. MilkdropShader exposes interpolated diffuse RGB as hue_shader. Keep these float attributes, original Native mesh/cache controls and shader HDR/fractional signals.

Raw Color storage and raw shape borders can retain values above1; `i25-shape-border-hdr-current-probe.milk` deliberately exercises raw border r1.25. This is an attribute-policy probe, not proof of an HDR framebuffer/display. Fill/custom-wave modulo and later framebuffer/clipping rules remain distinct.

Defaults are avoided in comparison fixtures: all enabled producer RGBA/style fields are explicit. Current shape defaults are enabledfalse, center red/alpha1, edge green/alpha0, border white/alpha0; custom wave defaults enabledfalse and RGBA1; PresetState gamma defaults2 and fShader0. Fixtures explicitly set gamma1/tint0/echo0 except the named display probes.

## Independent finite quantization oracle

`packing_oracle.py` is a small independent source-arithmetic oracle, not a renderer. Geometry uses double channel arithmetic; display first rounds diffuse and its255 product to float32. Both then truncate and mask, within the admitted unit interval. It does not call production Color::Modulo or predict final PNG values.

Known source coefficients:

| Requested channel | Original byte | Normalized original coefficient |
|---|---:|---:|
| .5 | 127 | 127/255 |
| .123456 | 31 | 31/255 |
| .003 alpha | 0 | 0 |
| .75 display gain | 191 | 191/255 |
| .9 display gain | 229 | 229/255 |
| 0 / 1 | 0 / 255 | 0 / 1 |

`fixture-ledger.json` records the independent coefficients and explicit decimal literals. File settings contain decimal numbers, not strings such as127/255 that the native numeric-prefix parser would read as127. Exact byte-fraction and0/1 boundaries belong to producer controls; small float/fmod differences are not silently called bit-identical.

`quantization_controls.cpp` is prepared, uncompiled source checking the actual copied Color::Modulo/raw Color APIs against independent bounded byte formulas. `source/` contains byte-identical source snapshots. These controls have not been compiled or executed, so no pass result is claimed.

## Actual screenshot siblings

The six I25 pairs are named `i25-CASE-float-current.milk` and `i25-CASE-byte-source-oracle.milk`:

| CASE | Producer isolated |
|---|---|
| shape-flat | uniform center/edge RGBA(.5,.123456,.75,.123456) |
| shape-gradient | different center/edge colours, each quantized before interpolation |
| shape-border | transparent fill; raw fractional border colour/alpha |
| shape-subbyte-alpha | white filled shape, alpha.003 versus original0 |
| wave-line | finite two-point line, positions/colours overwritten explicitly |
| wave-dots | same finite point programs with the unchanged current dot policy |

Oracle siblings change only the declared RGBA coefficients to their source byte fractions; geometry, styles and Native replay remain common. They represent quantized producer inputs on the current renderer, not original D3D pixels. Final PNG equality is possible after coverage, blending or storage and must be reported honestly.

I30 `gamma-0p75` and `gamma-0p9` each have float-current and byte-source-oracle siblings. They use version100, echo0, tint0 and a large opaque white shape to provide a nonzero uniform input. Both coefficients remain below1, preserving the one-pass gamma-only path. Current gains are.75/.9; source oracles explicitly use191/255 and229/255. Rad3/sides4 is finite and is intended to cover the viewport; the parent must verify the actual source field and coverage before interpreting display pixels.

`i30-echo-half-float-current.milk` exercises actual legacy echo with alpha.5, zoom1, orientation0, gamma1 and white tint/input. Original source packs both base weights to127/255; current keeps.5 each. Changing echo alpha alone cannot express both packed weights, because its unquantized weights always sum to1. `i30-echo-half-uniform-gain-oracle.milk` instead disables echo and uses one gamma pass254/255: a clearly labelled **uniform-white final-gain surrogate** for two original127-byte contributions. It is not an original per-pass/interpolation/feedback or cost oracle. Do not compare its timing with the echo fixture or generalize it to nonuniform textures, echo zoom/flip, gamma redraws or tinted corners.

`i30-composite-actual-hue-probe.milk` uses a version201 composite shader `ret=hue_shader`, so the actual float grid colour producer contributes to the image. Its fShader0 does not make shader-composite hue white; original/current shader paths compute hue independently of the legacy fShader amount.

No fake fragment-floor sibling is provided for that probe. Original shader colour packing occurs **after** float bilinear shade construction at each mesh vertex and **before** GPU interpolation. Quantizing corner shades first, or flooring interpolated hue_shader in the fragment shader, is a different operation. A valid original-byte grid oracle requires the parent's frozen per-vertex colour/position/index capture, quantization of each completed vertex colour, and replay on the same qualified grid. Root-owned composite-oracle rendering remains pending.

Endpoint controls are `i25-shape-endpoint-control.milk` and `i30-gamma-one-endpoint-control.milk`. All fixtures remain unparsed/uncompiled/unrendered in this owner preparation.

## Exact stock witnesses, without an affected census

Three unchanged originals are copied under `originals/`; their byte hashes match the handoff inventory (`stock-witnesses.json`). No stock executable or renderer run occurred.

- Royal Mashup114: the cited wave3 g.3/b.1 fields are overwritten by per-point r=t4,g=t5,b=t6 at487–489; alpha is replaced/gated at481–484. Frame code computes these colours from time-dependent sine values. The literal fields alone are not an emitted-colour witness. PSVERSION_COMP2 selects shader composition, so header gamma.16/echo.5 do not establish an active legacy diffuse path. Its comp body does not read hue_shader in the inspected code.
- 39.milk: PSVERSION_COMP0 selects legacy display; fShader0 gives white tint; echo alpha.5 is not overwritten by the inspected frame code. The two packed-half versus floating-half contributions are source-relevant. Enabled textured shape0 has center RGBA(.3,.8,1,.08), edge(0,.5,1,0), no border, and dynamic custom-wave colours also exist. Texture contents, emitted point alpha, coverage and final effect remain unverified.
- va ultramix -05_2.milk: no version header means the current preset-version default100 selects legacy display. Gamma.9, echo0 and tint0 have no inspected frame overwrite, giving a stronger gamma-only source witness. Its enabled shapes have off-screen static positions, so their literal fractions are not asserted visible. The preset's full equations, input/feedback and final image still require qualification.

The handoff5347/155 lexical candidate inventories are not an affected census and are not re-certified here. No new frequency, whole-corpus fidelity or visual-impact claim follows from these selected source traces.

## Parent qualification and status

Freeze source/ordered patches, actual APK/AAR/ABI/backend, all fixture/original bytes, matched PCM transport/effective hashes, frame/time/FPS/progress, entropy and context generation. Start matched256x144 authored/output, mesh48x32, Native Standard, no transitions/detail/diffusion. Exercise shapes and waves independently. Capture actual producer RGBA before interpolation/blending, applied styles/pass counts and the verified final-output read target; decode RGB lossless images and retain raw/hash evidence.

Repeat Native Standard4K separately, recording actual authored/reference/output sizes. Check retained alpha/fraction/HDR attribute behavior and unchanged past topology/style/replay fixes. Freeze actual hue offsets/grid colours for the composite probe; a seed label alone is not proof that independently constructed hue states match.

Source identities and prepared artifact hashes are local to this packet. Native identities/images and actual producer controls remain parent-owned acceptance gates. **I25 and I30 stay open retained-policy proposals; this packet does not complete either review.**

Parent executed the bounded actual Color API scalar controls against current production headers; they pass (`quantization-controls.txt`). This qualifies the bounded arithmetic and Color storage only; actual shape/wave/display/grid producer capture and Native images remain pending. The first direct compile omitted the parent libprojectM include directory and failed; corrected compilation uses both libprojectM and Renderer plus vendored GLAD headers. No canonical engine change.

Parent Native capture stage completed48jobs on frozenac3/27patches:22finitefixtures and2unchangedstockoriginals, each2repeats. All24 selected-RGB repeat groups and384 decodedPNG hashes pass, with all480 GL/preset/cleanup invariants perjob. See native-results.json/native-identity.json/native-captures. Actual colour-producer/grid controls remain pending; I25/I30 stayOPEN. FrozenaudioDelivery prose is corrected by ../AUDIO-PROVENANCE.md.

Parent executed all actual-production CGL geometry/display/composite groups: thirteen shape/wave fixture roles qualify actualRGBA/pass/replay; gamma.75/.9/1 andecho.5 actual vertexattributes/passcounts qualify; completed actual compositevertex/indices capture and pre-interpolation byte replay passes. See production-cgl-controls.txt and production-proof. Native4K48capture roles remain separatelyidentified. Dynamicstock pre-float doublethreshold values remainuncaptured; no affected-corpus orNativeAndroidbyte-grid replay claim.
