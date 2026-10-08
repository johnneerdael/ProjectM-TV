# I01 retained casing policy — owner packet

**Open: parser controls are prepared source only; Native screenshots are pending. This packet does not complete the policy review.** No canonical source/patch/test/helper/docs, git, build configuration/artifacts or devices were changed. No compilation, executable controls, GL/GPU or device work was performed. Files created here are owner evidence/proposal artifacts only.

## Proposed retained contract

Keep ASCII case-insensitive key storage and lookup, including GetCode prefixes. Keep the first occurrence after key normalization, in both mixed-case duplicate orders. Preserve value/code/shader text casing, existing numeric/default/prefix parsing and code-record sequencing. Do not silently switch to exact-case import or add a strict import mode without demonstrated need. No engine change is proposed.

Production PresetFileParser.cpp:79,111,128,150 normalizes lookups;176 normalizes keys;179–183 keeps the first normalized key. Original state.cpp:143–147 uses exact strcmp, and1397 requests lowercase zoom. Thus `ZOOM=2` without lowercase zoom loads2 currently but leaves original default1. The exact-case source difference is documented; tolerant loading is deliberately retained.

## Prepared real parser controls

`parser/PresetFileParser.{cpp,hpp}` are byte-identical snapshots of production sources. `key_policy_test.cpp` calls their actual APIs, with no mock or alternate parser. Controls cover canonical/mixed keys, missing defaults, integer/bool/string lookup, first mixed-case duplicate in both orders, invalid first occurrence, normalized code prefixes, unchanged shader/value casing and first duplicate custom-code record. They also check both original candidates' tolerant values and their existing duplicate per_pixel_1 precedence.

Future parent-owned scalar validation (not run here):

```sh
c++ -std=c++17 -I build/audit/key-policy-proposal/parser build/audit/key-policy-proposal/parser/PresetFileParser.cpp build/audit/key-policy-proposal/key_policy_test.cpp -o build/audit/key-policy-proposal/key-policy-controls
```

Run that executable with the two exact paths under `originals/` as positional arguments. A passing parser result will establish this bounded input contract; it will not establish appearance. No RED/GREEN or pass result is claimed by this source-only preparation.

## Exact stock originals and native source-oracle siblings

`originals/` contains unchanged byte copies of:

- PyroCybin - Computronium [stahlregens gelatine finish].milk — SHA25671450433120e7c01fc82f269226341b462ba1834d83c09c1287d7935eb1d6bf5
- PyroCybin - Toxic Lithography [stahlregens gelatine finish].milk — SHA2567d1ba79abe1bdf49be179d481913f39865959c1f159fb4e9946e764c27ebccb3

`candidates.json` records their exact keys and line numbers. In each, line4 is PSVERSION_comp=3, line33 fwarpAnimSpeed=.5, and line34 fwarpScale=2.331. Current loading gives composite version3, speed.5 and scale2.331. Original exact-case source requests PSVERSION_COMP/fWarpAnimSpeed/fWarpScale, so its source expectations are2/1/1 (state.cpp:1327,654–655,1408–1409). Both composite versions are positive; strict source loading does not disable the shader.

Both files declare warp0 and contain custom warp/composite code. This weakens an effect claim for the warp speed/scale values. Current FinalComposite.cpp gates authored composite loading with version>0; a version3 versus2 metadata difference alone is not evidence of a different native shader. Stock runtime/visual impact remains unconfirmed.

Both originals also contain two exact per_pixel_1 records at lines80–81. The current parser retains the first; later duplicate code must not replace it or be appended. This is separate from the casing question and stays unchanged in every surrogate.

`stock-oracles/` keeps all original bytes except three explicit loaded-value substitutions: canonical PSVERSION_COMP=2, fWarpAnimSpeed=1 and fWarpScale=1. `stock-oracle-pairs.json` records each replacement and both hashes. These are new native explicit-value surrogates for the original exact-case defaults, not Windows/D3D captures. Original authored shaders remain intact; whole-shader finite output is not certified by this preparation.

## Finite visible diagnostic siblings

`fixtures/` contains six new version100 presets with no authored shaders or extra geometry, decay0 and an opaque red outer border. Frame code sets `ob_size=.05*zoom` and publishes zoom/size into q1/q2. This makes the loaded-state consequence visible without depending on nonuniform feedback or arbitrary original shader behavior.

| Fixture | Current loaded zoom | Source border size |
|---|---:|---:|
| i01-actual-tolerant.milk (ZOOM=2) | 2 | .1 |
| i01-strict-source-oracle.milk (zoom=1) | 1 | .05 |
| i01-canonical-positive.milk (zoom=2) | 2 | .1 |
| i01-missing-default.milk | 1 | .05 |
| i01-duplicate-upper-first.milk (ZOOM=2, then zoom=1) | 2 | .1 |
| i01-duplicate-lower-first.milk (zoom=1, then ZOOM=2) | 1 | .05 |

`fixture-expectations.json` retains these source expectations. No fixture has been parsed, executed or rendered here. Border-size parameters are stated, not measured pixel widths. The strict oracle uses an explicit native zoom1 to represent the original source loader's result; it does not implement an original parser or certify original rasterization.

## Parent screenshot acceptance

Freeze parser/ordered-patch identities, fixture/original bytes, actual APK/AAR/ABI and backend, PCM transport/effective hashes, seed and context generation. Start matched256x144 authored/output, mesh48x32, Native Standard, fixed frame/time/FPS/progress, no transitions/detail/diffusion. Trace loaded zoom and q1/q2 before appearance comparison. Capture actual-tolerant versus strict-source-oracle and unchanged canonical/default/duplicate controls. Check actual-tolerant matches canonical-positive and preserves the documented first occurrence in each order.

Repeat Native Standard4K separately with actual authored/reference/output dimensions recorded. Bind and verify the final-output read framebuffer for captures. Render both exact stock originals and their clearly labelled explicit-value surrogates; equality is a valid bounded result and must not become an affected-corpus claim. Include resolved shader/fallback state and avoid declaring metadata differences visually active without evidence.

Screenshots and their decoded hashes/geometry checks are required before marking I01 policy review complete. Original Windows/D3D appearance and whole-corpus frequency/impact remain outside this packet.

## Identities and status

`source-identity.json` records parser snapshots, ordered current0001–0028 patch hashes and both byte-identical original state.cpp sources. `artifact-hashes.json` records prepared control/fixture/original/surrogate identities. Native artifact identities and captures remain parent-owned future evidence. Status stays **open / retained-policy proposal awaiting parser execution and Native images**.
