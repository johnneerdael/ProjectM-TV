# Patch0014: independent legacy tint controls

![Actual matched legacy tint control frames](comparison.png)

These are generated diagnostic presets, not artist presets. A full-screen opaque
shape supplies constant RGB64/128/192, waveform alpha is zero, gamma is one and
echo is off. The three sources differ only in `fShader`: zero,0.5 or1. All panels
are actual unmodified512×288 frame119, with the same input and clock.

At the center pixel, upstream/current-minus0014 give `(49,128,156)` for all three
amounts: the legacy path applies full animated shade regardless of the authored
setting. Current gives `(64,128,192)` at zero, `(56,128,174)` at half, and
`(49,128,156)` at full. The changed color is exactly the requested tint amount,
not a brightness adjustment to the screenshots.

An independent [complete-pixel oracle](pixel-oracle.json) checks every pixel of
all120 first-repeat frames in each configuration/role. With current zero tint,
all bytes equal the known input. Half tint is halfway between input and current
full tint: maximum `abs(2*half-input-full)` is1 RGB byte (allowed2). Full tint
matches both baseline roles within1 byte; their zero/half outputs remain full
shade within1 byte. This separates disabled/fractional tint correction from
preservation of full tint and from the mode-1 waveform change.

Each configuration has two exact120-frame repeats per role, no GL errors and no
shader warnings/errors. Source reconstruction, NDK rebuilt/canonical executable
comparison and all2160 decoded RGB frames verify against the selected14-patch
snapshot `41ec3fc1`. Receipts: [zero](zero-verification.json),
[half](half-verification.json), [full](full-verification.json),
[figure/frame hashes](figure-audit.json). Sources and per-role raw PNGs are kept
beside their result JSON. Workers/complete streams remain under ignored
`build/patch-proof/current14-workers-v1` and `legacy14-hue-{zero,half,full}-v2`.

The initial zero fixture used `shape_0_` instead of the preset reader's
`shapecode_0_` configuration prefix and rendered black in every role. It is
[recorded and excluded](excluded-initial-control.json); no tint-proof credit
comes from that inactive attempt. Version2 changes only the prefix and preserves
the initial source/results separately.

This is GPU TV evidence from the owned API36 emulator5630/M4 Pro/GLES3.0.
Shared deterministic hooks, upstream GLES admission and current/control binary
cache-export suppression are explicit. It is not a Windows/MilkDrop frame.
