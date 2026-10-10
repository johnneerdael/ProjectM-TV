# Optional SymPy component qualification

Date: 2026-10-10. Base branch `feat/predictor-static-output-bounds` at
`472b97c1`; exact qualified implementation hashes are in `manifest.json`.

The optional pinned SymPy 1.14.0 worker accepts existing pure scalar source
graphs, generates derivatives and lowers them to our existing range calculus.
It is opt-in; original casts, phase bindings, state and finite-domain obligations
remain authoritative. This introduces no app/core runtime dependency.

## Measured contribution

All 9,606 unchanged preset sources were parsed. The census compares audio-dependent
mesh (per-frame/per-pixel) and custom-shape controls, not custom shader fields.
The historical runner/manifest shorthand `main/shape` means this mesh/shape scope.
Both unconstrained finite inputs and an explicitly declared band [0,2] scenario
are retained; the latter is a premise, not an observed universal audio bound.

- 11,295 tighter nominal bounds across 1,756 presets.
- Only seven comparisons across six presets tighten by more than 1%; the remaining
  changes are small numerical enclosures and are not counted as material gains.
- Zero previously unknown bounds resolved.
- Zero unavailable workers and zero top-level source parsing failures.
- 255,171 unsupported and 1,771 still-unbounded control comparisons remain explicit.
  These are control queries, not distinct presets. Zero top-level failures does
  not mean complete language/behaviour understanding.

`material-cases.json` identifies every >1% change with source hashes and band/control:
Flower V2 rotation tightens 0.2 to 0.1; five shape-angle cases tighten 4 to 2 under
the declared audio domain. Both count repeated scenario queries separately.

Four workers completed the census in 964.31 seconds. Median paired per-preset
work was 0.391 seconds, p95 0.518, maximum 0.892. These costs include source parsing
and both baseline/trial calculations, not an isolated SymPy cost or speedup.
The complete prepared analyzer suite passed 3,173 tests plus 92 subtests in
256.01 seconds. A separate full-controls 100-source export passed its JSON schema
with unchanged model hashes and no rendered reference.

## Failure retained and repaired

The first trial used broad trigonometric simplification. One small six-band formula
exceeded the request deadline; sessions then correctly disabled the backend.
That incomplete trial cannot establish full-pack component availability.
`source-components-worker-failure.json` preserves the exact case.

The repair uses the targeted SymPy TR8 product-to-sum transform and rejects
unsupported source graphs before worker startup/IPC. The same failed preset was
retested successfully before the full requalification; the repair record is
retained. Deadlines remain necessary: a node budget is not a complexity proof.

## Boundaries and disposition

The calculus is nominal real arithmetic, not a finite-precision EEL/GPU theorem.
Bounds cannot erase original invalid/nonfinite-domain obligations. Native
conversions, textures, storage-qualified inputs and effects remain unsupported
in this adapter. No frame, audio or shader execution was performed.
No whole-preset image, mood, flashing or genre accuracy follows from these results.

Keep this small component optional. Its measured material benefit is limited,
but it removes bespoke algebra work and provides derivative programs for later
input/state proofs. Step 2 uses Z3 to address those premises rather than
expanding SymPy indiscriminately. No engine change or main merge is included.
