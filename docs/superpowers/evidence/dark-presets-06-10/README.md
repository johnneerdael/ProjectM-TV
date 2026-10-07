# Dark preset 06 / 10 investigation

The frozen bundles reported near-black 30-frame output at 256×144 using core
2.3.16. This investigation separates native shape coverage from authored shader
brightness. Input preset hashes remain unchanged:

- 06: `1683b34359e78a5a2ef3dc3686f384344611b52c6f947f6a9b59f2971b21a0cf`.
- 10: `ebaea03f237328932a81461f3a42b025450abbd8fae7a8014898e1428c98167d`.

## Confirmed custom shape defect

MilkDrop 2 `DrawCustomShapes` writes the authored position through the orthographic
projection in `support.cpp`, without a half-pixel position bias. D3D9 samples at
integer pixel centres. GLES samples half-integers. Copying the coordinates alone
therefore loses subpixel shapes centred at an integer D3D position. A direct
framebuffer control using `rad=.002`, `x=y=.5` rendered zero pixels before the fix,
rather than the single pixel required by the D3D9 rule.

Patch 0012 applies a half destination pixel translation to shape fills and borders
in each actual draw target. Equations, radii, colours, UVs and assets remain unchanged;
shared shader matrices are restored. The direct control now passes for
textured/untextured shapes at 256×144 and 512×288, with repeated draws, a negative
half-integer position control and matrix-restoration checks. The existing sampler
control still checks analytical bilinear weights at the corrected positions.

On the actual CI 2.3.18 AAR, preset 06 reproduces the supplied 2.3.16 RGB hash exactly.
The candidate increases its 30-frame maximum from 42 to 105 and mean RGB8 from
0.0012644 to 0.0033019 on the API34/Apple M4 Pro GLES3.0 emulator. This is evidence
of changed seed coverage, not a claim that the preset should become broadly bright.
The source still uses very small shapes, subtracts `bass/7-mid/11.2` in the warp,
and suppresses output with noise and a subtractive slow-colour composite.

## Confirmed composite sampling defect

A second independent impulse control found that the pass-through composite turns
one RGB8=255 feedback texel into four RGB8=64 pixels. MilkDrop 2 biases its D3D9
composite vertex positions by a half pixel and keeps UVs unchanged. GLES already
interpolates the unbiased grid at half-integer samples; the extra hardcoded UV
half-texel bias was therefore sampling between texels.

Patch 0013 removes that redundant composite UV bias. The production pass-through
now copies the impulse at full brightness and matches an asymmetric colour pattern
across two viewport sizes, resize reuse and repeated draws. The existing animated
Standard/plain-canvas host test now uses the ordinary authored composite instead
of subtracting the old bug's bias in a diagnostic shader; its tolerances are unchanged.
Warp texel offsets are configurable and default to zero, so that path is unchanged.

The final candidate (`d67dce98f209ec0e93e67c810e3e32be71994a15bff8df39533f06b5e9a7227a`)
contains both corrections. The earlier candidate metrics above isolate patch 0012.
With both fixes, the emulator's original 30-frame maxima are 222 for preset 06 and
9 for preset 10 (means 0.00354185 and 0.00122161 RGB8). Direct geometry and sampling
controls establish the corrections; these presets remain authored sparse/dark scenes.
All bundled assets remain byte-identical. The final five constant-composite controls
still return the same independently predicted colours.

## Preset 10: authored suppression also validated

The actual first-frame composite uniform `_qc` is `[0,0,0,0]`, confirming `q9=q12=0`.
For interior UVs, `h=q9=0` makes the water mask zero and the mirror mapping the
identity. The main/blur displacement remains. The composite then computes
`reta.x² * reta * main`, takes the `(.3,.1,.1)` branch and multiplies by 2.
A bright green/blue feedback buffer with little red can consequently yield black.
Legacy gamma, darken and video echo do not apply to custom composites.

