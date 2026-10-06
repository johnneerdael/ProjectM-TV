# Upstream master 4.2 rebase implementation plan

> **For agentic workers:** Execute the independent porting units in isolated scratch clones, then integrate and validate sequentially.

**Goal:** Successfully rebase ProjectM TV Engine onto immutable upstream master while retaining the supported TV behavior.

**Architecture:** Pin upstream master and retain local changes as an ordered patch series applied during configuration. Reconstruct old patched source for characterization and provenance, port against upstream abstractions, and preserve the public core interface.

**Tech stack:** Java, Android framework/GLES 3.0, C++17, CMake, Gradle, upstream projectM 4.2 development snapshot.

**Spec:** `docs/superpowers/specs/2026-10-06-upstream-master-4-2-design.md`.

## Global constraints

No routine version bump; no commits of modified upstream source; keep API 21 and both Android ABIs; preserve Native trails, audio, lifecycle and host integration; honor repository review/merge/release gates. Scratch clones are ignored build artifacts, not shipped dependencies.

## Units

### 1. Baseline and upstream assessment (root)

- [x] Verify target repository, current upstream commit and isolated worktree.
- [x] Recover any prior work; no prior migration artifact was found.
- [x] Reconstruct all 44 old patches with per-patch commit IDs.
- [x] Read current public board and cited vcpkg comment.
- [x] Run the reconstructed baseline host suite: 261/261 pass.
- [x] Write separate per-item/per-patch report in `docs/UPSTREAM_PATCH_VALUE.md`; final-device limits remain explicit.

### 2. HLSL compatibility port (independent agent)

**Goal:** Preserve translator numerical/parser/implicit-input behavior while dropping upstream equivalents.
**Files:** scratch clone `vendor/hlslparser/` and `tests/libprojectM/PresetShaderTranslationTest.cpp`; output `build/upstream-rebase/shader-port.patch` and disposition JSON.
**Approach:** Apply the cumulative old delta with three-way merge against current upstream; resolve against current upstream implementation, preserve tests and attribution. Do not edit renderer, shared tests CMake or tracked patch series.
**Execution:** Characterization first with existing regression tests; add focused coverage for changed semantics.
**Verification:** Final diff has no conflict markers and upstream-equivalent fixes are omitted; root integrates and runs host/parser/render controls.
- [x] Complete port and disposition.

### 3. Evaluator compatibility port (independent agent)

**Goal:** Keep per-thread random state and lone-dot compatibility against upstream evaluator 1.0.7+.
**Files:** scratch flattened `vendor/projectm-eval/`, `tests/libprojectM/EvaluatorLoneDotTest.cpp`; output `build/upstream-rebase/evaluator-port.patch` and disposition JSON.
**Approach:** Assess old 0004/0020/0034 against evaluator `22fb0cfd`; drop upstream equivalents, preserve focused tests. Do not edit shared tests CMake or other files.
**Execution:** Characterization first.
**Verification:** Evaluator delta applies against pinned nested gitlink; evaluator tests pass after integration.
- [x] Complete port and disposition.

### 4. Renderer and API port (root)

**Goal:** Preserve the final maintained TV rendering/API behavior using current renderer abstractions.
**Files:** upstream `src/`, remaining host tests and CMake; tracked `tools/projectm-patches/`, `third_party/projectm` gitlink, core JNI and build configuration when needed.
**Approach:** Port the cumulative local renderer delta with three-way source comparison; remove obsolete fixes, adapt texture/mesh/GL-loader ownership explicitly, preserve new upstream behavior. Integrate independent vendor ports into a clean series.
**Execution:** Characterization first; regression first for migration-specific loader/resource changes.
**Verification:** Fresh series application, host suite, sanitizer controls, Java tests and both ABI builds.
- [x] Resolve source conflicts, preserve upstream Mesh/ShaderCache ownership, add burn-in and blur controls.
- [x] Integrate three patches with master `6f6480746` / evaluator `22fb0cfd`; clean-export application passes.
- [x] Validate native/JVM/APK/AAR and the exact-AAR Milkbeat consumer; final CI remains separate.

### 5. Docs, review, merge and release (root)

