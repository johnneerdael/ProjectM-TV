# Locked15: clear large-angle rotation control

![Upstream and our library: actual large-rotation UV frames](comparison.png)

The original EoS/Phat/PeterP/Sentinel/Aware witness assigns rot10000000. This
generated diagnostic uses that same angle and visualizes its warp UV coordinates
as red/green, with constant blue64. It removes the original's unrelated equation
rejection and dark artwork from the diagnostic; it does not edit the artist preset.

On the tested GPU, upstream's sine/cosine reduce the field to the rotation center:
every pixel is RGB128/128/64. Current preserves a rotated coordinate gradient.
Patch0011 computes sine/cosine on CPU after float conversion, reuses sine and
supplies cosine through its instance-owned vertex buffer.

Both current and current-minus0015 produce exactly the same120-frame sequence:
this positive-zoom control is preserved by the newly added negative-power patch.
All role/frame pixels retain blue64; upstream's center-collapse is independently
checked over all120 first-repeat frames. [Pixel checks](pixel-checks.json).
The [original dark-preset capture](../../0011-rotation.png) remains separate;
the [original rotation investigation](../../../large-rotation-trig/README.md)
provides direct UV/equation/prepared-replay controls.

Source main120547f3 is the locked15-patch endpoint. Three roles each run twice,
120frames,512×288, matched PCM/clock/seed, on the owned API36 GPU Android TV
emulator5630/M4 Pro/GLES3.0. All repeats are exact, with no GL errors or shader
warnings. Reconstruction, independent NDK canonical rebuild and all720 decoded
RGB frames verify: [results](results.json), [verification](verification.json),
[figure audit](figure-audit.json). [Diagnostic source](large-rotation-uv.milk).
Capture adjustments and original snapshots remain distinct; no Windows or
universal driver-failure claim is made. Complete streams/workers remain under
ignored build/patch-proof/locked15-large-rotation-v5 and current15-control-bound-workers-v1.

This replay uses the job-bound seed/input harness: inputs are retained, job paths
bind to the recorded owned workspace, and the validated job seed initializes
the worker RNGs. The exact validated worker is retained and uploaded with a
device-side hash check; verification rebuilds that retained binary and enforces
the trusted waveform, supported 16:9 dimensions and retained execution exits. All720 RGB frames match the preserved v1 capture; published
images and figure hashes remain unchanged. Original v1 streams/workers remain
available separately under their prior ignored build paths.

The refreshed worker manifest records normalized line/feedback setter controls;
verification binds those controls to the requested job and each compiled role.
Earlier producer variants remain preserved in their ignored build directories.

Comparison labels were rebuilt with the committed bitmap font. The separate
comparison_relabel record preserves the original capture identity and all
framebuffer bytes; refreshed verification records the trusted glyph/renderer hashes.
