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

To compare builds at a fixed render height, set the profile app's settings directly (rooted TV; the release app's settings stay untouched):

1. `am force-stop nl.neerdael.projectmtv.profile`.
2. Write `shared_prefs/projectm_settings.xml` in the app's data directory, for example `render_height` (`0` = Auto), `memory_limit=false`, `blank_detection_v3=false`. Copy the file over the old one (`cat … >`) to keep its owner and SELinux context.
3. **`am force-stop` again**, then `am start -n nl.neerdael.projectmtv.profile/com.example.projectm.visualizer.MainActivity`.
4. Check that every `VisualizerRenderer: STATS … surface=WxH` line shows the requested size before using the run.

Step 3 is needed because the app's notification listener is rebound about a second after a force-stop, which starts the app's process again, and `ProjectMApplication` reads `projectm_settings` into memory at that moment. A file written after that restart is not read: the run uses the previous run's settings, or the defaults (Auto, 30 fps) if the restart read the file while `cat` had emptied it. On an Ugoos AM6, 4 of 7 alternating 1330p/Native runs rendered the wrong height without step 3; with it, 8 of 8 were correct. Clear `debug.projectmtv.preset` afterwards if you pinned a preset.
