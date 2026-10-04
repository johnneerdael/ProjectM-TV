# Single-pass raw/filtered routing (patch 0030 fix)

Snapshot: 2026-10-04. Branch `bug/native-4k-feedback-fidelity`.

## Defect

In candidate30 (`790aaa24`), the diffusion texture became the warp's `mainTexture`, so every main
descriptor read globally filtered state:

- Warp point samplers (`sampler_pw_main`, `sampler_pc_main` and aliases) bound to the filtered
  texture. `GL_NEAREST` at the sampler cannot undo the earlier blur, so state encoded in colour
  channels was averaged.
- In P2 placement, the composite shader and the old-school composite (video echo, filters) read the
  filtered final flip. This violated design requirement F3 (unblurred composite).

The private raw-point/P1 diagnostic established that routing point samplers to the raw frame
changes Mandelverse and Royal255 substantially. That diagnostic paid for P1 with an extra input pass.

## Change

`FeedbackDiffusion` draws one full-screen pass with two render targets:

- Location 0 is an exact y-flipped copy (`texelFetch`).
- Location 1 is the filtered copy (the unchanged 3/4-tap kernel).

Routing:

- `MilkdropShader` binds warp descriptors whose bound sampler is `GL_NEAREST` to the exact copy
  (`PresetState::rawMainTexture`). It binds all other descriptors to the filtered copy. Unit 0 stays
  bilinear, as before.
- The end-of-frame pass replaces the flip. The composite reads the exact copy, and both copies
  become the next frame's warp inputs.
- Motion vectors drawn onto the previous canvas trigger a recomputation before the warp.

Cost:

- Full-screen pass counts equal the uncompensated path: one per frame, or two in frames with motion
  vectors.
- Each pass writes one extra colour target.
- An active preset holds one more render-size RGBA texture.

## Host regressions

The engine-level tests in `FeedbackDiffusionRenderTest` compare compensation on against compensation
off at the same reference size. "Off" uses a gated `GetPixel(uv_orig)*0.0` term, because the reference
also changes `texsize` and the canvas size the preset sees.

On the previous 0030 these fail:

| Test | Previous 0030 | Differing bytes |
| --- | --- | --- |
| Point aliases `pw_main`, `wp_main`, `pc_main`, `cp_main` at scale 2 and 4 | Fail | 12,832–13,568 |
| Shader and point-sampled composites at scale 2 and 4 | Fail | 12,384–24,672 |
| Bilinear-read guard | Passes | — |

With this fix, all of them pass. `FeedbackDiffusion.OnePassWritesExactFlippedCopyAndFilteredCopy`
checks the raw output for exact byte equality, flipped and unflipped, on a non-square texture.

The three `WarpSamplerTest` regressions come from `02504a3a`: packed point state, mixed routing,
and unchanged output at/below the reference. The host suite passes 197/197.

The vertex and fragment shaders link as GLSL ES 3.00 (`glslangValidator -l`). Removing the fragment
shader's `precision highp int` makes linking fail ("Precision qualifiers must match:
flip_vertical"), so that line is required on GLES drivers.

## Actual-core emulator comparison

`build_mrt_fix.py` builds `25e6aa83` through the shared provider with the same private RNG/time
instrumentation and no private renderer edits. `run.py` renders the six raw-point presets on the
owned emulator-5582 (Apple M4 Pro translator):

- Sizes 1330 and 2160.
- Seed 12345, 480 frames, eight selected captures.
- Two fresh-process repeats per case.

**Results** (`results.json`):

- All 96 selected native RGB frames are byte-identical to the raw-point/P1 diagnostic.
- All 12 repeat pairs are exact.

The product therefore inherits the diagnostic's measured routing improvements without its extra
input pass:

| Preset | Size | P1 image MAE | This fix | Luma ratio (P1 → fix) |
| --- | --- | --- | --- | --- |
| Mandelverse | 2160 | 0.2329 | 0.1269 | 0.876 → 1.035 |
| Royal255 | 2160 | 0.1649 | 0.0917 | 0.952 → 0.958 |
| Royal255 | 1330 | 0.1687 | 0.1201 | 0.947 → 0.885 |

- Image MAE is 1182×665 area-reduced RGB error against classic29 ref0, averaged over the 12 s
  window.
- Royal191, Fed quadratrail and astral nz+ are unchanged and remain darker than classic. Their
  max/peak recurrence defects are independent of routing.
- Commit `b7811b19` adds only tests and the patch header; the renderer source matches `25e6aa83`.

**Artifact identities:**

| Artifact | SHA256 |
| --- | --- |
| APK | `913fa839dafc5497dd830f991767a318acfcb39570b54536bd460b22063fb81b` |
| AAR | `2ef7bdaba8d6b080026f2ace04d7439bf001076999d9e45cd685de4455511da2` |
| ARM64 ELF (APK = AAR) | `63df469c2f159a8703af2be16c4bea2574432162ac761efd97941f55cc0e7723` |

`analysis.json`, `comparator-index.json` and `source-results-manifest.json` hold the per-frame
metrics, the hash-verified comparator rows and the file hashes.

The raw captures (3.9 GB) remain in `build/native-4k-current-main/mrt-fix-validation/` of the
recovery worktree. They are not yet in an external backup.

## Limits

These results come from one emulator GPU stack, one seed and signal, and six presets. The workers are
instrumented lab builds, not shipping bytes. They make no claim about TV fidelity or frame rate.
