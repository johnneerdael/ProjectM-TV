# Feedback detail layer: prototype and evidence (2026-10-05)

Implementation plan: `docs/superpowers/plans/2026-10-05-native-4k-feedback-detail-layer.md`.

| Path | What it is |
|---|---|
| `detail-layer-prototype.diff` | Prototype against main's projectM engine (series 0001–0041, preset-lab instrumented). Apply with `patch -p1` in the engine root. Contains debug code and env switches (`PM_DETAIL=<alpha>`), not for shipping |
| `lab/one.py`, `lab/broad-dl.py`, `lab/broaddl-sum.py` | Host render of one preset; 68-preset screen with a per-config reference; summary of the old-engine screen |
| `results/broad-main/` | 68-preset screen on main's engine: authored 1182 and 1280, main at 4K, detail α 0 and 1 at 4K (per-preset JSON: luma ratio, MAE, contrast) |
| `results/broad-dl-oldengine/` | Earlier 68-preset screen on the pre-0036 lab engine (α 0, 0.5, footprint), kept for the record |
| `results/gallery-six-presets.json` | Numbers behind the six-preset comparison page |
| `results/shield-matrix.log` | SHIELD offscreen frame times, two rounds (the "Segmentation fault" lines are process-exit crashes after the timing was printed) |
| `pmbench/bench.cpp`, `CMakeLists.txt`, `matrix.sh` | Android offscreen engine benchmark (EGL pbuffer, RGBA8 FBO, glFinish per frame) |
| `pmbench/gpubench.cpp`, `*.frag` | Per-pass GPU micro-benchmark (alternating FBOs + glFlush against Mali forward pixel kill) |

Unpatched libprojectM 4.1.7 renders to framebuffer 0. For `-DUPSTREAM=ON` the lab engine's `ProjectM.cpp` was changed to bind `libprojectM::lab_target_fbo` (defined there, default 0) instead of 0 after the preset renders; `bench.cpp` sets it to its FBO. Upstream also lacks `SetLineReferenceSize`, which `bench.cpp` skips under `PMBENCH_UPSTREAM`.
