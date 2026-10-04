# Engineering handoff: initialization and selector proofs (4 presets)

Date: 2026-10-04. Owner task: source predictor blocker reduction, draft PR #25.

This handoff concerns **ProjectM-TV:core**, our patched native engine, not an
unpatched upstream binary. Use a separate worktree based on current `main`.
Implement engine fixes as `tools/projectm-patches/*.patch`; do not commit edited
`third_party/projectm` submodule files. Keep authored presets unchanged.

The checkpoint contains 23 distinct blocked presets from the original 315-case
subset: 16 parsing, four initialization and three random-binding cases. These
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

## Assignment and attribution

Do not treat all four cases as native bugs. One lacks an analyzer range proof;
three read authored globals before assignment and need a defined target-language
and engine initialization policy. Arbitrary zero filling would mask uncertainty.
All four exact source hashes have successful saved baseline rows; successful or
repeatable rendering does not prove a read is defined.

Evidence fixtures:
`tools/milk-analyzer/fixtures/remaining-uninitialized-5-2026-10-04.json` (historical5;
exclude the resolved New Creation case) and
`tools/milk-analyzer/fixtures/focused-blockers-23-helper-scratch-2026-10-04.json`
(current4). New Creation was resolved by component-level untouched-Q inference;
the three helper scratch ordering cases were resolved separately. Do not count
those as remaining native defects.

| Exact preset filename | Full-file SHA-256 | Section |
|---|---|---|
| Serge + martin - crystal palace tunnel003.milk | `f4ab74c7f561e50177b1b68ecf647045de78582ba378e39bb9295d26a55fd4e2` | warp_ |
| martin - ludicrous speed.milk | `9a99802ec59187a9f635f615db07622c5feaa15d02ed64beefb8156e68d48b22` | warp_ |
| martin - mandelbox explorer - wreck diver nz+ liquititty.milk | `2d767a8f65168592fc25b0e70accb968fa5b118296b64f66a62e5f889a9faddd` | comp_ |
| martin - organic light.milk | `71c481a0ebc470c3a9e717630cdd3785f4217248f81cbe6157cf1da99914698e` | comp_ |

## I1: prove the selector domain in ludicrous speed

`martin - ludicrous speed.milk`, warp:

```hlsl
float2 arg;
int k2=int(q29);
int k1=k2%4;
if(k1==0){arg=...;}
else if(k1==1){arg=...;}
else if(k1==2){arg=...;}
else if(k1==3){arg=...;}
uv+=arg*...;
```

Its main equations initialize `index4=rand(12)`, update
`index4=(index4+is_beat*bnot(index)*bnot(index2)*bnot(index3))%8`, and assign
`q29=index4`. Prove initialization and the recurrence, including is_beat's range,
all writes, evaluator rand/remainder behavior, frame ordering and float32-to-int
conversion. For a finite nonnegative q29 in int range, k1 is0–3 and the branches
are exhaustive. Without that proof, negative or non-finite inputs remain unresolved.

Likely fix owner: analyzer input-domain/control-flow analysis in
`tools/milk-analyzer/equation_loading.py`, `scene_equations.py`, `shader_fields.py`
and numerical domain handling. Native changes are needed only if actual native
behavior contradicts the established language policy. A finite sample of input
frames is a control, not proof for every reachable input. Include negative,
non-finite, overflow and changed-recurrence controls that must remain uncertain.

## I2: crystal palace reads mus without assigning it

`Serge + martin - crystal palace tunnel003.milk`, warp:

```hlsl
float3 mus;
// inside shader_body:
float3 ret1=crisp+mus+dots;
```

No earlier shader assignment initializes mus. Determine what legacy D3DX treats
this global as and what generated current GLSL declares/binds. If a compatibility
zero default is established, implement it narrowly with a versioned policy and
numerical controls. Do not generalize a global default to uninitialized locals.

## I3: mandelbox reads dist_c before its later assignment

`martin - mandelbox explorer - wreck diver nz+ liquititty.milk`, composite:

```hlsl
float dist_c;
// inside shader_body, in this order:
float focus=sat(abs(GetDistB(uv)-dist_c)*3);
// other work...
dist_c=clamp(GetDistB2(center),.1,.4);
```

A later assignment cannot initialize an earlier read. Determine the original
legacy default and current per-invocation storage semantics. Moving the assignment
would alter authored behavior and requires a separately justified preset repair;
it is not a parser fix. Compare a minimal control with explicit zero initialization
and one with a nonzero initializer, preserving order.

## I4: organic light uses uv3 before its first write

`martin - organic light.milk`, composite:

```hlsl
float2 uv3;
// inside shader_body:
uv3=.4*cos(42*uv3)+64*dz;
```

The right side reads uv3's old value. Do not infer persistent shader-variable state
from the previous framebuffer: feedback texture persistence is a separate mechanism.
Establish legacy global-default versus current translated storage, then select a
narrow target policy or explicitly retain the preset as unresolved.

## Native/reference code to inspect

Current engine: `vendor/hlslparser/src/HLSLParser.cpp`, `HLSLTree.cpp`,
`GLSLGenerator.cpp`; `MilkdropShader::LoadVariables`; main Q initialization and
copying in `PerFrameContext` / `PresetState`. Keep merged global uniform-copy fixes.

Supplied reference: `/Users/jneerdael/Scripts/MilkDrop3/code/vis_milk2/plugin.cpp`
(D3DX shader compilation and constant reflection) and `milkdropfs.cpp` (named
constant binding). Source inspection alone has not established matching core
zero defaults for mus, dist_c or uv3. Check default handling/compiler reflection
and actual generated declarations before patching.

## Exact saved baseline joins

- Serge + martin - crystal palace tunnel003.milk: `/Users/jneerdael/Scripts/Projectm-TV/.worktrees/quad-lines-follow-ups/build/follow-ups/core-corpus/measurements-core-emu-baseline-v1/rows/b8d846b1f9b5d1fb7245d34a36f851c1dde3d5756bcabdc5e9292ae2dab35ec2.json`; saved row hash `44ee49948d1ae0aaa080d71995528663effd85238d1fa0aba427ca88e75028de`.
- martin - ludicrous speed.milk: `/Users/jneerdael/Scripts/Projectm-TV/.worktrees/quad-lines-follow-ups/build/follow-ups/core-corpus/measurements-core-emu-baseline-v1/rows/6852a7e4fd112f67efdfb79268345a6fb86086f2144a1286437f9ebce9d7874f.json`; saved row hash `25821dfe3b187829fc472cc6285302feee9ccde24d0ec9a720ae79c7b563876d`.
- martin - mandelbox explorer - wreck diver nz+ liquititty.milk: `/Users/jneerdael/Scripts/Projectm-TV/.worktrees/quad-lines-follow-ups/build/follow-ups/core-corpus/measurements-core-emu-baseline-v1/rows/655b87fa4b14d21cccce47b1ff664038ab4a388baf5b60c9c277b7e7ca5ed19c.json`; saved row hash `d982325c510dcb721bd3a75fc675fcd60efe87d041a17776c176439d58fd529d`.
- martin - organic light.milk: `/Users/jneerdael/Scripts/Projectm-TV/.worktrees/quad-lines-follow-ups/build/follow-ups/core-corpus/measurements-core-emu-baseline-v1/rows/42d373bec3c6c33d095a4228bb43b77e77e7f9bb815fcedb640eb58f4e297587.json`; saved row hash `200287ffb3fa8c593f59765d32e9f80987a47a09dc50b5f14f73bc6c220201c4`.

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
