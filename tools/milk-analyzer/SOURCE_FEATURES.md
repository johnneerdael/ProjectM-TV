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

## Palette and correlated events

`palette_features.py` summarizes normalized N×3 RGB queries without constructing
a display field. The producer must establish where those queries came from;
feeding flattened simulated pixels into the helper remains mode B. Equal weights
measure query frequency, while explicit weights carry the producer's relative
weighting. They are not automatically screen-area weights.

`warm-cool-sectors-v1` assigns warm plateaus at −30…90 hue degrees and cool
plateaus at 150…270, joined with cosine tapers. Green120 and purple300 are neutral.
This is an editable vocabulary convention, not a measured audience preference.
The mean uses chromatic weight only. Grey, black and below-threshold queries have
no warmth or hue entropy. Positive weight underflow remains an explicit numerical
failure rather than being reported as zero chromatic support.

Hue entropy is `−sum(p*log(p))` in nats, with effective bins `exp(H)`. Spatial
per-frame entropy and pooled temporal entropy remain separate. The simulated-field
descriptor computes warmth over all supported chromatic pixels and samples. Its
hue-rate summary is the p95 of transition query-p95 shortest circular hue changes
per second; both query endpoints must be chromatic. Maximum hue rate and matched
chromatic-query support are also retained. Same-position colour changes can include
moving edges or changed textures; they do not establish object colour blending.

Every measured transition now preserves a correlated event record with start/end
time, positive duration, signed mean-luma change, brightening/darkening/RGB affected
areas and mean/maximum amplitudes within those areas. RGB amplitude uses the largest
absolute channel change; brightness uses encoded RGB luma. Empty affected regions
have null amplitudes. The source feature record hashes and retains these tuples.

Coherent and local/colour change rates use the sum of measured transition durations.
Local/colour changes are retained independently of the coherent 20% gate. These
are **sampled changes per second**, not flash cycles: every event keeps
`motion_crossing_ruled_out=false`. Do not use a zero sampled event rate as a proof
that arbitrary future audio, assets, state or time cannot produce flashes.

## Current implementation boundary

The [source scoring layer](SOURCE_SCORING.md) now consumes cached evidence using
explicit assumed mood/profile mappings. [Strict source extraction](STRICT_EXTRACTION.md)
executes geometry, sparse warp points and isolated shader-colour queries without
display fields; spatially independent supported composite colours can supply palette
features. Visibility-supported motion, causal-response integration and structural extraction
remain follow-up work. The published 2.3.15 AAR is
downloaded and byte-verified in the task workspace. The forecaster now selects
its five new policies from the exact source49 commit/patch identity: repeat/linear
unnamed shape sampling, coherent float32 blur ranges, signed negative zoom only
at unit exponent, evaluated built-in waveform controls, and evaluated legacy
gamma/echo/filter controls. Source44 and earlier policies remain historical or
explicit counterfactual controls; their evidence is not relabeled as 2.3.15.
The unreleased 4.2 rebase remains a separate future semantic identity.

The pinned AAR and both ABI/class hashes are in
`profiles/published-core-v2.3.15.json`. Source CPU controls verify modeled math,
including explicit reader IEEE tags at native-defined fallback/clamp boundaries.
Omitted waves do not consume unused geometry or draw controls. A separate fresh
JNI host built from the exact published classes/library passed one frozen
256×144 constant-RGB control with zero channel error. This establishes bounded
JNI loading/readback; it does not certify all five policies' GPU parity or authored
preset appearance. See `fixtures/published2315-jni-qualification-2026-10-07.json`.

Validate the pure calculations without a device:

```sh
python -m pytest tools/milk-analyzer/test_geometry_features.py tools/milk-analyzer/test_source_features.py -q
python -m pytest tools/milk-analyzer/test_palette_features.py tools/milk-analyzer/test_descriptors.py -q
```

Run the analyzer suite with prepared source-bound adapters as documented in the
[analyzer README](README.md). These controls validate calculations and contract
guards, not whole-preset appearance or mood accuracy.
