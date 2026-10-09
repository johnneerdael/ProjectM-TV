# Direct sampled-colour coordinate response

Image-driven advection occurs in53/100fixed-source cases. This extension shares
the affine UV analyzer across native UV and explicitly substituted sample-value
bases, retaining constant2-by-4 RGBA-to-UV matrices per input sample. Constant
weighted dot products expand into scalar terms. Shader globals x/y remain
uniform offsets instead of inheriting EEL spatial-variable semantics.

The direct row-sum norm holds sampled locations fixed and treats their RGBA
values as independent. A conditional offset box sums signed coefficients under
an explicitly unverified[0,1]premise, excluding base UV and uniform offsets.
GetBlur decoding and external/HDR texture ranges are not assumed. Nested sample
locations can add nonlinear response; full sensitivity and visible motion remain
null. A pureUV map may have sample gain0 without certifying a still preset.
No source coefficient is a mood, bass response or observed-binding claim.

References: [HLSL dot](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-dot)
defines weighted vector summation. Source31 PresetShaderHeaderGlsl330.inc149–153
shows GetBlur scale/bias decoding and lum weights(.32,.49,.29), whose sum is1.10.
Original MilkDrop2.25c compiles authored shaders through D3DX. The target remains
qualified full published2.3.33AAR/source31, not an unpatched upstream library.
The source-only parser/model/profile/hash obligations remain attached to results.

12new response controls cover direct channels, positive/negative gradient reads,
nested-image-coordinate uncertainty, dynamic/nonlinear/quantized refusal,
uniform-offset namespaces, pureUV zero gain, independent perturbations and the
64sample working-memory budget. Original xtramartin warp has direct gain norm
.044 in UV/sample-component units under the declared fixed-location model.
67combined response/sampling/polar/form controls and303full focused controls
pass. Independent correctness review has no findings and re-ran67controls.
The complete prepared analyzer suite passes2267tests and92subtests in
139.31seconds. Strict MkDocs and whitespace checks pass.

Fixed100 originals:100computed,682supported affine coordinate models.676are
UV/uniform-only maps; six directly sampled-colour response maps occur in six
presets. No earlier descriptor was lost.464remain unknown:403unsupported
nonlinear/dynamic forms,48non2D coordinates and13substitution-budget cases.
Exact names/source/record/model hashes, signed matrices and compact results are
in census.json; full coordinate/offset programs stay in the hash-bound raw batch.
Mean per-preset source export.30595793s,sum30.595793s. This measures source
extraction coverage/timing, not complete appearance or wholepack fidelity.

Raw paired batch:
`build/preset-corpus/source-coordinate-response-2026-10-09/batch-000001.zip`

SHA256: `c4df1125a1a1516fa7fbbbb831db452be413148d6d77896444da1100b875bac8`.
ZIP CRC and all100 original source bytes/hash joins were verified. No preset or
engine edits, audio/frame/image execution, devices or shared corpus were used.
Existing47numeric export remains unchanged. The independently recognizable-look
and calibrated mood/preference gates remain unmet.
