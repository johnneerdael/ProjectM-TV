# Per-read reference footprint (patch 0036 rewrite)

Snapshot: 2026-10-04. Branch `bug/native-4k-phase-aware-diffusion`, into `feat/native-4k-feedback-recovery` (merged product `0e3f948e`, uniform `(s²−1)/6` kernel). Starting point: [the darkening diagnosis handover](source-darkening-handover.md) (defects C and D).

## Result

Patch 0036 no longer blurs the whole previous frame. Every bilinear main-texture read of the warp (preset shaders and the default warp shader) whose coordinate depends on the pixel's position reproduces MilkDrop's reference-canvas read at that read's own phase. Details are in [ARCHITECTURE *Feedback diffusion*](../../../../ARCHITECTURE.md).

On the actual Android core (emulator-5582, Apple M4 Pro GLES translator, two fresh-process repeats, byte-identical), the final version (`45961f8c`) is closer to classic29 ref0 than the merged product on every case. Values are the 12 s luma ratio / 1182×665 area-reduced RGB MAE.

| Preset | 1330 product | 1330 footprint | 2160 product | 2160 footprint |
|---|---|---|---|---|
| `$$$ Royal - Mashup (191)` | 0.319 / 0.0223 | 1.116 / **0.0181** | 0.316 / 0.0226 | 0.413 / **0.0199** |
| `Fed - quadratrail` | 0.758 / 0.0020 | 1.020 / **0.0014** | 0.527 / 0.0029 | 0.624 / **0.0025** |
| `astral spinorgentics encrustcore nz+` | 0.663 / 0.2118 | 0.902 / **0.1277** | 0.645 / 0.2324 | 0.840 / **0.1546** |
| `Acid Mandala v1c` | 0.909 / 0.0567 | 0.989 / **0.0265** | 0.932 / 0.0431 | 0.980 / **0.0398** |
| `Mandelverse` | 1.015 / 0.1230 | 1.006 / **0.1147** | 1.035 / 0.1269 | 1.012 / **0.1138** |
| `$$$ Royal - Mashup (255)` | 0.885 / 0.1201 | 0.942 / **0.0759** | 0.958 / 0.0917 | 0.995 / **0.0678** |

Sources: [`actual-core-v2-45961f8c/analysis.json`](actual-core-v2-45961f8c/analysis.json). "Product" is the retained raw-point rows, which equal the merged product at 96/96 selected frames.

The host broad screen covered 68 presets: the 64 of `current-main-validation/broad-sample` plus Royal191, Fed, Acid and I Like Cartoon. It used desktop GL with the deterministic Preset Lab engine, 8 frames over 12 s, MAE against 1182×665 classic. Results are in [`host/results/broad-final-summary.txt`](host/results/broad-final-summary.txt).

| | Mean MAE 2160 | Mean MAE 1330 | Closer / within 5% / farther than the product |
|---|---|---|---|
| Uncompensated | 0.0578 | — | — |
| Product (uniform kernel) | 0.0413 | 0.0399 | — |
| Footprint, final | **0.0336** | **0.0316** | 2160: 34 / 30 / 4; 1330: 30 / 34 / 4 |
| Classic 1280×720 (genuine MilkDrop at a nearby authored size) | 0.0459 | — | — |

The footprint is within the distance from classic of an authentic 1280×720 render for 55 of 68 presets at 2160, against 47 for the product. The four farther cases are small:

- `Zylot & Shifter - Tartan`: 0.0087 → 0.0108
- `bdrv + al - dude's starpulse vector`: 0.0122 → 0.0137
- `$$$ Royal - Mashup (123)`: 0.0073 → 0.0081
- `Stahlregen + Geiss - Old school, baby!`: 0.0200 → 0.0217

## Findings

