# Current 4.2 patch image proof

Original image captures and integrity audit recorded, 2026-10-07. [PR #55](https://github.com/johnneerdael/ProjectM-TV/pull/55) tracks final repository review and publication. Original capture source is `654815d8`; all 13 ordered
patch hashes are in [series.json](series.json). The main
[patch reference](../../../UPSTREAM_PATCH_VALUE.md) now covers the locked 15-patch
capture inventory at `120547f3`, recorded in [current-series.json](current-series.json).
The [archived assessment](pre-rewrite-assessment.md) preserves earlier attribution.

## Current-main synchronization

Historical main `41ec3fc1`/PR #57 added patch 0014 after this capture checkpoint.
The [14-patch inventory](current14-series.json) preserves that intermediate endpoint;
main `120547f3` subsequently added 0015 to the locked publication inventory.
This folder's original `series.json`, workers, frames and verification receipts
remain tied to source `654815d8` and its 13 patches. They are preserved evidence,
not relabeled certification of the expanded endpoint. The [Hurricane comparison](components/legacy14-hurricane/README.md) now provides
matched current14 TV proof for0014. The [locked15 line comparison](components/locked15-lines/README.md) binds effective
reference/AA controls to new rendered manifests and preserves the original13-patch
line records separately. The [locked15 lone-dot replay](components/locked15-lone-dot/README.md) now verifies
the original preset’s upstream rejection and successful control/current frames,
with retained execution evidence. The [complete evaluator comparison](components/locked15-evaluator/README.md)
checks all three roles separately. Revalidation of other affected earlier
witnesses remains pending.

Main synchronization to `eb1e7c16` adds0016 mesh initialization caching. The
existing15-patch workers and captures stay frozen by agreement;0016 uses its
[separate AM6 performance evidence](../mesh-init-cache/README.md). It is not
credited as a new GPU image comparison or silently added to current-series.json.

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
frame/30, seed 12345, mesh48×32, dimensions512×288 and frames0–119. Feedback detail
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
|0003|Unchanged Stahlregen funky Blur base preset; lone-dot fixture|Stock rejects code; tolerant no 0003 role renders differently; removing0003 changes 120 frames. Fresh-thread isolation still needs its non-image control.|
|0004|widest swing.milk|Removing 0004 changes 119 frames.|
|0005|Cope - The Cloud; collapsed-range fixture|Original is unchanged by ablation in this input. Correctly versioned custom-shader diagnostic changes 119 frames.|
|0006|Hexcollie - This is where we begin stripped.milk|Removing 0006 changes 119 frames.|
|0007|319.milk; mode-switch fixture|Original ablation unchanged during this input; diagnostic mode switch changes 60 frames.|
|0008|idiot - Forty Six and2; invert fixture|Original ablation unchanged during this input; equation-only invert changes 60 frames.|
|0009|Unchanged suksma rand tritex preset|Removing 0009 changes 120 frames; exact-byte and alpha policy analysis remain separate.|
|0010|Custom-pack ownership enhancement; duplicate-name roots, fade/reset|Removing 0010 changes 59 frames. This demonstrates added per-preset lookup semantics. Static shader descriptor control is unchanged and retained.|
|0011|Unchanged EoS_Phat_PeterP_Sentinel_Aware_6 witness|Stock fails shape equations first; isolated removal changes 118 frames without that confounder.|
|0012|Unchanged sample 06; subpixel shape fixture|Original and synthetic ablations change120 frames. Synthetic no0012 loses coverage entirely.|
|0013|Unchanged sample 06; custom-composite impulse|Both ablations change120 frames. Impulse becomes four max 64 pixels without 0013 versus one max 255 pixel with it.|

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
initialization warnings. Earlier screenshots did not install a logging callback. A fresh portable-harness
replay records the original translator witness's composite fallback in upstream
and no 0002, with no such warning in the patched role; all 120 frame hashes match
the original images. It also records per-pixel code omission in the no 0003 witness.
No universal active-program classification is claimed for every pictured preset.

## Retained component expansion (2026-10-08)

The [single-page patch reference](../../../UPSTREAM_PATCH_VALUE.md#single-page-comparison-overview)
embeds the current component figures, plain-language differences and code causes.
Supporting receipts now include actual4K [lines](components/lines/README.md),
[shader lifetimes](components/shader-lifetime/README.md),
[global arrays](components/arrays-quicksand/README.md),
[local arrays](components/arrays-local/README.md),
[uniform-bank initialization](components/uniform-bank/README.md),
[compound time/helper state](components/uniform-time-helper/README.md), and
[fresh/reused attachments with pool allocation counts](components/texture-history/README.md).
These component-specific protocols supersede the first512×288 protocol only for
their own recorded runs. Resource/operation panels are measured diagnostics
alongside real healthy library frames, not invented appearance improvements.
The [23-row matrix](../../plans/2026-10-08-retained-component-proof.md) remains
incomplete, including default-off/external/pressure/context pool controls and
cache/batching/pass evidence. Deeper optimization and lifecycle comparisons are
deferred to a follow-up under the locked publication scope below. Final-head
review and repository gates remain open.

## MilkDrop 2 and limits

Original source is available locally; it supports specific geometry, sampling and
CPU-trig intent. No original Windows/D3DX image was rendered in this checkpoint.
A projectM reference-sized image, CPU oracle or diagnostic variant must not be
labeled as MilkDrop 2 output. No Wine/CrossOver/Windows host was found in the current installed tools/apps.
Real MilkDrop 2 GPU capture remains an optional investigation. No whole-corpus fidelity or physical-TV performance claim is made.

## Reproduction state

Private build outputs, retained frames and controller records are under this task worktree's
ignored `build/patch-proof/`. `harness/` preserves the exact standalone worker,
EGL capture and CMake sources; it reuses Preset Lab's existing JSON library and
analysis hooks. The archived `capture_pairs_checkpoint.py` preserves the helper
bytes but contains this checkpoint's absolute ADB path/device/private-work layout;
it is not yet a portable public command. [Portable preparation/capture/verification tools](../../../../tools/patch-proof/README.md)
are now verified through fresh exports and GPU captures. The
[reproduction receipt](reproduction-validation.json) records evaluator contracts,
logging and exact historical-frame matches. The [checkpoint audit](checkpoint-audit.json)
checks 31 images and 134 successful run entries, with 10 explicit failed runs retained.
Final repository review remains open.
Historical receipts retain frame hashes and the producer's repeat-check results,
along with selected PNG payloads. For runs whose complete RGB streams were deleted,
those PNGs remain independently checkable, but the other frame hashes cannot be
recomputed from the retained payloads. A full-frame verifier must require complete
streams; matching hash lists alone do not establish independently verified repeats.
The [full-payload replay](full-payload-replay-results.json) repeats the recognizable
texture journey with upstream, without0010 and patched workers. Its
[verification](full-payload-replay-verification.json) reconstructs each source role
and recomputes every frame hash from the complete retained RGB streams. The
[audit](full-payload-replay-audit.json) records 720 verified frames matching the
earlier journey, with zero GL errors. Raw streams remain in the ignored private
build directory; they are required for future full-frame verification and are
not committed as documentation assets.
The subsequent [executable-bound replay](bound-binary-replay-results.json) also
rebuilds each worker from the reconstructed source and checked-in harness using
NDK27.3.13750724. Its [verification](bound-binary-replay-verification.json) requires
matching canonical executable bytes after removing non-runtime debug/symbol
metadata and the GNU build-id note. All720 frames match the earlier full-payload
replay. The verifier requires an explicit NDK path for this source-to-executable
check; source-only reconstruction does not issue a verification certificate.
Do not run archived scripts against another device without deliberately creating
new task-owned paths and identities. Do not overwrite existing attempt directories.

The source receipts use zero-context unified diffs. Apply them only to the
identified parent source with `git apply --unidiff-zero`; source hash inventories
provide the full-file verification.

## Where subtle differences are visible

The primary patch document now uses earlier retained frames, aligned nearest
crops and explicitly labeled difference maps for9/12/13. Raw before/after crops
are never brightened. Whole-frame crop outlines are annotations; the third column
is derived data, not rendered appearance. `visibility-figures.json` records the
source RGB hashes, crop, map formula/gain/clipping and numeric differences.
The original dark witness changes only3 pixels for0012 and6 for0013 at frame29;
those small seed changes must not be sold as whole-scene brightness fixes.

The earlier319 waveform example sets wave_a=0 and receives no positive0007 credit.
The unchanged Hexcollie wormhole preset evaluates wave_mode=q8%7; new
`wave-witness-results.json` records exact two-repeat/all120-frame controls for
upstream, current minus0007 and current. Its all120-frame causal change is now the
primary original waveform example. Initial captures remain preserved.

## More visible unchanged originals selected from the full bundle

A source scan inspected all9,606 bundled presets with the existing Preset Lab
parser. It found5 direct alpha-image references for0009,6,123 enabled-shape
candidates for0012 and4,513 custom-main-composite candidates for0013. These are
source matches, not proven defects. Source ranking and the exploratory screens
remain separate from final two-repeat proof; zero effects and failures are retained.
35 initial candidate/patch scenarios,24 threshold candidates and6 further colour
threshold candidates were rendered exploratorily. None is whole-corpus certification.

The main document now leads0012 with the unchanged btbam green-machine variant
and0013 with the unchanged DemonLD Toxic water variant. Their repeat evidence is
in `visible-confirmed-results.json`, with the source hashes, frame images and
measurements identified in `visible-original-figures.json`. The originals are
not edited, and the figures use unbrightened full frames and aligned nearest
crops. They replace the tiny dark witness as the primary explanation; numerical
controls and the old records remain secondary.

## Clearer02/05 originals and recognizable10 host fixture

The source/history screen examined nine blur-bound originals and20 translator
witnesses. Their exploratory outcomes remain in `blur-translator-screen-results.json`.
Final original-preset controls are in `clearer-02-05-results.json`: madness portal
for0002 and the Julia embossed Jelly preset for0005, with upstream/no-patch/current
two-repeat120-frame zeroGL-error captures. `clearer-02-05-10-figures.json` identifies
full frames, aligned raw crops, input hashes and measurements.

The recognizable pack-switch fixture uses bundled onefish.jpg (a spotted texture)
and rose.jpg under the same shared.jpg name. Its original inputs, host sequence
and full repeated proof are retained in `recognizable-pack-fixture/` and
`recognizable-pack-switch-results.json`. This is explicitly a host-level fixture;
no named-image custom-shape fields were found in the bundled artist presets.
The separately requested predictor brief is `predictor-patch-0010-brief.md`.

## Predictor-created Aurora ownership witness

The user supplied animated SOL/LUNA packs and a forecast written before the GPU
test. The frozen witness makes patch 0010's ownership enhancement visible at frame 20, before
the fade: a blue LUNA emblem replaces SOL inside its still-orange portal.
All three roles repeat exactly with zero GL errors; the patched reset/no-reset
sequences match all 120 frames. See [frozen inputs, screenshots and audit](aurora-ownership/README.md).
Upstream uses its documented global lookup policy; the patch adds retained
per-preset paths for custom-pack hosts. These captures do not establish an
upstream contract violation or a MilkDrop compatibility correction.

## Human-review presentation

The main reference is the concise image-led review page. Its new
[upstream/our-library figure audit](human-review/figure-audit.json) records six
actual upstream/patched pairs at the selected visible timestamps, plus exact
matching crops. They replace ablation-only figures as the leading comparisons;
the original ablations remain supporting cause checks. Overview pixels reconstruct
to the retained capture hashes, and zooms use nearest sampling without gain.
The [expanded working assessment](expanded-assessment.md) preserves the inventory,
original input map and technical discussion separately from the review page.

## Locked publication scope

The user froze the engine inventory at main120547f3:15patches ending0015.
`current-series.json` identifies that locked set; `current14-series.json` preserves
the previous14-patch snapshot. Finish readable comparisons for all15patches,
then review/CI/publication. The user explicitly deferred deeper optimization and
lifecycle comparisons to a follow-up; they must not keep reopening this PR.
Earlier source/capture identities remain unchanged.
