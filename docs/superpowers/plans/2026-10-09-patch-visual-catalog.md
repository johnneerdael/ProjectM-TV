# Visible repair catalog

Goal: show the 18 retained audit repairs inline on the patch guide, comparing frozen upstream master e98fca85e57802d27a6d11499642de2a1d5e994e to ProjectM TV main 8a15996e8510533113a44e26feaddc3a7d6e85f5. Prefer Apple M4 Pro native GPU; fall back to an owned host-GPU Android TV emulator. Preserve old frozen artifacts and predictor worktrees.

## Units

- [x] Backend and rendering (root): establish hardware GPU support, source identities, matching instrumentation, seed/audio/time/dimensions. Render a targeted witness for each repair twice; label controls as synthetic. No broad performance benchmark.
- [x] Witness inventory A: I17 I08 I31 I09 I05 I06. Goal: select strongest original preset or explicitly synthetic control from existing evidence. Files: read issue README/results/preset assets and predictor tools; write build/catalog-inventory-a.md only. Approach: identify trigger and visible region, original source hashes and existing baseline limits. Verification: every recommendation cites existing file and distinguishes observed capture from proposed candidate.
- [x] Witness inventory B: I29 I10 I11 I12 I13 I18 M02. Same goal/approach/verification; write build/catalog-inventory-b.md only.
- [x] Witness inventory C: I19 I22 I20 I24 I16. Same goal/approach/verification; write build/catalog-inventory-c.md only.
- [x] Gallery (root): inline paired images and matching crops where useful, concise visible-effect captions, exact provenance and limits. Preserve older 0001-0016 entries.
- [ ] Verification and PR (root): source/image manifest checks, strict MkDocs, inspect rendered page, commit/push docs PR with substantive release notes. Publication remains distinct from PR readiness.

## Boundaries

No app/renderer behavior changes or version bump. Native desktop comparison does not establish physical-TV performance. Old per-patch baseline is not upstream master. No brightness edits or different zooms within a pair. If a repair has no visible original witness, present an explicit diagnostic rather than invent affected preset counts.

## Completed local evidence

26 cases/104 runs/41,280 frames pass with exact within-role RGB repeats and no reported GL errors on Apple M4 Pro. The guide shows23 pairs for18 IDs; artifact verifier and strict MkDocs pass. Browser desktop/narrow checks pass. Publication is tracked through the documentation PR.
