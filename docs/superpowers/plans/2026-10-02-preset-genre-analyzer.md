# Preset Genre Analyzer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The user has approved the spec; plan review and execution-method selection are pending. Do not dispatch agents until the user selects delegation.

**Goal:** Build an unattended, reusable preset analyzer and matcher that produces audience-aware collections for all twelve broad genres and makes them selectable in ProjectM-TV.

**Architecture:** Maintain a standalone Python package with an isolated C++ projectM worker. Cache universal preset fingerprints separately from audio descriptors, matching profiles, and exports. ProjectM-TV reads generated category indexes and restricts every selection path to active membership; it performs no offline analysis.

**Tech Stack:** Python 3.11+, standard-library argparse/dataclasses/JSON, NumPy, OpenCV, ffmpeg/ffprobe, pytest; C++17, CMake, SDL2, native OpenGL, the repository's projectM 4.1.7 and app patches; existing Java/JNI/GLES Android application.

**Spec:** `docs/superpowers/specs/2026-10-01-preset-genre-analyzer-design.md`

## Global Constraints

- Use all twelve fixed broad genre IDs from the spec; All is the unfiltered library. Do not add subgenres or automatic track-genre detection.
- Use `/Users/jneerdael/Desktop/audio`, at least one track per genre, for initial end-to-end testing. Ambient now has five recordings and Dance has six, including the favourite Saron Hart — Running (twenty-one recordings total). Neither further recordings nor ratings are a prerequisite.
- Target home TV listening with editable audience preferences. Keep audio response, genre fit, audience fit, and technical quality separate.
- `run` completes without prompts, manual analysis steps, or ratings. `match` never starts a render worker. Analyze new or changed presets automatically; reuse valid measurements.
- Inventory coverage and nonempty exports do not prove match correctness. Validate selected candidates against supplied recordings and independent visual-behavior counterexamples; retain predicted vs music-tested vs reviewed evidence explicitly.
- Start screening at 256×144, 30 fps, four seconds warm-up and twenty seconds measurement; extend uncertain cases to sixty seconds. Validate representatives at 512×288, 30/60 fps, three seeds, and on SHIELD.
- Use three non-overlapping thirty-second excerpts per supplied track; do not call excerpts from one track independent held-out evidence.
- Build analyzer instrumentation in an isolated engine-source copy. Do not modify shared vendored sources or depend on the missing prototype build directory.
- Keep user music and intermediate frames outside tracked app assets. Produce exact filename/tab/memory-weight category indexes from the current authoritative master index.
- Carry single-track/provisional evidence accurately. Optional manual overrides persist; unavailable stem/semantic measurements remain null with reasons.
- Treat session transition frequency as an existing app setting, not a measured preset property; it must not contribute a fabricated per-preset score.
- Preserve existing skip/weight behavior, hard-cut semantics, and All behavior. Respect unrelated changes. No release/version bump is required for this feature work.

## Review Focus

1. Paths with spaces, apostrophes, ampersands, Unicode, and attached album-art streams must decode/export without shell interpolation or artwork contamination: Tasks 1, 3, 8.
2. Engine, texture, decoder, metric, and profile changes must invalidate only affected stages; no stale predictions or unnecessary whole-library rerenders: Tasks 2, 3, 6, 7.
3. Slow-emerging or tiny reactive output must not be mistaken for a strong whole-scene musical response; intrinsic periodic animation must not masquerade as beat locking: Tasks 4, 5.
4. A category change while an old worker/prewarmer/auto-switch request is in flight must never display an out-of-category result: Task 9.
5. One-member, all-skipped, malformed, and missing category collections must terminate correctly and preserve an accurate visible category/fallback: Tasks 8, 9, 10.

## File and Interface Map

Create `tools/preset-lab/pyproject.toml`, `README.md`, `src/preset_lab/`, `tests/`, `native/`, and packaged `profiles/`. Keep the package independently installable with configurable source/asset paths; the Desktop audio path belongs in local invocation/configuration, not reusable module constants.

Within `src/preset_lab/`: `models.py` defines shared records; `inventory.py` and `identity.py` identify inputs; `preset_parser.py`, `eel.py`, `shader.py`, and `dependencies.py` produce static evidence; `audio.py` and `probes.py` prepare stimuli; `worker.py`, `cache.py`, and `pipeline.py` own execution; `features.py` and `response.py` compute fingerprints; `matching.py` applies profiles; `export.py`, `report.py`, and `cli.py` expose results. Add files only with the task that needs them.

