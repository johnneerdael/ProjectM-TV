# projectM Visualizer for Android TV (v1.8)

[![Android CI](https://github.com/johnneerdael/projectm-android-tv/actions/workflows/android.yml/badge.svg)](https://github.com/johnneerdael/projectm-android-tv/actions/workflows/android.yml)

A music visualization powerhouse for your Android TV, bringing the legendary projectM (an open-source reimplementation of Milkdrop) to your living room with the complete Cream of the Crop preset collection.

## Features

- **Instant start** - Visuals start as soon as the screen is up; presets are read straight from the app package, nothing is extracted to storage
- **Complete preset library** - The entire Cream of the Crop collection (9,795 presets), shuffled
- **Self-cleaning playlist** - Presets that fail to load, or render nothing while music is playing, are skipped automatically and remembered (reset from the menu)
- **Hardware-scaled rendering** - Render at 480p / 720p / 1080p / native; the TV's display scaler stretches it to full screen at no GPU cost
- **Smooth frame pacing** - Choose full refresh rate or an even half rate (30/25 fps) that stays smooth on modest hardware
- **TV-style overlay** - Compact settings panel inside the overscan-safe area; long preset names scroll
- **System audio visualization** - Reacts to any audio playing on the device
- **Remote-friendly controls**
  - **Right** - Random preset (instant cut)
  - **Left** - Previous preset (instant cut)
  - **Up / Down / Info** - Show the current preset name
  - **Center / Menu** - Open settings overlay (↑↓ select a row, ‹ › change its value)
  - **Back** - Close overlay / exit

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full design and the 1.7 regression analysis.

| Layer | Files | Responsibility |
|---|---|---|
| UI | `MainActivity`, `OptionRow`, `activity_main.xml` | Remote control, settings overlay, audio capture thread, preferences |
| Device | `DeviceProfile` | One place for device-tier defaults (render height, mesh size) |
| Rendering | `VisualizerView`, `VisualizerRenderer` | OpenGL ES 3.0 surface, hardware-scaler resolution, FPS |
| Bridge | `ProjectMJNI` | JNI bindings; everything except surface/frame calls is thread-safe |
| Engine | `app/src/main/cpp/native-lib.cpp` | projectM lifecycle, preset index/prefetch, skip list, black-frame detection |

## What is Milkdrop & the "Cream of the Crop" Pack?

### What is Milkdrop?

Imagine your music transforming into a vibrant, ever-changing universe of color, light, and motion. That's Milkdrop. At its core, it's a music visualizer, a plug-in originally created for the iconic Winamp media player, and now available for various other players like Kodi and projectM. Milkdrop uses your device's graphics power to generate intricate and dynamic visualizations that react in real-time to the beats, melodies, and frequencies of the music you're listening to. The result is a captivating and often trippy visual experience that perfectly complements your auditory journey.

### What Makes the "Cream of the Crop" Pack So Special?

With a vast and dedicated community of artists creating and sharing their own visual "presets" for Milkdrop over the years, the sheer volume of available options can be overwhelming. This is where the Cream of the Crop pack comes in as your expert guide.

Curated by Jason Fletcher, a respected figure in the Milkdrop community, this pack is a meticulously selected compilation of the "best of the best" presets. Fletcher sifted through thousands upon thousands of creations to handpick the most stunning, innovative, and awe-inspiring visuals. Think of it as the ultimate playlist for your eyes.

Boasting an incredible 9,795 presets, the Cream of the Crop pack is a testament to the creativity and technical artistry of the Milkdrop community. Its quality is so highly regarded that it has become the default preset pack for some versions of projectM, an open-source and cross-platform implementation of the Milkdrop engine.

### What to Expect from the Cream of the Crop Pack:

- **A Universe of Variety**: From pulsating geometric patterns and swirling nebulae to abstract landscapes and futuristic cityscapes, the diversity of visuals within the pack is staggering. You'll find a visual style to match any genre of music, from the most serene ambient tracks to the most frenetic electronic beats.

- **A Feast for the Eyes**: These aren't just simple loops. The presets in the Cream of the Crop pack are known for their complexity, smooth transitions, and breathtaking beauty. Prepare to be hypnotized by the intricate details and fluid animations.

- **A Gateway to a Thriving Community**: Exploring the Cream of the Crop pack is also a fantastic way to discover the work of talented visual artists and delve deeper into the world of music visualization.

## Android TV Specifics

- **OpenGL ES 3.0** - Required by projectM 4 (its shaders are GLSL `300 es`)
- **Hardware scaler** - `SurfaceHolder.setFixedSize()` renders at a lower resolution and lets the display pipeline upscale
- **Device tiers** - Low-RAM devices get a lighter per-vertex mesh; NVIDIA Shield defaults to 1080p, everything else to 720p
- **GL-thread safety** - All preset switches run on the rendering thread (projectM compiles shaders while loading presets)
- **Background work** - Preset indexing and prefetching of the next preset run on a native worker thread

### Audio

Audio is captured from the global output mix with Android's `Visualizer` API (session 0) at the maximum capture rate. The waveform is 8-bit unsigned mono PCM and is handed to projectM unchanged (`projectm_pcm_add_uint8`).

## Downloads

Every change on GitHub is built automatically; releases are published under **Releases**. See [docs/RELEASING.md](docs/RELEASING.md).

## Building and Installing

```bash
./gradlew assembleRelease          # optimized, non-debuggable APK signed with your local debug key
adb install -r app/build/outputs/apk/release/app-release.apk
```

`./install.sh` installs the release APK if present, otherwise the debug APK.

Engine logic can be tested on any Linux/macOS machine (no device needed):

```bash
app/src/test/native/run_native_tests.sh
```

Preferences are preserved when updating from earlier versions.

## Permissions

- `RECORD_AUDIO` - Required by the `Visualizer` API to capture system audio
- `MODIFY_AUDIO_SETTINGS` - Used by the `Visualizer` API

## Credits

- **ProjectM Team** - For the incredible open-source visualization library
- **Jason Fletcher** - For curating the Cream of the Crop preset collection
- **Milkdrop Community** - For creating thousands of amazing presets
- **Android Open Source Project** - For the Android TV platform

## License

This application is released under the same license as ProjectM (GPL v2).

## Usage Tips

- **Classic Milkdrop feel:** 7s transitions, ~30s preset duration
- **Dynamic show:** 10-15s presets with 2-3s transitions
- **Manual control:** Turn off auto change and use left/right
- **Stuttering?** Lower the resolution in the menu (720p or 480p); the image still fills the screen
- **Too many skipped presets?** Use *Reset* next to "Skipped presets" in the menu
