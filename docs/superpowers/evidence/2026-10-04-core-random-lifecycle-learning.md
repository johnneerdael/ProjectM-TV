# Published-core random lifecycle

Two 30-frame controls used the unchanged published2.2.4 AAR, the owned API34
emulator and a separate rand/srand forwarding observer alongside the existing
runner clock helper. The observer records values, caller offsets, thread IDs and
order. Single-thread Android adapter output matches with/without observation.
The observer serializes logging, so its timing can change concurrent scheduling;
these are observed instrumented lifecycles, not guaranteed uninstrumented ones.

Both traces contain 2,419 records: the runner's initial seed, two core reseeds and
2,416 draws. Four 184-draw constructor patterns and sixty 28-draw variable-load
patterns account for every intercepted draw. Two shader objects are constructed
on the render thread and two on a background thread. The background reseed occurs
after 35 loads in one run and 36 in the other, between complete load patterns.
This is a concrete reason that a single seed/two-object replay is insufficient.
The source's ProjectM constructor seeds from time(nullptr), overriding the runner
seed; the analyzer's private source replaces that expression with lab::Seed(1),
which must not be mistaken for the published AAR's behaviour.
Disassembly of the pinned AAR confirms this call sequence: time(nullptr) at
0xd0d94 followed by srand at 0xd0d98, returning to the traced offset 0xd0d9c.

Explicit replay now accepts reseed events with strict uint32 seed identity.
Reseeding consumes zero draws and preserves existing shader objects, including
their preset vectors and stored rotation parameters. It resets subsequent frame
random draws, not the objects' lifetime. Invalid seeds remain errors.

The two traces were mapped to complete constructor/load events using caller
patterns pinned to library SHA
11169fb1a75ee9ccfe607db44bee5022a42410486605a3eb01f43e0e65221755.
The mapping requires every event's full call pattern to be contiguous and owned
by one thread; interrupted or unknown patterns fail. It is a diagnostic probe,
not a general source-independent event recognizer. Explicit event order and
seeds were fed into the Android source adapter. No captured pixel values were
fed into replay. Replayed composite rand_frame and rand_preset predict every
captured RGB8 value with zero maximum error across 30 frames each.
Load times are taken from the scheduled frame time; these colour controls do
not validate the phases of time-dependent rotation matrices.

These checks verify numerical/lifetime understanding conditional on observed
CPU inputs. They do not count as blind visual predictions, automatic renderer
lifecycle assembly or whole-preset accuracy. The first qualitative probe reused
a misleading helper-return label in its prediction metadata; its original files
are preserved, and no blind accuracy claim is made from those labels.

Local probe sources and raw traces are under
`build/milk-analyzer/android-learning/`: `rand-trace.cpp`,
`replay-core-random-trace.py`, `random-frame/` and `random-preset/`.
Hashes, explicit events, record positions and render settings are checked in at
`tools/milk-analyzer/fixtures/core-random-lifecycle-proof-2026-10-04.json`.

Next obligations: infer constructor/fallback/prefetch events from real source
state, account for all shared stream consumers, establish the real seed input,
and represent or explicitly reject mid-event concurrent interleaving. Coordinate
those inputs with texture/equation RNG domains without substituting host streams.