Add `tools/import-preset-genres.py` for app import/check. Modify native selection in `core/src/main/cpp/native-lib.cpp`, prewarming in `preset_prewarm.h/.cpp`, JNI in `ProjectMJNI.java`, and the existing Android main-menu flow. Use existing host-native and JVM test infrastructure.

Shared records in `models.py`: `PresetRecord(path: str, sha256: str, weight_mb: int)`, `EngineIdentity(commit: str, patches_sha256: str, instrumentation_sha256: str)`, `RunConfig(width: int, height: int, fps: int, warmup_seconds: float, measurement_seconds: float, seed: int, audio_path: str)`, `JobSpec(preset: PresetRecord, stimulus_id: str, pcm_path: Path, config: RunConfig, identity: EngineIdentity)`, `WorkerResult(status: str, manifest: dict, diagnostics_path: Path)`, `StaticEvidence(complete: bool, paths: list[dict], unsupported: list[str])`, `Fingerprint(preset: PresetRecord, raw: dict, normalized: dict, quality: dict, evidence: dict)`, `TrackRecord(id: str, path: Path, genre_ids: tuple[str, ...], sha256: str, duration: float, excerpts: tuple[tuple[float, float], ...])`, `Corpus(tracks: tuple[TrackRecord, ...], descriptors: dict, identity: str)`, `MatchDecision(preset: PresetRecord, genre_id: str, music_fit: float, audience_fit: float, score: float, included: bool, evidence_state: str, contributions: dict)`, and `PipelineResult(render_jobs: int, reused_jobs: int, failed_jobs: int, export_path: Path | None)`.

Define `PipelineConfig(repo: Path, audio_root: Path, work: Path, audience_config: Path | None, run: RunConfig, concurrency: int, timeout_seconds: float, preset_limit: int | None, corpus_manifest: Path | None)` in Task 1. CLI flags construct this record directly; no hidden config-file generation is needed. Default audience configuration is the packaged home profile, concurrency is one worker, timeout is 120 seconds per job, and preset limit is null/full library. All are explicitly overridable. Later CLI tasks modify `cli.py` to register their handlers against the same entrypoint.

Preserve stable JSON schemas alongside these records. Reject non-finite floats on serialization and loading. Frame arrays are RGB uint8, shape `(height, width, 3)`, top-down; trajectory fields document units and timestamps.

## Task 1: Independently Installable Inventory and Input Contracts

**Files:** Create package metadata, `models.py`, `identity.py`, `inventory.py`, `cli.py`, `__main__.py`, `profiles/genres.json`, `tests/test_inventory.py`, `tests/test_cli.py`.
**Interfaces:** Produce shared records above; `inventory(presets: Path, index: Path, textures: Path) -> tuple[list[PresetRecord], dict]`; `main(argv: list[str] | None = None) -> int`. Genre catalog uses the exact twelve IDs/labels from the spec.

- [ ] Write failing tests: inventory preserves Unicode filenames and authoritative weights; duplicate bytes retain both names with a shared content identity; traversing filenames, duplicate index rows, malformed/negative weights and index/file disagreement fail with a specific diagnostic. CLI returns 2 for invalid options and 1 for failed operations.
- [ ] Run `python3 -m pytest tools/preset-lab/tests/test_inventory.py tools/preset-lab/tests/test_cli.py -q`; confirm missing-package failure before implementing.
- [ ] Implement records, canonical SHA-256 identity, strict JSON loading, inventory, and argparse entrypoint. Register `preset-lab` and independently installable dependencies. Provide machine-readable JSON stdout; progress/diagnostics go to stderr. Use subprocess argument arrays throughout.
- [ ] Verify the same tests pass and `preset-lab inventory --presets core/src/main/assets/presets --index core/src/main/assets/presets.idx --textures core/src/main/assets/textures` accounts for the current master library. Add install/inventory instructions to the package README.
- [ ] Commit this task's package/contracts/tests only after verification; retain unrelated work.

## Task 2: Isolated Deterministic projectM Worker and Doctor

