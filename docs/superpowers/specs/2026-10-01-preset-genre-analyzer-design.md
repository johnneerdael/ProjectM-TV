# Preset genre analyzer for ProjectM-TV

Status: approved by the user on 2 October 2026, including automatic matching without repeated manual analysis. The user has supplied one sample per genre and explicitly accepts this corpus for initial testing, with expansion later. The audience is confirmed as home TV listening with editable audience preferences. No analyzer or genre selector has been implemented by this design document.

## Outcome

Build a separate local tool that automatically characterizes MilkDrop presets with static dependency analysis and controlled projectM rendering, validates those measurements against user-supplied music, considers the intended viewing audience, and exports overlapping preset collections by broad genre. Store reusable fingerprints and matching profiles so future matching does not require repeating manual analysis or ratings. ProjectM-TV must support a persisted Music category setting, including All and Dance, which restricts every preset selection path to the chosen collection.

Keep the complete outcome in scope: a runnable analyzer, measured genre collections with audience-aware selection and review controls, an export contract, and a verified TV category selector. A parser, synthetic-only scores, or a menu without measured collections does not complete the project. Initial single-track evidence is sufficient for the user's agreed first test; broader generalization is assessed after corpus expansion.

User clarification: inventory coverage is not matching accuracy. Neither enumerating 9,606 presets, producing twelve nonempty indexes, nor showing that a renderer runs proves genre suitability. Match candidates against the actual supplied recordings and documented home-viewing preferences. Report predicted, music-tested, and optionally user-reviewed evidence separately. Completion requires the automatic matching behavior to pass real-music and deliberately contrasting visual-behavior checks; never replace those checks with counts or schema validation.

Source brief: https://chatgpt.com/s/t_6abed47009b48191ad5bcb13d9a66492

## Evidence from this checkout

- `core/src/main/assets/presets.idx` currently contains 9,606 presets. `tools/gen-preset-index.py` generates filename/tab/memory-weight rows; weights support device quality decisions.
- `core/src/main/cpp/native-lib.cpp` owns `PresetLibrary`, including shuffled order, random-ahead selection, history, skips, blank strikes, and background prefetch. The app does not use projectM's playlist library.
- `app/src/main/java/com/example/projectm/visualizer/MainActivity.java` uses `OptionRow` for settings and stores preferences. There is no music-category setting in the current selection path.
- The current app feeds Android Visualizer unsigned 8-bit mono waveforms to JNI unchanged. Native `FeedAudio` retains the latest engine-sized sample window. The older spike's independent per-block normalization is therefore a historical test path, not an exact model of current Android capture.
- `diagnostics/macos-reactivity-spike/README.md` records repeatable offscreen OpenGL renders with fixed time and random seeds, visibility measurements, synchronized clips, and texture warnings. Its archived source is available; its former `build/macos-reactivity` directory is missing. Recover useful techniques into maintained code rather than depending on that missing directory or absolute prototype paths.
- `docs/THIRD_PARTY.md` identifies projectM 4.1.7 plus the app's patches. Patch 0008 now fixes the floating-point remainder issue demonstrated by the older spike; do not carry its old exclusion list into a new engine build.
- `third_party/projectm/src/libprojectM/MilkdropPreset/PresetFileParser.cpp` uses the first occurrence of a key and stops numbered code at its first missing index. Analysis must follow those rules.
- Randomness exists in engine initialization, shader values, hue offsets, generated noise, texture choice, timing, and the evaluator. The inspected C API has no comprehensive deterministic-run control. Analyzer-only instrumentation is required.

## Approach selection

| Approach | Advantages | Cost or limitation |
|---|---|---|
| Python orchestration and metrics with a native projectM render worker — recommended | Uses the TV renderer's code; practical audio/CV tooling; process isolation and resumable jobs; easy reports | Needs a maintained native build and explicit deterministic instrumentation |
| Native C++ application for everything | One language and direct engine access | More work for corpus preparation, metrics, calibration, and review reports |
| Browser renderer as primary analyzer | Convenient preview and distribution | Butterchurn is a different implementation; its output cannot establish ProjectM-TV compatibility |

