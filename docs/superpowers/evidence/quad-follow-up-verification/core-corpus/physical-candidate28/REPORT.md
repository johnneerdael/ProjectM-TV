# Candidate28 actual-core physical-device validation

Candidate28 passes all strict runtime controls on the approved physical AM9 PRO at 192.168.51.53:5555. Four unmodified presets each pass two complete 480-frame captures, two selected-frame runs, and exact full-versus-selected equality at all 16 selected indices. This is actual production `:core` JNI/EGL/GLES execution in the dedicated test APK, not a direct-projectM or CGL surrogate.

## Provenance and device boundaries

- Source commit: `eca2d66704195dc4c412f269d52ce4bfde21e48f`, patches 1–28.
- Candidate APK SHA256: `ca8f3c1ae720fb18393dc611a8e569d388cfad2e6a36791ffed04f70e7bc7450`.
- Actual runtime core ELF SHA256: `d0867fca97c52998a975ad1970f08ec3ae29b91293b079b0c41a07f0c785cc9c`.
- Observer/instrumentation SHA256: `1abc75ec9591541bc3520b80d9d1a1bc91863ab5a6c1bbcf6c41bd09dc0c183f`, identical to the physical v4 baseline/candidate27 observer.
- Device: UGOOS AM9 PRO, Mali-G310, OpenGL ES 3.2 `v1.r44p1-01eac0.9b95285bf71814048571d5e10c324e77`, arm64-v8a.
- Dataset protocol SHA256: `1782ff842e513bbb671f08e9ebd2cc12f5c5df92dd1e9e76e6ad9b63e00a7497`.

Read-only power checks confirmed `mWakefulness=Awake` and interactive=true before installation and after the later optional baseline-install timeout. No wake command, property/setting change, production-app operation or emulator command was issued. The Mac emulator baseline was not touched. Only `nl.neerdael.projectmtv.corecorpus` was stopped/installed/cleared for the approved isolated test. Existing dedicated private/external staging was preserved to `measurements/recovered-device` before role clear; copied-file hashes are in `recovery-manifest.json`.

`frozen-run.py` is a byte-identical copy of the host runner used for this dataset. Its repository-root host path is supplied for the copied location; neither observer code nor renderer inputs changed. The APK executes the existing CoreJNI path, including core audio feeding, direct-output decision, line-reference policy and blank-detector observation. No classic/reference mode was emulated by bypassing the module.

## Runtime checks

Configuration: 2364×1330, 30 fps, seed 12345, 120 warm-up frames plus 360 measurement frames (16 logical seconds), the same uint8 PCM protocol and one eligible requested preset. Core prewarm pause remains active for the logical job duration. Each producer checks complete 1470-byte JNI audio blocks, requested current-preset name, unchanged preset counter, frame continuity, per-frame GL errors, captured-native hashes and actual ELF identity.

All 16 candidate jobs succeed. For each control:

- FULL1 and FULL2 concatenated 480-frame RGB streams are exactly equal.
- SELECTED1 and SELECTED2 have the same 16 native frame hashes.
- FULL and SELECTED agree at all 16 selected indices.

Exact control names/source checksums and all job results are retained in `measurements/inventory.json`, per-job `row.json`, and the four `candidate-*-checks.json` files:

- `A Remixed Digital Echasketch  Again 2 martin - no religion  + disco Fruits Machine + Raron + mstress + 8.milk`
- `$$$ Royal - Mashup (191).milk`
- `suksma - ed geining hateops - Matrix Moral Infinite.milk`
- `suksma - mood rings for masochist alien deities - portentous anskeptising.milk`

`verified.json` confirms 256 retained native `.rgb` files, totaling 2,414,684,160 bytes, each exact to its producer's SHA256 and size. These files are immutable. SHA-identical hardlink deduplication may preserve their paths/bytes without changing the proof; the exporting task has finished reading them.

## Actual before/after visual evidence

`assess.py` verifies each actual APK thumbnail checksum and creates matched sheets. Thumbnails are 256×144 Android Bitmap filtered output from the native capture; they are clearly not historical 1182 fidelity-error measurements. Full native files for the new candidate are retained independently.

