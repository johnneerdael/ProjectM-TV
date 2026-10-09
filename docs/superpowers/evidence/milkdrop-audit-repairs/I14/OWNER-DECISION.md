# I14 — defer the general motion-field compatibility change

Keep current triangle/raster/filtered RG16F motion reconstruction pending a separate compatibility implementation and resource review. The supplied source difference is real, but changing only the diagonal, texture precision or sampler does not restore MilkDrop2's four-node CPU bilerp. No general safe/no-cost repair is qualified. The two analytic oracle patches are test-only and must never ship or run against arbitrary stock presets.

The actual production CGL controls separate original node interpolation, current AD/BC rasterization, RG16F/RG32F storage, filtering and actual motion endpoints, preserving prior CPU trig/negative-power, Native replay and motion styles. At the finite Native48x32 fixture, start(.359375,.35546875) has source-bilerp endpoint(.5078125,.33203125), while the current AD field gives(.546875,.29296875). Storage/filtering remains an additional observed boundary, not a guessed half rounding model. See [production controls](PRODUCTION_CONTROLS.md).

Four Native3840×2160 v2 jobs (Standard1280×720 canvas) verify2 exact repeat groups and32 selected PNGs. Current versus the paired finite analytic bilerp oracle visibly changes slope and feedback trails: frame239 RGB MAE0.298407,67,636 changed pixels. Both roles preserve the same actual warp, styles, PCM and preset bytes; the oracle replaces only the motion query for this declared field. This is a bounded finite preset, not a Windows recording or a full source-corrected stock render.

[Current triangle field](native-v2/native-captures/motion-field-oracle-v2-audit-motion-bilerp-native48x32-before-0/frame-239.png) · [Source-bilerp finite oracle](native-v2/native-captures/motion-field-oracle-v2-audit-motion-bilerp-native48x32-after-0/frame-239.png).

Historical v1 Native proof used ignored static mv_x/mv_y keys and therefore the default vector grid. It is preserved under native/ but does not validate the declared2x2 fixture. V2 explicitly uses nMotionVectorsX/Y. Persistent feedback repeats the drawn segment in the final image; do not infer the number of newly emitted vectors from visible trails.

The handoff's794 lexical candidates are unconfirmed. No unchanged stock preset was rendered with a general corrected producer, because no such producer is available. The finite witness establishes a visible interpolation difference without claiming an affected-stock census.

A general repair must preserve actual completed node/producer ownership, both Native/authored consumers, mesh/context/resize/transition generations, per-preset state and prepared replay without duplicate equations. Original CPU node arithmetic differs from the retained GPU producer; replacing that producer globally would risk prior Native fidelity fixes. A compact node buffer/transform-feedback approach needs real program/linkage, sampler, fallback and resource-lifetime proof before a cost comparison. Changing only RG16F to RG32F adds3.515625MiB for the actual1280×720 UV map and still leaves triangle interpolation;31.640625MiB is the additional payload only for an actual4K map. These are allocation arithmetic, not measured bandwidth or FPS.

Owner options: retain current reconstruction, or authorize a separately qualified original-node/bilerp compatibility path with explicit producer and cost policy. No performance claim is made for an unimplemented general repair. Current shipping patches are unchanged by this decision.

[Native verification and hashes](native-v2/native-results.json) · [Exact worker identity](native-v2/native-identity.json) · [Detailed source boundaries](README.md).
