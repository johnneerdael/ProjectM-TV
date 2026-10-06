# MilkDrop source analysis and predictive collections beta

This focused subset of the experimental analyzer from [PR #25](https://github.com/johnneerdael/ProjectM-TV/pull/25)
imports its inductive main-Q domain and shader selector proof. The separate beta
collection tools below add numerical activity scoring using a published AAR. The source analysis
is a diagnostic tool; parsing or lowering success does not certify appearance.

## Four initialization cases

`martin - ludicrous speed.milk` initializes `index4` with native `rand(12)` and
updates it through a bounded Boolean increment and signed remainder. The main-Q
proof includes initialization, frame resets and persistent custom locals, proving
post-frame q29 in 0..7. Float32 narrowing and signed-int conversion establish
`int(q29)%4` in 0..3. Equality branches use immutable expression identity;
missing cases, negative/nonfinite/overflow inputs, changed recurrences, shared
register effects and local shadows cannot borrow the proof. Runtime scalar/grid
guards retain its premise even when the result folds to a constant.

The other three presets are `Serge + martin - crystal palace tunnel003.milk`
(`mus`), `martin - mandelbox explorer - wreck diver nz+ liquititty.milk`
(`dist_c`) and `martin - organic light.milk` (`uv3`). The Microsoft legacy compiler
reflects these globals as external constants with NULL defaults. Previously they
became uninitialized ordinary GLSL globals. Patch 0040 preserves uninitialized
scalar/vector float globals as uniform inputs and uses the existing initialized
per-invocation copies when shaders write them. Mixed comma declarations preserve
individual storage classes. Locals, static/const declarations, initialized globals,
arrays and matrices retain their previous handling.

The versioned `projectmtv-implicit-extern-zero-v1` target policy models GLES link-time
zero initialization for unbound implicit inputs. An explicit binding supplied when
lowering or evaluating a scalar/grid field overrides that default, including different
values for different grid lanes. The policy is enabled only for declarations carrying the native
implicit-uniform marker, in a reader stamped for the new engine. `strict-v1` keeps
external inputs symbolic. It never initializes a local just because its name matches.

This focused tool retains source parsing, equation-domain proof, shader lowering,
and offline compatibility checks. It does not include the experimental pipeline
simulation from PR #25. No image or device result is inferred from source checks.

This policy defines current core behavior. It does not claim equivalence to old
D3D9 device-register history, nor does NULL legacy reflection prove a zero value.
Authored presets and assignment order are unchanged. Before/after visual differences
for previously undefined values cannot be interpreted as appearance regressions
without a specified input policy.

## Build and validate

Initialize recursive submodules. Apply the committed projectM patch series through
an Android build or the native test runner before building source adapters. Build
host regressions using the normal repository prerequisites:

```sh
bash core/src/test/native/run_native_tests.sh
```

The Preset Lab CI job reuses its prepared engine and archive, builds the two CPU-only
adapters (`milk-native-reader`, `milk-shader-translate`), and runs:

```sh
python -m pytest tools/milk-analyzer -q
```

For a retained host engine build, configure adapters explicitly:

```sh
cmake -S tools/milk-analyzer -B build/milk-analyzer/native \
  -DENGINE_SOURCE=/absolute/path/to/patched/projectm \
  -DENGINE_BUILD=/absolute/path/to/host/build \
  -DENGINE_IDENTITY_FILE=/absolute/path/to/build-identity.json \
  -DSANITIZERS=OFF
cmake --build build/milk-analyzer/native -j 4
```

Match `SANITIZERS` to the linked archive. The identity JSON records pinned commit,
patch digest and instrumentation scope. Native reader fixtures retain raw and
assembled equation trees separately and stamp the selected loading policy. Prepared
historical adapters cannot certify the new target policy. The broader original
PR #25 suite remains a supplemental compatibility check; it is not imported here.

The native tests exercise actual parser generation, default and nonzero input values,
copy reset across invocations, local/static/initialized controls and preset hashes
checked each time the tests run. Offline translator tests require `glslangValidator`.
Numerical source tests require NumPy and pytest from the existing
`tools/preset-lab/requirements.lock`. No app runtime dependency is added.

## References

- [D3D9 global shader inputs](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-writing-shaders-9)
- [D3D9 application-driven constant initialization](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-using-shaders-9)
- [GLSL ES 3.00 storage and initialization rules](https://registry.khronos.org/OpenGL/specs/es/3.0/GLSL_ES_Specification_3.00.pdf)


## Predictive collections beta

The current app uses All (default), Chill1–30, Normal25–75 and Intense70–100.
`beta_score.py` executes the standard published ProjectM-TV:core AAR through its
JNI interface on a task-owned Android emulator. `beta_export.py` verifies complete
source-bound results, preserves master memory weights and publishes the three
indexes. This is numerical activity-based prediction, not a claim of source-only
visual accuracy. The [Pages article](../../docs/user-guide/predictive-collections.md)
describes the formulas, relative ranking and limitations.

The initial run uses the pinned standard2.3.3AAR in
`profiles/published-core-v2.3.3.json`. Before a new run, verify the latest published
release and update the explicit pin if needed; never label another AAR flavour as
capped. Do not edit a live run's scorer, descriptor, model, input or runtime files.
A changed artifact creates a new run identity; old rows cannot be silently reused.

Install the dependencies from `tools/preset-lab/requirements.lock`. An ARM64 API34
emulator, adb, Android SDK34/build-tools34, NDK27.3.13750724 and JDK21 prepare the
runner. No user recordings or raw frames are committed.

Prepare a new runtime directory (for example `build/predictive-beta/runtime`):
extract `classes.jar` and `jni/arm64-v8a/libprojectmtv.so` from the exact standard
AAR. Compile the helper against that AAR's classes and Android34:

```sh
javac -source 8 -target 8 -cp ANDROID_SDK/platforms/android-34/android.jar:RUNTIME/classes.jar -d RUNTIME/java tools/milk-analyzer/CoreBackendRunner.java
ANDROID_SDK/build-tools/34.0.0/d8 --min-api 34 --lib ANDROID_SDK/platforms/android-34/android.jar --output RUNTIME RUNTIME/classes.jar RUNTIME/java/nl/neerdael/projectm/analysis/CoreBackendRunner.class
ANDROID_SDK/ndk/27.3.13750724/toolchains/llvm/prebuilt/darwin-x86_64/bin/aarch64-linux-android34-clang++ -shared -fPIC -O2 tools/milk-analyzer/core_backend_clock.cpp -o RUNTIME/libbackendclock.so
```

Replace `ANDROID_SDK` and `RUNTIME` with actual paths; use the NDK's `linux-x86_64`
prebuilt directory on Linux. Different compiler output has a different recorded
helper hash. The Java runner calls the published JNI API, selects one preset via
an asset-index overlay, and keeps the AAR's original preset and texture content.
The clock helper interposes only core-origin realtime/monotonic calls, calls
`srand(12345)`, and streams top-left RGB bytes with a bounded header. Native
`random_device` shader/noise/image choices remain production inputs.

Generate the fixed mono float32 reference using NumPy, then keep it immutable:

```python
import numpy as np
from pathlib import Path
sample=np.arange(420*1470,dtype=np.float64)
t=sample/44100
quiet=.04*np.sin(2*np.pi*220*t)+.02*np.sin(2*np.pi*440*t)
melody=.12*np.sin(2*np.pi*220*t)+.07*np.sin(2*np.pi*880*t)+.04*np.sin(2*np.pi*3200*t)
phase=(t*2.3)%1
kick=.5*np.exp(-phase*30)*np.sin(2*np.pi*55*t)
pcm=np.where(t<5,quiet,np.where(t<9,melody,melody+kick))
Path('build/predictive-beta/input.f32').write_bytes(pcm.astype('<f4').tobytes())
```

Launch a separate owned emulator. Record its actual PID, serial, AVD name and
launch command in `owner.json`; the scorer verifies the live process and AVD before
every preset. Its `pid`, `serial` and `avd` fields must refer to that owned instance.
Never use another task's device, running process or result folder. The initial run
owns emulator5592; this is a historical task identifier, not permission to reuse it.

```sh
python tools/milk-analyzer/beta_score.py --aar build/predictive-beta/core.aar --runtime build/predictive-beta/runtime --pcm build/predictive-beta/input.f32 --owner build/predictive-beta/owner.json --device emulator-5592 --remote /data/local/tmp/projectmtv-predictive-beta-20261005 --output build/predictive-beta/scores
```

Use `--limit 5` for a pilot. Reuse the same arguments to continue a matching run;
use `--retry-unscored --only-preset "EXACT PRESET.milk"` to repair a diagnosed case before continuing. The batch now stops at its first failed measurement and refuses to continue past unresolved failures. A 120-second timeout
is a failed measurement, not evidence that an effect is calm. Original315 language
coverage and this full numerical run are different checks; the other agent's saved
baseline stays read-only.

When every source-bound row is scored:

```sh
python tools/milk-analyzer/beta_export.py --run build/predictive-beta/scores --aar build/predictive-beta/core.aar --bundle core/src/main/assets/preset-genres
python tools/milk-analyzer/beta_export.py --check --bundle core/src/main/assets/preset-genres
python -m pytest tools/milk-analyzer -q
```

The final command needs the prepared source adapters described above. The new beta
unit tests do not launch devices. CI checks the committed bundle's source, weights,
model hashes, ranks, exact overlapping memberships and checksums. Parsing success,
compile success and these checks do not certify mood or appearance accuracy.


The diagnostic-only repair preserves the exact original scorer in
`profiles/scorers/beta-score-v1.py.txt`. Previously completed records retain their
original evidence identity. `evidence-contexts.json` declares the original and
repaired producers: all render/audio/model/runtime inputs must match, the archived
source hash is pinned, and the numerical program AST must remain unchanged outside
main's resume bookkeeping and measurement diagnostic cleanup. Changed numerical
code or inputs cannot reuse those records. The bundle retains each row's producer
identity and the exact source file for each context.

Diagnostic collection is best effort and its errors are separate from the primary
measurement. For example, no `.skip` file is normally created when the engine's
skip count is zero; failure to pull that optional file does not make a completed
native measurement unscored.


### Direct-delta calibration repair

The current `audience-model-direct-delta-v2.json` is a fresh nonnegative interval
fit on the actual 30-Hz direct brightness and 10-Hz native motion vectors, using the
unchanged original eight user judgments. The old `audience-model-v1.json` expected
motion-compensated brightness and is retained solely to validate historical
producer activity. Both original scorer versions are archived; retained measurement
files are not rewritten. The exporter recalculates activity with the new model,
stores original activity separately and pins a distinct `derived_scoring` identity.

Calibration inputs, original feedback, exact preset hashes and measurement
identities are in `profiles/direct-delta-calibration/`. Feedback was on core2.2.2
under mostly unspecified music/device conditions, with a tentative sample1 and
possible darkness defect. This transferred-label beta fit is not perceptual
certification: held-out base-model diagnostics match4/8strict bands and6/8within
five points. Final corpus ranks are a separate relative transform.

Reproduce the fit offline (not required for normal export/verification):

```sh
python -m pip install -r tools/milk-analyzer/requirements-calibration.txt
python tools/milk-analyzer/fit_activity_model.py
```

The timeout callback always kills its local streaming child in a `finally` block,
even if remote ADB cleanup fails. Its diagnostic errors are retained and the timer
is joined before the outcome is saved. Timeout still halts the batch.


Retries now select only existing unresolved records. Naming an unmeasured or
already scored preset with `--retry-unscored` is rejected; without `--only-preset`,
the retry invocation repairs only selected unresolved cases. Run the normal command
again after those failures are resolved to continue unmeasured cases. The required
metadata pull has a 15-second timeout and records an unscored outcome if it fails,
even after the renderer has exited. Ownership/remote setup and overlay transfers
are bounded separately; runtime artifact pushes have a 180-second limit.


## Full visual prediction loop (in progress)

The mathematical source forecaster predicts structure, motion, colour, flashing
and feedback before comparison with the published core AAR. Fresh comparisons
now target canonical Native core 2.3.8, whose downloaded AAR is byte-identical to
2.3.7; saved 2.3.4/2.3.5/2.3.7 rows keep their identities.
The current goal progresses through three-preset batches with all three at95+
behavioural-rubric grades, then ten-preset batches with all ten at95+, followed
by a randomized100-preset final audit. Complete each batch under an unchanged
model before repairing its gaps. Each run uses60frames at30fps. This supersedes
the earlier100-for-three gate and ten-case80/100 streak; none is a calibrated probability.
Unknown or contradicted claims earn no credit. Generation is outside this work.

Fresh Round006 passes the three-preset stage: MoltenWheel, demonizer and
glassworms flip each score95/100 with no critical mismatch. All60 claims and
source predictions were frozen before the first published-AAR capture, and the
model/inputs stayed unchanged through the batch. Motion and colour point
estimates receive partial credit; these are operational behaviour grades, not
pixel-perfect or calibrated accuracy percentages. The next gate is ten fresh
presets with all ten at95+, before the randomized100-preset audit. Evidence:
`fixtures/visual-loop-round006-2026-10-06.json`.

The first ten-case Round007 does not pass: six reach95, two source-domain
attempts remain unresolved, one black-output case lacks motion/history coverage,
and one retained-history prediction is materially too bright. Original records
are preserved. Repair these gaps and improve the declared60-frame stimulus before
another ten-case gate; the randomized100-case audit remains pending. Evidence:
`fixtures/visual-loop-round007-2026-10-06.json`.

Round 001 scored 97.5, 100 and 90. It did not meet the gate. Its frozen compact
fixture preserves predictions, identities, measurements and misses. Earlier
Tripgnosis trajectory errors were repaired by correcting custom-wave point counts
and PCM resampling; that diagnostic retest earns no fresh-batch credit.

Source CPU profiles distinguish the 41 patches matching core 2.3.4, the
42 patches matching core 2.3.5 and the 43 patches matching core 2.3.7.
Prepare adapters separately for each identity;
the existing `build/milk-analyzer/native` adapters retain their historical
41-patch identity. Source adapters are not the Android AAR. The driver previously
used equation seed 12345. Production projectM-eval initializes MT19937 per thread
with `0x4141f00d`; calling C `srand` does not seed that generator.

For a fresh evaluator thread, declare `equation_seed` as `0x4141f00d` and select
the matching `equation_rng_policy` in the forecast domain:

| Policy | Required patch-series SHA-256 |
|---|---|
| `projectmtv-core-2.3.4-cold-thread-v1` | `d21d4e3d9725178c000fd6f7ea5cd331389fb1100b70fce51341ece65d3fd818` |
| `projectmtv-core-2.3.5-cold-thread-v1` | `d73c955a26380a502516e6ba3a18baf753851244de4de2e5a3083930766a539a` |
| `projectmtv-core-2.3.7-cold-thread-v1` | `d70f5b5ec3f3c0b4da764cb824153f142b88e17e27c2e9e71d2b481c19998c7d` |

All three require upstream commit `e0b0a967f0ffd7d332106c366668ed271718472b`.
The forecaster rejects another seed or a mismatched release/patch identity;
changing a policy name does not migrate historical rows to another engine.
Other explicitly supplied seeds retain the `declared-seed-v1` policy. Provenance
records the seed and cold-thread assumption; this is not a preset-switch reset
policy and does not fix shader/noise/image randomness.

For these three verified patched source identities, an omitted
`main_binding_policy` now resolves to `projectmtv-core-2.2.6-v1`: unqualified
`sampler_main` occupies unit0, where the warp pass applies the preset wrap mode;
qualified aliases retain their own filtering/wrap settings. The historical sorted
order could instead put `sampler_fc_main` on unit0 and leave unqualified main
wrapping, despite `bTexWrap=0`. Unknown source identities retain the historical
default; an explicit historical policy remains available for labeled diagnostics.
Provenance records the effective binding policy without modifying the requested
domain or its hash. Diagnostic retests retain their original grades.

The verified43-patch source defaults to
`projectmtv-core-2.3.8-shape-state-v1`, modeling the published core's sampler-state
leak. The first unnamed main-textured shape inherits the bound linear sampler:
clamp after a delayed blur update, otherwise the warp's frame wrap. Each textured
draw clears sampler0 afterward; later unnamed instances use the framebuffer
texture's repeat/nearest settings. Named-image descriptors keep their own modes.
Actual blur requests come from active custom source, including sampler/texsize
references and native GetBlur substring checks, with comments removed. Draw
ordinals keep separate instances from sharing the wrong callback.

This is compatibility with an observed engine defect, not an intended universal
MilkDrop rule. Unknown source identities retain `legacy-repeat-linear-v1`; the
current policy rejects an unverified source identity. Provenance records the
effective policy and native required blur level. Update this contract after an
engine fix; do not apply the old leak to another AAR identity. The separate
Downloads handoff identifies `widest swing.milk` as runtime-confirmed and3,940
statically configured main-textured sources as investigation candidates, not
certified defects across the library.

A separately frozen 60-frame native control through the unchanged 2.3.4 AAR
matched all predicted RGB8 values exactly for three equation random draws per
frame. An independent NumPy MT19937 control also checks draw order across 33 shape
instances and 60 frames. These bounded controls do not certify all authored
visuals. Correcting only the seed reduced case 012 mean RGB error from 0.15987 to
0.10398 against its saved reference; contour timing still differs.

The 2.3.4 and 2.3.5 JNI hosts enable patch 0024 quad lines with a 1024x768
reference at the 256x144 test size. The older source drawing path used
canonical GL lines. Declare `line_rendering_profile` as
`projectmtv-gles-quad-lines-v1` for the patched GLES hard-edge wave/shape-outline
path: it models strip-end padding, miter joins and GLES pixel-border tie bias.
This profile accepts the three exact engine identities above and currently
requires a viewport no larger than the reference area;
high-resolution scaling, antialiasing and motion-vector quads are not certified.
The original `canonical-gl-lines-v1` remains available for historical contexts.

Core 2.3.5 adds authored feedback/native trail detail in patch 0042. JNI leaves
that layer inactive through height 1330; above it, Native trails also use a
1280x720 line reference. The source model does not implement that feedback path
or scaled lines. Every forecast with the 2.3.5 engine identity rejects viewports
above the 1024x768 reference area or height 1330, even with the canonical line
profile or a declared lab equation seed. Accepting the low-resolution identity
does not establish 4K support or appearance accuracy. The first 2.3.5 batch,
slots 019–021, scored 97.5/17.5/65 under the frozen behavioural rubric. The
original 2.3.4 slots 016–018 were withdrawn before captures.

With the exact 2.3.5 or 2.3.7 engine and the GLES quad profile, built-in dotted waves use
one centered 2-pixel point at or below the reference area. The earlier model
used four offset 1-pixel copies. The canonical profile retains those historical
copies; quad-dot requests with other engine identities or larger viewports are
rejected. Correcting only this draw path makes Hyperspace's second frame match
the saved native white frame exactly and reduces its 60-frame RGB8 mean error
from 2.951 to 0.416. This is diagnostic evidence, not fresh acceptance credit.

Separate PCM cadence from the equation `fps` input. In the declared cold JNI
test host, the engine starts with target FPS 35. The JNI tracker updates it after
the 30th rendered image at simulated time 1 second. Supply equation FPS 35 for
images 1–30 and 30 for images 31–60 while retaining the 30 Hz PCM arrays and
timestamps. A separately frozen `q1=fps/256` control through the unchanged AAR
matches the expected red bytes 35 then 30 on every pixel. This timeline describes
that exact host lifecycle, not arbitrary app startup or device frame rates.
Correcting only this input in the unchanged frozen model restores `187`'s red
fan; its 60-frame RGB8 mean error falls from 1.130 to 0.0083, with maximum 2.
See `fixtures/visual-loop-dot-fps-repair-2026-10-06.json`. Point snapping and
motion-vector quad rasterization remain separate gaps.

Declare `point_subpixel_bits` separately when a renderer context establishes
point-centre snapping. The Apple M4 Pro API34 emulator controls uniquely match
nearest 1/256-pixel snapping (`8`), despite reporting `GL_SUBPIXEL_BITS=4`.
Five candidate grids were frozen before the finer native capture; only the
8-bit prediction matched all pixels. The setting propagates to custom and
built-in wave point coverage; omitting it retains unsnapped canonical coverage.
Integers 0–16 are accepted. `np.rint` halfway ties remain a declared mathematical
policy, with native exact-halfway cases unverified. Do not assume the same grid
on other GPUs. The case019 diagnostic mean RGB8 error improves from 1.023 to
0.748; remaining fine feedback differences are preserved. See
`fixtures/visual-loop-point-grid-repair-2026-10-06.json`.

Core 2.3.7 adds patch0043 to preserve authored geometry in Native trails. The
separate 43-patch archive and adapters retain their actual identities; unchanged
standalone image/random/composite adapters are reused only after source/header
byte-equality checks. Newly captured 2.3.7 FPS and hue controls complete 60 frames
with Standard trails inactive at144p: FPS matches exactly; hue differs by at most
one RGB8 level. The hue control retains its original source-math identity and
does not substitute for a full 43-adapter forecast. Larger viewports/detail paths
remain rejected; Native4K's authored-preservation purpose does not establish our
predictor's 4K accuracy. See `fixtures/visual-loop-release237-migration-2026-10-06.json`.

The CI-only 2.3.8 release changes no engine, JNI or patch source and publishes
the same complete AAR bytes. Its reference uses the existing verified 43-patch
engine policy, source backend and runtime namespace, with the new release label
recorded for fresh rows. Do not relabel earlier controls. The download and source
equivalence are in `fixtures/visual-loop-release238-equivalence-2026-10-06.json`.

Framebuffer conversion preserves the represented float32 shader value when
scaling to UNORM8. A float32 intermediate product can incorrectly round a value
just above a half-byte boundary back onto the boundary. Scaling in float64
avoids that extra rounding, then returns normalized float32 storage. An
independently frozen 60-frame AAR control matches all pixels under this rule;
the previous rule misses one channel in 30 frames. Native exact-halfway tie
handling and other dithering states remain unverified. This correction does not
by itself certify feedback-sensitive presets. See
`fixtures/visual-loop-unorm-conversion-repair-2026-10-06.json`.

Drawn geometry accepts a separate `triangle_subpixel_bits` input (integer4–16;
omission preserves canonical coverage). Snapped vertices remain in window-pixel
space for triangle coverage and interpolation; colors and UV attributes are not
snapped. This propagates through shapes, borders, center darkening and quad waves.
The declared Apple emulator's8-bit input makes case023's first pass-through
feedback frame match every native pixel. Later feedback still diverges; this is
not complete preset certification or a universalGPU rule. See
`fixtures/visual-loop-triangle-grid-repair-2026-10-06.json`.

A frozen curved-line native control agrees within one RGB8 level over 60 frames.
The full case 012 diagnostic now matches coherent flash counts (one brightening,
zero darkening) and predicts peak brightness jump 0.8194 versus native 0.8207.
Later feedback details still differ; this is not fresh-batch credit or general
pixel equivalence. The exact native preset repeats identically across the two
recorded loads, ruling out reference variability in that bounded comparison.

Wave forecasts now retain projected native clip coordinates through quad-line
expansion. Early rounding near normalized screen 0.5 could change tiny-segment
lengths and coverage; the shader expands those coordinates before viewport
translation. On the case013 diagnostic, mean luma improves from 0.1188 to 0.1406
(native 0.1414), and tracked motion from 0.1305 to 0.1755 (native 0.1764). An
isolated waveform's pixel positions differing by more than one RGB8 level drop
from70to14across60frames. The original batch grade is preserved; these controls
do not establish driver-wide pixel identity or earn fresh-case credit.

CPU wave/composite adapters now include the actual pinned `RenderContext.hpp`
instead of duplicating its structure. Its time field is float32; an earlier stub
used double and the long-clock tests mistakenly validated that stub. Hue math now
preserves native float intermediates. Adapter output records the header hash and
time width, and forecasts require the prepared float32 adapter. Focused controls
pass66tests plus19subtests; this is not a full imported-suite result. The corrected
type does not resolve randomized hue choices on its own.

For source/reference math comparisons, the user selected matching declared
random inputs. The opt-in Android test-host in `core_random_inputs.cpp` supplies
a uint32 entropy seed and a separate MT19937 lower-31-bit stream per core thread.
Only callers from `PROJECTMTV_TEST_CORE_PATH` are affected; production core is
unchanged. Enable it with `PROJECTMTV_TEST_RANDOM_SEED` and an owned
`PROJECTMTV_TEST_RANDOM_LOG`. Without the seed variable, supplied inputs are off.
The source shader-random bridge accepts `declared-mt19937-u31-v1`; its default
still uses host C rand. A supplied stream is a test input, not a claim about
production libc randomness or scheduling. The background worker's reseeding
cannot disturb this test profile's renderer stream.

The composite CPU bridge can generate hue offsets from `entropy_seed` using the
copied native initializer, or accept explicit `hue_offsets`; provide one. Seeded
hue and high-quality noise controls agree with the unchanged AAR within one RGB8
level over60frames. Noise seeds use the native system-clock microsecond count's
low32bits at the first draw, when resize recreates the textures. Both earlier
wrong seed attempts are retained. The matching-input case015 diagnostic has mean
RGB8 error0.563; it does not replace its failed original prediction or count as a
fresh perfect match.82focused tests plus19subtests pass under prepared adapters.
Random external image selection still requires a matching asset/binding context.

The current plan is `docs/plans/2026-10-05-predictor-visual-loop.md`. Raw artifacts
remain in ignored `build/visual-loop/`. The broader imported suite needs prepared
historical adapter profiles and is not reported passing. No whole-corpus accuracy
claim or change to the shipped beta collections follows from this research.
