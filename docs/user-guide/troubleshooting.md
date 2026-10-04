# Troubleshooting

## Visuals do not react to the music

Start music in the player before opening ProjectM TV. Open **Settings → Advanced → Diagnostics** and check the audio source and level.

| Audio status | Next step |
|---|---|
| No access | Grant Record audio permission to ProjectM TV |
| No player session found yet | Wait a few seconds while the app searches |
| Silent / no data | Confirm music is playing; try a verified player such as Spotify or SoundCloud |
| An active player session and changing level | Audio is reaching the visualizer; try another preset |

If no audio is found while Android reports music playing, the app searches again when the track changes with notification access, and otherwise once a minute. Encoded audio such as a Dolby bitstream arriving from a video app cannot be visualized.

## Picture stutters

Keep **Resolution** and **Transitions** on Auto, and use the default half-refresh-rate frame rate. Lower **Detail** in Advanced if the preset's equations limit the CPU. Blending two heavy presets can be slower than rendering one.

Higher resolutions use more memory. Keep Memory limit enabled, particularly on TVs with 2 GB RAM. After a memory-pressure report, automatic resolution may stay lower for the session.

## A preset looks different when revisited

Some presets choose random images from the bundled texture pack each time they load. Those choices stay fixed while the preset plays and are shared by its rendering stages. Revisiting the preset can choose other images; the renderer preserves each alias's requested filtering and edge wrapping. This does not guarantee the same appearance as MilkDrop on Windows.

## Presets skipped by an earlier version

Earlier versions skipped presets whose equation code projectM could not compile, including 27 bundled presets. The app now loads equation code like MilkDrop does, so these presets play. A code block that MilkDrop cannot compile either is left out and the rest of the preset plays, as in MilkDrop. Presets skipped earlier stay on this TV's skip list until you reset it: **Advanced → Skipped presets**. A reset also clears presets skipped as slow or black; the app skips those again if they still are.

## Fewer than 500 Dance presets are available

The collection packages 500, while the eligible count excludes this TV's skipped presets. **Advanced → Skipped presets** shows the skip count and lets you reset the list. Failed or consistently slow presets can be skipped again on that device.

## Dance is unavailable

The app falls back to **All** when a selected category has no eligible members. The full library remains available, subject to the same skip rules.

## Track titles are missing

Open **Track display → Track info → Configure**, then enable ProjectM TV in Android's notification-access settings. **Dismiss** permanently hides the automatic reminder; Track display still reopens setup. See the [screenshot walkthrough](getting-started.md#track-titles). The app reads the player's media session for titles. Titles are optional and do not control visualizer audio capture.

If the artist and title appear but the cover does not, the music app may not provide one. Covers have only been verified with Spotify and [Milkbeat](https://github.com/johnneerdael/Milkbeat); SoundCloud and SmartTube show the artist and title only.

## Updating a debug build fails

A production release and a locally built debug APK use different signing keys. Use the [separate preset-test app](development.md#test-on-a-tv-without-replacing-the-release) for development without replacing your production installation.

For unresolved problems, include the app version, device, Android version and relevant diagnostics in a [GitHub issue](https://github.com/johnneerdael/ProjectM-TV/issues).

## A preset looks different from MilkDrop

Some presets can fall back to a simpler shader when their custom shader cannot compile. The engine includes fixes for local variables named `sample`, declaration and statement macros, and swizzles after parenthesized constructors. These fixes leave the preset files unchanged. Passing parser and compiler checks does not establish identical appearance across GPUs; include the preset name, device and app version when reporting a difference.
