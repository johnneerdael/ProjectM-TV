# I31 — Gamma-only pass count

Candidate0019 restores MilkDrop2’s gamma-only epsilon `.001f` from `milkdropfs.cpp:4245`, preserving echo redraws’ `.0001f`, current float diffuse precision, live gamma, blend behavior and tint fix0014. Native4K output/timing and final integration remain pending.

The real-GL draw/attribute regression fails before at gamma1.0005: two passes instead of one. It passes after at the gamma boundary cases0/1/1.00005/1.0005/1.0011/2/2.001/2.0011/8, including uploaded per-pass float diffuse weights. Echo branch pass counts are tested unchanged. All42 normal renderer controls pass; all19 ordered patches apply cleanly.

The unchanged original **suksma - type o negative - world coming down.milk**, SHA256 `1eae0591633d591883bf3dc5340bed937d4ba80ef566ffb8ce668cef3bf919ed`, is the narrow source witness: loaded float gamma2.000999927520752, no echo, composite version0, tint0 and no overriding gamma/echo equations. Original count is two passes, current baseline three. The initial68 handoff candidates are not an impact census; most fail this branch/boundary condition.

Do not invent a brightness improvement. Ideal total float weights agree, but per-pass RGBA8 rounding can differ and original byte-packed diffuse remains separate I30. An identical captured image is a valid result if count/weights prove the correction. This candidate adds no pass or allocation and can remove one fullscreen pass in the narrow boundary interval. Actual Native4K measurements still determine the focused acceptance claim.

## Native4K result

All four480-frame original-preset runs complete with Native Standard1280×720 canvas, strict GL/name/cleanup checks and identical selected-frame repeats. Every one of the eight before/after full-resolution RGB frames is also byte-identical. This is a valid result: the narrow pass/weight difference is the causal oracle, and no visible brightness improvement is invented.

![Gamma-only original before, Native4K](before-4k-frame239.png)

![Gamma-only source-corrected after, Native4K](after-4k-frame239.png)

Mean/p90 timings before3.343/3.986 and3.272/4.183 ms versus after3.440/4.347 and3.332/4.148 ms are close with variable scheduling; no speedup or universal zero-cost claim is established. Production work removes a pass at the admitted boundary and adds no computation/resource. Count and image qualification pass; final timing/integration disposition remains open.
