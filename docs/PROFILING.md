# Profiling on a TV

The `profile` build type is the release build (same native optimisation, `RelWithDebInfo`), signed with the local debug key, installed as `nl.neerdael.projectmtv.profile` next to the real app, and marked `profileable` so simpleperf can record it from the shell (Android 10+).

```sh
./gradlew assembleProfile
ANDROID_USER=$(adb -s <tv>:5555 shell am get-current-user) || exit 1
ANDROID_USER=$(printf '%s' "$ANDROID_USER" | tr -d '\r')
case "$ANDROID_USER" in ''|*[!0-9]*) echo 'Cannot read Android user' >&2; exit 1 ;; esac
adb -s <tv>:5555 install -r --user "$ANDROID_USER" app/build/outputs/apk/profile/app-profile.apk
adb -s <tv>:5555 shell pm grant --user "$ANDROID_USER" nl.neerdael.projectmtv.profile android.permission.RECORD_AUDIO
adb -s <tv>:5555 shell am start --user "$ANDROID_USER" -S -n nl.neerdael.projectmtv.profile/com.example.projectm.visualizer.MainActivity

NDK=~/Library/Android/sdk/ndk/27.3.13750724
adb -s <tv>:5555 push $NDK/simpleperf/bin/android/arm64/simpleperf /data/local/tmp/
adb -s <tv>:5555 shell /data/local/tmp/simpleperf record --app nl.neerdael.projectmtv.profile \
    -e cpu-clock -f 1000 --call-graph dwarf,16384 --duration 100 -o /data/local/tmp/perf.data
adb -s <tv>:5555 pull /data/local/tmp/perf.data
```

Symbolize with the unstripped library of the same build:

```sh
mkdir -p symdir && cp core/build/intermediates/cxx/RelWithDebInfo/*/obj/arm64-v8a/libprojectmtv.so symdir/
$NDK/simpleperf/bin/darwin/x86_64/simpleperf report -i perf.data --symdir symdir --sort dso,symbol
$NDK/simpleperf/bin/darwin/x86_64/simpleperf report-sample -i perf.data --symdir symdir --show-callchain > samples.txt
```

Notes:
- On the SHIELD, `task-clock` is not available for app profiling; use `cpu-clock`.
- Call chains break inside NVIDIA's driver (`libglcore.so`): count samples by time window, not only by complete chains.
- The background shader compiler is a `std::thread` started from the GL thread and inherits its name (`GLThread …`): tell them apart by `thread_id`.
- The app logs one `LOAD`, `PREWARM` and `TRANSITION` line per switch (`adb logcat -s projectM-Native`), which is often enough without a profile.

## Settings and resolution for a benchmark

