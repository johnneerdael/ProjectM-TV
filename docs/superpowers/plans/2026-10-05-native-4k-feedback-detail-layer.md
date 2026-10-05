# Native 4K Feedback Detail Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Native (above-1330) render look like the preset as authored. Fix the darkening of feedback presets at Native 4K (`$$$ Royal - Mashup (191)` at 0.38× brightness, `Fed - quadratrail` 0.61×, `astral spinorgentics encrustcore nz+` 0.75×, `Geiss - Motion Blur` black on current main). Keep 4K sharpness where the preset allows it, and make Native faster than today by default.

**Architecture:** A new projectM patch replaces patch 0038's uniform diffusion pre-pass in the Native core with a two-resolution feedback loop.
- **State L:** the feedback state at the authored canvas size (1280×720 at 4K), warped exactly as MilkDrop would.
- **Native frame H:** an upscale of the warped L, plus an optional native-resolution detail band weighted by α, plus this frame's waves, shapes and borders drawn at native resolution.
- **Injection:** after the geometry, the geometry is written back into L at canvas size, so L stays a faithful authored-size MilkDrop state.
- **Setting:** a new user-facing three-level setting picks α: Standard 0 (the default), Medium 0.5 and High 1.

The capped (1330) core is unchanged.

**Tech stack:**
- projectM 4.1.7 plus the patch series in `tools/projectm-patches` (C++14, GLSL `#version 330` / `#version 300 es`).
- NDK/CMake core build; Java app (`app/src/main/java/com/example/projectm/visualizer`).
- Host GTest suite (`tools/projectm-host-tests.sh`); preset-lab (Python 3, numpy, OpenCV).

**Evidence:** `docs/superpowers/evidence/0025-feedback-diffusion/detail-layer/` (this branch). It holds:
- the prototype diff against main's engine;
- the lab scripts and the Android benchmark harness;
- every raw result quoted below.

The visual comparison of six presets is at https://claude.ai/artifact/PWZrv3myeC9fU9bB3E8g1G (private to the owner). It has a split view and 1:1 4K crops for authored, libprojectM 4.1.7, current main and the detail layer at α 0, 0.5 and 1.

---

## 1. Why: the problem and what was ruled out

MilkDrop presets are tuned at roughly 1024×768. Their look depends on the warp's per-frame bilinear resampling of the previous frame, which slightly blurs every feedback step. At native scale `s`, the same blur covers `1/s²` of the picture area. Trails therefore keep more contrast and lose less energy per frame, and presets whose look relies on that diffusion turn dark or harsh at 4K.

| Approach (all prototyped and measured) | Outcome |
|---|---|
| Patch 0038 (on main): a uniform pre-pass blur sized to `(s² − 1)/6` | Better than nothing; still 0.38–0.75× on Royal 191, Fed, astral; Acid Mandala's warp-shader structure is smeared away (see artifact crops) |
| Exact per-read footprint (rewrite `texture(sampler_main, …)`) | Best per-pixel match, but +6–11 ms per frame at 1330 on Mali-G52/G57 and +52 ms per frame at 4K on the TCL's G57; abandoned for cost |
| Stochastic / 3-tap / phase-aware pre-pass / polyphase texture | Either inaccurate or slower than the footprint (polyphase breaks 2×2 quad texture locality) |
| **Detail layer (this plan)** | Matches authored within ±3 % brightness on every reference preset; Standard is cheaper than current main |

Additional findings that constrain the design:
- **Non-integer scale fades dots.** At 2160 over a 1182×665 canvas (scale 3.249), `DotStyleFor` draws 6.5 px dots as 7×7 at alpha 0.86, and grid misalignment adds mixing. **The canvas must be an integer divisor of the render size**, so 2160 uses 1280×720 (scale 3) and 1440 uses 1280×720 (scale 2). The user accepted 1280×720 as the authored size for Native.
- **First-frame framebuffer bug.** Patch 0041 (on main) fixes it: blur allocation unbound the read and draw targets, which dropped frame-0 geometry. Any reference rendered without 0041 is wrong for blur-reading warps (Acid Mandala differed by 26 %).

