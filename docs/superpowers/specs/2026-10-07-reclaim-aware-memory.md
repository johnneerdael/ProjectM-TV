# Automatic memory policy without root

Scope revised 2026-10-08: the owner explicitly rejects a root cleanup setting. Improve the existing automatic controller; add no root capability, process cleaner, permission, UI setting, or music-player lifecycle service.

## Required behavior

Use device RAM, Android ActivityManager available-memory/pressure/threshold signals, rendering allocation estimates and actual completed-frame FPS. Let Android reclaim cached applications according to process importance. Do not enumerate or kill other applications, estimate unavailable per-app RAM, or grant growth credit for presumed cleanup.

Available memory already excludes resident music-player allocations. Do not subtract those again. Reclaimable portions already represented by Android's available-memory sample must not be counted twice. Android restricts other-app memory inspection on newer releases, so aggregate pressure reflects competing background use; a complete free-plus-background-minus-music total is not a supported portable input.

For Android-visible total RAM >= 3,584 MiB (nominal 4 GB+ hardware), remove the total-RAM percentage floor and retain reserve = Android threshold + 128 MiB. Below 3,584 MiB retain max(total / 5, Android threshold + 128 MiB). Keep 64 MiB recovery hysteresis and allocation/resize overlap allowances on all devices. This relaxes the current unnecessarily large reserve on larger TVs without removing genuine-pressure protection.

Keep healthy-sample/FPS hysteresis, per-preset backoff, confirmed-resident credit, explicit-resolution recovery, stale-generation rejection, pressure cleanup hooks and context/resume checks. Invalid telemetry and Android lowMemory still forbid growth; actual pressure still reduces rendering and flushes the app's own native caches. No allocation is authorized against hypothetical freed memory.

The existing foreground ProjectM Activity and Milkbeat Media3 foreground playback service already give higher process importance than cached apps. No permanent OOM-score override or real-time scheduling change is required. Playback survival is not guaranteed under every vendor policy.

## Evidence and limits

The AM6 reported 3,960,360 KiB total RAM, approximately 728 MiB cached-process PSS, and a total-RAM reserve floor of 773.5 MiB. Cached PSS is not wholly additional usable RAM: shared/file-cache/swapped pages and missing GPU attribution prevent naive addition. Ordinary Android reports omitted GPU memory while Mali reported approximately 591 MiB of graphics allocation.

The earlier silent-playback incident showed an empty audio buffer, retained focus and continued PLAYING state with a live original Milkbeat process. It did not establish a memory kill and remains a separate issue.

## Implementation and validation

Change RenderMemoryBudget and tests in the existing controller flow. Add regression coverage for a nominal 4 GB AM6-like total, threshold boundaries, 1/2 GB conservatism, moderate available-memory growth, truly unsafe candidate allocations, lowMemory/invalid samples, recovery hysteresis and allocation/resume generation semantics. Preserve the existing MemoryProvider/MemorySnapshot contracts and canonical core AAR consumer compatibility.

Update README, settings/development guidance, architecture/current memory-policy documentation and AGENTS.md. Run app/core JVM checks and build matched APK/AAR artifacts. On the awake user-authorized AM6, measure actual render height/FPS/memory and audio-frame progression under matched preset/audio/settings; verify context resume and real-pressure fallback where safely reproducible. Never wake the TV or operate unrelated devices. Do not infer whole-corpus performance or playback survival from these checks.

Complete the repository's PR, Codex review, CI, merge and publication gates; no manual release bump. The implementation adds no dependency, permission, or UI control. Rooted and unrooted TVs run the same automatic policy.

## Platform references

- [Android MemoryInfo](https://developer.android.com/reference/android/app/ActivityManager.MemoryInfo)
- [ActivityManager process-memory restrictions](https://developer.android.com/reference/android/app/ActivityManager#getProcessMemoryInfo(int[]))
- [Android cached-process lifecycle](https://developer.android.com/about/versions/14/behavior-changes-all)
