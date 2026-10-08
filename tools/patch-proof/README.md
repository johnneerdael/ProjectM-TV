# Current-patch Android TV image proof

Reproduce the source-bound comparison in
[the patch reference](../../docs/UPSTREAM_PATCH_VALUE.md). These private executables
render libprojectM directly on a GPU Android TV emulator; they are not production
AAR/JNI binaries or app screenshots. No app, preference or system property changes.

Requirements: Python 3.12+, Pillow, CMake/Ninja, initialized projectM/evaluator git
caches, NDK 27.3.13750724 and a booted ARM64 Android TV emulator using host GPU
acceleration. The proof scope requires television/Leanback features and rejects
reported software renderers. Select a task-owned serial and current Android user.
Offline verification requires the recorded emulator serial, both TV features and
a nonnegative integer Android user before issuing a verification receipt.
Do not use another task's emulator. The scripts never launch or wake a device.

Run from the repository root. `CACHE_REPO` is a checkout whose submodules are
initialized; it can be the primary checkout when the task worktree's gitlink is
empty. Preparation clones read-only caches into fresh private inputs. Use a new
work directory for each preparation/capture; existing directories are refused.

```sh
python3 -m venv build/patch-proof-env
build/patch-proof-env/bin/pip install Pillow
python3 tools/patch-proof/prepare.py --cache-repo CACHE_REPO --ndk NDK_DIRECTORY --work build/patch-proof-workers --roles upstream without-0006 patched
build/patch-proof-env/bin/python tools/patch-proof/capture.py --workers build/patch-proof-workers/workers.json --preset 'core/src/main/assets/presets/Hexcollie - This is where we begin stripped.milk' --textures core/src/main/assets/textures --device SERIAL --user USER --ndk NDK_DIRECTORY --work build/patch-proof-zoom
build/patch-proof-env/bin/python tools/patch-proof/verify.py --work build/patch-proof-zoom --ndk NDK_DIRECTORY
```

Use `--adb /path/to/adb` if it is not on PATH. Capture supports 512×288 (default),
256×144, 1280×720, 1920×1080, 2560×1440 and 3840×2160 through `--width`. It renders 120
frames at 30Hz, fixed seed 12345 and identical generated mono float32 PCM. The worker validates the job seed and installs it before libc, shader and evaluator RNG initialization; a conflicting PRESET_LAB_SEED cannot change the render. Evaluator controls explicitly use seed12345. Each role
runs twice; every RGB frame is hashed, alpha excluded, with lossless PNGs retained
at 29/59/119. The comparison adds labels above unchanged framebuffer pixels. Failed
or unstable roles have an explicit panel rather than a fabricated render.
`results.json` preserves load errors and available engine logs/warnings. A repeated
load failure is still a failure. `verify.py` checks source/binary identities, repeat
hashes, retained image payloads, counts, backend and comparison pixels. Successful
runs retain the complete `frames.rgb` stream locally; verification recomputes its
SHA256 and all 120 frame hashes. At 512×288 this adds about 50 MB per successful run.

New captures copy the preset to `inputs/witness.milk` and the complete texture
tree to `inputs/textures/` before hashing or uploading. Verification recomputes
both input hashes/inventories from these retained bytes. For an older capture
without `inputs/`, explicitly supply `verify.py --preset EXACT_PRESET --textures
EXACT_TEXTURE_DIRECTORY` (Python API: `verify(work, ndk, series_path,
preset=Path(...), textures=Path(...))`). Missing either path is an error. The
receipt distinguishes these supplied historical inputs from retained capture
bytes: they match the recorded hashes, but the original uploaded bytes were not
retained. Existing streams and workers remain unchanged. Incomplete retained
inputs fail verification even when external paths are supplied.

New reports record the exact owned remote workspace. Every job must reference
its audio.f32, witness.milk and textures directory; texture journeys use its
textures/a and textures/b roots and reload the same witness. Bands/manifest output
paths also stay within that workspace. Historical reports without this field
require explicit --historical-remote-workspace ORIGINAL_OWNED_PATH (Python API:
historical_remote_workspace=...). Receipts distinguish this supplied historical
workspace from a recorded one. Do not rewrite preserved reports to add it.

