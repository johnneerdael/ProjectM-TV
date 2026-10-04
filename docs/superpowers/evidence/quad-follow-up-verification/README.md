# Quad-lines follow-up verification

Current baseline: `a59b4e5` (PR #14 and PR #20 merged). Worktree: `.worktrees/quad-lines-follow-ups`,
branch `followup/quad-lines`. Device testing used the approved address `192.168.51.53`.
Code and per-fix evidence were committed and pushed in `9dd8875`; `c40d987` adds the first corpus
data checkpoint. The full corpus scan remains in progress; see [shared baseline](CORPUS-BASELINE.md).

The direct patched-projectM corpus scan was stopped after the user required `projectm-tv:core`
as its backend. Its 652 completed records are remotely backed up as supplementary evidence only;
they do not validate the core wrapper's loading, audio, direct-output or presentation paths.
A new core-backed protocol must establish its own baseline and repeats.

## Visual acceptance criterion

The user clarified that 10% is a rough diagnostic guide, not a hard gate. Judge fidelity against
the authored reference by visible structure, movement, colour, contrast and detail. A small numerical
increase does not establish degradation, and a low global image error does not establish improvement.
Use matched frames and motion examples; retain size-band controls and deterministic input so a visible
difference can be attributed to the change. Large changes in the overall look or lost motion remain open.

The corrected sampler sweep completed396 jobs with every repeat exact. Thirty of33 presets remain
byte-identical at all tested sizes. ADAMFX2, Matrix and MoodRings change due to the sampler correction;
nine actual matched before/after images are in `proofs/sampler-presets/`, with source/build hashes.
Their numerical scaling errors support the assessment; visual acceptance is reviewed separately.

Patch0027 restores the existing messages owned by preset-loading, expression-compilation and
factory exceptions. Six inherited-interface/public failure-event tests fail before the correction
and pass after it; the complete host suite passes169 tests with zero skips. This is a diagnostic
fix, not a change to preset compatibility or rendering. [Per-fix proof](proofs/preset-diagnostics/07-preset-diagnostics.png)
and raw logs are retained in `proofs/preset-diagnostics/`.

## Corrected custom-wave measurements

The attached task list predates the correction in `shifter-qload-acid-mandala-4k/README.md`.
The +21% thin-wave energy and 16–29% thick-wave lit-area claims were produced by rounding blurred
composite output per pixel. They do not establish renderer faults.

The new run uses a point-sampling composite shader with **actual render dimensions embedded as constants**,
so virtual `texsize` cannot resample the measurement on a reference-size grid. Energy uses raw linear sums.
Hit histograms are decoded only after checking that the canvas values are quantized pass counts.

`results-geometry.json`: 392 jobs, 14 synthetic presets, two identical renders per case, 30 fps,
4 seconds warm-up plus 4 seconds measurement, `bass-0.30`. Against classic 1 px GL lines at 1182×665:

- thin/thick custom waves at 1080/2160: maximum energy deviation **0.47%**, lit-share deviation **0.44%**;
- hit-histogram maximum absolute bin difference: **0.00358**;
- alpha-blended thick custom waves: energy and lit share within **0.35%**;
- 56 classic comparisons across the authored size and 360/480/540: `legacy_changed: []`.

An initial old-worker comparison differed for thick custom-wave dots because the old lab worker did not
enable `GL_PROGRAM_POINT_SIZE`. The current worker does, matching GLES. Rebuilding the old engine with
the same caller GL state removes those differences. The original mismatched-state results remain in
`build/follow-ups/verification/geometry/raw-original-tooling.json`; do not mistake them for an engine regression.

## Heights below 540

`results-low-real.json`: 154 jobs, seven real presets, two identical renders per case. All 28 classic
comparisons against the pre-quad engine are byte-identical. `results-low-nosmooth.json` adds 42 jobs on
three presets with desktop-only line smoothing disabled, controlling for the GLES difference.

These runs keep two comparisons separate: fidelity against authored 1182×665, and quad/classic parity at
the same physical render size. The one-pixel minimum below the reference naturally increases line share
relative to the authored picture; same-size parity alone cannot establish fidelity.

`I Like Cartoon` has large same-size image differences despite small luma differences. Disabling desktop
smoothing does not eliminate them. Removing only its main wave makes quad/classic output byte-identical
at 360, 480, 540 and 665, locating the discrepancy in waveform injection into nonlinear feedback.

Authored-size ±1.4% controls differ from the reference by **0.083–0.121 img_err**; 360-size ±1.4% controls
differ by **0.105–0.172**. The unmodified copied preset hashes match the original, so the ablation-copy
mechanism introduces no change. The earlier `0.0044` field in the priority evidence is the **range of
reference-error scores across capped 1260/1330/1440 renders**, not pairwise authored-size noise. Both
statistics are useful, but they are different quantities.

A blanket classic-at-unit-scale candidate was evaluated and rejected: it improves 10/21 authored comparisons
and worsens 11/21, including Cartoon by 0.021–0.058. `unit-classic-candidate.json` records that result.
The candidate remains scratch-only. It must not be presented as a successful fidelity fix just because
it would pass a same-size byte-parity test.

## Confirmed shader failure bugs

Production candidate: `tools/projectm-patches/0025-shader-failure-handling.patch`.

- `ShaderException` previously inherited the generic `std::exception::what()`, losing the driver diagnostic
  in standard handlers. The new test fails before the override and passes after it.
- A successful vertex shader leaked when fragment compilation subsequently threw. The failed shader
  itself was already deleted correctly. Real CGL allocation tests observed one leaked shader per failure,
  accumulating to 16; the cleanup now deletes it and rethrows the original error.
- The full host suite passes **157/157**, including vertex/fragment/link rejection, repeated attempts,
  and successful retry in the same context. All 25 patches apply to the pinned clean source.

Diffusion research candidate: `feedback-shader-fallback.patch`, applied only in scratch diagnostic series.
The PoC constructor rejected an entire preset when its optional shader failed, even with diffusion disabled.
It now catches that rejection and keeps the original feedback path. `results-shader-fallback.json` records
80 renders: ten rejected-shader/baseline comparisons and ten successful-diffusion before/after comparisons,
all repeated identically, at classic, 540, exact-reference 1024×768, 1080 and 2160. This fallback candidate
requires the shared compiler cleanup before production use.

The whole-native-suite run exposed a separate timing-sensitive CPU-bound-transition test. Its wall-clock
busy spin did not guarantee the CPU share required by the policy when the host thread was descheduled.
The test now feeds explicit wall/CPU samples to the actual transition policy, checking both CPU-bound and
low-CPU behavior. Raising the production CPU threshold from 80% to 99% in a scratch negative control
fails the CPU-bound assertion. The complete fake-engine and real-projectM ASan/UBSan suite passes
**2/2 while four rendering workers run concurrently**. Logs and overlap records are under
`build/follow-ups/native-deterministic-policy-*`. Production policy is unchanged.

Final patch25 rendering verification: 48 jobs, four presets, classic 665 and scaled 1080/2160, repeated
twice. All 12 before/after comparisons are byte-identical (`results-diagnostics-rendering.json`).

## Device work and remaining fidelity work

`SHIELD.md` contains the exact procedure. `device-build.json` records the isolated profile APK, package
`nl.neerdael.projectmtv.quadverify`, its hash and source. The approved device identifies as **AM9 PRO,
Mali-G310, Android 14**, rather than AM6 or SHIELD. Both quad shaders linked on that GLES driver.
The verification app has been stopped, all four debug properties restored, ADB returned to shell mode,
and the original Milkbeat foreground restored. No remote wake was performed. Authoritative cleanup:
`build/follow-ups/device-AM9-Pro/cleanup.json`. SHIELD/Tegra verification remains for later.

Current-series diffusion measurements completed **168 jobs on 12 presets**, including all named
regressions and ORB, against repeated authored-size and ±1.4% controls at 1330 and 2160. Every repeat
is byte-identical. Of 24 comparisons, 20 improve in mean image error and four worsen: Flexi and Cartoon
at 1330, Nuclear and rce-ordinary at 2160 (`results-diffusion-focus.json`).
Uniform diffusion is **not** approved
for shipping on the strength of a better median alone: inspect every degradation, identify its cause, and
verify the broader control/census sets before choosing a fix or gating rule.

Low global image error alone also does not establish fidelity: Royal 191's diffusion result has only
0.020 image error, but its mean luma is 0.38–0.41 of the reference and sampled motion is substantially
reduced. These remain unresolved differences, not accepted improvements.

`results-diffusion-float.json` isolates intermediate quantization: 24 new jobs, six presets at 1330/2160,
two identical renders each, replacing only P1's RGBA8 target with RGBA16F. Cartoon's 1330 error changes
**0.2163 → 0.1965** (baseline without diffusion: 0.1966). Nuclear at 4K changes **0.2139 → 0.1993**
(baseline without diffusion: 0.1785). Other 4K errors: Royal 103 **0.0728 → 0.0732**, Royal 191
**0.0204 → 0.0204**, penattrition **0.1138 → 0.1142**, rce **0.0855 → 0.0875**.
Conclusion: extra intermediate rounding contributes to Cartoon/Nuclear differences, but removing it
does not solve the wider fidelity problem. This format change is research-only; mobile renderability,
memory/bandwidth cost, and the full acceptance sets have not been verified.

`build_original_worker.py` adds a research-only sampler for the existing unfiltered feedback flip.
`original_read_control.py` uses preset copies to preserve only Nuclear's `uv_orig` read or rce's max-trail
read while keeping P1 for the others. Unmodified copies and diffusion-off variants must match the
original hashes before interpreting a result. No automatic shader rewrite or name-based rule is added.

Two early controls are invalid for fidelity conclusions: directly Y-flipping raw framebuffer coordinates
changed diffusion-off hashes, and placing the new descriptor at unit 0 caused the warp's subsequent
fixed-path bind to overwrite it. The latter produced byte-identical active results and is retained as
`results-original-read-invalid-slot.json`, explicitly marked invalid. The V3 worker puts the new
descriptor after main descriptors. Its fresh `original-read-slot-safe` run completed 40 deterministic
jobs; every unmodified-copy and diffusion-off comparison is byte-identical. Preserving Nuclear's
undisplaced read changes 4K error only **0.21386 → 0.21362**. That read alone does not explain its
regression. Preserving rce's max-trail read changes **0.08548 → 0.07764**, and luma ratio **0.894 → 0.923**.

The unit-0 overwrite affects existing explicit filter/wrap aliases that sort before `main`.
Production candidate patch26 reserves unit0 for implicit main. Driver checks fail14 assertions before
the fix and pass all38 cases after it; plain-main/default warp, unaffected aliases, and all16 composite
images remain byte-identical. Six public-API CGL rendering tests accompany the patch: RED3 fail/3 controls
pass; GREEN6 pass/0 skip. The complete host suite passes163 tests,0 skipped.

The original 396-job sweep on33 presets completed, but seven presets exposed an analyzer RNG fault in repeated
classic/1330 runs. Do not use those runs to claim fidelity or degradation. Process-global libc rand is
consumed outside the engine; private Park–Miller shader RNG instrumentation restores exact240-frame
repeats in the exact Echasketch case at665/1330/2160, with identical audio traces. The fix changes tools
only and creates a new instrumentation identity. The corrected 396-job sweep completed with zero repeat
mismatches (`results-sampler-impact.json`); the original runs remain labeled in
`results-sampler-impact-legacy-rng.json`.

Long-window verification completed50 jobs, all repeated identically (`results-diffusion-long.json`).
The12-second window confirms Royal191's motion loss: reference sampled motion0.01894, P1 at4K0.000296,
despite image error improving0.4042→0.0142. Penattrition's base version still loses energy (4K luma
ratio0.724). The base and nz+ variants differ substantially and must be measured separately.

