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