**Files:** AGENTS.md, README.md, docs/THIRD_PARTY.md, architecture/release/development/user-guide sources and affected tooling docs.
**Verification:** Docs agree with final implementation, strict MkDocs passes, PR includes substantive release notes, validation and documentation assessment. Final-head Codex review, required CI, merged main SHA, publication and Milkbeat update are verified.
- [ ] Evaluate and update all affected documentation.
- [ ] Obtain comparable TV rendering/lifecycle evidence or record concrete blocker.
- [ ] Make [draft PR #46](https://github.com/johnneerdael/ProjectM-TV/pull/46) ready after device evidence; complete final-head Codex review and CI.
- [ ] Merge and verify automatic release/Milkbeat update.

## Verified local checkpoint (2026-10-06)

These checks cover the recorded migration revisions. They do not replace final-head CI, GitHub Codex review or the TV matrix.

- Reconstructed baseline host suite: 261/261. Integrated master host suite: 329/329. Production native runner passes engine/render-policy checks and 21/21 ASan/UBSan CGL controls. EGL transition overlay skips on macOS because EGL/GLES development files are unavailable; Linux EGL CI remains open.
- Three patches apply to a clean upstream export. ARM64/ARMv7 debug/release core and profile APK builds pass. A fresh recursive `85ceac83` checkout builds debug core and release APK for both ABIs. Release JVM reports 30 app + 54 core tests without failures.
- Milkbeat `6802630c2db1983607b8693ac4bd4ce208f80c74` builds `githubDebug` against the exact migration AAR, SHA256 `c57c823d18e5e33c0fcb4c779e41eece0a3d613cf95092351a86a4332c864075`; all 28 focused consumer tests pass and ARM packaging matches that artifact. This completes the local consumer check, not the automatic release/update gate.
- Standard Preset Lab full suite: 164/164 including three native controls. Later focused worker-build/Android-header guard suite: 7/7; no inferred full-suite total. Milk-analyzer: 199 passing tests. Native trails/corpus tooling: 75 passing tests plus 35 subtests. Release tooling: 157 passing tests. Strict MkDocs build passes.
- AM6 Android 9 live-Milkbeat smoke renders at 1920×1080 and the three-line unreleased-master/pin label fits. Tracks differed between smoke runs, so sampled FPS is not a causal performance comparison. Task properties/preferences/listener state were restored after that profile check.

## Validation tooling review corrections

Local review found that copied CPU shader bodies needed production logging declarations and that public frame-time assignment alone left constructor/init timing unfrozen. The adapters now retain unchanged copied bodies with production logging; private clocks start at zero and use the upstream API before both JNI render calls. A time/progress-sensitive preset repeats six frames exactly across delayed fresh processes, while the uncorrected constructor-clock control diverges. The Android GLES compile regression prevents the private hook from importing desktop GLAD on Android.

Builders resolve engine/evaluator pins from the requested source commit. Frozen 24/44-patch historical sources retain their own identities; the candidate uses the three-patch master series. Rebase worker packages are distinct from existing corpus packages. Instrumented workers are separately hash-identified test artifacts, not shipping-byte-identical releases. Their historical timing/sample metadata literals require the explicit source-based limits in the comparison protocol.

## Device evidence and remaining gates

The completed frozen-audio pilot covers one preset, 1920×1080, Standard inactive, eight selected captures among 480 frames, two repeats per role and one Mali-G52/GLES 3.2 TV. Captures repeat bit-for-bit within each role, while cross-role differences are localized and reach RGB byte MAE 2.66 at frame 479. The source analysis does not support attributing this difference to the coordinate correction; its cause remains unproven. This is not a 4K/native-active, minimum-GLES-3.0-only, full-corpus or performance conclusion.

The four-witness frozen-audio TV matrix completed all 32 jobs. Same-role sampled captures repeat exactly; midgit has a material green/blue difference and remains the immediate investigation priority. The latest readiness gate is 100 frozen random presets with the same seed and zero pixel changes, plus the known midgit regression. Final documentation/evidence reconciliation, ready-PR status, final-revision CI and GitHub Codex review, merge, publication and automatic Milkbeat update remain unchecked.

## User clarification: full library and released baseline

The authoritative baseline is the latest released ProjectM TV core AAR, not stock libprojectM and not an instrumented rebuild. Verified on 2026-10-06: v2.3.11, source `b1bb994dbfaa04159630570cd9b2c255b173a6bd`, AAR SHA256 `3bc37560a87000ec7ac446895fee8ad09e93b5c83a601014b5fc396bd1f3e6d6`, checked against GitHub asset digest and release checksums. Freeze this artifact; record any later baseline change explicitly.

Evaluate all 44 historical patches and their affected or potentially affected presets across the full 9,606-preset inventory. Static candidates are not visual certification; resource/lifecycle changes can affect the whole inventory. The user's latest completion criterion is at least **100 randomly chosen presets with the same fixed seed and zero pixel changes**. Freeze the unbiased sample before rendering, without replacing failed presets. Use selection seed 12345 and render seed 12345, matching initial clock, PCM, settings, frame numbers and device/backend. Require same-role repeatability and exact old/new RGB equality; include midgit as an additional regression witness. The previous four-witness/32-job comparison does not satisfy this gate. Do not certify untested presets or infer full-corpus equivalence from the sample.

Build private workers embedding unchanged released baseline and candidate AAR bytes and verify packaged library/asset identity. The released JNI lacks deterministic seed/initial-clock controls. Keep unchanged-AAR runtime evidence separate from source-instrumented deterministic diagnostics; the user approved fixed-seed/fixed-clock deterministic source comparisons alongside unchanged released-AAR runtime checks. Do not silently relax exact fidelity, label untested presets verified, or proceed to readiness/merge before the expanded gate is satisfied.
