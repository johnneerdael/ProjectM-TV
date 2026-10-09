# Parent-owned CGL execution

No compilation, GL context or device operation was performed during preparation. The source was checked against the public/header interfaces by reading them. Freeze a patched production engine source directory before invoking these commands; use the same retained source as the screenshot role and record its hashes. Do not use an arbitrary older engine snapshot solely because it builds.

From the repair worktree:

```sh
cmake -S build/audit/extended-mode-proposal -B build/audit/extended-mode-proposal/cgl-normal -G Ninja -DREPO_ROOT="$PWD" -DPROJECTM_SOURCE=/absolute/path/to/frozen/patched/engine -DSANITIZERS=OFF -DCMAKE_BUILD_TYPE=Debug
cmake --build build/audit/extended-mode-proposal/cgl-normal --target extended-mode-controls -j 8
build/audit/extended-mode-proposal/cgl-normal/extended-mode-controls build/audit/dot-diagnostics-audio.u8 build/audit/extended-mode-proposal/common-pcm-cgl.jsonl
```

The wrapper adds the unchanged canonical native regression CMake subtree and builds only the new ignored target. It preserves its real CGL context/GLAD setup, production library and platform shim. Specify the concrete frozen engine directory in place of the placeholder. Do not claim these commands ran during preparation.

Sanitizers, separately:

```sh
cmake -S build/audit/extended-mode-proposal -B build/audit/extended-mode-proposal/cgl-asan -G Ninja -DREPO_ROOT="$PWD" -DPROJECTM_SOURCE=/absolute/path/to/frozen/patched/engine -DSANITIZERS=ON -DCMAKE_BUILD_TYPE=Debug
cmake --build build/audit/extended-mode-proposal/cgl-asan --target extended-mode-controls -j 8
ASAN_OPTIONS=detect_leaks=0 build/audit/extended-mode-proposal/cgl-asan/extended-mode-controls build/audit/dot-diagnostics-audio.u8 build/audit/extended-mode-proposal/common-pcm-cgl-asan.jsonl
```

Exit1 means control/setup/assertion failure. Exit2 means the common PCM had unsupported/nonfinite geometry, spectrum pairs or lasso operands at a selected capture; retain its JSONL and do not relabel it a pass. Nonselected early failures remain visible in the trace. Running with no arguments executes only bounded production GL controls. The CMake wrapper deliberately rejects non-Apple integration; no implicit GLES port is qualified.

## What the source proves when executed

Bounded controls set finite waveform arrays within ±32, strictly positive spectrum arrays, scale1/smoothing0 and clock1.5; all sixteen mode factories have bounded input. Production Waveform::Draw submissions are captured through real GL function pointers, with actual current-program/link-status assertions for authored and Native draws. For each expected mode, compare every authored position/primitive/count to its explicitly selected production Factory producer. Native replay checks segment endpoints, strip/loop closure, point counts, one/four style passes, 3x-reference half-width1.5, finite colors/geometry and authored-context restoration. Mode1 alpha1 from .8*1.25 is checked on authored and Native lines. Mode aliases include8.9/9.9,16/17,24/25,31 and signed negative cases. A reused Waveform instance crosses every valid mode and valid→NaN/Inf/out-of-int-range/negative invalid→valid recovery; invalid states must submit nothing and keep GL program/targets.

This checks actual selected geometry behavior rather than reading private m_mode or altering class access. Factory-derived expected coordinates share the mode implementation; it is a factory-selection/replay contract test, not an independent geometry-formula oracle. Modes2/3 share geometry; this control currently does not independently distinguish their complete opacity formulas. Existing opacity controls remain required. Native dots are checked for positions/counts, not independent exact gain/size pixel coverage. A rejected Native quad program fails the current quad expectation; a deliberate fallback needs a separate explicit control. No RGB image certification is claimed.

## Frozen common input trace

The optional source producer stage reads all480 complete1470-byte PCM blocks and sends only the API-reported latest tail through Audio::PCM::Add(uint8_t,1,count), then UpdateFrameAudioData once per frame. Current actual tail is576; SpectrumSamples512 is a different number. It records the queried count in every JSONL row. Clock frame/30, first dt0 then1/30, source frame labels0..479, authored reference1280x720/physical3840x2160 and mesh input48x32 must be reconciled with the exact worker's timer/frame semantics. The source preset profile here is scale1/smoothing0/alpha.8/mystery.25; stock presets have their own profiles.

