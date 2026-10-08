# I08 — Centered custom-wave input windows

Candidate patch0017 restores valid original oscilloscope windows without restoring the out-of-bounds behavior repaired upstream. Native 4K captures/timings and final integration gates remain pending.

MilkDrop2 `milkdropfs.cpp:2643–2654` starts the left/right oscilloscope channels at `(480-nSamples)/2 ∓ sep/2`, using signed integer division. The original copies static `samples` directly into the wave-frame context at line2545; the earlier subtraction at line2606 is overwritten by line2631 and does not determine the final point count. The current library’s prefix sampling starts both channels at0 and ignores oscilloscope separation.

The candidate applies centered offsets only when both complete windows fit the480 input samples. Oversized requests retain upstream resampling, invalid original offsets retain the safe prefix behavior, and spectrum behavior remains unchanged. Sample counts, smoothing coefficients, scales, rendered styles and prepared Native replay remain unchanged. No new sample, equation evaluation, render pass or texture is added.

The real-EEL/GL regression fails before on a finite two-point480-sample ramp: first value1 is0 rather than239/480×.004=.0019916667. It passes after for centered windows, positive/negative separation, large valid separation, full480 windows, preserved512-sample resampling, invalid-separation fallback and spectrum. Point counters verify that dual-target replay evaluates each point only once and restores the authored context. The existing bounds regression’s two-point expected endpoint is updated from prefix index1 to centered index240 (.96 with its unnormalized ramp); all unsafe/count/endpoint assertions remain intact.

The handoff supplies508 conditional candidates. No affected original is credited yet. Prefer an unchanged enabled small oscilloscope whose point equations actually consume value1/value2: `Mig_304 - geiss remix 2.milk` uses152 samples and sep8 directly in position and colour; `shifter - ice ripples.milk` uses22 samples in border injection alpha. Short-sample geometric waves that overwrite positions and ignore both values may be lexical false positives.

The candidate requires a matched Native Standard4K before/after replay with exact audio/clock/seed and capture repeats, plus no observed slowdown in the selected witness. These captures will represent source-corrected TV input semantics within the retained Native policy, not original Windows/D3D output. I19’s separate sample-cap hypothesis is absent from this candidate’s shipping series.