Recommend a standalone package under `tools/preset-lab/`, with its own command, dependency configuration, CMake build, tests, and documentation. It runs independently of the Android app and takes explicit preset, texture, and engine-source paths. Keep engine instrumentation in a build-local source copy; never mutate the shared vendored source while Android builds may be using it. A separate repository can later host the same package without changing the data contract.

Target this Mac first, using native offscreen OpenGL, then validate exports on the SHIELD/OpenGL ES runtime. Desktop measurements carry their backend identity and do not automatically certify all TV devices. Keep user music and intermediate captures outside tracked assets.

## Broad genres and music delivery

Use these fixed IDs and display labels. All is the unfiltered existing library, not a thirteenth musical genre.

| ID | Label | Useful contrast within supplied examples |
|---|---|---|
| `dance` | Dance | Steady strong beats, quieter passages, builds and drops |
| `pop` | Pop | Vocal verses, fuller choruses, softer and energetic arrangements |
| `rock` | Rock | Quiet and dense guitar/drum sections |
| `hip-hop` | Hip-Hop | Bass-led beats, sparse arrangements, vocal-led passages |
| `rnb-soul` | R&B / Soul | Smooth grooves, prominent vocals, different instrumental density |
| `jazz` | Jazz | Sparse and ensemble passages, steady and varied rhythms |
| `classical` | Classical | Solo and orchestral passages, sustained and percussive dynamics |
| `ambient` | Ambient | Sustained textures, sparse events, gradual changes |
| `folk-acoustic` | Folk / Acoustic | Plucked and strummed instruments, instrumental and vocal passages |
| `country` | Country | Acoustic and fuller band arrangements, vocal-led passages |
| `reggae` | Reggae | Bass and rhythmic interplay, sparse and fuller arrangements |
| `latin` | Latin | Percussion-led and melodic passages, different energy levels |

These are broad test buckets, not claims that every track in a genre has the same acoustics. Do not add subgenres or automatic genre detection. Allow one track and one preset to belong to multiple buckets.

Use the supplied corpus at `/Users/jneerdael/Desktop/audio`: one full track per genre is sufficient for the initial end-to-end tool and TV-category test. Do not require five tracks or independent held-out recordings before building, testing, or exporting the initial collections. Record the evidence as single-track testing, and expand the corpus later to assess how well the collections generalize. Prefer FLAC/WAV for future additions; the supplied M4A files are supported through the decoder. Ordinary mixed recordings are sufficient. Aligned stems are optional and improve source-response evidence.

User update, 2 October: Ambient now has five supplied recordings, mapped in the user's stated order. Keep a single broad `ambient` genre and treat the supplied subgenre/sonic descriptions as test scenarios, not additional category IDs or measured conclusions. The corpus now has sixteen recordings across twelve broad genres. Use `profiles/reference-corpus.json` in the tool package to preserve the filename/title/scenario mapping; keep all source audio external.

| File | User-specified reference | Test emphasis |
|---|---|---|
| `ambient.m4a` | Brian Eno — 1/1 | Sparse events, long silence, transients, clean decay |
| `ambient2.webm` | Steve Roach — Structures from Silence | Slow swells, sustained harmony, low beat density |
| `ambient3.webm` | Lustmord — Metastatic Resonance | Low/sub-bass, reverberation, unpredictable noise hits |
| `ambient4.webm` | Gas — Pop 4 | Masked kick/beat under dense texture |
| `ambient5.webm` | William Basinski — dlp 1.1 | Gradual spectral degradation, noise floor, dropouts |

Support numbered samples in flat folders, including WebM/Opus. Actual excerpt descriptors and measured response remain separate from the user's expected sonic profiles. Per-genre corpus provenance reflects its real recording count; other genres remain valid initial single-track tests.

Further user update: Dance has six recordings, ordered as listed below, bringing the current corpus to twenty-one recordings across twelve genres. Saron Hart is the user-confirmed favourite melodic techno reference; retain this preference as editable matching metadata, not a new category or a measured acoustic conclusion.

| File | User-specified Dance reference | Test emphasis |
|---|---|---|
| `dance1.webm` | Tiësto — Adagio for Strings | Beatless breakdown, rolling 4/4 bass, bright leads |
| `dance2.webm` | Charlotte de Witte & Enrico Sangiuliano — The Age of Love (Rework) | Low-end transients separated from acid/filter sweeps |
| `dance3.webm` | Ran-D — Zombie | Distorted kicks, low-mid bursts, vocal breakdown, synth chords |
| `dance4.webm` | Avicii — Levels | Sidechain ducking, piano plucks, vocal samples |
| `dance5.m4a` | Gigi D'Agostino — L'Amour Toujours | Quantized rhythm, sharp mid/high leads |
| `dance6.webm` | Saron Hart — Running | Favourite melodic techno reference |

