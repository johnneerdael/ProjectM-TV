# Patch0014: isolated mode-1 spiral control

![Matched generated mode-1 frames and source-pixel close-ups](comparison.png)

This labeled generated preset sets mode1, waveform alpha0.4, no volume modulation,
no feedback persistence, no custom shapes and full legacy tint (`fShader=1`). The
three roles receive the same PCM, seed and frame clock. Full tint preserves the
old hue path, isolating the waveform portion of0014 from its tint correction.

**Visible difference:** the source-pixel close-up shows the extra line connecting
the spiral's ends in upstream/current-minus0014. Current removes that closing
segment and changes intensity according to the mode-1 alpha rule. The crop
`(189,118,271,193)` is enlarged5× with nearest sampling; source RGB is unchanged.
At frame119,85 previously covered pixels become black and3 become covered;
peak RGB changes from124/82/13 to145/96/15. These are scoped rendered observations,
not a uniform25% brightness claim.

**Code cause:** `XYOscillationSpiral::IsLoop()` returns false after0014, selecting
an open line strip. `Waveform::Draw()` multiplies mode-1 alpha by1.25 before its
final clamp:0.4 becomes0.5 here. Final shade, blend overlaps and quantization mean
that framebuffer intensity is not a direct measurement of that alpha value.
Independent actual GL attribute/topology controls remain in the
[original PR57 investigation](../../../brainstain-dark-output/README.md).

All three roles have two exact120-frame repeats, zero GL errors and no shader
warnings/errors on the owned GPU Android TV emulator5630/M4 Pro/GLES3.0. The
current14-patch source is `41ec3fc1`. Source reconstruction, independent NDK
rebuild/canonical executable comparison and all720 decoded RGB frames pass:
[results](results.json), [verification](verification.json),
[raw frame/crop audit](figure-audit.json). Complete streams/workers remain under
ignored `build/patch-proof/legacy14-mode1-v1` and `current14-workers-v1`.
The source is retained as [legacy-mode1-spiral.milk](legacy-mode1-spiral.milk).
These are controlled GPU frames, not an unchanged artist or Windows render.
