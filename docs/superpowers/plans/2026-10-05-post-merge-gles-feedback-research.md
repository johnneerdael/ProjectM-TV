# Post-merge GLES feedback fidelity research

Current follow-up, 2026-10-06: patch0043 now preserves authored geometry recurrence and restores per-vertex shape inputs. Final actual-AAR matrices recover the two emulator witnesses at Standard/Medium/High and pass repeat/off controls; matched Mali-G52 captures remain faithful without the emulator's dramatic collapse. The exact upstream translator fault remains unproved, and the four Mac exceptions still have mixed residual metrics. See [the source-bound fix evidence](../evidence/native-trails-geometry-fix/README.md), including matched before/after screenshots. The original handover below records historical0042 observations; its captures and source identities are preserved.

Status: research handover, 2026-10-05. The owner explicitly accepted rare visual defects for post-merge investigation when the wider result improves the majority of presets. Waltra/Hexcollie fidelity defects are therefore not merge blockers under that ruling. This investigation made no tracked engine, patch, submodule, APK or Gradle changes.

## Preserved evidence and identities

- Actual-AAR matrix: `build/native-trails/summary-v1/summary.json`, contact/gallery images in its `images/` directory, and `hex-time-contact.png`. Both named presets have repeatable authored controls and exact old-Native/candidate-off controls; enabled levels report an active 1280×720 canvas rather than fallback.
- Baseline source: `6e71ac2a18a95463fbe3a21c05e6dd4027cb74a0`; candidate source: `55ee02f02e8a8a35616ba5ad7ef362dd6f3f0e70`. Candidate patch 0042 SHA256: `be3f39da0e936a48b581781ed1b8ab1e13810ac6ba55b37abba6f5efb5ad151e`. Sources are frozen under `build/native-trails/workers-v3/{baseline-native,candidate-native}/source/` with receipts/identities alongside them.
- Desktop pilot: `build/native-trails/mac-wide/runs/pilot-v1/`. Reported 35/35 jobs complete and all eight controls exact. Waltra enabled levels had mean luma ratios approximately 1.001/0.9996/0.9963 and MAE approximately 0.002; Hexcollie ratios and contrast were approximately 1 with MAE approximately 0.002. The wider frozen 160-preset screen subsequently completed all 976 jobs with no final failures. Standard lowers mean per-frame absolute luma error on 129/160, equals it on 17, and increases it on 14; see `../evidence/native-trails-production-mac-wide-v1/` for source-bound diagnostics.
- Private pass diagnostics: `build/native-trails/engine-diagnostic/`. Preserve `engine/`, `diagnostic-instrumentation.patch`, `diagnostic-identity.json`, desktop/GLES raw stage captures, comparison JSON, build/configuration logs and executable before removing this worktree. Build intermediates ending in `.o` were removed when disk filled; source, executable and evidence remain. Copy/archive this directory externally before cleanup; no external archive is claimed here.
- Diagnostic overlay SHA256: `dcfb2ffca08c1e51ccc13781a2125d4b02721b4f3f759be85339a607cb9aeed9`. Identity JSON records executable, PCM, both preset assets and ANGLE library SHA256 values. Private instrumentation is not shipping byte identity.

## Observed visual regressions

`Waltra - Heaven Liquid.milk`: actual Android AAR Standard/Medium/High mean luma ratios approximately 0.472/0.471/0.471 versus authored, while old Native is approximately 0.910. Frame300 loses many visible particles. Its three random additive filled circles seed noise/blur feedback; its composite includes mirrored red feedback, blur, powers and a nonlinear blue layer.

`Hexcollie - Julian Shader Wars4 nz+ sports fart.milk`: actual AAR enabled levels have approximately 0.032 of authored contrast and aggregate MAE approximately 0.2008, despite a mean luma ratio approximately 1.028. The spiral visible in authored/old Native becomes nearly uniform yellow at frames 120/300, and the later frame 479 structure differs strongly. The preset has92 tiny filled shapes with alpha gradients, inverted/sharpened blur feedback and a solarizing mirrored composite. Brightness alone misses this failure.

These are actual visual regressions in the measured GLES path. The evidence does not establish their cause, their prevalence in the full Android corpus, or behavior on physical TV GPUs. Authored rendering is1280×720;1182×665 is only the common metric resize, so a different authored canvas does not explain them.

## Bounded pass-level investigation

The private diagnostic copies the frozen candidate engine, keeps deterministic shader/evaluator/noise seeds, uses the same float PCM as the desktop pilot, and runs authored 1280×720/off versus native 3840×2160/Standard in separate processes. Capture the first 12 frames at 30 fps. Read persistentL, flipped canvas input, canvas warpLw, blur1–3, native geometry at each odd-scale canvas centre, qvariables, shader RNG state and evaluated shape vertex bytes. Native geometry is sampled at `(3*x+1,3*y+1)` without averaging. Trace hooks restore caller framebuffer bindings; no shipping readback/API was added.

