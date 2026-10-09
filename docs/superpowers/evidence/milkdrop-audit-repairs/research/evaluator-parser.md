## Scope and inspected identity

Read-only investigation of **I01, I02, I03, I04, I09 and M01** against the current patched source in `.worktrees/milkdrop-audit-repairs`. No files were edited; no builds, tests, GL work or device operations were performed.

All **9,606 current bundled preset hashes match the supplied inventory**. Relevant MilkDrop2 files are byte-identical between `/Users/jneerdael/Scripts/milkdrop2/src` and the original 2.25c source tree: `state.cpp`, `milkdropfs.cpp`, `nseel-compiler.c`, `asm-nseel-x86-msvc.c`, and `ns-eel.h`. MilkDrop3 was not used as an oracle.

The shipping series inspected contains patches **0001–0017**, with current0017 being custom-wave input windows. I19’s sample-cap proposal is outside that series.

## Disposition table

| ID | Current source finding | Recommended disposition | Bundled-source evidence |
|---|---|---|---|
| **I01** | Keys and lookup prefixes are lowercased; first occurrence wins after normalization. Original GetFast compares case exactly. | **Retain tolerant-loading policy.** Document strict-MD2 divergence and duplicate precedence; do not globally restore case-sensitive loading. | Exactly two handoff candidate files match their hashes. Each contains three mis-cased queried keys. No mixed-case duplicate keys found. Neither has confirmed visual impact from this difference. |
| **I02** | File booleans use parsed integer `>0`; original main flags use `!=0`. | **Small compatibility repair is feasible:** use nonzero conversion, coordinated with M01 and a declared contract change. | No literal-negative recognized file flags found. No original witness confirmed. |
| **I03** | Division and reciprocal powers suppress small operands using `1e-5`, including assignment variants. | **Repair only formerly suppressed finite results**, preserving existing zero, invalid-domain and overflow protections. Do not remove `COMPARE_CLOSEFACTOR` globally. | No small literal EEL divisor/power-base trigger found. Dynamic denominators remain possible; no original confirmed. |
| **I04** | `%` and `%=` return a signed integer remainder; original x86 applies absolute values before unsigned division. | **Defined-domain sign repair is feasible**, with explicit integer-width and undefined-input limits. Do not copy original unchecked 32-bit casts blindly. | No exact negative-integer witness confirmed. A broader scan finds `%` in 4,111 preset files, which is an exposure inventory, not an affected count. |
| **I09** | `$pi`, `$e`, `$phi` are float literals promoted into the double evaluator. Original expands them into decimal strings. | **Narrow safe correction:** remove the `f` suffix from the existing three literals in both lexer sources. | No named-constant EEL occurrences found. No original witness confirmed. |
| **M01** | Negative custom-wave enable becomes false before drawing/frame evaluation; original integer enable is truth-tested directly. | **Resolve together with I02**, or explicitly retain/version `>0` and align the external predictor. Initializers must remain unconditional. | No negative custom-wave enable literals found. No original witness confirmed. |

These are source-backed recommendations, not implemented or runtime-qualified resolutions.

## I01 — tolerant preset keys

[Production parser](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/PresetFileParser.cpp:164) lowercases stored keys and keeps the first occurrence. GetCode/GetInt/GetFloat/GetString likewise lowercase requests. [Original lookup](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/state.cpp:142) uses `strcmp`; [original zoom import](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/state.cpp:1397) requests lowercase `zoom`.

The two unchanged candidates are:

- `PyroCybin - Computronium [stahlregens gelatine finish].milk`, SHA256 `71450433120e7c01fc82f269226341b462ba1834d83c09c1287d7935eb1d6bf5`.
- `PyroCybin - Toxic Lithography [stahlregens gelatine finish].milk`, SHA256 `7d1ba79abe1bdf49be179d481913f39865959c1f159fb4e9946e764c27ebccb3`.

In both files, line4 is `PSVERSION_comp=3`, line33 is `fwarpAnimSpeed=.5`, and line34 is `fwarpScale=2.331`. Current loading accepts all three. Original defaults are composite shader version **2**, warp animation speed **1**, and warp scale **1**—so the shader candidate does **not** imply the original disables its composite shader. See [version defaults](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/state.cpp:1315) and [motion defaults](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/state.cpp:654).

Both presets explicitly set warp amount0 and contain custom warp/composite code. The key mismatch establishes loaded-state differences, but neither its geometry nor appearance consequence is confirmed.

**Regression design:** exercise actual `PresetFileParser` with canonical/mixed-case keys and mixed-case duplicates in both orders. Assert tolerant lookup and normalized first-occurrence precedence. Include GetCode prefixes and unchanged shader text; only keys should be normalized.

**Finite diagnostic:** use `ZOOM=2` and:

```ini
per_frame_1=ob_size=.05*zoom;ob_r=1;ob_g=0;ob_b=0;ob_a=1;
```

