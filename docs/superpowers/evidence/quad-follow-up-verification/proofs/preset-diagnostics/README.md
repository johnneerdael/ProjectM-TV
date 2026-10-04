# Adjacent preset diagnostic review

P2, high confidence: `MilkdropPresetLoadException`, `MilkdropCompileException`, and `PresetFactoryException` own an error message but inherit `std::exception::what()`. Both public ProjectM load entry points forward `what()` to `PresetSwitchFailedEvent`.

Parse/load failures traverse two lossy boundaries: Milkdrop load exception -> factory catch/wrap -> public load catch/event. Compilation failures during preset initialization traverse the public load catch/event. Fixing only the two Milkdrop exception classes leaves parse/missing-file event reasons generic; `green/two-overrides-test.log` proves that intermediate result.

Six RED regressions fail with observed `std::exception`: inherited standard-handler tests for all three types and public failure events for invalid stream, invalid per-frame expression, and missing preset filename. With three small `what() const noexcept override` methods returning owned `m_message.c_str()`, all six pass. Full GREEN host suite passes 169 tests from 20 suites, zero skipped.

## Reproduce

From the owning worktree:

```sh
build/preset-lab-venv/bin/python build/follow-ups/preset-exception-review/review.py red
build/preset-lab-venv/bin/python build/follow-ups/preset-exception-review/review.py green
build/follow-ups/preset-exception-review/green/build/tests/libprojectM/projectM-unittest
```

RED exits 1; GREEN exits 0. `0027-preset-exception-diagnostics.patch` is the full review candidate with tests/CMake entry; `code-only.patch` contains only the exception changes. Both remain scratch-only. `manifest.json` records identities, results and artifact checksums.

## Value and risk

Recommend integration as a contained diagnostics correction. It preserves load rejection, compilation behavior, render output and exception ownership while exposing the existing stage/path explanation through standard handlers and events. These no-allocation noexcept methods return pointers valid while the exception lives, matching standard `what()` semantics. It does not make the two failing corpus presets load, or recover evaluator line/column detail.

Public driver tests use macOS CGL and skip without it; the three inherited-interface tests do not require GL. No baseline worker, production source, live API, or device was modified.