**Files:** Create `native/CMakeLists.txt`, `native/worker.cpp`, `native/gl_capture.hpp`, `native/analysis_hooks.hpp`, `native/patches/`, `build_worker.py`, `worker.py`, `tests/test_worker_build.py`, `tests/test_repeatability.py`.
**Interfaces:** `prepare_engine(repo: Path, work: Path) -> tuple[Path, EngineIdentity]`; `build_worker(repo: Path, work: Path) -> Path`; `render_job(worker: Path, spec: JobSpec, on_frame: Callable[[np.ndarray], None], timeout_seconds: float) -> WorkerResult`. CLI worker: `preset-lab-worker --job job.json`; write RGB24 frames to stdout, diagnostics to stderr, and a final atomic manifest at the job's specified path.

- [ ] Write failing checks for no mutation of the supplied engine checkout, strict job validation, clean-frame dimensions/counts, fresh-process same-input hashes, and failure/timeout reporting. A fake worker exercises failure semantics without GPU access; the real repeatability test is separately marked `native` and cannot silently pass by skipping in the final Mac acceptance.
- [ ] Run `python3 -m pytest tools/preset-lab/tests/test_worker_build.py tools/preset-lab/tests/test_repeatability.py -q`; verify failure before worker implementation.
- [ ] Recover techniques by reading the archived prototype, not copying its absolute paths or obsolete normalization. Copy the pinned source plus nested dependencies, apply the app patch series idempotently in that copy, and apply analyzer-only hooks. Keep a digest of each source/patch/build configuration.
- [ ] Implement a synthetic clock, fixed subsystem seeds for initialization/shaders/hue/noise/texture selection, stable texture ordering, fresh evaluator state, locked preset/no transitions, band tracing, and final display-frame capture. Ensure hooks are enabled only for the analyzer build. Use SDL2 hidden OpenGL context and a caller-owned FBO; normalize framebuffer orientation once.
- [ ] Add `doctor` with build/backend/source/texture/decoder checks and real matched-prefix repeatability. Run it against a waveform preset, a noise/random-texture preset, and a shader preset; require equal same-input captures and no common-prefix drift before intervention.
- [ ] Run both test files, then the real native-marked checks and doctor. Record engine/backend identities and any unsupported driver behavior. Commit the worker and checks.

## Task 3: Supplied Music Ingestion, Descriptors, and Controlled Probes

**Files:** Create `audio.py`, `probes.py`, `tests/test_audio.py`, `tests/test_probes.py`.
**Interfaces:** `load_corpus(root: Path, manifest: Path | None, cache: Path) -> Corpus`; `describe_audio(pcm: np.ndarray, sample_rate: int) -> dict`; `make_probes(config: RunConfig, destination: Path) -> list[dict]`. Descriptor fields include spectral balance, onset timestamps/density, beat-period evidence, dynamics and energy variation, with availability flags.

- [ ] Write failing tests for the twelve supplied filename aliases, paths containing `&`/spaces/apostrophes, audio-plus-artwork files, invalid excerpt bounds, corrupt audio, silence, antiphase stereo, and records too short for three excerpts. Use synthetic generated audio fixtures, not copied user recordings.
- [ ] Run `python3 -m pytest tools/preset-lab/tests/test_audio.py tools/preset-lab/tests/test_probes.py -q`; confirm failures before code.
- [ ] Decode explicitly selected audio with ffmpeg into documented 44,100 Hz PCM. Document channel mixing, a shared gain/clipping policy and descriptor normalization; detect cancellation in antiphase inputs and flag it rather than calling it genuine silence. Hash source content and the exact decoder/conversion configuration.
- [ ] Select thirty-second excerpts centered at 25%, 50%, and 75% when they fit without overlap; otherwise select the maximum non-overlapping valid set. Store exact offsets and single-recording provenance. Support manifest overrides and optional aligned stems; compare full/leave-one-out mixtures at one shared gain. Missing sources remain null.
- [ ] Generate common-warmup silence/steady controls, spectral carrier interventions, isolated attacks, modulated/sustained stimuli, and tempo probes. Generate 60-second uncertainty extensions. Preserve identical pre-intervention PCM and avoid per-variant peak normalization. Give controlled PCM and simulated/captured Visualizer paths different cache identities.
- [ ] Verify fixture tests, then ingest all twelve actual M4A files without renaming/copying them into git. Confirm twelve genre descriptors and valid excerpts. Commit ingestion/probes/tests.

## Task 4: Faithful Static Dependency Tracing