Current loaded zoom2 gives border size.1; strict original default1 gives.05. The expected-stage surrogate can explicitly use canonical `zoom=1`. Label it a source-oracle diagnostic, not an original Windows screenshot.

**Risk:** changing global casing would withdraw support from existing authored files and alter duplicate selection. Retaining it adds no new runtime work. No strict-import mode is justified by the inspected originals.

## I02 and M01 — one shared boolean conversion

[GetBool](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/PresetFileParser.cpp:143) currently returns `GetInt(...) > 0`. It serves main settings, custom-wave enable/styles, and custom-shape enable/styles. [Original wrapping](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/state.cpp:1406) uses `!=0`; [original wave import](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/state.cpp:1191) retains the integer enable; [original draw gate](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:2600) truth-tests it.

A coordinated native compatibility repair is the one-line `>0` → `!=0` conversion. Zero/positive values, missing keys, and invalid-input defaults retain their current behavior. It deliberately changes negative inputs across all callers, including custom shapes—not only M01.

[Current custom-wave gate](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/CustomWaveform.cpp:96) precedes frame and point equations. However, [initialization](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/CustomWaveform.cpp:58) is unconditional, with [all waves compiled/initialized](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/MilkdropPreset.cpp:553). Preserve that ordering.

**Meaningful regressions:**

- Parse each boolean family using `-2,-1,0,1,2`, missing keys and invalid text.
- Assert loaded wrapping, inversion, wave/shape enable and style flags.
- For M01, set `wave_0_init1=reg01+=1;`, `wave_0_per_frame1=reg00+=1;`, and count point evaluations independently.
- Disabled variants must still execute init once, with no frame/point work.
- Enabled variants must execute frame once per frame and point once per authored point; Native geometry replay must not execute either again.
- Assert main-frame `q1=reg00` on the second frame, since the main frame runs before custom-wave drawing.

**Screenshot diagnostics:**

- I02: `bInvert=-1`, no shaders, no geometry and zero feedback. Current output remains black; nonzero compatibility produces white. Also retain the exact `bTexWrap=-1` scalar/sampler witness with a known edge field.
- M01: negative-enabled two-point red horizontal wave; point code `x=.25+.5*sample;y=.5;r=1;g=0;b=0;a=1;`. Current omits it; compatibility draws it. Supply valid mono arrays and separation0.

**Contract risk:** enabling formerly negative-disabled waves introduces their authored equations and draw work. That is expected compatibility behavior, but must be disclosed. The handoff’s `scene_equations.py` belongs to the other predictor worktree and is absent here. Current [native_reader.cpp](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/tools/milk-analyzer/native_reader.cpp:479) already delegates activation to production GetBool. An external predictor contract still needs a coordinated update or recorded follow-up.

## I03 — finite reciprocal results versus protective policies

The production implementations are:

- [division](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/vendor/projectm-eval/projectm-eval/TreeFunctions.c:567),
- [division assignment](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/vendor/projectm-eval/projectm-eval/TreeFunctions.c:746),
- [power assignment](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/vendor/projectm-eval/projectm-eval/TreeFunctions.c:840),
- [power](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/vendor/projectm-eval/projectm-eval/TreeFunctions.c:974).

Division suppresses `abs(denominator)<1e-5`; power suppresses `abs(base)<1e-5 && exponent<0`, then separately replaces NaN results with0. Original [x86 division](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/ns-eel2/asm-nseel-x86-msvc.c:812) directly divides; [pow binding](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/ns-eel2/nseel-compiler.c:551) calls `pow`.

The guards are inherited evaluator1.0.7 behavior, identified as upstream historical0020 in [patch provenance](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/docs/UPSTREAM_PATCH_VALUE.md:81). This is a protective-contract refinement, not removal of an accidental TV change.

**Minimal bounded repair:** within the formerly suppressed region, permit a nonzero division or power result only when the computed result is finite. Preserve exact-zero suppression, suppressed-region overflow/invalid outcomes, the existing general NaN-to-zero power rule, and all outside-region behavior. Apply this consistently to all four functions. Preserve argument evaluation and assignment aliasing.

Do not change comparison/boolean epsilons or the unrelated cotangent guard.

**Regression design:** compile and execute real EEL for `/`, `/=`, `pow`, `^`, `^=` and their intrinsic aliases. Cover ±1e-6 divisors; positive1e-6 and negative1e-6 bases with integer negative exponents; .0001 and exact.00001 boundaries; positive exponents; ±zero; fractional invalid powers; and finite-input overflow. Assert stored assignment variables and expression results. Existing evaluator tests explicitly protect zero division and zero negative power.

**Finite visual diagnostic:** separately map `q1=1/.000001` and `q2=pow(.000001,-1)` into outer/inner border widths:

```ini
per_frame_1=q1=1/.000001;q2=pow(.000001,-1);
per_frame_2=ob_size=.02+.08*q1*.000001;ib_size=.02+.08*q2*.000001;
```

