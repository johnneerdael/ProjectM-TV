# Native 4K feedback diffusion: darkening defects. Diagnosis and engineer handover

Snapshot: 2026-10-04, after PR #28 merged into `feat/native-4k-feedback-recovery` (merge `0e3f948e`, product head `af8202bd`, patch `tools/projectm-patches/0036-feedback-diffusion-compensation.patch`). Audience: the engineer who will fix these defects.

**This is a diagnosis, not a fix.** No product code, patch or branch was changed. Experimental confirmation of a phase-aware fix belongs to the main Native 4K agent's in-progress **phase-variance analysis** (`build/native-4k-current-main/phase-variance-analysis/` in the recovery worktree). Coordinate with it rather than duplicating its experiments. The experiments recommended to it are listed in [Recommended experiments](#recommended-experiments-for-the-phase-variance-analysis).

## Problem

Above the line-reference area, patch 0036 adds a uniform blur of `(s²−1)/6` native px² per axis to the warp's bilinear input, capped at 1.9. At 3840×2160 with the 1024×768 reference, `s² = 10.55`, so it adds 1.59 native px², which is 0.151 reference px². This restores MilkDrop's per-frame bilinear smoothing *on average over sample phase*: 1/6 reference px² per axis.

Three presets stay darker than the authored-size control after every routing and kernel-shape change so far:

- **Defect C:** `$$$ Royal - Mashup (191)`, `Fed - quadratrail` and `astral spinorgentics encrustcore nz+`.
- **Defect D**, a related but separate issue: bilinear warp reads get the filtered input, while the blur levels (`GetBlur1/2/3`) are still made from the unfiltered previous frame.

## Key quantity: per-read sample phase, not movement

For each axis, a bilinear read at fractional texel phase `f` adds variance `f(1−f)` texel². MilkDrop's smoothing therefore depends on where each read lands relative to the texel grid:

- Identity reads and whole-texel shifts (`f = 0`) add nothing.
- Uniformly distributed phases add 1/6 on average.

Phase must be evaluated **separately** on each grid:

- `f_ref` from the read position on the authored grid (classic 1182×665);
- `f_nat` from the read position on the native grid (3840×2160).

An identity read lands exactly on texel centres on *both* grids, even though its coordinates are not round numbers in reference units. Computing phase from absolute coordinates on the wrong grid invents blur for identity reads.

The per-read missing variance per axis is:

```text
missing (native px²)    = s²·f_ref(1−f_ref) − f_nat(1−f_nat)
missing (reference px²) = f_ref(1−f_ref) − f_nat(1−f_nat)/s²
shipped uniform term    = (s²−1)/6 native px²  =  (1 − 1/s²)/6 reference px²
```

The uniform term equals the missing amount only when both phases are uniformly distributed. It over-adds wherever `f_ref ≈ 0`: identity, texel-aligned or whole-texel reads.

Above the reference, `texsize.zw` reports the *reference* canvas (`ShaderCanvasSize()`): 1/1182 by 1/665 at both 1182×665 and 3840×2160. A one-texel shader offset is therefore an integer texel at the authored size but 3.249 native texels at 2160. That changes the read's native phase relative to the centre read.

Movement magnitude is not the quantity: whole-texel moves have zero phase. This handover does not propose distance-scaled compensation.

## Evidence

### E1. Actual-core emulator evidence (existing, reused)

All on emulator-5582 (Apple M4 Pro translator): seed 12345, the 480-frame PCM (`14a59e75…`), eight selected captures, 12 s window. Luma ratio and 1182×665 area-reduced RGB MAE are both against classic29 ref0. Sources:

- `build/native-4k-current-main/raw-point-controls/analysis.json`
- `gaussian-kernel-controls/analysis.json`
- `mrt-fix-validation/`

The current product is identical to raw-point at 96/96 frames.

