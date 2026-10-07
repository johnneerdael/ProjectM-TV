# Current 4.2 patch image proof

Status: **in progress**, 2026-10-07. Assessment source is `654815d8`; all 13 ordered
patch hashes are in [series.json](series.json). The main
[patch reference](../../../UPSTREAM_PATCH_VALUE.md) covers only that current series.
The [archived assessment](pre-rewrite-assessment.md) preserves earlier attribution.

## Comparison contract

Use a dedicated Android TV API36 AVD, `CurrentPatchProofTV36`, serial
`emulator-5630`, launched with `-gpu host -accel on`. Its observed features include
`android.hardware.type.television`, `android.software.leanback` and
`android.software.leanback_only`. The backend reports Google (Apple), Android
Emulator OpenGL ES Translator (Apple M4 Pro), GLES3.0 and GLSL ES3.00.
This is a TV system image; the prior API34 migration emulator is a phone image.
No physical TV, unrelated emulator or installed app is used by this capture task.

[protocol.json](protocol.json) records the device fingerprint/user, source pins,
compiled executable hashes, harness hashes, ordered patch identity, all 74 texture
hashes and frozen PCM identity. Workers render the library directly through a
private EGL pbuffer and RGBA8 framebuffer. They are **instrumented libprojectM
executables**, not unchanged production AAR/JNI binaries or Android app screenshots.
The images show the actual library framebuffer rendered on the TV emulator GPU.

Each named preset keeps its exact bundled bytes. Each successful role runs twice
from a fresh process. Audio is identical mono float32 at44100Hz; logical time is
frame/30, seed12345, mesh48×32, dimensions512×288 and frames0–119. Feedback detail
and reference-scaled lines are off in this first comparison. Read back RGBA8,
reverse rows and exclude alpha to produce RGB8. Record every frame's SHA256;
retain lossless PNGs at29,59,119. Headers add labels without altering frame pixels.
No independent brightness scaling or normalization is applied.

### Current-master source equivalence

Observed upstream master is `e98fca85e57802d27a6d11499642de2a1d5e994e`. Its sole
change from the app pin is exactly the captured GLES3.0 admission delta. The
[byte comparison](upstream-master-equivalence.json) proves that the baseline source
before shared clock/random instrumentation matches that master revision. Existing
image labels retain their producer description instead of silently changing identity.

### Explicit capture adjustments

- **Upstream + GLES3.0 admission:** unmodified upstream rejects this GPU before
  rendering because it requires GLES3.2. [gles30-admission.diff](gles30-admission.diff)
  lowers only its GL/GLSL version checks; it imports no preset or rendering repair.
- **Patched, binary cache disabled:** API36's guest `glGetProgramBinary` path
  reports `GL_INVALID_OPERATION` with `bufSize < programBinaryInfoBytes.size()`.
  [no-binary-cache.diff](no-binary-cache.diff) removes only the cache-store call in
  the private snapshot. [Initial attempts](initial-capture-attempts.json) and
  [guest errors](api36-binary-export-errors.json) remain evidence of the limitation.
  Do not call those failures crashes: exit2 indicates the harness's strict GL check.
- Both roles retain common deterministic Preset Lab clock/random instrumentation.
  Production RNG parity is not claimed. Extra patches above are recorded separately
  from the production series; no production source or released binary is modified.

The valid sampler images from cache-enabled and cache-disabled captures have the
same frame hashes. Broader pixel neutrality of cache removal has not been proved.
These captures cannot validate program caching, its failures or performance.

## Current captures

[Capture results](capture-results.json) retain two runs and all 120 hashes for each
successful role, plus explicit load errors for rejected upstream presets. Six
paired rendered presets repeat exactly with zero GL-error frames. Upstream rejects
`161.milk` during preset per-frame compilation and the rotation witness during
shape per-frame compilation, in both attempts. Their left panels quote the error
and explicitly say **no rendered framebuffer**; they are not black screenshots.
The patched roles repeat all 120 frames exactly with zero GL-error frames.

These full-series images demonstrate combined differences. They do not prove that
one named patch caused every difference. [Ablation results](ablation-results.json)
are collected separately by removing exactly one current patch, with the same
capture adjustment/settings and unchanged preset. A patch without a visible
witness needs a numerical or lifecycle fixture as well as an honest image result.