Normal flat-folder ingestion discovers additional numbered files and automatically attaches known annotations. An explicit manifest is optional and overrides automatic discovery; it is not required every time samples are added.

The following files were inspected with ffprobe on 2 October 2026. All twelve complete audio streams were also decoded with ffmpeg, returning exit code zero and no reported decode errors. Each has a 44,100 Hz stereo AAC audio stream and an attached MJPEG image. Select the audio stream explicitly; album artwork is not visualizer output. Resolve these filename aliases at ingestion without renaming the user's files.

| File | Genre ID | Duration (seconds) |
|---|---|---:|
| `ambient.m4a` | `ambient` | 1041.53 |
| `classical.m4a` | `classical` | 289.51 |
| `country.m4a` | `country` | 231.71 |
| `dance.m4a` | `dance` | 384.96 |
| `folk.m4a` | `folk-acoustic` | 165.49 |
| `hiphop.m4a` | `hip-hop` | 237.33 |
| `jazz.m4a` | `jazz` | 563.57 |
| `latin.m4a` | `latin` | 225.79 |
| `pop.m4a` | `pop` | 178.17 |
| `r&b.m4a` | `rnb-soul` | 243.93 |
| `reggae.m4a` | `reggae` | 172.92 |
| `rock.m4a` | `rock` | 216.92 |

For initial runs, select three non-overlapping thirty-second excerpts spread across each track, with explicit offsets in the manifest and an option to replace them manually. These are within-track checks, not independent held-out validation. A future shorter track may supply fewer valid excerpts; do not repeat or pad it and pretend to have more evidence.

Accept the current flat folder, genre folders, or a manifest with track ID, local path, genre IDs, excerpt start/end in seconds, and optional aligned stem paths. Require finite, valid excerpt bounds and readable audio. Preserve source hashes and excerpt offsets. When the expanded corpus permits an independent split, group recordings into calibration and held-out validation sets; excerpts and stems from one recording stay in the same group. Do not reuse a recording across those groups under different filenames. With the initial corpus, record independent validation as unavailable.

For stemmed examples, support drums, bass instrument, melody, and vocals. Record other components separately. Missing stems produce unavailable source-response values, never invented zeroes or spectral-band proxies. Stem separation is not required for the first tool; any later estimated stems must identify the separation method and uncertainty.

## Audience fit

Treat audience fit as a separate, editable preference layer over measured preset behavior. A technically beat-responsive preset can still be distracting or aesthetically unsuitable for the intended viewers. The same fingerprint must support multiple audience preferences without repeating native rendering.

Use the user-confirmed setting of home TV listening with editable audience preferences. Define preferences for visual energy, motion pace, complexity, contrast/color intensity, persistence, transition frequency, and tolerance for abrupt changes or flashes. Keep preference values versioned and visible in the report. Do not infer a listener's age, identity, or tolerance from genre alone.

Use these starting editorial hypotheses for genre/listener fit; calibrate them with the supplied music and user review rather than presenting them as established facts about audiences.

| Genre | Proposed visual experience to review |
|---|---|
| Dance | Clear beat engagement, bass-responsive movement, sustained interest through builds and drops |
| Pop | Accessible, varied visuals that follow verse/chorus energy without constant abrupt changes |
| Rock | Strong rhythmic/structural motion that can rise with dense passages and settle with quiet ones |
| Hip-Hop | Clear groove and bass response with room for sparse or vocal-led passages |
| R&B / Soul | Smooth motion and coherent color, with groove response rather than relentless visual agitation |
| Jazz | Detailed, fluid variation that accommodates both restrained and lively performances |
| Classical | Continuity and dynamic development across sustained and percussive passages |
| Ambient | Persistent, gradual evolution with low abrupt-change emphasis |
| Folk / Acoustic | Clear, restrained visual structure that responds to articulation and quieter dynamics |
| Country | Readable rhythmic movement and variation that suit both acoustic and fuller arrangements |
| Reggae | Flowing, groove-led movement that responds to bass and rhythmic interplay |
| Latin | Expressive rhythmic variation that accommodates percussion and melodic passages |

