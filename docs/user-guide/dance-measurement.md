# Historical Dance measurement

> This article preserves the earlier Dance experiment. The current app ships the [predictive preset engine beta](predictive-collections.md) with All, Chill, Normal and Intense. Dance is no longer an available collection, and the old import commands below do not produce the current bundle.


Dance is a collection of 500 existing MilkDrop presets selected for large bass-caused changes on screen. It does not modify their equations or shaders. **All remains the default**, using the full library; choosing Dance restricts automatic, random and previous selections to the collection, subject to the TV's existing skip rules.

The selection is automatic. Finding `bass` in a preset is useful for understanding its code, but cannot establish visible response strength: the value may affect an invisible element, be overwritten, saturate, or interact with shader branches and feedback. We execute the complete preset with the app's patched projectM engine and measure the rendered result.

## Controlled experiment

The offline worker uses a fresh process and OpenGL context for each condition, a synthetic frame clock and fixed random seeds. Texture enumeration is stable. Presets run at **256 × 144, 30 fps, seed 12345**, with **four seconds of warmup followed by twenty seconds of measurement**.

Each preset receives five runs:

1. A steady carrier, comprising 80 Hz, 440 Hz and 5 kHz tones, each at amplitude 0.04.
2. An identical repeat of the carrier to check repeatability.
3. Carrier plus bass bursts at amplitude 0.05.
4. Carrier plus bass bursts at amplitude 0.15.
5. Carrier plus bass bursts at amplitude 0.30.

The bass source is deterministic noise filtered to 20–250 Hz and normalized by its maximum absolute sample. Bursts occur once per second, with a 10 ms attack and 120 ms exponential decay. Applying that envelope introduces modulation sidebands. The complete signal is not independently normalized between conditions. PCM is mono float32 at 44.1 kHz.

All conditions have byte-identical audio before the intervention. We require byte-identical rendered warmup images, and identical complete images for the repeated carrier. A render failure, compatibility warning or repeatability failure produces **unknown**, with no strength score. Unknown is an evidence state, not a claim that the preset cannot react to bass.

## Measuring what changes on screen

For pixel `p` at measured frame `t`, let `B` be its rendered RGB channels with the bass intervention, and `C` its channels in the matched carrier control. Channels are 8-bit output values.

```text
d(p,t) = (|B_R - C_R| + |B_G - C_G| + |B_B - C_B|) / (3 × 255)
M(t)   = mean over all pixels of d(p,t)
A(t)   = fraction of pixels where d(p,t) > 8/255
I(t)   = mean d(p,t) within that affected area
```

`M` combines how much the pixels change with how much of the screen changes. A tiny white element covering 1% of the screen can contribute at most 0.01, even if it changes completely. An effect covering half the image with average RGB difference 0.60 contributes approximately 0.30. Unrelated animation that renders identically in the control contributes zero.

This measures output difference, including color, brightness, geometry and feedback effects. It is not optical-flow distance, physical loudness, a perceptual color metric or a probability of suitability.

For each bass amplitude we take the **95th percentile of `M(t)`** over the measured window. The ranking score is the arithmetic mean of those three values. This favors a substantial upper range of response rather than a single exceptional frame. Very brief flashes can be underrepresented by that percentile.

We also retain mean magnitude, affected area and local intensity at a representative upper-response frame, mean affected area, first-second magnitude, and the first response delay. Delay has frame-scale resolution: at 30 fps, roughly 33 ms. These fields help distinguish an immediate kick effect from a large difference that develops through feedback. A high sustained score can coexist with a weaker first hit.

## Selecting 500

Collection size is separate from a strongest-response threshold. We select the highest-ranked 500 eligible measurements under one verified experiment identity; this does not label all 500 equally strong. Ties are resolved by filename. Original memory weights are copied from the authoritative master index.

The first screening pass attempted all 9,606 presets on the then-current renderer. Before release, shortlisted candidates are revalidated on the production renderer when its patches change. The bundle records that candidate coverage explicitly. A shortlist revalidation is not a claim that every preset was rerendered with the newer engine, or that the resulting order is optimal for every song or GPU.

## Cache identities and reproducibility

Measurements are reusable without manual reanalysis. Their identities include:

- Preset content and filename.
- Native worker binary, pinned projectM commit, app patches and instrumentation.
- Texture content.
- Generated audio content.
- Resolution, frame rate, seed and timing.
- Measurement implementation.

Selection rejects incompatible experiments, stale presets, incomplete conditions and non-finite scores. New or changed presets can be measured separately; a library update does not require relabelling unchanged presets by hand. Renderer, signal or measurement changes require fresh compatible evidence.

`manifest.json` records the library and experiment provenance. `presets.jsonl` records rank and screen measurements. `genres/dance.idx` contains exact filenames and master memory weights. Checksums and membership checks prevent the index, evidence and catalog from silently diverging.

Raw framebuffer captures are streamed for comparison and discarded after measurement. Keeping numerical results makes ranking cheap, but cannot reconstruct a new motion or flashing metric later. A Chill collection therefore needs additional measurements rather than interpreting weak bass response as calm movement.

## Reproduce or expand the collection

Install [Preset Lab](https://github.com/johnneerdael/ProjectM-TV/tree/main/tools/preset-lab) in a separate Python environment. Its README documents native build dependencies and the test-app workflow.

```sh
preset-lab bass-screen --repo . --work build/preset-lab/bass-screen
preset-lab bass-select --repo . --measurements build/preset-lab/bass-screen/measurements --count 500 --destination build/preset-lab/dance-selection --dance-only --import
```

Use repeated `--preset 'Exact filename.milk'` arguments for a subset or `--priority` to check candidates first while scanning the full library. Use `--worker` to reuse a particular native build. Exporting a completed subset remains labelled partial library coverage unless compatible evidence covers the complete current library.

## TV integration and validation

Changing category clears navigation history and stale prefetched choices. The GL thread applies the request, loads an eligible member with a hard cut and only then acknowledges completion. Failed loads are skipped and retried in bounded batches across frames. An unavailable category falls back to All. Existing memory weights and device-specific skip behavior still apply.

Regression tests cover tiny elements versus whole-scene effects, intrinsic animation, real bass-sensitive shaders, repeatability, cache invalidation, source changes and bundle integrity. Native and Android tests check category membership, random selection, switching and fallback. A live UGOOS test verified audio delivery while Dance was selected; that establishes operation on that device, not causal strength for every selected preset on every GPU.

No music recordings or raw captures are shipped in the app. Selection describes the stated signals, timing, seed, resolution and renderer. It does not guarantee response across all songs, starting states or hardware, and does not assign aesthetic quality or certify non-flashing behavior.