**Files:** Create `preset_parser.py`, `eel.py`, `shader.py`, `dependencies.py`, `tests/test_dependencies.py`, `tests/fixtures/presets/`.
**Interfaces:** `parse_preset(path: Path) -> dict`; `trace_dependencies(parsed: dict) -> StaticEvidence`. Path records contain audio input, scoped intermediary chain, sink, impact class, and source section/line.

- [ ] Write failing fixtures asserting `bass -> q1 -> zoom` structural reachability; overwritten assignments do not create false current-frame paths; init/persistent state, branch conditions, per-vertex, wave/shape scope, shader uniforms and waveform sample values are covered. First duplicate key wins, first numbering gap stops code, comments/backticks behave like the engine. Unsupported syntax sets `complete=False` instead of claiming no audio influence.
- [ ] Run `python3 -m pytest tools/preset-lab/tests/test_dependencies.py -q`; confirm failure before implementing.
- [ ] Implement scoped EEL expression/statement parsing with conservative persistent-state and control dependencies. Reconstruct sections according to the current engine parser. Implement scope-aware shader expression/assignment/control propagation and mark any unsupported language feature explicitly. Keep reachability independent of dynamic strength; never evaluate untrusted code in Python.
- [ ] Test against fixtures and representative actual presets; compare section reconstruction with engine behavior. Check that the analyzer's trace output identifies actual dependency chains and preserves incomplete-analysis evidence. Commit the tracing implementation.

## Task 5: Streaming Visual Metrics and Universal Fingerprints

**Files:** Create `features.py`, `response.py`, `tests/test_features.py`, `tests/test_response.py`.
**Interfaces:** `measure_frame(frame: np.ndarray, previous: np.ndarray | None, fps: int) -> dict`; `fingerprint(preset: PresetRecord, trajectories: dict, static: StaticEvidence) -> Fingerprint`. Store raw-unit measurements and normalization/version metadata separately.

- [ ] Write failing fixtures for black/white frames, a tiny pulsing dot, full-scene response, known translation/rotation/expansion, bright flashes, persistent decay, and unrelated periodic motion. Assert normalized flow is resolution/fps consistent within documented tolerance. True attack synchronization must exceed shifted/shuffled onset controls; intrinsic animation must not earn equivalent audio-response strength.
- [ ] Run `python3 -m pytest tools/preset-lab/tests/test_features.py tools/preset-lab/tests/test_response.py -q`; confirm failures first.
- [ ] Implement luminance/contrast/saturation/edges/coverage, dense optical flow and robust motion decomposition, acceleration/jerk, persistence, flash statistics and lagged onset coupling. Weight whole-scene response by visibility. Compare feature trajectories with silence and steady controls, retaining raw pixel delta only as supporting evidence.
- [ ] Normalize with frozen versioned transforms, never current-library min/max. Keep source-removal results distinct from spectral sensitivity. Record missing stems as null, separate render/texture/compatibility faults from weak response, and automatically schedule longer tests for uncertain emergence. Exclude unresolved quality candidates with explicit reasons rather than waiting for ratings.
- [ ] Verify fixtures and real matched-run clips, including the older tiny-dot example under the current fixed engine. Record current evidence rather than reusing the obsolete exclusion list. Commit metrics/fingerprints.

## Task 6: Resumable Automatic Analysis with Stage-Specific Caches

**Files:** Create `cache.py`, `pipeline.py`, `tests/test_pipeline.py`.
**Interfaces:** `analyze_library(records: list[PresetRecord], corpus: Corpus, config: RunConfig, work: Path, worker: Path) -> list[Fingerprint]`; `run_pipeline(config: PipelineConfig) -> PipelineResult`. Use finite timeout/concurrency controls, one native process per job, atomic success markers, and JSONL events.

- [ ] Write failing integration tests with a counting fake worker: unchanged second run launches zero jobs; one changed preset reruns only its jobs; relevant texture/engine/probe changes invalidate affected universal runs; changed music affects its descriptors/validation only; changed metric version reuses retained captures when available, otherwise schedules necessary jobs; changed audience/genre profile launches no render jobs. Interrupted/truncated jobs cannot become successes.
- [ ] Run `python3 -m pytest tools/preset-lab/tests/test_pipeline.py -q`; verify failure before implementation.
- [ ] Implement content-addressed render, metric, audio-descriptor, validation and matching caches with explicit parent identities. Cache raw renders/trajectories independently from profiles. Stream worker frames into metrics and selected preview encoders; preserve diagnostic evidence. Record retention choices so recomputation never assumes removed captures still exist.
- [ ] Implement bounded concurrent scheduling, per-job timeouts, crash isolation, restart/resume and automatic changed-input discovery. Drain stderr concurrently with RGB stdout so verbose engine diagnostics cannot deadlock a worker; include a noisy fake-worker regression. Keep exit status nonzero when required outputs are unavailable. Report attempted/reused/failed counts and pending items in a durable manifest; never report interruption as completion.
- [ ] Verify counting-worker cache scenarios and a real small-preset batch/resume. Commit pipeline/cache behavior.