Use `--line-reference-height 1080` to request the patched library's 1920×1080
reference-size line path. Upstream keeps its existing GL-line implementation;
the same preset/audio/clock/render size is used in both roles. A separate current
capture with height0 supplies a classic-line control. `--line-antialiasing` enables
the patched API's optional AA. These host settings and the job bytes are retained.

For high-resolution runs, add `--compress-streams`. The tool streams complete
RGB frames through lossless gzip and verifies the decompressed frame/stream hashes
before removing that run's raw copy. Verification accepts either `frames.rgb` or
`frames.rgb.gz` and reads one frame at a time. No frames are dropped, no pixels
are changed, and older frozen raw streams are untouched.

Capture and verification require the same NDK directory and rebuild every worker
from the reconstructed source and checked-in harness. They compare canonical ELF
copies after stripping debug/symbol tables and the path-sensitive GNU build-id note;
runtime sections, program headers and load permissions remain part of the match.

`--shader-failure-probe` runs sixteen intentional fragment rejections through the
actual linked `Renderer::Shader` before rendering, then tests a valid retry. Its
shared GL observer counts live vertex shaders via `glIsShader`, records rejection
messages, restores the entry point and releases diagnostic leaks. Verification
requires the upstream1–16 / corrected0 count sequence,34 creations, a linked retry,
clean diagnostic cleanup, no GL API errors and matching observations across repeats.
The shader errors are intentional diagnostics; the subsequent images are valid
healthy-preset frames. A changed native harness requires freshly prepared workers.
`--texture-history-probe` tests the actual linked `TextureAttachment` with a
shared allocator fixture: null 64×48 RGBA8 allocations receive green bytes before
library initialization. A raw allocation/readback proves the fixture works.
The probe reads complete fresh and recreated attachment pixels, fills retired
contents blue, counts real storage allocations, and records pool bytes plus
caller framebuffer/clear-color/mask/scissor preservation. The patched role opts
into a 32,768-byte pool only for this diagnostic and resets it before normal
preset rendering. Green is controlled initial storage, not a naturally observed
artist-preset failure. Verification checks all readback bytes, the allocation
control, state, counts and exact independent repeats. Context recreation,
external ownership and pressure-release controls remain separate work.

Successful image verification also binds each manifest to its outer role/repeat,
seed12345/FPS30 and retained manifest.json/job.json. It checks the fixed clock,
frame window, dimensions, reference/diagnostic settings and exact host-event
sequence; jobs must agree across roles/repeats apart from identity. Render
manifests record applied_controls from the helper that invokes the line/feedback
setters, including source-verified normalization. The verifier checks reference
width/height, antialiasing and float32 feedback alpha against that record. Upstream
has no TV control API and reports classic0/0, false and disabled feedback, even
when a paired job requests reference scaling. Earlier manifests without these
fields require fresh workers/capture for current certification. The retained
PCM length and hash must match the trusted deterministic waveform digest, and
dimensions must use the six capture widths with their derived 16:9 heights. Run metadata cannot silently
certify frames produced with a different protocol.

Capture rejects unsupported role names before creating output directories, and
both capture and verification require each role label to match its worker identity
and removed-patch metadata. Swapped worker records cannot silently relabel a run.
Both also check the prepared patch inventory against the recorded series. Capture
retains each validated worker under inputs/workers/ and uploads that copy, then
checks its remote SHA256 before execution. Verification rebuilds and checks this
retained executable; the original prepared-worker file is not the execution
payload. Captures without retained workers need a fresh replay for a current
certificate; preserve their earlier receipts rather than rewriting them. In the
identity, `ordered_patches` lists the complete input series for patched/ablation
roles; `patch_removed` names the omitted patch. Upstream has an empty inventory.

The default series remains the immutable13-patch checkpoint so older commands
cannot silently relabel frozen captures. For the locked15-patch publication endpoint,
pass `--series docs/superpowers/evidence/current-patch-proof/current-series.json`
to **prepare, capture and verify**. Prepare derives its source commit and allowed
ablation numbers from that manifest; `without-0014` and `without-0015` are supported there. Use `current14-series.json` explicitly to replay the preserved14-patch snapshot.
Workers and captures record a canonical manifest digest, and verification rejects
a different selected snapshot. Unbound legacy receipts are accepted only against
the original frozen manifest. Source reconstruction still checks every actual
patch input, engine/evaluator pin, source tree and rebuilt executable.

