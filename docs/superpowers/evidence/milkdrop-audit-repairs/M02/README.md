# M02 — original border fan coverage restored

Patch0028 changes only the eight triangle indices to preserve MilkDrop2's four strip fans for inverted outer/inner radii. Vertices, float colour/alpha, blending, outer-before-inner order and one indexed call per visible border stay unchanged. Widths remain authored and unclamped. The existing float-precision policy is intentionally retained; this is not Windows/D3D pixel equivalence.

The baseline actual-GL control fails4/46 profiles; the candidate passes all46, including independent original CPU float-rotation fans at8/32 targets. The integrated normal and ASan/UBSan suites pass51/51 each. All28 patches apply. Final full Android/JVM/host/review/CI integration remains separate.

Twenty-four actual Native3840×2160 runs (Standard1280×720 canvas) verify12 repeat groups and192 selected PNGs. Ordinary, half-size, opaque and invisible fixtures are selected-RGB identical. Inverted translucent outer and inner borders change; outer frame239 changes2,082,654 pixels, RGB MAE14.156. The handoff's abstract overlap direction is not the observed GPU corner direction: bounded CGL current00=128 versus fan223, while final Native frame239 current199 versus corrected175. Preserve these contexts rather than reusing the handoff's modeled pixel as a capture claim.

[Before outer border](native/native-captures/border-topology-audit-border-inverted-before-0/frame-239.png) · [Corrected fan](native/native-captures/border-topology-audit-border-inverted-after-0/frame-239.png). These are explicitly finite diagnostics, not unchanged stock presets. Stock affected count remains unconfirmed; supplied lexical candidates are0.

Twelve isolated ABBA runs verify all manifests/selected RGBs and exact installed APK per row. Mean1.679363→1.680356ms (+0.000994ms/+0.059%). Cycles+1.369%,+4.781%,-5.574% show no consistent slowdown. This bounded emulator result is not a universal physical-TV performance claim. No additional calls, triangles or buffers are introduced.

The separately identified predictor already describes the original fan model. Its worktree is untouched. [Versioned contract](predictor-contract.json) binds the repaired target topology, retained colour policy and exact inspected predictor source; it does not certify its other primitives.

[Native proof](native/native-results.json) · [Costs](border-topology-cost-results.json) · [Baseline RED](border-topology-root-red.txt) · [Normal](border-topology-integrated-normal.txt) · [Sanitizers](border-topology-sanitizer-controls.txt).
