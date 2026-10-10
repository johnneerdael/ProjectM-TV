# Nominal coordinate interpolation

Source-only fixed 100-preset recheck. Uniform scalar lerp weights distribute across ripple terms and uniform-affine phases. Equal spatial baselines use A+t*(B-A); offsets retain explicit interpolation. Local sampled weights remain independent parameters, not uniform images.

- 33 additional complete scenario sampling-site bounds across six already covered presets.
- 34 changed sampled-offset reports across seven presets; the seventh correctly remains image-dependent spatial scaling.
- No new unconstrained complete offset models. The number with at least one complete conditional site stays 36.
- All 100 originals computed without work-budget exhaustion; source-gap inventories unchanged. Exact source/ZIP joins verified.
- Prepared analyzer suite: 2,850 tests and 92 subtests passed in 164.75 seconds.
- Root focused checks: 62 tests passed. Independent review: 61 focused tests passed, no actionable findings.
- Strict MkDocs and diff checks passed.

The six new controls cover blended ripple branches, affine phase interpolation, spatial weights, zero-weight invalid branches, fixed image-offset blends and equal-baseline image-weight blends. Four positive controls failed before implementation. No source preset or renderer is changed.

Scenario premise: six engine bands [0,2], shader canvas 854x480, independently sampled RGBA [0,1]. This is not measured audio, texture contents, visible speed, feedback stability or mood certification. Native precision remains separate.

References: [official HLSL interpolation math](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-lerp); original MilkDrop2.25c `vis_milk2/plugin.cpp:3437` compiles shaders through D3DX; pinned patched source34 `vendor/hlslparser/src/GLSLGenerator.cpp:1213` maps lerp to mix.

Raw checkpoint: `build/preset-corpus/source-coordinate-blends-2026-10-10/`. Adjacent export/suite/RED/docs logs are retained. Census includes exact affected names/hashes, per-site before/after models, scenario/source/model/archive identities. Latest verified published core is v2.3.36, byte-identical to the local full v2.3.34 AAR checkpoint; Android runtime qualification remains separate.
