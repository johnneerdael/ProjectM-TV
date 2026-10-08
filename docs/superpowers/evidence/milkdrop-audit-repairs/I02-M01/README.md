# I02 and M01 — nonzero file flags

Candidate0027 changes the shared production `GetBool` comparison from `>0` to `!=0`. Negative parsed integers enable main effects and custom wave/shape flags as in MilkDrop2. Preserve integer-prefix parsing, invalid/range defaults, normalized first occurrence, casing and unconditional initialization. No recognized negative first-occurrence flags were found by the actual production parser across all9,606 stock files; this is loading evidence, not a whole-corpus visual census or a claim about custom packs.

## Executable proof

Real CGL production parser/state/wave controls fail before the one-line repair:72 parser assertions,6 zero-sample frame-gate assertions and18 two-point drawing/replay assertions. After repair the combined renderer suite passes53/53. Actual authored64 and Native128 targets show finite red geometry for negative and positive enable values, and no geometry for zero. Initialization executes once for all variants. Over two frames, enabled waves execute one frame program and two points each frame; Native replay adds no equation evaluations. Following main-frame Q sees the previous wave register write. Each pixel check explicitly binds the intended read target. [RED](source-red.txt) · [Normal53](source-normal53.txt).

The local analyzer's `source_context.scalar` used the same positive-only conversion. It now matches native nonzero integer semantics. Focused integer-prefix/range/default controls fail5 before repair and pass21/21 after. Its existing stage-resolution negative-wrap assertion is updated; source-bound adapter/full analyzer validation remains a separate gate. [Analyzer RED](analyzer-red.txt) · [GREEN](analyzer-green.txt). External predictor `scene_equations.py` is outside this checkout and remains a coordinated contract followup.

## Remaining Native acceptance

Final-output Android Native4K invert/two-point controls, wrap sampler edge control and source-bound ARM builds remain pending. Negative enable values activate authored equations/draws that the prior loader skipped; this is a real increase in workload for such external inputs, and no universal zero-cost claim is made. No affected stock original has been confirmed. Current acceptance is source-stage only; this candidate is not certified for merge.