- `Echasketch-actual-core-sheet.png`: stable a59 baseline FULL2, pre28 candidate27 and candidate28 at matched 4–16 s samples. Entire 480-frame candidate28 stream equals the stable prior candidate27 stream `04a41b5f11f1114a2e54b2989626577ca5538137a2ea66b6173b6c686e81ce95`; all 16 selected hashes agree. Scene, palette and fine feedback structure are unchanged in these stable runs.
- `Royal191-actual-core-sheet.png`: baseline, candidate27 and candidate28 remain exactly equal across the matched samples. Candidate28's full 480 stream equals prior candidate27 `e7e8abe146e77290753f36fb0eba32dfd63b9ab5dccfdb56005ee0aee22b8ee1`. The existing bright native arc field remains; patch28 does not solve authored/reference fidelity.
- `Matrix-actual-core-sheet.png`: baseline a59 differs from both corrected candidates in red/blue recursive detail, consistent with the earlier sampler26 semantic correction. Candidate28 and candidate27 are exact at the ten native indices shared with the old 240-frame pilot. Their full stream hashes cannot be compared across different lengths; no 480-frame pre28 Matrix equality is claimed. There is no visible additional 28 change in the matched prefix.
- `MoodRings-actual-core-sheet.png`: actual candidate28 bubble/ring surfaces and later colorful flow remain active through 16 s. This is a **candidate-only** sheet because the v4 pilot has no Mood Rings comparator and the optional fresh baseline installation timed out. No before/after or authored-fidelity improvement is inferred for this case from these new controls alone.

The sheets were visually inspected. The preserved stable before/after captures show no added massive 28 structure, palette or detail change in the available comparators. This is a bounded comparison, not an all-preset or all-audio claim. `assessment.json` records exact matched frame coverage, source code/core identities and thumbnail differences.

## Wall-time observations, not shipping FPS

Full capture performs a synchronous native readback and hashes every frame. Selected capture reads only 16 frames. The resulting wall times include instrumentation, readbacks, bitmap/hash work, startup and host transfer; do not convert them into shipping frame-rate claims or attribute a speed change to28. Exact per-run producer and host times are retained in `row.json`/`assessment.json`.

The first Echasketch FULL runs report 59.312/58.858s producer and65.216/64.892s host elapsed. Its first selected run reports 19.462s producer and25.393s host. These confirm the expected observer overhead while logical frame/audio inputs and pixels remain exact.

## Optional baseline install stopped safely

After all 16 candidate jobs completed, the script attempted to install the immutable a59 baseline solely for fresh matched spot-checks. `adb install -r` timed out after 300 s. The script stopped; **no baseline job ran and no later package data clear occurred**. Read-only verification afterward found the installed dedicated ELF still equals candidate28 `d0867fca...`, and the device remained awake. No blind retry was made. The timeout traceback is preserved in `run.log`; prior test staging was already preserved before the attempt. Root explicitly requested no retry.

## Attribution limits

The original physical v4 baseline FULL1 startup outlier remains preserved and quarantined. Candidate28 repeats match the stable old runs, but these runtime controls do **not** prove that patch28 was the sole cause of resolving that particular outlier. The separate real-CGL poisoned-storage/context-collision regressions establish the two renderer contract defects. No private poisoned-core observer was added here, and no production RNG parity, shipping-performance or full-corpus completion claim is made.

## Offline reproduction and preserved artifacts

```sh
build/preset-lab-venv/bin/python build/follow-ups/core-corpus/tv-candidate28/verify.py
build/preset-lab-venv/bin/python build/follow-ups/core-corpus/tv-candidate28/assess.py
```

These are offline validation/export commands. Do not rerun `spot_checks.py` without coordinating device ownership: it contains the original optional baseline role stage. The completed candidate jobs, frozen host runner, protocol/inventory/PCM, actual producer logs, all captured frames, recovery evidence, strict check files, matched sheets, `assessment.json`, and `verified.json` are preserved under this independent dataset. No source harness/API or production/worktree files were edited.
