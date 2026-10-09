# Frame-free routes for the maintained 47 feature fields

Research date: 2026-10-09. Source checkout: `predictor-memory-repair`, HEAD `d39bab3a73c273131e6f4de7e69a5fedefd1b201`, PR #67. This document inspects source and existing reports only. No equations, shader numerical simulation, display fields, native capture, devices, or benchmarks were run for this research.

The smallest useful next step is a complete-output uniformity proof plus a scalar descriptor reducer. It can remove spatial execution for colour and sampled flash evidence in qualifying presets, while retaining the optical-flow unknowns. Keep geometry execution independent, and add conservative invariant-output proofs as separate evidence. General feedback presets still need their declared initial state, materials and execution context; identifying a feedback mechanism does not determine its visible colour or motion.

## Contract and source anchors

The 47-field export comprises **12 colour + 17 flashing + 11 motion + one event-list + six geometry fields**. The authoritative names and units are [`source_features.py:UNITS`](../../../tools/milk-analyzer/source_features.py#L22), `forecast_feature_record` and `_geometry`. Geometry may be absent in a caller's forecast; this is the complete export contract, not a claim that every field is computed for every preset.

| Implementation anchor | Semantics relevant to replacement |
|---|---|
| [`descriptors.py:DescriptorStream.add`](../../../tools/milk-analyzer/descriptors.py#L118) | Consumes normalized float32 display RGBA, calculates luma with `[.2126,.7152,.0722]`, pixel-weighted palette, same-location temporal differences, event regions and optical flow. |
| [`descriptors.py:DescriptorStream.report`](../../../tools/milk-analyzer/descriptors.py#L187) | Specifies aggregation, regular-schedule frequency gates, detrending/FFT, supported-flow subset/window policy, and null rules. |
| [`descriptors.py:visible_motion`](../../../tools/milk-analyzer/descriptors.py#L49) | Farneback forward/backward flow, normalized luma, Sobel/edge gate, residual consistency, minimum support; visible motion is an estimator. |
| [`palette_features.py:palette_summary`](../../../tools/milk-analyzer/palette_features.py#L49) | Hard HSV hue bins; saturation/value thresholds; explicit query weights; chromatically conditional warm/cool. |
| [`palette_features.py:hue_change_summary`](../../../tools/milk-analyzer/palette_features.py#L88) | Shortest circular hue differences at matching positions, not tracked motion. |
| [`strict_source_features.py:colour_queries`](../../../tools/milk-analyzer/strict_source_features.py#L39) | Already evaluates isolated shader RGB queries; only promotes spatially independent queries to whole-output palette evidence. Current dependency walker treats every loop as hidden, conservatively. |
| [`strict_source_features.py:strict_features`](../../../tools/milk-analyzer/strict_source_features.py#L69) | Executes source equations, six shape derivatives, selected composite queries and separate builtin-warp point queries; does not build frames. |
| [`geometry_features.py:trajectory_summary`](../../../tools/milk-analyzer/geometry_features.py#L21), [`scene_geometry_features`](../../../tools/milk-analyzer/geometry_features.py#L145) | Same-identity custom shape fan vertices, equal vertex weighting; reset on topology/disappearance; entire derivative window withheld on budget exhaustion. |
| [`pipeline_fields.py:SourcePipeline._store`, `_rgba`, `step`](../../../tools/milk-analyzer/pipeline_fields.py#L260) | Output clamp/storage policy, final custom/default/legacy composite, feedback before composite. Shader-expression RGB alone is not necessarily final stored RGB. |
| [`forecast.py:forecast_source`](../../../tools/milk-analyzer/forecast.py#L542) | Descriptors receive stored display output, possible physical-surface upsample/UNORM8, and a separate native mesh UV field. |
| [`source_classify.py:main`](../../../tools/milk-analyzer/source_classify.py#L11), [`mood_scoring.py:_range`, `_constraints`](../../../tools/milk-analyzer/mood_scoring.py#L68) | Rescores cached evidence; does not execute presets. Unsupported inputs retain uncertainty. Strict evidence cannot carry relabeled `source-field-statistic` entries. Chill requires separately named matching-domain preset-output bounds. |

## Route definitions

**D — declared schedule calculation:** Exact from the complete admitted time schedule and warmup; no pixel or equation execution. Preserve the producer's support gates. These are domain facts, not appearance proofs.

**U — complete-output uniform scalar execution:** Prove final stored display RGB spatially independent, then execute one RGB value per admitted time. Static constants are a subset. Use the existing scalar HSV/palette functions and the same descriptor aggregation, storage policy, warmup and thresholds. This preserves formula-level pixel statistics because every location has the same value. Numerical parity still needs validation: NumPy's repeated float32 reductions can differ from a scalar real-arithmetic formula. Do not claim bit equality before checking the pinned reduction behavior.

**G — equation/geometry execution:** Existing strict route, without rasterization. This remains sampled execution, not purely static analysis or a whole-domain bound.

**W — builtin warp-map execution:** Execute the exact declared mesh and query map. This needs no feedback RGB, but preserving the old field requires its entire raster query schedule/mean or a proved equivalent analytic reduction. Five arbitrary point queries are a different statistic.

**E — spatial estimator:** Preserve the actual optical-flow/support calculation when a numerical estimator value is requested. A physical trajectory, analytic UV speed, invariant image proof or small query set cannot replace it. Uniform output has explicit gate-derived special cases below; these do not turn unavailable flow into measured zero speed.

**B — conservative bound:** Applicable alongside any route when a sound interval proves the property over the *declared* spatial/time/input/resource domain. Store a bound as bound evidence, not as a sampled value. A proof over a finite schedule is not an arbitrary-future no-flash guarantee. Generic normalized-RGB bounds alone rarely narrow classification enough.

## Every field

`U/B` means exact scalar reduction for uniform output; otherwise spatial feedback statistics remain unknown unless sound bounds or a separately proved weighted spatial partition are available. No broad spatial partition implementation is recommended as the first step.

| # | Field | Route and preserved requirement |
|---:|---|---|
| 1 | `colour.mean_luma` | U/B. Mean encoded-RGB luma per frame, then equal-frame mean; not physical luminance. |
| 2 | `colour.mean_contrast` | U/B. Per-frame luma population standard deviation. Uniform mathematical value is zero; validate float32 reduction parity. An output luma envelope `[a,b]` bounds population SD by `(b-a)/2`. |
| 3 | `colour.mean_saturation` | U/B. All-pixel HSV saturation mean, including achromatic/below-value-floor pixels. |
| 4 | `colour.mean_coloured_fraction` | U/B. Both HSV saturation and value threshold gates, inclusive comparisons. Uniform frame contributes 0 or 1. |
| 5 | `colour.mean_effective_hue_bins` | U/B. Mean of per-frame histogram effective-bin counts. **Descriptor empty histogram is 0**, although `palette_summary` reports null for its own empty effective-bin field. |
| 6 | `colour.temporal_effective_hue_bins` | U/B. Effective bins of the combined chromatic histogram, not mean frame diversity. Empty histogram is 0. Uniform frames contribute equal spatial mass. |
| 7 | `colour.mean_hue_entropy_nats` | U/B. Mean of non-null per-frame entropies; all-achromatic window remains null. |
| 8 | `colour.temporal_hue_entropy_nats` | U/B. Entropy of combined chromatic histogram; no chromatic mass remains null. |
| 9 | `colour.warm_cool` | U/B. Chromatic-mass weighted sector coordinate. Achromatic output remains null, not neutral zero. |
| 10 | `colour.hue_rate_p95_cycles_s` | U/B. p95 of transition query-p95 shortest circular same-position changes, only chromatically matched transitions. No matched chromatic pixels remains null. |
| 11 | `colour.maximum_hue_rate_cycles_s` | U/B. Maximum of matched transition maxima, with the same support/null rule. Per-transition shortest difference is at most `.5/dt`; this is an aliased sample statistic, not continuous hue speed. |
| 12 | `colour.mean_hue_query_support` | U/B. Mean both-endpoints-chromatic screen fraction; transitions required. Uniform transition contributes 0 or 1. |
| 13 | `flashing.peak_mean_luma_jump` | U/B. Maximum absolute signed spatial-mean luma delta; at least one measured transition. |
| 14 | `flashing.peak_brightness_change_area` | U/B. Maximum fraction with absolute same-position luma delta at least `brightness_jump`. Uniform transition contributes 0 or 1. |
| 15 | `flashing.peak_paired_luma_area_product` | U/B. Maximum **paired** mean-luma jump × thresholded area within each transition. Never multiply separately aggregated peaks. |
| 16 | `flashing.peak_brightening_screen_area` | U/B. Maximum fraction with signed luma delta at least `brightness_jump`. |
| 17 | `flashing.peak_darkening_screen_area` | U/B. Maximum fraction with signed luma delta at most negative `brightness_jump`. |
| 18 | `flashing.peak_visible_brightening_fraction` | U/B. Uses union of endpoint max-RGB visibility masks and its own denominator; empty union produces 0 after a measured transition. |
| 19 | `flashing.peak_visible_darkening_fraction` | U/B. Same union support and empty-support rule, signed negative threshold. |
| 20 | `flashing.peak_rgb_change_area` | U/B. Maximum fraction with maximum channel difference at least `rgb_jump`; luma invariance alone does not imply zero. |
| 21 | `flashing.coherent_brightening_transitions` | U/B. Count transitions meeting both area and signed-mean thresholds; not cycles. |
| 22 | `flashing.coherent_darkening_transitions` | U/B. Same coherent rule with negative sign; not cycles. |
| 23 | `flashing.dominant_sampled_brightness_hz` | U/B. At least 16 measured rows on a regular schedule, linear detrending, `rfft`, DC removed, nontrivial total power required. Constant/detrended-zero output stays null. |
| 24 | `flashing.spectral_peak_fraction` | U/B. Power of selected FFT peak divided by total non-DC detrended power; same gates/nulls as #23. |
| 25 | `flashing.frequency_resolution_hz` | D. `1/(N*dt)` only for at least three measured rows with the exact existing regularity test. Irregular/short schedule remains null. |
| 26 | `flashing.nyquist_hz` | D. `.5/dt` with the same three-row/regularity gate; not maximum possible underlying event frequency. |
| 27 | `flashing.measured_duration_seconds` | D. Sum measured transition intervals; no transitions remains null. Withhold if extraction does not establish the complete admitted window. |
| 28 | `flashing.coherent_transitions_per_second` | U/B. Count transitions with coherent-up **or** coherent-down divided by measured duration. |
| 29 | `flashing.local_or_colour_change_transitions_per_second` | U/B. Count transitions having any thresholded luma **or** RGB area divided by duration. |
| 30 | `motion.available_transition_fraction` | E. Flow-supported transitions / measured transitions. Proven uniform final output gives exact 0 from contrast gate, but insufficient window still means unknown at record adaptation. |
| 31 | `motion.mean_supported_area` | E. Mean valid-pixel area over **supported transitions only**. Uniform/untrackable output remains null. |
| 32 | `motion.median_speed_viewports_per_second` | E. Median of per-supported-transition pixel speed medians. Respect legacy subset versus coverage-gated policy; uniform output remains null. |
| 33 | `motion.p95_speed_viewports_per_second` | E. p95 of transition pixel-p95 speeds, with the same window policy. Not p95 geometry or analytic UV speed. |
| 34 | `motion.mean_acceleration_viewports_per_second_squared` | E. Change in consecutive available transitions' median flow vectors / mean dt, then mean magnitude; no consecutive supported pair remains null. |
| 35 | `motion.mean_warp_query_displacement` | W/B. Mean per-frame norm of the **builtin warp UV** minus original pixel centres, then mean of available rows. Not temporal speed; custom shader sample transforms and content visibility are absent from this metric. |
| 36 | `motion.matched_brightness_change_p95` | E. p95 across supported transitions' correspondence-matched pixel-p95 luma changes. Uniform output remains null. |
| 37 | `motion.peak_matched_brightness_change_p95` | E. Maximum supported transition matched-brightness p95; same null rule. |
| 38 | `motion.peak_untracked_brightness_change_screen_area` | E; uniform U special case. Maximum raw thresholded luma area outside valid flow mask. With uniform output all flow is unavailable, so this equals #14, provided a measured transition exists. |
| 39 | `motion.peak_matched_brightening_screen_area` | E. Maximum screen fraction inside valid flow mask above matched positive luma threshold. No available flow remains null, not zero. |
| 40 | `motion.peak_matched_darkening_screen_area` | E. Same supported-flow fraction for negative matched luma threshold; null if no available flow. |
| 41 | `flashing.events` | U/B for numerical regional data; a bound is not a replacement event list. Preserve one correlated record per measured transition, signed delta, time/dt, each region's area/mean/max amplitude, null amplitudes for empty regions, coherent flags and `motion_crossing_ruled_out=False` as authored by current producer. |
| 42 | `geometry.speed_p95` | G/B. p95 of equal-vertex same-identity custom-shape divided-difference magnitudes. Needs two consecutive samples; visibility unproved. |
| 43 | `geometry.speed_maximum` | G/B. Maximum of those sampled vertex speeds; not between-sample bound. |
| 44 | `geometry.acceleration_p95` | G/B. p95 second divided differences × `2!`; three corresponding samples required. |
| 45 | `geometry.acceleration_maximum` | G/B. Maximum second divided-difference magnitude; preserve topology resets and budget behavior. |
| 46 | `geometry.jerk_p95` | G/B. p95 third divided differences × `3!`; four corresponding samples required. |
| 47 | `geometry.jerk_maximum` | G/B. Maximum sampled third derivative; no temporal smoothness or visibility proof. |

The partition is **3 D + 6 G + 1 W + 27 U/B + 10 E = 47**. The uniform special cases for E do not expand the meaning of supported flow. A fully uniform display can yield a useful palette and zero sampled change counts while all flow speeds are correctly unknown.

## Bounds that can help without spatial execution

Start with output envelopes and invariance, not a general abstract renderer. Clipped RGB gives each channel and luma `[0,1]`, SD `[0,.5]`, saturation/area/product `[0,1]`, warm/cool `[-1,1]`, hue entropy `[0,log(hue_bins)]` when chromatically supported, and effective bins `[1,hue_bins]` when supported or 0 for the descriptor's empty histogram. These bounds do **not** establish the chromatic denominator or resolve a null field. Hard hue-bin/threshold discontinuities require subdivision or abstention; a min/max RGB box is not a colour histogram.

A proved pointwise RGB change envelope wholly below both descriptor jump thresholds establishes zero thresholded areas and transition counts for that domain. Luma-only bounds cannot rule out coloured changes. Interval subtraction of unrelated per-frame envelopes is conservative and often loose; maintain correlated terms before using it for a no-change result. FFT peak location/fraction generally cannot be recovered from an amplitude envelope. Discontinuous branches, division domains, pow/log/normalization, random state, loop termination and float storage require explicit policies and conservative unknowns.

Physical geometry derivative bounds can be useful **as separate geometry evidence**. They do not bound the maintained Farneback output or whole-preset visible motion. Images can be invariant despite moving coordinates, or animated despite stationary shapes. Textureless/repetitive images and brightness changes can also make flow untrackable. Replacing #32–34 with analytic velocity would change the field contract.

## Separate program-level no-flash/no-motion proof

Begin with a narrow proof of **final stored RGB invariance** over a declared domain. A resolved constant final composite independent of UV, diffuse, feedback, random, material and time/audio/state inputs is a useful witness. Include stage selection/fallback, output storage and any physical-surface blit. Live irrelevant upstream mechanisms do not determine final colour, but skipped upstream obligations and any newly admitted unsupported paths must be explicit rather than silently borrowing the old forecast's qualification.

Prove global invariance only when all admitted executions return the same stored output and termination/domain obligations hold. For spatially nonuniform stationary output, also require a fixed initial state and invariant material/sample coordinate domain, or a sound invariant-state argument. A source file without resource/initial-state premises cannot generally prove this for arbitrary feedback. A finite RGB time series establishes sampled invariance only; aliasing and future events remain possible.

Emit a separate `source-domain-bound` witness with `interval_kind=conservative-domain-bound`, `support.scope=preset-output`, and matching `domain_sha256`, plus the dependencies and proof premises. The existing Chill constraint names are `motion.speed_upper_bound_vp_s`, `motion.acceleration_upper_bound_vp_s2`, `motion.jerk_upper_bound_vp_s3`, `flash.coherent_transitions_hz`, and `flash.local_or_colour_pulses_hz` ([`mood_scoring.py:CHILL_CONSTRAINTS`](../../../tools/milk-analyzer/mood_scoring.py#L28)). Their acceptance requires a sound definition of whole-output activity; only a verified invariant-output witness supports zero bounds. A static feature-family label, stationary shape or zero sampled count does not.

Retain the original 47 estimator values/nulls unchanged. In particular, the old flow estimator can return null speed for a program proved stationary, and a constant brightness FFT has no dominant frequency. Extra proof evidence can improve separate eligibility constraints without forging a measured speed, matched brightness or frequency.

## Smallest implementation sequence and controls

1. **Reuse typed dependency/LoopPlan reasoning to produce a complete final-output route decision.** Return uniform, spatial, or unresolved with causes; separate ordinary inputs, sampler reads, loop/effect obligations, and selected stage/fallback. Avoid the current blanket hidden-loop rejection only after termination and all live plan dependencies are accounted for. Lower once per stable program/context rather than once per frame. This step can support hoisting even when the whole preset remains spatial; the parent research investigates that opportunity separately.
2. **Implement uniform scalar descriptor reduction, preserving all 27 U fields and the two E gate-derived special cases.** Apply the full display clamp/UNORM storage policy first; the existing strict colour-query path only clamps and cannot be copied unchanged into equivalent simulated field values. Execute required equations/audio/state in their declared order. Use resolved current output only; legacy/default and resource-dependent composites initially abstain. Preserve all other flow fields as null and six geometry fields through their existing route. Add D values only for a fully admitted schedule.
3. **Add the narrow invariant-output proof above.** Append matching-domain bounds; do not widen meanings or rewrite cached 47-field records. Prove constant-after-storage where clipping/quantization makes a live scalar input irrelevant, only with sound input domains and numerical policy. Defer arbitrary spatial feedback invariants.
4. **Keep W optional.** Reuse exact builtin mesh queries without RGB fields when #35 is requested; do not pretend current `warp.query_displacement_mean` at five points equals #35. An analytic affine reduction still needs exact query positions, area weighting and norm aggregation. Add only if an actual consumer requests this field and measured cost warrants it.

Acceptance controls should compare every numeric value, null and support label against the existing descriptor producer on small synthetic controls in a later authorized validation task. No such simulation was performed here. Include: constant black/grey/chromatic fields; uniform luma pulses versus equal-luma RGB changes; achromatic/chromatic transitions; hue wrap/bin boundaries; threshold equality; one/two/three/15/16 measured rows; irregular dt and warmup boundaries; constant/linearly detrended FFT null; paired event peaks from different transitions; UNORM8 threshold crossing and float32 reduction differences. Include both motion window policies and confirm uniform output's exact unavailable-flow fraction, unknown supported areas/speeds and untracked brightness area.

Dependency controls must include live UV/diffuse/material/feedback, dead reads, component projections, uniform versus spatial hidden loop reads, zero-iteration versus bounded/unresolved loops, nonfinite unused uniforms, fallback stages and policy/hash changes. Existing strict tests already exercise spatial colours, missing feedback, hidden-loop dependence and unused nonfinite uniforms ([`test_strict_source_features.py`](../../../tools/milk-analyzer/test_strict_source_features.py#L17)); extend these boundaries rather than replacing their unknowns. Geometry controls must keep same-identity/topology/budget rules and avoid visible-motion aliases. Scoring controls must retain simulated opt-in, exact record/context hashes, unknown preference weight, and rejection of nonmatching or partial-scope bounds.

## Existing measurements and coverage limits

[`static-effect-family-benchmark-2026-10-09.json`](../../../tools/milk-analyzer/fixtures/static-effect-family-benchmark-2026-10-09.json) records **100 fixed content-hash-selected pack sources**, one process, Python 3.14.5/macOS arm64, no simulation: cold parsing + symbolic families **25.609 s total, 0.25609 s mean, 0.35133 s p95, 0.54795 s max**; cached **0.70359 s total, 0.00704 s mean**, with 100/100 cache hits. Peak process maxrss is **111,869,952 bytes** on Darwin. These timings cover static mechanism analysis, not the proposed scalar reducer, geometry route or equivalent 47-field extraction.

[`static-effect-family-review-100-2026-10-09.json`](../../../tools/milk-analyzer/fixtures/static-effect-family-review-100-2026-10-09.json) reports 100 computed analyses, 99 with mechanisms and 91 with explicit unknowns. Its counts are **mechanism rows**, including 128 radial-feedback rows, 125 polygon-shape rows, 75 image-driven-advection rows and 62 custom-wave rows; they can exceed the number of presets and cannot be converted to preset route coverage. The file explicitly says classification accuracy was not measured. These results support keeping feedback and unknowns first-class; they do not say how many final composites are uniform or how many 47-field simulations can be avoided.

The task reports full simulation at roughly 40 seconds to minutes per preset, but this inspection found no paired same-input timing report in the cited files. Therefore no speedup factor, uniform-output coverage percentage, cost of scalar/geometry execution, or whole-pack runtime projection is claimed. A source-only fixed-100 routing census should count uniform/spatial/unresolved final outputs and denominator-preserving reasons; subsequent paired timing must retain the same engine/context/source hashes, original cases and field-support outcomes. No rerolling of difficult sources.

Recommendation: prioritize the shared dependency route decision and uniform scalar reducer, then append narrow invariant-output bounds. Retain the full spatial/flow path for requested estimator values and unresolved resources. This gives useful frame-free evidence without defining a replacement framework or changing what the 47 existing fields mean.