## 2. Design

### 2.1 Per-frame pipeline (Native core, detail layer active)

Notation: `S` = integer scale; `W×H` = render size; `CW×CH = W/S × H/S` = canvas; `L[0]` = authored state from last frame; `Hprev` = the native framebuffer from last frame.

1. **First frame or resize:** set `L[0] = box_S(Hprev)`, an S×S box average.
2. **Motion vectors:** if the preset shows them, draw them onto `Hprev` as today, **and onto `L[0]` at canvas size**. Use a render context with `viewportSize = CW×CH` and line reference 0, i.e. MilkDrop's 1 px lines. They are part of the feedback. Skipping them was a prototype bug: `Stahlregen … Tides` went black and `StarGate rEmIx` lost its texture.
3. **Blur levels:** build blur1–3 from `L[0]` with reference scale 1.0, not from the native frame. Keep projectM's timing: before the warps when the warp shader does not sample blur, and after the warps when it does (`m_warpSamplesBlur`). The latter fixed `Waltra - Heaven Liquid`.
4. **Per-vertex equations:** evaluate them once (`PerPixelMesh::Prepare`, new).
5. **Authored warp:** `Lw = warp(L[0])` at CW×CH: `CopyTexture` flip of `L[0]`, then `PerPixelMesh::DrawAgain` into `L[1]`. Set `glViewport(CW, CH)` *before* the flip; the prototype rendered black without it.
6. **Native warp (only if α > 0, or if motion vectors need the u/v map):** `Hw = warp(Hprev)` at W×H, as today.
7. **Combine:** `Hc = bilinear_up(Lw) + α · (Hw − bilinear_up(D))` with `D = box_S(Hw)`. At α = 0 this is `bilinear_up(Lw)`, so no D and no Hw reads.
8. **Geometry:** draw this frame's shapes, waves, darken-centre and border onto `Hc` at native resolution with quad lines, as today. Call the result `Hp`.
9. **Inject:** `L[0] = Lw + G`, where `G = Hp − Hc` at the native pixels at each canvas pixel's centre:
   - **odd S:** the middle pixel;
   - **even S:** the mean of the middle 2×2.

   Do not box-average the whole S×S block: that spreads a dot over several canvas pixels at a fraction of its peak and dimmed Royal 191.
10. **Composite:** comp shader and echo run on `Hp` at native resolution, unchanged.

Shader uniforms that consume RNG (`rand_frame`, `rot_rand`, …) must be evaluated once per frame and reused by the second warp. The prototype caches them per `renderContext.frame` in `MilkdropShader`.

### 2.2 Levels

| Level (working name) | α | Native warp | Extra passes over today | Look |
|---|---|---|---|---|
| **Standard (default)** | 0 | skipped (runs only when motion vectors need the u/v map) | canvas warp, upscale, canvas inject | Authored trails (720p state ×3), native-resolution new geometry and comp. Fastest |
| Medium | 0.5 | yes | canvas warp, down, combine, inject | Half the native trail detail |
| High | 1 | yes | same as Medium | Full native trail detail on the authored brightness and blur base |

Medium and High cost the same; the choice between them is taste. Performance advice is therefore Standard against Medium/High.

### 2.3 Memory (4K, RGBA8)

- **Every level:** `L[0]`, `L[1]` and the canvas flip texture, 3 × 3.7 MB.
- **Medium/High also:** D (3.7 MB) and one native scratch texture for Hc (33 MB). Inject needs `Hc` after geometry overwrites the frame.
- **Standard:** can avoid the native scratch texture. Inject recomputes `Hc = bilinear_up(Lw)` at the canvas centre.

Check the totals against `DeviceProfile.memorySafeHeight` and the SHIELD low-memory history (ARCHITECTURE.md › Memory limit).

## 3. Measurements to date

