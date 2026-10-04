# Profiling on a TV

The `profile` build type is the release build (same native optimisation, `RelWithDebInfo`), signed with the local debug key, installed as `nl.neerdael.projectmtv.profile` next to the real app, and marked `profileable` so simpleperf can record it from the shell (Android 10+).

```sh
./gradlew assembleProfile
adb -s <tv>:5555 install -r app/build/outputs/apk/profile/app-profile.apk
adb -s <tv>:5555 shell pm grant nl.neerdael.projectmtv.profile android.permission.RECORD_AUDIO
adb -s <tv>:5555 shell am start -S -n nl.neerdael.projectmtv.profile/com.example.projectm.visualizer.MainActivity

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

## Fixed settings for a benchmark

To compare builds at a fixed render height, set the profile app's settings directly (root shell on the TV; the release app's settings stay untouched). `L` is the app's notification listener; it is disallowed only while it is enabled, and allowed again only in that case, so notification access ends up as it was:

```sh
a() { adb -s <tv>:5555 shell "$@"; }
P=nl.neerdael.projectmtv.profile
L=$P/com.example.projectm.visualizer.TrackListenerService
ON=$(a settings --user current get secure enabled_notification_listeners | tr ':' '\n' | grep -cxF "$L")
[ "$ON" = 1 ] && a cmd notification disallow_listener $L
a am force-stop $P
a pidof $P                            # must print nothing before the write
# write /data/data/$P/shared_prefs/projectm_settings.xml, e.g. render_height (0 = Auto, -1 = Native
# in a Native Core build),
# memory_limit=false, blank_detection_v3=false: push the file to /data/local/tmp and `cat` it over
# the old one (as root), which keeps its owner and SELinux context
[ "$ON" = 1 ] && a cmd notification allow_listener $L
a am start -n $P/com.example.projectm.visualizer.MainActivity
```

Then check that every `VisualizerRenderer: STATS … surface=WxH` line shows the requested size before using the run.

Why the listener is disallowed: Android rebinds the app's notification listener about a second after a force-stop, which starts the app's process again, and `ProjectMApplication` reads `projectm_settings` at that moment. If that happens before the write, the process keeps the previous run's settings. If it reads the file while `cat` has emptied it, it gets no settings, and its one-time migrations then save that nearly empty map over the new file, so even another force-stop before `am start` gives the defaults (Auto, 30 fps cap). Measured with alternating render heights: on an Ugoos AM6 (Android 9), 4 of 7 runs were wrong with a single force-stop and 8 of 8 right with a second force-stop after the write; on an Ugoos AM9 Pro (Android 14), 1 of 16 runs with the second force-stop still got the defaults. With the listener disallowed no app process exists during the write. Clear `debug.projectmtv.preset` afterwards if you pinned a preset.
