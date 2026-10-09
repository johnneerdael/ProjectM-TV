# I07 retained stereo-band policy packet

Source-only retained-policy preparation. No builds, helpers/canonical/Git edits, GPU or device operations occurred. Retain upstream both-channel band analysis; no shipping left-only option or change is proposed. Parent owns execution/images.

## Source/provenance and mono boundary

Original MilkDrop2 `plugin.cpp:9512–9581` copies both waveforms for rendering, but computes its analysis FFT from `m_sound.fWaveform[0]` only. Band sums use fSpecLeft, then existing short/long temporal averages produce relative values. Original left-only combination is a source fact, not an executed Windows result.

Current PCM.cpp computes both channel spectra, combines each bin as .5*(L+R), then updates all three Loudness bands from that combined spectrum. [Upstream commit494269ef50479afeda1278dd0adc1002e5acfab3](https://github.com/projectM-visualizer/projectm/commit/494269ef50479afeda1278dd0adc1002e5acfab3) intentionally fixes right-weighted content under-reacting. Per-channel render waveforms remain separate. This policy predates TV patches and is already in the pinned upstream engine.

The actual TV capture route is MainActivity.onWaveform→ProjectMJNI.addWaveform(byte[],length)→native pending uint8 buffer→FeedAudio→projectm_pcm_add_uint8(...,PROJECTM_MONO). PCM::AddToBuffer duplicates mono samples into both input channels. Given equal initial history and ordinary bounded finite PCM, equal spectra give .5*(S+S)=S, so this combination difference is inactive. Output4K does not create stereo. A mono preservation image should demonstrate invariance, not manufacture a difference.

State caveat: a generic host switching from stereo to mono with fewer than576 new samples can retain unequal older ring-buffer contents. Require a fresh mono-only context or fill the full576-sample analysis ring before claiming equal-channel invariance. Actual TV startup/history uses the mono route; this caveat does not invent stereo TV transport.

## Stage scalar control

`stage-controls.json` declares immutable spectrum inputs and prior temporal state; its rational expectations are source arithmetic models, not executions. Use512-bin arrays, a single active bin inside each tested band, L band sum1/R3, prior short/long averages1, frame100 and secondsSinceLastFrame1/30. Current combined sum2 yields long average≈1.008 and relative≈1.984127; left-only yields1. The short relative current≈1.785714 also changes. Actual float32 rate adjustment uses nested powers; record it and use a declared tolerance rather than asserting rational bit identity.

Capture original/combined band sums, short/long averages before/after, CurrentRelative/AverageRelative, raw FrameAudioData bass/mid/treb and attenuated values **before EEL**. Mutable EEL vol or bass reassignment is not the raw audio oracle. Test channel swap, right-only, equal-channel mono, zero/silence and initialization frame49/50 boundaries. A left-only source-oracle sibling must share FFT, time/state, aligners, compiler and engine otherwise, isolating combination. It is not a complete original Windows audio implementation.

For precise prior state, a test-only access adapter or source-instrumented copy may be needed because Loudness's accumulators are private. Do not set public EEL variables to pretend that the analysis pipeline executed. Do not repeatedly call UpdateFrameAudioData within the same frame; it updates temporal state.

## Controlled full stereo execution

Use the existing native C API `projectm_pcm_add_float(handle, interleaved, samplesPerChannel, PROJECTM_STEREO)` or direct PCM::Add(...,2,count) in a source instrument. The public count is samples **per channel**; storage is LRLR,2×count floats, within−1..1. Preserve original sample order, chunk sizes, ring phase, amplitude conversion, elapsed time and frame count. Public stereo C API exists; the shipping Java/JNI byte waveform bridge remains mono.

Warm two fresh roles using the same equal-channel bounded tone for≥60 frames, one576-sample chunk/frame, fixed30Hz analysis interval. Then hold left amplitude.05 and change right.05→.15 with identical frequency/phase, record per-channel spectra and the actual resulting band sums before predicting relative values. Current averaged and left-only source-oracle roles must have identical pre-step state. Run channel-swapped step, right-only step, mono duplication and identical stereo control. Use the same protocol for bass/mid/treble stimuli, selecting bins from captured production spectra rather than assuming a sample-rate/FFT-bin mapping. Whole pipeline FFT/windowing/float effects mean the isolated1/3 band sums are not automatically guaranteed by PCM amplitudes.

At source stage, parent can freeze generated float32 stereo PCM bytes and transported/effective hashes. For Android unchanged-AAR stereo evidence, first verify that a genuinely stereo-capable bridge can reach an existing exported stereo-capable native entry point without altering the published library. Public upstream C API declarations do not prove those symbols remain exported/reachable in the packaged libprojectmtv.so. If a new source-instrumented bridge/native build is required, identify it as new source-engine evidence; do not relabel its results unchanged-AAR. Bridge count/layout/logging must show both channels reached PCM. No stereo bridge is implemented here. The≥60-frame mature-audio protocol also requires its own frozen lifecycle; it cannot borrow the existing≤30-frame cold JNI progress qualification.

**Invalid shortcut:** concatenating/interleaving L/R into ProjectMJNI.addWaveform bytes produces one longer mono signal; PCM duplicates it. Assigning different named L/R vectors in a helper without exercising the native channel argument is likewise not stereo execution. Do not label either as unchanged-library stereo proof.

## Finite diagnostic/oracle siblings

- `diagnostic-live-bass.milk`: exposes real bass in q1 and maps it to an opaque red border width. Requires declared real stage input/temporal state; stereo differences require the stereo native route.
- `oracle-averaged-stage.milk`: same geometry with an explicit q1=2/1.008 scalar, yielding width≈.07460317.
- `oracle-left-only-stage.milk`: explicit q1=1, yielding width.05.

All use a compiled constant-black warp, disable other geometry/effects, and have finite bounded widths. Require the actual custom warp compiles; fallback/black output alone is not proof. Capture q1 and the actual submitted border geometry before interpreting final pixels. Explicit-value siblings are **stage-oracle surrogates**, not original runtime results or proof that mono input became stereo. Their algebraic inputs approximate the declared float source-stage expectation; parent must bind actual float results for tighter geometry comparisons.

Use matched256×144 output/authored canvas, mesh48×32, detail/diffusion inactive, Native Standard, no transition, frozen seed/clock/FPS/progress and valid transport metadata first. A separate Native4K preservation/retained-policy qualification must record actual output/reference/canvas dimensions and audio lifecycle. Do not compensate by changing Native rendering/trails or audio amplitudes between roles.

## Exact original candidates and limits

`Sjadoh - Fortune Teller.milk`, SHA25660d9ae2f5adb14e3cd6beb99da7643e33ba103178aae84d152305cfc67e2b088, line42 uses bass directly in zoom; line43 adds bass to wave_r; line46 uses bass_att in warp. This provides scalar→geometry provenance. It also has gamma/echo/large wave alpha/nonlinear warp and historical misspelled identifiers, so final images need actual stage logs rather than assuming every visible change is I07.

`fiShbRaiN - city slicker.milk`, SHA256382688e31a8e1ed82968f1a2be31d09ce37041d2f104b5171936e452dd7dbc05, lines226–227 drive motion-vector red/green from bass/treb. Its vector alpha.05, warp and time-dependent offsets make it a follow-up stress witness. Hold renderer/motion policies identical; downstream saturation may hide some raw audio/color changes.

These are source-exact candidates, not executed affected originals. identities.json records hashes and line provenance. The supplied8985 lexical candidate files are conditional audio-input consumers, not a confirmed affected census. They cannot establish stereo impact under the production mono route. No corpus-wide, cross-GPU, Windows audio, original FFT bit-identity or external consumer transport claim is made.

## Cost and disposition

Retention adds no new shipping work. Upstream's existing policy combines512 bins (one add/multiply per bin) in a512-float temporary; both FFTs already existed before that upstream change. Do not infer a new FFT pass. No performance measurement is needed to call this unchanged behavior; no performance improvement is claimed.

Disposition proposed: retain stereo average as an intentional upstream improvement and document original left-only divergence plus mono TV invariance. If stereo source/unchanged-library images remain unavailable, record those gates explicitly while keeping the policy. A left-only compatibility mode requires separate demonstrated need, versioning and consumer migration; it is not justified by a broad lexical inventory alone.

Parent executed `pcm_policy_controls.cpp` directly with the current production PCM/Loudness/FFT/aligner sources. The common480frame uint8 mono transport uses576sample tails; every spectrum bin and allcurrent/attenuated bands are identical between averaged and left-only combination stages. Coherent stereo step/channel-swap/right-only inputs execute actual PCM::Add(...,2,...), show asymmetric differences, and equal stereo remains identical. No GPU/no Windows audio equivalence is claimed. See pcm-policy-controls.txt and executed-pcm-identity.json. Actual frame60 averagedbass1.993457794 vs left-only1.004740357 is frozen into explicit finite border surrogates under executed-fixtures; their Native images are pending, and they are not stereo JNI execution. Status remainsOPEN pending Native owner images.
