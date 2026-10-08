# Validation and evidence

A visualizer change is easy to get subtly wrong. A one-texel shift in a feedback preset becomes a different picture ten seconds later, and every GPU driver interprets edge cases its own way. ProjectM TV therefore separates three questions and answers each with its own evidence:

1. **Does the change do what it claims?** Native regression controls and single-patch ablations.
2. **Did it change anything it should not?** Frozen fixed-seed comparisons across releases.
3. **What does the evidence not cover?** Stated explicitly with every result.

## Deterministic rendering

Comparing two renders is meaningful only if everything except the engine is frozen. Evidence runs fix:

- **Audio:** a stored PCM stream, identical for every run.
- **Clock:** time advances exactly one frame per frame (frame/30), not by wall clock. projectM's internal timer origins are frozen too.
- **Random numbers:** seed 12345 for the evaluator. Production random-texture choices use `std::random_device`, so evidence records which image was actually bound.
- **Mesh and size:** for example a 48×32 warp mesh at 512×288 or 1920×1080.
- **Identity:** SHA-256 of the preset, textures, engine source, patch series, built binary and PCM, recorded with every result. A result whose inputs cannot be identified is not used.

Each role is run at least twice. Its frames must repeat byte for byte before any comparison counts.

## Regression controls

`core/src/test/native/run_native_tests.sh` builds the patched engine with AddressSanitizer and UndefinedBehaviorSanitizer and runs real-GL controls, including:

| Control | Checks |
|---|---|
| `shader-parser-regressions`, `parser-presets` | HLSL constructs plus 16 unchanged bundled presets whose shaders failed before (hash-pinned) |
| `float-literal-regressions`, `float-literal-presets` | Bit-exact float32 round trips, locales, nonfinite rejection, 95 hash-pinned shader sections |
| `random-texture-*` | Slot identity, sampler modes and texel values against known textures |
| `shape-sampler-regressions`, `blur-range-regressions`, `warp-zoom-regressions` | Effective sampler state at real draws, blur normalization, vertex UV readback for signed zoom |
| `dynamic-wave-controls`, `dynamic-display-controls`, `dynamic-original-presets` | Per-frame waveform and display controls against static controls, in all Native trails paths |
| `warp-rotation-regressions` | Signed, moderate, large and maximum finite rotation angles across four feedback frames |
| legacy compatibility controls | Constant-colour output with disabled and fractional `fShader`, mode-1 waveform opacity and open-strip topology against MilkDrop 2.25c expectations |

`tools/projectm-host-tests.sh` runs projectM's own GoogleTest suite with the patches applied (329 tests at the 4.2 rebase).

## Release-to-release fidelity

When the engine moved from projectM 4.1.7 to 4.2 master, the rebased renderer was compared with the published v2.3.15 release:

| | |
|---|---|
| Presets | 100 randomly selected + 351 required regression witnesses (447 bundled, 4 overlaps) + 1 external witness |
| Profiles | 448 at 1080p + 61 at 4K (Native trails Standard, Medium, High) = 509 comparisons |
| Runs | 509 × 2 engines × 2 repeats = 2,036 fixed-seed runs |
| Result | Every RGB frame 0–479 identical across engines and repeats: 977,280 frame hashes, zero changed |
| Backend | API34 ARM64 Android emulator, Apple M4 Pro GPU, GLES 3.0 |

This establishes that the migration preserved behaviour on that set. It does not establish correctness against MilkDrop 2, cover all 9,606 presets, or cover other GPUs. It predates patches 0010–0013. [Evidence](https://github.com/johnneerdael/ProjectM-TV/blob/main/docs/superpowers/evidence/upstream-master-4-2/fidelity-final/README.md).

## Single-patch proof images

The [patch catalog](patches.md) images come from rendering each witness three ways:

- upstream with only the GLES 3.0 admission;
- the full series *without* one patch;
- the full series.

A difference between the second and third proves that patch is responsible. A full-series image alone does not: 0001 is too broad to remove in isolation, so its image shows only that the preset now loads.

The capture checkpoint holds 31 images from 134 successful runs. Ten failed runs are retained alongside them, with their diagnostics, rather than discarded. Proof workers disable the shader binary cache because of an emulator driver error, so the images do not validate caching.

## What is not claimed

- **Windows appearance.** No Windows/Direct3D reference renders exist in this project's evidence. MilkDrop 2 behaviour is established from its released source code, not from screenshots.
- **Every TV.** Device checks ran on NVIDIA SHIELD TV (Tegra), Ugoos AM6 (Mali-G52) and Ugoos AM9 (Mali-G310) at various times, and on emulators. Other GPUs may differ, especially for GLES 3.0 float render targets.
- **Performance.** Historical speedups were measured on the 4.1.7-era engine and are not re-claimed for 4.2.
- **The whole library.** No change is certified across all 9,606 presets.

## Continuous integration

Every reviewed pull request and every merge to `main` runs, before anything is published:

- the JVM tests;
- the native sanitizer suite;
- the asset checks (`tools/check-presets.py`, `tools/gen-preset-index.py --check`);
- Preset Lab and source-analysis tests;
- a verification of the shipped mood-collection bundle (source hashes, measurement provenance, score calculation, membership);
- a strict build of this guide.

A merge publishes a versioned APK and core AAR only after the full suite passes.
