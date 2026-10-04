# SHIELD / Tegra verification

Prepared for the quad-lines follow-up to PR #14. No device operation has been run.

The locally built profile APK is `build/follow-ups/apk-verify-repo/app/build/outputs/apk/profile/app-profile.apk`,
package `nl.neerdael.projectmtv.quadverify`. It installs alongside the existing app and uses the same
release optimisation. `device-build.json` records its SHA-256 and source commit.

Verification-only changes live in that scratch repository:

- `debug.projectmtv.verify.line_mode`: `classic` uses reference 0; `unit` sets the reference to the actual render size,
  producing 1 px quads; `milkdrop` uses the production 1024×768 reference.
- The preset pin takes precedence over resume in this test app, so restarting can compare the requested preset.
- `projectM-Verify` logs successful line/motion-vector shader links and explicit GL fallback after rejection.

## Connect and record

Ask for approval before using the device. The user must turn the TV on; never remotely wake it.
Enable USB debugging on the SHIELD and authorize the computer. Use a wired ADB connection.

Set `SERIAL` to the connected SHIELD serial and `APK` to the built file above. Use that serial on every command.
Record device model, Android version, GPU, panel/UI/render sizes, installed production version and existing
`debug.projectmtv.*` values before changing anything. Leave the production app and music-player settings intact.

```sh
adb -s "$SERIAL" install -r "$APK"
adb -s "$SERIAL" shell pm grant nl.neerdael.projectmtv.quadverify android.permission.RECORD_AUDIO
adb -s "$SERIAL" shell setprop debug.projectmtv.preset 'Geiss - Surface (1-02 Version)'
adb -s "$SERIAL" shell setprop debug.projectmtv.verify.line_mode classic
adb -s "$SERIAL" shell am start -S -n nl.neerdael.projectmtv.quadverify/com.example.projectm.visualizer.MainActivity
```

In the verification app choose fixed 1080p and 60 fps, then repeat at 720p. Diagnostics must confirm the
actual render size before accepting a run. Silence is required for the flat-line tie check.

## Pixel-border and shader check

Capture the flat line in `classic`, then restart in `unit` at the same fixed size:

```sh
adb -s "$SERIAL" exec-out screencap -p > classic.png
adb -s "$SERIAL" shell am force-stop nl.neerdael.projectmtv.quadverify
adb -s "$SERIAL" shell setprop debug.projectmtv.verify.line_mode unit
adb -s "$SERIAL" shell am start -S -n nl.neerdael.projectmtv.quadverify/com.example.projectm.visualizer.MainActivity
adb -s "$SERIAL" exec-out screencap -p > quad-unit.png
adb -s "$SERIAL" logcat -d -s projectM-Verify projectM-Native VisualizerRenderer > shader-and-render.log
```

Compare the lit row in a lossless crop at equal panel coordinates; retain the full screenshots and render-size logs.
Check a continuous row, endpoint coverage and pixel-border tie direction at both 1080 and 720.
Require successful link logs for both line programs, and confirm the production-reference mode visibly scales lines.
A screenshot matching classic alone is insufficient: it could be the shader-failure fallback.

The shell screenshot is the display composition. If the SHIELD scales a different-size surface into it,
the tie check must account for that scale or use a render-buffer capture; do not infer a native pixel-row decision
from a resampled screen image.

## Frame rate

Use fixed 1080 and 720, 60 fps, stable audio, the same preset and render size in each mode. Pin:

- `$$$ Royal - Mashup (103)`;
- `TonyMilkdrop - I Like Cartoon`;
- `fat cancer tour meant t nz+`;
- `Flexi - alien complex 03`.

For each preset alternate `classic,milkdrop,classic,milkdrop`; restart the test app after changing the pin/mode.
Wait 25 seconds, then retain 60 seconds of `VisualizerRenderer: STATS`. Report mean and range, audio activity,
shader-link results and actual render size. The result compares the whole reference-sized rendering behaviour,
including blur/sample/texsize rules, not an isolated line-GPU cost. Repeat outliers.

## Cleanup

Stop the verification app, restore previously recorded debug-property values (or clear properties that were empty),
and remove only this verification package if approved. Leave the TV power state, production app and music player intact.

```sh
adb -s "$SERIAL" shell am force-stop nl.neerdael.projectmtv.quadverify
adb -s "$SERIAL" shell setprop debug.projectmtv.preset '""'
adb -s "$SERIAL" shell setprop debug.projectmtv.verify.line_mode '""'
```

If either property originally had a value, restore that value instead of the empty example above. Verify cleanup
with `getprop`; keep the evidence and worktrees.
