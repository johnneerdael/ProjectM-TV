# Optional source-domain proofs

Use `--proof-python PATH` on `effect_family_export.py` to add Z3 evidence to
existing scalar value-envelope records. Prepare the isolated Python with
`requirements-source-components.txt`; the worker requires Z3 5.1.0.0. Ordinary
operation does not import Z3. The caller owns the worker and closes it at the end
of the export context.

The additional `solver_refinement` record preserves the ordinary
`nominal_value_range`, its unknown reasons and native qualifications. A proven
real range does not populate native selector domains or alter activity/appearance
predictions. Cache identity includes the worker hash, version, numeric model,
literal conversion policy and time budgets.

## Scalar and predicate queries

Consume the existing typed `Field` graph; do not parse source text a second time.
Require explicit finite input domains and pure scalar operations. Support exact
binary-valued literals after the analyser's existing float conversion, arithmetic
polynomials, abs/min/max, comparisons and selects. Reject casts, samples,
side effects, qualified storage/phase inputs and unsupported calls before any
correlated terms can cancel.

Prove proposed value endpoints by checking for violating assignments. Tighten a
conservative interval through a fixed number of binary decisions. Retain proven
outer endpoints when a later decision times out; record each unknown solver
check. This is a conservative enclosure, not a claimed optimal range. Predicate
queries distinguish always true, always false, mixed and unknown outcomes.

The ordinary model is `nominal-real`. An explicit
`ieee754-binary32-rne` predicate query uses separate binary32 operations and
checks original intermediate finiteness. Reject unrepresentable singleton input
domains and retain unresolved finiteness/feasibility. This model can demonstrate
rounding counterexamples; it does not establish the TV backend's conversion,
denormal, contraction or arithmetic behavior. Both models report
`native_numeric_certified: false`.

## Main-frame invariant evidence

Call `equation_domains.main_q_domain_evidence` with a source reader record,
equation-loader policy and explicit candidate bounds for private persistent
state. The result returns the existing `native_domains` separately from the
optional `nominal_proof`.

Check the actual accepted initialization and ordered frame trees. Prove that
initialization establishes every candidate, then that the complete transition
preserves it. Reload the post-init snapshots of Q1–Q32 each frame, reset host
inputs and built-in controls, and require explicit domains for reset values that
the program reads. Retain sequential assignments; do not treat them as
simultaneous equations. Prove frame Q outputs only after both induction
obligations succeed. Never substitute a finite number of observed frames for
induction.

Reject shared registers without a cross-phase adapter, per-pixel mutation,
unknown initialized storage, effects and unsupported arithmetic. A failing
initialization or transition returns its obligation and solver counterexample.
Candidate generation and stronger native EEL/float transport proofs remain
separate work.

## Reproducible source census

Run `source_proof_validate.py` against a frozen sample manifest and a
hash-identified native reader. This census compares consumed main/per-pixel/shape
scalar graphs under declared audio-band ranges [0,2]. It records new nominal
bounds, tighter bounds, unsupported/unknown/unavailable outcomes and processing
cost independently. It excludes a shader-field census and corpus-wide native
state inference. No equations, shaders or frames are executed.

```bash
build/preset-lab-venv/bin/python tools/milk-analyzer/source_proof_validate.py \
  --reader build/preset-corpus/source31/adapters/milk-native-reader \
  --proof-python /path/to/prepared/python \
  --sample-manifest build/preset-corpus/source-random-2000-2026-10-10/results-run/run-manifest.json \
  --output build/preset-corpus/source-z3-census --workers 4
```

Keep all terminal outcomes and source identities. A useful hypothetical-domain
bound does not establish simultaneous input reachability, temporal speed,
visible audio response, mood accuracy or physical-device performance.