Keep physical response, music/genre fit, audience fit, and technical quality as separate report fields. Explain which preference contributions affect inclusion. Offer optional human review for visual-theme/content suitability when it cannot be measured reliably; never claim that color or optical flow establishes a semantic or cultural match. Lack of such review does not block automatic matching. Keep personal overrides possible. Do not equate energetic visuals with strobing.

The initial TV setting remains Music category; audience preferences shape the exported genre collections. An additional audience selector in the TV app is outside the current request unless the user asks for it.

## Tool workflow and components

Proposed command name: `preset-lab`. The following are the command contract to implement, not commands available today.

1. `doctor`: check engine identity, worker build, GL backend, textures, decoding, output space, and deterministic repeatability fixtures. Report failures before launching a batch.
2. `inventory`: enumerate presets, hash their bytes, map textures, and identify format/feature support. Preserve exact relative paths and duplicate-content relationships.
3. `analyze`: reconstruct executable preset sections, build static dependency evidence, generate probes, launch isolated native runs, and stream feature trajectories into cached results.
4. `validate`: render selected presets with the supplied corpus and optional controlled stem variants. Start with within-track checks; add independent held-out recordings when the corpus expands.
5. `report`: generate a local review report with separate music-fit and audience-fit scores, evidence, warnings, and synchronized comparison clips. Collect explicit per-genre suitable/unsuitable/uncertain ratings and audience/theme notes in a local review file.
6. `export`: validate the results against the target app library and write the versioned metadata bundle plus per-genre app indexes. Permit initial single-track-tested collections with that evidence level in metadata; fail a complete twelve-genre export if a required genre has no eligible members.

Expose `run` as the normal unattended workflow: inventory, reuse or generate measurements, ingest corpus descriptors, score genre/audience fit, validate chosen candidates, and export indexes plus a report. It must complete without ratings, prompts, or manual sequencing of analysis commands. Keep individual commands for diagnosis and targeted reruns.

Expose `match` for recomputing memberships from stored fingerprints and current music/audience profiles without launching render workers. Automatically analyze unknown or changed presets during the next `run`; recompute only affected stages. User-supplied corpus additions update audio descriptors and matching targets automatically. Optional new real-music render checks remain separate from universal fingerprint reuse.

Separate modules for inventory/identity, preset parsing and static tracing, audio/probes, native rendering, feature extraction, genre scoring, review, and export. Use JSON for metadata and JSONL for run events and trajectories. Use filesystem caches initially; no cloud service, database server, or TV-side analysis is needed.

Run one fresh native process per preset/stimulus/seed/configuration. Cap concurrency according to measured GPU memory and worker behavior. Enforce a per-job timeout, preserve stderr and failure details, and continue unrelated jobs after a crash. Resume successful cached jobs by content identity, not filenames alone. Record interruption as incomplete; never convert it to an audio-response result.

## Static dependency evidence

Reconstruct code exactly as this engine does, including duplicates, numbering gaps, section scope, and shader backticks. Parse EEL assignments, expressions, and control dependencies; account for init, per-frame, per-vertex, custom shape, and custom wave execution. Trace audio inputs through scoped intermediates, persistent state, and q variables to visible outputs. Include waveform/sample inputs and shader audio uniforms, not only bass/mid/treb names.

Classify sinks as structural transforms, geometry, visibility, color, or texture/shader effects. Emit source paths and line/section evidence, for example `bass -> q1 -> zoom`. Keep static reachability and impact class separate from measured strength. An expression mentioning bass does not prove visible audio response.

Handle shader dependencies with scope-aware parsing and conservative control/data propagation. Mark unsupported constructs and incomplete analysis explicitly. Avoid declaring absence of audio dependencies when parsing was incomplete. Do not execute preset expressions in Python or infer a full dependency graph from a token-frequency regex.

## Controlled rendering

Build the same projectM commit and patch series as the target app. Fingerprint both plus every analyzer instrumentation patch. Add test-only controls for synthetic time/frame count, all active random sources, stable texture enumeration, and evaluator reset. Disable automatic preset changes and transitions during primary characterization; use a clean engine and cleared feedback buffers per run.

