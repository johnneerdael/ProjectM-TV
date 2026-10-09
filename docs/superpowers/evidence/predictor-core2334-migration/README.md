# Published v2.3.34 migration preparation

Status on 2026-10-10: pending full artifact acquisition and qualification.

Live GitHub release metadata identifies [v2.3.34](https://github.com/johnneerdael/ProjectM-TV/releases/tag/v2.3.34),
commit `984bfe19e408bed374647e4bdea8c053f0922a15`, with the complete
`projectM-TV-core-2.3.34.aar` asset of 41,888,344 bytes and expected SHA256
`a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3`.
Its digest differs from the qualified v2.3.33 artifact. Release metadata and a
remote Actions artifact reference do not prove locally acquired AAR bytes.

The release adds `0035-program-cache-switch.patch`. Its four source changes
apply to isolated copies of the prepared source31 files, leaving the pinned
source31 tree unchanged. This partial source check is not a complete engine
build, AAR runtime control or appearance comparison. The new switch defaults
to enabled; correctness of the published binary still requires its own evidence.

Host downloads currently fail DNS resolution. The in-app browser fails during
local plugin initialization; Chrome reached the asset redirect but the download
operation timed out and no local artifact was found. Further native Chrome
access was denied. Network or permission settings were not modified.

Local preparation evidence is under `build/preset-corpus/published34/`:
`release-discovery.json`, `acquisition-status.json`, the exact patch,
`source-patch-check.json`, and the four-file `patch-check-source/` copy.
Continue using the qualified v2.3.33 publication and source31 adapters until
the complete new AAR is acquired, hashed and separately qualified. No old
runtime qualification is transferred on a source-only or metadata assertion.
