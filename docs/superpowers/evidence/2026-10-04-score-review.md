# Recent audience-scoring review

Reviewed committed changes `44e6fbb..5e506ed`, excluding unrelated local drafts
and player files. This review does not establish completed 9,606-file scoring
or perceptual accuracy. Ten review perspectives covered correctness, testing,
maintainability, project standards, agent access, prior learnings, Python quality,
CLI behavior, performance and adversarial input cases.

## Findings resolved

- The new export arithmetic gate lacked a test of the actual CLI boundary.
  Subprocess tests now cover complete valid export and stale/missing record
  rejection before any review assets are written.
- Malformed JSON, non-object result records and malformed nested descriptors
  could terminate the whole audit. Per-record validation now reports these
  records as invalid and continues auditing the rest of the inventory.
- A missing paired-luma-area product returned an absent flash contribution.
  Combining only the model score could silently verify a different category.
  Complete finite flash evidence is now required. The regression uses positive
  flash counts and a product that yields an 80-point flash contribution.
- Asset verification imported score calibration and therefore SciPy even when
  no score was recomputed. The scoring import is now limited to export; a fresh
  subprocess verifies assets with SciPy deliberately unavailable.
- Expected incomplete exports emitted a traceback. They now emit bounded JSON,
  exit nonzero and provide the argument list for writing a full audit report.

Three focused reviewers rechecked the fixes and returned no remaining findings
in the four changed implementation/test files. The focused suite passed all
30 tests; the complete analyzer suite passed 538 tests and 33 subtests. The
stopped corpus was re-audited: 144 scores arithmetically verified,
zero invalid, three originally unresolved and 9,459 missing. Separately identified
sparse-field diagnostic scores have not been spliced into that old identity.

## Remaining completion dependency

The shared baseline on `followup/quad-lines` is accumulating records, but the
inspected corpus outputs retain eight isolated adjacent frame pairs. The current
model requires continuous transitions for acceleration and full-window flashing
rate. Its owner must provide those measurements under an explicit protocol, or
a separate scoring pass must be authorized after the user stopped the duplicate.
The exact handoff is `2026-10-04-shared-corpus-scoring-handoff.md` in this directory.

No corpus restart, production release or complete debug APK is claimed here.
