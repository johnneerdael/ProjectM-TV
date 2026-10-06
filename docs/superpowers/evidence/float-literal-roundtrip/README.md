# Float32 shader literal round-trip root cause and related audit

Base: `f745670d35d3a362bea1a6a56928b55b70cc9887`, the source of published
Native core 2.3.8. Upstream projectM 4.1.7 `e0b0a967` plus 43 patches.
Fix: patch 0044. Authored bundled presets are unchanged.

## Root cause and correction

The tokenizer parses decimal text into a double and narrows it into the float32 AST.
For the reported `1.00000011920928955078125`, that AST value is correct:
`0x3f800001`. `GLSLGenerator::OutputExpression` delegates float emission to
`String_FormatFloat`, which previously used classic-locale `ostringstream` with
default six significant digits. It emitted `float(1)`, reparsed as `0x3f800000`.
The separate scale `4194304.0` also became `float(4.1943e+06)`, or `4194300`.
This loss happens in generated source before any GPU arithmetic or filtering.

Patch 0044 selects `numeric_limits<float>::max_digits10` (9 on the supported
float32 implementations), keeps the classic locale and appends `.0` when a finite
value has neither a decimal point nor exponent. This preserves floating spelling,
including negative zero, without changing integer/Boolean AST emission. See the
[C++ numeric-limits definition](https://eel.is/c++draft/numeric.limits) and
[GLSL ES 3.00 specification](https://registry.khronos.org/OpenGL/specs/es/3.0/GLSL_ES_Specification_3.00.pdf).
The contract preserves the **parsed float32 value**, not arbitrary real-number
precision or cross-driver runtime arithmetic.

The related audit exposed a nonfinite identifier collision: `float inf=.5;` plus
an overflowed `1e40` literal previously emitted `float(inf)` and linked successfully,
silently reading `.5`. NaN could similarly bind `nan`. The generator now rejects all
nonfinite float literal nodes through its existing error state. Native translation
reports failure and uses the existing stage fallback; it does not substitute zero.
The standalone formatter still provides nonfinite diagnostic text to the reader.
Runtime nonfinite arithmetic is outside this literal policy.

## Reproduction and measured scope

The exact handoff control is committed as
`core/src/test/native/projectm-regressions/float-literal-control.milk`:

```hlsl
(q1 * 1.00000011920928955078125 - 1.0) * 4194304.0
```

The per-frame equation supplies `q1=1`; warp green is `.375`; the composite red
is `.25 + warp_red*.5`, preserving green. The preexisting handoff froze expected
RGB8 `(64,96,0)` for six-digit emission and `(128,96,0)` for preserved float32
before its capture. Neither coefficient nor scale was edited.

A fresh task-owned API 34 ARM64 emulator with the Apple M4 Pro GLES3 translator
reproduced these predictions at **every pixel**, at 256×144, mesh 48×32, one frame,
zero PCM. Each run used one indexed preset, no skips, and frame serial delta 1.
Standard trails was inactive at 144p. A Java/JNI wrapper was rebuilt from current
`CoreBackendRunner.java`, with capture dimensions changed to 256×144 and frame
serial/trails metadata added. Its matching clock/transport helper was rebuilt from
current `core_backend_clock.cpp`; clock interposition affects the runner, while
both extracted AAR libraries remain unchanged. Each run used a fresh process and
role-specific private files. The synthetic asset overlay supplied only the exact
preset/index. The published baseline AAR hash matches the engineering handoff.

| Artifact | RGB8 | Raw top-down RGB8 SHA-256 |
|---|---|---|
| Published 2.3.8 AAR | `(64,96,0)` | `2f4f540e783fcdb105a0f641ceb8509c9f8d63f1661caed04033e88326388774` |
| Locally rebuilt candidate release AAR | `(128,96,0)` | `14e97d8c85b433581afa4a126f40344345c18150e4dbb5392b16370576e6a257` |

![Published baseline capture](baseline.png)
![Candidate capture](candidate.png)

The host CGL full-engine test independently reproduced the same before/after values.
The markers distinguish ordinary fallback outcomes; direct program-handle
attribution remains unavailable through this JNI wrapper. There is no physical-TV
FPS, thermal, or full-corpus appearance claim. A published final-AAR reproduction
is required after release; the local candidate has the build's default local base
version and is identified by its checksum, not a new release number.

## Validation and identities

`results.json` records upstream/base/patch identity, local AAR/native/archive/helper
hashes and both JNI capture metadata records. Raw logs, generated GLSL and transports
remain in the task worktree's ignored `build/` and `/tmp/projectmtv-float-*` logs.
The permanent native tests and source-adapter tests reproduce the behavior without
those local files.

- Formatter tests first failed with `0x3f800001 -> float(1)`; the full-engine render
  first failed at `(64,96,0)`. Fixed tests preserve 20 boundary values plus 99,609
  deterministic random finite values out of 100,000 generated bit patterns,
  including subnormals, extrema, fractions and signed zero. Comma-decimal/global
  grouping controls retain classic spelling. All 20 generated GLES3 controls link.
- The nonfinite collision test first accepted the shader on both GLSL targets;
  the final generator rejects it, plus directly injected ±infinity and NaN nodes.
- All 95 preset SHA-256 values match the supplied inventory, and all 99 authored
  AST witnesses preserve their emitted/reparsed float32 bits. The shared fixture is
  `tools/milk-analyzer/fixtures/float-literal-presets.json`; `float-literal-presets`
  directly compiles all 95 affected sections through production `MilkdropShader`
  with real CGL, bypassing fallback exception handling.
- Native runner: engine/policy controls and all 18 real-projectM groups pass under
  ASan/UBSan. The separate EGL/GLES transition-overlay check is skipped on macOS
  without those development libraries; the CGL render controls run. All 44 patches
  apply to a fresh pinned recursive export.
- All 95 affected sections translate and link offline as GLSL ES 3.00 with explicit
  descriptors derived from the production sampler scanner (`offline-presets.json`).
  This separates source/compiler compatibility from the real CGL stage test and
  the bounded JNI pixel control.
- Release-tooling suite: 135 passed (no release tooling changes).
- Full source-analysis suite: 199 passed, using rebuilt reader/translator adapters.
  Metadata stamps `float_literal_policy=float32-roundtrip-v1` and the formatter
  source hash. Lowering already consumes `renderer_literal`, so it follows the
  rebuilt engine automatically. Historical measurement/calibration fixtures keep
  their historical identities and were not regenerated or relabeled.
- Complete projectM host suite: 261 passed. The existing array-initializer emission
  expectation was updated for `.0` spelling; its full-array behavior is unchanged.
- `:core:assembleDebug :core:assembleRelease :app:assembleDebug testDebugUnitTest`
  succeeds with JDK 21, SDK 34, NDK 27.3.13750724, both production ABIs. No Java/JNI
  API or routine release-version change.

Documentation evaluated: README, user guide/Pages sources, architecture, attribution,
release guide, analyzer/core-corpus/Preset Lab guides and the Markdown inventory.
README, user-guide troubleshooting/development, architecture, attribution, analyzer
instructions and AGENTS were updated. Release/setup instructions and historical
reports retain their existing scope. Strict MkDocs build passes.

## Related-code audit: remaining bounded findings

The audit covered numeric formatting/scanning in hlslparser, preset values,
projectm-eval, JNI and the source analyzer. No independent six-digit runtime shader
emitter was found. `HLSLTokenizer::GetTokenName` uses `%f` only for syntax diagnostics;
JNI rounded numeric logs likewise do not feed shader execution.

The following inherited issues are separate from AST-to-GLSL serialization and
were reproduced with synthetic inputs; this patch does not change their contracts:

| Finding | Reproduction | Path / limits |
|---|---|---|
| Decimal-to-double-to-float double rounding | `1.000000059604644830901776231257827021181583404541015625` becomes AST `0x3f800000`; direct float parsing yields `0x3f800001` | `Engine.cpp::String_ToDouble` → `HLSLTokenizer::ScanNumber`; no ≥18-fractional-digit candidate found in bundled shader lines. Direct float parsing needs a separate locale/range/ABI compatibility change. |
| Unchecked integer narrowing | Decimal `4294967296` and hexadecimal `0x100000000` become token `0` on this ARM64 host | `Engine.cpp::String_ToInteger` and `HLSLTokenizer` hexadecimal scan; `long` width makes overflow behavior ABI-dependent. No above-INT_MAX bundled shader candidate found. |
| Host C numeric locale affects non-HLSL parsers | Under `LC_NUMERIC=de_DE.UTF-8`, preset `stof("1.25")` and actual evaluator expression `1.25;` yield `1`; C locale yields `1.25` | `PresetFileParser::GetFloat`, evaluator `Scanner.l` / pre-generated `Scanner.c`; project code does not change LC_NUMERIC, so exposure requires an embedding host that does. HLSL scan/format already uses classic locale. |
| Float-width named constants in double evaluator | `$pi` yields `3.1415927410125732`; explicit decimal yields `3.1415926535897931`; `$e` / `$phi` similarly narrow | `Scanner.l` and generated `Scanner.c` use `f` suffixes before assigning the default double evaluator. No named-constant uses found in bundled presets; no visual impact established. |

These need separate parsing/evaluator policy work and regression coverage. They are
recorded rather than hidden by a claim that this serializer fix makes all numerical
behavior exact.

## CI GLES readback portability follow-up

[Main run 37439022977](https://github.com/johnneerdael/ProjectM-TV/actions/runs/37439022977)
at merge `b62511ccd96fb868024fdfb9afac677bfe557b10` built the APK and core AAR,
but both native-test jobs failed only `float-literal-render` with `float control GL error`.
The earlier local CGL and Android JNI captures used different readback paths:
the CGL regression requested RGB, while the JNI helper already requested RGBA.
The GLES regression's RGB request was a test portability defect.

An isolated Ubuntu 24.04 ARM64 Mesa probe reported llvmpipe (LLVM 20.1.2),
OpenGL ES 3.2 Mesa 25.2.8. Its RGBA8 framebuffer advertised implementation read
format `0x1908` (RGBA), type `0x1401` (unsigned byte). Before readback there was
no GL error; RGB readback returned `0x502` (INVALID_OPERATION); RGBA readback
returned no error and `(128,96,0,255)`. The
[OpenGL ES specification](https://registry.khronos.org/OpenGL/specs/es/3.0/es_spec_3.0.pdf)
guarantees RGBA/UNSIGNED_BYTE for normalized fixed-point read buffers, with
additional implementation-selected pairs. Desktop OpenGL's RGB support cannot
be assumed in GLES.

The regression now reads four bytes per pixel as RGBA, keeps its exact RGB
assertions at four-byte offsets, and drops alpha only when writing the optional
three-byte RGB PPM. A separate pre-readback error check distinguishes rendering
errors from readback errors. Production renderer, formatter patch 0044, authored
presets and the independent `(128,96,0)` prediction are unchanged.

The original test also fails at readback on Linux x86_64 Mesa softpipe with
ASan/UBSan enabled; changing only the readback/conversion code makes the same
control pass and restores `(128,96,0)` at every pixel. Its optional P6 export is
still packed RGB, with raw hash
`14e97d8c85b433581afa4a126f40344345c18150e4dbb5392b16370576e6a257`,
matching both the original CGL and Android JNI preserved-literal captures.
Corrected macOS CGL runs pass all 18 groups under ASan/UBSan and preserve that
same P6 byte hash.

Local driver limitations were kept separate from the reported CI failure. A native
ARM64 Linux container on llvmpipe timed out in 12 baseline GL groups (random-texture
manager/stages/shorthand/numerical/lifecycle/blur-framebuffers/midgit-render,
shader-render, float-literal-render, parser-presets, initialization-presets and
float-literal-presets). An emulated x86_64 llvmpipe run crashed in LLVM's JIT during
EGL context creation, before rendering/readback. These were observed on unchanged
baseline source and do not supply a passing suite. The functional red/green
comparison uses Mesa softpipe on x86_64 with sanitizer checks retained; neither
repository timeouts nor the CI llvmpipe backend were changed. See
[Mesa's backend selection documentation](https://docs.mesa3d.org/envvars.html).

The first full softpipe pass completed 17 of 18 groups; `implicit-input-bindings`
printed its successful assertions but timed out during process exit. Its isolated
rerun passed in 0.34 seconds. The complete repeat then passed all 18 groups in
24.89 seconds. The exact `core/src/test/native/run_native_tests.sh` command also
passed all engine/policy checks, all 18 groups and the EGL fade tests under
ASan/UBSan with `GALLIUM_DRIVER=softpipe`. This emulation-side instability is
recorded separately from the deterministic RGB readback failure; no check or
timeout was disabled to obtain the successful sanitized runs.

## Published AAR verification

Release [v2.3.10](https://github.com/johnneerdael/ProjectM-TV/releases/tag/v2.3.10)
from `fa18cbab14552a2903e331f74102260fc29c2455` published after the native,
Preset Lab, APK/AAR and documentation jobs passed. Its public notes include the
unpublished PR #41 fixes and the PR #42 readback correction.

The downloaded published core AAR SHA-256 is
`3bc37560a87000ec7ac446895fee8ad09e93b5c83a601014b5fc396bd1f3e6d6`.
The same unchanged one-frame control through its extracted ARM64 JNI library
produces `(128,96,0)` at every pixel, raw RGB hash
`14e97d8c85b433581afa4a126f40344345c18150e4dbb5392b16370576e6a257`.
The task-owned API34 emulator used the original capture dimensions, mesh and zero
PCM; one preset, no skips and frame serial delta1 were verified. Source/AAR/native,
helper hashes and metadata are recorded in `published-2.3.10.json`. This completes
the published-AAR control without broadening the appearance/performance claim.