Preparation requires the selected documented series and pins. Supported roles are
`upstream`, `patched`, and removals of patches0002 onward in the selected manifest. Patch0001 is
consolidated and other patches depend on it; compare its representative witnesses
against upstream rather than claiming a standalone removal. All compiled sources,
patch hashes, harness/dependency hashes, capture adjustments and binaries are
identified in the preparation directory.

The upstream role exports the app pin plus the exact GLES3.0 admission delta. That
source matches observed master e98fca85; see the committed equivalence receipt.
All roles share deterministic Preset Lab instrumentation. Patched roles disable
program-binary cache export because the API36 guest reports metadata GL errors.
These adjustments remain explicit and never change production source. This proof
does not validate caching, performance, production RNG parity or Windows appearance.

For the non-image evaluator contracts, prepare the `upstream`, `without-0003` and
`patched` roles, then add `--evaluator-control` to a capture invocation in a new
work directory. It runs fresh threads sequentially through the compiled evaluator
and records their 128-value streams and lone-dot compilation/value. Both capture
and verification require exactly these three evaluator roles; subsets are not a
complete evaluator comparison. This control
does not create a GL context. Upstream and the no 0003 role should reject the dot
and retain shared random-stream progression; patched threads begin independent
identical streams and dot evaluates to zero. Verify both repeats with `verify.py`.
Pass the same `--ndk NDK_DIRECTORY` used for preparation to both capture and verify.
Verification parses each retained `output.txt` and checks its stdout JSON against
the inline control, allowing capture's appended stderr diagnostics. Image
verification independently rejects reported software renderers even when all
backend records agree.

[The frozen evidence](../../docs/superpowers/evidence/current-patch-proof/README.md)
also includes the duplicate-name texture-root fade/reset journey and specific
activation fixtures. Its archived helpers preserve the original producer code;
new reproductions retain their own identities rather than overwrite those results.

For patch 0010, prepare `upstream without-0010 patched`, select
`docs/superpowers/evidence/current-patch-proof/fixtures/texture-roots-shapes/preset.milk`
and its containing folder for `--textures`, then add `--texture-journey`. It uses
roots `a`/`b`, switches the root at 20, starts a two-second soft cut at 21 and resets
textures at 40. The worker retains 40/59/119 PNGs as well as 29; the generic comparison
shows 119 after the transition completes, so inspect 40/59 for the ownership difference.
Patch 0010 is a host-integration enhancement: it adds per-preset lookup retention
to upstream's documented global texture-path reset behavior.

New capture records identify their producer script; verification records identify
the verifier. The capture tool removes only its own hashed remote scratch directory
after pulling evidence, including on handled failures. Local records remain intact.
Before staging a retry, it removes that same owned remote directory with checked
cleanup, then recreates it; failed cleanup stops capture before any upload.
Capture and verification rebuild the prepared source from the pinned engine/evaluator
checkouts and patch inputs, then check the role-specific source tree and capture
adjustments against that reconstruction. The role labels and removed-patch fields
are checked against the reconstructed source.
For a nonzero worker exit, it independently attempts to retain the engine log,
structured manifest and partial RGB stream before cleanup. It records unavailable
pulls explicitly and keeps the run failed. Raw failed streams stay in the ignored
local build directory. Verification accepts a rejected role only when both runs
explicitly failed with nonzero integer exit codes and no claimed successful repeat.
Every completed command has a retained execution.json exit receipt. Rejection
checks require matching job settings, artifact inventory/hashes and available
diagnostics; successful manifests or derived images contradict a rejection.
Earlier runs without these execution receipts need a fresh capture for current
certification; their preserved receipts remain historical.

Run the evidence-integrity and failed-capture controls with:

```sh
build/patch-proof-env/bin/python -m unittest discover -s tools/patch-proof -p 'test_*.py' -v
```

Comparison labels use the committed5×7 bitmap font in assets/, loaded through
Pillow’s legacy font API without FreeType or the installation’s default font.
Capture records the glyph/font/atlas and renderer identities; Pillow version is
provenance only. Verification checks those identities when recorded and compares
the fixed-font label pixels. Label-only reconstruction of an existing comparison
is recorded separately as comparison_relabel, with original capture_sha256 and
all framebuffer streams left unchanged. See assets/README.md for font provenance.
