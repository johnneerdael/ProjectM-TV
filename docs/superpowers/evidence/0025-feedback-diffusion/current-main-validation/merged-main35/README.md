# Current-main35 / MRT candidate36 validation

Baseline: `f435dd7c58ea1f16d9d182ecfc5632b77f5b6f98`, including merged PR26 translator fixes0030–0032 and PR27 equation-loading fixes0033–0035. Candidate: PR28 commit `1b2c266331c9624ef7027da86d825096d243e86a`, the same prerequisites plus0036 raw/filtered MRT diffusion. This is a new measurement epoch. Earlier main29-era pixels do not substitute for its baseline.

Fresh actual-core Android APK and release AAR builds succeeded. Each pair contains exactly the same `libprojectmtv.so`; frozen worker dictionaries and `current-pair-aar-proof.json` preserve source, patch, instrumentation and binary identities. Runtime pilot results are pending. Both roles have identical production core-source dictionaries, observer/harness, packaged assets and first35 patches.

An earlier private composition check found that PR28d617’s unchanged0036 failed against main35 at the `MilkdropPreset.hpp` member-context hunk. The owner resolved that integration at1b2 by regenerating against the full prerequisite series. `pr28-on-current-main-apply-check.json` preserves the failed epoch and its resolution; do not treat it as a failure of the current1b2 source.

Adapters are archived here for reproducibility but compute repository root from their original depth. Restore to `build/native-4k-current-main/merged-core-validation/build.py` or `build/native-4k-current-main/current-main-mrt-candidate/build.py` before execution; existing destinations are immutable and reruns need a new epoch. The original composition adapter intentionally still pins the historical d617 failure.
