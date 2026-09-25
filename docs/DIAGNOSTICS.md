# On-device Diagnostics

`tools/tv-diagnostics.sh` collects performance and fidelity data from an Android TV over adb and writes a Markdown summary. It needs a computer on the same network as the TV, with adb, curl and awk (macOS or Linux).

## Prepare the TV
1. Enable developer options: *Settings → Device Preferences → About → Build*, press OK 7 times (Fire TV: *My Fire TV → About*, click the device name 7 times).
2. Turn on *Network debugging* / *ADB debugging*.
3. Play some music on the TV during the run, so presets react and blank-preset detection is active.

## Run

```bash
tools/tv-diagnostics.sh 192.168.50.105:5555 --sweep
```

The first connection shows an *Allow debugging?* prompt on the TV; accept it with the remote.

| Option | Effect |
|---|---|
| *(default)* | Builds the release APK from this checkout, installs it and observes it for 180 s |
| `--release` | Installs the latest GitHub Release instead of building |
| `--no-install` | Tests the version that is already installed |
| `--allow-uninstall` | If the installed app has a different signing key, uninstall it first (resets app settings) |
| `--sweep` | Also measures each fixed resolution (720p, 1080p, …), driving the menu with key events |
| `--duration SEC` | Observation time (default 180) |

## What it collects

| File | Content |
|---|---|
| `summary.md` | Device and GPU, panel/UI size, startup times, FPS (app and SurfaceFlinger), resolution decisions, sweep table, surface composition, skipped presets, crashes, memory |
| `app_log.txt` | App log lines (`STATS`, `STARTUP`, `SKIP`, `QualityController`, crashes) |
| `device.txt` | System properties, display modes, CPU, memory, GLES driver |
| `screen_*.png` | Visuals, main panel, Advanced panel |
| `raw_logcat.txt`, `raw_surfaceflinger.txt` | Full dumps (git-ignored) |

### App log lines used by the script
- `VisualizerRenderer: STATS fps=59.8 surface=2560x1440`: every 5 s.
- `projectM-Native: STARTUP first preset shown 212 ms after engine creation`.
- `projectM-Native: Indexed 9795 presets (3 skipped) in 84 ms`.
- `projectM-Native: SKIP preset='…' reason=…`.
- `QualityController: …`: dynamic-resolution decisions.

### Reading the results
- **Is 4K really shown at 4K?** Compare *Render sizes* with the *Panel* line, then check the *Surface composition* section. A render buffer of 3840x2160 composed by the hardware composer (`DEVICE`) on a 4K display mode means full-resolution output.
- **FPS:** *App FPS* is measured by the render loop; *SurfaceFlinger FPS* comes from the compositor's frame timestamps for the app's surface. The two should agree.

## Memory analysis with heaptrail

The Java heap is small (UI only); most memory is projectM's native and GPU memory. [heaptrail](https://github.com/johnneerdael/heaptrail) is still useful for catching leaked Activities or listeners across app restarts. Attach `dumpsys meminfo` for the native and GL side:

```bash
heaptrail android-capture --serial 192.168.50.105:5555 \
  --package com.example.projectm.visualizer --out diagnostics/heap --foreground
adb -s 192.168.50.105:5555 shell dumpsys meminfo com.example.projectm.visualizer > diagnostics/heap/meminfo.txt
heaptrail --diff-series launch.hprof restarts5.hprof restarts10.hprof \
  --native-context diagnostics/heap/meminfo.txt --diff-by bytes --top 30
heaptrail -i restarts10.hprof --find-referrers com.example.projectm.visualizer.MainActivity
```

Release builds are not debuggable. If `am dumpheap` refuses the process, capture from a debug build (`./gradlew assembleDebug`), then reinstall the release build afterwards.
