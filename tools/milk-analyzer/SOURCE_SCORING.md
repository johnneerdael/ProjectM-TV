# Source mood and profile scoring

`mood_scoring.py` implements the research's explicit initial mappings over cached
source feature records. It does not execute presets, build display fields, inspect
images, or replace the packaged beta indexes. Its weights and thresholds are chosen
assumptions, not calibrated audience accuracy.

## Score cached evidence

```sh
python tools/milk-analyzer/source_classify.py \
  --features source-features.json --profile melodic-techno-v1 --output scores.json
```

The input is a schema1 source feature record, including its context and record
hashes. Native evidence is refused. Strict source evidence is the default;
`--allow-simulated` explicitly permits a `source-field-simulation` record and keeps
that basis in the output. A hash-consistent edited domain cannot borrow the old
domain identity: the domain payload is checked against its declared input hash.

Use `--profile-file` for an editable JSON profile instead of a starter profile.
Profiles contain `id`, `preferences` and `constraints`. A preference names a raw
feature or `score.intensity`, `score.smoothness`, `score.warm`, `score.cold` or
`score.psychedelic`, with `target:[low,high]`, positive `scale` and positive `weight`.
A constraint names a raw feature, `minimum` and/or `maximum`, and can require
declared conservative bound evidence with `require_bound:true`.

Profile changes rescore the same record without source execution. Output preserves
the feature-record/context hashes, scoring-code hash and profile hash separately.
Unknown measurements retain their requested preference weight. Equal large weights
are normalized safely; numeric underflow is unresolved rather than silently losing
that preference. A profile with no measurements is not automatically eligible.

## Physical inputs and current coverage

The formulas consume these research keys:

| Axis | Required physical input | Saturation scale |
|---|---|---|
| Motion activity | `motion.speed_p95_vp_s` | .75 normalized viewport coordinates/s |
| Abrupt movement | `motion.acceleration_p95_vp_s2`, `motion.jerk_p95_vp_s3` | 3/s² and15/s³ |
| Discontinuities | `motion.discontinuities_hz` | 2 events/s |
| Coherent brightness changes | `flash.coherent_transitions_hz`, `flash.coherent_delta_peak` | 4 transitions/s ×.30 encoded-luma delta |
| Brightness activity | `brightness.jump_p95` | .30 encoded-luma change |
| Bass response | `audio.bass_peak_rgb_effect` | .20 whole-area mean absolute normalized RGB difference |
| Palette | `palette.warm_cool`, `palette.coloured_support`, `palette.effective_hue_bins`, `palette.hue_rate_p95_cycles_s` | −1…1; fraction; `(bins−1)/7`; .50 hue cycles/s |
| Structure | `structure.nonlinear_warp`, `structure.symmetry`, `feedback.complexity` | supplied normalized structural coordinates |

Current producer aliases are supported for the corresponding `colour.*` palette
fields and `flashing.coherent_transitions_per_second`. A direct cold preference can
also use `colour.warm_cool`; negative warmth is valid. Negative motion magnitudes,
event rates or other unsigned physical values are rejected.

**Most complete activity/style inputs remain future extraction work.** The scorer
does not convert the current flow estimator's mean acceleration into geometry p95,
use a peak as a p95, infer discontinuities from births, substitute partial custom
shape motion for whole-preset motion, or manufacture symmetry/fractal/feedback
scores. Actual current records often yield wide intervals and no automatic
activity/genre assignment. That abstention is part of the contract, not evidence
that a preset is inactive. The palette mappings already consume current records.

## Initial formulas

For normalized components M,A,J,F,B,R,Q in0…1:

```text
M = clip(speed/.75)                 A = clip(acceleration/3)
J = clip(jerk/15)                   Q = clip(discontinuities/2)
F = clip((coherent_rate/4)*(coherent_delta/.30))
B = clip(brightness_jump/.30)       R = clip(bass_effect/.20)

Ibase = 1 +99*(.28M+.12A+.08J+.32F+.12B+.08R)
Intensity = max(Ibase,1+99F)
Smoothness = 100*(1−.35A−.45J−.20Q)
Warm = 50*(1+warm_cool)             Cold = 50*(1−warm_cool)
Psychedelic = 100*(.20*palette_diversity+.25*nonlinear_warp
                  +.25*feedback_complexity+.20*symmetry+.10*hue_evolution)
```

Raw values remain in the feature record. Clipping applies only to scoring. Missing
components occupy0…1 and produce a score interval; coefficients are not
renormalized around them. Supplied feature intervals propagate through the model.
Supported interval evidence is distinct from a point-valued score. These are
range estimates/declarations, not calibrated statistical confidence intervals.

Warm/Cold additionally need at least20% coloured support. Smooth starts at80.
Psychedelic starts at70 and requires at least two of nonlinear warp, feedback
complexity and symmetry to have supported lower coordinates of at least.60.
Rainbow colour alone does not qualify it, and flashing is not a requirement.

## Bands and hard constraints

Chill1–30, Normal25–75 and Intense70–100 are inclusive and overlap. Assign a band
only when the whole intensity interval lies inside it and is at most10 points
wide. Boundary-spanning intervals remain ambiguous.

Chill additionally requires declared full-preset conservative bounds within the
matching context: speed≤.20, acceleration≤.60, jerk≤2, coherent transitions=0 and
local/colour pulses=0. Each bound must identify the same domain, `preset-output`
scope, `source-domain-bound` evidence and `conservative-domain-bound` interval.
Samples alone do not prove these constraints. The scorer checks declarations; it
does not create a new mathematical proof certificate. A low intensity with missing
or failed Chill constraints is not forcibly classified Normal or Intense.

## Genres and personal defaults

Starter profiles cover ambient, chillout, trance, melodic techno, techno, hardstyle,
pop, hip-hop, jazz and classical, plus neutral, gentle home TV, focus, psychedelic
and party preferences. All are editable assumptions. Genre suitability expresses
fit to a requested music/viewing context; it does not discover an absent song's
genre from preset code.

Each preference uses `fit=exp(−.5*d²)`, where d is distance outside its target range
divided by scale. Suitability is100 times the weighted mean fit. Unknown preferences
contribute a range0…1 while keeping their weight. Default automatic eligibility
requires every constraint to pass, at least90% supported preference weight and a
suitability interval at most10 points wide.

Melodic techno targets intensity35–75, Smooth85–100, bass effect.02–.08, symmetry
.75–1 and feedback half-life.3–1.5 seconds. Its weights are.25,.20,.20,.20,.05;
palette is deliberately unrequested, so total weight is.90 before normalization.
Missing requested structure/feedback remains unknown instead of being dropped.

Optional `--age-band 70+` selects the owner's gentle first-use default only when
no explicit profile is chosen. The other age bands share the same neutral default.
Any explicit profile—including neutral or psychedelic—fully overrides that prior.
No age-specific taste probability, brightness rule or medical safety claim is made.
Whole-preset comfort constraints and player transition behavior require separate
evidence; accepted individual presets do not prove an acceptable transition.

## Verification and remaining work

```sh
python -m pytest tools/milk-analyzer/test_mood_scoring.py tools/milk-analyzer/test_source_classify.py -q
```

These analytic/hypothetical feature controls validate mappings, unknown propagation,
context guards and profile behavior, not whole-corpus prediction quality. Strict
colour-query orchestration, complete geometry/transport visibility, pulse proofs,
causal-response integration, structure extraction and an intentional validated
source-index migration remain separate work. The existing beta indexes are unchanged.