## Task 7: Automatic Music/Genre/Audience Matching

**Files:** Create `matching.py`, `profiles/audience-home.json`, profile versions in `profiles/genres.json`, `tests/test_matching.py`.
**Interfaces:** `match_presets(fingerprints: list[Fingerprint], corpus: Corpus, genre_profiles: dict, audience_profile: dict, overrides: dict | None = None) -> list[MatchDecision]`. `match` CLI loads valid stored fingerprints and writes decisions/index candidates without importing or calling `render_job`.

- [ ] Write failing tests: no ratings file still yields decisions for all twelve genres; one preset can match several genres; audience-preference changes reorder fixtures and alter only audience contributions; identical inputs reproduce scores; zero/missing/non-finite metrics never invent strength; explicit rejection overrides inclusion; missing independent validation remains identified. Monkeypatch worker launch to raise and require `match` to succeed.
- [ ] Run `python3 -m pytest tools/preset-lab/tests/test_matching.py -q`; verify failures before matching code.
- [ ] Define documented initial genre-style target vectors from the spec's editorial hypotheses and corpus descriptors. Store values/weights/thresholds in editable versioned JSON, identifying them as starting preferences. Use an auditable bounded weighted fit over spectral/onset response, measured behavior and audience target distances; contributions must reconstruct the score. Keep technical eligibility outside aesthetic ranking. Do not infer demographics or semantic/cultural visual themes.
- [ ] Rank measured candidates per genre automatically, perform the configured real-music checks through the pipeline, and retain predictions vs observed validation distinctly. Integrate automatic descriptor updates when music is added. Persist optional human feedback/overrides and reuse it; neither initial inclusion nor future matching requires new ratings.
- [ ] Verify fixture tests, a no-ratings end-to-end small-library match, and audience-only rescoring with zero worker launches. Add independent contrasts: quiet/persistent vs frantic/flashing under the Ambient home profile, beat-responsive vs intrinsic-only motion under Dance, and strong visible response vs a tiny/blank region. Run selected candidates against the actual genre recordings and inspect the contribution/validation evidence. Do not infer accuracy from the number of results. Commit matching and editable profiles.

## Task 8: Reproducible Exports, App Import, and Optional Review Report

**Files:** Create `export.py`, `report.py`, `tests/test_export.py`, `tests/test_report.py`, `tools/import-preset-genres.py`, `tools/preset-lab/tests/test_import.py`.
**Interfaces:** `export_bundle(decisions: list[MatchDecision], inventory: list[PresetRecord], evidence: dict, destination: Path) -> Path`; `write_report(fingerprints: list[Fingerprint], decisions: list[MatchDecision], destination: Path) -> Path`; importer CLI `--bundle PATH --repo PATH`, plus `--check` verification mode.

- [ ] Write failing tests for byte-identical exports, exact weights/path membership, manifest/index checksums, stale assets/engine/profile provenance, invalid genre IDs, duplicate rows, path traversal, malformed weights and non-finite values. Empty required categories fail complete export without replacing a previously valid bundle. Test HTML escaping for preset names containing markup and safe local clip references.
- [ ] Run `python3 -m pytest tools/preset-lab/tests/test_export.py tools/preset-lab/tests/test_report.py tools/preset-lab/tests/test_import.py -q`; confirm failures first.
- [ ] Write schema-version-1 `manifest.json`, `presets.jsonl`, and byte-sorted `genres/<id>.idx` using current master weights. Stage and atomically publish complete bundles. Keep measurement identity stable; put nondeterministic execution times outside reproducible artifact checksums. Include single-track evidence, audience-profile identity, exclusions and unreviewed decisions.
- [ ] Implement import/check against current asset bytes, textures, engine/app patches and master index; copy verified indexes plus manifest into `core/src/main/assets/preset-genres/`. Never regenerate genre membership in the app importer.
- [ ] Generate a local HTML report with synchronized audio/video clips, separate fit components and evidence, diagnostics and optional review-file instructions. No server/account required. Support optional suitable/unsuitable/uncertain overrides; reporting never blocks automatic export.
- [ ] Verify tests, inspect rendered report in the browser, import a real small-library bundle into a disposable fixture repo, and confirm corrupt import leaves existing files intact. Commit export/import/report.

