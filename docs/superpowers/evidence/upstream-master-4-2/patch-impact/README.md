# All-preset historical patch impact inventory

**Scope: all 9,606 presets; 44 historical patches. This is a source-candidate inventory, not a visual fidelity certificate.**

The primary product baseline is the latest released **ProjectM-TV core v2.3.11**, canonical/versioned AAR SHA256 `3bc37560a87000ec7ac446895fee8ad09e93b5c83a601014b5fc396bd1f3e6d6`, verified source `b1bb994dbfaa04159630570cd9b2c255b173a6bd` plus its 44 historical patches. It is not stock libprojectM. User-authorized fixed-seed/clock source comparisons remain distinct from unchanged released-AAR runtime checks.

The inventory used existing native PresetFileParser/EEL/HLSL frontends, original-byte token ownership and sampler/scalar APIs. All 9,606 reader processes completed. Native AST parsing is not actual GLSL-driver acceptance, engine initialization or appearance certification; language extensions and unresolved effects remain explicit.

Shared render/resource/lifecycle/host paths retain an **all-presets potentially affected** scope with activation conditions. Positive source matches prioritize inspection. A missing feature match is not evidence of unchanged output. The complete 44 × 9,606 source-impact inventory remains in scope; the current render acceptance gate below uses the user-approved random sample.

| Original patch | Potential scope/count | Positive source matches | Port/upstream disposition |
|---|---|---:|---|
| `0001-plasma-transition-float-overflow-shield.patch` | All 9,606 | 0 | Upstream equivalent; duplicate source omitted |
| `0002-render-target-resize-program-cache-shader-state.patch` | All 9,606 | 0 | Partial upstream; retained in new 0001 |
| `0003-hlslparser-classic-locale.patch` | 8100 source-domain candidates | 8100 | Partial upstream; retained in new 0002 |
| `0004-projectm-eval-thread-local-rand.patch` | All 9,606 | 5170 | Retained/consolidated in new 0003 |
| `0005-cache-translated-preset-shaders.patch` | All 9,606 | 8100 | Retained/consolidated in new 0001 |
| `0006-custom-shapes-batched-draws.patch` | All 9,606 | 6123 | Retained/consolidated in new 0001 |
| `0007-framebuffer-texture-pool.patch` | All 9,606 | 0 | Retained/consolidated in new 0001 |
| `0008-hlsl-floating-point-modulo.patch` | 8100 source-domain candidates | 551 | Upstream equivalent; duplicate source omitted |
| `0009-tile-gpu-invalidate-and-mesh-orphaning.patch` | All 9,606 | 6968 | Retained invalidation in new 0001; warp orphaning omitted |
| `0010-skip-redundant-previous-frame-flip.patch` | All 9,606 | 791 | Retained/consolidated in new 0001 |
| `0011-indexed-warp-mesh.patch` | All 9,606 | 0 | Partial upstream; retained in new 0001 |
| `0012-merged-warp-pass-direct-blur.patch` | All 9,606 | 6968 | Retained/consolidated in new 0001 |
| `0013-motion-vector-map-only-when-shown.patch` | All 9,606 | 791 | Retained/consolidated in new 0001 |
| `0014-video-echo-in-final-orientation.patch` | All 9,606 | 4679 | Retained/consolidated in new 0001 |
| `0015-keep-output-for-blur-reading-and-discarding-shaders.patch` | All 9,606 | 6968 | Retained/consolidated in new 0001 |
| `0016-direct-composite-output.patch` | All 9,606 | 0 | Retained/consolidated in new 0001 |
| `0017-pcm-max-samples-is-buffer-size.patch` | All 9,606 | 0 | Upstream equivalent; duplicate source omitted |
| `0018-hlslparser-parenthesized-constructor-expressions.patch` | 8100 source-domain candidates | 1843 | Upstream equivalent; duplicate source omitted |
| `0019-hlslparser-number-scan-without-source-copy.patch` | 8100 source-domain candidates | 8100 | Upstream equivalent; duplicate source omitted |
| `0020-projectm-eval-1.0.7-evaluator-fixes.patch` | All 9,606 | 9093 | Upstream equivalent; duplicate source omitted |
| `0021-hlslparser-self-referencing-macros.patch` | 8100 source-domain candidates | 0 | Upstream equivalent; duplicate source omitted |
| `0022-custom-waveform-sample-bounds.patch` | All 9,606 | 4641 | Upstream equivalent; duplicate source omitted |
| `0023-milkdrop-preset-unconditional-shader-includes.patch` | All 9,606 | 6968 | Retained/consolidated in new 0001 |
| `0024-quad-lines.patch` | All 9,606 | 9592 | Retained/consolidated in new 0001 |
| `0025-shader-failure-handling.patch` | All 9,606 | 0 | Partial upstream; retained in new 0001 |
| `0026-custom-warp-sampler-binding.patch` | All 9,606 | 2948 | Retained/consolidated in new 0001 |
| `0027-preset-exception-diagnostics.patch` | All 9,606 | 62 | Upstream equivalent; duplicate source omitted |
| `0028-initialize-fresh-color-history.patch` | All 9,606 | 0 | Retained/consolidated in new 0001 |
| `0029-per-frame-record-compatibility.patch` | All 9,606 | 40 | Consolidated with 0033 in new 0001 |
| `0030-hlslparser-uniform-write-copies.patch` | 8100 source-domain candidates | 2023 | Retained/consolidated in new 0002 |
| `0031-hlslparser-array-initializer-layout.patch` | 8100 source-domain candidates | 57 | Retained/consolidated in new 0002 |
| `0032-sampler-state-preprocessing.patch` | 8100 source-domain candidates | 51 | Retained/consolidated in new 0001 |
| `0033-legacy-equation-code-all-phases.patch` | All 9,606 | 62 | Retained/consolidated in new 0001 |
| `0034-projectm-eval-lone-dot-number.patch` | 9604 source-domain candidates | 7 | Retained/consolidated in new 0003 |
| `0035-leave-out-uncompilable-equation-code.patch` | All 9,606 | 6 | Retained/consolidated in new 0001 |
| `0036-hlslparser-contextual-identifiers-macro-tokens-postfix.patch` | 8100 source-domain candidates | 1947 | Retained/consolidated in new 0002 |
| `0037-random-texture-alias-bindings.patch` | All 9,606 | 192 | Partial upstream; retained in new 0001 |
| `0038-feedback-diffusion-compensation.patch` | All 9,606 | 7898 | Retained/consolidated in new 0001 |
| `0039-feedback-diffusion-build-policy.patch` | All 9,606 | 0 | Retained internally in new 0001; public capped retired |
| `0040-hlslparser-implicit-global-inputs.patch` | 8100 source-domain candidates | 2014 | Retained/consolidated in new 0002 |
| `0041-blur-framebuffer-bindings.patch` | All 9,606 | 6968 | Retained/consolidated in new 0001 |
| `0042-feedback-detail-layer.patch` | All 9,606 | 8909 | Retained/consolidated in new 0001 |
| `0043-authored-geometry-feedback.patch` | All 9,606 | 9555 | Retained/consolidated in new 0001 |
| `0044-hlslparser-float-literal-roundtrip.patch` | 8100 source-domain candidates | 8100 | Retained/consolidated in new 0002 |

