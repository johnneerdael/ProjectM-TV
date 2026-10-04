# Engineering handoff: random texture aliases and binding context (3 presets)

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

## Assignment and evidence boundary

Establish the actual runtime binding of `sampler_rand00` and `sampler_rand01`, then
fix any alias/descriptor/asset-context mismatch and expose enough binding identity
for the analyzer. These same three presets appear under both `dynamic sampler
expression` and `sampler_state` gap labels; they are **three**, not six, presets.

Explicit sampler2D declarations can make offline translation compile without
proving which texture the native renderer selects. The analyzer intentionally
does not clear them on that basis. A current production binding bug is not yet
certified: first determine whether the remaining issue is native association,
missing runtime inputs, or only analyzer binding instrumentation.

Merged PR #26 already handles sampler-state removal/scanning syntax. Do not repeat
that historical51-case fix or claim these three still have the old parser failure.
Reference core2.2.8 contains74 texture-like assets under assets; this is not proof
they are extracted or discoverable at runtime. Check actual extraction/search paths.

| Exact preset filename | Full-file SHA-256 | Section |
|---|---|---|
| EoS - glowsticks v2 04 music minimal - swim  - dictatutorial rt roam3 2.milk | `5dd383cf79e1aacbed944ded85d70a365dde2c51f2ca7646ed0b7fde0cf4c79f` | comp_ |
| EoS - glowsticks v2 04 music minimal - swim  - dictatutorial rt roam3.milk | `06b84ff69c3aeeb88eff3dea63dd3c1f5b146b4c2afb9df204f5f2561e7aee15` | comp_ |
| midgitstraights of majillaen - featy sweet.milk | `d4cd997dedc57ab34c7247fee1ba94d4061528d12d16cde5a468145fb216ebba` | comp_ |

## Authored behavior to preserve

All three composite shaders declare two random aliases with WRAP overrides and
sample both. The two EoS versions have identical shader source hash
`829742c66b7b88cf305c32924842b12fec26a26bf367ef4b861975e2ee0e5c5d`;
the midgitstraights shader hash is
`7904cb659869118fed10df59aeb127f3597b34b8abf400b7e0cb5ec7482bedc3`.
Their full-file hashes differ, so test each preset's complete context.

```hlsl
sampler sampler_rand00=sampler_state {AddressU=WRAP;AddressV=WRAP;};
sampler sampler_rand01=sampler_state {AddressU=WRAP;AddressV=WRAP;};
shader_body {
    ret=tex2D(sampler_rand00,uv).xyz;
    ret+=tex2D(sampler_rand01,uv).xyz;
}
```

The real shaders additionally rotate coordinates, combine feedback/blur and scale
by audio. Do not replace random textures with noise or main feedback merely to
produce a compilable shader. Decide/document name-prefix sampler policy versus
ignored authored sampler_state fields using actual target behavior.

## Trace and fix the whole binding chain

Inspect these functions in the patched engine snapshot/current main:

- `MilkdropShader::GetReferencedSamplers` and `PreprocessPresetShader`: preserve
  the exact alias through scanning and state removal.
- `MilkdropShader::LoadTexturesAndCompile`: strips a two-letter filtering/wrapping
  prefix for random recognition, resolves slots00–15, caches descriptors in
  `PresetState::randomTextureDescriptors`, and reuses them across warp/composite.
- `TextureManager::GetRandomTexture`: scans files, applies optional suffix-prefix
  filtering, obtains a selected texture descriptor and names the descriptor with
  the original random alias. It returns an empty descriptor when no files match.
- `TextureManager::ExtractTextureSettings`, `TextureSamplerDescriptor`, generated
  sampler/texsize declarations and descriptor uniform binding: verify GL texture
  target, alias name, unqualified name, filter/wrap state, assigned texture unit
  and matching shader uniform. Also inspect core asset extraction/search-path setup.

Check reuse of one random slot under differently qualified names: reuse must keep
texture selection shared where intended without losing the current shader's alias
or requested sampler mode. Do not assume a cached descriptor's original name is
valid for every later qualified alias. The private lab fixes random seeds for
reproducibility; production random seeding is different and must be recorded.

## Required binding diagnostics and controls

For each alias, record requested name, parsed slot/filter/prefix, selected asset
path and content hash, texture dimensions/target, descriptor names, sampler mode,
unit and generated uniform. Record missing/prefix-miss paths explicitly. Check
custom-versus-fallback stage selection and retain compiler messages. If all native
bindings are correct, deliver a source-bound analyzer descriptor manifest instead
of an unnecessary renderer patch.

Use an isolated test directory with two distinguishable textures of known values
and dimensions. Under a controlled seed, verify alias-to-asset identity and compare
source-predicted numerical output for each alias independently. A visual screenshot
or shader compile alone cannot validate this association. Include:

- rand00/rand01, same-slot reuse across both stages, different slots, and same
  slot under fw/fc/pw/pc qualified aliases.
- Optional randNN prefix suffix; empty directory and no matching prefix.
- Spaced/unspaced sampler_state declarations; ignored state fields versus
  explicitly named mode, with a documented policy.
- Stable per-preset selection, preset switch/reset, reload, and normal production
  randomness without silently inheriting the lab's seeded policy.
- Unqualified main and named main/blur/noise controls, retaining patch0026 ordering.

Analyzer locations: `coverage_audit.py` currently guards random aliases from
explicit offline-binding credit; `shader_fields.py` / `sampling_policy.py` must
consume only a source/runtime-bound association. Clear those guards only after
identity/provenance and lifecycle semantics are established.

Evidence: `fixtures/focused-blockers-23-helper-scratch-2026-10-04.json`, the older
sampler-state fixture/handoff (historical syntax), and the prepared35-patch
`MilkdropShader.cpp` / `TextureManager.cpp`. Keep histories distinct.

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


## Latest merged-engine predictor checkpoint

PR29 and PR30 are merged into main. A fresh37-patch reader/translator recheck of
the original315 files clears all16parser blockers, leaving **6** source/lowering
gaps: the three global-input cases and three random-binding context cases. No new
blockers or source-token inventory changes appeared. See
`fixtures/focused-blockers-6-merged29-30-2026-10-04.json`. This supersedes earlier
22-case counts; it does not certify Android/AAR appearance. The global-input owner
continues those three cases; the predictor owner handles random context adoption.
