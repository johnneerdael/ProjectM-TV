# Retained component image proof implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every substantive retained component of current patches 0001–0003 a clear GPU comparison of upstream projectM 4.2 and our library, in addition to the existing current0004–0013 evidence.

**Architecture:** Extend the existing direct-libprojectM EGL capture harness with focused host sequences and observable GL operation/resource counts. Keep upstream and current sources, presets, textures, PCM, frame clock and geometry inputs matched. Use actual framebuffer images for appearance and measured diagnostics alongside images for changes that preserve appearance.

**Tech stack:** Existing C++17/GLAD/EGL worker, NDK27.3.13750724, task-owned API36 Android TV emulator5630 with Apple M4 Pro host GPU; existing Python/Pillow capture and verifier.

**Spec:** The user's request for a comparison for each retained component, and the component inventory in `docs/UPSTREAM_PATCH_VALUE.md` §§0001–0003. The historical mapping is provenance only.

## Global constraints

- Preserve current13-patch source bytes and engine/evaluator pins; do not modify production renderer, assets or versions.
- Use only task-owned GPU Android TV devices. Keep captured user0, seed12345, frame/30, mesh48×32 and identical frozen synthetic PCM for each pair.
- Preserve historical workers, receipts and images. New experiments use fresh work directories and new source/harness/binary identities.
- Reconstruct source, rebuild/canonical-check executable identity, retain complete RGB payloads, check GL errors and two independent repeats.
- Classify enhancements and host policies accurately. Patch0010 is an enhancement; fixed-width MilkDrop lines are the baseline for #682.
- Label generated diagnostics, altered presets, operation counts and historical4.1.7 evidence separately from unchanged artist presets and current4.2 GPU frames.
- Keep raw streams and binaries under ignored build paths. Commit selected PNGs, source/preset identities, protocols and results.
- A frame that remains visually identical is valid preservation evidence but does not by itself prove a cache, resource or performance benefit.

## Review focus

- Cross-component effects: a full-library image difference must not be attributed solely to batching or caching when another rendering change is active.
- Failed shaders: record fallback/omitted code and intentional rejection; never replace a rejected render with a black screenshot.
- Low/high resolution: retain the one-pixel minimum, verify actual dimensions, and show high-resolution line effects with aligned crops.
- GL observer state: counters/allocation controls must not redirect bindings or alter one role alone; negative controls must expose an observer fault.
- Driver limits: binary-export failures remain explicit. Do not weaken GL validation to obtain a caching result.

## Comparison matrix

Every row needs upstream/current frame panels, a plain-language explanation and a source-bound receipt. Component-specific diagnostics accompany panels where the expected image is unchanged.