## Per-patch activation conditions

- **0001:** Plasma transition executes between any preset pair; overflow in procedural transition shader.
- **0002:** Caller framebuffer, resize-history preservation, program/uniform caches, soft-cut outgoing cadence; host state can activate for any preset.
- **0003:** HLSL numeric scan/float emission invokes locale conversion, including generated shader headers/wrapper values.
- **0004:** Evaluator rand state used by foreground/background contexts; shared-state/race influence cannot be bounded by absence of rand in one file.
- **0005:** Bounded cross-instance translated GLSL cache activates on custom shader preparation and impacts shared memory/load state.
- **0006:** Custom shape instances batch uploads/draw order; shared GL state/resource contract is potentially library-wide.
- **0007:** Color-attachment pool reuse, initialization, context loss and memory pressure; all presets allocate framebuffer history.
- **0008:** Float/vector/integer remainder typing and operator precedence; native typed modulo AST is a direct positive candidate, unknown ASTs stay unresolved.
- **0009:** Full-coverage framebuffer invalidation and old warp buffer orphaning; discard/blur conditions alter applicability. New port retains invalidation, deliberately adopts upstream same-size SubData instead of warp orphaning.
- **0010:** Reuse flipped previous-frame input except first frame, vector draws, resize or invalidated history.
- **0011:** Warp grid geometry/index upload and draw sequence executes for all presets; upstream indexed mesh replaces old mechanism, local replay remains.
- **0012:** Merged warp/geometry pass, direct blur target ownership and fallback for nonrenderable attachments.
- **0013:** Motion-vector UV output eligibility follows runtime mv_a/mv_x/mv_y, including equations and Native consumers, not static settings alone.
- **0014:** Classic video-echo/final orientation and framebuffer target state; shader/version and runtime echo settings gate direct draws.
- **0015:** Preserve discarded-pixel contents and prior-frame blur-read timing; conservative shader text gating and GL history state.
- **0016:** Host direct-composite output vs stored history during transitions/switches/discards; any preset can participate in host transitions.
- **0017:** Public PCM capacity 576 vs 480 affects host audio submission/analysis globally, independent of lexical audio usage.
- **0018:** Parenthesized HLSL constructor followed by an operator; lexical pattern is prioritization, not a complete syntax/visual affected subset.
- **0019:** Bounded numeric scanner invoked across custom HLSL tokenization, including generated shader inputs.
- **0020:** Evaluator tolerance 0.00001 in comparisons/logic/while/division/pow plus error-message ownership; numeric domains/error/resource propagation are not proven from token absence.
- **0021:** Self-referencing object macro expansion; positive same-line identity macro candidate. Aliases, includes and unknown preprocessing cannot be cleared by lexical absence.
- **0022:** Custom waveform sample count/smoothing/separation and bounds; shared audio/resource use remains potentially all presets.
- **0023:** Release/nondebug shader-analysis includes compile correctness; all engine consumers potentially affected, not a preset-content feature.
- **0024:** Reference-size quad lines/points/shape borders/waves/vectors plus blur/fade/sample count and virtual dimensions; runtime references, resolution and host options gate it.
- **0025:** Vertex/fragment/link failure cleanup and diagnostics; any shader or built-in program can fail under driver/resources independently of valid source.
- **0026:** Warp unit 0 implicit main binding vs named point/clamp/wrap aliases; shared GL sampler state and default main path potentially all presets.
- **0027:** Preset/factory/expression owned diagnostics through exception handlers; any load can fail from source/path/resources.
- **0028:** Fresh/reused history transparent-black initialization and context-safe allocation clear; no safe subset from feedback token absence.
- **0029:** Rejected per-frame records retry concatenated/comment-stripped legacy form; accepted path unchanged. Superseded by all-phase 0033 implementation.
- **0030:** Assignments/compound writes/increments/out-inout to global uniforms create initialized shared per-invocation copies; helpers/global initialization order matter.
- **0031:** Scalar/vector array initializer grouping/element conversion and whole-global-array initialization; native typed initializer AST positive candidates.
- **0032:** sampler_state removal/source-position alignment and sampler identifier boundaries before shader_body; native independent AST model may retain states so translation screening is separate.
- **0033:** Legacy retry applies to preset/wave/shape phases including disabled component compilation; source records/comment/semicolon rules and compile diagnostics.
- **0034:** Lone-dot EEL number token maps to0; native existing tokenizer positive evidence, no custom grammar and no visual proof.
- **0035:** Reject only uncompilable equation blocks with warnings/defined init state rather than rejecting preset; malformed preset parse still fails.
- **0036:** Contextual identifier lookahead, reserved sample, macro token spacing/grouping and parenthesized postfix expressions.
- **0037:** Random-image slots 00–15, aliases/filter/wrap descriptors/source paths and cross-stage identity; texture loader/shared ownership potentially all presets.
- **0038:** Reference-scale bilinear diffusion, exact point/composite routing, gating/kernel cap/fallback and cached input invalidation; host dimensions/resources can activate for all presets.
- **0039:** Internal compile-time PROJECTMTV_DISABLE_FEEDBACK_DIFFUSION controls legacy laboratory policy; public capped artifact is retired. Applies across all presets when explicitly used.
- **0040:** Plain uninitialized float scalar/vector globals become external uniforms with initialized writable copies; flags from native transformed AST distinguish supported globals.
- **0041:** Read/draw framebuffer preservation before first-use/resize blur allocation; subsequent geometry can target wrong FBO regardless own blur tokens.
- **0042:** Native feedback canvas/resources, levels, viewport/UV invalidation, frame RNG replay and fallback; runtime host dimensions/levels govern activation for all presets.
- **0043:** Authored geometry feedback/replay and per-vertex shape inputs; main waves/borders/darken center plus shared state make absent custom geometry insufficient exclusion.
- **0044:** Float32 emitted literal round trips, integral float/signed zero and nonfinite AST rejection; generated wrappers/header literals make all active custom shader paths candidates.

