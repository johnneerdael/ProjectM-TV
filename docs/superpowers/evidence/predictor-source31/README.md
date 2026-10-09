# Published 2.3.31 migration controls

Source migration commit: `54f39b27`. Published release commit:
`8a15996e8510533113a44e26feaddc3a7d6e85f5`. The profile in
`tools/milk-analyzer/profiles/published-core-v2.3.31.json` binds the complete
published AAR, both native libraries, classes, asset inventory and 34-patch source.

The frozen prepared source suite passed **1,834 tests and 92 subtests**.
The independent review's authored motion history correction then passed
35 focused source/detail controls. These establish scoped source policies.
They do not count as visual accuracy scores.

Three predictions were frozen before any successful native control capture.
The native host used the unchanged full published AAR as an AssetManager archive,
its extracted unchanged ARM64 library, and a DEX independently reproduced from
that AAR's classes.jar plus the declared public-JNI helper. Each control overlays
only a synthetic preset and one-entry selection index. No bundled authored
preset was edited. PCM is zero float32 through the public unsigned-byte JNI
ingress, with declared clock and random inputs. Every run renders 30 updates at
30Hz, 128×72, 48×32 mesh, Standard trails, Classic transition and no auto changes.

| Control | Maximum RGB8 difference across all 30 frames | Result |
|---|---:|---|
| Gamma-only composite | 0 | Pass |
| Negative odd echo orientation | 1 | Pass at declared tolerance ≤1 |
| Named-constant conditional | 0 | Pass |

The device was task-owned `emulator-5670`, AVD
`projectmtv-source31-controls`, API34 ARM64. The observed renderer is Android
Emulator OpenGL ES Translator (Apple M4 Pro), GLES3.0. The captured metadata
establishes 30 completed native frames, exactly one indexed preset and zero
skips. Both fingerprint and executable/asset hashes are in the report. The
emulator was stopped after the bounded controls; no shared TV or corpus device
was operated.

`qualification-report.json` contains the complete identity and result rows.
Per-case directories retain synthetic source, frozen prediction/provenance,
predicted/native RGB arrays, and observed metadata. Predictions use the model
snapshotted under local `build/preset-corpus/runtime31/frozen-model/`; the model
inventory includes an unused in-progress static detector, which is not called
by these forecasts and receives no validation credit here.

The first harness launch used the older unsized-stream clock adapter with the
sized Java helper. It produced no accepted frame stream. Its attribution is
preserved in `harness-error-first.json`. The corrected clock adapter exports
the required sized JNI method and has SHA256
`d34bf522deb53c8fcb28f4e1a3e5b0404521c6e38f8eb283f024eff3381cf355`.
A later filename assertion omitted `.milk`; the successful gamma capture was
preserved and its recorded name checked correctly rather than recaptured.
Neither harness issue is evidence of a native library defect.

The gamma fixture checks numerical agreement for normalized storage; it is not
an independent discriminator for every pass-count epsilon boundary. Focused
source controls separately distinguish the .001 versus .0001 pass contracts.
These three controls do not certify all18 fixes on Android, the packed motion
capability route, arbitrary random-image selection, high-resolution behavior,
real music, whole authored-preset appearance, or effect-family classification.

No full-corpus rendering was started. Earlier corpus artifacts keep their
original source29 identity. Static family inference and its benchmarks remain a
separate milestone.
