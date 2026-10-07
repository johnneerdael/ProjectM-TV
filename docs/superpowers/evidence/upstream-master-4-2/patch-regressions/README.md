# Named patch regression inventory

Frozen original source: `b1bb994dbfaa04159630570cd9b2c255b173a6bd` (44 patches). Frozen merged main: `43023889ec38cf1250f3bfcaaf079a840acbdf76` (49 patches, including PR44/PR47/PR48/PR49). Preset bytes are unchanged between these revisions. This is source research; no new GPU or device run was performed.

The [machine inventory](regression-presets.json) contains **351 required bundled presets plus one required external witness** and **133 optional-only historical sampled controls**. It preserves all 468 exact names recovered from historical evidence and adds 16 other explicit fixtures/main witnesses/ambiguity controls. The source set, source hashes, patch mappings, and membership are frozen before new pixel results. The [source inventory](source-inventory.json) lists the exact revisions/files searched; its SHA-256 is `ebcca9678131d3a42294a1f7cf7024ec9a09e4940806092445804e857ea51f5b`.

| Reason category | Distinct bundled names carrying that reason | Selection |
|---|---:|---|
| `required-issue-witness` | 84 | Required |
| `required-regression-fixture` | 261 | Required |
| `owner-required-control` | 17 | Required |
| `required-ambiguous-reference-control` | 2 | Required conservative coverage |
| `optional-historical-sampled-control` | 468 | Optional unless another required reason exists |

Reason counts overlap. A required reason takes precedence, and its historical sampled evidence remains in the record. `presets` is the required bundled union, and `required_external_presets` supplies the separately stored external witness; both are consumed by the comparison selector; `optional_historical_sampled_controls` is a disjoint optional-only set. No member is removed because it previously failed or because new results are inconvenient.

The required set includes the 102-name newly compiling GLES translator fixture, 16 parser fixtures, four initialization/selector controls, 95 authored float-literal fixtures, three random-binding controls, the 33-name targeted sampler/reference-size set, the existing 17-preset focused Native trails matrix, explicit framebuffer/geometry/brightness investigation witnesses, nine blur controls, and the merged-main shape/zoom/live-controls witnesses. These sets overlap. The translator TSV compares patches 0030–0032 together; it does not identify one causal patch for every individual filename. Literal fixtures establish an authored-AST regression condition, not literal reachability or a confirmed visible effect.

The recorded wide selection contains 66 explicit historical render-or-preset failures. They remain required issue witnesses with unresolved patch attribution. The separate transport-only failure had a successful repeat and stays optional: transport failure is not an engine defect. Wider successful sampled controls remain optional unless a named patch fixture or issue report independently promotes them.

Each original patch has a row in [the patch table](PATCHES.md), including zero-name rows and the separately named external 0021 witness. The JSON retains direct code-path activation and the existing original-44 migration mapping. Patches 0045–0049 are merged source fixes adapted into candidate patches 0004–0008; their current source byte hashes are recorded. Final candidate checkpoint, review, and fidelity acceptance remain with the root task. Engine-wide/lifecycle/resource fixes cannot be scoped safely by absence of a source token or a named fixture. Their activation conditions still need focused transition, resize, concurrent prewarm, cache, and resource checks alongside the preset gate.

The 9,606-name corpus catalog, operational deduplication receipts, and the explicitly non-defect 382 activity-predictor candidates do not establish patch issue membership. They are documented exclusions from the witness extraction, not exclusions from the independent unbiased random selection or claims that those presets are unaffected.

## External witness and ambiguous reference coverage

