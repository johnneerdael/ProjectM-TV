# Random texture binding investigation — 2026-10-04

Base: published core 2.2.8 source `f435dd7c58ea1f16d9d182ecfc5632b77f5b6f98`; upstream projectM `e0b0a967` plus patches 0001–0035. Candidate engine change: patch 0037, final engine source commit `9c20236c3f38a1bed5205e435b6e7639a1158685`. Local release AAR/native hashes are in `local-artifact-identity.json`; that build uses the default local version 2.2.0 and is not the published 2.2.8 AAR. No authored presets or analyzer source were changed.

## Findings and fix

The three reported presets use unqualified `rand00`/`rand01`. Their source-bound compiled shader bindings select real bundled textures and match their GL uniforms both before and after this patch. The report's remaining analyzer gap is not evidence that these three still have the historical sampler-state parser failure.

Related native defects were reproduced independently:

| Trigger | Before | With 0037 |
|---|---|---|
| `pc_rand00_red` | mode qualifier hides the filename filter; selected texture uses default sampler | red-prefixed image, point/clamp sampler, exact alias and unqualified texsize |
| warp `rand00_red`, composite `fw_rand00` | cached old descriptor leaves the new alias undeclared | shared image, current alias and requested sampler |
| `rand00_red` plus `rand00` | emitted short sampler stays at unit zero | both uniforms bind the selected image |
| `pc_rand00_red` plus `pc_rand00` | unrestricted selection happens first; duplicate texsize declarations | filtered selection, qualified short alias, unique uniform declarations |
| case-sensitive short alias with unused long declaration | shorthand removal loses the active alias spelling | preserve exact original spelling before eliminating a shorthand |
| two long aliases for one slot | overlapping generated declarations can fail compilation | declarations deduplicated individually; shared image |

Selection belongs to a preset slot 00–15, not a descriptor name. Each use receives an alias and sampler appropriate to its shader. Within a shader, filename-filtered aliases fill new slots before unrestricted forms; competing prefixes retain lexical precedence. Across stages or shader reloads, an already selected slot wins, even if the later alias supplies another filter. A new preset has new slots. `sampler_state` fields remain ignored under patch 0032; the name prefix controls sampling. Unqualified user textures use linear/wrap. Patch 0026 still reserves warp unit zero for unqualified main.

Loaded textures now retain their lowercase base name and exact `SourcePath()`. Generated textures have an empty source path. This internal C++ diagnostic information does not change Java/JNI signatures. Selection still uses a fresh `std::random_device` seed for each new image. The isolated controls use two distinguishable known-value TGA textures and unique filename filters to force repeatable associations without introducing a production seed override.

## Exact source-bound observations

`preset-bindings.json` records each source/preset hash, selected asset path/hash, dimensions/target, filter/wrap, unit and uniform. Its scope is a compiled source-bound shader pair on Apple M4 Pro OpenGL 4.1, not an observation from the published Android AAR. The separate full-preset loader chooses its own production-random images. Keep these observations distinct.

| Preset | Full-file SHA-256 | Native source parsing / custom compilation / full load | Full render diagnostic |
|---|---|---|---|
| EoS - glowsticks v2 04 music minimal - swim  - dictatutorial rt roam3 2.milk | `5dd383cf79e1aacbed944ded85d70a365dde2c51f2ca7646ed0b7fde0cf4c79f` | accepted before/after | no GL error before/after |
| EoS - glowsticks v2 04 music minimal - swim  - dictatutorial rt roam3.milk | `06b84ff69c3aeeb88eff3dea63dd3c1f5b146b4c2afb9df204f5f2561e7aee15` | accepted before/after | no GL error before/after |
| midgitstraights of majillaen - featy sweet.milk | `d4cd997dedc57ab34c7247fee1ba94d4061528d12d16cde5a468145fb216ebba` | accepted before/after | `GL_INVALID_FRAMEBUFFER_OPERATION` (1286) before/after |

Retained debug compiler messages show the full loader successfully compiling custom warp/composite shaders; no fallback message appears in the final diagnostic. The renderer unbinds its program after drawing, so post-draw current-program inspection cannot certify stage selection. Numerical behavior and appearance of the full authored presets remain unverified. The midgit framebuffer result is an unresolved baseline diagnostic, not a claimed fix or a regression introduced by 0037. Bundled-image diagnostics also surface pre-existing vendored SOIL2 JPEG left-shift UBSan warnings; these are outside the binding fix. Both outcomes remain in ignored local diagnostic logs in this evidence directory (not committed).

The core extracts all top-level `assets/textures/` files to private `files/textures/` before marking its worker ready, skips already copied files whose sizes match, and supplies that path to live/prewarm engines before the first preset. This source review and host asset scan establish the implemented path; actual Android extraction/binding has not been freshly measured for this change.

## Validation and limits

- Seven ASan/UBSan real-GL CTest controls pass: manager, cross-stage aliases, shorthand, numerical samples, lifecycle, existing macro and waveform regressions. `numerical-controls.json` preserves expected/actual RGB bytes; these prove the controlled alias associations, not full-preset appearance.
- Full native host runner passes; macOS transition-overlay GLES test is skipped without EGL/GLES. All 222 upstream engine tests pass, including main/named-main sampler controls. CI's Linux native job, including the GLES transition test, passes for `a30de789`.
- Fresh debug core/app build and JVM tests pass. Release APK/core AAR build and release JVM tests pass. All 36 patches apply to a clean recursive export. Preset index/content checks and MkDocs strict build pass.
- The separate PR25 analyzer checkpoint passes 750 tests and 35 subtests using its prepared historical adapters, with bytecode/cache writes disabled. A pinned copy rechecks the original 315 inputs: source/code/parsed/unvisited inventories unchanged, no newly blocked presets. It reports 22 gaps versus the saved 23 because independent analyzer work cleared `martin - ludicrous speed.milk`; this patch receives no credit. The three random-binding guards remain. See `subset-audit.json` for adapter/module provenance. No new 36-patch analyzer adapter or full-corpus rendering was run.
- Dedicated TV before/after captures and frame-rate validation are pending device allocation. The shared corpus baseline and running devices/processes/settings were not changed.

Rerun the native suite with `core/src/test/native/run_native_tests.sh`. For optional exact-preset diagnostics, configure `core/src/test/native/projectm-regressions` against the applied engine, enable `-DCMAKE_CXX_FLAGS=-DMILKDROP_PRESET_DEBUG`, build `random-texture-regressions`, then run `random-texture-regressions presets <new-fixture-directory>`. Its companion JSON is preserved even when a full-render diagnostic fails. Do not clear analyzer guards until a matching runtime/AAR-bound descriptor manifest and lifecycle profile are consumed by the analyzer.