User-reported ORB is the bundled `ORB - Toffie Grider.milk`. Device screenshots at 1080 are byte-identical
with classic and quad lines: mean RGB `[255, 248.04, 0]`, only three RGB colors. This locates the observed
yellow output outside the quad/classic distinction in that experiment.

`results-orb-lifetime.json` and `results-orb-ablations.json`: **20 jobs**, each a 64-second run, repeated
identically. Classic at 1182×665, classic at 1080, and quad at 1080 all converge to nearly uniform yellow.
At the classic reference, one-second image difference falls from **0.144 at 8 seconds to 0.000051 at
16 seconds** at 30 fps. At 60 fps it is already **0.000155 at 8 seconds**. The full 64-second frame stream
is **byte-identical between pre-quad and current classic engines**. Thus this symptom predates PR #14.

A raw-canvas composite still settles (centre RGB about `[0.847, 0.447, 0]` at 16 seconds), so final
composite saturation alone cannot explain the lost motion. Disabling the only visible input, the orange
outer border, leaves black for the entire run. Disabling the blur-driven displacement also settles.
Conclusion: the short four-second measurement window misses this long-lived feedback state.
Hypothesis: the authored recurrence approaches a border-driven fixed point; this still needs comparison
with original MilkDrop before calling it an authored preset defect or changing engine behavior.