Use matched runs with the same initial state, seed, clock, frame count, and common warm-up audio. Divergence must be absent before an intervention. Fresh processes reset evaluator state. Repeatability is guaranteed only within a recorded build/backend/configuration after passing repeat checks; different GPUs need tolerance-based comparison. Identical seeds alone do not remove random-consumption differences caused by audio-dependent branches. Measure ensembles and retain that uncertainty.

Start with 256×144 at 30 fps, four seconds of common warm-up, and twenty seconds of measurement for screening. Extend uncertain/slow-start presets to sixty seconds. Validate representative candidates at 512×288, 30 and 60 fps, three seeds, and on the TV. Keep all raw durations and settings in the run manifest; these are proposed operating defaults, not established classification thresholds.

Generate silence, steady multiband carrier, low/bass/mid/high spectral probes, amplitude modulation, isolated attacks, tempo variations, and sustained changes. Use PCM stimuli through projectM's actual audio pipeline and record the resulting engine band values. An injected frequency can affect multiple bands; sub-bass is an external probe response, not a native MilkDrop variable.

Keep two audio-path identities:

- Controlled PCM for scientific experiments, with fixed and documented gain, resampling, channel mixing, and clipping policy.
- Captured or explicitly simulated Android Visualizer waveform behavior for TV validation, including sample/callback cadence and the latest-window feeding behavior. Mark a simulation as approximate until checked against device capture.

For stem comparisons, compare the full mix and aligned leave-one-source-out variants at a shared gain. Never independently normalize variants in a way that erases the intervention. Validate alignment and clipping. Label isolated-stem rendering separately from source-removal sensitivity; neither implies reliable source detection from an arbitrary mixed song.

## Dynamic fingerprint

Compute feature trajectories from the final composited display framebuffer, not projectM's intermediate feedback texture. Retain timestamps, audio envelopes/onsets, engine bands, and render diagnostics.

| Family | Measurements and interpretation |
|---|---|
| Spectral response | Matched-control changes in visual feature trajectories for each probe; measured band trajectories, response delay, uncertainty across seeds |
| Source response | Controlled stem/removal experiments when supplied; evidence and missing-value status for each source |
| Motion | Optical-flow density and speed; fitted translation, rotation and radial expansion; fit residual as irregular motion; acceleration and jerk |
| Appearance | Mean/quantile luminance, spatial contrast, saturation/chroma, Laplacian edge energy, visible coverage |
| Temporal behavior | Flash frequency/magnitude, persistence after stimulus cessation, smoothness, beat/onset locking and lag |
| Technical quality | Blank/near-blank and clipping ratios over windows, static/flat output, load/render failures, texture/shader warnings, performance |

Normalize flow by image dimensions and time; describe each metric's units and normalization version. Optical-flow fit residual is an irregularity proxy, not a universal measure of mathematical chaos. Keep raw metrics before creating normalized ratings.

Compare visual feature trajectories against both silence and steady-carrier controls. Intrinsic animation must not count as strong musical response. Use onset-aligned and lagged tests plus shifted/shuffled onset controls to distinguish beat locking from unrelated periodic animation. Pixel difference remains supporting evidence only. Visibility weighting prevents a tiny reactive dot from earning a high whole-scene response score.

Record load failure, warnings, near-blank output, flat output, and renderer mismatch as different conditions. Zero GL errors alone do not prove a valid image. Check initial quality thresholds against known fixtures; permit later calibration against reviewed clips. Automatically extend uncertain darkness/slow emergence to longer runs, then exclude unresolved candidates with evidence and offer optional review. Do not wait for manual verdicts or permanently blacklist presets because they contain a shader operator or failed on an older engine.

## Automatic genre matching and optional calibration

Characterize each preset with a universal synthetic battery once per engine/asset/configuration identity. Genre scoring is downstream computation and does not require a new synthetic battery per genre. Real-music validation remains an additional render stage; it is not eliminated by the universal fingerprint.

Start with editable, versioned genre and audience profiles over the measured features and auditable linear contributions. Treat the initial profiles as hypotheses: genres are heterogeneous, and energetic jazz or quiet dance must remain valid examples. Avoid unexplained hard-coded scores presented as measured truth. Normalize using a frozen calibration set and record its identity; adding presets must not silently change existing scores. Compose genre fit and audience preference penalties explicitly, retaining both component scores and the quality verdict in the result.

