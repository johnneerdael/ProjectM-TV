# Published v2.3.34 migration preparation

Status on 2026-10-10: complete published artifact acquired; matching source
adapters and runtime qualification remain pending.

Live GitHub release metadata identifies [v2.3.34](https://github.com/johnneerdael/ProjectM-TV/releases/tag/v2.3.34),
commit `984bfe19e408bed374647e4bdea8c053f0922a15`, with the complete
`projectM-TV-core-2.3.34.aar` asset of 41,888,344 bytes and expected SHA256
`a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3`.
Its digest differs from the qualified v2.3.33 artifact. Release metadata and a
remote Actions artifact reference do not prove locally acquired AAR bytes.

The full cached AAR was subsequently found in the local Gradle modules cache.
It has the exact published size and SHA256 above. A copied worktree artifact
passes ZIP CRC; both ABI libraries and classes are independently hashed. All
9,606 presets and 74 textures, and every other asset byte, match published33.
The ARM64 library SHA256 is
`b04caf83c2d4b89015a727899225ecba970a9b732afc7997760e584dcc367013`;
ARMv7 is `e0a6bb6927f8f44a93ab82665b7bf99faf0e801f3b4b38f3c2148946ffcb3596`,
and classes.jar is
`a4e3f33e655a784551d064b4a16ce9c43ced202bc24103892b1fc861c3d2ff92`.

The release adds `0035-program-cache-switch.patch`. Its four source changes
apply to isolated copies of the prepared source31 files, leaving the pinned
source31 tree unchanged. A complete prepared source34 snapshot now compares
985 source files: only those four change. Its host CPU archive build passes,
with patch identity
`a6e0298331988d9777607f2cb75ade4bb362f69787e865aaaf6578479267d0df`.
This is not AAR runtime or appearance qualification. The new switch defaults
to enabled; correctness of the published binary still requires its own evidence.

Initial host downloads failed DNS resolution. The in-app browser failed during
local plugin initialization; Chrome reached the asset redirect but the download
operation timed out and no local artifact was found. Further native Chrome
access was denied. Network or permission settings were not modified.

Local preparation evidence is under `build/preset-corpus/published34/`:
`release-discovery.json`, `acquisition-status.json`, the exact patch,
`source-patch-check.json`, `artifact-identity.json`, and the complete AAR.
Source34 preparation is under `build/preset-corpus/source34/`, including
`source-delta.json`, its production snapshot and host CPU build.
Continue using the qualified v2.3.33 publication and source31 adapters until
the new AAR and adapters are separately qualified. No old
runtime qualification is transferred on a source-only or metadata assertion.