Use explicit opaque colors. Before, both widths are.02; finite-compatible expected widths are.1. Capture Q values as the primary proof.

**Risk:** recovered finite values can materially amplify authored control signals. Preserve resource ceilings and existing undefined-domain policies. CPU work increases only where the old guard skipped arithmetic; no measured performance claim follows.

## I04 — absolute integer remainder

[Current `%`](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/vendor/projectm-eval/projectm-eval/TreeFunctions.c:588) and [current `%=`](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/vendor/projectm-eval/projectm-eval/TreeFunctions.c:821) cast into `PRJM_EVAL_I`, then use signed remainder. This type is int64 for the default double evaluator.

Original [modulo](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/ns-eel2/asm-nseel-x86-msvc.c:860) applies `fabs`, converts to 32-bit integers, and uses unsigned division; assignment does the same. The normal 32-bit evaluator call wrapper sets [round-toward-zero](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/ns-eel2/nseel-compiler.c:225). Therefore finite, exactly representable `(-5)%2` gives original1 versus current−1 without a rounding ambiguity.

**Repair boundary:** absolute-valuing a defined signed remainder matches the original bounded sign behavior while retaining current integer width. Convert the remainder to floating point before `fabs`; avoid `llabs(INT64_MIN)`. Account for signed-minimum divided by−1 before executing C remainder. Nonfinite and out-of-range float-to-integer conversion remains a separate policy problem; do not describe this as universal modulo parity.

Keep renderer mode aliases and HLSL floating modulo untouched.

**Regression design:** execute `%`, `%=` and intrinsic aliases with all ±5/±2 combinations, exact multiples, fractional truncation within signed32 range, zero divisor, assignment aliasing, and argument side effects. Assert both return and assigned values.

**Finite screenshot diagnostic:**

```ini
per_frame_1=q1=(-5)%2;ob_size=.1;ob_a=1;
per_frame_2=ob_r=.5+.5*q1;ob_g=.5-.5*q1;ob_b=0;
```

Before is green; source-compatible expected is red.

**Original candidates:** `390 threx no more warningsce Rumbo Pal Recodo.milk` has active shape3 position-folding expressions `x%2` and `y%2` at lines698–699, SHA256 `ae12392bb5713fddc484b5835209b374ff9646781e48d9bbd164bec7785d7b70`. Its operands depend on gmegabuf and Q values; negative nonzero remainders are unconfirmed. The `martin - beamer…` subtraction/modulo candidate is weaker: its `ind` result is not used in the inspected branch. Neither is a confirmed original witness.

## I09 — named constant precision

[Scanner.l](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/vendor/projectm-eval/projectm-eval/Scanner.l:66) and [Scanner.c](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/vendor/projectm-eval/projectm-eval/Scanner.c:1426) use:

```c
3.141592653589793f
2.71828183f
1.61803399f
```

Original [constant expansion](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/ns-eel2/nseel-compiler.c:1077) supplies those same decimals without intermediate float rounding.

Remove only the `f` suffixes. Do **not** substitute longer mathematical e/phi values. Update both files: Android [disables Flex/Bison regeneration](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/core/src/main/cpp/CMakeLists.txt:91), so changing Scanner.l alone would leave shipping behavior unchanged.

**Regression design:** compile/execute lowercase and uppercase named tokens; compare evaluator values against explicitly parsed matching decimals before shader/geometry float conversion. Include expressions subtracting each matching decimal, ordinary numeric tokens, and the existing lone-dot controls. Preserve thread-local random state.

**Finite screenshot diagnostic:**

```ini
per_frame_1=q1=($pi-3.141592653589793)*10000000;
per_frame_2=ob_size=.02+.1*abs(q1);ob_a=1;ob_r=1;ob_g=0;ob_b=0;
```

Current q1 is approximately.874228, producing width≈.107423; corrected q1 is0, producing.02. This is deliberate amplification of a scalar precision difference, not evidence that stock presets visibly differ.

**Risk/dependency:** no new evaluation, allocation or GL pass is needed. This correction belongs upstream in projectm-eval. Preserve the exact checked-in scanner delta and TV lone-dot/random repairs.

## Integration and evidence requirements

Parser changes belong to libprojectM; I03/I04/I09 belong to projectm-eval, as the repository’s [upstream guidance](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/docs/UPSTREAM_PATCH_VALUE.md:130) already distinguishes.

None of these recommendations requires changing presets, Native reference coefficients, trails gains, geometry replay, rotation/power transport, texture ownership, or patches0016/0017.

Run scalar/parser regressions first, then capture the declared finite diagnostics at matched authored dimensions and Native Standard4K. For retained policies, a captured explicit-value oracle is useful expected-stage documentation, but must be labelled as a diagnostic surrogate. No confirmed original runtime witness or completed screenshot evidence was produced in this read-only investigation.
