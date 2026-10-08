# I17 — Built-in waveform opacity

Candidate patch0016 is implemented; Native 4K appearance/timing acceptance and final integration gates remain open.

Both MilkDrop 2 reference files have SHA256 `68749d31bb6b3020ca89b1e7630fd704e58a5de8dd6275c9f5ea005c6586a7d9`. Lines2882–2995 multiply mode-adjusted alpha by an unbounded volume ramp, replace mode3 alpha with the size coefficient, and clamp only the final result. Lines3315–3317 skip final alpha below .004. MilkDrop3 remains a separate source reference.

Current baseline15 TV patches retain projectM’s volume function, which replaces mode attenuation with `wave_a` and saturates the ramp prematurely. Mode3 also multiplies `wave_a` where the original replaces it. These operations coexist with useful TV size buckets and Native line/dot compensation; those policies are preserved.

| Control | Baseline | Source expectation / candidate |
|---|---:|---:|
| Mode2, alpha .8, vol .85, bounds .75/.95, matched256 canvas | .4 | .028 |
| Circle, alpha .1, vol2.2, bounds .75/.95 | .1 | .725 |
| Mode3, alpha .5, treble1, matched256 canvas | .04875 | .0975 |
| Mode1, alpha .003, no modulation | Draw .00375 | Skip below .004 |

The new real-GL attribute regression fails baseline on the first row and passes candidate. It also checks mode3 with authored alpha0, above-bound amplification, below-bound suppression, clamp, nonmodulated attenuation, and threshold boundaries. In float arithmetic `.0032f × 1.25f` is slightly below `.004f`; the exact threshold test uses mode0 alpha `.004f`. Native quad attribute checks use a3840×2160 render context and1024×768 reference, preserving its distinct coefficients. These checks are stage evidence, not full-resolution output screenshots.

All38 normal renderer controls pass after the candidate; all37 pre-existing sanitizer controls pass at baseline with the new test failing as expected. All16 patches apply to a clean pinned export. Test logs are linked alongside this file. Further sanitizer/host/JVM/Android/docs validation remains required.

The static handoff supplies5,300 conditional candidates. No affected original is yet credited. `Happening.milk` is selected for the first unchanged-original replay because it uses mode2 with volume modulation and no custom waveform/shape/shader layers. Its expected corrected appearance has fainter newly injected dots while retaining Native dot sizing and authored feedback; the exact visibility depends on the actual audio volume.

No pass, texture, sample or repeated equation evaluation is added. Threshold suppression can remove work, but a no-performance-regression claim requires matched Native 4K timings. Captures must compare baseline15 and candidate16 under the same PCM, seed, clock and Native Standard state. They represent source-corrected TV output, not original Windows/D3D screenshots.

The source predictor in the separate predictor worktree still models the baseline behavior. Its historical identity is preserved; it cannot claim agreement with candidate16 until its versioned opacity contract is updated and qualified.
