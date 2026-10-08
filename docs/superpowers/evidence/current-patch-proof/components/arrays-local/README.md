# Local flat-array shader control

![Upstream/current-minus0002 fallback and current local-array shader](comparison.png)

This is an explicitly generated [diagnostic preset](flat-local.milk), not an
unchanged artist preset. Its composite declares
`float2 taps[2] = {0.25, 0.5, 0.75, 1.0}` inside the shader function, then uses
the two vector elements to produce the colour gradient.

Upstream and current-minus0002 reject the incorrect scalar-to-vector array
constructor and use a generic fallback that shows the red input shape. Current
groups the four scalars into two `float2` elements and runs the authored gradient.
This independently exercises local flat layout; the Quicksand original exercises
global flat layout and whole-array assignment.

The frame panels contain unaltered actual GPU output at512×288. All three roles
repeat all120 RGB frames exactly in two fresh processes with zero GL-error frames.
Source reconstruction, canonical NDK executable comparison and complete decoded
stream verification pass. Shader compiler/fallback logs are preserved alongside
the successful-render status: [results](results.json), [verification](verification.json),
[frame/figure audit](figure-audit.json). No MilkDrop GPU reference is claimed.
