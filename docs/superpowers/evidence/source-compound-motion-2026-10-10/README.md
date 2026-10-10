# Compound source-time movement bounds

The source model now describes sums/products of oscillators, nested phase
modulation and supported safe quotients with continuous nominal range/rate
estimates. The original expression DAG remains exported. Exact old constant,
affine-time and single-oscillator estimates are distinguished from conservative
compound upper bounds; periods or harmonic path families are not invented.

The rules apply chain/product/quotient derivatives and interval magnitudes.
[NIST DLMF4.20](https://dlmf.nist.gov/4.20) documents the trig derivatives;
[4.21](https://dlmf.nist.gov/4.21) supplies the related identities.
Target EEL sin/cos/abs/min/max/divide functions are checked against prepared
source34 `vendor/projectm-eval/projectm-eval/TreeFunctions.c`. Original
MilkDrop2.25c intent remains referenced in the supplied ns-eel2 source.
No native source or authored preset is changed or copied into the model.

`nominal_continuity` separates smooth formulas from a weaker piecewise
Lipschitz class allowing cusps, and from unknown regularity. This distinction
propagates through centre/vertex and compact instance rows/group summaries.
It does not prove a cusp occurs or certify visible smoothness/Chill suitability.
Dynamic sides and known invalid float32 projections retain unknown vertex
regularity. Unbounded rate and bounded values remain separate facts.

EEL zero-guarded division is separate from ordinary division: an entire
proved denominator envelope strictly inside the guard gives zero; crossings
stay unresolved. Missing audio/state domains, random and integer-step inputs
remain unsupported. Endpoint/rate operations expand outwards. Positive rate
underflow and nonfinite estimates stay unknown. A rounded singleton envelope
is insufficient to prove constant trig. These are nominal calculus estimates,
not shader-interval execution, float32/libm parity, visibility or mood proofs.

Twenty-five test-first controls cover independent formulas, singularities,
guards, cusps, propagation, value/rate separation and arithmetic edges. Review
found quotient underflow and false singleton folding; their exact regressions
were observed failing and fixed. The existing affine/single-oscillator paths
also now reject rate underflow rather than claiming stationarity. Producer
focused255tests pass; independent review passed237and found no further issue.
The obsolete unsupported-product fixture became a positive conservative-bound
control; unknown/state/singular cases remain guarded.

On the unchanged100source sample:
- 34previously unknown control rates are now available across16presets.
- Six shape-centre bounds across four presets are new; the known-centre pool
  is26presets. Some of those presets already had other known shapes.
- Five shape-vertex bounds across three presets are new; the known-vertex pool
  is20presets. These are geometric bounds, not on-screen motion measurements.
- Instance path support increases from2to194paths; complete instance-group
  speed bounds remain unknown. Audio/state/radius gaps still constrain them.
- All34new compound named controls have smooth nominal formulas in this sample;
  cusp handling is validated by controls, not claimed as a new sample finding.

No previously supported shape path became unknown in the source comparison.
Overlapping counts are ingredient coverage, not visual/mood prediction accuracy.
The100exports total33.12preset-operation seconds, maximum1.41seconds for one
preset on this host. These sample timings are not a whole-corpus guarantee.
No native equation/shader execution, audio/time sampling or frame inspection
was used. Raw source byte/hash joins and ZIP CRC match the preceding batch.
`census.json` preserves exact rows and source/model/parser/engine identities.

Raw paired archive:
`build/preset-corpus/source-compound-motion-2026-10-10/batch-000001.zip`
SHA256 `333c04e6feccc59d4f3a50b7fa35be6d117c5ae8f281d06c97d4b35e4c392c47`.
The observed latest2.3.36full AAR remains byte-identical to2.3.34; source34
is the explicit matching source adapter. Unchanged-AAR runtime qualification
remains pending separately; no shared corpus or device was operated.

Final prepared suite: **2,503tests and92subtests pass in143.25seconds**.
Strict MkDocs and whitespace checks pass. This is a source-math checkpoint,
not an appearance or calibrated mood score.
