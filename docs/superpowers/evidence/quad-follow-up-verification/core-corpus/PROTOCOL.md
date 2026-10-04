# Core-backed corpus protocol

Use the actual `projectm-tv:core` JNI wrapper on device `192.168.51.53` only. The dedicated package `nl.neerdael.projectmtv.corecorpus` runs framework instrumentation with a GLES3 EGL pbuffer; no Activity, wake command, other device, or production-package replacement is needed. Baseline and candidate APKs share this dedicated package, so run each role as a block. Force-stop this package before every job for a fresh process.

Freeze all 9,606 exact preset byte identities and texture identities. Verify every APK asset against that inventory before preparing a protocol. Record each APK and embedded/runtime core ELF SHA256, source commit, ordered patch series and private clock/RNG instrumentation identity. The baseline must use actual `a59b4e5` core, with patches 0001–0024; the candidate uses the current core patch series. Preserve test instrumentation separately from production changes. Never reuse the old direct patched-projectM results as core evidence.

The shipping-cap experiment renders 2364×1330 at a synthetic 30 fps. The full screening window has 120 warm-up plus 360 measurement frames, for 480 rendered frames. Feed every frame's complete 1,470-byte unsigned PCM block through `ProjectMJNI.addWaveform`; leave the production wrapper's 576-sample tail selection intact. Generate one 16-second bass-0.30 seeded signal and quantize `clip(rint(128+127*x),0,255)`. The short 240-frame pilot uses the exact first 352,800 bytes, preserving the long signal prefix. Do not independently generate the short FFT noise.

Selected readback indices are 120,121,150,151,180,181,210,211,238,239,300,301,390,391,478,479. Adjacent pairs screen short and long window motion. Every rendered frame records the exact current preset name, switch counter and PCM block count; any substituted name is an explicit terminal failure. The APK supplies a skip mask leaving exactly one eligible preset.

Read back GLES RGBA, then strip alpha for the **native RGB8 oracle**, retaining bottom-to-top GL row order for byte hashes. Selected mode hashes only read frames; it cannot claim a full-stream hash. Full pilot mode reads and hashes every frame but retains files only for selected indices. Corpus output retains native selected-frame hashes, compact metrics and lossless 256×144 PNG thumbnails. APK thumbnails flip orientation to top-to-bottom and use `AndroidBitmap.createScaledBitmap(...,256,144,true)` bilinear sampling. Host verification hashes each PNG; this thumbnail comparison is separate from historical 1182-pixel fidelity metrics.

Schema 2 jobs are pushed under `/sdcard/Android/data/nl.neerdael.projectmtv.corecorpus/files/jobs/<job_id>/`. Launch using `am instrument -w -e job <job.json> nl.neerdael.projectmtv.corecorpus/nl.neerdael.projectm.corecorpus.CorpusInstrumentation`. The APK publishes atomic `result.json` last, with `frames.jsonl`, selected file checksums, runtime core identity and GL metadata. Failed jobs, timeouts, incorrect current presets and nondeterministic repeats remain explicit records.

Run host tests:

```sh
build/preset-lab-venv/bin/python -m unittest discover -s docs/superpowers/evidence/quad-follow-up-verification/core-corpus -p test_run.py -v
```

After both APKs exist, prepare immutable inputs, then run eight full/selected comparisons across baseline/candidate and short/long cases:

```sh
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/core-corpus/run.py prepare --baseline-apk BASELINE.apk --candidate-apk CANDIDATE.apk
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/core-corpus/run.py pilot
```

Each pilot case also repeats selected mode. Independently verify selected native files against APK hashes and the full capture's corresponding hashes before allowing a scan. Keep Royal native proof files and compact other full pilot native samples after independent verification to keep retained pilot raw data below 2 GB. Preserve native checksums and the verification result when compacting.

Do not launch the entire corpus until the successful pilot and immutable protocol have been reviewed and core-aware remote checkpointing is working. `scan --reviewed-pilot-sha256 <reviewed report file SHA256>` requires the exact eight-check report. The scan attempts every preset twice for each role and verifies exact selected-frame repeat hashes. This scan therefore has 38,424 jobs. Resume requires matching protocol, source identities, row checksums and retained file hashes. Compiler warnings and fallback diagnostics remain evidence; wrapper/GL success alone does not prove custom-shader compilation.
