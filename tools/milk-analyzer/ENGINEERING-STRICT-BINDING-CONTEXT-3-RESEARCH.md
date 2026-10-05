# Engineering research report: three strict random-binding context cases

Date: 2026-10-05. Repository: johnneerdael/ProjectM-TV. Predictor branch:
`feat/preset-audience-scoring`, task worktree
`/Users/jneerdael/Scripts/Projectm-TV/.worktrees/preset-genre-analyzer`.

## Finding and research objective

The source audit still reports three composite sections as unresolved under the
strict GLES300/Android context. **This is not evidence of three remaining native
renderer bugs.** The immediate cause is known: the analyzer withholds descriptor
bindings for random aliases without matching context, and its current observed
context validator only accepts host GLSL330 evidence. Determine whether the
correct fix is source-contract interpretation, Android context/provenance capture,
or a separately reproduced engine defect. Do not start from an assumption that
PR30's alias fixes failed.

All three original shader sections already parse and translate. The two gap labels
`shader expression not lowered: sampler_state` and `dynamic sampler expression`
refer to the same three presets, not six. The original315-subset recheck against
2.3.3's41-patch source leaves only these three; the parser and global-initialization
cases clear. Source interpretation is separate from successful full rendering and
from visual/mood accuracy.

## Exact affected presets

Paths are relative to `core/src/main/assets/presets/`. Preserve these files and
verify the full-file hash before reproducing.

| Exact filename | Full-file SHA-256 | Section / file lines |
|---|---|---|
| EoS - glowsticks v2 04 music minimal - swim  - dictatutorial rt roam3 2.milk | `5dd383cf79e1aacbed944ded85d70a365dde2c51f2ca7646ed0b7fde0cf4c79f` | comp_ / 714–745 |
| EoS - glowsticks v2 04 music minimal - swim  - dictatutorial rt roam3.milk | `06b84ff69c3aeeb88eff3dea63dd3c1f5b146b4c2afb9df204f5f2561e7aee15` | comp_ / 655–686 |
| midgitstraights of majillaen - featy sweet.milk | `d4cd997dedc57ab34c7247fee1ba94d4061528d12d16cde5a468145fb216ebba` | comp_ / 505–535 |

The two EoS composite sections share shader-source SHA-256
`829742c66b7b88cf305c32924842b12fec26a26bf367ef4b861975e2ee0e5c5d`.
Midgit's composite source SHA-256 is
`7904cb659869118fed10df59aeb127f3597b34b8abf400b7e0cb5ec7482bedc3`.

They all contain the following pattern (the full shaders also rotate coordinates,
combine feedback/blur and scale colour by audio):

```hlsl
sampler sampler_rand00 = sampler_state { AddressU=WRAP; AddressV=WRAP; };
sampler sampler_rand01 = sampler_state { AddressU=WRAP; AddressV=WRAP; };
shader_body {
    ret=tex2D(sampler_rand00,uv).xyz;
    ret+=tex2D(sampler_rand01,uv).xyz;
}
```

## Exact artifact and completed fixes

Use the **standard** published `projectM-TV-core-2.3.3.aar`, not an older AAR or the
separate core-native flavour. Release commit:
`6e71ac2a18a95463fbe3a21c05e6dd4027cb74a0`.

- AAR SHA-256: `e83be55299d310e6282204cb39740cfe09d1e2609471eb58c6299c8961eec9eb`.
- ARM64 libprojectmtv.so SHA-256: `ee1f57e20a1f438809c8c8b2121be19fa23ff8ca640a2b50857bee9b04c9e34d`.
- It includes41native patches, including PR29 parsing, PR30 random aliases,
  PR33 global-input policy and PR34 blur framebuffer ownership.

The old midgit GL error1286 is historical: PR34 diagnoses and fixes framebuffer
bindings saved after blur allocation had unbound them. Its before/after host
manifest reports1286→0. Do not reopen that issue from the older PR30 JSON; retest
2.3.3 before alleging a current failure. Full authored-preset Android rendering
and appearance have not yet been certified by this predictor's current controls.

## Immediate analyzer failure path

Inspect the files in the predictor worktree (the focused main analyzer is a
separate subset; do not overwrite broader predictor work):

1. `tools/milk-analyzer/coverage_audit.py`, `audit_source`, around lines128–146:
   random aliases keep `bindings=None` unless a context is supplied and verified.
