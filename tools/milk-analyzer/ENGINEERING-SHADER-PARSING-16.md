# Engineering handoff: remaining shader parsing failures (16 presets)

Date: 2026-10-04. Owner task: source predictor blocker reduction, draft PR #25.

This handoff concerns **ProjectM-TV:core**, our patched native engine, not an
unpatched upstream binary. Use a separate worktree based on current `main`.
Implement engine fixes as `tools/projectm-patches/*.patch`; do not commit edited
`third_party/projectm` submodule files. Keep authored presets unchanged.

The checkpoint contains 22 distinct blocked presets from the original 315-case
subset: 16 parsing, three initialization and three random-binding cases. These
counts are source interpretation gaps, not failed visual predictions. Previously
merged PRs #26/#27 must not be reimplemented. PR #28 merged into the separate
Native4K feature branch, not into this core 2.2.8 reference.

Published reference: core **2.2.8**, main commit
`f435dd7c58ea1f16d9d182ecfc5632b77f5b6f98`.
AAR SHA-256: `97d832fb5a10beb3828e465486c6664497b0a0d1d1234d81717106f8fd35ac28`.
ARM64 native library SHA-256:
`85ae024c44664d034c16b356d9010a1fb1da7b4055ff475171d56937c97e6e95`.
Source CPU diagnostics use an isolated 35-patch snapshot; its lab instrumentation
and explicit texture descriptors do not establish production random-seed, GPU or
appearance parity. Record the exact new AAR/library/commit/profile for retests.

All affected filenames below are relative to `core/src/main/assets/presets/`.
Verify the full-file SHA-256 before testing. Preserve original source, diagnostics
and unresolved outcomes rather than changing source to make a test pass.

## Assignment and evidence

Fix three native parser/preprocessor families. All16 originals reject in the
unchanged native CPU translator bodies. Isolated diagnostic copies isolate the
causes; they are not shipped preset repairs. Retest current AAR custom shader
selection before claiming a current runtime fix.

Authoritative fixture: `tools/milk-analyzer/fixtures/remaining-native-parser-16-2026-10-04.json`.
It records exact shader-source hashes, original/variant request hashes, diagnostics,
minimal controls and engine identity. Full local diagnostic requests/results are
in `build/milk-analyzer/remaining-parser-investigation/` in the predictor worktree.
The private engine archive hash is
`01c128d5bca6e27b834878a437088ab63294ff8a99dac2abe3211486f68c9963`.

## P1: `sample` variable consumed as an interpolation modifier (14 presets)

`vendor/hlslparser/src/HLSLParser.cpp`, `AcceptInterpolationModifier` accepts
`sample` when probing a type. An expression beginning with an existing local
called `sample` is then misinterpreted. Diagnostics include `expected identifier
near '*'` and `expected identifier near ';'`.

```hlsl
shader_body {
    float3 sample = tex2D(sampler_main, uv);
    ret = sample*sample*sample;
}
```

The original rejects. Renaming the local and references to `sampled` translates.
All14 exact diagnostic copies translate after that isolated rename, and their
GLES300 outputs pass the offline compiler.

Investigate declaration-vs-expression lookahead and parser token rollback. Preserve
legitimate interpolation modifiers; check legacy MilkDrop/D3D compiler acceptance
before broadening identifier rules. Do not globally delete the word `sample` or
rename authored files. Regression controls: legitimate modifier syntax, sample
as a local in a return/assignment/arithmetic expression, shadowing and unrelated
identifiers. Verify original sources after fixing the parser.

| Exact preset filename | Full-file SHA-256 | Section |
|---|---|---|
| EVET + Flexi - Rainbox Splash Poolz.milk | `be239e68191d98dc976e8bf3c1551162f7bf98b058f218f92e4f1800dbaaefdf` | comp_ |
| EVET - Brainsplolz.milk | `ca7f632030a524c044bcf6b3387fe97a3b28f72edaa9ef93988b036ac5ff0a31` | comp_ |
| Flexi - dimension window.milk | `ca23e254c3bea2a8e59fc07fec1ddc993a9fada9469c2c0f2557610fc5b1016d` | comp_ |
| Flexi - ianus portal.milk | `c6f7140722af728dedd6630659fd3e940634880d7c095386a28caa051d4028ef` | comp_ |
| Flexi - madness portal.milk | `e02d91b828f75316042cade88768cdbe962e59a35ca6281eac1b50a71f8a5e4e` | comp_ |
| Flexi - rorschach bomb.milk | `ea5c6343586c38d7b77cb1f92d69e91b3cb8fe6ec1c24f8a61fc896830e58801` | comp_ |
| Flexi - spirally caterpillar coop mode.milk | `83a21c74a7affda7c9ed85da05fc652b988b22eb2596a394e78e5ec86f84dd22` | comp_ |
| Flexi - spirally repetative 2.milk | `a0e1f244b13156627e3df8b50db2f47e67e7e3b4ce2571b5cb464f2a470417bd` | comp_ |
| Flexi - truly soft piece of software - topology - cohere perfectly normal people stopped functioning.milk | `249b57cb667831ef86d09fda33c3c7c35a74d3f818cfa916bd47e8d718c75233` | comp_ |
| Flexi - truly soft piece of software - topology - cohere.milk | `a6dd160c7fd71b64707bb25724bee5645a87bc75e3436766b665966a19034362` | comp_ |
| Flexi, Geiss and Rovastar - tokamak, the ultimate plasma torus.milk | `12064864d58f8337ca1ede72f20ce2ead38a1a591c75cf810cdcbed167db670b` | comp_ |
| Hexcollie - Hedgehog dreams.milk | `9b7d343de88e5a59363152b2161ae4aa98d8b4f323eb4cdd0fdb91374f3887c7` | comp_ |
| lice - veritubule.milk | `fd1e37383cb6c78a6d1eb906ca7982db7fc0d69d8b891f71be259341029c481b` | comp_ |
| suksma - fuck retro anything.milk | `d57fea66d8addb123af5327e19d7410ed923d0a64416b448fee2458510730883` | comp_ |