## Useful positive source candidates

- `active_custom_shader`: 8100 presets. These are source candidates, not confirmed visual changes.
- `uniform_write_copy_ast`: 2023 presets. These are source candidates, not confirmed visual changes.
- `array_initializer_ast`: 57 presets. These are source candidates, not confirmed visual changes.
- `sampler_state_tokens`: 51 presets. These are source candidates, not confirmed visual changes.
- `implicit_global_input_ast`: 2014 presets. These are source candidates, not confirmed visual changes.
- `random_sampler_tokens`: 192 presets. These are source candidates, not confirmed visual changes.
- `lone_dot_equation_tokens`: 7 presets. These are source candidates, not confirmed visual changes.
- `static_motion_vectors_alpha`: 791 presets. These are source candidates, not confirmed visual changes.
- `raw_equation_rejected`: 62 presets. These are source candidates, not confirmed visual changes.
- `assembled_equation_rejected`: 6 presets. These are source candidates, not confirmed visual changes.

## Current fidelity acceptance gate

The latest user-approved completion criterion is **at least 100 unbiased random presets with seed 12345 and zero output changes**, plus an explicit regression for `midgitstraights of majillaen - featy sweet.milk`. This supersedes the earlier full-9,606 render requirement. The source-impact inventory continues to cover all 44 historical patches and all 9,606 assets; it does not certify untested presets.