All host renders use preset-lab on desktop OpenGL (macOS) with a fixed seed, the lab clock, 480 frames and the 8 standard capture frames. Authored is main's engine at 1280×720 with no line reference.

**Six reference presets, brightness relative to authored / mean error** (`results/gallery-six-presets.json`):

| Preset | libprojectM 4.1.7 | Main today | Standard (α 0) | Medium (α 0.5) | High (α 1) |
|---|---|---|---|---|---|
| Acid Mandala v1c | 1.21 / 0.186 | 0.90 / 0.068 | 1.00 / 0.016 | 1.00 / 0.019 | 1.01 / 0.020 |
| astral spinorgentics | 0.13 / 0.407 | 0.75 / 0.141 | 0.97 / 0.080 | 0.98 / 0.081 | 1.03 / 0.086 |
| Royal Mashup 191 | 2.23 / 0.063 | 0.38 / 0.018 | 1.02 / 0.002 | 1.02 / 0.002 | 1.02 / 0.002 |
| Fed quadratrail | 0.06 / 0.004 | 0.61 / 0.003 | 0.99 / 0.001 | 0.99 / 0.001 | 1.00 / 0.001 |
| Waltra Heaven Liquid | 0.55 / 0.110 | 0.96 / 0.023 | 1.00 / 0.002 | 1.00 / 0.003 | 1.00 / 0.004 |
| I Like Cartoon (chaotic) | 1.01 / 0.184 | 1.07 / 0.205 | 1.02 / 0.187 | 1.00 / 0.182 | 1.04 / 0.178 |

**68-preset screen at 3840×2160 on main's engine** (`results/broad-main/`, reference authored 1280×720):

| | Main today | Standard | High |
|---|---|---|---|
| Median error | 0.0178 | **0.0056** | 0.0091 |
| Presets below 0.75× brightness | 5 (Motion Blur 0.00, Royal 191 0.38, Fed 0.61, Tartan 0.72, astral 0.75) | **0** | 0 |
| Presets above 1.10× | 5 | 2 | **3 (ADAMFX Creation 1.98, Mandala Chasers 1.58, Geometry 101 1.32)** |
| Closer to authored than main (5 % tolerance) | — | 64 closer, 2 tied, 2 farther | 55 closer, 4 tied, 9 farther |

Error measures likeness to authored. High's native detail counts as error, so judge High's quality by eye. Its over-brightening is a real defect; see §4 Task 3.

**SHIELD Android TV 2019 (Tegra X1+), offscreen** (`pmbench`, EGL pbuffer, RGBA8 FBO at the render size, glFinish per frame, 60 warm-up + 240 measured frames, two interleaved rounds; `results/shield-matrix.log`). The times are per frame, GPU+CPU serialized, without the app's display composition. They compare engines; they are not app fps.

| Preset | libprojectM 4K | Main 4K | Standard 4K | High 4K | libprojectM 1330 | Main 1330 |
|---|---|---|---|---|---|---|
| Acid Mandala | 29.2 ms | 25.8 ms | **21.3 ms** | 30.0 ms | 25.4 ms | 15.1 ms |
| astral (CPU-bound) | 37.3 | 37.8 | **36.7** | 39.7 | 38.5 | 36.2 |
| Royal 191 | 14.6 | 13.2 | **12.2** | 16.4 | 9.3 | 6.8 |
| Fed quadratrail | 15.0 | 15.0 | **11.3** | 17.4 | 9.8 | 6.8 |
| Waltra | 27.2 | 24.2 | **20.2** | 28.9 | 12.4 | 10.2 |
| I Like Cartoon | 22.0 | 20.7 | **15.0** | 24.1 | 11.8 | 9.4 |

- Standard takes 3–28 % less time per frame than main at 4K.
- High takes 5–24 % more than main and 3–16 % more than libprojectM 4.1.7 at 4K.
- At 1330, main takes 6–41 % less time per frame than libprojectM 4.1.7, so the patch series as a whole is a speed-up; the CPU-bound astral gains least.
- libprojectM reports `GL_INVALID_OPERATION` (0x502) on every run; ours report none.
- The 1330 column is the Native-policy core with 0038 active. The shipped capped core disables diffusion, so the app at 1330 is faster still.

