# Source prediction and native validation loop

User target: ten consecutive fresh randomly selected presets, each achieving at
least 80/100 agreement for full visible behaviour: structure, motion, colour,
flashing and feedback. Any failed comparison resets the streak. Diagnose the
missing calculation/context, add a focused correction and regression evidence,
then evaluate new random presets. Do not substitute audience-score agreement.

Reuse the existing mathematical source forecaster and semantic analyzer imported
from `feat/preset-audience-scoring` at4cd38ad9. Preserve production beta rankings,
models and their provenance. Do not use saved native scores or captures as forecast
inputs. Freeze source, model, input/profile, predictions and score rubric before
capture. Keep diagnosis reruns separate from fresh-case acceptance.

The explicit behavioural rubric is in ignored `build/visual-loop/protocol.json`:
five equally weighted categories, four observable claims each. Each earns5for a
supported match,2.5for a partial match,0for mismatch/unknown. Require total>=80,
no critical contradiction and a matching capture/source/profile. This is an
operational descriptive-agreement grade, not a calibrated perceptual probability
or proof about every possible input/time/random state. Retain quantitative
source-field/observed-field diagnostics separately; pixel similarity alone cannot
satisfy full-behaviour acceptance.

Native validation uses unchanged published standard core2.3.4 AAR via its exact
JNI class/library and assets, on task-owned emulator5596. The renderer host is
256x144 GLES3,30fps,48x32mesh. The declared18-second PCM schedule contains quiet,
melodic, kick-driven and silence phases. Actual random realization remains an
external input; representative source random inputs are explicit. No shared
corpus/device is operated. All raw frames/audio remain under ignored build/.

Initial engineering work: port the existing source modules without replacing
production rank/model code, prepare CPU math adapters for the same41-patch engine,
fix their missing quad-line geometry/state dependencies, freeze one random case,
then render and compare it. Prepared adapters must finish before dependent tests.
Preserve older-profile failures; do not rewrite expectations simply to claim a
passing suite. Current source-forecast controls:27tests and16subtests pass after
the waveform adapter repair. Broader imported tests still require profile
reconciliation; no blanket compatibility or appearance claim is made.

Archive each prediction and outcome; when ten consecutive fresh cases pass,
audit the frozen artifacts, random sequence, five category scores and final model
revision. Follow repository validation, documentation and PR/review workflow for
retained code changes. Do not mark the goal complete before the streak is proved.
