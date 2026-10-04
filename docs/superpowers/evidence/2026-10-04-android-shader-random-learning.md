# Android shader random uniforms

The existing copied-source random adapter ran on macOS. It must not supply an
Android forecast with a host-libc sequence merely because the seed is identical.
An ARM64 build of that same adapter, executed on the owned API34 emulator, uses
Android/bionic. Under seed 12345 and the same five construction/load events,
672 scalar uniform components differ from the Mac result. Repeat Android
execution is exact for this request.

An independent Android control emits 452 raw C-rand draws and the twenty speed
power coefficients. Independently composed rotation matrices agree with all 72
uploaded matrices within 6.294341e-6. Preset/frame random vectors match their
expected draw offsets exactly. This tests the explicit numerical profile; it
does not establish correspondence to a particular renderer's random lifecycle.

`shader_random.execute_ledger` now accepts explicit `adb` and `serial` arguments
alongside an Android-compiled adapter. It transfers only the adapter and JSON
request to a new uniquely named temporary directory, executes them, and removes
that directory. No core AAR or app is modified. The result must identify
Android/bionic and pass the same event order, draw consumption, time and uniform
bank checks as host execution. The recorded serial and binary hash preserve
transport identity. An explicit serial is required; no device is auto-selected.

Remote commands use shell-v2 without a PTY, retaining exit status. A live negative
control printed a valid Android ledger and then exited 7: exec-out incorrectly
accepted it; the status-preserving path rejects it. Preparation/execution/cleanup
failures have regression coverage. Successful replay still reproduces the
452-draw ledger.

## Reproduction

Use the pinned engine's vendor headers and generated `cpu_random_adapter.hpp`:

```sh
/Users/jneerdael/Library/Android/sdk/ndk/27.3.13750724/toolchains/llvm/prebuilt/darwin-x86_64/bin/aarch64-linux-android26-clang++ -O2 -std=c++17 -static-libstdc++ -I tools/preset-lab/src/preset_lab/native -I build/milk-analyzer/native -I build/preset-lab-production/engines/96df3b3b13f0b358a26aeeafb4127dc8a62e51b0be76e56c33eeaea3faea705a/vendor tools/milk-analyzer/native_random.cpp -o build/milk-analyzer/android-learning/milk-shader-random-android
```

Call `execute_ledger` with this binary, the saved request's seed/events, the SDK
ADB path and the explicitly authorized serial. Bind returned uniforms through
`bind_random_uniforms` with the matching profile and event/time identity; the
existing forecast accepts those explicit per-stage banks. The Android fixture
is also exercised through scalar and grid shader matrix evaluation.

## Frequency and remaining work

Source-only scanning finds explicit shader random names in 3,205 of the 9,606
presets: rand_frame in 2,908, rand_preset in 412, rot_d in 12, rot_f in three and
rot_uf in one. Counts overlap; comments are removed, while disabled/unreachable
source is retained. These are lexical witnesses, not verified live dependencies
or successful predictions.

The native source constructs warp before composite. Failed warp preparation can
discard its instance; composite load/compile failures can construct replacement
instances. Each construction consumes 184 draws and each variable load 28 in
the copied source. Texture creation/selection, idle/transition presets, equation
random calls, actual seed mixing and render/load order can shift the shared
stream. Those must be accounted for before automatically assembling the complete
renderer ledger. Their order is still unverified against the published AAR.

Evidence: `tools/milk-analyzer/fixtures/android-shader-random-proof-2026-10-04.json`
and `tools/milk-analyzer/fixtures/shader-random-source-frequency-2026-10-04.json`.
Whole-preset appearance accuracy and renderer lifecycle verification remain false.