Extract reusable descriptors from the supplied music: spectral balance, onset/beat structure, dynamic range, energy changes, and temporal variation. Combine them with explicit genre/audience preferences and measured preset response to rank candidates automatically. Preserve the matching model and reference descriptors so expanding the corpus requires automatic descriptor updates and scoring, not a new manual analysis exercise. Initial music-render checks establish observed fit for the sample recording; fingerprint-based predictions for other cases retain their evidence status.

Offer optional calibration from human suitable/unsuitable/uncertain ratings of synchronized clips, including a separate audience-fit judgment. Neither initial export nor later matching requires human ratings. Retain optional feedback and overrides and reuse them on subsequent runs. Begin with the supplied one-track-per-genre corpus. Hold out entire recordings and preset content families when evaluating generalization after expansion; do not report such generalization from the initial corpus. Report per-genre sample counts, reviewed decisions, and disagreement where available; report false inclusions/exclusions only against an identified reviewed reference set. Permit multi-genre membership and manual overrides with evidence/reasons.

Export eligibility requires successful runs, sufficient quality evidence, complete required measurements, and an explicit profile/inclusion decision with its evidence state. Initial measured/profile-selected collections can be exported for TV testing with single-track/provisional provenance; identify unreviewed decisions and missing independent validation in the tool report and bundle. Exclude failed or incomplete candidates, and honor human rejection/overrides. Do not fabricate measurements or present provisional membership as broadly validated genre suitability. Human review improves the initial collections; broader corpus validation follows later and is not a prerequisite for the first usable test tool.

Butterchurn is optional differential validation for a small sample after the native pipeline works. A mismatch triggers review, not an automatic verdict that either renderer is correct. MilkDrop3-only features remain explicitly unsupported in the core projectM/MilkDrop2 classifier.

## Result identity and export contract

Every result records schema version, exact preset relative path and SHA-256, texture-pack digest, engine commit, app-patch digest, analyzer-instrumentation digest, worker/metric/genre-profile/audience-profile versions, audio/probe hashes, seed, backend/driver, resolution, fps, duration, and run status. Separate raw evidence, normalized fingerprint, genre scores, audience fit, overrides, and export inclusion. Cache raw renders separately from metrics and scoring so changing an audience profile or genre threshold only recomputes downstream results.

Missing metrics use null with a reason. Never use zero to mean not measured. A score has an evidence state such as provisional, reviewed, or validated; do not invent a statistical confidence value unless the procedure defines it.

Write an export bundle containing:

- `manifest.json`: schema version 1, generation identity, source library digest, renderer identities, genre ID/label/count entries, audience-profile identity, corpus sample counts and evidence level, calibration/validation provenance, and checksums for all exported index files.
- `presets.jsonl`: exact preset paths/hashes, fingerprint evidence, genre fit and inclusion decisions, and exclusion/review reasons.
- `genres/<id>.idx`: only included members, in the same UTF-8 `filename<TAB>weight-MB` format as the current app index; use weights from the app's authoritative index rather than recalculating them in the analyzer.

Reject absolute/traversing paths, unexpected genre IDs, duplicates within a category, malformed weights, unknown preset references, stale hashes, and non-finite scores. Current bundled presets are flat filenames; require this for version 1 app export. Sort rows bytewise for reproducible diffs. Write to a staging directory and publish only after validation succeeds. Changing weights or preset bytes requires regenerated export metadata.

An app-side import/check command verifies the bundle against current preset and texture bytes, engine patches, and the master index, then copies validated genre indexes into `core/src/main/assets/preset-genres/`. CI repeats that check. Runtime consumes the small category indexes; it does not hash every preset at startup.

## ProjectM-TV behavior

Add an `OptionRow` labelled Music category to the main settings panel. Default to All; offer the twelve labels from the fixed catalog when their verified export indexes are available. Index verification checks integrity and membership; it does not claim independent musical/audience validation. Persist the genre ID in preferences and apply it after native initialization. Display the active collection's eligible count.

Keep one immutable master catalog and existing memory weights/skips. Derive the active shuffle/order from the selected category intersected with known, non-skipped members. Route next, random, previous, automatic/beat changes, blank recovery, and prefetch/prewarming through that same active membership.

