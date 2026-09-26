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
mkdir -p symdir && cp app/build/intermediates/cxx/RelWithDebInfo/*/obj/arm64-v8a/libprojectmtv.so symdir/
$NDK/simpleperf/bin/darwin/x86_64/simpleperf report -i perf.data --symdir symdir --sort dso,symbol
$NDK/simpleperf/bin/darwin/x86_64/simpleperf report-sample -i perf.data --symdir symdir --show-callchain > samples.txt
```

Notes:
- On the SHIELD, `task-clock` is not available for app profiling; use `cpu-clock`.
- Call chains break inside NVIDIA's driver (`libglcore.so`): count samples by time window, not only by complete chains.
- The background shader compiler is a `std::thread` started from the GL thread and inherits its name (`GLThread …`): tell them apart by `thread_id`.
- The app logs one `LOAD`, `PREWARM` and `TRANSITION` line per switch (`adb logcat -s projectM-Native`), which is often enough without a profile.
