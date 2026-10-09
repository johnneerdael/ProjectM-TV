# I01 — retain tolerant preset-key loading

**Disposition: retain case-insensitive loading.** The production parser controls and40 repeated Native runs qualify this bounded policy decision. No engine patch is added. Native4K fidelity and the existing first-occurrence rule are preserved.

Original MilkDrop2 requests exact-case keys. Current projectM normalizes ASCII keys and lookup/code prefixes, accepts authored mixed-case keys, and keeps the first occurrence after normalization. Value, equation and shader text retain their casing. Switching to exact-case loading would discard values that currently load successfully; this packet documents the difference and retains the existing contract.

## Executed parser proof

`key_policy_test.cpp` was compiled directly with the current production `PresetFileParser.cpp`, without a mock. [Results](production-parser-controls.txt) cover canonical/mixed-case keys, numeric/default/string/bool lookups, both duplicate orders, invalid first occurrence, code prefixes, and unchanged value/shader text. Both unchanged stock candidates pass their loaded-value and duplicate-code assertions.

The prepared assertion initially expected the second duplicate expression. The corrected test retains the actual first `per_pixel_1` q5 assignment at line79 and excludes records80–81. Parser behavior did not change.

## Native evidence

[Results and decoded capture hashes](native-results.json) and [artifact/source identity](native-identity.json) identify source ac3dd034 and its current27 patches, ARM64, API34, Apple M4 Pro/GLES3 backend, the instrumented AAR and private capture APK. The overlay retains native bytes and all stock assets, appends exactly eight diagnostic/oracle entries, and verifies the installed APK SHA before every row. These are source-instrumented evidence artifacts; they are not shipping APK/AAR bytes.

Twenty runs use Native3840×2160 output with Standard1280×720 reference canvas. Twenty more use matched256×144 output/reference. Each runs480 frames at30FPS, seed12345, mesh48×32 and the same mono PCM. All480 GL/preset checks pass; core/EGL cleanup succeeds. Every run verifies read framebuffer0 for all eight selected captures. All20 repeat groups match decoded RGB exactly.

The finite version100 fixtures use decay0, no authored shader, no other geometry and an opaque red outer border with `ob_size=.05*zoom`. LoadedZOOM2 matches canonicalzoom2 and upper-first duplicates. Explicitzoom1 matches missing default and lower-first duplicates. The two groups differ at both resolutions. This is a finite visible loaded-state witness, not original Windows rasterization.

| Native4K fixture | Current tolerant loading | Explicit original-source default |
|---|---|---|
| `ZOOM=2` | [zoom2 / border.1](captures/i01policy-audit-i01-actual-tolerant-current-0/frame-239.png) | [zoom1 / border.05](captures/i01policy-audit-i01-strict-source-oracle-current-0/frame-239.png) |

## Unchanged stock originals

`originals/` contains byte-identical Computronium (SHA25671450433120e7c01fc82f269226341b462ba1834d83c09c1287d7935eb1d6bf5) and Toxic Lithography (SHA2567d1ba79abe1bdf49be179d481913f39865959c1f159fb4e9946e764c27ebccb3). Their mixed keys load composite version3, warp speed.5 and scale2.331. Original exact-case requests retain defaults2/1/1. [Substitution manifest](stock-oracle-pairs.json) records the full-preset siblings changing only those three explicit values, while preserving shaders and duplicate records.

Both original/surrogate pairs have identical selected RGB frames at both resolutions and on both repeats. The version values are both positive, and warp0 weakens the speed/scale witness. The observed equality does not establish whole-shader finiteness, Windows/D3D equality or an affected-preset count. It does establish that these two supplied examples have no selected-frame visible difference under the frozen input.

## Limits and followup

This retained policy adds no rendering work or engine code. No performance improvement is claimed. Original Windows/D3D playback and whole-corpus prevalence remain unmeasured. Any future strict import option needs a separate versioned API/consumer decision and its own fidelity evidence. `source-identity.json` preserves the earlier prepared snapshot with28 historical patches; `native-identity.json` is authoritative for the executed27-patch artifact.

[Audio provenance correction](../AUDIO-PROVENANCE.md): frozen manifest prose says latest512, while its actual FeedAudio queries the576-sample engine limit. Images/native bytes remain unchanged; no512-tail input equivalence is claimed.