| Preset | Size | Classic luma | Luma ratio (current product) | MAE | Contrast (luma std): product vs classic |
|---|---|---|---|---|---|
| Royal 191 | 1330 | 0.0319 | 0.319 | 0.0223 | 0.060 vs 0.107 |
| Royal 191 | 2160 | 0.0319 | 0.316 | 0.0226 | 0.060 vs 0.107 |
| Fed quadratrail | 1330 | 0.0046 | 0.758 | 0.0020 | 0.020 vs 0.022 |
| Fed quadratrail | 2160 | 0.0046 | 0.527 | 0.0029 | 0.017 vs 0.022 |
| astral nz+ | 1330 | 0.512 | 0.663 | 0.212 | 0.280 vs 0.368 |
| astral nz+ | 2160 | 0.512 | 0.645 | 0.232 | 0.273 vs 0.368 |

- **Routing:** raw-point vs P1 left all three exactly unchanged. They have no point-sampled main reads.
- **Kernel shape:** a same-variance 5-texel Gaussian left them unchanged (Royal191 0.314, Fed 0.513, astral 0.635 at 2160).
- **Dose dependence:** Fed darkens more at 2160 (variance 1.59) than at 1330 (variance about 0.5).
- **Uncompensated comparisons:**
  - `first-matrix-analysis.json`, near-reference comparator: Fed baseline29 is *closer* at 2160 (luma 1.144×, MAE 0.0020, vs candidate 0.521×, 0.0029). Royal191 baseline explodes (13.9×, MAE 0.399); candidate 0.33×, MAE 0.021.
  - Broad sample (`current-main-validation/broad-sample/classic-comparison.json`): astral baseline29 native luma error 0.038 (1330) and 0.062 (2160), vs candidate 0.172 and 0.182. That's "farther" on all eight frames.

### E2. Host variance-scale experiment (new, supplementary)

