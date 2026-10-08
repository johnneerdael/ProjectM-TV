# Frozen authored/native numerical controls

These scripts reproduce the task-local U01 workflow. Run from the predictor
worktree root only after the exact prepared source adapters and full published
AAR/runtime deployment described by the analyzer README are present. They rely
on explicitly identified local paths and the task-owned API34 emulator; they are
not a generic install or full-corpus rendering command.

1. `freeze-controls.py` computes three independent 30-frame 3840×2160 predictions
   using the exact v2.3.27 source. Canvas dimensions and Medium/High detail gain
   are separate controls. Each effective field, input and model file is hashed;
   duplicate fields share compressed storage without dropping frame records.
2. `capture-controls.py` requires all three complete freezes before its first
   draw. It verifies ownership and remote full-AAR/Java/native/clock/PCM/config
   identities, captures all 30 frames, compares RGB numerically and retains
   metadata, logs and compressed fields. The maximum declared allowance is one
   RGB8 level. A mismatch stops further capture until diagnosed.

The scripts operate only `emulator-5596`, AVD
`projectmtv-predictor-visual-loop-api34`, with its observed owner PID24651.
A changed owner or helper/context requires a new declared deployment; never edit
an existing freeze to fit a new context. Ordinary source tests alone do not
certify native appearance. These controls earn zero random-preset streak credit.

All three source predictions were frozen before capture. The published AAR
passes all 90 numerical frames: Standard maximum RGB8 error0; Medium/High error1.
The Standard artifact gatherer stopped after successfully reading all frames
because the clock-only helper produces no shader-random log. Its saved unique
field and metadata were recovered without re-rendering; that limitation is
recorded in `qualification-checkpoint.json`. The corrected gatherer persists
frame/header records before pulling mandatory logs and resumes completed cases.
These controls contain no authored random references, and no random-input
certification is claimed. U01 remains open for blit and feedback/geometry checks. The public-JNI helper supports P=N4K; forcing
N1920/P4K is unavailable, so scaled physical-blit source tests remain separate
from an actual core-transition witness.


## Feedback and geometry follow-up

A fourth independently frozen 30-frame 4K control exercises zoomed authored
feedback, a moving coloured custom shape and a shared-register increment in its
frame equation. All 30 predicted fields differ, so the comparison checks evolving
state rather than repeating a static picture. Native geometry replay preserves
one equation execution per frame. The maximum RGB8 difference is one level.
All 120 source/native frame records were independently decoded and compared;
metadata records 30 completed frames, one indexed preset, no skips and the
1280×720 authored canvas for every control. No source/preset repair or native
library modification was needed. U01 disposition awaits the final requirement audit.

`physical-blit/` contains the separate six exact RGBA8 operator comparisons.
These are bound to the recorded backend and do not certify an arbitrary GPU or
an actual two-preset Auto transition. Current default and unknown resource guards
remain; only explicit allocated authored/native contexts use the new route.


The feedback fixture's effective decay is **1**, zoom **1.002**. Its appended
`fDecay=.97` loses to the earlier `fDecay=1` because the parser keeps the first
occurrence. The freeze is preserved unchanged; this control does not certify
.97 decay. Its moving alpha-blended shape, zoomed recurrence and one register
increment per frame remain the tested behavior. Raw parsed values are retained.
