# Conditional varying feedback colour envelopes

The additive feedback_envelope record supports affine-in-main RGB expressions
with varying non-image coefficients and offsets. Existing scalar source bounds
supply coefficient ranges; per-output-row sums of absolute coefficient maxima
bound fixed-coordinate RGB infinity-norm perturbations. Different sample sites
stay independent. Signed coefficients and unit-interval sample premises supply
raw RGB boxes. Correlation can tighten these conservative envelopes but is not
estimated from time/frame samples.

Image-driven coordinates retain unknown contraction. Otherwise gain<1 is only
a sufficient colour-operator bound under image-independent nonexpansive sampling
and identical external inputs. Nominal log(.5)/log(gain) half-life excludes
native rounding, storage, drawing/blending, blur/detail, discard and full feedback.
Failed sufficient conditions are not instability; actual persistence stays null.
Nonlinear sampled-colour products, unbounded/singular coefficients, blur/history
and unresolved nodes remain unknown. The older exact point model is unchanged.

Native Q/fixed-decay narrow nodes validate finite float32 endpoint conversion
before using explicitly derived local scalar domains. scalar_value_envelope
accepts input_domains and exports consumed declared premises. Known overflow,
invalid/reversed/malformed domains and unresolved narrowing abstain. Fixed decay
retains min(float32(decay),1), including negative values. Synthetic derived
input names are local; underlying finite-input assumptions stay exposed.

Seventeen new controls cover time/audio coefficients, signed independent sites,
shared-site combination, offsets, image-driven coordinates, Q/fixed decay,
nonlinear/unbounded/singular/blur cases, upload overflow and domain premises.
191producer focused tests pass; independent review passed40feedback/value/point
controls with no actionable issues. No shader/equation/frame execution occurs.

The unchanged100source sample all retains structured descriptions and exact
byte/hash joins plus ZIP CRC.23have envelope models,77remain unknown. The union
with the earlier point model is still23: **zero new sample coverage**. This
feature is qualified on varying-weight controls, not credited as a real-sample
classification gain. Supported cases have14true/7false/2unknown sufficient
contraction results, all conditional colour-only facts.76fail affine colour
factorization;1lacks finite coefficient/offset bounds. These gaps prioritize
nonlinear colour and mixed/history paths rather than additional scalar weights.

Source-operation times total38.695619seconds, maximum2.350692seconds on this
host; no corpus/hardware guarantee. Native/preset/shared devices/full corpus
remain unchanged. Mood, full feedback and actual appearance remain unverified.
Census keeps exact names/hashes, per-site coefficient ranges and remaining gaps.

Raw paired archive: `build/preset-corpus/source-feedback-envelopes-2026-10-10/batch-000001.zip`.
SHA256bb185a6cf4e8640f5d945ef656ec045548b4bf72b2bc5a088bb7f2ba24fe714a.
Reader SHA256754e4f4129db585cb4f7d5bee915d6bb24ac10ab25901ee7ef0832ce50744afc.
Saved compile manifest file SHA25601e97e69283242d039ad2925e1845b41aa81a96418c758e12a086ca3a899e32f.
Latest release rechecked2.3.36/90b5bf9d, full AAR SHA256
 a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3.
Source34matches that math-source line; published-runtime qualification remains
independently pending. No visible persistence or mood accuracy is credited.

Final prepared suite: **2,705tests and92subtests pass in154.81seconds**.
Strict MkDocs and whitespace checks pass. These are source/interval-rule
checks, not actual persistence, appearance or mood certification.