Desktop CGL Waltra control: frame 0 all recorded state/pass/vertex bytes match exactly. Frame1 inputs, warp and all blur levels remain exact; geometry and persistentL differ by only0.000009 stored-byte MAE, max 1.

Private host GLES uses native arm64 SDK ANGLE 2.1.1 (`fbf66f49c7cc`) with Metal/Apple M4 Pro, macOS 15.8 build 24H23. This is a different driver from the actual AAR's Android Emulator OpenGL ES Translator. All four corrected diagnostic runs completed12 frames with no logged GL errors or preset-load failures. An initial attempt used unsupported GLES RGB readback and produced GL_INVALID_OPERATION; its logs are retained under `invalid-rgb-read-attempt/` and must not be used as pixel evidence. The corrected probe readsRGBA and extractsRGB.

| Earliest inspected boundary | Before it | First observed difference |
|---|---|---|
| Waltra frame 1, reconstruction/native geometry → sampled authored state | qvariables, shaderRNG, shapevertices, flippedinput, Lwarp and blur1–3 byte-exact | Geometry and persistentL MAE 0.005757 stored bytes, max 4; 8187 RGB bytes differ |
| Hexcollie frame 0, same boundary | qvariables, shaderRNG, shapevertices, flippedinput, Lwarp and blur1–3 byte-exact | Geometry and persistentL differ in 95 RGB bytes, max 1 |
| Hexcollie frame 1 | qvariables/RNG/vertices still exact; small prior-state divergence | Sparse geometry error reaches116 stored bytes;145 RGB bytes differ |

The early difference is already present before Inject; Inject reproduces the sampled geometry state at scale 3. The current trace does not separate reconstruction from geometry rasterization, so neither has been proved responsible. By frame 11 the differences have entered warp and blur feedback. `gles-stage-comparison.json` contains frames 0/1/2/3/11 statistics; all 12 raw captures remain available. Twelve frames do not reproduce or explain the complete 480-frame Android collapse.

Double-evaluated shape/wave equations are not supported by source or traces: the shipping path calls each shape/wave draw once. Standard evaluates the per-pixel mesh once via Prepare then draws via DrawAgain; higher levels evaluate via Draw then reuse DrawAgain. The two flagged presets have no visible motion vectors. Byte-exact evaluated vertices, qvariables and shader RNG further refute that explanation in this bounded probe.

Geometry coverage/blending also needs separate controls: Waltra's main waveform is mode6, thick/additive with fWaveAlpha0.004; Hexcollie's is mode1, thick with the same tiny alpha. Such small inputs can seed a nonlinear recurrence. Authored GL lines versus native scaled quads, native-centre coverage, shape alpha interpolation and stored-byte rounding are candidates; the current geometry snapshot includes all of them. Do not attribute the difference solely to the random circles or tiny shapes without per-component captures.

Precision remains a hypothesis, not a confirmed cause. New detail shaders declare highp float/int/sampler2D, while shared CopyTexture and untextured geometry shaders use mediump floating values; CopyTexture's sampler2D uses its default precision. GLSL ES 3.00 declares builtin gl_FragCoord highp, so do not claim it is mediump without implementation evidence. See [GLSL ES 3.00 specification](https://registry.khronos.org/OpenGL/specs/es/3.0/GLSL_ES_Specification_3.00.pdf), sections 4.5 and 7.2. A global precision change could alter existing consumers and needs explicit default-off controls.

## Reproduce the private GLES diagnostic

Run from the preserved task checkout. Prerequisites already used: CMake/Ninja, AppleClang, pinned engine/evaluator sources, Android NDK 27.0.12077973 headers, and the installed emulator's arm64 ANGLE dylibs. No new packages were installed.

```bash
cmake -S build/native-trails/engine-diagnostic/engine -B build/native-trails/engine-diagnostic/angle-cmake -G Ninja -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=OFF -DBUILD_SHARED_LIBS=OFF -DENABLE_GLES=ON -DENABLE_SYSTEM_PROJECTM_EVAL=OFF -DENABLE_PLAYLIST=OFF '-DCMAKE_CXX_FLAGS=-include /Users/jneerdael/Scripts/Projectm-TV/.worktrees/native-trails-production/tools/projectm-host-gl-shim.h'
cmake --build build/native-trails/engine-diagnostic/angle-cmake --target feedback-diagnostic -j4
```

The private CMake overlay overrides the upstream Darwin GLES restriction and links ANGLE; do not apply it to shipping sources. `gles-headers/` contains copies of the installed NDK's EGL/GLES/KHR headers. The binary sets PRESET_LAB_SEED 12345 and forces an offscreen ANGLE Metal ES 3 context.

