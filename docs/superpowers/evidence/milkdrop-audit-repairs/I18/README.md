# I18 — built-in wave RGB clamp

Candidate0028 clamps only the already converted local float RGB channels with the original six ordered comparisons, then uses the original nonzero brightening predicate. Raw frame RGB remains unchanged, including NaN/Infinity bits. Positive/negative brightening normalize the clamped finite producer. No geometry, sample count, opacity, styles, replay, draw, target or allocation is added by this arithmetic block. Darken predicates are unchanged; the separate negative-darken proposal remains outside the shipping series because it activates extra draws and additional NaN/−Infinity cases.

## Actual production GL proof

Baseline fails the independent RGB producer assertion. Candidate passes52/52 normal renderer controls and28-patch application. Tests observe actual constant authored/dot RGBA and both endpoint colors of every Native instance, not just the first buffer point. Across direct/replay, thin/thick/dots, ordinary/additive, three brighten values and alpha.0039/.0041/.5, raw frame bits stay identical and exact primitive/count/instance/style/geometry/submitted alpha signatures match an in-range control.159 smoothed points/158 segments and existing pass schedules are retained. Finite HDR/negative/dim/boundary RGB plus NaN in each channel and ±Infinity local-clamp cases execute through Waveform::Draw. Nonfinite pixels are not visual oracles. [RED](production-red.txt) · [GREEN](production-green.txt) · [Normal52](production-normal52.txt).

## Remaining qualification

Exact source candidates Geiss Artifact6d and suksma fame/arch-ass are recorded, not confirmed affected by rendering. Source-bound Android original/finite captures, actual black custom-shader palette proof, same-profile Native repeat/custom controls, clean cost and latest sanitizer/integration remain pending. No whole-corpus effect, zero-cost measurement or original Windows/D3D screenshot claim is made. [Candidate identities](stock-candidates.json) · [separate policy boundaries](REFINEMENT.md).