The current renderer chooses resolution automatically from target FPS and live memory headroom. Compare app runs with the same target FPS, Native trails level, preset and music, and record the actual render-size changes. For exact fixed-size engine comparisons, use `tools/native-trails/` offscreen workers; retired `render_height` and `memory_limit` preferences do not fix the new app’s render size. Set the profile app’s current settings directly (root shell on the TV; the release app's settings stay untouched). Resolve the foreground Android user once and use that ID throughout. `/data/data` is user 0; the settings path for this run is `/data/user/<userId>/<package>/shared_prefs/projectm_settings.xml`. Keep the same user in the foreground while measuring. `L` is the app's notification listener; disallow and restore it only if that user had enabled it. Run these steps in a shell script so a failed query stops before writing:

```sh
a() { adb -s <tv>:5555 shell "$@"; }
P=nl.neerdael.projectmtv.profile
L=$P/com.example.projectm.visualizer.TrackListenerService
ANDROID_USER=$(a am get-current-user) || exit 1
ANDROID_USER=$(printf '%s' "$ANDROID_USER" | tr -d '\r')
case "$ANDROID_USER" in ''|*[!0-9]*) echo 'Cannot read Android user' >&2; exit 1 ;; esac
SETTINGS_PATH=/data/user/$ANDROID_USER/$P/shared_prefs/projectm_settings.xml
ACCESS=$(a settings --user "$ANDROID_USER" get secure enabled_notification_listeners) || exit 1
case "$ACCESS" in ''|*sage:*|*rror*|*nvalid*|*xception*) echo 'Cannot read notification access' >&2; exit 1 ;; esac
ON=$(printf '%s' "$ACCESS" | tr -d '\r' | tr ':' '\n' | grep -cxF "$L")
restore_listener() {
    if [ "$ON" = 1 ]; then a cmd notification allow_listener "$L" "$ANDROID_USER"; fi
}
trap restore_listener EXIT
if [ "$ON" = 1 ]; then a cmd notification disallow_listener "$L" "$ANDROID_USER" || exit 1; fi
a am force-stop --user "$ANDROID_USER" "$P" || exit 1
PROCESSES=$(a ps -A -o UID,PID,NAME) || exit 1
PIDS=$(printf '%s\n' "$PROCESSES" | tr -d '\r' | awk -v u="$ANDROID_USER" -v p="$P" '
    NR == 1 { if (NF != 3 || $1 != "UID" || $2 != "PID" || $3 != "NAME") exit 1; next }
    NF == 0 { next }
    NF != 3 || $1 !~ /^[0-9]+$/ || $2 !~ /^[0-9]+$/ || $2 < 1 { exit 1 }
    int($1 / 100000) == u && $3 == p { print $2 }') || exit 1
[ -z "$PIDS" ] || { echo 'App is still running for this user; do not write settings' >&2; exit 1; }
# write "$SETTINGS_PATH", e.g. native_trails=0/1/2 (Standard/Medium/High),
# frame_rate_cap=30, blank_detection_v3=false: push the file to /data/local/tmp and `cat` it over
# the old one (as root), which keeps its owner and SELinux context
restore_listener || exit 1
trap - EXIT
a am start --user "$ANDROID_USER" -n "$P/com.example.projectm.visualizer.MainActivity"
```

Then check that every `VisualizerRenderer: STATS … surface=WxH` line from this user's app process records the actual automatically chosen size. Compare time spent at each size alongside FPS; two Auto runs can choose different resolutions, so their FPS alone is not a fixed-size engine benchmark. Numeric `ps` UID/PID/NAME fields and these user-scoped commands were checked against Android 9 and 14 sources; availability on older Android versions was not verified. If a query fails, leave the settings untouched and restore notification access for the captured user before retrying.

Why the listener is disallowed: Android rebinds the app's notification listener about a second after a force-stop, which starts the app's process again, and `ProjectMApplication` reads `projectm_settings` at that moment. If that happens before the write, the process keeps the previous run's settings. If it reads the file while `cat` has emptied it, it gets no settings, and its one-time migrations then save that nearly empty map over the new file, so even another force-stop before `am start` gives the defaults (Auto, 30 fps cap). Measured with alternating render heights: on an Ugoos AM6 (Android 9), 4 of 7 runs were wrong with a single force-stop and 8 of 8 right with a second force-stop after the write; on an Ugoos AM9 Pro (Android 14), 1 of 16 runs with the second force-stop still got the defaults. With the listener disallowed no app process exists during the write. Clear `debug.projectmtv.preset` afterwards if you pinned a preset.

## Native trails and automatic memory checks

Use Standard/Medium/High with the same target frame rate and pinned preset. Record
`VisualizerRenderer: STATS` samples, Diagnostics’ active canvas/inactive/fallback
state, resolution changes, process memory and Android memory-pressure events.
Medium/High use the same detail passes; their gain differs. Use the offscreen
workers for serialized engine mean/p90 times at a fixed size.

For a live run, verify `dumpsys media_session` reports the music player in state 3
before and after testing, and track that player’s process. Automated resolution
can react to FPS and memory; the measured result must state actual resolution,
level, audio, device and elapsed interval. Never report emulator timings as TV
app FPS, or guest PSS as all GPU texture memory. Restore task properties and
the profile app’s preferences after the run, and never wake a TV remotely.
