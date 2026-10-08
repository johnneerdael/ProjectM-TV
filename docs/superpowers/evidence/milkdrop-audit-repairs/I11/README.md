# I11 — Legacy physical triangle diagonal

Candidate0024 selects the opposite AD cell diagonal only for the actual compiled legacy/default path. Custom warp keeps BC; failed custom compilation uses legacy. It selects six offsets once per mesh initialization and fills the existing index buffer: identical vertices, indices, triangles, winding sequence, quadrant order and draw/pass counts. A cached compiled-path flag prevents stale topology if the path changes at fixed dimensions. No second persistent index buffer, texture or target is added. Source initialization bookkeeping changes still require focused cost qualification.

## Executable proof

The test uses the actual production mesh/warp shader and an asymmetric corner field: A/B/C displacement0, D displacement1. At raw cell local(.3125,.3125), the original physical legacy diagonal contributes.3125; the previous diagonal contributes0. On a known64×48 gradient feedback target, that is red90 versus10 at the same pixel. Baseline fails; candidate passes. It also reads actual indices across all quadrants, checks identical288-index count and winding, exercises legacy→custom→failed-custom→legacy without size changes, preserves custom/affine output and prepared replay.

[Source RED](source-red.txt) · [Full normal suite48/48](source-normal.txt). All24 patches apply to a fresh pinned source. I10's oscillators are disabled in this witness (warp0); equation traversal and per-vertex values are unchanged. Source-stage GL proof is not Windows pixel-identity certification.

## Original and remaining validation

The stronger original candidate is `07.milk`, SHA256 `ec440dc5d1409388d8b55c17e683bbe8e1cd5effac1060faefdb71e222ad7849`: nonlinear radial/angle per-pixel zoom and explicit warp0. The878 lexical candidates are not an affected census. Exact-original Native4K captures, finite corner-field diagnostic and repeat/cost qualification remain pending, as do final combined integration gates.
