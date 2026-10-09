# Authored Fidelity Followup Implementation Plan

> For agentic workers: use executing-plans for inline execution; source-only independent unit preparation may use ce:work dispatch. User has already authorized execution through merge-ready newPR; no repeat approval required.

**Goal:** Implement I19,I22,I20,I24,I16 and deliver a new merge-ready PR with combined Native4K evidence.

**Architecture:** Five independent ordered renderer patches retain current ownership/replay. Restore already source-proven waveform corrections, capture thickness per shape instance, and qualify the actual previous motion producer without a fake field oracle. Keep diagnostics and immutable snapshots separate.

**Tech Stack:** C++17/projectM/evaluator, CMake/NDK27.3, framework Android/Java, hostCGL and EGL/GLES3.

**Spec:** docs/superpowers/specs/2026-10-09-authored-fidelity-followup.md

## Global Constraints

- Sourcebaseline960eed2c; mainaf164a97; newbranchfix/milkdrop-authored-fidelity; existing28patches preserved.
- User accepts genuinely required authored cost. All previous Native4K/replay/float/nonfinite/texture fixes remain.
- Device5640 only; fixed3840x2160/Standard1280x720,480frames30FPS,mesh48x32,seed12345 and frozenPCM. Exact identities/finalread0.
- Patch source only; no gitlinks, version bump, publicAPI changes, preset mutation or corpus restart.

## Review Focus

- Single-dot NaN input: preserve value while finite point overrides render; no artificial zero.
- Mixed thickness/nonfinite flags: retain instance identity; safe fallback outside defined int domain; no last-instance or replay reevaluation.
- UVproducer discard/output writes: actual prior producer semantics, not an analytic or UV-only substitute.
- Context/resize/two-presets: prevent stale texture leases/generation and first-frame misuse; restoreGLstate.
- Combined cost: compare frozen complete tuple, do not sum separate witness percentages or overlap jobs.

## Tasks

### 1. I19 width-dependent samples

Goal: source caps modes4/6/7 by reference-equivalent width; two-point safety floor; extensions unchanged.
Files: patch0029; core/src/test/native/projectm-regressions/sample_cap_test.cpp; CMakeLists.txt.
Approach/pattern: restore I19/sample_cap_control.cpp realFactory controls and proposed-width-cap.patch against current28.
Execution note: test-first; root owns canonical mutation.
Verification: finite boundary/count/geometry controls fail current then pass; unaffected extended modes/replay; unchangedRoyal103 finalNative captures.
- [x] Restore test and verify RED.
- [x] Add ordered patch, verify GREEN/current suite, commit unit.

### 2. I22 custom dots

Goal: authored point counts and supported one-dot programs; preserve NaNsample, RNG and line smoothing/replay.
Files: patch0030; custom_wave_inputs_test.cpp; CMakeLists.txt.
Approach/pattern: archived with-dot-controls test and proposed-custom-dots.patch; retain currentI08/I06 tests.
Execution note: test-first.
Verification: 0/1/2/thick/thin/ring/line/alias/replay and independent NaN/guard ablations; originalnebula/mosaicNative repeats.
- [x] Restore source tests and verify RED.
- [x] Patch, verify GREEN/current tests and commit unit.

### 3. I20 circle

Goal:239 denominator,240angular/241raw/481smoothed strip; current unblended transition/style preserved.
Files: patch0031; circle_geometry_test.cpp; CMakeLists.txt.
Approach/pattern: archived actualgeometry/draw control and sourceclosure patch.
Execution note: test-first.
Verification: raw/smoothed/sourceformula/counts, aspect/time/mystery, Native thin/thick/dots/replay; unchangedRoyal137/11 captures.
- [x] Restore controls and verify RED.
- [x] Patch, verify GREEN and commit unit.

### 4. I24 evaluated instance style

Goal: preserve evaluated finite int-nonzero thickness per instance and both target draws.
Files: patch0032; shape_thickness_test.cpp; CMakeLists.txt; archived simpleproposal.
Approach/pattern: InstanceDraw captures flag; derive LineStyle per draw; existing LineRenderer APIs/VBOs untouched. Source preparation may be delegated in isolated ignored dir; root integrates.
Execution note: test-first.
Verification: alternating/static/dynamic/fractional/negative/no-assignment/invalid fallback, borderalpha/textures/overlap/batchflush/linefallback/AA/aspects, once-only equations/replay, actualtwo city-lights originals.
- [x] Prepare bounded production repair and independent tests.
- [x] Verify RED/GREEN, sanitizers/resources/Native/cost; integrate after qualification.

### 5. I16 field freshness

Goal: first active consumer uses latest compatible previous completed field, not old enabled field/currentC.
Files: patch0033; motion_uv_freshness_test.cpp; CMakeLists.txt; MilkdropPreset-related isolated source.
Approach/pattern: actual real-fragment publication/lifecycle and existing owner first-frame/texture rules. Source preparation may be delegated; no generic lazy shortcut.
Execution note: characterization plus failing temporal controls.
Verification: on/off/on, multiple disabled, count/alpha off, A=B, default/custom/fallback/discard/output-write, native/authored consumers, resize/context/detail/presets/transition, GLstate/equation/RNG counts, visibleNative fixture with valid feedback.
- [x] Trace current lifecycle and choose qualified production policy.
- [x] Verify RED/GREEN/full ownership controls and integrate.

### 6. Combined acceptance/newPR

Files: docs/evidence/new followup; AGENTS.md; THIRD_PARTY.md; finalPRbody.
Interfaces: all five source patches and controls; frozenbaseline960eed2c plusfinalcandidate.
- [x] Freeze/artifact-build exactbaseline/candidate; validate original/finite/unaffectedNative repeats and captures.
- [x] Measure isolated combined ABBA on relevant original/structural workloads; report absolute/relative cost and selected appearance.
- [x] Fresh normal/sanitizer/host/JVM/bothABI/recursive/docs/helpers/analyzer and Linux/Mesa bothlinkroutes; shaderlink when required.
- [ ] Fullce:review/autofix, resolvefindings, finalhead checks; newPRrelease notes and monitoring/rollback plan.
- [ ] RequiredGitHubCI/review green; PRnon-draft/merge-ready, without merging/releasing.

## Next focus after this PR

User steering on 2026-10-09: prioritize repeatable PC performance benchmarks and integration/merging of the fixes after this qualification is complete. Keep the current PR scoped to focused combined Native4K acceptance. PC benchmark results must identify the backend, preset/audio/seed, resolution and CPU/GPU timing scope; they do not establish real-TV headroom. This followup does not authorize merging or releasing the current PR before its review and CI gates.
