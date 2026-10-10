# Equation phase snapshots and uniform mesh controls

An unresolved main-frame scalar can be fixed across a mesh pass while varying
between frames. The source graph now tags bare/local persistent reads with
`equation_phase` and `value_binding`. Native source34 PerPixelMesh.cpp245–300
captures/reloads main controls for every vertex; PerPixelContext.cpp75–106
copies readonly values and Q state separately. Pixel-mutated Q/local state
remains distinct. Original MilkDrop2 pools/copy intent remain the reference;
this addition does not manufacture native initial values or a state recurrence.

Pure main/init scalar snapshots can supply uniform transport proofs. Shared
registers, pixel-local state and random/memory calls remain guarded. Finite
input assumptions remain named; known source value envelopes do not establish
state values, rates or continuity. Control JSON explains the uniformity basis.

Phase metadata exposed two naming/identity mistakes. Main locals named rad/ang
must not be geometric coordinates solely by name. More seriously, structural
input identity previously ignored phase and could merge a main scalar rad with
a pixel radius in conditional branches. Failing fixtures preceded both repairs;
input keys now preserve phase/binding/state scope, and cached spatial-dependency
checks retain actual pixel/shader coordinates. No native/preset files changed.

Ten phase controls cover persistent/bare main reads, unknown rates/values,
pixel-local state, copied/mutated Q, exported metadata, shared/rand guards,
coordinate names and mixed-main/pixel conditional identity.291producer focused
tests pass. Independent final review passed109phase/transport/family controls
and found no actionable findings. No equation/shader/frame execution or visual
judgment feeds this addition.

The unchanged100source sample all exports with exact bytes/hash joins and ZIP
CRC. Affine-component support25→31, initial radial zoom58→59, displacement25→26.
New uniform rows: zoom1, rotation2, stretchX/Y2each, translationX/Y6each,
centreX/Y4each. The groups overlap and unknowns remain:64affine,36radial,
69displacement;5disconnected for each component. These are component coverage
counts, not complete-preset appearance/mood accuracy. Preset-operation time
35.096746seconds, maximum1.752591seconds, not a corpus/hardware guarantee.

`census.json` preserves exact source joins, changed rows, statuses and identities.
Raw paired archive: `build/preset-corpus/source-phase-uniformity-final-2026-10-10/batch-000001.zip`.
SHA256 `0f007d5cbb09566cac2fec7b1316efe4ed9a689e56a5e2c9074fcaa4a64299c2`.
Reader SHA256 `754e4f4129db585cb4f7d5bee915d6bb24ac10ab25901ee7ef0832ce50744afc`.
Matching source34targets published2.3.36bytes; runtime qualification remains
separate/pending. No shared device/full corpus was operated. Mood, flashing,
full feedback and visible motion remain unresolved work.

Final prepared suite: **2,630tests and92subtests pass in146.74seconds**.
After clarifying one exported condition sentence to include frozen snapshots,
25affected focused tests pass and a fresh100export has identical descriptors
except that sentence and record hashes. Final producer identities are retained.
Strict MkDocs and whitespace checks pass. These are source-rule checks, not
whole-preset visual or mood accuracy.
