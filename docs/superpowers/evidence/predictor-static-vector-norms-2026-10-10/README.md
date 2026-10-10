# Nominal vector length and distance

Source-only fixed100 checkpoint. Length/distance preserve typed scalar components; distance subtracts before norm. Component boxes give lower/upper hypot enclosures. Reverse triangle inequality gives norm response ceiling hypot(component ceilings), including at zero. Native quantization, singular components, mismatched widths and matrices stay guarded.

-Ordinary complete colour stages:76 versus71; five new stage bounds.
-Scenario complete colour stages:81 versus74; seven new stages across seven presets.62 presets have at least one complete scenario colour stage, versus58 previously (stage gains can occur within already covered presets).
-Direct colour response: six presets with positive bounds, versusfive; nine fully bounded scenario band routes, versussix.
-Time component coverage unchanged. Source-gap inventories unchanged; all100 source/preset/ZIP/result joins and work budgets verified.
-Full prepared suite:2,900 tests and92 subtests pass in166.61 seconds. Root99 focused tests, independent105 focused tests, strict MkDocs and diff checks pass.

Nine controls cover signed vector boxes, zero-origin response, sampled-colour magnitude, point distance, singular components, raw vector domain names, invalid types/widths, quantized response and multiple temporary distances. Four initial positive tests failed for missing norm support. Review then found a P1 predictor memo collision: ID-only caching of temporary subtraction nodes could return20 for a sum that must equal210. The preserved RED regression reproduced it; retaining(original node,result) and checking identity fixes repeated runs. The faulty version was not committed or qualified as final evidence.

Bounds assume relevant finite source intermediates and declared sampled RGBA[0,1], with the supplied band/canvas scenario explicit. They are nominal enclosures and sufficient response ceilings, not minimum/typical reaction, normalization proof, final geometry, visible brightness/motion, feedback or mood certification. Source component correlations can make the bounds loose. Divide/normalize by a norm touching zero remains singular.

References: [HLSL length](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-length), [HLSL distance](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-distance). Original MilkDrop2 uses D3DX intrinsics; patched GLSL keeps the corresponding built-ins. No renderer or preset changes.

Raw final checkpoint:`build/preset-corpus/source-vector-norms-2026-10-10/`; adjacent suite/export/docs/RED logs retained. Census files record exact affected names/hashes, matching-scope stage gains, bounds and reader/source/model/scenario/archive identities. Reader source34 matches the verified byte-identical full published2.3.34–2.3.36 AAR checkpoint; Android runtime qualification remains separate.
