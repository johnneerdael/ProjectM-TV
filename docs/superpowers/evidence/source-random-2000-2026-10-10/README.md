# Frozen 2,000-preset source-only audit

Producer model commit: `c564bda0fb53e530dee427d0e992ee292dfb9f1c`.
No model changes occurred during the audit. The original 100-preset controls remain
separate; 19 naturally overlap this random selection.

## Selection and execution

Select 2,000 of the 9,606 bundled Cream of the Crop files by sorting
`SHA256(seed + NUL + relative_path + NUL + full_source_SHA256)` ascending.
Seed: `ProjectM-TV-source-random-2000-2026-10-10-v1`. There are 2,000 distinct paths
and source hashes. No failed case is replaced or rerolled. The sealed selection
and full corpus inventory hash are in `sample-selection.json.gz`.

Four isolated CPU workers use the existing source34 native reader, patched shader
translator and offline validator, then the source-only exporter with the declared
audio/canvas scenario. The target matches the pinned full AAR bytes shared by
v2.3.34–v2.3.36. Native operations here are file parsing and offline source
translation/validation: no shader/equation simulation, captured frames, devices,
runtime random-image choices or AI classifier is used. Compiler and sampler
declaration evidence is conditional, not native-driver or upload certification.

The run took **483.54 seconds (8 minutes 4 seconds)** including batch ZIP creation.
Average per-preset worker time was 0.897 seconds, median 0.839, maximum 6.628;
these include parsing, offline compilation and static export. They are not pure
math timings or renderer performance. Results are saved once with no duplicate
analysis cache; each completed group of 100 is paired with its original `.milk`
file in a ZIP. ZIP completion order/timestamps can vary with scheduling.

## Verified outcome

- 2,000 terminal exports, all with status `computed`; no worker error/timeout.
- 1,995 structured descriptions; five explicit traversal-budget unknown fallbacks.
- All 2,000 records pass the schema, including those five valid unknown records.
- All source hashes, compile-proof seals and analysis/compatibility joins verify.
- Twenty ZIPs contain exactly 2,000 unique matching source/result pairs.

The five fallbacks remain in the pool with full hashes in `report.json.gz`:

- `Flexi + geiss - the deep diver's cognitive dissonance 1's and 0's where they don't belong.milk`
- `flexi - grind my glitch up [192].milk`
- `flexi - grind my glitch up [230].milk`
- `flexi - grind my glitch up [317].milk`
- `flexi - grind my glitch up [319].milk`

Computed, structured and schema-valid do not mean complete interpretation or
whole-preset prediction accuracy. This audit measures source coverage; no visual
or mood match rate is established.

## Conditional traits and next priorities

Counts below are distinct presets, and groups overlap. Scenario quantities assume
the declared domains, rather than measured music or runtime inputs.

| Source quantity | Default | Declared scenario |
| --- | ---: | ---: |
| Some lookup partial-time bound | 1,605 | 1,636 |
| Positive lookup time ceiling | 77 | 88 |
| Complete fixed-sample feedback colour gain | 776 | 786 |
| Stricter previous-image raw-warp gain | 121 | 166 |
| Sufficient raw-warp colour contraction | 53 | 56 |

The difference between some time bound and positive time ceilings includes zero
partial components; these do not certify stillness, no flashing or Chill suitability.
Uniform native displacement is bounded for 626 presets, and separate spatial
native displacement for 165. Those are transport ceilings, not observed speed.

The source interpretation report identifies 187 presets with loop/domain proof
obligations, 156 with component-projection type gaps, 75 with unresolved EEL
memory normalization, and 74 with EEL loop normalization. Feedback-specific missing
blur-to-previous-image transfer affects 348 presets. Counts are unions across
sections, rather than repeated sites. These are specific gaps within otherwise
partially understood programs, not wholesale unreadable-preset counts or proof
of native library defects. The five traversal fallbacks also need focused repair.

Full ranked preset lists are in `report.json.gz`. Its descriptor priorities scan
source interpretation plus native displacement, nonlinear colour, feedback
sensitivity and sampling geometry; they do not claim exhaustive coverage of every
material/activity subtree. Families are contributing source constructions, not
verified dominant effects. Bound/prominence/feedback and mood calibration remain
separate from schema and coverage checks.

## Reproduction and artifacts

Keep the pinned native adapters and Python environments prepared in this worktree.
The scripts are plain Python and reuse the existing exporter/store; no AI service
is required. They reject changed model/tool/scenario/runner identities and retain
failed outcomes. Run from the predictor worktree root:

```sh
build/preset-lab-venv/bin/python docs/superpowers/evidence/source-random-2000-2026-10-10/run_sample.py --output build/preset-corpus/source-random-2000-2026-10-10/results-run --workers 4
build/docs-venv/bin/python docs/superpowers/evidence/source-random-2000-2026-10-10/summarize.py build/preset-corpus/source-random-2000-2026-10-10/results-run build/preset-corpus/source-random-2000-2026-10-10/report-reproduced.json build/preset-corpus/source-random-2000-2026-10-10/run.log
```

Resuming the completed run validates artifacts and schedules no duplicate exports.
A changed producer needs a new output directory. The runner hashes its own bytes;
the committed copy matches the executed lab copy. A four-case actual source smoke
checks structured/schema output, compile proof and archive hashes before the
larger run. Independent review rechecks the selection and all final 2,000 proof and
archive joins, finding no integrity issue.

The immutable local result folder is:
`build/preset-corpus/source-random-2000-2026-10-10/results-run/`.
It contains `batch-000001.zip` through `batch-000020.zip`, `results/`,
`compatibility/`, `run-manifest.json` and `sample-selection.json`.
The run log is `build/preset-corpus/source-random-2000-2026-10-10/run.log`.
Compressed report and selection files in this evidence directory preserve source
IDs and priorities without committing the multi-gigabyte loose export.
