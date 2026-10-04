# Full-corpus audience scoring and ProjectM-TV review build

The user authorized scoring every shipped preset, diagnosing remaining unscored
entries, regular commits/pushes to a feature branch, and a ProjectM-TV debug build
with All, Chill, Normal and Party for their evaluation.

## Output contract

- Inventory the exact shipped corpus by path and SHA-256. Include every file;
  do not replace failed cases or silently reduce the collection.
- Store a finite absolute intensity score from 0 to 100 for every preset, the
  scoring-model identity, audio/input profile, execution backend and relevant
  evidence. Missing values remain visible until diagnosed and resolved; do not
  assign a fabricated midpoint or zero to an unsupported calculation.
- Keep collection-relative 1–100 rank separate from absolute intensity. Preserve
  ties. Relative rank alone does not establish Chill/Normal/Party membership.
- Generate inclusive, overlapping groups: Chill 0–30, Normal 25–75, Party 70–100.
  All contains the complete corpus once. Group overlaps are intentional.
- Use the user's five-percentage-point tolerance when validating judgments;
  do not silently expand category membership thresholds by that tolerance.
- Preserve historical/frozen predictions. Source fixes and later measurements
  receive distinct versions; development agreement is not independent accuracy.

## Scoring and review

Reuse the current source reader, mathematical execution and numerical activity
descriptors. Freeze model weights and scoring parameters for each collection
generation. Review missing-domain, missing-input, nonrendering and measurement
failures independently instead of treating all absent metrics as calmness.

The user approved native projectM numerical execution for incomplete interpreter
cases and AI video inspection to learn correct behavior when knowledge gaps
exist. Label execution backends explicitly; native measurements are not
independent predictions. Keep diagnosis/learning separate from frozen scoring
results and independent human audience validation.

Use ProjectM-TV `:core` as the numerical backend, including this project's
patch series and renderer defaults. Pin the AAR and native-library hashes;
unmodified upstream projectM is not an equivalent scoring backend.

The debug app consumes generated group indexes and scoring metadata, defaults to
All, and makes the selected preset's score identifiable during evaluation. Use
the current ProjectM-TV code and engine after reconciling the feature branch with
upstream. Keep production collections and app behavior outside this review
build unchanged. Do not publish a production release as part of this goal.

## Completion evidence

1. Reviewed, reproducible scoring implementation and pinned corpus/model inputs.
2. A coverage report with one finite score for every shipped preset and zero
   unscored entries, including diagnosed failures and their resolved behavior.
3. Generated indexes whose paths, overlaps, scores and corpus identities verify.
4. Debug APK successfully built with exactly All/Chill/Normal/Party available,
   selected-score display and the complete generated collection.
5. Feature branch commits pushed and the debug artifact available to the user.

Tests, numeric renderer agreement and a successful APK build do not by themselves
establish human audience-fit accuracy; the delivered build enables that review.