1. **Phase, not average variance.** astral's max-trail base read is an identity read. MilkDrop smooths it by nothing; the uniform kernel smoothed it every frame. With the read's own reference phase (relative to `uv_orig`), identity and whole-texel reads stay plain. astral 2160: 0.61 → 0.82 (host).
2. **Kernel shape matters.** A symmetric four-tap stencil with the per-read missing variance (host `sym`) barely moved Fed (0.56) or Royal191 (0.34). The asymmetric MilkDrop two-tap blend `(1 − f, f)` at reference spacing (host `emu`) reproduced classic at an exact integer scale. At 3546×1995 (s = 3.000) it gave Fed 1.007 / 0.0015 and Royal191 0.76 / 0.0136, against the product's 0.71 and 0.31 there. See `host/results/targeted-metrics.json` (`x3*`) and the [prototype diff](host/prototype-diagnostics.diff).
3. **Defect D disappears.** There is no filtered copy. Blur levels and bilinear reads use the same frame, as in MilkDrop.
4. **Integer scales decouple native pixels.** At s = 2 (2364×1330, Auto's cap) and s = 3, reference-spaced taps land exactly on native texel centres. Native pixels then form s² independent copies of the reference grid. Chaotic or sharpening feedback lets them drift apart; the shared blur levels and `GetPixel − GetBlur1` amplify the differences.
   - First footprint build at 1330: Acid 0.111 → 0.166 MAE (ratio 1.41), Waltra Heaven Liquid 0.0107 → 0.0339.
   - Non-integer scales (1260, 1440, 2160) were fine, because taps between texels couple neighbours.
   - Pulling the taps a quarter native texel towards the read restores that coupling; the tap distance is then re-solved for the exact reference variance.
   - A scan of the pull-in at 1330 fixed the value (`targeted-metrics.json`, `emup*`, `b25_*`):
     - 0.1 left Acid diverging (0.129).
     - 0.25 gave Acid 0.103, Waltra 0.0100 and Royal191 1.10 / 0.0171.
     - 0.5 and 1.0 tipped Royal191 into its bright regime (2.2× and 3.5×).
   - At s = 3, a size the app does not offer, 0.25 is too weak for Acid and Waltra (0.133 / 0.037).
5. **Stored coordinates have no relative phase.** `$$$ Royal - Mashup (255)` stores seed positions in its colour channels and samples `sampler_fw_main` there. A phase relative to the pixel is meaningless for that read; the first build made it 0.0917 → 0.175. A flow-insensitive position-dependence pass now leaves reads whose coordinates come only from texture data plain. Royal255 2160: 0.0766, the uncompensated level, which is also what an exact shared-lattice emulation (`abs3546x1995`) gives.
6. **Fed's remaining 2160 darkness is dot drawing, not diffusion.** `DotStyleFor()` draws 6.5 px main-wave dots as 7×7 px at alpha 0.86. Fed's `max`/`×0.94 − 0.04` recurrence kills dim peaks.
   - The integer scale with exact 6×6 dots gave Fed 1.007.
   - At 2160, unfaded 7×7 dots gave 1.05 / 0.0015.
   - Rounding to 6×6 gave 0.58, the same as GL's own point-size rounding of 6.5.
   - Exact-size dots (sprite plus discard) gave 0.79–0.84.
   - Not changed here: line geometry is separate work. Recorded as follow-up.
7. **The gate barely matters now.** With per-read footprints, disabling `DiffusionWarpEligible()` changed 1 of 68 broad presets (broad2 `nogate`).

## Method and reproduction

- **Host:** Preset Lab's `prepare_engine` on this branch's patch series, with deterministic clock/RNG. The worker is the darkening handover's diagnostic copy, which saves the 8 protocol frames.
  - Scripts: [`host/run.py`](host/run.py) (targeted), [`host/broad.py`](host/broad.py) (68-preset screen; each 4K capture is reduced and deleted), [`host/metrics.py`](host/metrics.py), [`host/broadsum.py`](host/broadsum.py), [`host/viz.py`](host/viz.py).
  - Prototype variants (`sym`, `emu`, `emuc`, `emus`, `emup`, `abs`, dot modes) are environment switches in a scratch engine: [`host/prototype-diagnostics.diff`](host/prototype-diagnostics.diff). They are diagnostics, not product code.
  - Raw captures (>40 GB) were not retained; metrics are in `host/results/`.
- **Actual core:** [`actual-core-v2-45961f8c/run.py`](actual-core-v2-45961f8c/run.py) adapts `mrt-fix-validation/run.py`. It reads the recovery worktree's classic29 ref0, raw-point and P1 rows read-only and verifies them by hash.
  - The candidate is built by the shared provider with unchanged product sources, and AAR/APK ELF identity is verified.
  - Two documented identity exceptions:
    - The cache cleanup removed the comparator roles' `.cxx` intermediates; their compile provenance is taken from `mrt-fix-validation/artifact-proof.json`, with the same APK, AAR and ELF hashes asserted.
    - The candidate's `native-lib.cpp` differs from baseline29 only by PR #27's initialization-warning log callback. These six presets render byte-identically on main35 and main29 (`current-main-validation/precision-controls-v2/historical-mrt25-vs-current36.json`).
  - [`actual-core-v1-9025ebb7`](actual-core-v1-9025ebb7/analysis.json) is the first build, kept as the record of the integer-scale and stored-coordinate regressions.

## Limits

- One signal, seed and window, and one emulator GPU. Host desktop GL is exact against actual core for Royal191 and Fed only. TV fidelity is not measured.
- Device cost is not established by this evidence; see the PR for any AM6 measurement. Per read: one fetch, or four where the reference phase is fractional, with no separate pass.
- Royal191 is a bifurcation preset (its luma ratio swings between 0.3 and 3.5 across nearby kernels). Its MAE improvement does not mean its regime is matched; at 1330 it overshoots to 1.12.
- The position-dependence pass is textual and flow-insensitive, and errs towards rewriting.
- The quarter-texel pull-in was chosen on 1330 measurements of three presets, then checked on the 68-preset screen.
