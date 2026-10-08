# Current4.2 high-resolution reference-line comparison

![Upstream, our classic-line control and our reference-sized lines at4K](comparison-4k.png)

Unchanged bundled preset: `Geiss - 3D - Shockwaves.milk`. Actual GPU library
framebuffers are 3840×2160 on the task-owned API36 Android TV emulator. All three
configurations use the same preset bytes, textures, synthetic PCM, seed12345,
frame/30 clock and mesh48×32. Each has two exact120-frame RGB repeats and zero GL
errors, with no shader warnings/errors. Source reconstruction and canonical
NDK27.3.13750724 executable rebuild checks pass. Complete lossless gzip streams
remain in the private build directory; the verifier checks their decoded bytes.

**What to look for:** upstream's thin loops and feedback trails are dimmer.
Our library with classic lines looks nearly identical to upstream. Enabling the
1920×1080 reference-size path retains broader, brighter rings and trails at4K.
This is the high-resolution enhancement relevant to [upstream #682](https://github.com/projectM-visualizer/projectm/issues/682),
not a claim that fixed-width MilkDrop lines violate their original behavior.

**Why it changes:** fixed1px strokes cover less of a4K image. The enabled path
uses a2× line scale for this render/reference area ratio and retains the
associated reference-size sampling/feedback policy. It is not an image-brightening
operation applied to the screenshots. The reference policy includes more than
line geometry alone; these panels do not isolate AA or every reference-policy
subcomponent. Optional AA is disabled in this case.

At frame119, upstream versus our classic control has RGB8 MAE0.005962; our classic
control versus the enabled reference path has MAE19.675516. The controls distinguish
the enabled host feature from the rest of the current patch series. These are
sampled image differences, not TV performance or universal appearance results.

The overview is the same4× BOX reduction for every panel, with an annotated crop
rectangle. Below it is the same360×360 source crop enlarged2× by nearest-neighbour;
no gain, normalization or colour edit is used. The full-resolution PNGs remain
available: [upstream](upstream.png), [our classic control](our-classic-control.png),
[our enabled reference path](our-reference-lines.png).
[Figure/input/binary audit](figure-audit.json).

Capture receipts and independent verification:

- [Upstream/current reference-path runs](lines-geiss-4k-v1-results.json),
  [verification](lines-geiss-4k-v1-verification.json).
- [Current classic-control runs](lines-geiss-classic-4k-v1-results.json),
  [verification](lines-geiss-classic-4k-v1-verification.json).

The sources use the common deterministic instrumentation and explicit capture
adjustments documented in the parent evidence. These are direct-source EGL
library captures, not production AAR/JNI or original Windows MilkDrop renders.