**Per-pass micro-benchmark** (`pmbench/gpubench.cpp`, ms per full-screen pass, 2 render targets per pass):

| Pass | SHIELD 1330 / 4K | TCL MT9689 G57 1330 / 4K | AM9 Pro G310 1330 / 4K |
|---|---|---|---|
| Native full-screen copy (reference) | 2.7 / 8.0 | 6.9 / 16.9 | 1.8 / 4.8 |
| Combine | 3.4 / 8.9 | 7.2 / 16.1 | 2.1 / 5.3 |
| Upscale only (Standard) | 0.7 / 1.7 | 4.2 / 10.7 | 1.8 / 4.5 |
| Canvas warp (Acid / Cartoon) | 0.9 / 1.1 at 4K | 7.1 / 5.4 at 4K | 3.8 / 2.6 at 4K |
| Down (box S×S) | 1.1 / 2.9 | 3.3 / 9.9 | 1.2 / 9.0 |
| Inject | 1.2 / 2.4 | 3.7 / 8.6 | 1.5 / 3.4 |

The combine and upscale rows come from the corrected benchmark; the canvas warp, down and inject rows from the first run, whose combine shader had a uniform bug that did not affect those passes. No app fps has been measured on any TV yet; see Task 7.

## 4. Tasks

Follow AGENTS.md:
- isolated worktree under `.worktrees/`, `bug/` or `feat/` branch from the latest `origin/main`;
- projectM changes only as patches in `tools/projectm-patches` (never commit inside `third_party/projectm`);
- no version bump;
- the PR needs release notes, validation and a documentation assessment, plus a completed Codex review, before merge.

### Task 1: Port the prototype into a clean patch `0042-feedback-detail-layer.patch`

Start from `detail-layer/detail-layer-prototype.diff`. It applies to main's engine (series 0001–0041) and contains debug code that must not ship.

- [ ] Move `DetailLayer` from the file-static `std::unordered_map<const void*, …>` into `MilkdropPreset` members. Use projectM's `Renderer::Framebuffer` / `TextureAttachment` / `Shader` / `CopyTexture` instead of raw GL handles where practical. Release the resources in the destructor and on resize.
- [ ] Put the down, combine and inject shaders next to the static shaders (`MilkdropPreset/Shaders/*.frag`, generated via `MilkdropStaticShaders`) with the GLSL 330 / ES 300 header the other shaders use. ES needs `precision highp float; precision highp int; precision highp sampler2D;`.
- [ ] Remove every `getenv` (`PM_DETAIL`, `PM_DETAIL_DEBUG`, `PM_FRAME_DEBUG`, `PM_GEO_DEBUG`, `PM_REBIND_TEST`) and the `DetailMean` read-backs. One leftover `std::string(getenv(...))` crashed every render when the variable was unset.
- [ ] Add `PerPixelMesh::Prepare()` (equations only) and `DrawAgain()` (draw only). The Standard level must call `Prepare` when it skips the native warp. Without it the mesh freezes; the prototype then differed by MAE 0.19.
- [ ] Per-frame caching of shader random uniforms (prototype: `MilkdropShader.cpp`, keyed by `renderContext.frame`) so the second warp sees the same values.
- [ ] Skip patch 0038's pre-pass when the detail layer is active. Keep 0038 for the case below where the detail layer cannot run.
- [ ] Canvas rule: `S = round(sqrt(W·H / (1280·720)))`. The layer is active only if `S ≥ 2`, `W % S == 0` and `H % S == 0`. Otherwise fall back to the 0038 path and log once. 3840×2160 gives S 3 and 2560×1440 gives S 2; Native is offered only above 1330 (`QualityController`).
- [ ] **Line reference:** the canvas is `ShaderCanvasSize()` = render size / `LineScale`. The app passes 1024×768 (`core/src/main/cpp/native-lib.cpp:1683`), which gives 1182×665. For the detail layer the Native core must pass **1280×720**, so `LineScale` equals S. The capped core keeps 1024×768. Check that `texsize`, `BlurSourceFor()`, `MaximizeColorsTextureSize()` and `SampleDecisionWidth()` all follow the 1280×720 canvas.
- [ ] Standard: skip the native warp unless `writeMotionUV`; skip D and the native reads in combine. Better: draw `bilinear_up(Lw)` straight into the current framebuffer, so Standard needs neither the Hc texture nor the blit. Inject then rebuilds Hc from Lw. Next, let the canvas warp write the motion-vector u/v map, so Standard never needs the native warp; the motion vectors then read a canvas-size u/v map (normalized coordinates, so this works).
- [ ] Shader compile or link failure on a driver: disable the layer for the instance and fall back to 0038, as 0038 already does for its rewrite.
- [ ] Preset transitions: each preset in a blend owns its own L. Verify memory with two presets alive and the blend at lower internal resolution (ARCHITECTURE.md › Transitions/Resolution).
- [ ] Patch 0002 scales framebuffer contents on resize. Rebuild L from the scaled native frame (step 1) after a resize.