`results-orb-upstream.json`: four64-second stock-projectM4.1.7 runs, with only lab FBO/API compatibility
and compile logging. Both shaders compiled, repeats are exact, and the entire frame stream is
byte-identical to current classic rendering at30 and60fps. None of ProjectM TV's rendering patches
causes the settled ORB state; original MilkDrop remains an unverified reference.

## Per-fix image proof

`proofs/` contains separate PNG/SVG evidence for shader diagnostics, real driver shader-object lifetime,
optional-shader fallback, and the deterministic transition test. Its manifest, raw excerpts, fresh
allocation reruns and artifact hashes preserve provenance. The diagnostic string is test input, the
failed preset emitted no frame, and the transition proof is test-only; the captions state those limits.
Sampler and analyzer repeat-delta proofs are retained in their scratch reports while packaging proceeds.

The user approved the reference-grid experiment. It is throwaway code until fidelity and cost gates
pass. The first two probe results are invalid: the copy used the native viewport and then an explicit
target-texture overload that changes a CPU attachment pointer without attaching the GL texture.
The corrected probe uses the framebuffer overload and a positive full-frame gradient control.
Invalid results are retained and marked; no strategy conclusion is drawn from them.

`orb_lifetime.py` preserves source variants, hashes, per-second motion, RGB, and snapshots at 4/8/16/32/64
seconds. The initial baseline's RGB reductions used float32; subsequent ablations use float64 reductions.
All byte hashes and motion comparisons use the same original frame data.
Device captures and line-row diagnostic data are in `build/follow-ups/device-AM9-Pro`.
The row-peak experiment is confounded by feedback/saturation and does not prove a raster tie defect.

