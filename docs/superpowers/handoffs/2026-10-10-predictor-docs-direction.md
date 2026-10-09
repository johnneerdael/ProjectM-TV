# Predictor direction: documentation handoff

Date: 2026-10-10. Source implementation checkpoint: `9c8ff632` on
`feat/predictor-static-output-bounds`.

## Delivery and integration

This is a documentation-only change for separate publication on `main`. It updates
`docs/user-guide/predictor.md`, `predictor-export.md` and
`predictive-collections.md`. It does not merge the experimental predictor, change
Android/AAR behavior, regenerate scores or operate corpus/devices.

The existing predictor worktree was used. No new worktree was created. The local
`origin/main` reference inspected was
`a3a045bd8a7655e48bce2368008e2ced7d724063`; fresh public-page retrieval failed, so
this is not a claim of remote synchronization. The two public pages named by the
user already exist at that local main reference. The separate `predictor-effects.md`
page does not, so this change deliberately uses experimental GitHub links instead
of depending on an absent main-relative page or a new navigation item.

Cherry-pick only the docs commit reported with this handoff onto the chosen docs
branch from current main. No analyzer commit is needed to publish these pages.
Keep useful newer main edits if a conflict arises. Push the experimental
implementation branch before publishing its new reference/evidence links; local
commits may not yet be available on GitHub while connectivity is unavailable.

Run the destination's own `python -m mkdocs build --strict` using its prepared docs
environment after integration. The source worktree check does not guarantee a
future main checkout has identical navigation/assets. No versions or release
changelog entries were changed.

## Direction documented

The current development priority is source semantic interpretation and a
machine-readable approximate baseline look: structures, geometry/materials,
coordinate mappings, colour ingredients, feedback relationships and per-element
audio controls. No AI image classification feeds the static export.

Keep three paths distinct:

1. The shipped beta mood bundle uses historical controlled native-frame measurements.
2. The preserved 47-field numerical feature export simulates source behavior under
   explicit audio/time/assets/render settings. Omitting retained frames does not
   remove simulation.
3. The newer `effect_family_export.py` record adds
   `analysis.visual_description` without executing equations, shaders, audio or
   display frames. This is the active direction, not a renamed 47-field exporter.

The numerical catalog, examples, hashes and CLI commands retain their original
2026-10-08 checkpoint. The overview no longer presents hypothetical preferences
or older extraction as an already complete source-only mood model.

## Current evidence

- Committed source-hue evidence records 2,301 analyzer tests and 92 subtests passing.
  Tests are intermediate controls, not a visual accuracy percentage or proof of
  complete preset interpretation.
- Fixed-100 ingredient counts are overlapping coverage: 61 presets with
  nonidentity affine maps; 23 with 64 direct sampled-colour coordinate-response
  maps; 35 with 36 supported RGB mixture stages; 15 consuming native-time formulas;
  14 consuming native-hue recipes; two each for four mixed polar maps and four
  distinct periodic radial generators. Do not sum these into an accuracy score.
- The locally verified target profile is the full published 2.3.33 AAR, hash
  `13290b486d08569f229f1f684e57aba849a31a2506270a4d305777322d8d7377`.
  It carries byte-equivalent qualification through 2.3.32/source31. Native library,
  Java/assets, source CPU/model and runtime control identities remain distinct.
  The three small JNI controls are not whole-authored-preset appearance evidence.

Authoritative committed references:

- `tools/milk-analyzer/EFFECT_FAMILIES.md`
- `tools/milk-analyzer/SOURCE_APPEARANCE.md`
- `tools/milk-analyzer/export-contract/source-appearance.schema.json`
- `tools/milk-analyzer/profiles/published-core-v2.3.33.json`
- `docs/superpowers/evidence/source-sampling-geometry-2026-10-09/README.md`
- `docs/superpowers/evidence/source-blur-bindings-2026-10-09/README.md`
- `docs/superpowers/evidence/source-colour-mix-2026-10-09/README.md`
- `docs/superpowers/evidence/source-native-time-2026-10-09/README.md`
- `docs/superpowers/evidence/source-composite-hue-2026-10-10/README.md`
- `docs/superpowers/evidence/source-polar-mixed-2026-10-09/README.md`
- `docs/superpowers/evidence/source-radial-grid-2026-10-09/README.md`

These technical files are on the experimental implementation branch, not required
as local files for the docs-only main integration.

## Open work, not proven ceilings

Recognizable whole-preset reconstruction, final prominence/coverage/palette,
perceived motion, flashing, complete feedback and calibrated preference matching
remain pending implementation or validation. Current null/unknown values express
that state; they do not show these questions are permanently impossible.

The current 64-direct-sample/4,096-node substitution budget, 256-node control
export budget and supported constant-affine operators are extendable
implementation constraints. Source-only execution-free extraction is the chosen
method, not a defect or an accuracy ceiling. Missing selected images, random
phases, initial history, audio and clock values are additional inputs for an exact
instance; a useful approximate baseline need not know every such input.

Historical 95/97.5/100 scores belong to frozen native-render comparison protocols.
They are not current static JSON accuracy. Preserve the distinction between mean
agreement, pass rate, completed-case denominator and unresolved original cases.
The source-only recognizable-look notification gate is not established yet.

## Validation

Verified for this delivery:

- `build/docs-venv/bin/python -m mkdocs build --strict`: passed, exit 0.
- `git diff --check`: passed, no output.
- Archived local `origin/main` guide and `mkdocs.yml` to a temporary directory,
  overlaid only the three changed user-guide pages, then built with the same
  prepared docs interpreter and `--strict`: passed, exit 0. This was not a new
  worktree and did not mutate main.

The pre-existing Material startup warning did not fail either strict build. No
analyzer code/tests were run for this documentation-only task, and no new
appearance test is claimed. Existing analyzer test numbers above are attributed
to their committed checkpoint rather than presented as freshly rerun.