Patch 0021 names `martin + Se7enSlasher - pixies party (random texture edit).milk`. The [upstream report](https://github.com/projectM-visualizer/projectm/pull/1025) describes its identity-macro freeze. Targeted public-source research recovered the [exactly named original .milk file](https://github.com/IkeC/Milkwave/blob/e1c4210275153ffa7203430b0a8583600e383e79/Visualizer/resources/presets/Incubo_/martin%20%2B%20Se7enSlasher%20-%20pixies%20party%20(random%20texture%20edit).milk) from primary Milkwave source, not a converted JSON or similarly named sibling. Its original `comp_2` at line 1307 contains the precisely reported self-referential `sampler_rand00` macro. The public file is 47,750 bytes, Git blob `372b4b988b1fa25ed8fb832a070cbe91a0ba4a35`, SHA-256 `990472f4a5af7fbff629fd2340b14753a7fd1ec7ffc77203267dfdfbf4c8e37e`.

The unchanged bytes and source license notice are stored in `external-witnesses/`; the JSON `required_external_presets` array records its path and provenance. Keep it separate from shipping assets and add it to the laboratory comparison input on both roles. The upstream tester supplied no historical asset hash, so exact identity to that tester’s private copy remains unproven; the recovered public source matches both the exact reported filename and reported trigger. No full-preset runtime or pixel result is claimed here.

The older translator report and [original PR26](https://github.com/johnneerdael/ProjectM-TV/pull/26) both truncate `ORB - Stahl - Tantalum Gran random tex …`. Historical identity cannot be resolved from those archived records. The full catalog contains exactly two matching bundled filenames; **both are now required** as `required-ambiguous-reference-control`, with exact names/hashes in `unresolved_name_aliases.candidate_assets`. This conservative coverage does not claim either file has been identified as the original failure. The [reference coverage report](REFERENCE-COVERAGE.md) records the two hashes and source-search proof.

The hash-pinned `float-literal-control.milk` remains a separate committed synthetic preset. Original patch test groups support language, lifecycle, state, failure, and numeric contracts; they are not invented bundled preset names.

## Comparison boundary and gate

The baseline product is the latest released **ProjectM TV core AAR after PR49**, with published bytes and source revision independently verified by the root task. It is not stock libprojectM. The older source-research boundary remains release v2.3.11, source `b1bb994d`, canonical AAR SHA-256 `3bc37560a87000ec7ac446895fee8ad09e93b5c83a601014b5fc396bd1f3e6d6`; preserve that historical identity rather than relabeling it as the newer release. Publication and exact latest-AAR verification are not claimed by this research artifact.

Freeze the unbiased seed-12345 random 100 independently, then union it with the required bundled array and `required_external_presets`. Use equal fixed seeds, equal deterministic constructor/load/frame clocks, identical PCM, assets, settings, dimensions, mesh, and capture protocol on baseline/candidate. Confirm same-role repeat equality first, then require exact RGB equality at **every frame** in the agreed window for every required preset. Retain load/translation/fallback/GL failures as failed gate records; do not skip or replace them. Supplement the instrumented source comparison with unchanged released-AAR runtime checks, preserving distinct instrumentation/source/binary identities.

Zero differences for the frozen denominator supports that denominator under the measured protocol. It does not certify untested presets, other seeds/drivers/resolutions, performance gains, or all activation paths. No exact-fidelity acceptance or new visual failure is asserted here.

## Validation and reproduction

- All 484 distinct bundled names exist in the task assets and match the catalog SHA-256; required and optional-only arrays are disjoint and complete for the recovered named records.
- All used source hashes verify against the frozen extracted bytes. Every ordered original-44 patch hash and merged-main 0045–0049 source is recorded; 49 rows are present.
- `git diff b1bb994d 43023889 -- core/src/main/assets/presets` is empty, establishing unchanged authored preset assets across these sources.
- The exporter was rerun and an independent JSON/source/asset membership check was performed. Research helpers and archive-search receipts remain in ignored `build/upstream-rebase/patch-regressions-research/`; no native compilation, GPU run, or device operation was used.

For a fresh audit, read root-repository `source-inventory.json` entries with `git show <commit>:<path>`, verify their SHA-256, and inspect each reason’s line or JSON pointer. Entries with an explicit external `repository` must be fetched from that repository at the pinned commit/blob and verified independently. Join `catalog_id` to `../patch-impact/impact.json.gz` → `preset_catalog` for the complete canonical catalog. Verify current preset bytes before freezing a render denominator. A source or asset change requires a new inventory identity and documented membership review before viewing new results.
