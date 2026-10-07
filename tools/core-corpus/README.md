# Shared focused-validation components

The historical v2.2.1 bulk core-AAR producer, 134,484-job corpus scanner and
hard-coded device smoke command are retired. Their historical source remains
available at [the pre-retirement revision](https://github.com/johnneerdael/ProjectM-TV/tree/6feb100b2ee1524f3da72216e582c7133cd726a2/tools/core-corpus).

## Retained consumers

Focused [Native trails validation](../native-trails/README.md) still uses:

- `build_core_aars.py`: requested engine/evaluator gitlink checkout and explicit frame-time helpers.
- `run_corpus.py`: unchanged deterministic PCM, safe preset prefixes, device-session ownership/locking and verified RGB PNG decoding.
- `android-worker/` and `native-lab/`: the shared public-JNI worker and opt-in private clock/seed bridge.
- Relevant helper, engine-pin and bridge-seed unit controls.

The old full-scan scheduler, worker provenance gates, SQLite scan store, sampled
comparison/summary CLI, bulk AAR production paths and historical-source
transformation tests have been removed. The helper modules reject direct CLI
execution rather than silently accepting obsolete commands.

## Validation

Run from a development checkout with the tooling dependencies installed:

```sh
python -m pytest tools/native-trails tools/core-corpus -q
```

The release gate runs Native trails/Preset Lab and current-engine checks; it does
not restore the retired historical corpus scan.

## Archived evidence

Existing captures, identities, fixture metadata and published score provenance
are preserved. `baseline-release.json` remains a historical record, not a current
engine baseline. Archived protocols bind exact helper hashes: reverify them using
their recorded source revision, not these reduced helper modules. Do not relabel
old captures or regenerate collection scores as part of this retirement.
