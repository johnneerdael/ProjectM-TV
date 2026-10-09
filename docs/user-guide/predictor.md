# The road ahead: predicting presets from source

Today's [preset moods](predictive-collections.md) come from **watching** each preset. Every preset is rendered for 14 seconds at 128×72 pixels, and its frames are measured: how much the picture moves, how often brightness jumps. This works, but it has hard limits. A short, tiny render of synthetic audio cannot see how a preset reacts to real music, develops over minutes, or looks at 4K, and every new preset must be rendered before it can be placed.

The **predictor**, in development on the [`feat/predictor-visual-loop`](https://github.com/johnneerdael/ProjectM-TV/tree/feat/predictor-visual-loop/tools/milk-analyzer) branch (pull request [#45](https://github.com/johnneerdael/ProjectM-TV/pull/45)), takes the opposite approach. It **reads** the preset and works out its behaviour mathematically, the way an engineer would read the code, instead of looking at pictures.

!!! note "Status"
    This page describes a **direction**, not a finished design. The predictor is research in progress: it is not merged, and it does not change the moods shipped in the app. The formulas, profiles and thresholds below show how the work is currently sketched. Expect them to change as the research matures. The published beta collections stay as they are until a source-based version has been validated well enough to replace them.

## Measuring pictures vs. analysing source

| | Today: measure rendered frames | Predictor: analyse the source |
|---|---|---|
| Input | Pixels from one 14-second render | The `.milk` file itself |
| Method | Optical flow and brightness differences | Executes the equations in MilkDrop's phase order, follows shapes, waves, warp transport, feedback and final colour expressions analytically |
| Audio | One synthetic test signal | Traces which outputs depend on which audio bands, and can test counterfactual inputs with everything else held fixed |
| Resolution | 128×72 | Resolution-independent quantities: viewport units, events per second |
| Uncertainty | A single number per measurement | Explicit intervals; *unknown* when a quantity cannot be established |
| New presets | Must be rendered first | Analysed directly from text |
| Explanations | "This preset moves a lot" | Which code moves what, and why |

The difference matters most for the cases pictures handle badly. A colour pulse that is fast but small, a preset that is calm in silence but violent on a drop, or one whose structure only appears after a minute: all of these are visible in the code even when 14 seconds of 128×72 frames miss them.

## From code to physical measurements

The predictor first produces **feature records**: physical quantities with units, evidence type and support, kept separate from any opinion about mood. Examples:

| Feature | Unit | From the source |
|---|---|---|
| Motion speed, acceleration, jerk (95th percentile) | viewport widths per second, per second², per second³ | Shape and wave vertices, warp transport, by divided differences over the evaluated timeline |
| Discontinuities | events per second | Sudden jumps in geometry |
| Coherent brightness changes | transitions per second × brightness step | Reachable final-colour expressions and their discontinuous branches |
| Bass response | normalized RGB difference | The same program run with and without a bass change, all else identical |
| Palette | warm/cool −1…1, coloured share, hue bins, hue rate | Final colour functions at declared points |
| Structure | normalized coordinates | Nonlinear warp, symmetry, feedback complexity |

Each value says what supports it. Missing support yields *unknown*, never a guessed zero. A preset that stands still produces a genuine 0; a preset whose motion cannot be established produces no number at all.

## From measurements to moods, and much more

Scores are computed from those features with explicit, inspectable formulas. As an illustration, the current research sketch, which is likely to change, uses:

```text
Intensity  = max(1 + 99·(0.28·speed + 0.12·acceleration + 0.08·jerk
                        + 0.32·flashes + 0.12·brightness jumps + 0.08·bass response),
                 1 + 99·flashes)
Smoothness = 100·(1 − 0.35·acceleration − 0.45·jerk − 0.20·discontinuities)
Warm, Cold = from the palette's warm/cool balance
Psychedelic = palette diversity, nonlinear warp, feedback complexity, symmetry, hue evolution
```

Every input is normalized to a saturation scale (for example, speed saturates at 0.75 screen widths per second). Unknown inputs widen the result into an interval instead of being dropped. A preset is placed in **Chill**, **Normal** or **Intense** only when its whole intensity interval fits in the band and is at most 10 points wide. Chill additionally requires *proven* bounds on speed, acceleration, jerk and the absence of flashes for the whole preset. When the evidence is not strong enough, the predictor abstains instead of guessing.

Because the measurements and the preferences are separate, the same analysis can serve many different tastes **without re-running anything**:

- **Genre profiles:** starter profiles exist for ambient, chillout, trance, melodic techno, techno, hardstyle, pop, hip-hop, jazz and classical. *Melodic techno*, for example, targets intensity 35–75, smoothness 85–100, a subtle bass response, strong symmetry and feedback that fades within 0.3–1.5 seconds.
- **Viewing profiles:** neutral, gentle home TV, focus, psychedelic and party.
- **Your own profile:** a small JSON file listing what you want (a target range per feature or score, how much it matters) and hard limits (for example "never more than one flash per second").

Changing a profile simply rescores the stored features. That opens the way to collections tuned to a genre, a room or a person, rather than three fixed moods.

## How well does source prediction work?

The predictor is tested by writing down **20 observable claims** per preset before any frame is rendered, then grading them against captures from the unchanged published engine. In a randomized audit of 100 bundled presets:

- **85 of 100** scored 95 or more out of 100; 71 matched all 20 claims;
- among the 88 presets it could analyse, the mean score was **98.8**;
- the 12 it could not complete hit numeric domains the analyser could not resolve at that checkpoint: mostly undefined powers (such as negative bases), plus division, dot-product and nonfinite-coordinate cases which were retained as unresolved in that audit;
- the audit's own target is 100 of 100 presets at 95 or more, so this run did not pass it (mean 86.95 when unanalysable presets count as 0). It used the published 2.3.11 engine, before the projectM 4.2 rebase.

These are historical behavioural-rubric grades. Average agreement measures closeness; the pass rate depends separately on the chosen gate. [How the score is measured](authoring/testing.md#how-are-you-measuring-97-accurate) explains the 20-claim arithmetic, a real 97.5 example, the 5% numerical tolerance, visual assessment and the difference between 85/100 and 85/88. Later repairs and source-only corpus exports do not retroactively increase this audit's accuracy.

## What remains before it replaces today's moods

- **Extraction coverage.** Palette features already come from source. Complete visible motion, spatial colour coverage, pulse proofs, structure and full feedback analysis are still being built. Until they are, many presets correctly come out as *unknown*.
- **Calibration.** The formula weights are explicit starting assumptions, not yet fitted to viewers' judgments.
- **Validation at scale.** The 100-preset audit covered 60 frames at 256×144 with one audio stream. Longer runs, real music and 4K detail must be checked before the source-based index replaces the measured one.
- **An intentional migration.** The shipped collections will change only in a release that says so, with the new index verified like the current one.

## Options it could enable

Keeping *measurement*, *preference* and *validation* separate makes several features possible. None of them is a commitment yet; they illustrate where this could go:

- **Moods that explain themselves:** "Intense because of three full-screen flashes per second on the kick", instead of a bare number.
- **Genre collections:** presets matched to ambient, techno or classical listening, using editable profiles instead of a fixed model.
- **Personal profiles:** your own limits and preferences, such as warm colours only, no flashes, or slow motion, applied to the whole library at once.
- **A gentle first-use default** for living rooms, with strict proven limits on flashing and abrupt motion, instead of a guess.
- **Instant placement of custom packs:** presets you upload could be analysed from their text, without a render pass.
- **Transparent uncertainty:** presets whose behaviour cannot be established are marked unknown, rather than silently placed in the wrong collection.

## Further ahead: generating presets

If preset behaviour can be predicted from source, the same machinery can in principle work in reverse: search a restricted, typed preset grammar for programs that satisfy a set of feature constraints, such as "smooth, warm, bass-reactive, no flashes". This is an idea for later, not part of the current work, and it makes no promise about aesthetic quality. The hand-written *Aurora* test presets already show the first half: a preset designed so that its behaviour could be forecast before rendering ([details](authoring/testing.md#aurora-a-preset-designed-to-be-predicted)).

## What to expect

When it lands, the result should be moods that explain themselves and new presets that can be placed without rendering. It should also leave much more room to make collections your own.


## Use the predictor output in another tool

The [predictor export contract](predictor-export.md) documents the feature envelope,
all 47 simulated fields, strict extraction, provenance and unknowns, with downloadable
JSON Schema, catalog and real examples. It also describes the limits of using
these measurements for a Rust/wgpu adaptation and the additional semantic
information needed for effect-family recognition or generation. The contract is a
research checkpoint, separate from the accuracy rubric and shipped collections.
