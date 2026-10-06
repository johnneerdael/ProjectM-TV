# Source feature evidence

The experimental predictor separates physical calculations from preference scores.
`source_features.py` emits schema 1 records with units, evidence kind, support,
unknown reasons and immutable context/record hashes. It does not assign moods or
regenerate the shipped beta collections.

## Two evidence paths

`geometry_features.scene_geometry_features(scene)` consumes the existing
`scene_equations.execute_scene` output. It reuses custom shape fan vertices,
identifying each component by shape index and physical draw ordinal. Authored
equations can overwrite the EEL `instance` variable; it is not used as identity.
The extractor constructs no display
field, performs no optical flow and does not rerun equations or RNG. Feed its
report to `source_features.geometry_feature_record(geometry, context=context)`
for `strict-source-no-display-frames` evidence.

`forecast_source` additionally returns `feature_basis=source-field-simulation`,
`geometry_features` and `source_features`. Its existing `descriptors` still
summarize simulated display arrays. `retain_surfaces=False` discards those arrays
after computing them; it does not make this strict frame-free prediction. Each
geometry feature retains `sampled-source-geometry` evidence, while display
statistics carry `source-field-statistic` evidence. The forecast adapter rejects
native-frame results and attempts to label a simulated forecast as strict.

## Geometry measurements

Speed, acceleration and jerk report p95, maximum, sample count and normalized
viewport-coordinate units per second, second squared and second cubed. X and Y
are fractions of viewport width and height, not physical screen distance. Every
vertex receives equal weight; these are not screen-area-weighted estimates.

For derivative order n, use n! times the n-th divided difference on n+1
consecutive positions and their actual timestamps. This accounts for unequal
time intervals and recovers constant derivatives of polynomials of degree n.
It remains a sampled finite-difference estimate, not a bound between samples.
At least two, three and four samples respectively are required. Missing support
produces null, while supported stationary geometry produces genuine zero.

Aggregation streams one scene sample at a time and stores compact numerical
magnitudes. The default budget is 1,000,000 derivative magnitudes across all
orders. Exceeding it withholds every derivative summary, reports an explicit
budget unknown and records the partial geometry window; it never exports prefix
percentiles as though they covered the complete declared window.

Births and deaths are counted between samples; components present in the initial
sample are not births. A changed vertex count resets that component's history and
counts a topology change. Disappearance breaks correspondence. The closing fan
vertex is excluded because it repeats the first perimeter vertex.

The current strict scope is **custom shape fan vertices**. Waveform motion,
feedback transport, visibility, occlusion and preset activity remain unknown.
Do not infer calmness from the absence of shapes, or visible motion from an
invisible shape's coordinates. Abrupt changes can raise derivatives, but no
teleport/snap detector or whole-domain smoothness proof is implemented here.

## Identity and unknowns

Records preserve the forecast's source, parsed source, PCM/audio, domain,
compatibility, random and material hashes; absent random/material inputs retain
explicit null identities. Context includes engine commit/patch digest, source
archive, model and reader provenance plus the domain payload. Mode B also requires
the waveform binary identity; strict shape evidence does not require executing
that binary. The adapter verifies hash formats and the domain payload's hash.

`context_sha256` identifies these inputs and the adapter source; `record_sha256`
also covers computed evidence. Preference/profile settings are not part of these
physical feature records. Later profile changes can rescore the same record.

Each scalar feature contains:

```json
{
  "value": null,
  "unit": "normalized viewport coordinates/s³",
  "status": "unknown",
  "evidence_kind": "sampled-source-geometry",
  "interval": null,
  "interval_kind": null,
  "support": {
    "sample_count": 0,
    "scope": "custom shape fan vertices",
    "visibility_established": false
  },
  "dependencies": ["executed equation geometry", "declared time schedule", "component and vertex identity"],
  "unknown_reasons": ["Insufficient consecutive same-identity geometry samples"]
}
```

Dependencies describe calculation inputs, not a complete proof of which audio
band or material influences the output. No calibrated uncertainty interval is
invented. Native runtime failures, inactive output and unsupported contexts are
not converted to computed zero: the adapter accepts only computed source forecasts,
and individual unavailable metrics remain unknown. Future collection eligibility
must inspect required feature support rather than source-parser coverage alone.
Palette statistics require measured frames; temporal event and motion statistics
require measured transitions. An empty warmup-only window cannot supply a computed
zero flash count, hue diversity or motion-availability fraction.

## Current implementation boundary

Palette warmth/hue blending, correlated flash-event records, strict shader colour
queries/bounds, visibility-supported motion, causal response, structure tags and
mood/profile transformations remain follow-up work. The published 2.3.15 AAR is
downloaded and byte-verified in the task workspace, but the forecaster's source44
policies have not yet been migrated to its five newer patches. Historical evidence
is not relabeled as 2.3.15. The unreleased 4.2 rebase remains a separate future
semantic identity.

Validate the pure calculations without a device:

```sh
python -m pytest tools/milk-analyzer/test_geometry_features.py tools/milk-analyzer/test_source_features.py -q
```

Run the analyzer suite with prepared source-bound adapters as documented in the
[analyzer README](README.md). These controls validate calculations and contract
guards, not whole-preset appearance or mood accuracy.
