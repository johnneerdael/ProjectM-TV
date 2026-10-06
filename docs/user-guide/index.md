# ProjectM TV user guide

ProjectM TV visualizes music another app plays on Android TV. It uses **ProjectM TV Engine**, our extensively modified fork of projectM based on unreleased projectM 4.2 master, pinned to commit `6f6480746`, with 9,606 MilkDrop presets. Start music in your player, open ProjectM TV and control it with your TV remote.

The engine combines expanded preset compatibility with authored-scale feedback and native-resolution geometry and output, up to 4K. It is designed to preserve the authored look as resolution increases, with [known visual and device limits](troubleshooting.md#native-trails-look-soft-or-different). The settings panel shows **ProjectM TV Engine** and labels the upstream version separately as **Based on unreleased projectM 4.2 master**, with pinned commit `6f6480746`. This development snapshot is not an upstream 4.2 release.

![ProjectM TV showing a preset and the playing track](images/launch.jpg)

## Start here

- [Install and get started](getting-started.md)
- [Use the remote controls](controls.md)
- [Adjust settings](settings.md)
- [Choose a predictive collection](predictive-collections.md)
- [Troubleshoot audio and performance](troubleshooting.md)

## Choose the visuals

| Preset mood | What it includes |
|---|---|
| **All — default** | The complete 9,606-preset library, in shuffled order |
| **Chill** | Beta activity scores 1–30 |
| **Normal** | Beta activity scores 25–75 |
| **Intense** | Beta activity scores 70–100 |

The choice is saved. Your TV's skip list and performance checks still apply, so the eligible count can be lower than the number packaged in a collection.

This guide describes the current source, including [Native resolution and Native trails](settings.md). Standard trails is the default, and resolution is always automatic up to the panel’s native size, using target FPS and live memory headroom. The setup walkthrough uses real screenshots from an earlier isolated test installation on an Ugoos AM6; Android settings can look different on your TV. At least 2 GB of RAM is highly recommended.

## For the curious

The [predictive collections article](predictive-collections.md) explains the beta activity scores, overlapping bands, published-AAR backend and limits. [Build and test](development.md) covers the source and verification tools.

[Project and releases](https://github.com/johnneerdael/ProjectM-TV) · [README quick start](https://github.com/johnneerdael/ProjectM-TV#readme) · [Milkbeat user guide](https://johnneerdael.github.io/Milkbeat/)
