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

## Clipping correction

The prototype implements a centered, headroom-limited version of candidate C.
For each integer-scale block and RGBA channel, subtract the detail band's
actual block mean, then choose one gain no larger than the requested alpha
that keeps every reconstructed pixel in [0,1]. A common gain preserves the
centered band's zero mean; independent per-pixel symmetric clamps do not.
Standard keeps its original fast path. No extra textures or render passes are
added, but Medium/High perform additional neighborhood reads in combine.

Run `python lab/check-combine.py --gles` from this directory, or pass the full
script path from the repository root. The test extracts the actual GLSL from
the prototype, links its ES 3.00 form and executes 39 GPU cases. Coverage
includes RGBA8 black/white headroom, unclamped float output range and block
means, bilinear reconstruction, retained sparse detail, and 32 frames of
colored feedback at scales 2 and 3. The original prototype fails on black at
Medium. Preset Lab CI runs this check under Mesa.

For full-preset comparisons, run from the repository root after installing
`tools/preset-lab/requirements.lock` and Preset Lab:

```bash
python docs/superpowers/evidence/0025-feedback-diffusion/detail-layer/lab/prepare-screen.py
python docs/superpowers/evidence/0025-feedback-diffusion/detail-layer/lab/screen-clipping.py --workers build/detail-clipping/screen/workers.json --out build/detail-clipping/broad --jobs 2
```

Add `--indices 3,38,40 --before --save-frames` for the three reported regressions, including
original Medium/High and an original Standard control. Workers, the prototype,
engine patches, capture instrumentation and generated PCM are hash-identified
in the output protocol. The original screen's PCM is unavailable; the new
screen uses a documented synthetic signal and does not replace the historical
JSON. Only eight frames are read/exported per job; all 480 engine frames run.
Worker checksums and the capture-frame contract are verified before rendering. Use fresh, empty `--work` and `--out` directories; existing data is not overwritten. A failed render, truncated output, failed PNG export or GL error fails the screen and cancels the other workers. Output and
local captures remain under ignored `build/`; preserve selected summaries and
comparison images with their protocol when recording evidence.

The owner accepted Standard's roughly 13% differences and the targeted
Medium result around 14.3%. Numerical likeness figures are diagnostics, not
hard gates: fix clipping-driven feedback bias and assess fidelity by the
original preset's character. Investigate residual brightness differences
separately after this fix. Device costs and the production port remain tasks
in the implementation plan; this evidence branch does not change APK/AAR code.

Recorded corrected-prototype results, source identities and temporal comparisons
are in `results/clipping-fix/README.md`. Run
`python docs/superpowers/evidence/0025-feedback-diffusion/detail-layer/lab/test-screen.py`
from the repository root for the eight runner failure/integrity regressions.