Select and freeze 100 distinct presets from the complete sorted catalog using seed 12345 and a recorded deterministic sampling algorithm. Record the ordered filenames and asset hashes. Do not filter, redraw or replace presets because they are slow, fail, are unknown or produce mismatches. Keep the explicit midgit regression separately identifiable, including its activation conditions and source identity.

Use the same fixed render seed 12345, clock, PCM, render profile and device/backend for the verified released-source reconstruction and candidate. First require same-role repeated output; then compare **every full-resolution top-down RGB8 frame** of the frozen render window with exact byte/hash equality. Zero changes means all matched frame hashes are equal. Sampled capture frames, downsampled MAE, skipped, unstable or unknown jobs do not satisfy the criterion. Stream hashes and retain first-divergence witnesses/stage traces to bound storage, preserving exact source/asset/producer identities.

Keep unchanged released-AAR runtime journeys as an independent product-byte check. Minimum GLES 3.0 support, lifecycle/resource controls and the supported Native render paths remain distinct validation concerns; AM6 GLES 3.2 does not prove a 3.0-only driver. Passing the declared 100-preset fixed-seed gate does not establish fidelity for the other presets, future states, songs or drivers.

The lowercase native-setting lookup is fixed, and the analyzer suite passes 206 tests. This removes the identified source-stage classification error; it does not turn parsing or AST extraction into visual evidence.

This inventory task ran no GPU/device tests. Earlier four-preset instrumented comparisons and unchanged-AAR Oscilloscope runtime controls remain separately identified evidence. The compact JSON preserves the original source-impact records and its earlier proposed `next_gate_plan` for provenance; this README's current acceptance criterion supersedes that archived full-corpus render proposal.

## Compaction verification

Original explicit-list JSON: `e2cb787a18cfb15ee497b48cb3b6ec7dfd9b36c90eadfb9a904414fe558d3be5` (122,193,655 bytes, ignored build artifact). Compact JSON: `d99388e904de83f6280dd91370d4c0c0cb4c94b5f4376c90b54d164641aff1a4` (14,900,021 bytes). All 44 potential memberships, positive-match feature metadata, witnesses, unresolved memberships and all 9,606 exact filename/SHA mappings reconstruct identically. Source flags retain candidate labels and do not become confirmed visual effects.

See [schema and export instructions](schema.md) and [compressed machine-readable inventory](impact.json.gz).

Compressed artifact SHA256: `9d76f2ab38f2436e9856521bec2d3cc7a16224707050f6db65154ef5ba228758`; 1,374,075 bytes. Decompression exactly recovers the compact JSON whose digest is recorded above.
