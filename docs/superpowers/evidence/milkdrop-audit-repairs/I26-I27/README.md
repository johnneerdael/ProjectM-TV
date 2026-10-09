# I26/I27 retained shader-input policy — owner packet

Source preparation only. Retain current corrected inputs; no shipping rollback, compatibility mode or engine patch is proposed. No builds, GPU/device operations, canonical/helper or Git edits occurred. Native producer/program/output evidence remains the parent's open gate. None of the new presets was parsed, compiled or rendered here.

## Source boundaries and retained policies

**I26:** original MilkDrop2 milkdropfs.cpp3970–3971 constructs shader volume using `.3333f*(bass,mid,treb)`. C++ comma semantics discard bass/mid and use the treble operand; the attenuated tuple has the same defect. Current PCM::GetFrameAudioData computes `(bass+mid+treb)*.333f` and the attenuated equivalent. MilkdropShader::LoadVariables binds those immutable audioData fields, not mutable EEL variables. Both the corrected mean and height-derived mip values are already present in pinned upstream [PCM.cpp](https://raw.githubusercontent.com/projectM-visualizer/projectm/6f64807467e312034883a4389e6aa80a675458bc/src/libprojectM/Audio/PCM.cpp) and [MilkdropShader.cpp](https://raw.githubusercontent.com/projectM-visualizer/projectm/6f64807467e312034883a4389e6aa80a675458bc/src/libprojectM/MilkdropPreset/MilkdropShader.cpp); retain their attribution.

The current coefficient is exactly the authored float literal.333f, **not exact1/3**, and original is.3333f. Bands(1,2,3) give current≈1.99800003 versus original≈.99989998. Equal bands(1,1,1) also differ:≈.99900001 versus≈.33329999. Correct the handoff's suggested equal-band unaffected control. Zero injected relative bands agree; treble-only inputs retain a small coefficient difference. No NaN/Infinity normalization or other audio/equation policy is changed.

**I27:** original milkdropfs.cpp3950–3952 computes both mip_x and mip_y from GetWidth(), then their mean. Current uses width and height independently. TV additionally applies ShaderCanvasSize's retained reference reporting before these calculations. At a declared256×144 shader canvas, the original width-duplicate tuple is(8,8,8), current approximately(8,7.169925,7.584963). At actual1280×720 canvas current is approximately(10.321928,9.491853,9.906891).

Original GetWidth() is its host-reported width; current ShaderCanvasSize may report a reference canvas different from physical output. Compare **matched declared dimensions** to isolate the duplicated-width defect. An oracle using1280 for all three components models that defect at a1280×720 input canvas; it is not proof that actual original Windows Native4K used1280. Preserve TV's reference reporting, actual textures/output, Native trails/detail/diffusion, mesh, transitions and prepared replay.

## Field/packing/ABI contracts

The internal shader bindings are float32 vec4 values, unchanged by retention:

| Binding | Components | Shader names |
|---|---|---|
| _c3 | bass,mid,treb,vol | bass,mid,treb,vol=_c3.w |
| _c4 | bassAtt,midAtt,trebAtt,volAtt | bass_att,mid_att,treb_att,vol_att=_c4.w |
| _c12 | mipX,mipY,mipAvg,0 | mip_x,mip_y,mip_avg; mip_xy=_c12.xy |

The shader header and LoadVariables source hashes are in identities.json. These are internal packed-uniform contracts, not new public JNI/C API fields. No Android Java, JNI signature, AAR classes, native transport or shader macro alias is changed. Bind each observed source engine to exact ABI/compiler/source/patch hashes; bind published evidence to APK/AAR/classes.jar/libprojectmtv ABI hashes. Android ARM64 and ARMv7 have separate producer artifacts even when expected finite scalar values agree.

## I26 execution design

Separate three proof levels:

1. **Audio producer:** capture raw analysis relative and attenuated band triples, and PCM::GetFrameAudioData's computed vol/volAtt before any EEL execution. If exact triples are injected for a bounded source control, set/compute the complete coherent FrameAudioData tuple, including its volume fields, through an explicitly identified source adapter. Updating only bass/mid/treb while leaving vol0 does not exercise the current producer contract. Real producer execution and injected fields are different evidence types.
2. **Binding:** compile the actual custom composite, require successful link and live relevant uniform locations, then capture _c3/_c4 immediately after production LoadVariables and before the draw. The live fixture exposes both volume components; direct-band siblings expose xyz independently. Record immutable audioData and separately snapshot mutable EEL fields. `I26-mutable-eel-live.milk` assigns EEL vol7/vol_att9 and bands11/12/13 but must leave shader inputs at the supplied immutable tuple; its shader output must match the ordinary live fixture.
3. **Image:** `I26-live.milk` renders float3(vol/4,vol_att/4,0). With relative(1,2,3), attenuated(.5,1,2), current nominal output≈(.4995,.291375,0); original comma-stage oracle≈(.249975,.16665,0). The two explicit-value oracle siblings use the source-bound float32 scalar models, not fresh production audio. Capture producer/binding first, then final output with explicit read FBO/attachment, dimensions and compiler/program identities. An optimized-away/fallback program cannot satisfy the live uniform gate.

Run bass-only, mid-only, treble-only, zero, equal-band and unequal-band finite controls. For the ratio stock candidate, require differing relative/attenuated spectral distributions; coefficient factors cancel in vol/vol_att, so equal scaling does not demonstrate that authored path's effect. Do not mutate EEL vol to impersonate the original shader defect or change volume modulation globally.

## Actual audio transport versus injection

The production TV route remains unsigned8-bit mono PCM via ProjectMJNI.addWaveform and PROJECTM_MONO. PCM duplicates it into L/R. **I26 still applies to mono**: frequency-band bass/mid/treble values can differ, and even equal bands expose the comma defect. Channel equality is not frequency-band equality. This is distinct from I07 stereo averaging, whose cause is inactive for equal-channel history.

Scalar injection is not stereo PCM execution. Interleaving L/R bytes into the mono JNI entry point is still one mono signal. A stereo source/native bridge, if used, needs its own declared channel/count/layout identity and verified reachable native API; it must not be relabelled unchanged-library evidence if it modifies the published native bytes. Stereo is unnecessary to qualify I26's uniform binding with coherent finite band fields.

Silence PCM is also **not zero relative bands**: existing small-long-average fallback returns relative1. Declare the actual PCM/history/frame/elapsed time and record raw bands instead of equating zero PCM with zero _c3/_c4. Exact injected zero-band controls are useful but must be labelled injected. Mature audio and cold≤30-frame JNI progress protocols have separate lifecycle qualifications.

## I27 execution design and profiles

`I27-live.milk` outputs float3(mip_x,mip_y,mip_avg)/16. Capture the exact actual shader canvas and _c12 before interpreting colors. At matched256×256, current and duplicate-width model both give(8,8,8); at256×144 they differ only in y/avg. The explicit oracle siblings cover square256, nonsquare256×144 and1280×720 current/duplicate-width tuples. Numeric values are source arithmetic models; logf rounding and shader precision require observed float32 producer values/tolerance.

Profile fields must include physical display, completed native render dimensions, shader canvas width/height, line-reference dimensions, actual main-texture dimensions, authored/detail canvas, aspect, mesh, trails gain/detail status and transition generation. With native3840×2160/reference1280×720 and scale3, current reporting gives1280×720 even if texture/output remain native size. ShaderCanvasSize uses area scale and rounded derived dimensions; during reduced/scaled transitions the actual reported integer canvas may vary. Do not hard-code physical4K into the oracle or equate the actual authored detail target with shader reporting without recording both.

The initial finite controls use output/authored256×144 or256×256, no line references/detail/diffusion, mesh48×32, Native Standard, locked preset/no transition, frozen30FPS clock/seed and valid unsigned mono PCM. No texture noise or random bindings occur in diagnostics. Their constant-black compiled warp and scalar composite still need actual compile/link proof. Parent must separately qualify final Native4K output/reference policy; these presets alone do not prove it.

## Exact original candidates

**I26 primary:** `Cope - The Neverending Explosion of Red Liquid Fire.milk`, SHA256ec4a844e75a8c8a8d4a41890495841b670960186988f29797799929a3b5d34d8. Warp2 is declared and live code at280 adds noise3*vol, followed by color feedback at282. Its per-frame equations separately assign EEL vol at260–262, illustrating the immutable-shader boundary. Freeze noise texture bytes, sampler, rand_frame/rand_preset, audio/history, clock and source renderer identity. Scalar binding evidence is necessary before final image attribution.

**I26 ratio follow-up:** `$$$ Royal - Mashup (23).milk`, SHA256822dcc2c35813af84e1ba3c4af0b96c0f8ae32f2e6f971ca4b09206d98addf73, live warp569 uses saturate(vol/vol_att−1.1) and modifies feedback at570. It also overwrites EEL vol and uses noise/blur. Different spectral relative/attenuated profiles are required; common coefficient scaling cancels in this ratio. Keep all non-I26 shader/canvas/noise/feedback inputs fixed.

Both are exact bytes/source candidates, not executed affected originals. identities.json records relevant lines and source hashes. Supplied97 lexical candidates and research's96 active/comment-filtered candidates use different filters; neither is an affected census. Confirm actual compiled consumption and no shadowing/optimization in each original before claiming impact.

**I27:** no exact unchanged corpus witness is available. A fresh source-only token search across current bundled presets found no mip_x/mip_y/mip_avg/mip_xy tokens. It does not prove absence of indirect/internal aliases or future external presets. Do not fabricate an affected original or borrow an audio-volume original to certify the mip policy; use the labelled diagnostics and leave the unchanged-original gate inapplicable/unavailable.

## Ownership, cost and open gates

Disposition proposed: retain all-band shader volume and height-aware mip reporting as corrected upstream behavior, and retain TV shader-reference reporting as intentional policy. Retention adds no new rendering pass, texture, draw, allocation or arithmetic relative to current shipping source. No measured performance benefit or universal visual fidelity claim is made.

Parent owns actual source producer execution, compiled-program/binding proof, unchanged-library transport evidence where reachable, focused original and finite diagnostic Native captures, repeat/cost qualification if required, and final contract documentation. This packet finishes source preparation only; **I26/I27 Native validation remains open**.

Parent actual CGL controls compiled and executed successfully. Actual production HLSL compile/link/source capture,LoadVariables/_c3/_c4/_c12 readback, coherentfinitefield/realPCM/EELbinding isolation and scalar16x16 output checks pass. See production-cgl-controls.txt and compiled-proof. Native4K30job capture controller92243 is ongoing; both IDs remainOPEN pending finalimage qualification. No engine patch.