| Patch | Captured witness | Scoped result |
|---|---|---|
|0001|161.milk|Upstream rejects equations; patched renders and repeats. Consolidated renderer subfeatures need separate review; no cache/performance proof.|
|0002|Flexi - dimension window.milk|Removing 0002 changes 120/120 frames; all successful roles repeat.|
|0003|Unchanged Stahlregen funky Blur base preset; lone-dot fixture|Stock rejects code; tolerant no0003 role renders differently; removing0003 changes 120 frames. Fresh-thread isolation still needs its non-image control.|
|0004|widest swing.milk|Removing 0004 changes 119 frames.|
|0005|Cope - The Cloud; collapsed-range fixture|Original is unchanged by ablation in this input. Correctly versioned custom-shader diagnostic changes 119 frames.|
|0006|Hexcollie - This is where we begin stripped.milk|Removing 0006 changes 119 frames.|
|0007|319.milk; mode-switch fixture|Original ablation unchanged during this input; diagnostic mode switch changes 60 frames.|
|0008|idiot - Forty Six and2; invert fixture|Original ablation unchanged during this input; equation-only invert changes 60 frames.|
|0009|Unchanged suksma rand tritex preset|Removing 0009 changes 120 frames; exact-byte and alpha policy analysis remain separate.|
|0010|Duplicate-name shape image roots; fade/reset|Removing 0010 changes 59 frames. Static shader descriptor control is unchanged and retained.|
|0011|Unchanged EoS_Phat_PeterP_Sentinel_Aware_6 witness|Stock fails shape equations first; isolated removal changes 118 frames without that confounder.|
|0012|Unchanged sample06; subpixel shape fixture|Original and synthetic ablations change120 frames. Synthetic no0012 loses coverage entirely.|
|0013|Unchanged sample06; custom-composite impulse|Both ablations change120 frames. Impulse becomes four max 64 pixels without 0013 versus one max 255 pixel with it.|

Every successful role has two identical120-frame RGB sequences and zero GL-error
frames. These counts refer to each recorded scenario, not universal patch effects.
[Original extra captures](original-extra-results.json),
[initial diagnostics](fixture-results.json),
[activated diagnostics](fixture-results-v2.json),
[texture-root shape journey](texture-roots-shapes-results.json) and
[its static-binding preservation control](texture-roots-results.json) remain separate.
Initial blur/composite fixtures omitted `MILKDROP_PRESET_VERSION`, which kept shaders
inactive; their zero-effect results are preserved and receive no shader-proof credit.
The versioned follow-ups are new source identities rather than overwritten attempts.
The initial lone-dot fixture also changed no visible state; the follow-up changes
wave colour, making accepted versus omitted code observable.

[ablation-builds.json](ablation-builds.json) freezes each removed patch, exact source
changes from the full capture snapshot and executable hash. Common source
instrumentation is retained as [upstream diff](upstream-instrumentation.diff) and
[patched diff](patched-instrumentation.diff), with full source inventories.
The texture-root event harness uses a separate [identity](events-worker-identity.json)
and `harness-events/`; its callback records available upstream logs and patched
initialization warnings. Earlier screenshots did not install a logging callback,
so complete fallback/active-program classification remains a final audit item.

## MilkDrop 2 and limits

Original source is available locally; it supports specific geometry, sampling and
CPU-trig intent. No original Windows/D3DX image was rendered in this checkpoint.
A projectM reference-sized image, CPU oracle or diagnostic variant must not be
labeled as MilkDrop 2 output. No Wine/CrossOver/Windows host was found in the current installed tools/apps.
Real MilkDrop 2 GPU capture remains an optional investigation. No whole-corpus fidelity or physical-TV performance claim is made.

## Reproduction state

Private build outputs, full captures and live handles are under this task worktree's
ignored `build/patch-proof/`. `harness/` preserves the exact standalone worker,
EGL capture and CMake sources; it reuses Preset Lab's existing JSON library and
analysis hooks. The archived `capture_pairs_checkpoint.py` preserves the helper
bytes but contains this checkpoint's absolute ADB path/device/private-work layout;
it is not yet a portable public command. Generalized preparation, full image/link/source audit, callback/active-program
classification, relevant non-image controls and final repository review remain open.
Do not run archived scripts against another device without deliberately creating
new task-owned paths and identities. Do not overwrite existing attempt directories.
