# Nominal scalar audio-control response

The additive audio-route record `nominal_audio_response` reuses the existing
bounded calculus. Selected scalar inputs vary together by the same delta;
other state, audio, time and coordinate inputs stay fixed. The producer applies
chain/product/quotient rules, trig, abs and continuous min/max clamps. Bounds
are sufficient nominal upper bounds, not typical/minimum response estimates,
response directions, real audio time-rates or affected screen area.

For example .2*sin(3*bass)has maximum nominal control slope at most.6 per
bass unit. .2*sin(3*bass+2*mid+time)has bass bound.6 and mids bound.4,
with the other variables held fixed. sin(bass*mid)cannot establish a global
bass bound without a declared mid domain. Thresholds, singular denominators,
dynamic casts/narrowing, opaque effects and budgets remain explicit unknowns.
Quantized main-Q shader uploads receive no false continuous-response credit.
Native numeric and final appearance/mood qualification remain separate.

Packed shader lanes keep names such as _c3.x. Missing/empty/non-string parent
identities are rejected. Scalar projection avoids temporary graph-node IDs in
the memo cache. Native/state input supply is supported by source inspection:
original MilkDrop2.25c vis_milk2/milkdropfs.cpp484–489 binds imm_rel/avg_rel,
and source34 PerFrameContext.cpp158–163 binds audioData bass/mid/treb and
attenuated values. This does not prove those engines have identical audio
analysis. Persistent inputs held fixed are partial instantaneous response,
not derivatives of recurrence or native frame history.

## Fixed sample

All100 exact presets retain computed structured descriptions, original source
hash/byte joins, paired JSON bytes and ZIP CRC. Removing only the new additive
response records and record hashes leaves every preceding description field
identical to the nonlinear-colour checkpoint.

1,705element routes contain218bounded responses across35presets.133bounded
routes across12presets have no preceding linear_gain estimate, adding useful
nonlinear control response data.1,487routes remain unknown; they are not zero
response. The new bounds contain no zero-valued response certificates.
Counts are ingredients, not resolved whole visuals or mood accuracy. Compact
census preserves exact names/hashes, bounded control/input/units and reasons.

Sum of per-preset export times38.738404seconds; maximum2.440571seconds on
this host. No image/audio/time sample, shader or equation execution feeds the
producer. Reader/source34 and saved compile-manifest identities remain pinned;
this is the matching source model for the latest published2.3.36 AAR bytes.
Published-AAR runtime qualification remains separately pending. No authored
presets, native engine, shared corpus/device or full-corpus render was changed.

Raw archive:
`build/preset-corpus/source-audio-response-2026-10-10/batch-000001.zip`.
SHA256 `8c1bcb01d0b10c709fb907300c410ae4d5e6fb7b06d5e29ed1c860763d5e9cba`.
Exact reader, engine/patch, manifest and source-model hashes are in census.json.

## Controls and references

Eighteen new controls cover chain rules, independent bands, min/max cusps,
thresholds, singular/unbounded products, safe denominators, declared domains,
narrowing, underflow, packed identities, main-Q upload and fixed-state premises.
The missing descriptor and packed projection controls failed before their
implementation; an invalid-parent test failed before the guard fix. Red logs
are retained under build/preset-corpus/source-audio-response-*.log.
Independent final review found no actionable math/domain/identity issues;
the integrated198focused checks passed before the extra invalid-parent control.

The basic clamp/interpolation definitions were checked against primary
[Microsoft saturate documentation](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-saturate)
and [Microsoft lerp documentation](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-lerp).
The response bounds are our nominal mathematical inference, not Microsoft
claims of visual accuracy. Direct saturate/lerp response operators are still
outside this response walker; the separate value-range model supports them.

## Final validation and next work

The full prepared suite passes **2,745tests and92subtests in158.35seconds**.
Strict MkDocs and whitespace checks pass. Every prior fixed-sample description
field survives unchanged after removing the additive response records/hashes.
These are interpretation/export checks, not whole-preset visual or mood passes.

`unknown-route-inventory.json` ranks both route counts and distinct affected
presets, retaining exact names/hashes. Operators appear anywhere in an exported
unresolved route; their presence is not root-cause proof.330route expressions
exceed the export representation budget and remain excluded from operator
frequency counts, not from the unknown-route denominator. This inventory can
prioritize follow-ups without assuming a new primitive resolves every route
that happens to contain it.
