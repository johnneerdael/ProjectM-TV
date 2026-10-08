# I18 — built-in wave RGB clamp

Candidate0028 clamps only the already converted local float RGB channels with the original six ordered comparisons, then uses the original nonzero brightening predicate. Raw frame RGB remains unchanged, including NaN/Infinity bits. Positive/negative brightening normalize the clamped finite producer. No geometry, sample count, opacity, styles, replay, draw, target or allocation is added by this arithmetic block. Darken predicates are unchanged; the separate negative-darken proposal remains outside the shipping series because it activates extra draws and additional NaN/−Infinity cases.

## Actual production GL proof

Baseline fails the independent RGB producer assertion. Candidate passes52/52 normal renderer controls and28-patch application. Tests observe actual constant authored/dot RGBA and both endpoint colors of every Native instance, not just the first buffer point. Across direct/replay, thin/thick/dots, ordinary/additive, three brighten values and alpha.0039/.0041/.5, raw frame bits stay identical and exact primitive/count/instance/style/geometry/submitted alpha signatures match an in-range control.159 smoothed points/158 segments and existing pass schedules are retained. Finite HDR/negative/dim/boundary RGB plus NaN in each channel and ±Infinity local-clamp cases execute through Waveform::Draw. Nonfinite pixels are not visual oracles. [RED](production-red.txt) · [GREEN](production-green.txt) · [Normal52](production-normal52.txt).

## Remaining qualification

Exact source candidates Geiss Artifact6d and suksma fame/arch-ass are recorded, not confirmed affected by rendering. Source-bound Android original/finite captures, actual black custom-shader palette proof, same-profile Native repeat/custom controls, clean cost and latest sanitizer/integration remain pending. No whole-corpus effect, zero-cost measurement or original Windows/D3D screenshot claim is made. [Candidate identities](stock-candidates.json) · [separate policy boundaries](REFINEMENT.md).

## Native observations and corrected expectation

Five initial finite controls complete20 Native4K runs with exact selected RGB repeats and an explicit constant-blue custom-warp proof: every no-wave shader-proof capture has meanRGB(0,0,64), so fallback cannot qualify. In-range RGB remains pixel-identical. Positive HDR brightening changes the submitted palette and final image as expected. Unbrightened HDR and negative-brighten HDR2/1/0 are pixel-identical on this RGBA8 backend. This contradicts the earlier proposed claim that raw2×alpha.5 would yield red1 while clamped1×alpha.5 yieldsred.5 in these actual targets; preserve the capture observation instead of asserting that blending premise. Source-stage color values still differ.

The first unchanged suksma fame candidate is selected-RGB identical; Geiss Artifact6d is weak(maxMAE.021011). The stronger unbrightened chemosynthetic nosferatu candidate also has exact unchanged selected images. Neither unbrightened original is claimed visually affected. Static HDR expressions are exposure, not impact.

Positive-brightening originals Geiss BlurMix3 and SkinDots10b complete8 additional Native4K runs with exact selected repeats, maxMAE2.587901 and.167054. [BlurMix3 before](original-Geiss---Blur-Mix-3-before-4k.png) · [source-corrected after](original-Geiss---Blur-Mix-3-after-4k.png) · [original results](brightened-original-results.json). Original palettes can become brighter/whiter because source clamp precedes normalization, with geometry and alpha unchanged. This is a source-defined palette correction, not a resolution-gain policy change.

DimRGB(.2,.1,.05) controls complete12 Native4K runs. Negative brighten before equals zero/unbrightened; negative after equals positive-brighten. Zero and positive remain unchanged across the patch. This is the actual nonzero-predicate visual proof: [before](dim--1-before-4k.png) · [after](dim--1-after-4k.png) · [results](dim-results.json). Current52/52 ASan/UBSan controls pass: [Sanitizer52](production-asan52.txt). Source-instrumented captures are not Windows images, all-frame hashes or a whole-corpus census. Clean cost remains active.

## Focused cost and disposition

Twelve isolated ABBA Geiss BlurMix3 runs give mean2.036141ms before versus1.923487ms after (−.112653ms/−5.533%). Cycle changes−12.303%,+2.174%,−7.604% show variability; no consistent slowdown is observed and no universal speedup is claimed. All timing-run selected RGB matches the original witness by role. [Cost results](cost-results.json) · [full log](clean-timings.txt).

Retain RGB-only0028 after actual source/submission52, sanitizer52, compiled blue-background proof, unchanged in-range/unbrightened controls, original positive-brightening palette and negative dim-brightening Native4K proof, and focused cost qualification. No alpha, width, geometry, sample density, targets or replay equations are changed. Negative-darken activation stays outside this repair. Final combined integration/CI remains open.
