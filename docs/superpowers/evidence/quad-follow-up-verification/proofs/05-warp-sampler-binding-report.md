# Custom warp sampler binding evidence

Candidate: `0026-custom-warp-sampler-binding.patch`. Tests: `check.py`.

Only scratch files changed. No commits, pushes, devices, or production edits.

## Proven root cause and limits

Patched-25 `PerPixelMesh.cpp:341` calls `LoadVariables()`, then lines 354 and 365 bind main texture and a linear sampler at unit 0. Its wrapping follows the evaluated per-frame `wrap` value (including `bTexWrap` and per-frame expression changes). This override is intentional for unqualified `sampler_main`.

`MilkdropShader.cpp:527` always inserts `main` into the sampler-name set; lines 68–86 build main descriptors in set order and lines 314–322 bind those descriptors sequentially. Explicit aliases that sort before `main` therefore occupy unit 0 and lose their requested sampler mode. Only the first main descriptor is overwritten; later descriptors survive.

Driver-confirmed affected names: `fc_main` and `cf_main` clamp become wrap when `bTexWrap=1`; `fw_main` wrap becomes clamp when `bTexWrap=0`; `cp_main` point/clamp becomes linear and may also wrap. Their rendered output incorrectly depends on `bTexWrap`. `pc_main`, `pw_main`, `wf_main`, and `wp_main` alone sort after `main` and are already correct. Only the listed lowercase aliases and mixed canonical main are tested here. Capitalization is untested; no universal claim is made. This is a unit-order bug, not a blanket failure of all explicit samplers.

Mixed shaders expose a second consequence of the same root cause: unqualified `sampler_main` is shifted to a later unit and no longer follows `bTexWrap` when an earlier explicit name exists. The mixed test proves both bindings after correction.

`FinalComposite.cpp:140–142` loads descriptors and draws without an intervening override. All sixteen explicit composite sampler cases pass on baseline and remain byte-identical with candidate. No separate composite correction is warranted.

## Minimal correction

Insert the exact implicit `main` descriptor at the beginning of `m_mainTextureDescriptors`; append named aliases normally. Unit zero is reserved for the existing warp override. The production correction changes one descriptor-order block in `MilkdropShader.cpp`; no sampler API, default bind, or shared sampler state changes. The final patch also includes `WarpSamplerTest.cpp` and its `tests/libprojectM/CMakeLists.txt` entry.

## Real driver and rendering verification

Driver: Apple M4 Pro, OpenGL `4.1 Metal - 89.4`. Width 128, height 96, 30fps, two frames, seed 42, silence PCM. Private deterministic worker sources use pinned projectM `e0b0a967f0ffd7d332106c366668ed271718472b` plus patches 1–25 and the pinned evaluator, through the existing worker builder. Candidate adds patch26 only to its private source. `source-path.txt` preserves these snapshots for subsequent builds even when the parent's patch series changes.

The warp fixture seeds an asymmetric RGB gradient/stripe pattern at time <0.05s, then samples with a fractional texel shift and outside the right edge. Composite fixtures sample that same analytic seed. Driver probes run immediately before actual warp/composite draws, query active sampler uniforms and unit bindings, and read wrap S/T plus min/mag filters. They restore active texture state. Manifests prove zero GL error frames for every baseline and candidate case.

The RED run has 14 expected failures in 38 cases: wrong named warp state, rendered dependence on preset wrap, semantic alias image mismatches, and mixed-main wrapping. GREEN has zero failures in the same 38 cases. GREEN additionally checks byte identity against baseline for all sixteen composite images, unaffected explicit aliases, unqualified main-only custom shaders (wrap on and off), and the nonempty fixed warp/default pipeline (wrap on and off).

Point/clamp `cp_main` candidate images match already-correct `pc_main` exactly. Wrap `fw_main` candidate images match already-correct `wf_main` exactly. Alias equality and independence from `bTexWrap` are rendered semantic assertions, alongside literal driver-state expectations.

Evidence: `red/results.json`, `green/results.json`, per-case `stderr.log`, `manifest.json`, `frames.npy`, and `frame2.ppm`. `contact-sheet.png` shows four affected cases; `image-impact.json` records observed pixel differences. At wrap=0, the point/clamp correction changes 12,236 of 12,288 pixels, with mean absolute RGB byte difference 8.498 and max 61. Clamp/wrap corrections affect the expected out-of-bounds edge region (2,794 pixels in this fixture). These are synthetic fixture results, not performance claims or preset-quality measurements.

## Reproduce

Run from the owning worktree root:

```sh
build/preset-lab-venv/bin/python build/follow-ups/sampler-binding-review/check.py build red
build/preset-lab-venv/bin/python build/follow-ups/sampler-binding-review/check.py test red
build/preset-lab-venv/bin/python build/follow-ups/sampler-binding-review/check.py build green
build/preset-lab-venv/bin/python build/follow-ups/sampler-binding-review/check.py test green
build/preset-lab-venv/bin/python -m pytest tools/preset-lab/tests -q
```

RED exits 1 with 14 assertion failures; GREEN exits 0 with no failures. Existing suite: 158 passed, 3 skipped in 14.19s. The skips belong to existing environment-gated native tests, not this real-driver regression.

Not validated here: Android GLES/TV hardware or broad real-preset visual impact. Parent owns those comparisons and integration review. No unrelated texture-binding issue is inferred from these results.

## Durable integrated engine regression

The final patch adds six tests to `projectM-unittest`. They render through the public `ProjectM` API into an RGB8 framebuffer with one CGL context for the suite. Warp fixtures seed with `if (frame < 2)` during zero-indexed frames 0 and 1 and sample during frame 2, requiring no real-time delays or private instrumentation. Aliases have identical requested behavior, explicit modes must ignore preset wrap, unqualified main must follow preset wrap, and mixed output must match the independently rendered reference average within one byte. The fixture explicitly proves that wrap and point/linear filtering produce different images. A nonempty fixed warp scene must exactly match unqualified pass-through. Composite samplers provide the unaffected control.

Fresh uninstrumented sources (pinned upstream plus patches 1–25) produce RED failures in exactly three of six tests: `ExplicitModesIgnorePresetWrap`, `EquivalentAliasesHaveIdenticalFilteringAndWrapping`, and `MixedMainAndExplicitClampMatchIndependentReferences`. The three controls pass. With the code correction, GREEN is six passed, zero skipped. Full integrated host suite: 163 passed from 18 suites, zero skipped. Build and test artifacts live in `host/red/` and `host/green/`; `test.log` preserves focused red/green output and `host/green/suite.log` preserves the full run.

```sh
build/preset-lab-venv/bin/python build/follow-ups/sampler-binding-review/host.py build red
build/preset-lab-venv/bin/python build/follow-ups/sampler-binding-review/host.py test red
build/preset-lab-venv/bin/python build/follow-ups/sampler-binding-review/host.py build green
build/preset-lab-venv/bin/python build/follow-ups/sampler-binding-review/host.py test green
build/preset-lab-venv/bin/python build/follow-ups/sampler-binding-review/host.py suite green
```

The host preparer filters the parent patch series to 1–25 even after patch26 is integrated. It applies test-only changes to RED and the full candidate to GREEN. Non-Apple builds or unavailable CGL contexts explicitly skip these six rendering tests; those environments have not validated their rendering assertions.

The standalone trace checker and copied red/green worker executables are also exported under `export/`. Its `base-path.txt` retains the owning repo path and `red/source-path.txt` / `green/source-path.txt` retain frozen original source locations. Running the exported tests again gives RED 14 failures and GREEN zero failures across 38 cases, independently of the current parent patch series.
