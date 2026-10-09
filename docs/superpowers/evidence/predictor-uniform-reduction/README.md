# Opt-in static uniform-work reduction

User steering: reduce expensive pixel work using more static interpretation,
without weakening prediction correctness. This is an additional milestone after
the source31/static-family delivery; the larger metric-routing task remains open.

`shader_uniformity.py` proves lane independence from the typed data graph and
binding shapes. Equal observed pixel values are not a proof. Samples, evolving
loop state, effects, unknowns and unsupported operations retain the old path.
Sampler coordinate roots, including roots hidden in loop plans, remain mutable
and are excluded from hoisting. A finite traversal budget fails closed.

Set forecast domain `shader_work_policy=uniform-proof-v1` to evaluate proven
uniform subgraphs once with the same numerical interpreter at one lane, then
reuse their values. The historical/default `full-grid-v1` remains available and
unchanged. Texture callbacks, selected branch domains, loop state, return-array
ownership and arithmetic profiles are retained. Per-stage work counters identify
the reductions. This does not yet remove complete feedback or descriptor fields.

The reviewed callback defect is fixed: read-only broadcast coordinates initially
rejected in-place wrapping. Keeping writable values alone was insufficient when
the same node was reused; blocking mutable coordinate roots and their dependent
consumers preserves that existing behavior. Regression tests cover both cases.

Final prepared suite: **1970 tests and 92 subtests pass**. Reviewed grid/domain/
loop/storage controls and randomized arithmetic comparisons pass. Two authored
presets at128×72 for three source updates and one at854×480 for two updates have
identical feedback/display bits and identical complete47feature objects under
both policies. These are numerical source-model comparisons, not new AAR captures.

The synthetic one-frame854×480 expression benchmarks show about18.3× uniform
and3.0× mixed-expression speedups. A complete short Confetti480p forecast improves
about1.06× (1.824s→1.722s). Do not advertise expression ratios as corpus speedups.
The JSON files retain timing scope, hashes and equality results.

The per-field research is
`docs/superpowers/research/2026-10-09-static-metric-routes.md`. Further work must
prove complete final-output uniformity and reduce its colour/flash descriptors
without changing estimator definitions, null rules, storage or thresholds.
No-flash/physical-motion bounds belong to separate evidence when the existing
optical-flow estimator would be unsupported. Corpus auto-routing remains held
until broader eligibility and complete-preset comparisons establish its value.
