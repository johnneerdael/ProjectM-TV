# I24 — Live custom-shape outline thickness

MilkDrop2 consumes `int(thick) != 0` after each shape instance equation and selects four outline passes or one. The current Native renderer selects both its legacy border iterations and quad-line style from the static `thickOutline` setting, so the live value is ignored. Prepared batches also use one shared style; any repair must retain the evaluated value per instance for both authored and native replay, without rerunning equations or changing the existing pixel-centre/offset policies.

## Refined original candidates

All14 handoff candidate byte hashes still match. Twelve candidates assign live thick on a shape whose static border alpha is0 and whose shape-frame code has no direct border_a assignment. They are weak witnesses; no appearance impact is claimed. The two stronger originals are `martin - city lights v2 c.milk` and `martin - city lights v2(1).milk`.

Their shape0 is enabled with49 instances, static thin outline and border alpha.2. The conditional instance>=45 assigns thick=1 on the last four instances, after hiding those instances' fills. This directly identifies the intended effect: four bright, thick blue outlines, while the first45 instances retain their thin style. A global static thick workaround would also thicken the first45 and is not an acceptable expected-image oracle. See [source-screened candidates](source-refined-candidates.json).

## Cost and remaining work

Source-correct selection adds three outline passes for each of those four instances:12 extra outline draws at the authored target, with corresponding Native replay work. This is an authored rendering workload difference, not proof of a measured frame-time regression. A candidate cannot be accepted under the no-performance-impact requirement until its focused timing evidence is gathered. Preserve existing batching, bounded buffers, GL ownership, configuration defaults and per-instance style identity. Fractional inputs truncate toward zero before nonzero testing; undefined nonfinite/out-of-range conversions need the existing safe-input policy rather than invented original appearance.

Execution controls, source-correct candidate, final-output 4K original screenshots and timing qualification remain pending. This entry is not a completed repair or owner decision package.
