# Live native controls — live-controls-v1

Patches 0048–0049 repair the built-in waveform and legacy display paths. The
original evidence bundles dated 2026-10-06 remain unchanged in Downloads.
All seven affected source hashes match the supplied 44-patch identities on
current main (47 patches). The downloaded published 2.3.11 AAR matches
`3bc37560a87000ec7ac446895fee8ad09e93b5c83a601014b5fc396bd1f3e6d6`; its ARM64
library matches `8bb82903af3825e16b734ceddf7316ba83da43509fb3fa3614537749a5c124f0`
(the exact verified library identity is recorded in the validation manifest).

The existing 23 native regressions passed before modification. New regressions
failed before the repair: dynamic dots produced different pixels from static
dots, and equation-only darken did not produce the independently predicted
squared colour. After the repair, all three focused controls pass on macOS
OpenGL with ASan/UBSan. Android debug APK/core and debug JVM tests also pass.

`dynamic-wave-controls` checks all 16 modes and mode switches, truncation,
positive wrap, negative/undefined input handling, dots, thickness and blending
against fresh static controls. It compares draw counts/primitives/blend state
and rendered pixels on GL-line, quad-line and paired authored/native targets.
`dynamic-display-controls` uses a known constant surface to independently
predict each filter and their order, including defaults off and return to off.
Gamma/echo cases compare unchanged static branches, fractional gamma redraws,
the echo threshold, zoom and all orientations. Conditional equations verify
frame reset defaults. `dynamic-original-presets` checks original hashes at
configure time, equation compilation, selected composite path and full draws
for 319, Hexcollie's wormhole2 and idiot's Forty Six and 2 under declared
synthetic audio and clocks in Off/Standard/Medium/High detail paths. These
controls are source/native evidence, not a Windows visual comparison.

The user waived physical-TV checks and requested a dedicated emulator on the
Metal M4 GPU. Emulator results and captures will be recorded here before the
PR is ready. No shared corpus, shared devices or preset files are modified;
no full-corpus render is run. No performance or affected-preset-count claim
follows from the candidate inventories (45 waveform, 647 broad display).
Historical predictor policy, collection scores and audits remain unchanged.
