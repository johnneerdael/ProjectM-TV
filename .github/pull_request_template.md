<!--
Fill in each section. Delete sections or checklist items that don't apply, and say why if it isn't obvious.
Repo rules this template checks for:
- projectM is changed only through patch files in tools/projectm-patches/, never by committing inside third_party/projectm.
- Rendering changes are compared on identical frames (preset-lab) and, where they affect what viewers see or frame rate, on a TV.
- Releases follow docs/RELEASING.md: fixes ship as a patch release, big performance or default changes as a minor release, never as a pre-release.
-->

## Summary

<!-- What changes for viewers or developers, and why. Link issues here or upstream (projectM-visualizer/projectm). -->

## Changes

-

## projectM patches

<!-- Only when tools/projectm-patches/ changes. -->

- [ ] The change is in a patch file in `tools/projectm-patches/`; nothing is committed inside `third_party/projectm`
- [ ] The patch is regenerated from the submodule (`tools/regen-projectm-patch.sh <patch>`), and its header explains the change
- [ ] `tools/check-patch-series.sh`: every patch applies to a clean export of the pinned projectM
- [ ] `tools/projectm-host-tests.sh`: projectM's host test suite passes
- [ ] Rendering that should not change didn't: `preset-lab line-compare ... --baseline <report>` shows `legacy_changed: []` (or the change is explained below)
- [ ] Shader changes link as GLSL ES 3.00 (`glslangValidator -l`, with `#version 300 es` prepended)

## Tests

- [ ] Native engine tests: `bash core/src/test/native/run_native_tests.sh` (regenerate changed patches first)
- [ ] JVM unit tests: `./gradlew testDebugUnitTest`
- [ ] Build: `./gradlew :app:assembleDebug`
- [ ] preset-lab, if `tools/preset-lab/` changed: `python -m pytest tools/preset-lab/tests`

## On a TV

<!--
For rendering, audio or performance changes. Method in docs/PROFILING.md: install the profile build next to the release app,
pin a preset with `adb shell setprop debug.projectmtv.preset '<name prefix>'`, use the same render height in both apps,
alternate release and profile runs, and read fps from the `VisualizerRenderer: STATS` log lines.
-->

- Device, GPU and Android version:
- What was checked (logcat errors, screenshots, fps before and after with the same preset, render height and audio):
- [ ] `debug.projectmtv.*` properties cleared and app settings restored afterwards

## Evidence

<!-- Before/after images, line-compare or benchmark tables. Say what was compared with what (build, render size, audio, frame). -->

## Docs and release

- [ ] README, `docs/ARCHITECTURE.md` and the user guide describe the new behaviour
- [ ] For a release: `versionCode` and `versionName` bumped in `app/build.gradle`, a section added at the top of `RELEASE_NOTES.md` (ending with `---`) and a changelog in `fastlane/metadata/android/en-US/changelogs/<versionCode>.txt`

## Not tested / known limitations

-
