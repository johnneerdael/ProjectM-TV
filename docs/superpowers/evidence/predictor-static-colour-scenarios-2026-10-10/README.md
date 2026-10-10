# Quantized and declared-scenario colour bounds

Final source-only fixed 100-preset checkpoint. Value-only floor/frac rules supplement existing nonlinear bounds; validated caller scenarios add a separate colour envelope while ordinary stage records remain alongside it.

- 71 ordinary complete colour-stage bounds, up from69; 74 complete under the declared scenario.
- Five presets gain complete stage bounds relative to the prior checkpoint: two through floor/frac, three through caller premises.
- 58 presets have at least one complete scenario colour stage.
- Three ordinary stage records change; source-gap inventories unchanged.
- Exact preset/ZIP/result joins and work budgets verified for all100 originals.
- Final prepared analyzer suite: 2,871 tests and92 subtests passed in164.86 seconds.
- Root81 focused tests, independent83 focused tests and strict MkDocs pass. Final independent review reports no outstanding actionable findings.

Scenario: six engine bands [0,2], explicit shader canvas854x480 and independent sampled RGBA [0,1]. These are nominal value enclosures, not average brightness, a palette, temporal continuity, flashes, whole feedback or mood accuracy. Missing bands and invalid/native-upload domains remain guarded.

Nine added controls include negative frac bins, seam crossings, absence of rate credit, quantized floor levels, singular expressions, separate scenario/default records, missing bands/nonfinite Q uploads, original bass premise through Q upload, and exact large integer endpoint enclosure in both signs. Eight tests failed for missing behavior before implementation. The floor multiplication control uses enclosure rather than exact equality because existing outward padding can include another level.

Review caught two predictor issues before commit: scenario domains were accidentally removed from the finite-premise summary through an upload; ordinary float conversion could exclude a valid exact floor integer near10^16. Both have preserved RED regressions and verified fixes. Local sample/derived placeholders are excluded while original input names remain; floor endpoints convert outward or abstain. Earlier frozen outputs/suites are retained as pre-repair checkpoints and are not the final artifact.

References: [HLSL floor](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-floor), [HLSL frac](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-frac). MilkDrop2 delegates the shader intrinsics to D3DX; patched GLSL uses floor/fract. No renderer or authored preset changes.

Final raw artifacts: `build/preset-corpus/source-colour-scenarios-final-2026-10-10/`; adjacent final export/suite/docs and earlier RED logs retained. Census binds affected names/hashes, source/reader/model/archive and scenario identities. Latest published v2.3.36 remains byte-identical to the verified full local v2.3.34 AAR checkpoint; source34 adapters are used, with Android runtime qualification separate.
