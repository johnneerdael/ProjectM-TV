# I03 — defer finite small-input arithmetic recovery

**Disposition: keep I03 outside shipping patches.** The candidate executes the expected finite arithmetic and has Native4K images, but real runtime power recovery fails the requested no-performance-loss gate. I04 is being qualified independently.

Current evaluator suppression returns0 for tiny divisors/bases where original arithmetic can produce finite results. The candidate recovers finite division/power results inside that region while retaining zero/invalid/overflow protections. Its TreeFunctions.c-only finite-math compiler override also restores pre-existing NaN guards outside this region. That wider behavior is explicit and is not a generic nonfinite clamp or Windows/x87 parity claim.

## Verified source and Native evidence

The real full-engine evaluator passes198 combined host and ARM64 controls:89I03,76I04,20boundaries and13alias/side-effect cases. [Host proof](combined-host/controls.txt) and [ARM64 proof](combined-arm64/controls.txt) identify the scope; actual compiler commands place the override after fast-math for only TreeFunctions.c. The guarded raw proposal without that policy was rejected because NDK fast-math removed the guards.

Twelve Native480frame finite jobs pass per-frame GL/name/cleanup and finalREAD framebuffer0 checks, with six exact selected-RGB repeat groups. [Results/identities](native-combined/native-results.json) distinguish the instrumented core from shipping bytes. Fixed API34ARM64/GLES3/hostGPU, output3840×2160/Standard1280×720, common unsignedmonoPCM, seed12345/30FPS/mesh48×32 remain common.

| Finite derived I03 preset | Image |
|---|---|
| Current suppression | [Before](native-combined/native-captures/arithmetic-audit-math-I03-finite-fixture-before-0/frame-239.png) |
| Finite-recovery candidate | [Source-corrected candidate](native-combined/native-captures/arithmetic-audit-math-I03-finite-fixture-after-0/frame-239.png) |

The preset maps million-valued division/power into visible borders. It is a source-bound synthetic witness, not a confirmed affected stock preset or original Windows recording. No exact stock trigger is confirmed; dynamic small operands are not excluded by the narrow inventory.

## Runtime cost

[Verified36run results](runtime-cost-proof/verified-results.json) bind every request/source/preset/PCM/capture hash and preserve per-run manifests. All before/after selected RGB frames for these constant-geometry workloads are identical. RuntimeQ operands prevent compiler folding; each operation executes at the48×32 per-pixel grid. Three ABBA cycles are12runs per workload.

| Runtime workload | Beforems | Afterms | Delta | Cycle deltas |
|---|---:|---:|---:|---|
| Tiny division + bounded remainder |1.576356|1.481111|−6.04%|−11.70%,−.02%,−5.51%|
| Tiny-base negative power |1.468158|1.578336|+7.50%|+7.12%,+5.07%,+10.12%|
| Ordinary division/power/remainder |1.523019|1.648143|+8.22%|+17.61%,+.02%,+6.49%|

Power recovery costs+.110177ms in this emulator witness, with every cycle increasing. The ordinary combined workload also increases; it includes the broader compiler policy and is not attributed solely to I03. These are serialized source-engine timings including glFinish, not physical-TV FPS or universal bounds. No shipping performance claim is made from the lower division/remainder result.

Earlier literal-input timings are preserved in [compiled-constant checkpoint](compiled-constant-cost-checkpoint/README.md). The evaluator folds those operators at loadtime, so they are not evidence of repeated runtime callback cost. This correction is part of the evidence, not hidden.

## Owner followup

Review the exact bounded recovery and wider guard policy in [combined proposal](combined-proposal/COMBINED_INTEGRATION.md). Recovering arithmetic can additionally activate authored loop/draw workloads; resource limits and prior replay/nonfinite/rendering policies must remain. A future implementation must address or explicitly accept measured cost, requalify supported compiler domains and target Native4K feedback, then complete integration checks. The current source-corrected candidate is preserved for review and is not in the canonical27patch series. I04's outcome is not inferred from I03's power cost.
