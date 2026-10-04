# Authored code examples: predictions recorded before rendering

These are deliberate examples with mathematical answers, not part of the random
100-preset validation streak and not additions to the released Android library.
Both use a procedural composite shader with no texture sampling or framebuffer
feedback. A later renderer check validates these predictions; it does not generate them.

## Bass Pulse

A luminous cyan/blue ring and soft halo on a dark navy background. There is no
time-driven motion. Bass changes the ring's radius, thickness and tint immediately.

For `b = bass`, let `e = clamp(0.85*(b-0.8), 0, 1)`:

- Radius: `0.22 + 0.18*e`, in height-normalized UV distance: `p=(uv-0.5)*(width/height,1)`.
- Core half-thickness: `0.010 + 0.030*e`; another 0.010 distance softens its edge.
- Saturation starts at bass 0.8 and reaches the maximum near 1.97647.
- The tint moves from `(0.08, 0.62, 0.95)` toward `(0.65, 0.90, 1)`.
- The halo has a Gaussian falloff around the ring, `exp(-130*edge²)`.

This is a direct expansion/thickening response. The radius changes by 0.18;
the core half-thickness grows fourfold. At 1080p, the radius ranges from 237.6 to 432 pixels; the maximum ring diameter occupies 80% of the screen height. No hidden accumulated feedback causes it.

## Calm Drift

A soft, dim teal glow with broad diagonal brightness bands on a dark blue
background. The glow's centre drifts smoothly in two directions; the bands slide
slowly. The motion follows time, while smoothed bass makes only a small brightness change.

- Centre: `(0.12*sin(0.12*time), 0.10*sin(0.0852*time+2))`.
- Drift periods: approximately 52.36 s horizontally and 73.75 s vertically.
- Gaussian spatial envelope: `exp(-3.5*distance²)`.
- Bands: `0.75 + 0.25*sin(5*x + 3*y - 0.09*time)`.
- The bass term adds at most 0.018 to a baseline multiplier of 0.85, about a
  2.12% relative increase. It uses `bass_att` and has no on/off threshold.

Colour/position predictions are code-derived. Their exact pixel dimensions depend
on render aspect ratio; these equations state their coordinate units explicitly.
