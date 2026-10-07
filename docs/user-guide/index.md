# ProjectM TV

**ProjectM TV** turns the music playing on your Android TV into MilkDrop visuals, at up to 4K. It ships **9,606 presets** and runs **ProjectM TV Engine**, a version of projectM tuned to behave like the original MilkDrop 2 and to run well on TV hardware.

![A ProjectM TV preset with the playing track's cover, artist and title](images/launch.jpg)

> **Install on your TV with the Downloader app: code `4821216`**. See [Install and get started](getting-started.md).

## Use it

- **[Install and get started](getting-started.md):** permissions, track titles, first settings.
- **[Remote controls](controls.md)** and the **[settings reference](settings.md)**.
- **[Preset moods](predictive-collections.md) (beta):** Chill, Normal and Intense, with example captures.
- **[Custom preset packs](custom-packs.md):** upload up to 50,000 of your own presets from a phone.
- **[Picture quality and performance](picture-quality.md):** resolution, Native trails, transitions, device tiers.
- **[Troubleshooting](troubleshooting.md)**.

ProjectM TV listens to the music app's own audio session. It never uses the microphone, stores no audio, and connects to the internet only if you enable auto-update.

## What makes it different

**Presets that work.** MilkDrop presets were written for Windows and Direct3D 9. Many fail or look wrong in other players because of equation syntax MilkDrop tolerated, HLSL its compiler accepted, or pixel rules that differ between Direct3D and OpenGL. ProjectM TV Engine carries [13 patches](engine/patches.md) that restore MilkDrop 2's behaviour, each proven with before/after captures.

**4K without the darkness.** At 4K, MilkDrop's one-pixel lines and pixel-sized blurs shrink to a fraction of the picture they covered on the author's screen, and many presets go dark. ProjectM TV scales lines, blur and texel steps to their authored size, and keeps feedback trails on an authored-scale canvas while drawing new geometry sharply at native resolution. Read [Rendering MilkDrop at 4K](engine/resolution.md).

**Built for a TV box.** Shaders compile in the background, so preset changes don't freeze the picture. Resolution adapts to frame rate and free memory, protecting the music app. Blends adapt to whether the GPU or the CPU is the limit. Read [How a frame reaches your TV](engine/pipeline.md).

**Presets understood from their source.** This project has analysed every bundled preset: parsing it, translating every shader, and running it under controlled audio. It is now learning to predict a preset's behaviour from its code alone. In a randomized test, behaviour predicted from source matched the rendered result almost exactly for 85 of 100 presets. Read [The road ahead](predictor.md).

## Write presets

The **[preset authoring section](authoring/index.md)** documents how a `.milk` preset really executes, from MilkDrop 2's source code and the analysis of thousands of real presets:

- the [file format](authoring/milk-format.md) and the [order of each frame](authoring/execution.md);
- [equation semantics](authoring/equations.md), [shaders](authoring/shaders.md) and [textures](authoring/textures.md);
- [motion, waves, shapes and blur](authoring/effects.md);
- [how to test and predict presets](authoring/testing.md), and a [checklist](authoring/checklist.md) of mistakes found in real presets.

## Under the hood

- [ProjectM TV Engine](engine/index.md): lineage, design rules and the patch series.
- [Validation and evidence](engine/validation.md): how changes are proven, and what the proofs do not cover.
- [Build and test](development.md): building the app, using the engine in another app, and the test suites.

ProjectM TV is open source (LGPL-2.1), and the presets and textures are CC0. Its engine also powers **[Milkbeat](https://github.com/johnneerdael/Milkbeat)**, a music player for Android TV by the same author, which plays local files, network shares and streaming services with MilkDrop visuals.

[Project on GitHub](https://github.com/johnneerdael/ProjectM-TV) · [Releases](https://github.com/johnneerdael/ProjectM-TV/releases) · [Report an issue](https://github.com/johnneerdael/ProjectM-TV/issues)