Acceptance:
- `tools/check-patch-series.sh` applies all patches.
- Host tests pass (`tools/projectm-host-tests.sh`).
- At α 0, a new host render test compares L with a plain projectM render at the canvas size, frame for frame. This was **not** verified in the prototype: only the final native output was compared (error 0.001–0.08 against authored). Expect a small difference, because injected geometry is drawn at native resolution and then sampled; set the tolerance from measurement.

### Task 2: Public API (core AAR boundary with Milkbeat)

- [ ] Add a projectM C API call in the patch, e.g. `projectm_opengl_set_feedback_detail(projectm_handle, float alpha)`. Specify a negative value as "off" (0038 path) and 0…1 as α. Default to **off in the library**, so other consumers and the capped core are byte-identical.
- [ ] `native-lib.cpp`: pass the level from `g_inputs` (same pattern as `presetDuration` / `beatCuts` around line 1081) and apply it on the GL thread.
- [ ] JNI/Java: an additive method on the core interface, and nothing removed. Check Milkbeat's use of the AAR before naming it. AGENTS.md treats the AAR as an integration boundary.

### Task 3: Fix the over-brightening at Medium/High (gate for exposing them)

**Root cause (measured):** the detail band `Hw − up(D)` is signed. Writing `Hc` to RGBA8 clips its negative part at 0 in dark areas, so the clipped energy is a positive bias that the native feedback loop accumulates.

In `Mandala Chasers` at α 1 (PM_DETAIL_DEBUG means, sampled every 40 frames), the clipped `Hc` averaged 1.1–3.4× the authored `Lw`, typically about 2×, e.g. 0.021 against 0.006. The box-averaged native warp output was 0.04 at that point: the native frame had drifted far above the authored state. The visible result is blocky smears and 1.58× brightness. α 0 never forms the band.

- [ ] Candidate fix A (re-anchor): after combine, compute `E = Lw − box_S(Hc)` and add `bilinear_up(E)` before the geometry. The native frame's S×S means then always equal the authored state. Cost: one canvas-size down pass plus a fused add.
- [ ] Candidate fix B: keep the detail band in a signed float texture (RG/RGBA16F) owned by the layer, decayed and warped separately, and never store it in the clamped frame. Costs more memory and bandwidth.
- [ ] Candidate fix C (cheapest, fallback): limit the band symmetrically per channel, `d = clamp(d, −min(Lw, 1−Lw), +min(Lw, 1−Lw))`. That is unbiased, but it removes detail around dots on black, which are exactly the cases High is for.

