# Physical framebuffer blit qualification

This is a numerical GPU operator proof for the unchanged full published v2.3.27 AAR, separate from an actual core transition or preset render. The bound published classes and native library are unchanged. The private helper kept the core preset-frame serial at zero.

The source framebuffer is RGBA8 at 1920×1080 and the destination is a 3840×2160 default RGBA8 pbuffer with no multisampling. Two runs of gradients, one-pixel stripes and clamped edges match every pre-frozen source-predicted RGBA8 sample with zero error. No image inspection, model changes or randomized/streak credit was used.

The declared source operator computes float32 pixel-centre UVs, the qualified Apple fixed8/fraction4 linear samples, then storage rounding of the represented float32 value. A separately frozen exact-rational quarter-weight/RNE calculation differs on the gradient by one byte at 2,108,068 samples; this records conversion-order sensitivity rather than a universal GPU halfway-rounding rule.

See `proof-summary.json`, `freeze.json`, `results.json` and `repeat-verification.json`. Raw arrays remain at the recorded build artifact location; their hashes are copied here. `java-reproduction-verification.json` binds the operator helper to the full published AAR.

The public JNI has no forced render-scale setter. Auto transitions begin at 75% or 60% and can adapt to 50%; a faithful 1920×1080→3840×2160 core transition witness requires its own frozen two-preset/history/time inputs and observed scale. None was executed here.
