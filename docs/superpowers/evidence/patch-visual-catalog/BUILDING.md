# Reproduce the native catalog workers

Use Python3.12+, Git, CMake3.22+, Ninja, a C/C++ toolchain, SDL2 and native OpenGL. On macOS the worker uses SDL/OpenGL on the host GPU. Rendering receipts must identify the actual backend; a successful build alone does not prove hardware rendering or Native4K TV performance.

Provide read-only engine checkouts at the exact commits below, with their `vendor/projectm-eval` submodule initialized at `22fb0cfd8f2dfbcd2b68f2443e7f44e19b32c09a`:

- ProjectM TV source: `8a15996e8510533113a44e26feaddc3a7d6e85f5` (34 ordered patches).
- App engine cache: `6f64807467e312034883a4389e6aa80a675458bc`.
- Upstream master cache: `e98fca85e57802d27a6d11499642de2a1d5e994e`.

Run from any directory; replace the example paths with the checkouts and a **new** output directory:

```sh
python3 /path/to/ProjectM-TV/docs/superpowers/evidence/patch-visual-catalog/prepare_host.py \
  --repo /path/to/ProjectM-TV \
  --engine-cache /path/to/app-engine-cache \
  --upstream-cache /path/to/upstream-master-cache \
  --work /path/to/new-catalog-host \
  --jobs 6
```

The builder archives frozen tooling/patches from Git, then uses the existing Preset Lab archive-only preparation for both engines and their evaluator. Cache working-tree modifications are ignored. All patch application, deterministic clock/random instrumentation and compilation happen under `--work`; existing output directories are refused. Failed builds retain their logs and require a different output directory for a clean retry.

Both roles share the same deterministic instrumentation and harness. The sole harness adjustments guard TV-only line controls with `CATALOG_TV`, set patched `SetFeedbackDetail(-1.0f)` to disable TV feedback detail, and define `CATALOG_TV` only for the patched worker. They reproduce the catalog's native comparison controls; they do not represent production Native Standard trails.

Catalog requests use line reference width/height0/0 and antialiasingfalse; upstream has its classic line behavior and no TV feedback-detail control. Both roles receive the actual request window width/height directly, including3840×2160, without a1280×720 shader-canvas override. Preserve these request controls when reproducing the catalog.

Outputs are `<work>/{upstream,patched}/native-build/preset-lab-worker`. Each role's `identity.json` records source/evaluator pins, ordered patch hashes, original/modified harness hashes, instrumentation identity, complete instrumented source-tree digest, worker hash, builder hash and commands. `source-tree.json` retains the per-file source hashes; shared `harness-identity.json` records the exact modifications. Compiler/platform differences can change executable hashes, so a locally rebuilt binary needs its own capture receipt.

Invoke each worker with one JSON request path using the existing Preset Lab request protocol. Preserve the same preset bytes, textures, PCM, seed, clock, dimensions and line settings across roles; record request/frame hashes and actual GL backend separately. This builder does not render, select witnesses, certify visual equality or measure TV performance.