Acceptance:
- On the 68-preset screen, High has no preset above 1.10× that Standard does not also have.
- ADAMFX Creation, Mandala Chasers and Geometry 101 are within ±10 % of authored.
- Median error stays ≤ 0.010.

### Task 4: App setting

- [ ] Add an Advanced row in `MainActivity` / `activity_main.xml`, next to the existing rows. **Do not call it "Detail":** that row already exists and means the mesh size (Minimal…Ultra, `DeviceProfile`). Suggested label: *Native trails*, *Trail sharpness* or *Feedback detail*, with values *Standard / Medium / High*. The owner decides; see §5.
- [ ] Show the row only when Native is selected and the device runs the Native-policy core, or show it disabled with a reason. It has no effect at Auto or at numeric heights (capped at 1330).
- [ ] Persist it in `projectm_settings` with Standard as the default. A migration is needed only if the key collides.
- [ ] Diagnostics panel: show the active level and canvas, e.g. `trails: standard (1280×720 ×3)`, or `off (0038)` with the fallback reason.
- [ ] Until Task 3 passes, ship only Standard, or hide Medium/High behind a developer toggle.

### Task 5: Tests

- [ ] Host unit tests for the canvas rule (S, divisibility and fallback), the inject sampling positions for odd and even S, and API defaults.
- [ ] Host render tests:
  - L equals the canvas-size render at α 0;
  - motion-vector presets (`Tides`, `StarGate rEmIx`) are not black or dim;
  - the blur-reading warp (`Waltra`) matches authored ±3 %;
  - the Standard fast path equals α 0 with the native warp (the prototype was bit-identical on Acid and Royal).
- [ ] Replace or retire `FeedbackDiffusionTest` / `FeedbackDiffusionRenderTest` cases that assume 0038 is always active in the Native core.
- [ ] GLES: the shaders compile on Mali-G52 (AM6), G57 (TCL), G310 (AM9) and Tegra (SHIELD). Use the `pmbench` harness offscreen, or a profile APK with an uncommitted `__android_log_print`: `fprintf(stderr)` is invisible on Android (memory note).

### Task 6: 68-preset quality screen (host)

- [ ] Run `lab/broad-dl.py` with main's engine for authored and today's Native, and the patch's engine for Standard/Medium/High (CONFIGS example in §6).
- [ ] Acceptance for Standard is no regression against this plan's numbers: median ≤ 0.006, no preset below 0.85×. The lowest today is `Flexi + orb + geiss - the computer is your friend` at 0.86×; it is chaotic, with an authored-1280-vs-authored-1182 error of 0.39.

### Task 7: Device performance and recommendations

- [ ] Profile APK on each TV, with the user's permission and **music playing** (`dumpsys media_session` state=3). Use the AM6 method in memory/`docs/PROFILING.md`: pinned preset via `debug.projectmtv.preset`, fixed resolution via prefs, STATS lines. Restore `debug.projectmtv.*` and the prefs afterwards.
- [ ] Devices: Ugoos AM6 (Mali-G52, rooted), TCL Smart TV Pro (MT9689 G57, adb TLS), AM9 Pro (G310), SHIELD 2019 (Tegra X1+). Never wake a TV remotely.
- [ ] Measure Native at Standard, Medium and High against today's Native and Auto, on Acid Mandala, Royal 191, Fed, Waltra, Cartoon and one CPU-bound preset (astral).
- [ ] Write the recommendation table for the user guide (which level per device). If Medium/High halve fps on Mali, say so plainly.

### Task 8: Documentation (mandatory for every feat/bug change)

- [ ] `docs/ARCHITECTURE.md`: replace the patch-0038 paragraph in §5 with the detail layer: the pipeline, why integer canvases, the levels, the fallback, and 0038's remaining role. Update §5 › Resolution (Native line reference 1280×720).
- [ ] `docs/THIRD_PARTY.md`: patch 0042 entry. `AGENTS.md`: patch list line.
- [ ] `docs/user-guide/settings.md`: the new row, what each level does, its cost, and the device recommendations from Task 7. Add `troubleshooting.md` entries for "Native looks soft" (raise the level) and "Native stutters" (Standard).
- [ ] `docs/PROFILING.md`: how to measure the levels.
- [ ] `README.md`: only if it describes Native rendering.
- [ ] PR release notes (user-facing):
  - Native 4K keeps presets as bright as authored (name Royal 191 and Fed with before/after numbers from Task 7);
  - the default is faster;
  - a new setting for sharper trails at a cost.

