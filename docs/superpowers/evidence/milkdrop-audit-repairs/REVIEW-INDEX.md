# Native4K audit review

Current checkpoint:33/33 findings classified,13 repaired IDs in12 new shipping patches,10 retained policies and10 complete deferred packets. Every finding has a repair or completed owner packet. [Draft PR61](https://github.com/johnneerdael/ProjectM-TV/pull/61) is open; final combined integration/CI/review gates remain separate.

The priority images below are verified final presented output (read framebuffer0), not the historical intermediate captures. They use matched frozen audio/seed/preset bytes and source-instrumented GLES builds. They show expected source-derived TV behavior, not original Windows recordings. Open the PNGs at full resolution for small line/dot details.

| Priority | Disposition and visible effect | Before | Source-corrected candidate |
|---|---|---|---|
| I17 opacity | Repaired0017. Happening's freshly injected dots use the authored opacity operations. | [Native4K](I17/final-I17-before-4k.png) | [Native4K](I17/final-I17-after-4k.png) |
| I19 sample counts | Deferred. Royal103 has more additive strokes at the1280 authored canvas; clean Native cost+.158ms/+2.56%. | [Native4K](I19/final-I19-before-4k.png) | [Native4K](I19/final-I19-after-4k.png) |
| I08 input windows | Repaired0018. Mig304 custom waves use centered/channel-separated audio windows. | [Native4K](I08/final-I08-before-4k.png) | [Native4K](I08/final-I08-after-4k.png) |
| I22 custom dots | Deferred. Nebula loses unauthored midpoint stars; complete proposal measured+.105ms/+5.038% in mosaic. | [Native4K](I22/final-I22-stars-before-4k.png) | [Native4K](I22/final-I22-stars-after-4k.png) |

I19 brightness is compared against the same corrected authored policy: at frame239, corrected authored1280 mean RGB154.689 versus corrected Native4K154.714. That is close average brightness, not pixel identity. At authored256 the correction instead darkens171.080→135.551. [Authored1280 corrected image](I19/final-authored1280-after-frame239.png) and [matched-resolution evidence](I19/final-resolution-bands.json) answer the resolution question. Performance, rather than a judgment that brighter output is inherently wrong, is the deferral reason.

Recent evidence: [M02 border repair](M02/README.md), [I15 minimum-length policy](I15-I23/I15-OWNER-DECISION.md), [I14 interpolation followup](I14/OWNER-DECISION.md), [I16 stale-map followup](I16/OWNER-DECISION.md), and [I24 original city-lights thickness/cost followup](I24/OWNER-DECISION.md).

Every finding's current status, source/capture identity and owner packet is linked from the [complete ledger](README.md). Lexical candidate counts remain unconfirmed impact counts. Accepted focused tests do not certify the full preset corpus or physical-TV FPS; prior TV fixes and frozen historical matrices remain preserved.