## Task 9: Native Category Membership across Every Selection Path

**Files:** Modify `core/src/main/cpp/native-lib.cpp`, `preset_prewarm.h/.cpp`, `core/src/test/native/engine_test.cpp`, `core/src/test/native/run_native_tests.sh`; add category fixture assets through the test script.
**Interfaces:** Add `PresetLibrary::SetCategory(const std::string&) -> bool`, `Category() -> std::string`, `CategoryCount(const std::string&) -> int`, and `CategoryGeneration() -> uint64_t`. Keep master names/weights immutable. JNI request/applied status is separate; category changes run in the render/control path.

- [ ] Extend host tests to fail on category leaks through next/random/previous/automatic/beat/blank recovery, manual category changes with Auto change off, rapid changes, stale prefetch/prewarm results, startup requests before ready, singleton collections, unknown/malformed assets, all-skipped categories and reset-skip behavior. Assert weights/global skips survive switching to/from All.
- [ ] Run `core/src/test/native/run_native_tests.sh` in the isolated execution checkout; confirm new tests fail before implementation. Keep existing engine and real-GLES checks passing after changes.
- [ ] Read verified category indexes once on the library worker; enforce subset membership and expected weights. Derive active order from master minus global skips. Clear crossing history/random-ahead/cursor and tag/invalidate queued prefetch/prewarming work on category generation changes. In-progress shader compilation may finish and populate a harmless shared cache; its result cannot determine the displayed selection.
- [ ] Apply category requests before ordinary queued switch commands. Suppress stale automatic switches/fades and use established hard-cut logic if the current preset is outside the new set. Ensure failures/skips exhaust only the selected eligible set, then visibly apply All fallback without retry loops.
- [ ] Publish applied category/count/fallback state thread-safely. Replace queued prewarmer requests from the new active membership; verify race behavior with controlled worker barriers in host tests. Commit native integration only after existing and new host tests pass.

## Task 10: Persisted TV Music Category Setting

**Files:** Modify `core/src/main/java/nl/neerdael/projectm/core/ProjectMJNI.java`, `app/src/main/java/com/example/projectm/visualizer/MainActivity.java`, `app/src/main/res/layout/activity_main.xml`; create `MusicCategories.java` and `app/src/test/java/com/example/projectm/visualizer/MusicCategoriesTest.java`.
**Interfaces:** JNI `setMusicCategory(String genreId)`, `getMusicCategory() -> String`, `getCategoryPresetCount(String genreId) -> int`; Java catalog maps the exact spec IDs/labels, validates persisted IDs, and builds available option lists. Native getter reflects applied/fallback state, not an unfulfilled request.

- [ ] Write failing JVM catalog/state tests for all twelve labels, All default, invalid persistence, startup-not-ready vs unavailable, missing assets, empty eligibility and applied fallback. Extend native tests to verify JNI calls request/apply the correct state and counts.
- [ ] Run `./gradlew :app:testDebugUnitTest :core:testDebugUnitTest --no-daemon`; confirm new tests fail before implementation.
- [ ] Add the existing-style OptionRow with Music category, persist IDs, queue category application after initialization, and reconcile native fallback with visible value/preferences. Show eligible count. Keep focus navigation and existing main/advanced settings behavior; do not add automatic genre detection or a separate audience menu.
- [ ] Verify JVM/native suites, build `./gradlew assembleDebug --no-daemon`, and exercise row changes/restart/fallback on the SHIELD. Record the app's actual applied category and selected preset membership. Commit UI/JNI changes after verification.

## Task 11: Full Automatic Library Run and SHIELD Acceptance

**Files:** Update package `README.md`, root `README.md`, `docs/ARCHITECTURE.md`; generate verified `core/src/main/assets/preset-genres/` assets; add an ignored-workspace acceptance manifest and selected evidence under the existing diagnostics convention.
**Interfaces:** Normal CLI `preset-lab run --repo PATH --audio PATH --work PATH --audience-config PATH`; cached CLI `preset-lab match --work PATH --audience-config PATH --output PATH`. Individual doctor/inventory/analyze/validate/report/export commands remain available. A development `--limit` must mark its library coverage partial and cannot certify full-library completion.

