# Source component adoption implementation plan

> **For agentic workers:** Use the executing-plans workflow in the existing
> `predictor-memory-repair` worktree. The user approved the component report and
> authorized full 9,606-source validation. Keep original predictor-maths work
> paused; implement the component additions in order with separate evidence.

**Goal:** Incorporate useful existing symbolic/compiler components, measuring
their real contribution before expanding or promoting them.

**Architecture:** Existing native parsing, typed graphs and baseline bounds stay
authoritative. Optional isolated workers consume bounded pure source graphs;
results supplement baseline records with version/source/domain provenance.
Native conversions, state, texture inputs and unresolved cases remain explicit.

**Tech stack:** Python source analyzer, pinned SymPy1.14.0/Z35.1.0.0, existing
glslang/SPIR-V CLI tools; no new Android dependencies or new worktree.

## 1. SymPy derivative and range adapter

Files: create `source_symbolic.py`, `source_symbolic_worker.py`,
`test_source_symbolic.py`, `requirements-source-components.txt`; modify
`source_control_bounds.py`, `effect_family_export.py`, analyzer documentation.

- [x] Write controls before implementation: correlated polynomial/trig derivative,
  a nonzero derivative bound, a state multiplier retaining null, typed cast/sample/
  side-effect rejection, bounded worker timeout and clean close, optional-off parity.
- [x] Run `build/preset-lab-venv/bin/python -m pytest tools/milk-analyzer/test_source_symbolic.py -q`
  and verify the missing-feature failure.
- [x] Implement a persistent optional worker context with bounded node count,
  response deadline, exact rational constants and no source-text evaluation.
- [x] Generate derivatives through SymPy; lower supported derivative expressions
  into the existing scalar-value range calculator with outward rational enclosures.
  Preserve original source/domain obligations and baseline bounds in the result.
- [x] Expose opt-in CLI configuration and provenance/cache identity. Default-off
  output must remain substantively identical.
- [x] Run focused controls and prepared suite, then source-only benefit validation
  over the fixed sample and full pack if needed. Count new/tighter actual bounds,
  unknowns, timeouts and cost. Freeze the model during qualification.
- [x] Review, document exact cases and commit/push the tested step.

## 2. Z3 proof component

Files: extend the isolated worker/client protocol and tests; integrate only with
existing source-domain entry points whose inputs/numeric contract are explicit.

- [ ] Add proof controls for declaration-bound polynomial predicates, a bounded
  recurrence and an unbounded mutation, format/order negatives and timeout unknown.
- [ ] Lower only qualified graph operations, retaining real versus native-FP scope.
  Reject unsupported functions, unknown storage, missing domains and effects.
- [ ] Consume proofs as additional domain evidence, preserving initialization,
  reset and transition obligations before any recurrent-state claim.
- [ ] Measure changed calculations and exact affected source cases; run full-pack
  source checks when focused/sample evidence cannot establish practical value.
- [ ] Review and commit the step; keep unsupported constructions explicit.

## 3. Compiler analysis components

Files: add an auxiliary wrapper/evidence exporter around installed glslang,
SPIR-V Tools and SPIRV-Cross. Reuse their APIs/CLI rather than another binary parser.

- [ ] Add exact GLES300 AST and labelled ES310 inspection controls; preserve original
  shader/preset/tool hashes and auto-binding/profile distinctions.
- [ ] Apply selective passes and function summaries; test casts, loop/control-flow,
  samples and source joins. Do not blanket inline helper code or promote inspection
  results to native runtime equivalence.
- [ ] Compare information recovered with current live source slices and report
  actual additional useful facts/cost before integration.
- [ ] Add Stims fixture/pattern components with adapters for our actual host rules.
- [ ] Evaluate Slang/Crab/Naga against remaining named gaps; more adapter work is
  allowed when it saves substantial bespoke work. Keep low-risk useful small
  additions eligible. Update evidence and commits after each verified component.

## Acceptance

Report new supported calculations, tighter estimates, changed predictions/unknowns
and processing cost independently. Do not translate compiler success into appearance
accuracy, nor infer a 10k improvement from a toy control. Retain negative/failed
fixtures, exact full-pack denominator and all terminal outcomes. No shared devices,
captures or duplicate render corpus are needed.
