# Direct shader RGB partial source-time response

This source-only checkpoint adds raw shader RGB rate ceilings after scalar
projection, retaining independent `[0,1]` sampled colour inputs held fixed.
It performs no image construction, shader execution or frame inspection.

## Fixed 100-preset sample

All original sample presets export successfully with the pinned source34 reader,
sealed compile manifest and declared audio/canvas scenario. Exact names, stages
and rate ceilings are recorded in `time-response-census.json`.

- Default: 63 presets have at least one resolved partial RGB rate component.
- Declared scenario: 64 presets have at least one resolved component.
- Six presets have positive partial rate ceilings, in both default and scenario
  groups. There are 14 positive stage/scenario records, including overlap.
- Zero additional positive presets are gained solely by the scenario.

Do not count zero partial rates as static images or calm presets. Texture sample
motion/history, geometry, audio/state changes and later feedback remain excluded.
Resolved upper bounds need not be reached and do not establish average intensity.

## Controls and interpretation

Nine new controls cover sample-modulated sine pulses, sample-coordinate-only
time variation, discontinuous thresholds, time-dependent Q uploads with unaffected
lanes, declared audio amplitude bounds, packed `_c2.x`, native oscillator uniforms,
singular contributing factors and linkage into the activity export.
Seven original controls failed before the new field was implemented. The activity
linkage control separately failed before integration. A test's bass-premise key
was corrected to the actual native packed alias `_c3.x`; the bound itself remained
unchanged and its provenance was inspected directly.

Independent review ran 84 focused tests and found no actionable issues. Clock
aliases, Q/narrow taint, held-fixed sample scope and default/scenario separation
were checked. Mathematical controls do not certify whole-preset appearance.

Prepared full suite: 2,937 tests and 92 subtests passed in 167.47 seconds.
All 100 source-appearance records validate the current JSON Schema. Strict MkDocs
and diff whitespace checks pass.

Local preserved outputs under `build/preset-corpus/`:

- `source-shader-time-red.log`
- `source-shader-time-2026-10-10/`
- `source-shader-time-suite.log`
- `source-shader-time-docs.log`

The JSON export documents fixed samples, excluded coordinate response, declared
domains, unresolved reasons, null total RGB rate and null visible flash frequency.
The referenced original MilkDrop2 `milkdropfs.cpp`, lines 3946–3978, binds wrapped
preset-local shader time separately from the native oscillators' elapsed clock.
The model treats nominal clock advancement between resets/wraps, following the
declared core contract; phase origins and finite-precision uploads remain separate.
See the public guide and `SOURCE_APPEARANCE.md` for units and shader references.

No AAR/native code or authored presets were changed. This is source interpretation
progress, not new native runtime or mood certification.