2. `random_binding_context.py`, `verified_context`, around line15: only
   `glsl330` with `host-real-GL-production-random-device-v1` is accepted. GLES300
   is deliberately refused; the captured manifest is an observed host pair.
3. `shader_fields.py`, `native_sampler`, around lines409–417: sampler_state
   declarations become ordinary typed inputs only when native_samplers supplies
   their dimensions. Without context, the initializer remains unsupported.
4. The texture-call path around line784 then reports a dynamic sampler expression
   because its operand is not a typed input. These labels do not imply runtime
   texture handles actually change each frame.

With verified PR30 host context, **all three exact composite sections lower with
no unresolved sampler expressions**. The importer checks source/policy/asset
hashes, pair-wide slot consistency, per-stage unit consistency, dimensions under
the declared upload policy and sampler modes. Old host render errors remain
separate from valid binding identity. Missing/stale context keeps the guard.

## Published-AAR numerical evidence

The unchanged2.3.3 native library was exercised in the task-owned API34 ARM64
learning emulator:128×72,30fps,48×32mesh,30frames per control, explicit PCM and
clock adapter. The helper's JNI ABI was checked against2.3.3. The emulator was
stopped after the bounded tests; shared corpus devices/TVs were not operated.

The isolated asset namespace contains one16×16PNG with RGB8=[51,102,153]. The
following predictions were frozen before capture:

| Control | Expected result | Maximum RGB8 error across30frames |
|---|---|---:|
| rand00 | sampled constant image | 1 |
| rand01 | sampled constant image | 1 |
| two slots | half the sum of the two samples | 1 |
| qualified fw_rand00 | sampled constant image | 1 |
| same-slot cross-stage | composite outputs half the warp image | 1 |
| cross-stage qualified alias | composite outputs half the warp image | 1 |

Half-colour composite output prevents an equal-colour default composite from
masquerading as successful alias lookup. All six alias controls pass the declared
≤1RGB8 tolerance. An empty-pool negative control is retained as diagnostic, not
credited as a successful random binding. Three global-input controls also match
the new policy; they are not these random-context cases.

This proves bounded alias behavior with the supplied asset set. It does **not**
identify images selected in a later arbitrary production load, validate every
sampler mode/asset decoder, or certify the three full authored visuals.

## Important fixture/protocol traps

- Core init extracts bundled AssetManager textures into the search folder. Our
  first attempted single-image test actually had75images after combining the AAR
  assets with an overlay. Those predictions failed and are preserved. Merely
  adding one PNG to a folder does not isolate the texture pool. The corrected
  test uses an overlay-only asset namespace and the unchanged published library.
- SOIL can resize images during upload. The observed host rounds NPOT images up
  to powers of two:320×160→512×256,500×400→512×512,190×200→256×256. Validate
  file hashes and decoded dimensions under the actual driver/upload policy;
  do not compare raw image dimensions blindly with descriptor texsize values.
- Random image choice is an input for a preset lifetime. Different loads can
  select different images. Preserve slot identity across warp/composite and
  each alias's filter/wrap mode; don't promise one fixed filename from source.

## Research and proposed fix routes

First reproduce the strict audit on one affected file using the prepared2.3.3
reader and source-bound compatibility request; compare no-context versus valid
context. The difference should point directly to the guard above.

Then choose the smallest correct route:

- **Source-contract route:** prove the41-patch TextureManager/descriptor contract
  establishes typed2D random-slot inputs and name-based sampling without needing
  a particular selected filename. Represent selected image/texsize/lifetime as
  explicit runtime inputs. Keep missing images/load failure and complete-render
  errors distinct. This may remove a false language-understanding blocker without
  inventing image contents or claiming a visual match.
- **Runtime-context route:** capture Android alias→slot→selected image path/hash→
  uploaded dimensions/target→sampler mode→unit/uniform for the exact three shaders.
  Bind the manifest to preset/shader hashes, AAR/native hash, asset-pool identity,
  GL profile and selection epoch; feed it to the validator under an explicit
  GLES300 policy. Do not relabel host random choices as Android observations.
- **Native-defect route:** only if a new2.3.3 reproduction contradicts those
  contracts, report and patch the precise native function with before/after
  controls. Keep the original preset unchanged.

