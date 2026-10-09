# I23 — retain Native thick-line offset policy

**Disposition: retain current custom-wave and shape-outline offsets, Native scaling and replay. No engine patch.** Actual vertex-output controls and repeated Native4K comparisons qualify this bounded style decision.

Original MilkDrop2 uses one matched-target pixel per extra-pass axis. Current custom waves use half a horizontal pixel and height/(2×width) vertical pixels; shapes use half a pixel per axis. Native scales these reference offsets: at3840×2160/reference1280×720, custom offsets are(1.5,.84375) and shape offsets(1.5,1.5). Main waves have a separate policy and are excluded. Keep the common shape half-destination-pixel phase.

[Production controls](production-cgl-controls.txt) observe actual shader positions, offsets, widths, alpha, primitives, instance counts and once-only equations for authored/Native replay. Four-pass scheduling and current styles pass. Transparent custom waves still submit passes; transparent shape fill remains, while zero-border-alpha suppresses outlines. These are existing contracts, not new optimizations.

[Native results](native-results.json) and [identity](native-identity.json) bind current27/ac3, API34ARM64/GLES3, output3840×2160/Standard1280×720, commonPCM/seed12345/30FPS/mesh48×32. Forty-four runs cover the shared I15/I23 packet; all22 repeat groups and352 PNG/RGB checks pass, with per-frame GL/name/cleanup and finalREAD framebuffer0 checks. [Style comparison](style-comparison-results.json) verifies both live shape/wave fixtures match their explicit current-offset siblings in all eight selected frames. Original-reference-pixel siblings differ.

| Native4K thick wave | Image |
|---|---|
| Current reference offsets | [Current](native-captures/motionstyle-audit-motion-style-I23-wave-live-current-0/frame-239.png) |
| Original one-reference-pixel surrogate | [Reference policy](native-captures/motionstyle-audit-motion-style-I23-wave-1280x720-original-reference-oracle-current-0/frame-239.png) |

The reference surrogate uses four thin copies and means one1280×720reference pixel, presented at scale3. It does not claim that original Windows at physical4K used3pixel offsets. No full-original raster, HDR framebuffer or performance equivalence follows from it. The unchanged Royal113 source witness repeats; the current packet does not substitute static thick flags for executed point visibility or provide a full source-corrected original Royal image.

Retention adds no shipping work. Keep all float-color, input-window, interpolation, line-band, opacity and prepared-replay repairs. A future original-offset option needs an explicit authored/reference/physical dimension contract and its own target fidelity/performance checks. Whole-corpus prevalence and physical-TV timing remain unmeasured. I15 minimum-length review remains separate and open.
