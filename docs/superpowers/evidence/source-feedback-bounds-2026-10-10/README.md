# Conditional source feedback colour bounds

`feedback_transfer.colour_bounds` derives raw per-channel intervals from known
affine previous-main sample coefficients and constant bias. Its explicit input
premise is independent sampledRGB in[0,1]. Signed coefficients use separate
lower/upper sums; different sampling sites cannot cancel into a false small
gain. The existing absolute row sum is an infinity-norm difference bound with
coordinates and non-image inputs held fixed.

For an image-independent, nonexpansive sampler and identical external inputs,
a gain below1 supplies a sufficient contraction bound for this nominal
colour-only operator. Positive gain below1 also supplies an ideal perturbation
half-life upper bound, including signed/channel-mixed or multi-copy operators.
Zero gain gets no artificial finite half-life. A gain at/above1 only fails this
sufficient condition; it does not prove actual amplification or instability.
Image-dependent or unknown coordinates retain unknown contraction.

Bounds exclude shader float32 rounding, storage quantization, drawings,
blend/detail/blur and discard feedback. Actual feedback stability, visible
flashing and mood remain unverified. Nominal raw intervals are not final pixel
colours or whole-preset brightness estimates.

Ten test-first controls cover fixed decay, multiple/signed copies, independent
perturbations, per-channel mixing, negative/large/zero gains, image-dependent
coordinates and nonlinear abstention. The producer passed154focused controls;
independent review passed167and found no source-math issue. Its clarification
about shader rounding was added to the exported conditions and documentation.
The prepared full suite passes2,412 tests and92subtests in143.80s. Strict
MkDocs and whitespace checks pass; these remain source-math checkpoints.

The same fixed100 original sources all export with the explicit source34 reader.
Twenty-two have RGB envelopes, thirteen have a sufficient conditional colour
contraction bound, and eleven have ideal perturbation half-life bounds. One
half-life bound is newly available beyond the previous scalar case. These
overlapping counts measure ingredient coverage, not mood/appearance accuracy.
`census.json` keeps source/model/parser hashes and the per-preset values.

Raw paired batch:
`build/preset-corpus/source-feedback-bounds-2026-10-10/batch-000001.zip`,
SHA256 `8f7e86558885c378f7c404a00f31f399c4b36113ba879445d7c7e3f47ac58964`.
ZIP CRC and original source-byte joins match the preceding fixed sample.

No engine/preset code, device or full numerical corpus was changed or operated.
Source34 is opt-in and distinct from unchanged-AAR runtime qualification;
the default remains source31/published33 while that runtime gate is pending.
