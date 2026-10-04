# Per-frame record compatibility probe

The unmodified161/430 per-frame programs fail at their split `is_beat` token
with projectM's inserted newlines. Both compile after the MilkDrop expression
preprocessing step removes record breaks and line comments. This strengthens the
cause identified by the four actual-core physical failures.

The [pinned MilkDrop source](https://github.com/WACUP/vis_milk2/blob/50cbd69c69497f22baa521066e04ee05d5940ea4/vis_milk2/state.cpp#L1530)
removes linefeed control characters; its comment says “replaces … with a space,”
but the function body does not insert a space. The probe follows the body.

This is a compiler component probe, not a substitute backend for the corpus.
No preset bytes, APKs, production expressions or live baseline inputs changed.
`results.json` identifies exact inputs, source and linked evaluator library.

Reproduce against the completed host-suite evaluator:

```sh
clang++ -std=c++17 -I third_party/projectm/vendor/projectm-eval/projectm-eval/api \
  docs/superpowers/evidence/quad-follow-up-verification/core-corpus/diagnostic-presets/compiler-probe/probe.cpp \
  build/follow-ups/core-initial-history-review/host-suite/build/vendor/projectm-eval/projectm-eval/libprojectM_evald.a \
  -o build/follow-ups/per-frame-compatibility/probe
build/follow-ups/per-frame-compatibility/probe docs/superpowers/evidence/quad-follow-up-verification/core-corpus/diagnostic-presets/compiler-probe/161.eel
build/follow-ups/per-frame-compatibility/probe docs/superpowers/evidence/quad-follow-up-verification/core-corpus/diagnostic-presets/compiler-probe/430.eel
```

Next, use original compilation first and retry the MilkDrop-compatible joining
only if that fails, scoped to per-frame expressions. Prove healthy programs keep
the original path and genuinely invalid code still fails. A real-core candidate
APK and corpus comparison remain required before claiming the presets work.
