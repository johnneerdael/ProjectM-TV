# I22 — Discrete custom dots

Candidate patch0018 passes the source-stage regressions and40 normal renderer controls. Native4K captures/timings and final integration remain pending.

MilkDrop2 `milkdropfs.cpp:2722–2726` smooths custom waves only when dots are off. The baseline library always smooths, turning two finite authored points(.25,.5)/(.75,.5) into three submitted points including a midpoint. Candidate0018 submits only authored dot points, preserving maximum buffer capacity, point/color ordering, Native dot styles and prepared replay. Ordinary line smoothing remains2N−1 and Native quads retain their smoothed segment count.

Original line2634 also permits one custom dot. Its normalized `sample` input is0/0, so the candidate preserves it as NaN rather than inventing0. A point program that overwrites position/color independently of that input can render a finite authored point. The real-EEL/GL test traces NaN while emitting the independently finite point; all0/1/2-dot, thick/thin and line cases are covered. Invalid geometry or color derived from NaN remains an unsupported appearance domain, not a claimed portable original render. No raw/nonfinite equation value is repaired silently.

The new draw-hook regression fails before on the interpolated two-point midpoint and passes after. It reads actual submitted VBO endpoints, counts authored/native draws, verifies one execution per point and checks line smoothing plus empty/single-line suppression. No test-only code is added to production.

The handoff supplies1,875 lexical candidates. No original is credited before runtime. Primary unchanged witness: **shifter - mosaic mitosis.milk**, SHA256 `8a9c95567882bf3fd2644e28cb2e0067b62f52b38cb9d10cc4ada34c90710419`. Its enabled custom wave1 has12 dots and point code folding time-driven sine positions, adding random jitter and randomized alpha. Before smoothing submits23 dots; original source expects12. Point RNG is consumed only for the12 authored points in both roles, and must remain frozen. Source-corrected appearance removes the11 unauthored particles while preserving the true particle positions. The other waveform/shape/feedback components are kept intact.

Expected performance: existing two-or-more-point dots avoid interpolation and submit fewer vertices; supported single-dot programs now perform their missing authored evaluation/draw. Neither path adds a render target or Native replay evaluation. Native4K timings remain required, and no whole-corpus or physical-TV claim is established by the stage controls.
