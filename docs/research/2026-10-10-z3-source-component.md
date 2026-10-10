# Z3 source-domain component qualification

The optional adapter can check declaration-bound scalar expressions and
candidate main-frame invariants using Z3 5.1.0.0. Its fixed 2,000-source scalar
census found **no new finite bounds and no tightening above 1%**. Keep the
component opt-in and supplemental; this evidence does not justify changing
native selector domains or prediction defaults.

## Measured outcomes

Use the existing immutable sample from
`source-random-2000-2026-10-10/results-run/run-manifest.json`, preserving each
preset hash. The census reads the exact sources through the hash-identified
`source31/adapters/milk-native-reader` and lowers their consumed
main/per-pixel/shape scalar graphs. Explicit audio-band domains are [0,2].
Other inputs, state and native conversions retain their existing guards.

| Outcome | Result |
|---|---|
| New supported calculations | 562 qualified scalar solver queries; zero previously unresolved scalar envelopes became finite |
| Tighter estimates | 514 smaller nominal enclosures across 307 presets; zero exceeded 1% range-width improvement |
| Predictions and unknowns | Existing prediction/native ranges unchanged; 17,382 unsupported queries, zero unknown solver checks or unavailable sessions |
| Processing cost | 17,944 control queries; 4.29 seconds cumulative query time, 9.40 seconds source graph analysis, 208.81 seconds wall time including native parsing; slowest preset 1.576 seconds |

Every one of the 2,000 source records completed. Supported real expressions
mostly improve small endpoint-enclosure differences. The census excludes shader
fields and corpus-wide persistent-state inference. Its results do not establish
appearance, mood or visible audio-response accuracy. A full 9,606-source scalar
rerun was not justified by this sample's zero material gains.

## Qualification after stronger guards

The first frozen census preceded three guard corrections: preserve the original
value calculator's explicit overflow/domain failures before cancellation;
reject phase-qualified input names without a binding adapter; and reset only
actual Q1–Q32, keeping `q999` private persistent storage.

Recheck all **334 source cases containing the 562 previously supported queries**
with the corrected implementation. Preset/engine identities, status counts and
all 514 changed ranges are identical. No supported query was lost. This recheck
took 33.68 seconds wall time and 3.12 seconds cumulative query time, with zero
unknown checks or unavailable workers. The other 1,666 previously unsupported
source cases were not rerun; the corrections only strengthen the scalar guards.
The exact-Q correction affects the separate invariant entrypoint, which the
scalar census does not exercise.

The archive keeps the original frozen census, corrected supported-case recheck,
comparison record, final qualified module snapshots and independent controls.
It does not relabel the original run as having used the corrected implementation.

## Actual source-domain controls

Native-reader controls validate the additional invariant entrypoint against
real accepted equation trees:

- Initialize `counter=0`, then run
  `counter=min(1,counter+.25);q29=counter;`. Candidate private-state domain [0,1]
  passes initialization and complete ordered transition proofs; nominal q29 is
  [.25,1]. The existing native interval entrypoint cannot infer this min-based
  domain, and its output remains unchanged.
- Replace the update with `counter=counter+1`: the transition fails with a
  counterexample. Initialize `counter=-1`: initialization fails.
- Preserve sequential assignments and the actual main-Q post-init snapshot
  reload. A private variable named `q999` cannot receive that reset policy.
- Retain shared-register, per-pixel mutation, missing-domain, malformed-program,
  unknown-storage and intermediate-overflow negatives.

These are synthetic native-reader controls, not evidence of new corpus support.
Candidate generation remains explicit. The proof establishes a nominal real
inductive property only; it does not establish native EEL rounding, post-frame
float32 transport or reachability of every state in the candidate domain.

The same expression `(1+x)-x == 1` is true in the real model and false at binary32
`x=16777216`. Separate explicit binary32 RNE operations produce the counterexample;
an independent Python `struct` binary32 conversion witness also produces zero.
Unrepresentable singleton domains and potential nonfinite intermediate values
cannot produce vacuous proofs. No TV/backend arithmetic was measured.

## Evidence and checks

The [evidence archive](evidence/z3-source-component-2026-10-10.zip) has SHA256
`61f73fd1234b949697c1d66ecb35bb78700671a6cb34c979281f505aa5314469`.
Its corrected recheck manifest has SHA256
`0e4947908eea3b28a29fba42efeadbc59b32c9e347e423570cdc5b1726203aa1`.
The archive includes all sample/result identities, terminal source counts,
version/time-budget provenance and checksummed qualified implementation files.
ZIP integrity and every listed artifact hash were checked.

The focused proof, existing symbolic and equation-domain suites pass 57 controls:

```bash
env MILK_PROOF_PYTHON=/path/to/prepared/python \
    MILK_SYMBOLIC_PYTHON=/path/to/prepared/python \
    build/preset-lab-venv/bin/python -m pytest \
    tools/milk-analyzer/test_source_proofs.py \
    tools/milk-analyzer/test_source_symbolic.py \
    tools/milk-analyzer/test_equation_domains.py -q
```

The new overflow, qualified-name and private-Q reset controls were observed
failing before their corrections, then passing. Timeout, worker shutdown,
unknown-result and pinned-version mismatch controls retain unresolved outcomes.
The implementation reuses the existing bounded nonblocking worker transport;
it adds no Android runtime dependency. See
`tools/milk-analyzer/SOURCE_PROOFS.md` for API and reproduction details.
