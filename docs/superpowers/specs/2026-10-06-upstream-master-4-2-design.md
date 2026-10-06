# Rebase ProjectM TV Engine onto upstream master (4.2 development)

## Requested outcome

Replace the upstream 4.1.7 base with current upstream master, preserve the maintained TV engine features, remove patches made obsolete upstream, and adapt remaining patches to the refactored renderer. Validate the Android APK and core AAR integration before review, merge, publication and Milkbeat update. This is an upstream development snapshot, not a claim that upstream released 4.2.

## Baseline and scope

- ProjectM TV main: `b1bb994dbfaa04159630570cd9b2c255b173a6bd`; 44 patches over `e0b0a967f0ffd7d332106c366668ed271718472b` (4.1.7).
- Upstream master observed 2026-10-06: `6f64807467e312034883a4389e6aa80a675458bc`; CMake version 4.2.0, evaluator gitlink `22fb0cfd8f2dfbcd2b68f2443e7f44e19b32c09a`. Pin the immutable commit.
- Preserve API 21, GLES 3.0, arm64-v8a/armeabi-v7a, the Java/JNI boundary, Auto quality, Standard Native trails, prewarming, transitions, texture callbacks, quad lines and preset compatibility.
- Keep engine changes in patch files; change the submodule gitlink only to the upstream commit, never commit modified sources inside the submodule. No routine release-version bump.

## Approach

Reconstruct the existing patch chain in an ignored scratch clone to preserve exact old behavior and patch provenance. Port renderer, HLSL translator and evaluator changes independently against upstream, then integrate an ordered patch series and test it from a fresh recursive checkout. Consolidating interdependent historical follow-ups is permissible when the migration report maps every old patch to its retained or upstream replacement behavior. Preserve attribution. Use upstream mesh, vertex-buffer and loader abstractions where suitable.

## Upstream unfinished work

Evaluate the public 4.2 board and current issues, including GL/GLES selection (#1004), texture loading/ownership (#970 and #974), variable monitoring (#664/#971), and vendored-symbol collisions (#1038). The maintainer warns the board is stale. Android does not need variable-monitoring UI or vcpkg packaging to rebase; loader compatibility, callback texture ownership and native symbol isolation must be established from code/build/runtime evidence. Do not adopt unfinished APIs solely because they appear on the board.

The cited vcpkg comment explains that stb_image implementation macros produce out-of-line symbols in a single translation unit: calling it header-only does not remove link incompatibilities. Inspect the linked JNI binary, not just shared-library visibility flags.

## Verification and completion

Keep existing functional controls for shader translation, numerical render output, custom-waveform bounds, random texture identity, Native feedback/geometry and JNI ownership. Add focused regression coverage for migration-specific loader/resource changes. Run patch application, host and sanitizer native suites, JVM tests, both Android ABIs, release APK/AAR and strict MkDocs checks. Compare before/after rendering and lifecycle on an available awake TV without waking it remotely. Verify Milkbeat compatibility. Obtain completed Codex review for the final PR head, required CI, merge into main, and verify the automated publication/update results. Record unavailable prerequisites honestly and keep the task open when a required gate is unproven.

## User clarification: full library and released baseline

The authoritative baseline is the latest released ProjectM TV core AAR, not stock libprojectM and not an instrumented rebuild. Verified on 2026-10-06: v2.3.11, source `b1bb994dbfaa04159630570cd9b2c255b173a6bd`, AAR SHA256 `3bc37560a87000ec7ac446895fee8ad09e93b5c83a601014b5fc396bd1f3e6d6`, checked against GitHub asset digest and release checksums. Freeze this artifact; record any later baseline change explicitly.

Evaluate all 44 historical patches and their affected or potentially affected presets across the full 9,606-preset inventory. Static candidates are not visual certification; resource/lifecycle changes can affect the whole inventory. Exact fidelity is required for all presets. The previous four-witness/32-job instrumented ProjectM TV source comparison is supplementary and does not establish unchanged released-AAR fidelity or whole-corpus coverage.

Build private workers embedding unchanged released baseline and candidate AAR bytes and verify packaged library/asset identity. The released JNI lacks deterministic seed/initial-clock controls. Keep unchanged-AAR runtime evidence separate from source-instrumented deterministic diagnostics; the user measurement-criterion clarification is pending. Do not silently relax exact fidelity, label untested presets verified, or proceed to readiness/merge before the expanded gate is satisfied.