Each of16 persistent production factory instances consumes that frame's FrameAudioData and logs smoothed point counts/nonfinite points. It separately logs scaled spectrum pair minima and nonpositive/nonfinite pairs, plus lasso angle minima/nonfinite arguments/tan. This stage does not issue a full GL draw for every common-input mode/frame; bounded GL controls establish selection/replay, while common stage establishes host source producer domains. No epsilon or replacement values hide an invalid domain. All selected frames120/150/180/210/239/300/390/479 must qualify; reports retain earlier unsupported frames.

Host FFT/libm/compiler differences can change the source producer relative to ARM64. Match transport hashes and API tail count first; host finiteness alone does not qualify the unchanged shipping AAR spectrum. Native screenshot source/manifest identity must explicitly correct stale descriptive latest512 metadata while preserving frozen historical manifests and image hashes.

## Unchanged-AAR Android qualification without new shipping exports

Keep shipping APK/AAR/native bytes unchanged. If the exact binary exposes enough symbols, use a task-owned debuggable worker and external LLDB breakpoint at the actual PCM::UpdateFrameAudioData/GetFrameAudioData return. Read the returned FrameAudioData memory through the matching ARM64 ABI/debug symbol addresses, with exact ELF Build-ID/hash correspondence. Record waveform/spectrum/volume, frame clock/count and production FeedAudio tail. Do not attach approximate rebuilt debug symbols to a different binary, and do not patch shader/core memory. Breakpoint/readback timing perturbs performance, so input qualification is separate from a clean unchanged-binary screenshot run. Symbol availability/ABI mapping is not verified here.

If exact shipping symbols/ownership cannot be inspected reliably, build a separate explicitly identified ARM64 diagnostic producer/worker using the exact production Audio::PCM source and same API-backed576 unsigned tails. Trace actual target spectrum/tan/finite vertices there, freeze diagnostic source/compiler/libm hashes, then run the clean unchanged AAR with the same transport/profile/clock and captures. This is source-instrumented target-input evidence, not direct proof of hidden shipping arrays; disclose that limit. Prefer existing core-corpus source-instrumented hooks under an isolated producer role. No new JNI export or shipping library change is necessary. Root owns all such device operations and final images.

I21 remains retained-policy work pending those images and final producer/source lineage review.

## Current lineage and pipeline scope

Use root's CURRENT retained ac3 patched source (27 retained patches after I22 withdrawal), not the older b481 inventory snapshots. The CMake wrapper takes PROJECTM_SOURCE explicitly and never hardcodes b481. Frozen original packet identities remain historical source descriptions. Root's36 Native capture runs/18 exact repeats are external ongoing evidence and are not re-executed here.

This standalone target exercises the actual untextured Waveform and Native line programs, and asserts their active link status. It does not instantiate the full preset warp/composite pipeline from the screenshot .milk siblings. The root image packet must independently prove version201 black warp actually compiled using the production CompileForPipeline/program-status route; nonempty or black captures alone do not prove custom warp selection. Do not call this test a replacement for that full-pipeline program gate.

## Added full-pipeline custom marker

The prepared executable now also initializes actual production MilkdropPreset with version201/warp2 and a constant-blue warp, seeds previous feedback orange, renders into its explicit256x144 output target and requires finalRGB≈(0,0,64). This distinguishes the actual custom pipeline from legacy fallback on the orange seed. Waveform-only hooks are destroyed before the full pipeline draw. It is separate source CGL proof; original frozen black siblings remain untouched. The new diagnostic-warp-compile-blue.milk can qualify Android custom selection as a separate owned run; root must identify that preset and actual shader version in the manifest. Do not retroactively label frozen black images as strict Android compile proof. No shader program was compiled or marker executed during preparation.

The previous pipeline-scope paragraph applies to the original waveform-only portion; this added marker fills the production CGL custom-warp activity gap. It does not read a private program pointer or certify the exact frozen black body on Android.
