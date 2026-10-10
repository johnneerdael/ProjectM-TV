# Nonzero normalized colour-component bounds

The colour projector preserves normalized scalar lanes in a typed internal range/response node and retains the authored shader domain guard. A strictly positive outward norm minimum is required before any unit component or continuous response claim. Zero-touching, singular, malformed and quantized-response cases stay unknown.

Fixed100 checkpoint:

- One new complete scenario colour stage, in `Stahlregen + Unchained - Dot Kung Fu (fucked up reflecto) hog rot.milk`.
- 82 complete scenario stages, versus81;63 presets with at least one complete scenario colour stage, versus62.
- No new ordinary complete stages or continuous colour-response coverage.
- All100 source/ZIP/result joins and work budgets verified; source-gap inventories unchanged.
- Full prepared suite:2,907 tests and92 subtests pass in166.73 seconds.
- Root106 focused tests, independent112 focused tests, strict MkDocs and diff checks pass. Review reports no actionable findings.

Seven controls cover positive-offset sampled colour, zero-touching domains, declared positive audio-vector response, singular/unbounded component domains, signed components, invalid lanes/matrices and quantized response. Three positive tests failed before implementation. The first implementation retained an unsupported normalize domain wrapper; it was corrected to discharge only the specific typed nonzero component proof, preserving other guards.

The component unit bound is [-1,1], with sign retained. Ratio bounds use the component box and outward norm limits. If norms are at leastm>0, normalized-vector differences are bounded by original-vector differences divided bym; the response ceiling is hypot(component response ceilings)/m. These are nominal sufficient enclosures, not minimum/typical reactivity, response direction, final palette, actual geometry/feedback or mood certification. Component correlations can make them loose; native arithmetic, storage, sampling and runtime domains are unqualified.

Reference: [HLSL normalize](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-normalize) defines division by length with an indefinite zero-length result. MilkDrop2 delegates the shader intrinsic to D3DX; patched GLSL retains the same domain. No renderer or authored preset changes.

Final raw artifacts:`build/preset-corpus/source-normalization-2026-10-10/`; adjacent suite/export/docs/RED logs retained. Census includes the exact affected source hash, before/after stage bounds and reader/source/model/scenario/archive identities. Latest release rechecked asv2.3.36, unchanged full AAR digest `a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3`; source34 matches its byte-identical verified2.3.34 checkpoint. Android runtime qualification stays separate.