- [ ] Write an end-to-end no-ratings acceptance test using generated audio and fixture presets, asserting twelve nonempty measured/profile-matched indexes, complete provenance, successful import and zero render launches on unchanged replay/profile-only matching. Verify partial runs cannot claim full-library coverage.
- [ ] Run `python3 -m pytest tools/preset-lab/tests -q` and real-native checks. Fix meaningful failures before starting the long batch; do not repeatedly broaden testing without cause.
- [ ] Run the full master library against the supplied twelve-track corpus with bounded concurrency. Render universal probes per unique preset content; score all presets automatically and validate chosen candidates against their genre samples. Record covered/analyzed/reused/excluded/failed counts and exact source identities. Resume the same live batch/cache if observation times out; do not restart it based only on a timeout.
- [ ] Automatically regenerate and verify the bundle, import category assets, build the test APK, and verify SHIELD All → Dance and every genre through manual/automatic/previous/random paths, persistence, skips and fallback. Match verification must include actual supplied-music runs and contrasting visual behavior, in addition to index integrity/counts. Exercise representative 512×288/30/60-fps/three-seed comparisons and TV input-path differences. Record unresolved device limitations honestly.
- [ ] Verify a repeat run launches no unchanged rendering, then change an audience preference and show cached membership changes. Add a new/modified fixture preset and prove automatic incremental analysis without rating prompts. Keep source fingerprints separate from sample validation evidence.
- [ ] Document installation, one-command use, profile editing, expansion of the music corpus, cache invalidation, exclusions and TV behavior. Commit verified genre assets and documentation; keep user audio/raw frames out of git.

## Task 12: CI and Completion Audit

**Files:** Modify `.github/workflows/android.yml`; add `.github/workflows/preset-lab.yml` for Python and fake-worker tests, and native worker checks on an appropriate configured Mac runner if available. Keep local real-GPU checks required when CI cannot provide a backend.
**Interfaces:** Importer's `--check` runs without user recordings against committed provenance/indexes; test fixtures are generated or redistributable and independent of Desktop paths.

- [ ] Add CI tests that fail on tampered index weights/checksums/source identities and on accidental tracked test music/raw captures. Run fixture Python tests, existing native/JVM suites, and importer integrity checks. Report unavailable real-GPU checks as not run, not green evidence.
- [ ] Run the same checks locally plus the verified APK/SHIELD acceptance before making completion claims. Confirm every spec requirement maps to code, command output or runtime evidence; unresolved parser/renderer/corpus/device evidence remains explicitly incomplete.
- [ ] Commit CI/verification documentation once checks pass. Review the complete diff for cross-component contracts, cache reuse, selection races, automatic operation and unintended release changes; correct actual findings and rerun affected checks.

## Plan Self-Review and Execution Handoff

Coverage: static reconstruction/tracing (4), deterministic native measurement (2, 3, 5), spectra vs stems (3, 5), caching and unattended operation (6, 7, 11), audience/genre scoring (7), report/export/import (8), every TV selection path and fallback (9, 10), full-library/corpus/SHIELD evidence (11), CI and final audit (12). Optional Butterchurn validation is excluded from required initial delivery as the spec permits; MilkDrop3 remains explicitly unsupported.

Shared type/signature names above are the task interfaces. JSON records include schema versions, identities and unavailable-value reasons. Tests exercise all five Review Focus classes. User recordings and subjective ratings are not hidden CI dependencies.

Recommend native execution in this session: the tasks share worker/cache/model interfaces and one TV selection state machine, so implementing them sequentially avoids handoff overhead. Isolate implementation from unrelated diagnostics/work before product edits. Commit the approved spec alongside that isolated branch's first verified task rather than staging unrelated files in this shared checkout.

Plan review and execution-method selection are the remaining planning gate. Native means the current agent implements the tasks; delegated execution means fresh implementer/reviewer agents per task. Do not start product implementation until that gate is satisfied.

Technical references: [Python argparse](https://docs.python.org/3/library/argparse.html), [NumPy real FFT](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html), and [OpenCV optical flow](https://docs.opencv.org/4.x/dc/d6b/group__video__track.html). Inspect the actual installed versions during Task 1/doctor and pin the resolved dependency set for reproducibility.
