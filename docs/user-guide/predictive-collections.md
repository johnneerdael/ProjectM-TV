# Predictive collections (beta)

Choose **Preset mood** in the settings panel: **All**, **Chill**, **Normal** or **Intense**. All stays the default and keeps the full library available. The choice is saved; automatic changes, Random and Previous stay within your collection, subject to the TV's skip rules. Saved Dance or earlier genre choices return to All.

| Collection | Score range | Intended starting point |
|---|---|---|
| Chill | 1–30 | Lower activity and gentler viewing |
| Normal | 25–75 | Moderate activity, with room at both edges |
| Intense | 70–100 | Stronger movement and brightness changes |

Ranges are inclusive. Scores 25–30 belong to both Chill and Normal; 70–75 belong to both Normal and Intense. Original preset equations and shaders are unchanged.

This is a **beta predictive preset engine**. Scores order activity within this collection; they are not percentages of prediction accuracy. Chill is a useful starting point, not a guarantee of smooth motion or no flashes. Different songs, random images and seeds, resolutions and GPU drivers can change the result. Report a mismatch with the preset name, mood, music, device and render settings so it can be traced back to the model.

## What supplies the predictions

The numerical backend is the standard published **ProjectM-TV:core 2.3.3 AAR**, with its patched JNI renderer and bundled textures. It is not the unpatched upstream library or Preset Lab's private desktop renderer. The release commit, AAR and ARM64 native-library hashes are pinned in `tools/milk-analyzer/profiles/published-core-v2.3.3.json` and copied into the bundle manifest.

Each preset gets one load and 420 frames at 30 fps, a 128×72 GLES3 pbuffer and a 48×32 mesh. A declared clock helper supplies the test timeline; the published native library is unchanged. The first 60 frames are warm-up. A shared synthetic mono reference contains quiet tones for 0–5 seconds, a brighter melodic section for 5–9 seconds, then the melodic section plus low-frequency kick pulses for 9–14 seconds. There are no user recordings in the shipped bundle.

The standard AAR uses the **capped** rendering policy. The standard APK uses the Native-capable policy, with Auto as its resolution default. This low-resolution probe does not certify appearance or ranking at the TV's render size, including above-reference feedback compensation. The helper calls `srand(12345)`; the evaluator keeps its native thread-local Mersenne Twister seed. Shader/noise and image choices using `random_device` are not fixed by that call. One load does not sample every possible random state or image choice.

## Activity calculation

The frozen development model combines four numerical descriptors:

- Coherent brightness transitions per second, measured on all 30-fps frames. A transition needs a normalized pixel-brightness change of at least 0.1 across at least 20% of the image, plus a mean-brightness change of at least 0.1.
- Median motion in viewport widths per second, using optical flow sampled at 10 fps.
- Mean acceleration from that motion estimate.
- The 95th percentile, over 30-fps frame pairs, of their per-pixel 95th-percentile brightness change. This uses the same pixel coordinates rather than optical-flow matching.

For feature vector `x`, the raw activity is `4.3508 + sum(weight * log1p(x) / scale)`. The weights are approximately `12.5672, 27.2565, 38.1601, 12.2385`; the exact values and scales are in `audience-model-v1.json`. A paired coherent-flash proxy can raise this value. When optical flow lacks a usable result, the record explicitly identifies a temporal-change/spatial-gradient motion proxy. These are numerical activity features, not AI image labels or an independent source-only appearance prediction.

Raw activity remains unclipped. Moving/activity-bearing presets are sorted by it, equal values share an average ordinal position, and those positions are rescaled so the lowest distinct group scores 1 and the highest scores 100. This gives a relative spread rather than measuring distance in an absolute perceptual unit. Rebuilding a changed library can shift scores. A collection with no distinct activity values would receive midpoint scores.

Effects with no visible activity in the probe receive score 1 with an explicit inactive flag, remain in All and are excluded from the three curated groups. Failed or missing results cannot be exported as calm presets.

The model is a small development candidate, not an accuracy-certified audience classifier. Colourfulness, fractal structure, taste and long-term feedback evolution are not separately certified by this score. A 14-second probe can miss later behaviour.

## Evidence and reproducibility

`core/src/main/assets/preset-genres/presets.jsonl` records every preset's full source hash, native memory weight, raw activity, score, activity state and membership. `manifest.json` records beta status, model/runtime/PCM hashes, render settings, collection counts and checksums. The three index files contain original filenames and master-index memory weights. All still uses `presets.idx`.

The exporter refuses missing or failed rows, stale source or texture hashes, another AAR flavour, mismatched runtime identities or a wrong frame schedule. Its verifier recalculates ranks and memberships and compares them with the indexes. Checksums alone are insufficient to establish correct membership.

```sh
python tools/milk-analyzer/beta_export.py --check --bundle core/src/main/assets/preset-genres
python -m pytest tools/milk-analyzer/test_beta_collections.py tools/milk-analyzer/test_beta_export.py -q
```

Scoring requires an owned Android emulator, adb, NumPy/OpenCV, the published AAR and prepared Java/clock-helper artifacts. Use the [analyzer README](https://github.com/johnneerdael/ProjectM-TV/blob/main/tools/milk-analyzer/README.md) for preparation and the exact invocation. The other agent's historical corpus is supporting evidence and is not substituted for this run.

New export, after every row is resolved:

```sh
python tools/milk-analyzer/beta_export.py --run build/predictive-beta/scores --aar build/predictive-beta/core.aar --bundle core/src/main/assets/preset-genres
```

No full corpus is rendered during app use. The app reads the prebuilt indexes; subsequent scoring improvements can update them in a new release.
