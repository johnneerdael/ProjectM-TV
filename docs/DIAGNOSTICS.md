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
| `summary.md` | Device and GPU, panel/UI size, startup times, FPS (app and SurfaceFlinger), resolution decisions, sweep table, preset load times and transition FPS, output measurements, memory limit and other apps killed for memory, surface composition, skipped presets, crashes |
| `app_log.txt` | App log lines (`STATS`, `STARTUP`, `LOAD`, `TRANSITION`, `OUTPUT`, `SKIP`, `QualityController`, crashes) |
| `device.txt` | System properties, display modes, CPU, memory, GLES driver |
| `screen_*.png` | Visuals, main panel, Advanced panel |
| `raw_logcat.txt`, `raw_surfaceflinger.txt` | Full dumps (git-ignored) |

### App log lines used by the script
- `VisualizerRenderer: STATS fps=59.8 surface=2560x1440`: every 5 s.
- `ProjectMTV: Audio source now: media capture|standard`: the source feeding the engine after each change. Without these lines the standard source (Visualizer) was used throughout.
- `ProjectMTV: Audio source: …`: media capture events (started, declined, unavailable, failed to start, stopped by the system, ended).
- `projectM-Native: STARTUP first preset shown 212 ms after engine creation`.
- `projectM-Native: Indexed 9794 presets (3 skipped) in 84 ms from presets.idx`.
- `projectM-Native: LOAD preset='…' ms=412 smooth=0 size=2240x1260 weight_mb=33 shader_kb=4.6 loops=2 avail_drop_mb=61 rss_growth_mb=12`: every preset switch.
  - `ms` is the stall (parse, textures, shader compile) during which the picture freezes.
  - `weight_mb` is the preset's estimated extra memory from `presets.idx`.
  - `shader_kb` / `loops` are the size of its warp and composite shaders and their loop count.
  - `avail_drop_mb` / `rss_growth_mb` are how much the system's available memory fell and the app grew during the load. They show which presets cause memory peaks at a switch.
- `projectM-Native: TRANSITION preset='…' mode=lightweight load_ms=412 fps=48.2 blend_fps=58.9 before_fps=59.9 frames=… slow_frames=2 worst_ms=431`: when a transition ends. `fps` includes the load, `blend_fps` excludes it, `slow_frames` counts frames over 50 ms.
- `projectM-Native: TRANSITION auto: classic blend ran at …`: Auto switched to lightweight transitions.
- `projectM-Native: OUTPUT preset='…' samples=18 luma_range=3..9 change_pct_min=0.4 change_pct_avg=1.1 region_pct_min=2.0 luma_changes=… hue_only_changes=… flat=18/18 still=17/17 skipped=no`: what a preset showed while music played (see *Output measurements* below).
- `projectM-Native: SKIP preset='…' reason=…`.
- `QualityController: …`: dynamic-resolution decisions, including `Memory pressure …` when Android asks apps to free memory.
- `ProjectMTV: Memory limit: render height up to 1260 (RAM 1941 MB)` (or `Memory limit: off`). The sweep only covers the levels up to this limit; turn *Advanced › Memory limit* off first to sweep up to the panel resolution.

### Reading the results
- **Did the music app get killed?** *Memory › Other apps killed during the run* lists processes Android stopped while they were visible, perceptible or foreground services (e.g. `com.soundcloud.android (prcp)`). Cached processes are left out, because Android kills those routinely.
- **Switch stalls:** *Preset switches* shows the load time per switch (the freeze) and FPS during transitions, per mode.
- **Output measurements:** *Candidates* lists presets that were flat or still in every sample. Compare them with what the screen showed, to choose thresholds before flat/still presets may be skipped.
- **Is 4K really shown at 4K?** Compare *Render sizes* with the *Panel* line, then check the *Surface composition* section. A render buffer of 3840x2160 composed by the hardware composer (`DEVICE`) on a 4K display mode means full-resolution output.
- **FPS:** *App FPS* is measured by the render loop; *SurfaceFlinger FPS* comes from the compositor's frame timestamps for the app's surface. The two should agree.

## Memory analysis with heaptrail

The Java heap is small (UI only); most memory is projectM's native and GPU memory. [heaptrail](https://github.com/johnneerdael/heaptrail) is still useful for catching leaked Activities or listeners across app restarts. Attach `dumpsys meminfo` for the native and GL side:

```bash
heaptrail android-capture --serial 192.168.50.105:5555 \
  --package nl.neerdael.projectmtv --out diagnostics/heap --foreground
adb -s 192.168.50.105:5555 shell dumpsys meminfo nl.neerdael.projectmtv > diagnostics/heap/meminfo.txt
heaptrail --diff-series launch.hprof restarts5.hprof restarts10.hprof \
  --native-context diagnostics/heap/meminfo.txt --diff-by bytes --top 30
heaptrail -i restarts10.hprof --find-referrers com.example.projectm.visualizer.MainActivity
```

Release builds are not debuggable. If `am dumpheap` refuses the process, capture from a debug build (`./gradlew assembleDebug`), then reinstall the release build afterwards.
