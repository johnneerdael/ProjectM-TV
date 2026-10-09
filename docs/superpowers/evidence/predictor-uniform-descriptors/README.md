# Uniform final-expression reduction

This is a narrow opt-in numerical primitive on the predictor feature branch,
not an enabled corpus route or a whole-preset speed claim. No AAR, authored
preset, native device or other agent's corpus was changed.

`uniform_source_descriptors.uniform_expression_window` proves lane independence
of one lowered RGB expression under each explicitly supplied uniform input
binding. It rejects live UV, polar and interpolated diffuse inputs even if a
caller supplies a single query value or a declared default. Texture samples,
loops, effects, unknown operations, missing bindings and proof-budget exhaustion
remain unresolved. It executes the existing grid interpreter at one lane, then
applies the declared output clamp/UNORM8 policy and temporal descriptors.

The producer must separately establish selected custom-composite identity,
target compatibility, the complete final output, frame-dependent lowering,
actual equation/random/context bindings and any later display blit. The function
does not certify those premises or upstream rendering success. It does not
replace the maintained forecast or alter the corpus defaults.

## Numerical qualification

`UniformDescriptorStream` constructs no display/RGB frame. Small real-width rows
retain NumPy luma and saturation reduction behavior; zero-stride views retain
repeated mean rounding. Hue histograms and hue-change percentiles use weighted
four-lane NEON groups plus scalar-tail multiplicities. The implementation requires
OpenCV **5.0.0**, optimized ARM64/NEON dispatch; unqualified backends abstain.
The pinned test environment uses Python3.14.5 and NumPy2.5.3. Qualification does
not claim all future builds of those packages have identical numeric behavior.

The distinction is necessary because scalar hue330.0 and vector hue329.999969
can fall in different hard bins. OpenCV's
[5.0.0 RGB2HSV_f implementation](https://github.com/opencv/opencv/blob/5.0.0/modules/imgproc/src/color_hsv.simd.hpp)
contains separate SIMD and scalar-tail formulas. The exact two-colour regression
checks32×18/854×480 and nonmultiple-of-four query counts3×7/5×7. It also checks
matched query counts and sampled hue speed.

29 focused tests cover stored shader output against full fields, dead/live
spatial reads, resource/loop/missing-input abstention, declared spatial defaults,
random and dim supported colours, warmup/schedule rules, constant FFT nulls,
backend rejection, boolean thresholds, overflowed dt and nonfinite hue rates.
Counts, nulls and flags are exact; ordinary numeric comparisons use rtol2e-6,
atol2e-7. Independent review found the missing derivative/threshold validations;
red reproductions were saved and fixes rechecked. Unsupported optical-flow
values remain null, and warp displacement/geometry need their separate routes.

## Measurements

`measure.py` records a synthetic uniform time/bass shader over60 updates at15fps,
854×480. Three paired trials compare full shader-field construction plus the
existing descriptors with one-lane execution plus uniform descriptors. Parsing
is outside the timed window. The reports retain raw timings, exact source,
model/parser identities and backend. This excludes equation execution, warp,
feedback, geometry and complete preset qualification.

The same fixed100 exact source bytes from the earlier static review ZIP were
also parsed and lowered for a dependency-shape census, without numerical
shader/equation execution. **Zero uniform-binding candidates were found**:
85 spatial/resource/unproven,13 without an available parsed authored composite,
two unresolved lowering cases. Target compatibility was not supplied, so this
census certifies no automatic routes. These100 cases are retained; no rerolling.

This result limits the optimization's likely coverage. Broader gains require
safe reuse of shared shader work, spatial partitions or sound feedback/loop
invariants. Family recognition alone cannot replace final-output statistics.
Neither this census nor timing establishes visual accuracy or corpus speedup.

Local reproducible outputs: `build/preset-corpus/uniform-descriptors/`.
`benchmark.json`, `census.json` and the measurement script are stored beside this
document after the frozen bounded run finishes. No full-corpus render was started.