## Reproduce

Use the preset-lab Python environment and worker metadata under `build/follow-ups`:

```sh
python measure.py geometry --classic-worker classic-points
python analyze.py geometry
python measure.py low-real
python analyze.py low-real
python measure.py low-nosmooth --filter 'Cartoon|103|Flexi'
python analyze.py low-nosmooth
python low_control.py
python check_shader_fallback.py
python check_rendering_unchanged.py
python measure.py diffusion-focus
python analyze_diffusion.py
python orb_lifetime.py
python orb_lifetime.py --ablations
python build_float_worker.py
python float_control.py
python build_original_worker.py
python original_read_control.py
python long_window.py
python build_upstream_worker.py
python orb_lifetime.py --upstream
python preset_sets.py
python build_sampler_worker.py
python sampler_impact.py
python build_reference_worker.py
python reference_gradient_control.py
python reference_probe.py
```

The scripts live in this directory; lossless five-frame arrays, all-frame hashes, worker identities,
PCM and job diagnostics live in `build/follow-ups/verification`. The old-engine worker uses tooling
from `da4fe0e` with the current caller point-size state. Diagnostic series port the priority evidence patch
onto 0001–0024, adding the missing TexturePoolTest CMake context. Builds and experiments use owned
scratch repositories, and leave the original evidence/PoC worktrees unchanged.