Five controls retain the authored composite text and supply independently known
uniform feedback colours. All 30 frames in every control agree with the algebra
and RGBA8 conversion: white gives `[153,51,51]`; zero red gives black; quarter red
with .75 green/1 blue gives `[1,2,3]`; weak red gives `[0,1,1]`; white with the
explicit diagnostic `q12=1` gives `[255,255,255]`. These are diagnostic presets,
not unchanged-source appearance or randomized prediction credit.

Eight unchanged-source 900-frame runs cover both presets at 144p and 1080p,
from fresh black and after a 60-frame white seed preset. Preset 10's cold 1080p
30-second window reaches max RGB8 122 and mean RGB8 1.0802; white-history entry
reaches 153 and mean 12.8300. Its initial 144p one-second window reaches only 8.
That short cold window does not establish a failed shader or permanently black
preset. The shape-only candidate reaches 8 and the final candidate reaches 9 in that short
window. Corrected sampling does not override the authored brightness suppression.

## Local validation

- 34/34 normal and 34/34 ASan/UBSan native CGL controls and 329/329 host controls pass.
- 134 app/core JVM tests and the debug APK plus both-ABI release core build pass.
- 157 release-tooling tests, 77 Native trails/core-corpus tests (35 subtests) and strict MkDocs pass.
- The UGOOS AM6 (Android 9/API28, ARMv7 process, Mali-G52/GLES3.2) renders both original presets in paired 30-frame, 1920×1080 frozen-audio baseline/candidate runs without skipped presets or GL readback failures. The metadata and final-frame identities are in `results.json`. An additional paired API34 2560×1440 capture activates Standard trails (1280×720 authored canvas), exercising different authored/native draw targets. These are offscreen core captures; setup/readback time is not app FPS or a performance benchmark.

## Sources and scope

- Local `../milkdrop2` at `f05b0d811a87a17c4624170c26c93bac39b05bde`:
  `milkdropfs.cpp` shape geometry/sampler binding and `support.cpp` projection;
  `plugin.cpp` zero-initializes the custom audio history and uses .9 startup decay,
  consistent with the approximately 10 initial relative bass/mid values here.
- Local `projectm-visualizer.org` at `a7036b8f90046513dd2dc0be09a99879f0556cd9`:
  preset rendering order, custom shapes and memory-buffer documentation. Its shader
  input/built-in-texture pages are placeholders and supplied no evidence.
- [Microsoft D3D9 rasterization](https://learn.microsoft.com/en-us/windows/win32/direct3d9/rasterization-rules),
  [HLSL conversion](https://learn.microsoft.com/en-us/windows/win32/direct3d9/casting-and-conversion),
  and [GLES 3.0 §§2.1.6, 3.6, 4.1.8](https://registry.khronos.org/OpenGL/specs/es/3.0/es_spec_3.0.pdf)
  support the sample-centre and normalized-colour reasoning.

`results.json` records artifact/source/PCM identities, metadata, metrics and the
independent controls. Pixel/PCM captures remain untracked. The host uses frozen
clock/random inputs, disables auto changes, beat cuts and blank detection, and
includes the core's initialization renders before the measured frame serial.
Long runs repeat the frozen one-second audio transport; they do not model arbitrary
music or normal app skipping. No original Windows/D3DX rendering, whole-corpus
fidelity or performance gain is claimed.

## Release state

CI run 37639894403 built the 2.3.18 APK/core successfully but failed Preset Lab's
historical source controls because checkout was shallow. Publication and the
Milkbeat update were skipped. This PR retains full history with `filter: blob:none`
for those controls. A fresh depth-one clone reproduces the missing-source failure; a fresh full-history `blob:none` clone retrieves the identical baseline source. Reviewed PRs use trusted-main workflow definitions before merge, so the transformation tests additionally use a checked-in full baseline source fixture pinned to SHA256 `3172d17e20019cb1b34e634f108edc3b669e5a663c18d843f32abac5f15603a6`. Those tests pass in a fresh shallow checkout without changing or skipping the historical-source checks. The local candidate is not the unchanged CI artifact or an
official 2.3.18 release; the next reviewed main merge uses normal automatic versioning.