Apply category changes on the render/control path without GL operations on the UI thread. Rebuild the active order, reset the cursor and random-ahead choice, clear category-crossing history, invalidate old prefetch/prewarm results, and suppress stale automatic-switch requests. Tag queued work with a generation so an old-category worker result cannot become the next displayed preset.

If the displayed preset belongs to the new category, it may continue. Otherwise switch immediately with the app's established hard-cut path even when Auto change is off. Previous after a category change must never cross back into another category. Shared presets do not become new duplicate assets.

Unknown persisted IDs or missing/malformed category assets fall back visibly to All. If every member of a selected category is skipped or fails, fall back to All and communicate that no eligible presets remain; never silently keep the category label while selecting outside it. A valid one-member collection must remain usable without an endless avoid-current retry loop. All preserves the current library behavior and existing skip-list policy.

The selector is manual. Music category changes preset selection; it does not select a music source, alter playback, or infer the currently playing track's genre.

## Verification and completion gates

| Requirement | Evidence required before completion |
|---|---|
| Independently runnable tool | Clean maintained build/install instructions; `doctor` and end-to-end CLI run outside Android; no dependency on missing prototype paths |
| Faithful static tracing | Fixtures for indirect q-variable paths, reassignment, scope, conditionals, persistent state, custom waves/shapes, shader uniforms, duplicates, gaps and comments; supported paths match engine execution |
| Deterministic experiments | Repeated framebuffer/trajectory captures with identical config; no pre-intervention drift; logs identifying every controlled random/time path |
| Valid dynamic metrics | Known motion/flash/blank fixtures; real preset clips; intrinsic motion and tiny-dot regressions; meaningful beat controls; nulls for missing stems |
| Reliable batch operation | Crash/timeout/interruption/resume tests; cache invalidation for changed presets/textures/engine/audio/metric/profile identities |
| Automatic reusable matching | Unattended `run` produces all twelve indexes with no ratings file; repeated unchanged runs launch zero render jobs; `match` never launches a render worker; profile/corpus changes reuse valid universal fingerprints; unknown/changed presets are analyzed automatically |
| Genre-specific collections | Initial twelve-track corpus is sufficient; measured, nonempty collections for all twelve genres; correct single-track/provisional provenance and review/override behavior; broader validation can follow later |
| Matching correctness | Genre/audio/style/audience contributions are independently inspectable; supplied-music checks for selected candidates; counterexamples distinguish quiet/persistent, beat-responsive, frantic/flashing, tiny/blank and incompatible output; predicted-only membership cannot be described as music-tested or broadly accurate |
| Audience-aware selection | Editable audience profile affects downstream scoring without rerendering; separate fit components and explanations; review overrides; no genre-based demographic inference |
| Correct export | Schema/checksum/path validation; exact membership and memory-weight consistency with the current 9,606-entry master catalog or its current successor; reproducible output |
| TV category integration | JNI/library tests for every selection path, singleton/empty sets, skips, restart, history, rapid category changes, stale prefetch/prewarm work and fallback |
| Runtime compatibility | Built app plus SHIELD demonstration of All → Dance, automatic and manual switches, persistence and fallback; representative desktop/TV comparison clips |

Use the already supplied recordings alongside synthetic fixtures throughout development. The initial deliverable must work end to end with one sample per genre and carry its evidence limits accurately. Broader corpus expansion and independent validation are follow-up work, not a reason to block the agreed first test. Do not ship fabricated measurements or memberships to make the selector appear complete.

## Proposed implementation sequence

1. Maintain the native worker and deterministic probes; establish doctor/repeatability checks against the current engine.
2. Implement inventory, static dependency evidence, streaming feature extraction, and resumable batches.
3. Implement ingestion of the supplied twelve tracks, synchronized review clips, separate genre/audience scoring, and verified exports with explicit single-track provenance.
4. Integrate category imports and all native selection paths; add the persisted TV control and regression checks.
5. Generate the full library's initial genre collections, exercise review/overrides with the supplied tracks, validate on the SHIELD, and document the tested workflow and corpus-expansion path.

This sequence preserves the full end state while using the user's accepted initial corpus. Written-spec review and an implementation plan precede product code.