```bash
DYLD_LIBRARY_PATH=/Users/jneerdael/Library/Android/sdk/emulator/lib64/gles_angle DIAG_PCM=/Users/jneerdael/Scripts/Projectm-TV/.worktrees/native-trails-production/build/native-trails/mac-wide/audio-float.f32 build/native-trails/engine-diagnostic/angle-cmake/feedback-diagnostic authored '/Users/jneerdael/Scripts/Projectm-TV/.worktrees/native-trails-production/core/src/main/assets/presets/Waltra - Heaven Liquid.milk' /Users/jneerdael/Scripts/Projectm-TV/.worktrees/native-trails-production/build/native-trails/engine-diagnostic/gles/waltra/authored
DYLD_LIBRARY_PATH=/Users/jneerdael/Library/Android/sdk/emulator/lib64/gles_angle DIAG_PCM=/Users/jneerdael/Scripts/Projectm-TV/.worktrees/native-trails-production/build/native-trails/mac-wide/audio-float.f32 build/native-trails/engine-diagnostic/angle-cmake/feedback-diagnostic standard '/Users/jneerdael/Scripts/Projectm-TV/.worktrees/native-trails-production/core/src/main/assets/presets/Waltra - Heaven Liquid.milk' /Users/jneerdael/Scripts/Projectm-TV/.worktrees/native-trails-production/build/native-trails/engine-diagnostic/gles/waltra/standard
```

For Hexcollie replace the preset basename with `Hexcollie - Julian Shader Wars4 nz+ sports fart.milk` and output directory `gles/hex/{authored,standard}`. Each invocation starts a fresh process because evaluator RNG is thread-local and not reset by constructing another engine. `.rgb` files use bottom-left framebuffer orientation; adjacent `.size` files give width/height. `.bin` files preserve raw CPU bytes. Use byte equality and mean/max absolute byte differences; compare equal dimensions. Current paths are recorded verbatim for reproducibility and must be updated after archive relocation.

## Next research, after merge

1. Preserve/freeze the actual AAR receipt, presets, complete PCM/time/seed inputs and worker source. Add the same pass boundaries to a private actual Android AAR diagnostic, including a separate native Hc capture immediately after Combine and before shapes. Validate every readback/error/preset identity; do not substitute final luma for persistent state.
2. Determine whether the first difference appears in reconstruction or geometry rasterization. Compare Lw with Hc at canvas centres, then compare each shape's result with the same evaluated vertices rendered at authored resolution. Record qualifier ranges/precision and translated shader source where the driver exposes it. Check coordinate/filtering, interpolation, blending/dither and sampler precision separately; change one variable per controlled trial.
3. Build a focused GLES regression around colored additive circles and tiny alpha-gradient filled shapes at odd scale 3, followed by a blur/sharpen/invert recurrence. Compare persistentL and blur textures frame-by-frame with plain authored rendering. Keep the direct-L host fixture and unchanged/default-off frame hashes as controls.
4. Evaluate a narrowly scoped precision/sampling fix only after a controlled trial identifies the boundary. If rendering the same evaluated geometry at canvas size is needed, cache/reuse evaluated geometry; do not rerun persistent shape/wave equations or RNG for a second draw.
5. Re-run frozen temporal captures on both named presets and representative controls, all three gains, actual AAR and at least one physical TV GPU when the owner authorizes device work. Reassess documentation/release notes and obtain fresh review before a production fix. The authorized live AM6 run covered FPS, automatic quality and background music continuity; it did not provide matched physical-TV brightness captures.

Do not change0042 as part of this handover. Research conclusions must distinguish measured first-pass differences from a proved explanation of the later Android visual collapse.

## Additional Mac exceptions to research after merge

Matched frame-300 inspection and eight-frame metrics flag four larger luma-error increases against old Native: `Flexi + orb + geiss - the computer is your friend trust the computer.milk`, `rediculator qrem glob.milk`, `suksma - Hexcollie - Julian Carnival - shimmy dumb grid dogmaklyasm nz+6.milk`, and `suksma - don't know, but yes this bored (adnan's).milk`. Their mean per-frame luma-error increases are approximately 0.0174, 0.0213, 0.0330 and 0.0200 respectively. Computer-is-your-friend changes color/pattern, shimmy-grid-nz+6 changes the retained small structures, and the other two show smaller color/temporal differences. All enabled gains share much of the difference. These are direct Mac observations with a different PCM feed and driver from Android; do not assume the same cause as the two GLES cases. Use the frozen eight-frame captures and source-bound `summary.json` to investigate temporal and persistent-state differences before proposing a fix.

Committed portable diagnostic overlay, identity and stage statistics are in `../evidence/native-trails-gles-stage-diagnostic/`; the full private source and raw-stage archive must be retained locally before deleting the task worktree.