## 5. Open decisions for the owner

1. **Label and values.** Avoid a bare "Low" for the default: users read it as low quality, while it is the authentic and fastest choice. Suggested: *Native trails: Standard / Medium / High*.
2. **Medium's α.** 0.5 is a guess with identical cost to High. Keep three levels, or offer Standard and High only.
3. **Automatic choice.** Should Native pick Standard on Mali tiers and allow High on SHIELD-class devices (`DeviceProfile` tier), or always default to Standard? Decide after Task 7.
4. **Native without the layer.** Should Native at panel sizes where `S < 2` or the size isn't divisible keep 0038, or render plain? None of the current test TVs hit this.

## 6. Reproducing the evidence

Lab engines are built from a pristine export of `third_party/projectm` plus a patch series, **instrumented by preset-lab**. Without `_instrument()` (`tools/preset-lab/src/preset_lab/build_worker.py`), projectM runs on the wall clock and random devices, and two runs of the same job differ by MAE 0.08–0.13. That briefly made main look like it rendered different content.

```bash
# engine = pinned projectM + main's series + lab instrumentation
E=/tmp/engine-main; mkdir -p $E
git -C third_party/projectm archive HEAD | tar -x -C $E
git -C third_party/projectm/vendor/projectm-eval archive --prefix=vendor/projectm-eval/ HEAD | tar -x -C $E
for p in tools/projectm-patches/*.patch; do (cd $E && git apply "$OLDPWD/$p"); done
(cd tools/preset-lab && PYTHONPATH=src python3 -c "from pathlib import Path; from preset_lab.build_worker import _instrument; _instrument(Path('$E'))")
# detail-layer engine: the same, plus the prototype diff
cp -R $E /tmp/engine-detail && (cd /tmp/engine-detail && patch -p1 < docs/superpowers/evidence/0025-feedback-diffusion/detail-layer/detail-layer-prototype.diff)
# host worker: cmake -S tools/preset-lab/src/preset_lab/native -B build -DPROJECTM_SOURCE=$E && make preset-lab-worker
```

- `lab/one.py IDX LABEL W H RW RH [ENV=…]` renders one preset of `broad-list` (68 presets).
- `lab/broad-dl.py OUT` runs the screen. `CONFIGS` maps each label to `[w, h, rw, rh, env, worker, reference_label]`. Example for Standard: `"md0_4k": [3840, 2160, 1280, 720, {"PM_DETAIL": "0"}, "<detail worker>", "c1280"]`.
- `pmbench/` is the Android offscreen harness (CMake with the NDK toolchain, arm64, API 28; `-DUPSTREAM=ON` for unpatched 4.1.7, which needs the one-line `lab_target_fbo` change in `ProjectM.cpp` described in `bench.cpp`). `matrix.sh` is the SHIELD run. Processes segfault at exit after printing; the timings are unaffected.

## 7. Pitfalls met in the prototype

- **Mali micro-benchmarks:** forward pixel kill drops repeated full-screen draws into one FBO. Alternate two FBOs with `glFlush`, or the timings come out about 30× too low. Feed realistic inputs: a random u/v map inflates costs about 10×.
- **Viewport before `CopyTexture`:** it draws with the current viewport.
- **Hidden icons from `ls`:** this machine aliases `ls` to eza with icons, so `ls | grep ^name` matches nothing. Use `/bin/ls`.
- **S = 2 inject:** with an even scale there is no centre pixel. A single off-centre sample shifts injected geometry by half a native pixel. Use the 2×2 mean.