**Setup:**
- Desktop GL, Apple M4 Pro. Preset Lab's isolated engine (`prepare_engine`): pinned projectM `e0b0a967`, the 36-patch series at `af8202bd`, Preset Lab's deterministic clock/RNG instrumentation. Engine identity: patches `d9f14ff8…`, instrumentation `254db5d7…`.
- Two scratch-only diagnostic hooks (`diagnostic-hooks.diff`): `PM_DIFFUSION_VARIANCE_SCALE` multiplies the kernel's requested variance; `PM_DUMP_UV_DIR` dumps the warp mesh.
- 48×32 mesh (one of the app's Detail levels), the protocol PCM converted to float, logical time `(frame+1)/30`, seed 12345, the same eight frames.
- Classic is 1182×665 with no reference. The native renders are 3840×2160 with reference 1024×768.

**Reproducibility:**
- Repeats are exact: 3/3 spot-checked configurations gave 8/8 identical frames.
- At ×1 the host reproduces the actual-core values exactly for Royal191 (0.316 / 0.0226) and Fed (0.527 / 0.0029). Those two are therefore reliable proxies.
- astral, Mandelverse and Acid differ from actual core in absolute level (noise textures and RNG paths), so treat them as directional.

| Preset | ×0 (no compensation) | ×0.25 | ×0.5 | ×1 (shipped) |
|---|---|---|---|---|
| **astral nz+** luma ratio / MAE | **0.866 / 0.147** | 0.735 / 0.183 | 0.678 / 0.203 | 0.612 / 0.234 |
| **Fed quadratrail** | 1.119 / 0.0022 | **0.893 / 0.0019** | 0.745 / 0.0021 | 0.527 / 0.0029 |
| **Royal 191** | 13.34 / 0.396 | 11.80 / 0.347 | 9.65 / 0.279 | **0.316 / 0.0226** |
| Mandelverse (control) | 0.992 / 0.139 | 0.991 / 0.137 | 0.994 / 0.136 | 1.005 / 0.138 |
| Acid Mandala (control) | 0.998 / 0.116 | 0.988 / 0.114 | 0.943 / **0.106** | 0.917 / 0.111 |

Contrast (luma std) falls monotonically with variance for astral (0.344 → 0.266; classic 0.366) and Fed (0.0245 → 0.0168; classic 0.0219).

**No single global scale fits all presets:**

| Preset | Best amount |
|---|---|
| astral | ×0 |
| Fed | about ×0.25 |
| Royal 191 | at least a threshold between ×0.5 and ×1 (regime switch) |
| Acid | about ×0.5 |
| Mandelverse | insensitive |

A global variance scale, or a scalar gain, is therefore not a fix.

### E3. Phase analysis of the actual warp reads (new)

**Method:**
- The warp vertex shader (`PresetWarpVertexShaderGlsl330.vert`) is evaluated on the dumped per-vertex parameters and warp uniforms (`phase_analysis.py`).
- UVs are interpolated to *actual pixel centres* of each grid. Bilinear interpolation over mesh cells approximates the GPU's per-triangle interpolation.
- Every main-texture read of each warp shader is mapped onto the classic grid (`f_ref`) and the native grid (`f_nat`).
- A synthetic identity mesh gives `f(1−f) < 1e−12` on both grids, confirming the convention.

Results, mean over 8 frames:

| Preset / read | `f_ref(1−f_ref)` | needed native px² | uniform native px² | texel-aligned at ref | uniform > 2× needed |
|---|---|---|---|---|---|
| astral `tex2D(main, uv)` (base of its max trail) | **0.000** | **0.000** | 1.591 | **100%** | **100%** |
| astral `tex2D(main, (uv−.5)·(1∓8·|tz|)+.5)` | 0.167 | 1.591 | 1.591 | 1% | 9% |
| Royal191 `GetPixel(uv ± texsize.zw)`, `tex2D(main,(uv−.5)·.9+.5)` | 0.167 | 1.591 | 1.591 | 1% | 9% |
| Fed `GetPixel(uv)`, `GetPixel(uv ± texsize.zw)` | 0.166 | 1.585 | 1.591 | 1% | 9% |
| Mandelverse `uv` (control) | 0.049 | 0.444 | 1.591 | 64% | 78% |
| Acid Mandala `uv` (control; 75% of vertices valid, zoom reaches 0) | 0.166 | 1.580 | 1.591 | 1% | 10% |

The mesh explains the astral row. Its per-frame code forces `zoom = 1` and `warp = 0`, with no rotation or translation, so the mesh is the identity. Royal191's zoom (`max(1.0001, 0.95 + .075·max(treb_att, mid_att+.5))`) plus rotation, and Fed's zoom 0.978, spread phases almost uniformly at both sizes.

### E4. Per-frame peak retention (new, analytic)

`peak_retention.py` models a one-reference-texel feature, per axis.

| Case | Mean per-axis peak retention |
|---|---|
| Classic bilinear at random phase | 0.750 |
| 3840×2160, shipped kernel ×1 | 0.741 |
| 3840×2160, ×0.5 | 0.888 |
| 3840×2160, ×0.25 | 0.943 |
| 3840×2160, ×0 | 1.000 |

Single-frame peak loss for isolated features therefore matches at ×1.

### E5. Owner's synthetic probe (cited, read-only, in progress)

`phase-variance-analysis/driver-results.txt`, Apple M4 Pro, grid about 4× the reference (`ref` 99/100/101). An identity-copied 4-px checker keeps its contrast without filtering (sd 80 every frame). With filtering it drops to sd 4.9 by frame 8. A single-pixel impulse disappears by frame 2 with filtering. This confirms on a controlled fixture that uniform compensation flattens identity reads. `full-renderer-results.txt` and the PR28 host build there are the owner's ongoing work.

### E6. Broad-sample structure (existing data, correlation only)

Among the 64 presets at 2160:
- 9 of the 12 "farther" cases use `texsize.zw` offsets in the warp, against 3 farther among the 32 presets that don't.
- Max-trail (3/9 farther) and subtractive-decay patterns do not separate the cases.

This is correlation, not causation.

## Diagnosis

1. **astral nz+: uniform compensation over-adds on an identity read. Confidence: high.**
   - Its max-trail base read `tex2D(main, uv)` is texel-aligned on 100% of pixels at both sizes, so MilkDrop adds no smoothing, but 0036 adds 1.59 native px² every frame.
   - In a `ret = max(ret, …); ret -= 0.01` recurrence, that removes peaks and contrast each frame.
   - The host dose-response is monotonic, and the uncompensated render is best on luma, MAE and contrast. The broad sample independently shows baseline29 much closer.
   - Its zoomed reads (uniform phase) are correctly compensated on average. The defect is specific to the aligned read.

2. **Fed quadratrail: mechanism not isolated. Best amount about ×0.25. Confidence on mechanism: low to medium.**
   - Its reads' mean phase variance matches the uniform term (1.585 vs 1.591 native px²), and single-frame peak retention matches, yet the uncompensated or ×0.25 render is closer.
   - Candidate mechanisms, untested:
     - Per-tap phase decorrelation. At the authored size the centre and ±1-texel taps share one phase and one bilinear split. At 2160 the ±3.249-native-px taps have different native phases, and compensation blurs all of them alike.
     - The max of four neighbours with `ret·0.94 − 0.04` turning small per-frame differences into a steady-state brightness change.
     - **Defect D:** the GetBlur1 taps inside its max come from the unfiltered frame.

3. **Royal 191: a regime (bifurcation) case. Confidence on mechanism: low to medium.**
   - Below about ×0.5–×1 the recurrence `GetPixel(uv+dx) + GetPixel(uv+dy) − P(0.9·zoom) − 0.4` runs away into a bright regime (9.6–13.3×).
   - ×1 lands in the authored dark regime, but at 0.32× of its luma. MAE is far best at ×1.
   - Average phase variance matches. The remaining dark-level gap may come from per-tap phase decorrelation of its ±1-reference-texel Laplacian-like taps, or from the composite. That composite is dominated by `GetBlur3·2 + GetBlur3(echo)·2`, so defect D, the blur source, directly affects its displayed brightness.

4. **Defect D (blur/main footprint mismatch): proven by code, effect not measured in isolation.**
   - `MilkdropPreset::RenderFrame` builds the blur levels from the unfiltered previous framebuffer while bilinear warp reads see the filtered copy.
   - It is relevant to Fed (GetBlur1 in the max) and Royal191 (GetBlur3 in the composite).

5. **Eligibility gate gap (observation).** `DiffusionWarpEligible()` excludes point-only warps, undisplaced `uv_orig` reads and peak-plus-sharpen. It cannot see that astral's mesh is the identity, because that comes from per-frame equations rather than shader text. A syntactic gate cannot fix this; phase is a runtime property of the mesh.

## Fix directions (phase-aware)

Constraints apply to all of these: no preset rewrites, no scalar brightness gain, no filename whitelists, and no distance-scaled amounts.

1. **Per-read compensation from phase.** Compensate the missing variance `s²·f_ref(1−f_ref) − f_nat(1−f_nat)` native px² per axis at the read itself.
   - The warp vertex stage already produces the read UV.
   - `f_ref` comes from `uv·canvas − 0.5` (the canvas is `ShaderCanvasSize`); `f_nat` from `uv·render − 0.5`.
   - Shader offsets such as `uv + texsize.zw` are part of the read position. The cleanest place is therefore the main-texture sampling helper (`GetPixel` / bilinear `sampler_main` in the translated shader header), as a variable-footprint read. That keeps the preset's code untouched.
   - Identity and whole-texel reads then get zero added variance by construction.
2. **Per-region fallback** if per-read sampling is too costly. Compute a per-vertex missing-variance field from the mesh (reference vs native phase of the vertex UV) and use it to modulate the pre-warp filter locally. This loses per-tap shader offsets, so verify it against direction 1.
3. **Defect D.** Make the blur chain's source consistent with what bilinear reads see, or prove that the difference is intentional for the affected recurrences. Test it with routing, placement and variance held fixed.
4. **Keep cost in view.** The AM6 already shows that the uniform filter alone costs about 19% at 2160 on light presets (see the cost brief). Per-read sampling changes that cost profile and must be measured on the AM6.

## Recommended experiments for the phase-variance analysis

These are for the main Native 4K agent to run or adapt. One variable each, against classic29 ref0 using the actual-core protocol unless stated otherwise.

1. **astral aligned-read control.** Same build as `af8202bd`, with added variance forced to 0 only for texel-aligned reads, where the per-fragment `f_ref` and `f_nat` are both about 0. Zoomed reads stay compensated. Expect luma toward the uncompensated level (host ×0: 0.866). This isolates direction 1's effect on the confirmed case.
2. **Per-read phase-aware prototype (direction 1).** Run on Royal191, Fed, astral, Mandelverse, Acid and Royal255 at 1330 and 2160, with two repeats. Report luma, MAE, contrast and sharpness.
3. **Royal191 regime map.** Host variance ×0.6/0.7/0.8/0.9/1.0/1.2. The host matches actual core exactly for this preset, so it is cheap. Locate the regime switch and whether the dark-regime level depends on variance.
4. **Fed decomposition.**
   - (a) Defect D, blur source consistent, variance ×1.
   - (b) Per-tap phase-correlated compensation: one shared added variance for the centre and ±1-texel taps.
   - (c) Host variance grid ×0.1–×0.4.
5. **Broad phase screen.** For all 64 broad-sample presets, compute the texel-aligned fraction of main reads from mesh dumps (`phase_analysis.py` generalized). Test whether it predicts "farther"; E6 suggests the `texsize.zw` offsets matter.
6. **Do not repeat** the owner's synthetic identity/impulse probe, or a distance-scaled sweep.

## Acceptance tests for the fixer

- **Host suite:** `bash tools/projectm-host-tests.sh` stays green. Add engine-level render tests in the style of `FeedbackDiffusionRenderTest`:
  - identity-mesh feedback with compensation is byte-identical to compensation off at the same reference size;
  - a uniformly displaced warp still receives compensation;
  - whole-texel shifts receive none.
- **Actual core:** the three presets plus controls on emulator-5582 using the actual-core protocol (`mrt-fix-validation/run.py` pattern; `reproduce.sh --check` style preflight). No regression on Mandelverse/Royal255/Acid relative to `0e3f948e`. astral luma ratio and MAE must improve over 0.645 / 0.232 at 2160.
- **Broad screen:** rerun the 64-case screen and compare against `0e3f948e`, not baseline24.
- **Device cost:** AM6 cost using the N1 protocol (see the separate cost brief). Restore `debug.projectmtv.*` properties and settings afterwards.
- **GLES:** shader changes link as GLSL ES 3.00 (`glslangValidator -l`, with `#version 300 es` prepended).

## Constraints and ownership

- Change projectM only through `tools/projectm-patches/0036-feedback-diffusion-compensation.patch` (or a new numbered patch after 0036), regenerated against the pinned tree plus 0001–0035. `main` owns 0030–0035 (PR #26, PR #27). Never commit inside `third_party/projectm`.
- Devices:
  - emulator-5582 is shared with the main agent's scans; check its leases first (`*/lease.json` under `build/native-4k-current-main/`).
  - Never touch emulator-5580 or `.worktrees/quad-lines-follow-ups`.
  - Physical TVs need user authorization; never wake one remotely.
- Never remove a worktree. Work in your own `bug/` worktree and open a PR to `feat/native-4k-feedback-recovery`.

## Reproducing the host evidence

Everything is in `~/Downloads/2026-10-04-native-4k-darkening-evidence/`:
- `diagnostic-hooks.diff`, `run_matrix.py`, `phase_analysis.py`, `image_metrics.py`, `peak_retention.py`;
- results (`*.json`, `*.txt`), `capture-digests.txt` (25 runs) and `identity.txt`.

Steps:

1. In a checkout at `af8202bd` or later, run Preset Lab's `prepare_engine(repo, work)` into a scratch directory.
2. Apply `diagnostic-hooks.diff` to the snapshot's `FeedbackDiffusion.cpp` and `PerPixelMesh.cpp`, and to a copy of `tools/preset-lab/src/preset_lab/native/worker.cpp`.
3. Configure and build the worker copy with `-DPROJECTM_SOURCE=<snapshot>`.
4. Run `run_matrix.py`, then `phase_analysis.py`, then `image_metrics.py`. All 25 renders take under a minute on an M4 Pro. The raw captures, about 4 GB, were not retained.

## Limits

- **Host results:**
  - Desktop GL 4.1 with a 48×32 mesh, one PCM and seed, eight frames.
  - Exact against actual core only for Royal191 and Fed at ×1.
  - The phase analysis approximates triangle interpolation bilinearly.
  - Acid's mesh degenerates (zoom 0) on 25% of vertices.
- **Not established:**
  - the mechanisms behind Fed and Royal191's residual darkening;
  - defect D's contribution;
  - TV fidelity of any variant.
- A one-time desktop driver note, "unit 1 … unloadable, using zero texture", appeared in one host run. It did not affect repeatability; check it if host and device diverge.
