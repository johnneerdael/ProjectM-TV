# Visible catalog of the 18 retained audit repairs

The user guide now shows 23 lossless before/after pairs for the 18 retained repair IDs in patches 0017–0033. Patch 0021 contains two repairs; 0034 supplies the motion-field compatibility fallback rather than an additional audit ID. The older 0001–0016 catalog remains separate.

## Frozen sources and backend

| Role | Source |
|---|---|
| Before | Actual upstream master `e98fca85e57802d27a6d11499642de2a1d5e994e`, no TV patches |
| After | ProjectM TV main `8a15996e8510533113a44e26feaddc3a7d6e85f5`, all 34 patches |
| Patched engine base | `6f64807467e312034883a4389e6aa80a675458bc` |
| Evaluator, both roles | `22fb0cfd8f2dfbcd2b68f2443e7f44e19b32c09a` |
| Observed GPU | Apple M4 Pro, OpenGL `4.1 Metal - 89.4` |

Native SDL/OpenGL rendering is supported on this host, so no emulator was needed. Upstream master was archived directly from its exact Git commit. Both private engine copies receive the existing Preset Lab deterministic clock/random instrumentation. No production renderer, submodule, predictor worker, preset asset or frozen historical capture was changed.

## Protocol and observed results

Each pair uses identical preset and texture bytes, generated float32 mono audio at 44,100 Hz, seed 12345, a 48×32 mesh and 30 Hz fixed clock. Audio is the current Preset Lab tail submission (`AudioBufferSamples`, 576 on these sources), not reconstructed Android Visualizer bytes. Worker time is `(frame+1)/30`; this avoids an artificial zero-time startup singularity. The signal is:

```text
t = sample / 44100
envelope = .4 + .3 * sin(2*pi*1.7*t)^2
pcm = envelope * (.45*sin(2*pi*80*t) + .15*sin(2*pi*440*t) + .10*sin(2*pi*1600*t))
```

Output dimensions are actual 1280×720 or 3840×2160 framebuffer sizes. Line reference size is 0/0, line antialiasing is false, and patched feedback detail is explicitly -1 (off). No 1280×720 virtual-canvas override is applied to the 4K runs. Desktop framebuffer invalidation is the existing explicit no-op on Apple OpenGL. These controls compare original engine semantics without the production Native Standard-trails policy.

**26 cases, 104 successful runs, 41,280 rendered frames.** Each engine role runs twice. Every RGB frame hash matches its repeat; all run manifests report zero GL-error frames and the Apple M4 Pro renderer. Alpha is excluded. The 17 initial 720p cases run 480 frames; four supplementary controls, the motion-field diagnostic and four priority-preset 4K cases run 240. Frames 29/59/119/150/180/210/239/300/390/479 are retained when present. Selected frames are fixed in `gallery.json`, based on the earlier witness inventory and explanatory clarity rather than claiming a statistically representative sample.

The gallery contains 13 unchanged bundled originals and nine explicitly synthetic diagnostics across its main and supplementary pairs. Five main diagnostic entries cover constants, negative echo, traversal, border overlap and motion history; four supplementary diagnostics clarify aspect, host time, dots and per-instance outlines. No stock affected-preset census is claimed.

## Reading the pictures

- A whole-master versus all-patches picture includes earlier fixes too. It is not a single-patch ablation. The existing issue-specific source controls and incremental repair captures supply causal evidence; their old checkpoints are never relabelled as upstream master.
- Gamma epsilon has no demonstrated perceptible improvement in the isolated original witness. Its catalog pair is an appearance-preservation example, with an explicit limit.
- Royal103 changes substantially at 720p because the cap is active. At actual-width native 4K, both raw budgets reach 480 and the cap is inactive; that pair is nearly unchanged. Production Standard trails use a different reference canvas, so this does not overturn the earlier Standard-4K brightness observation.
- The border diagnostic also changes tint because earlier patch0014 honors fShader=0. Captions separate that hue change from patch0028 coverage. Live-style fixtures also exercise older controls absent upstream; isolated source controls establish the individual thickness correction.
- Matching zooms are CSS viewports over the original PNGs, using identical source rectangles and nearest-neighbour display. Full-resolution images remain clickable. No brightness, colour, alpha or pixel contents were edited.
- Desktop GPU captures are visual development evidence. They establish neither Windows/D3D pixel identity, physical-TV performance, Android capability fallback coverage nor a new performance benchmark. Renderer fixes are already merged in PR #65; this change documents them.

