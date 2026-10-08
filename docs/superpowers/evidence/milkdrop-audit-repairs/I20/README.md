# I20 — circle angular spacing and closure

The deferred proposal (historical0028, then candidate0027) changes only Circle.cpp:240 angular samples use denominator239, followed by an exact first-point duplicate before shared smoothing.241 raw points become481 smoothed vertices, drawn as a strip. Original unblended MilkDrop2 uses this contract. The previous240/479 loop had a different seam and point120. Preserve240 audio samples, radius seam interpolation, float6.28/time/aspect/mystery values, opacity, Native widths/thick passes/dot gain/density and one-producer replay.

## Executable proof

Real production geometry, independent source formula, smoothing and LineBatch controls cover21 finite cases: square/landscape/portrait, reference/Native dimensions, zero and finite PCM, time, smoothing and negative mystery. Every raw/smoothed point, exact endpoint duplicate and480 Native segments match the source oracle. Baseline147 geometry assertions fail. Real CGL authored/Native thin/thick/dot submissions add20 baseline failures: strip/dot481 counts and Native480 segment instances. After repair all55 then-integrated normal renderer controls pass; fresh shipping-series51/51 checks pass after removal of the four boolean proposal controls. [Current51](source-current-normal51.txt) · [Current27 patch application](source-current-patch27.txt). Actual red pixels are visible in both intended read targets; no persistent register changes or extra draw/replay style passes are introduced. Mode1 remains open and line-mode density controls remain unchanged. [RED167](source-red.txt) · [Normal55](source-normal55.txt).

Current integrated ASan/UBSan controls also pass51/51: [Sanitizer51](source-current-asan51.txt). ARM64 source-instrumented core/worker build passes at5d721fba.

## Limits and remaining acceptance

Original waveform-geometry blending suppresses its endpoint duplicate. ProjectM TV composites separately rendered presets and has no such wave-blend state; this patch preserves that transition architecture and applies the unblended contract to each preset. It does not claim original blend equivalence or Windows/D3D pixels.

The handoff2736 lexical matches remain unconfirmed affected presets. Eight Royal candidate files match supplied hashes. Two unchanged originals now pass8 final-output Native4K jobs with exact eight selected RGB repeats: Royal137 (thin lines) and Royal11 (dots). Full-frame selected differences peak at12.953767 and22.313464 RGB MAE respectively. Feedback amplifies the geometric change over16 seconds; this is an affected source-trigger witness, not a whole-corpus count. [Royal137 before](original-137-before-4k.png) · [after](original-137-after-4k.png) · [Royal11 before](original-11-before-4k.png) · [after](original-11-after-4k.png) · [metrics](circle-original-image-metrics.json). Android Native4K original/finite/repeats, seam/style acceptance and cost remain pending. The patch adds2 smoothed vertices and1 segment relative to the current loop, with no new draw/pass/target or equations; this source count is not a zero-cost measurement. Candidate remains unaccepted pending those gates.

## Performance gate and owner disposition

All12 finite Native4K style runs pass, with exact eight selected RGB repeats for thin/thick/dots. [Finite before](finite-thin-before-4k.png) · [source-corrected after](finite-thin-after-4k.png) · [repeat results](finite-results.json). Original and finite screenshots are GLES source-corrected candidates, not Windows recordings.

Three isolated ABBA cycles/12 Royal137 runs give mean1.712315ms before versus1.770416ms after: +.058101ms/+3.393%. Cycle changes are+7.069%,+5.715%,−2.504%; variability prevents a universal slowdown claim, but the positive overall cost leaves the no-performance-impact gate unproven. Every timing run's selected RGB matches the original witness by role. [Full cost evidence](cost-results.json). The extra2 smoothed vertices/1 segment are source-required; no fidelity-equivalent optimization was established. Physical-TV FPS is unmeasured.

**Disposition: defer for owner review and withdraw from the shipping patch series.** Retain the [proposed patch](proposed-circle-source-closure.patch), source/GL/sanitizer proofs, actual unchanged-original before/source-corrected screenshots, all finite styles and the complete timing batch. Owner can accept original geometry with this bounded emulator cost uncertainty, or retain the current loop until an equivalent implementation is cost-qualified. No decision question is required to continue the remaining audit.
