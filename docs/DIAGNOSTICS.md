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

The first connection shows an *Allow debugging?* prompt on the TV; accept it with the remote. The script captures the foreground Android user ID once, records it in the summary, and uses it for installation, permission grants, notification access, stopping/starting the app and process lookup. Keep that user in the foreground throughout the run. An APK update replaces shared package code even when installation targets one user.

| Option | Effect |
|---|---|
| *(default)* | Builds the release APK from this checkout, installs it and observes it for 180 s |
| `--release` | Installs the latest GitHub Release instead of building |
| `--apk PATH` | Installs the supplied APK; its application ID must match `--package` (or the default ID) |
| `--no-install` | Tests the version that is already installed |
| `--package ID` | Application ID to test (default `nl.neerdael.projectmtv`). Alternate IDs require a matching `--apk` or `--no-install`; building and `--release` only support the default ID |
| `--allow-uninstall` | Attempts signing-key recovery by uninstalling only for the captured Android user (resets that user's app settings); refuses if another user has the same package or that state cannot be verified |
| `--sweep` | Also measures each fixed resolution (720p, 1080p, …), driving the menu with key events |
| `--duration SEC` | Observation time (default 180) |

For an already installed profile build, run:

```bash
tools/tv-diagnostics.sh 192.168.50.105:5555 --package nl.neerdael.projectmtv.profile --no-install
```

To install a newly built profile APK instead, replace `--no-install` with `--apk app/build/outputs/apk/profile/app-profile.apk`. The script does not inspect supplied APKs to verify their application ID; supply an APK that matches the package being tested. Incompatible build/`--release` and package combinations fail before connecting to the TV, building, downloading or installing anything. If multiple APK-source options are supplied, the last one selects the mode; the package check uses that final mode regardless of option order.

On a signing-key conflict, `--allow-uninstall` checks `pm list users` and each other user's `pm list packages --user <userId>` before removing any app data. Another user's installation, including a stopped user's, retains shared package code and its signing key; the script refuses recovery in that case. Failed or malformed queries also stop before uninstalling. Use `--no-install` to measure the existing app or supply an APK signed with its installed key. If Android still retains an incompatible package after an allowed user-scoped uninstall (for example a preinstalled package), the retry fails explicitly; the script never broadens removal to all users.

## What it collects

| File | Content |
|---|---|
| `summary.md` | Device and GPU, panel/UI size, cold start and observation start times, FPS (app and SurfaceFlinger), resolution decisions, sweep table, preset load times and transition FPS, output measurements, memory limit and other apps killed for memory, surface composition, skipped presets, crashes |
| `app_log.txt` | App log lines (`STATS`, `STARTUP`, `LOAD`, `TRANSITION`, `OUTPUT`, `SKIP`, `QualityController`, crashes) |
| `am_start_cold.txt`, `am_start.txt` | `am start -W` output of the cold start and of the start that is observed |
| `device.txt` | System properties, display modes, CPU, memory, GLES driver |
| `screen_*.png` | Visuals, main panel, Advanced panel |
| `raw_logcat.txt`, `raw_surfaceflinger.txt` | Full dumps (git-ignored) |

### App log lines used by the script
- `VisualizerRenderer: STATS fps=59.8 surface=2560x1440`: every 5 s.
- `ProjectMTV: Audio source now: player session N|none`: the player session the Visualizer listens to, after each change. Without these lines no player session was found.
- `ProjectMTV: Player session search: …`: each search, with the session found (or *nothing playing*), how many ids were probed and how long it took.
- `projectM-Native: STARTUP first preset shown 212 ms after engine creation`.
- `projectM-Native: Indexed 9794 presets (3 skipped) in 84 ms from presets.idx`.
- `projectM-Native: LOAD preset='…' ms=412 smooth=0 size=2240x1260 weight_mb=33 shader_kb=4.6 loops=2 avail_drop_mb=61 rss_growth_mb=12`: every preset switch.
  - `ms` is the stall (parse, textures, shader compile) during which the picture freezes.
  - `weight_mb` is the preset's estimated extra memory from `presets.idx`.
  - `shader_kb` / `loops` are the size of its warp and composite shaders and their loop count.
  - `avail_drop_mb` / `rss_growth_mb` are how much the system's available memory fell and the app grew during the load. They show which presets cause memory peaks at a switch.
- `projectM-Native: Preset load failed (): Could not parse preset data.`: projectM could not load the preset; the app skips it for good on this TV.
- `projectM-Native: Preset code left out (name.milk): Could not compile per-pixel code: syntax error, unexpected '*', expecting '(' (line 12, column 12)`: an equation block that does not compile, left out like MilkDrop does; the preset still plays. The line is the number of the preset's code line (e.g. `per_pixel_12`); an unexpected end of file is reported one line past the block's last line.
- `projectM-Native: TRANSITION preset='…' mode=lightweight load_ms=412 fps=48.2 blend_fps=58.9 before_fps=59.9 frames=… slow_frames=2 worst_ms=431`: when a transition ends. `fps` includes the load, `blend_fps` excludes it, `slow_frames` counts frames over 50 ms.
- `projectM-Native: TRANSITION auto: classic blend ran at …`: Auto switched to lightweight transitions.
- `projectM-Native: OUTPUT preset='…' samples=18 luma_range=3..9 change_pct_min=0.4 change_pct_avg=1.1 region_pct_min=2.0 luma_changes=… hue_only_changes=… flat=18/18 still=17/17 skipped=no`: what a preset showed while music played (see *Output measurements* below).
- `projectM-Native: SKIP preset='…' reason=…`.
- `QualityController: …`: dynamic-resolution decisions, including `Memory pressure …` when Android asks apps to free memory.
- `ProjectMTV: Memory limit: render height up to 1260 (RAM 1941 MB)` (or `Memory limit: off`). The sweep only covers the levels up to this limit; turn *Advanced › Memory limit* off first to sweep up to the render height cap.
- `ProjectMTV: Render height cap: 1330 (panel height 2160)`: the highest render height the app uses (`QualityController.RENDER_HEIGHT_CAP`); the sweep stops there too.

### Cold start

The app's notification listener (`TrackListenerService`, needed for track titles) is rebound by Android about a second after `am force-stop`, and that starts the app's process again. A plain stop-and-start therefore measures a warm start in an already running process. The script instead:

1. disallows the app's enabled notification listeners (`cmd notification disallow_listener`),
2. force-stops the app for the captured user and waits up to 10 s until that user's process is gone,
3. runs `am start --user <userId> -W` and allows that user's listeners again right away (also on exit or Ctrl-C),
4. records the `TotalTime` and whether a new process started for the activity: no process before the start and an `ActivityManager: Start proc <pid>:<package>/… for …activity` line (on Android 10+ also `LaunchState`).

*Startup › Cold start* says *cold start* only when step 4 found a new process for the activity (the `Start proc` line, or `LaunchState: COLD`). It says *unverified* when neither is available, and otherwise names why the time is not a cold-start time. The cold-started process had no listener access, so the script stops it and starts the app again for the observation (*Observation start*, normally warm).

The foreground user is resolved with `am get-current-user` once. Listener reads use `settings --user <userId>`; `cmd notification allow_listener` and `disallow_listener` receive that same numeric ID as their final argument, including during cleanup. Process lookup uses `ps -A -o UID,PID,NAME`, matching the exact package process name and Android user (`UID / 100000`); another user's same-named process cannot affect cold-start evidence or app-log filtering. A failed user lookup, unavailable/malformed process table or ambiguous process match aborts instead of treating it as no process. These APIs were checked against Android 9 and 14 sources; availability on older Android versions was not verified.

If notification access cannot be read, the script leaves the listener alone, so Android may restart the app and the start is reported as warm or unverified. If the script is killed with `kill -9`, restore notification access using the numeric Android user shown in the run: `adb -s <tv>:5555 shell cmd notification allow_listener <package>/com.example.projectm.visualizer.TrackListenerService <userId>`.

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