Native locations: `MilkdropShader::GetReferencedSamplers`, `PreprocessPresetShader`,
`LoadTexturesAndCompile`; `PresetState::randomTextureDescriptors`;
`TextureManager::GetRandomTexture`, `ExtractTextureSettings`, `LoadTexture`;
`TextureSamplerDescriptor::{SamplerDeclaration,TexSizeDeclaration,Bind}`;
JNI `PresetLibrary::ExtractTextures`; SOIL's NPOT/upload capability handling.

## Evidence and reproducible inputs

Repository/predictor files:

- `tools/milk-analyzer/fixtures/strict-binding-context-research-3-release233.json`:
  exact gaps, source comparison, runtime identities and completed control results.
- `fixtures/random-binding-host-context-37.json` and
  `fixtures/random-binding-host-assets-37.json`: observed host binding records and
  independently decoded metadata; host-only scope.
- `test_random_binding_context.py`: rejects stale hashes, conflicting units,
  cross-stage slot changes, contradictory dimensions and profile extrapolation;
  verifies all three exact host source sections.
- Native merged evidence:
  `docs/superpowers/evidence/random-texture-bindings/` and
  `docs/superpowers/evidence/midgit-framebuffer/` on the2.3.3 release commit.

Local predictor-worktree paths (not all are committed):

- `build/milk-analyzer/focused-315-release233-2026-10-05/`: coverage.jsonl,
  gap-priority.json, compatibility.json, comparison.json and41-patch reader trees.
- `build/milk-analyzer/android-learning/release233-verification/`: probe.py,
  frozen predictions, results, raw RGBA readbacks, metadata and report.json.
- `build/milk-analyzer/android-learning/runtime-core-2.3.3/identity.json`.
- `build/milk-analyzer/core-2.3.3/`: standard published AAR and checksums.
- Earlier failed/corrected controls:
  `android-learning/random-alias-2026-10-04/` and
  `android-learning/random-alias-isolated-assets-2026-10-04/`.

The clock adapter hash is `168ee9cb0afb9a7c54e54e2931c5dd76be7348a14b6b1a6122b6b3ffadf5a58f`;
helper DEX hash is `ca07aba01095d2f59a0923c5154dc84adf29d30a8e0d0fd866f93d6d3f4503d4`.
These are declared test-host inputs, not modifications to the published native library.

## Acceptance and handback

Deliver root-cause attribution and the exact changed guard/context/native code.
Show all three originals interpreted under the declared target context without
preset edits, source-token exclusions or appearance credit from compile success.
Retain negative controls for missing/prefix-miss textures, stale identities,
conflicting aliases, slot reuse, dimension changes and profile mismatches.

For numerical certification, compare independently frozen predictions with native
results under matching source/audio/assets/clock/render settings. Preserve errors
and asset epochs. Check the exact three authored full renders separately from
synthetic alias controls. Recheck the original315 subset and report new gaps;
no duplicate full-corpus render is required.

Do not modify the other agent's corpus/devices. Use a separate engineering worktree
and patch files for any engine change; do not commit edited submodule sources.
Include exact AAR/native/source/asset hashes, before/after evidence, limitations
and the remaining count. A valid outcome may be an analyzer/context fix with no
additional native patch.


## Follow-up result (2026-10-05)

The isolated source-contract fix is recorded in
`fixtures/strict-binding-context-source-contract-2026-10-05.json` and the analyzer
README's conditional random-slot section. It leaves the observed host validator
unchanged and does not add a native patch. Opt-in conditional GLES300 lowering
clears all three exact random-state language gaps while retaining image/texsize/
epoch/fallback obligations. The producer working-state original315 comparison is
3→0, with unchanged inventories and no new blockers. The committed predictor base
alone is6→3 because its helper-generated-copy follow-ups remain pending; they
are not included in this isolated commit. Full authored Android appearance remains
unverified. Six saved2.3.3 alias controls were independently hash/numerically
rechecked with max1RGB8 error; no device or shared corpus was operated.


## Integrated handback (2026-10-05)

The isolated source-contract commit5e0085c6 is now cherry-picked as2a2eefbb after
saving the pending2.3.3 global-input changes. Combined verification passes798tests
and35subtests. The original315 source audit now reports3→0language gaps under the
explicit pinned random-slot policy,with unchanged token inventories and no new
blockers. `fixtures/focused-blockers-0-release233-contract-2026-10-05.json` records
this final local integration checkpoint. Strict/default policy remains available;
runtime texture/texsize/epoch/fallback obligations and unverified appearance remain.
