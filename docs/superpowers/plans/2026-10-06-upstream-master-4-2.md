# Upstream master 4.2 rebase implementation plan

> **For agentic workers:** Execute the independent porting units in isolated scratch clones, then integrate and validate sequentially.

**Goal:** Successfully rebase ProjectM TV Engine onto immutable upstream master while retaining the supported TV behavior.

**Architecture:** Pin upstream master and retain local changes as an ordered patch series applied during configuration. Reconstruct old patched source for characterization and provenance, port against upstream abstractions, and preserve the public core interface.

**Tech stack:** Java, Android framework/GLES 3.0, C++17, CMake, Gradle, upstream projectM 4.2 development snapshot.

**Spec:** `docs/superpowers/specs/2026-10-06-upstream-master-4-2-design.md`.

## Global constraints

No routine version bump; no commits of modified upstream source; keep API21 and both Android ABIs; preserve Native trails, audio, lifecycle and host integration; honor repository review/merge/release gates. Scratch clones are ignored build artifacts, not shipped dependencies.

## Units

### 1. Baseline and upstream assessment (root)

- [x] Verify target repository, current upstream commit and isolated worktree.
- [x] Recover any prior work; no prior migration artifact was found.
- [x] Reconstruct all 44 old patches with per-patch commit IDs.
- [x] Read current public board and cited vcpkg comment.
- [ ] Run the reconstructed baseline host suite and record failures.
- [ ] Write per-item relevance and per-patch disposition reports.

### 2. HLSL compatibility port (independent agent)

**Goal:** Preserve translator numerical/parser/implicit-input behavior while dropping upstream equivalents.
**Files:** scratch clone `vendor/hlslparser/` and `tests/libprojectM/PresetShaderTranslationTest.cpp`; output `build/upstream-rebase/shader-port.patch` and disposition JSON.
**Approach:** Apply the cumulative old delta with three-way merge against current upstream; resolve against current upstream implementation, preserve tests and attribution. Do not edit renderer, shared tests CMake or tracked patch series.
**Execution:** Characterization first with existing regression tests; add focused coverage for changed semantics.
**Verification:** Final diff has no conflict markers and upstream-equivalent fixes are omitted; root integrates and runs host/parser/render controls.
- [ ] Complete port and disposition.

### 3. Evaluator compatibility port (independent agent)

**Goal:** Keep per-thread random state and lone-dot compatibility against upstream evaluator 1.0.7+.
**Files:** scratch flattened `vendor/projectm-eval/`, `tests/libprojectM/EvaluatorLoneDotTest.cpp`; output `build/upstream-rebase/evaluator-port.patch` and disposition JSON.
**Approach:** Assess old0004/0020/0034 against evaluator22fb0cfd; drop upstream equivalents, preserve focused tests. Do not edit shared tests CMake or other files.
**Execution:** Characterization first.
**Verification:** Evaluator delta applies against pinned nested gitlink; evaluator tests pass after integration.
- [ ] Complete port and disposition.

### 4. Renderer and API port (root)

**Goal:** Preserve the final maintained TV rendering/API behavior using current renderer abstractions.
**Files:** upstream `src/`, remaining host tests and CMake; tracked `tools/projectm-patches/`, `third_party/projectm` gitlink, core JNI and build configuration when needed.
**Approach:** Port the cumulative local renderer delta with three-way source comparison; remove obsolete fixes, adapt texture/mesh/GL-loader ownership explicitly, preserve new upstream behavior. Integrate independent vendor ports into a clean series.
**Execution:** Characterization first; regression first for migration-specific loader/resource changes.
**Verification:** Fresh series application, host suite, sanitizer controls, Java tests and both ABI builds.
- [ ] Resolve source conflicts.
- [ ] Integrate complete ordered patch series and new pin.
- [ ] Validate native/JVM/APK/AAR and core API consumer.

### 5. Docs, review, merge and release (root)

**Files:** AGENTS.md, README.md, docs/THIRD_PARTY.md, architecture/release/development/user-guide sources and affected tooling docs.
**Verification:** Docs agree with final implementation, strict MkDocs passes, PR includes substantive release notes, validation and documentation assessment. Final-head Codex review, required CI, merged main SHA, publication and Milkbeat update are verified.
- [ ] Evaluate and update all affected documentation.
- [ ] Obtain comparable TV rendering/lifecycle evidence or record concrete blocker.
- [ ] Open ready PR, complete final-head Codex review and CI.
- [ ] Merge and verify automatic release/Milkbeat update.
