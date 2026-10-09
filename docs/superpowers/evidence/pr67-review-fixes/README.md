# PR67 review fixes

Review comments were inspected live on2026-10-09. Both are valid predictor/tool
issues; neither is a new ProjectM-TV AAR defect. Author presets, native source,
adapters, devices and the other agent's corpus remain unchanged.

## P1 — source archive admission

[Review thread](https://github.com/johnneerdael/ProjectM-TV/pull/67#discussion_r4230278755).
`verify_target` checked only64-character lowercase SHA syntax. The controller
then froze that initially trusted value, so later consistency checks could not
establish canonical qualification. An all-zero digest passed with otherwise
valid publication/source identities.

The source31 CPU archive is now pinned separately from the full AAR and ARM
libraries. The exact value is
`997c082aabf9d0702c58da57efdd4c05e6faa99b9abd46ba1041d1fbb4b9cca8`.
It matches the migration fixture and a fresh SHA256 of
`build/preset-corpus/source31/native-build/projectm/src/libprojectM/libprojectM-4.a`.
The central gate applies to target probing, frozen-controller checks and worker
admission before source parsing. Historical source29 diagnostics retain their
separate scope.

Three regressions first failed to raise on the old implementation: direct
well-formed wrong hash, mocked target probe and frozen/worker admission. They
pass after the exact-equality fix. The fixture-consistency control distinguishes
the CPU archive from published Android byte identities. Independently rerun
publication/runner controls pass36 tests.

## P2 — visible shader lanes

[Review thread](https://github.com/johnneerdael/ProjectM-TV/pull/67#discussion_r4230278764).
The native reader declares `float3 ret` and emits `float4(ret.xyz,1)` in
`native_reader.cpp`. Walking an implicit float4-to-float3 cast as an entire
vector could attribute an unused fourth-lane sampler to RGB, then incorrectly
retain disconnected warp/drawing families.

Typed RGB-sink normalization now precedes mechanism traversal and contribution
gates. It preserves scalar broadcasting, vector truncation, consumed RGB,
cross-lane operations such as normalize, helper writes and loop/domain effect
uncertainty. The projection does not establish runtime termination or correctness
of unresolved domains.

The comment's literal `GetPixel(...).a` is invalid for that float3 helper, but
valid discarded-fourth-lane `GetPixel(...).r` and `tex2D(...).a` reproduce the
reported defect. Negative controls include constructors, implicit/explicit
casts, helper/loop returns and upstream disconnects. Paired positives include
RGB consumption, shared helper writes, scalar broadcasts and normalization
whose RGB denominator depends on all four lanes. Family/export controls pass
92 tests; the original69 family controls remain intact.

Final prepared suite: **2037 tests and92 subtests pass**. Strict MkDocs and
independent review pass. The fixing commit is recorded in the PR validation.
These checks are source diagnostics and
regressions, not new visual accuracy or whole-corpus appearance certification.
