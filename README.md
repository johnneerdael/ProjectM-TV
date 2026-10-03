# Evidence for PR #14: quad lines that scale with the render size

This branch holds the images and measurements behind each change in
[PR #14](https://github.com/johnneerdael/ProjectM-TV/pull/14) (projectM issue #682). It is an orphan branch and is never merged.
Each PR comment titled "Evidence: …" embeds the images listed here.

- `img/<fix>/`: images. JPEG q82, at most 1600 px wide; small zoomed crops are PNG.
- `data/<fix>/`: measurements as JSON. Local paths and device-specific details are removed; the numbers are unchanged.

## Shared method

- **Renderer.** Desktop renders use the repo's `preset-lab` worker (desktop OpenGL), built from the projectM 4.1.7 patch series. Each
  build is named below by commit, or as a prototype patch when it was tested before it was committed.
- **Input.** `bass_signals` "bass-0.30" PCM (seed 12345) at 30 fps. Both images in a pair use the same clock and seeds, so they
  show the same moment.
- **Mean luma.** The mean over the measured frames of Rec.709 luma / 255 per pixel, usually a 4 s window after a 4 s warm-up. A
  ratio compares it with a reference render.
- **Authored look.** Classic 1 px GL lines at 1182×665, the 16:9 size with the area of MilkDrop's 1024×768.
- **Render sizes.** preset-lab renders at the size the job asks for. The app's 1330 render-height cap (fix 8) is applied in the app,
  so lab "4K" renders really are 3840×2160.
- **TV.** Ugoos AM6 (Amlogic S922X, Mali-G52 MP6, Android 9) on a 3840×2160 panel.
  - Settings: `render_height` 2160 and a 60 fps cap in both apps.
  - The preset is pinned with a debug property.
  - fps is the mean of the app's 1 s STATS lines from 25 s to about 90 s after launch.
  - Runs alternate between the release app 2.1.4 and the PR build.

## 1. The issue: line share across resolutions (`1-line-share`)

- **Images:**
  - `royal-mashup-103-…jpg` and `serge-circles005b-…jpg`: top row old GL lines, bottom row quad lines, at 480 | 1080 | 4K, each
    labelled with its mean luma.
  - `synthetic-thin-line-crops.png`: a thin main wave without feedback. The same picture area at the three heights, nearest-neighbour.
- **Build:** worker from patch 0021 at `31b8cbf` (the LineScale clamp). The reference then was a height of 1080, so lines were 1 px at
  1080 and 2 px at 4K. The 4K tiles come from the previous ladder run, because the clamp changes nothing at scale 2.
- **Final build:** the reference is now 1024×768, so lines are 1.62 px at 1080 and 3.25 px at 4K. The principle is the same: above
  the reference, lines keep a constant share of the picture.
- **Data:**
  - `ladder-final-results.json`: synthetic share table and real presets.
  - `ladder-results.json`: the first ladder, whose synthetic section A has the old 4K ÷ 480 = 0.222.

## 2. Thick main wave as MilkDrop's four passes (`2-thick-main-wave`)

- **Images:**
  - `$$$ Royal - Mashup (191).milk` at 1920×1080, last frame of the same run: GL lines | two slope bands (`84c7050`) | four offset
    passes (`493e173`).
  - The same three as a 520×300 centre crop at 100 %.
- **Build:** preset-lab `line-compare` runs `simplify-head` (`84c7050`) and `simplify-a` (`493e173`), reference 1920×1080
  (`line_reference_height` 1080). These are existing frames; nothing was rendered for this branch. The GL-lines frame is
  byte-identical in both runs.
- **Final build:** the four-pass drawing is unchanged. The reference is now 1024×768.
- **Data:** `thick-main-wave.json`. It holds the synthetic ratios (±0.13 %), the fixed-list medians and the two runs' entries for 191
  and Serge 158 002.

## 3. Dots in whole pixels (`3-dots`), data only

- **Data:** `dots.json`. Measured on synthetic presets without feedback (`geo-dots.py`):
  - before `4fc2eea`: 0.25 at 720, against an expected 0.444;
  - after: 0.443–0.459 at 720 and 0.998–1.001 at 1080.
- **Images:** none. No before image was kept, and the existing dot crops miss the dots.

## 4. Waveform sample-count rule (`4-sample-count`)

- **Images:**
  - `mashup103-fix.jpg`: authored 1024×768 | quad @1080 before | after | quad @4K before | after. Top row is the preset as
    bundled; bottom row is its wave drawn as lines.
  - `mashup103-ablation.jpg`: which element drives the wash-out.
- **Build:** prototype `0021-quad-lines.sample-width.patch` on 0021 with reference 1024×768. Commit `9aae5ab` is the same rule and
  reports the same numbers (0.21 at 1080, 0.23 at 2160).
- **Data:** `mashup103-ablation.json`.

## 5. Blur textures follow the reference (`5-blur`)

- **Images:** Nuclear and fat cancer tour: authored 1182×665 | 4K with blur at render size | 4K with blur at the reference size.
  Labels are luma ratios against the authored render.
- **Build:** legacy-audit prototype variants `base` (103 fix) and `blur`. The final commit `1cdb714` is frame-identical to the
  prototype on all 18 presets.
- **Data:** `blur.json`. It has the per-preset ratios and the TV runs at native 4K: release 2.1.4 against the PR build at
  `1cdb714`/`58d437f`, no music.

## 6. MaximizeColors follows the reference (`6-maximize-colors`), data only

- **Data:** `maximize-colors.json`. Only 1 of 18 presets changes frames (Fvese-mvfun2), and its luma does not change.
- **Images:** none, because there is no visible difference to show.

## 7. Virtual `texsize` (`7-virtual-texsize`)

- **Images:** authored 1182×665 | 4K with the real texsize | 4K with the virtual texsize, for:
  - sawtooth grin;
  - penattrition;
  - Serge circles005b;
  - LuxXx Growing Alien Organs, a preset that gets **worse**.
- **Build:** texsize-research prototypes `bmc` (103 fix + MaximizeColors + blur) and `vt`. The final commit `272fd61` implements `vt`.
- **Data:**
  - `virtual-texsize-results.json`: 97 presets. Within ±10 % of authored: 77 → 84 at 1080 and 60 → 72 at 4K.
  - `texsize-census-summary.json`: the census summary.

## 8. Render height cap 1330 (`8-render-cap`)

- **Images:**
  - Per preset: authored 1182×665 | native 3840×2160 (before) | 2364×1330 with virtual texsize, upscaled to 4K (after), for Acid
    Mandala v1c, Serge circles005b, Flexi alien complex 03 and Royal Mashup 191 (**worse**).
  - `acid-mandala-v1c-centre-crop-4k-scale.jpg`: a 960×540 centre crop at 4K pixel scale.
  - `acid-mandala-resolution-ladder.jpg`: the mechanism, from authored through 1080, 2× and 4K to 4K with reference diffusion.
- **Build:** before = 0021 at `4a5606b`, native 4K. After = 0021 at `272fd61`, rendered at 2364×1330 (cap commit `3ad22b2`). This is
  the final build; `eaa5f4a` only changes docs.
- **Data:**
  - `render-cap-results.json`: 24 presets with img_err, luma and sharpness, plus the 1260/1330/1440 comparison.
  - The TV runs are in `10-tv/final-capped-vs-release.json`.

## 9. Joints (`9-joints`)

- **Images:**
  - Heater Core C custom wave 0 isolated (white, alpha 0.4, one frame) at **10 px**, zoomed 3×: this patch's miter joins against
    the same polyline as separate per-segment quads (simulated). Red dots mark the strip points.
  - The simulated per-segment frame.
  - A hairpin cusp, compared across GL lines 1 px, this patch and per-segment quads.
- **Build:** worker at `84c7050` (the 10 px and 5 px widths use reference heights 108 and 216). The join geometry has not changed
  since then.
- **Data:** `heater-core-joints.json`. At 10 px there are 2 double-blended joint pixels per frame against 3,535 for per-segment quads.

## 10. TV, Ugoos AM6 (`10-tv`)

- **Images:** device screencaps at about 20 s, release 2.1.4 | PR build at `d9894a4` (quad lines with a 1080 reference, native 4K):
  - Mashup 103, 162 and 191, and Serge 158 002.
  - The screencap is the 1920×1080 UI composition. The bottom 180 rows are cropped to remove an on-screen track overlay.
  - Live music, so the two images are not the same moment.
- **Data:**
  - `native-4k-ab-music.json`: native-4K A/B for 8 presets at `d9894a4`.
  - `native-4k-perf-split.json`: `84c7050`, the final A/B plus the in-build split between line drawing and line width.
  - `final-capped-vs-release.json`: the final build at the 1330 cap against 2.1.4 at native 4K.

## 11. Root causes that needed no change (`11-root-causes`)

- **Images:** `shifter-q-load-size-sensitivity.jpg`. shifter "q load" with classic lines at 1182 and at ±1.4 % of that size, then the
  PR build at 1440 and 1600.
- **Data:**
  - `isolate-results.json`: the shifter and Acid Mandala isolation runs.
  - `custom-wave-canvas-hits.json`: exact canvas hit counts that show the earlier custom-wave difference was a measurement artefact.
