# Current-patch Android TV image proof

Reproduce the source-bound comparison in
[the patch reference](../../docs/UPSTREAM_PATCH_VALUE.md). These private executables
render libprojectM directly on a GPU Android TV emulator; they are not production
AAR/JNI binaries or app screenshots. No app, preference or system property changes.

Requirements: Python 3.12+, Pillow, CMake/Ninja, initialized projectM/evaluator git
caches, NDK 27.3.13750724 and a booted ARM64 Android TV emulator using host GPU
acceleration. The proof scope requires television/Leanback features and rejects
reported software renderers. Select a task-owned serial and current Android user.
Do not use another task's emulator. The scripts never launch or wake a device.

Run from the repository root. `CACHE_REPO` is a checkout whose submodules are
initialized; it can be the primary checkout when the task worktree's gitlink is
empty. Preparation clones read-only caches into fresh private inputs. Use a new
work directory for each preparation/capture; existing directories are refused.

```sh
python3 -m venv build/patch-proof-env
build/patch-proof-env/bin/pip install Pillow
python3 tools/patch-proof/prepare.py --cache-repo CACHE_REPO --ndk NDK_DIRECTORY --work build/patch-proof-workers --roles upstream without-0006 patched
build/patch-proof-env/bin/python tools/patch-proof/capture.py --workers build/patch-proof-workers/workers.json --preset 'core/src/main/assets/presets/Hexcollie - This is where we begin stripped.milk' --textures core/src/main/assets/textures --device SERIAL --user USER --work build/patch-proof-zoom
build/patch-proof-env/bin/python tools/patch-proof/verify.py --work build/patch-proof-zoom
```

Use `--adb /path/to/adb` if it is not on PATH. Capture supports 512×288 (default)
or 256×144 with `--width 256`, matching the measured checkpoint. It renders 120
frames at 30Hz, fixed seed 12345 and identical generated mono float32 PCM. Each role
runs twice; every RGB frame is hashed, alpha excluded, with lossless PNGs retained
at 29/59/119. The comparison adds labels above unchanged framebuffer pixels. Failed
or unstable roles have an explicit panel rather than a fabricated render.
`results.json` preserves load errors and available engine logs/warnings. A repeated
load failure is still a failure. `verify.py` checks source/binary identities, repeat
hashes, retained image payloads, counts, backend and comparison pixels.

Preparation requires the documented 13-patch series and pins. Supported roles are
`upstream`, `patched`, and `without-0002` through `without-0013`. Patch0001 is
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
and records their 128-value streams and lone-dot compilation/value. This control
does not create a GL context. Upstream and the no 0003 role should reject the dot
and retain shared random-stream progression; patched threads begin independent
identical streams and dot evaluates to zero. Verify both repeats with `verify.py`.

[The frozen evidence](../../docs/superpowers/evidence/current-patch-proof/README.md)
also includes the duplicate-name texture-root fade/reset journey and specific
activation fixtures. Its archived helpers preserve the original producer code;
new reproductions retain their own identities rather than overwrite those results.

For patch 0010, prepare `upstream without-0010 patched`, select
`docs/superpowers/evidence/current-patch-proof/fixtures/texture-roots-shapes/preset.milk`
and its containing folder for `--textures`, then add `--texture-journey`. It uses
roots `a`/`b`, switches the root at 20, starts a two-second soft cut at 21 and resets
textures at 40. The worker retains 40/59/119 PNGs as well as 29; the generic comparison
shows 119 after the transition completes, so inspect 40/59 for the lifetime defect.

New capture records identify their producer script; verification records identify
the verifier. The capture tool removes only its own hashed remote scratch directory
after pulling evidence, including on handled failures. Local records remain intact.
For a nonzero worker exit, it independently attempts to retain the engine log,
structured manifest and partial RGB stream before cleanup. It records unavailable
pulls explicitly and keeps the run failed. Raw failed streams stay in the ignored
local build directory. Verification accepts a rejected role only when both runs
explicitly failed with nonzero integer exit codes and no claimed successful repeat.

Run the evidence-integrity and failed-capture controls with:

```sh
build/patch-proof-env/bin/python -m unittest discover -s tools/patch-proof -p 'test_*.py' -v
```
