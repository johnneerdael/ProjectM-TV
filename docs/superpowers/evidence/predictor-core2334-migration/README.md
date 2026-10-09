# Published v2.3.34 migration preparation

Status on 2026-10-10: complete published artifact and matching source adapters
prepared; unchanged-AAR runtime qualification remains pending.

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
The matching reader, equation/audio, waveform, noise, image, random, composite
and shader translation adapters are built. Their digests are recorded in
`adapter-identities.json`; cold timing and RNG receive separate34 policy names.
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

## Source admission and runtime boundary

`matches` retains exact identity comparison. A separate one-way `math_matches`
lineage admits only known source34 as a source31 math successor. It does not
rename the source34 reports, turn changed AAR bytes into equivalent bytes, or
transfer native GPU/binding evidence. The static exporter supports an explicit
source34 reader and derives run identity from that actual parser. Default static
and numerical corpus targets remain source31/published33 until runtime controls
pass. `profiles/candidate-core-v2.3.34.json` explicitly marks that gate false.

Eighteen focused test-first controls pass. They check strict/source-math identity
separation, RNG/cold timing, six waveform modes, six complete noise banks,
random-contract parser/translator identity, static export and three integrated
source forecasts (legacy warp, shape, dots/quad lines). The source31/34 forecast
display arrays match for those small16x8 controls; they are independent CPU
model comparisons, not unchanged-AAR runtime results. Independent review passes
all18 controls and reports no remaining source-admission finding.

The final prepared analyzer suite passes2,402 tests and92subtests in139.70s.
Strict MkDocs and whitespace checks pass. These are source/adapter regression
checkpoints and do not clear the unchanged-AAR runtime gate.

The same fixed100 originals all produce source34 exports. Their structured
visual descriptors match the preceding source31 checkpoint in all100 cases;
actual reader/engine/archive identities remain distinct. `static-census.json`
records the source joins and hashes. This establishes extraction consistency
for that sample, not GPU/native behaviour or mood accuracy.

Three new predictions (gamma-only, negative echo and named constants) are
frozen under `build/preset-corpus/runtime34/`: each30frames at128x72, with
explicit silence, clock, entropy and raster settings. Predicted outputs and
model hashes precede any native capture. No capture has occurred, so these
controls remain pending rather than passing by comparison to old AAR output.

The v2.3.34 Java classes were compiled with the declared helper and D8 inputs.
An independent D8 reconstruction matches the deployed-candidate DEX digest;
`java-reproduction-verification.json` binds it to the full unchanged AAR.

The new task-owned API34 emulator, `projectmtv-predictor-core234` on port5688,
exited132/SIGILL during host startup. Its crash identifies `init_cache_info`
before guest startup or AAR loading; `host-bootstrap-failure.json` preserves
the result. This is not evidence of an AAR defect. The unchanged launch was not
retried, and shared devices were not operated. Upstream
[QEMU cache detection](https://raw.githubusercontent.com/qemu/qemu/master/util/cacheflush.c)
uses a separate Darwin path because Apple does not expose CTR_EL0; that context
does not by itself prove the exact SDK build defect or authorize binary changes.

## Confirmed bootstrap failure path

Bounded disassembly of the installed ARM64 executable now identifies the
failure path. `_init_cache_info` first makes its cache-size query; a failed query
or zero size branches to address0x100465be0, instruction0xd53b0029:
`mrs x9, CTR_EL0`. That is the exact instruction recorded in the crash.
A read-only `sysctlbyname("hw.cachelinesize")` check in this execution
environment returns-1/errno1(EPERM). Thus the denied host query selects the
unsupported fallback before Android or the AAR runs.

`cache-query.json`, `init-cache-info.asm.txt` and
`emulator-binary-identity.json` bind that evidence. The SDK, host permissions,
running shared emulator and devices remain unchanged. No replacement emulator
binary was found in the bounded local artifact search. Finish the prepared
controls in an execution environment where the host query succeeds or with a
vendor emulator that handles its failure safely; do not repeat the same launch.
This is a host/tooling restriction and fallback defect, not a ProjectM-TV AAR
bug report. Source-only work can continue while that runtime gate is pending.
