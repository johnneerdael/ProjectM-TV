# Source-only behaviour and preference evidence

The experimental export now includes `analysis.visual_description.static_behaviour`.
It derives conditional component evidence from the typed program graph, without
evaluating audio/frame sequences, equations, shaders or rendered images. The patched
source reader parses the preset; compiler evidence may qualify stage selection.

## Consumer fields

| Field | Meaning and units | What it does not establish |
|---|---|---|
| `context` | Declared viewport pixels, feedback frames/second, scalar input ranges | Actual device or input trajectory |
| `flashing.records` | Component brightness delta, RGB-infinity-norm change/second, periodic cycles/second and conditional event schedules | Visible strobe timing or whole-image contrast |
| `motion.contributions` | Conditional viewport-unit/second envelopes, audio partial response, backward-sampling and forward-transport distinctions | Typical optical flow or actual trajectories from displacement alone |
| `prominence.by_component` | Clipped support, opacity, final difference gain and displayed contribution intervals | Guaranteed dominance, visible contrast or accumulated feedback coverage |
| `colour.components` | Source RGB/HSV anchors, hue-family possibilities, conditional final palette and contribution weights | A measured palette or a unique image |
| `classification` | Known-source potential index, conservative interval, overlapping candidate and eligible preference bands | Calibrated human mood accuracy |

`classification.predicted_bands` uses the known component potential estimate.
Unknown contributing activity suppresses Chill suggestions even provisionally;
zero-valued partial components do not supply a calm point estimate.
`classification.eligible_bands` additionally requires complete bounded evidence;
unknown contributing activity or execution/domain gaps veto eligibility. Consumers
must not automatically classify a provisional Chill candidate as safe/calm. The
source-potential value is not a measured mean, maximum frame intensity or p95.

## Preference assumptions

The initial policy `static-activity-preference-v1` uses references of0.75 viewport
units/second for motion,1 RGB unit/second for brightness change,0.30 RGB units for
flash contrast and2 cycles/second for flash frequency. These are editable future
preference assumptions, not a human-fitted classifier. The overlapping bands remain
Chill1–30,Normal25–75,Intense70–100. Stronger partial evidence can support an intense
candidate; missing effects cannot certify absence of flashing.

Brightness deltas for materials already contain alpha. Their screen weighting uses
support and final difference gain, without multiplying alpha a second time. Motion
uses opacity-weighted displayed contribution. Tiny, offscreen, transparent and
disconnected effects have separate controls. Feedback can grow or redistribute a
source contribution, so an initial small support is not a lifetime ceiling.

The colour producer joins shape centre/perimeter/border colours, wave colours and
qualified transfer rules. It preserves unknown inherited feedback/image colours.
Hue candidates and encoded-RGB temperature tags describe possible ingredients;
they do not prove a warm/cold or psychedelic overall appearance.

## Reproducible reference and cohort

The default reference is1920×1080 at30 feedback frames/second. A caller may supply
`--behaviour-context context.json` with `viewport`, `feedback_fps`, optional named
`reference_profile` and finite `scalar_input_domains`. These values participate in
cache identity. No context silently changes the authored shader/audio engine.

`static_behaviour_validate.py` runs an unchanged source inventory against frozen
source-bound offline compiler records and one immutable reader per worker. Optional
`--symbolic-python` and `--proof-python` enter reusable SymPy/Z3 worker sessions.
The manifest freezes model, source, reader, context, compiler-record and component
identities. Compressed per-preset rows retain errors and partial evidence. Counts
of useful descriptors or provisional bands are coverage, not appearance accuracy.

Independent producers retain their own partial results when another producer
exhausts its bounded traversal. Producer failures are exported and veto automatic
eligibility. Separate bounded caches prevent one failure from poisoning other
component calculations.

The new builder is still being qualified. See the task plan and saved cohort
results for current checkpoints; a synthetic constant-colour control passing does
not certify general feedback presets.
