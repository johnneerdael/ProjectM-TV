# Sixteen preset shader parser regressions

Base: main `f435dd7c58ea1f16d9d182ecfc5632b77f5b6f98`, projectM v4.1.7
`e0b0a967f0ffd7d332106c366668ed271718472b`, patches 0001–0035.
Fix: patch 0036. Authored preset bytes are unchanged. The native regression
manifest records each original filename, section and full-file SHA-256 and
CMake rejects changed witnesses before building.

## Causes and changes

- Failed type lookahead consumed interpolation modifier identifiers, including
  a local named `sample`. Restore tokenizer state when no type matches; retain
  real interpolation modifiers. `(sample)` also exposed a null-node crash.
  Escape `sample` with the generator's existing unique-name mapping because
  GLSL ES reserves it. Authored source identifiers stay unchanged.
- Macro definition and propagation stripped token whitespace, then expansions
  added parentheses around declarations and semicolon-terminated statements.
  Preserve token spacing and authored parentheses and use token substitution
  for object and function macros. This also restores authored precedence for
  unparenthesized arithmetic macros. Identity macros retain their guard.
  [Microsoft's HLSL macro reference](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-appendix-pre-define-2)
  describes replacement by tokens with argument substitution.
- The parenthesized-constructor fast path returned before postfix parsing.
  Parse its complete enclosed expression first, then use existing member/index
  handling. Casts and member validation retain their existing paths.

## Results and limits

| Check | Before | After |
|---|---|---|
| Focused parser controls | sample, declaration/statement macros and constructor postfix cases reject; `(sample)` crashes under ASan/UBSan | 24 controls pass, including modifier/cast/identity controls and invalid members |
| Generated control fragments, GLSL ES 3.00 | not all generated | 22/22 compile with `glslangValidator -l` |
| Sixteen original affected shader sections, CPU adapter | 16/16 reject | 16/16 translate and compile offline as GLSL ES 3.00 |
| Sixteen originals, production `MilkdropShader` on desktop GL | before result not yet recorded here | 16/16 directly compile/link, without fallback exception handling |
| Numerical controls through real engine | baseline recorded in test failures | 12 red-channel controls match independent expected values within 2/255 |
| Complete projectM host suite | existing baseline | 222/222 pass on macOS CGL |
| Android core and JVM tests | existing baseline | `:core:assembleDebug testDebugUnitTest` succeeds |

The CPU adapter is local diagnostic scaffolding copied from the predictor
worktree and rebuilt against this worktree's parser/generator. Its binary hashes
and per-request hashes are in `results.json`; raw requests, outputs and compiler
logs remain in this worktree's ignored `build/parser-witnesses/`. Explicit blur
sampler declarations are used for the two warp witnesses. Neither adapter
success nor desktop GL compilation certifies Android driver selection,
MilkDrop parity, full-preset numerical behavior, performance, or appearance.

Permanent checks: `bash core/src/test/native/run_native_tests.sh` exercises
parser/generator controls, numerical render controls and direct production
shader compilation for the 16 hashed originals on macOS OpenGL or Linux GLES.
`bash tools/check-patch-series.sh` verifies the patch series from a fresh export.
The experimental `tools/milk-analyzer` is not part of main and is not added by
this fix; its complete test suite and original315 predictor classification need
a separately prepared snapshot if retested.

## Original witnesses

| Preset | SHA-256 | Affected section |
|---|---|---|
| EVET + Flexi - Rainbox Splash Poolz.milk | `be239e68191d98dc976e8bf3c1551162f7bf98b058f218f92e4f1800dbaaefdf` | composite |
| EVET - Brainsplolz.milk | `ca7f632030a524c044bcf6b3387fe97a3b28f72edaa9ef93988b036ac5ff0a31` | composite |
| Fed + Geiss - Color Pox Remix.milk | `acae4b876741a1fa0962a8894633bca09c6e22c27b367945de3825f5dfebf2d1` | warp |
| Flexi - dimension window.milk | `ca23e254c3bea2a8e59fc07fec1ddc993a9fada9469c2c0f2557610fc5b1016d` | composite |
| Flexi - ianus portal.milk | `c6f7140722af728dedd6630659fd3e940634880d7c095386a28caa051d4028ef` | composite |
| Flexi - madness portal.milk | `e02d91b828f75316042cade88768cdbe962e59a35ca6281eac1b50a71f8a5e4e` | composite |
| Flexi - rorschach bomb.milk | `ea5c6343586c38d7b77cb1f92d69e91b3cb8fe6ec1c24f8a61fc896830e58801` | composite |
| Flexi - spirally caterpillar coop mode.milk | `83a21c74a7affda7c9ed85da05fc652b988b22eb2596a394e78e5ec86f84dd22` | composite |
| Flexi - spirally repetative 2.milk | `a0e1f244b13156627e3df8b50db2f47e67e7e3b4ce2571b5cb464f2a470417bd` | composite |
| Flexi - truly soft piece of software - topology - cohere perfectly normal people stopped functioning.milk | `249b57cb667831ef86d09fda33c3c7c35a74d3f818cfa916bd47e8d718c75233` | composite |
| Flexi - truly soft piece of software - topology - cohere.milk | `a6dd160c7fd71b64707bb25724bee5645a87bc75e3436766b665966a19034362` | composite |
| Flexi, Geiss and Rovastar - tokamak, the ultimate plasma torus.milk | `12064864d58f8337ca1ede72f20ce2ead38a1a591c75cf810cdcbed167db670b` | composite |
| Hexcollie - Hedgehog dreams.milk | `9b7d343de88e5a59363152b2161ae4aa98d8b4f323eb4cdd0fdb91374f3887c7` | composite |
| lice - veritubule.milk | `fd1e37383cb6c78a6d1eb906ca7982db7fc0d69d8b891f71be259341029c481b` | composite |
| suksma - crisco orgy - rosvell roams nz+.milk | `f99c8383eb1010a257c9188776b734edf6438c307a72f777f442b5479aad61b6` | warp |
| suksma - fuck retro anything.milk | `d57fea66d8addb123af5327e19d7410ed923d0a64416b448fee2458510730883` | composite |