| Component | Controlled trigger / expected evidence | Status |
|---|---|---|
| High-resolution quad lines and optional AA (#682) | Unchanged line-heavy preset at low/reference/high sizes; matched 4K frame and aligned crop; current classic/quad control for attribution. | Pending |
| Reference sample/fade/blur/canvas policy | Dense main wave and blur-reading original; freeze reference dimensions; show full frames plus sampled dimensions/LOD. | Pending |
| Vertex-shader cleanup on fragment rejection | Repeated intentional fragment rejection followed by valid render; frame panels plus live shader-object counts. | Pending |
| Defined fresh/reused feedback history | Fresh allocation and pooled reuse with controlled initial bytes; actual first-read pixels, caller-state control and first-frame preset panels. | Pending |
| Explicit warp sampler unit-zero reservation | Original mixed qualified/main samplers; rendered alias lookup plus sampler/unit observations. | Pending |
| Ordered custom-shape batching | Many shape instances, fixed draw/evaluation order; frame panels plus GL draw/upload counts. | Pending |
| Evaluate-once geometry replay | Stateful equation/RNG geometry drawn on two targets; frame panels plus evaluation/RNG counts. | Pending |
| Texture pooling | Load/retire/reload same-size targets; frame panels plus allocation/reuse/retained-byte counts; pooled clears verified separately. | Pending |
| Translated GLSL cache | Reload identical custom shaders across engine instances; frame panels plus translation/cache-hit counts. | Pending |
| Program-binary cache | Cold/warm driver program load; frame panels plus compile/load/hit counts. Preserve the known API36 export limitation if it prevents the measurement. | Pending |
| Uniform-location and program-bind caches | Identical repeated rendering; frame panels plus queried-location/bind counts. | Pending |
| Flip reuse | Motion-vector-off sequence plus vector/resize invalidation; frame panels and copy-pass counts. | Pending |
| Direct blur attachment rendering | First use, unchanged size, resize and fallback; blur/preset pixels plus copy/draw/binding observations. | Pending |
| Visibility-gated motion-vector UV output | Runtime hidden/shown vector phases; unchanged hidden frame plus UV-target/pass counts. | Pending |
| Final-orientation video echo | Unchanged classic echo preset and orientation control; pixels plus copy/draw counts. | Pending |
| Discard preservation and authored blur-read timing | Clip/discard composite and blur-reading warp; actual preserved pixels, first-use/resize control. | Pending |
| Direct composite output and switch history | Caller target, stored-output control, subsequent host switch; matched frames and pass/history counts. | Pending |
| HLSL array initializer layout (0002) | Recover unchanged original with flat local/global array initializer; if no suitable original exists, explicitly labeled shader fixture; fallback status and visible authored output. | Pending |
| Writable uniform initialization (0002) | Original shader writes to incoming globals, including helper/out/inout; code-level activation and visible authored output. | Pending |
| Contextual identifiers/macros/postfix (0002) | Existing Madness/dimension-window evidence; add distinct activation control where a language component is not exercised. | Partial — existing original images |
| Float emission and implicit globals (0002) | Existing coefficient/implicit-global controls, plus visible shader frame and emitted-value/uniform diagnostics. | Partial — existing controls |
| Evaluator lone-dot compatibility (0003) | Existing unchanged Stahlregen and diagnostic frames. | Captured — audit retained evidence |
| Evaluator thread-local RNG (0003) | Existing fresh-thread streams; frame panels from a controlled concurrent-evaluation sequence plus random-stream diagnostics. | Partial — existing numerical control |

## Tasks

### Task 1: Verify the source-to-executable evidence chain

Files: `tools/patch-proof/{source_identity,prepare,capture,verify}.py` and their tests.

- [x] Reconstruct each claimed source role from pinned git inputs and canonical patch bytes.
- [x] Retain full RGB streams and recompute every frame hash.
- [x] Rebuild and canonical-check the executable using the exact pinned NDK and checked-in harness; exercise upstream/current/without0010 control roles.
- [x] Run the tool tests and fresh GPU replay, commit, reply and resolve the corresponding PR thread. Source/binary-bound replay verifies720 frames;33 controls pass at this milestone; fix a54d0e9f and threadPRRT_kwDOPcunRM6qIf5s are recorded.

### Task 2: Capture the high-resolution line enhancement first

Files: extend `tools/patch-proof/native/worker.cpp` only as required by controlled jobs; add new receipts/images under `docs/superpowers/evidence/current-patch-proof/components/`.

- [x] Select an unchanged original, inspect its active paths and freeze its hash: `Geiss - 3D - Shockwaves.milk`, a classic main-wave preset, from the separate11-candidate source screen. The33 named historical controls remain available for follow-up.
- [ ] Capture upstream/current with identical inputs at low/reference/4K sizes. Retain a current-library classic/quad API control to separate the reference-scaling enhancement from other patch effects.
- [ ] Verify complete frames/repeats/binary identity and GL status. Inspect full frames and identical nearest-neighbour crops; select a visible frame without brightness manipulation.
- [ ] Add the #682 comparison and mechanism/limits to current0001, explicitly disclosing miter/flat ends and related reference-size policy.
- [ ] Commit and push this independently reviewable milestone.

### Task 3: Capture compatibility/correctness components

Files: focused worker/control helpers and `components/` receipts; update current0001–0003 descriptions.

- [ ] Recover original activation sources for arrays, writable uniforms and qualified samplers from the pinned regression inventory.
- [ ] Add component diagnostics using existing engine/GL interfaces for shader lifetime, attachment initialization/bindings and stateful geometry replay. Observe a failing negative control before relying on each observer.
- [ ] Execute the corresponding matrix rows twice per role; require stable inputs, full payload verification and clean expected GL handling.
- [ ] Publish per-component frame panels, measured diagnostic panels, code-level causes and preservation limits.
- [ ] Commit/push each coherent component group; mark matrix rows captured only after validation.

### Task 4: Capture optimizations and host capabilities

Files: focused host event sequences/GL observers and `components/` receipts.

- [ ] Count actual translations, shader compiles, binds, uploads, copies, draws and allocations using shared observers, without inferring a speedup from fewer operations.
- [ ] Execute all optimization/host rows, including resize/switch/discard/fallback controls; preserve identical-frame outcomes as explicit results.
- [ ] For each row, publish upstream/current frame panels plus measured operations/resources and the exact activation contract.
- [ ] Keep any unmeasurable driver-specific row pending with the concrete recorded failure; do not substitute a timing or appearance claim.
- [ ] Commit/push the completed groups and update this matrix.

### Task 5: Final document and repository gates

- [ ] Audit every matrix row against real files/results; remove incomplete contribution claims and label all limitations.
- [ ] Confirm report navigation/local links, strict MkDocs, source/preset/version invariants and appropriate native/tool tests.
- [ ] Sync current main, update PR release notes and obtain completed final-head Codex review with all threads resolved.
- [ ] Pass required CI, merge through GitHub, and verify automatic publication/Milkbeat update as required by AGENTS.md.
