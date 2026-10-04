# Core corpus checkpoint

The full core corpus is not yet running. PR #23 remains a draft.

- Actual optimized core APKs: baseline `a59b4e5` / patches0001–0024; candidate `4270934` / patches0001–0027. Their identical private clock/RNG observer identity is `1abc75ec9591541bc3520b80d9d1a1bc91863ab5a6c1bbcf6c41bd09dc0c183f`.
- Published core AAR2.2.4 and its public JNI interface were independently inspected; see `published-aar-proof.json`. Instrumented measurement APKs are separate artifacts, not byte-identical release AARs.
- Device51.53: actual core pilot v4 rendered24 successful jobs. Seven of eight full/selected equivalence checks passed. Initial baseline Echasketch FULL1 is an outlier: FULL2 and both selected repeats agree; candidate FULL1/FULL2 and both selected repeats also agree. Do not approve the failed pilot or describe the outlier as a proven capture-mode effect.
- Source inspection found fresh colour attachment storage allocated with null pixels and no clear, while reused pooled storage is cleared. On first core load, the idle preset can have no output texture to copy. A deterministic initial-history probe is underway; attribution of the individual outlier is still unproven.
- The user approved the fastest backend, including an isolated Mac Android emulator. Owned emulator5580/PID92211 uses a new API34 AVD under `build/follow-ups/core-corpus/mac-emulator/`; existing user AVDs remain untouched.
- Seven emulator controls pass: all480-frame traces, requested preset names, native-library identity and sampled PNG/hash checks. Royal/Matrix/Echasketch selected repeats agree, and baseline Echasketch full-v-selected samples agree. Actual render times are about1.4–2.2s versus approximately11–27s for these selected TV controls. This is control-level evidence, not a full-corpus ETA or cross-driver pixel-equivalence claim.
- Source, harness and transport changes are committed and pushed on `followup/quad-lines`. The stopped direct-engine652-record dataset is separately protected on `evidence/quad-lines-corpus-2026-10-04`; it is supplementary, not core validation.

Authoritative live evidence: `build/follow-ups/core-corpus/measurements-core-v4/` for TV pilot and full-repeat diagnostics; `build/follow-ups/core-corpus/mac-emulator/speed-probe/` for emulator controls. The speed checkpoint archive includes169 checksum-verified members.

Next: finish the initial-history diagnosis, run the complete actual-core emulator pilot, preserve its input/APK identities and results remotely, then launch the full immutable9606-preset baseline/candidate screen. Capture comparison images for confirmed changes, address Codex review feedback on the final PR head, and package unresolved findings in Downloads. Never claim full coverage from the control pilot.
