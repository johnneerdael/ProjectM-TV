<!--
Fill in each section. Delete sections or checklist items that don't apply, and say why if it isn't obvious.
Repo rules this template checks for:
- projectM is changed only through patch files in tools/projectm-patches/, never by committing inside third_party/projectm.
- Rendering changes include before/after captures and, where they affect what viewers see or frame rate, measurements on a TV.
- Each tested main merge publishes automatically. Routine PRs do not bump versions; planned release-line changes follow docs/RELEASING.md.
-->

## Summary

<!-- What changes for viewers or developers, and why. Link issues here or upstream (projectM-visualizer/projectm). -->

## Changes

-

## Release notes

<!--
Write factual, public, user-facing changes for the release notes. If there are no app changes, write
Internal: followed by a brief explanation. Fill the placeholder below before submitting.
Omit validation/test results, badges and installation information; CI appends those separately.
-->

-

## projectM patches

<!-- Only when tools/projectm-patches/ changes. -->

- [ ] The change is in a patch file in `tools/projectm-patches/`; nothing is committed inside `third_party/projectm`
- [ ] The patch is generated against the pinned projectM plus earlier patches in the series; its header explains the change and any upstream source
- [ ] From a fresh recursive checkout of this PR, `./gradlew :core:assembleDebug` succeeds: the Android CMake build applies the complete patch series to the pinned projectM (attach the build log)
- [ ] `bash core/src/test/native/run_native_tests.sh` passes, including the real projectM shader macro/parser and custom waveform regressions; record any skipped GL checks below
- [ ] Before/after TV captures and fps measurements use the same preset, render height and audio; explain any rendering differences in Evidence (profile setup in `docs/PROFILING.md`)
- [ ] Shader changes link as GLSL ES 3.00 (`glslangValidator -l`, with `#version 300 es` prepended)

## Validation

- [ ] Native engine tests: `bash core/src/test/native/run_native_tests.sh` (record any skipped GL checks below)
- [ ] JVM unit tests: `./gradlew testDebugUnitTest`
- [ ] Build: `./gradlew :app:assembleDebug`
- [ ] preset-lab, if `tools/preset-lab/` changed: `python -m pytest tools/preset-lab/tests`

## On a TV

<!--
For rendering, audio or performance changes. Use docs/PROFILING.md to install and profile the build next to the release app;
pin a preset with `adb shell setprop debug.projectmtv.preset '<name prefix>'`, use the same render height in both apps,
alternate release and profile runs, and read fps from the `VisualizerRenderer: STATS` log lines.
-->

- Device, GPU and Android version:
- What was checked (logcat errors, screenshots, fps before and after with the same preset, render height and audio):
- [ ] `debug.projectmtv.*` properties cleared and app settings restored afterwards

## Evidence

<!-- Before/after captures or benchmark tables. Say what was compared with what (build, preset, render size, audio, capture timing). -->

## Docs and release

- [ ] README, `docs/ARCHITECTURE.md` and the user guide describe the new behaviour
- [ ] The public `Release notes` section matches the final change and contains no placeholders or test logs
- [ ] No routine version bump; planned release-line changes update the base version/code/commit together following `docs/RELEASING.md`

## Not tested / known limitations

-