## Files and reproduction

`gallery.json` maps all 18 IDs to captions, frames and matched crop rectangles. `images.json` binds every published PNG to both file and raw-RGB hashes. `captures/` retains the exact input/role identities, every-frame hashes and difference diagnostics for all 26 cases. `run-manifests.json` retains all 104 native run manifests with explicit role/repeat labels and caller-observed preset/PCM hashes. These input hashes were bound from the preserved requests and unchanged files; they are caller observations, not additional worker telemetry. `workers.json`, the two source-tree inventories and `textures.json` identify the actual source/harness/binary/asset bytes. `fixtures/` preserves all nine synthetic preset inputs.

See [BUILDING.md](BUILDING.md) for the portable two-worker recipe. Capture a pair with:

```sh
python3 docs/superpowers/evidence/patch-visual-catalog/capture_host.py \
  --repo /path/to/ProjectM-TV --work /path/to/new-catalog-host \
  --name Happening-4k --preset '/path/to/ProjectM-TV/core/src/main/assets/presets/Happening.milk' \
  --width 3840 --frames 240
```

The original evidence uses the same algorithm; the portable adapter adds CLI arguments, refuses overwrite and checks the worker hash before/after capture. Python, compiler and package differences need new local worker/capture identities rather than reuse of these hashes.

Run the bounded artifact/document checks with Pillow available:

```sh
python3 docs/superpowers/evidence/patch-visual-catalog/verify_images.py --repo .
python3 docs/superpowers/evidence/patch-visual-catalog/test_verify_images.py -v
mkdocs build --strict
```

Both pass. Chrome presentation checks pass at the normal desktop viewport and390×844: the pairs and matched zooms render, all76 compiled image references resolve, and the narrow page has390px content width with no horizontal overflow. The disappearing-dot crop and live outline crop retain source pixels without amplification. PR/Pages publication remains a separate gate from renderer or physical-TV qualification.

PR66 review correction: the bounded verifier now requires identical run/capture/input case sets, exactly two repeats per role, matching dimensions/frame count/fps/seed, exact worker identity and preset/PCM hashes. The old same-length720p/4K manifest exchange incorrectly passed; it now fails. Six focused receipt controls pass without new renders or changes to any PNG.

Further PR66 receipt corrections: runtime texture inventories are recorded and checked before/after each future capture; preset/PCM mutations also reject. The published26 cases bind to the retained post-batch74-texture inventory, which was independently checked against exact main8a15996e bytes. These annotations do not invent retrospective per-run filesystem observations. The verifier anchors every role to workers.json and validates source-tree, ordered-patch and texture digests. Ten bounded receipt controls cover inventory tampering and joint run/capture identity drift; no images or engine binaries were regenerated.

Final filename binding: every PNG name must equal its case/role label, and its selected frame must match gallery.json. Exchanging Before/After PNGs together with their image metadata, or changing the gallery frame, now rejects. Twelve focused receipt controls pass; the lossless images are unchanged.

Repeat/fixture custody: run-manifests.json now retains all104 original independent frame-hash sequences. The verifier compares every sequence with its role capture rather than trusting repeat_equal, and binds each preset hash to a committed relative original/fixture path. Fifteen focused controls reject stale repeat flags and changed/missing fixtures. The original renders are preserved; no new capture was run. The gamma caption additionally reports overlapping valid historical emulator timings rather than claiming visible or measured performance improvement.