## P2: declaration macro loses whitespace and is wrapped as an expression (1 preset)

Inspect object macro expansion in `vendor/hlslparser/src/HLSLParser.cpp` and the
boundary with `MilkdropShader::PreprocessPresetShader` / `TranspileHLSLShader`.
The exact shader has both a declaration macro and a statement-valued macro.

```hlsl
#define smp sampler sampler_manyfish;
smp
shader_body {ret=tex2D(sampler_manyfish,uv).xyz;}
```

The native preprocessor emits `(samplersampler_manyfish;)` after the last header
declaration, then rejects near `'('`. Equivalent direct declaration translates.
Expanding the authored macros with token spacing preserved in a diagnostic copy
makes the full witness translate.

Preserve token separation and distinguish declaration/statement macro expansion
from scalar expression wrapping. Tests must cover nested macros, function-like
macros, semicolons, comments and sampler declarations. The full preset's
`#define texx tex2D(sampler_manyfish,uv);` must also remain valid when used after
`float3 add=`. Do not merely special-case the exact identifier `smp`.

| Exact preset filename | Full-file SHA-256 | Section |
|---|---|---|
| Fed + Geiss - Color Pox Remix.milk | `acae4b876741a1fa0962a8894633bca09c6e22c27b367945de3825f5dfebf2d1` | warp_ |

## P3: postfix swizzle after parenthesized expression rejects (1 preset)

Inspect `HLSLParser` primary/postfix/member expression parsing.

```hlsl
shader_body {ret=(float3(1,2,3)*2).xyy;}
```

This rejects near `'.'`; direct `float3(1,2,3).xyy` translates. The full witness
rejects near a member access in its nested noise-coordinate expression. It first
needs explicit built-in blur descriptors in the CPU adapter; otherwise an earlier
missing-descriptor error conceals this actual syntax problem. Materializing the
constructor and parenthesized coordinate expression into locals before the same
swizzles makes the diagnostic copy translate, retaining coordinate operations.

Support postfix member chains after parentheses without weakening vector/type
validation. Test repeated/reordered components, chained parentheses, numeric
scalar members where allowed, constructor/function-return swizzles and invalid
members. Retain q/time/texture-size coordinate order and vector conversions.

| Exact preset filename | Full-file SHA-256 | Section |
|---|---|---|
| suksma - crisco orgy - rosvell roams nz+.milk | `f99c8383eb1010a257c9188776b734edf6438c307a72f777f442b5479aad61b6` | warp_ |

## Required delivery

Report the root cause, changed patch/analyzer code, exact affected filenames and
hashes, before/after outcomes, controls, target commit and AAR/native hashes.
Keep raw source parsing, generated-shader compilation, preset loading, actual
custom-versus-fallback shader selection and numerical behavior as separate
results. Compile/load success alone does not establish correct appearance.

Run the focused controls plus unaffected controls, then the analyzer suite with
prepared pinned adapters:

```sh
build/preset-lab-venv/bin/python -m pytest tools/milk-analyzer -q
```

The producer checkpoint passed 735 tests and 35 subtests. These tools require
prepared native adapters; ordinary CI alone does not establish this experimental
suite. Recheck the original315 subset against the new implementation and retain
source-token/parsed inventories and any newly introduced gaps. Do not start a
duplicate full-corpus render. The other agent's saved baseline is read-only at:
`/Users/jneerdael/Scripts/Projectm-TV/.worktrees/quad-lines-follow-ups/build/follow-ups/core-corpus/measurements-core-emu-baseline-v1/`.
Its instrumented protocol is distinct from published-AAR controls. Do not alter
its devices, running processes, rows or settings.
