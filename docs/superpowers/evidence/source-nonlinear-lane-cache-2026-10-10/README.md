# Nonlinear colour lane cache identity repair

Review reproduced a predictor determinism bug using the unchanged authored
control GetPixel(float2(ang,1/rad)). Serial and independent threaded calls
could export different sampled-channel domains and record hashes. A canonical
swizzle was a temporary Field, memoized by its Python ID without retaining it.
After collection, another lane could reuse that ID and retrieve the old lane.

The cache now keys the original input node and retains (original,value) entries.
Canonicalized temporary swizzles do not supply cache identity. The regression
asserts exact x/y/z declared domains over12threaded/repeated calls; the existing
independent-call record-isolation test also passes. No native engine, preset or
AAR is changed. This is a predictor bug, not an observed renderer defect.

Both failures were captured before the repair:
- build/preset-corpus/nonlinear-canonical-cache-red.log
- build/preset-corpus/nonlinear-canonical-lanes-red.log

Focused nonlinear/effect-family suite:99tests pass in5.12seconds.
Subsequent band/forms/family/nonlinear suite:142tests pass in6.21seconds.
Historical exports remain preserved. Their lane attribution was not reliable;
a fresh exact fixed-sample export will supersede them for current qualification.
This evidence does not certify full appearance, numerical native performance
or calibrated moods. Whitespace checks pass.
