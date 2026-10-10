# Static effect mechanisms

The experimental predictor identifies supported mathematical constructions from
parsed preset code: polar depth sampling, angular mirror folds, spatial twists,
feedback flow, recognized fractal recurrences, waves and point/shape primitives.
This path constructs no display frames and consumes no audio signal.

!!! note "Feature branch"
    PR67 merged into the experimental `bug/predictor-grid-memory` branch. It has not changed
    the app's shipped mood collections. Reproduction requires that branch's
    prepared source31 parser and Python environment.

## Interpret the evidence

A preset can contain several mechanisms. Detection follows contributing outputs,
consumed vector lanes, loop state and drawing controls. Unused helpers, discarded
coordinates and disabled components do not establish an effect. Unsupported code
and excessive symbolic complexity remain explicit unknowns.

The visible appearance is conditional on active stages, masks, opacity, texture
content and feedback initialization. A Julia recurrence does not promise a
prominent colorful fractal. Dots do not establish independently simulated particles.
No recognized family is not proof that a preset lacks an interesting effect.

## Export without simulation

From the prepared implementation checkout:

```sh
build/preset-lab-venv/bin/python tools/milk-analyzer/effect_family_export.py path/to/preset.milk --output ~/Downloads/ProjectM-TV-static-single
```

Omit the preset argument to analyze the bundled pack, or supply a folder. Default
output is `~/Downloads/ProjectM-TV-static-effect-families`. Matching JSON and exact
`.milk` bytes are zipped every100 attempts, plus a final partial batch. Failures
retain a null analysis and their reason. Completed records resume under the same
identities; cache hits skip parsing and detection. Use a fresh process after code
edits. Changed run identities require a new output folder.

No frame-count, resolution or FPS setting is required. Those belong to the
separate [47-field simulated export](predictor-export.md).

## Consume the result

The envelope has `export_kind: preset-effect-families`, exact preset/parser/model
identities, and an `analysis` object. Schema1, policy `source-effect-families-v1`,
contains `families`, `stages`, `unknowns`, declared profile and hashes. Each family
includes its mechanism, stage/component, parameters, dependencies, contribution/
appearance conditions and source evidence. `record_sha256` hashes the semantic
record with only that key omitted.

Join numerical records by exact preset SHA256 and compatible context. Preserve
null parameters and conditions. Use these descriptors to select an original
Rust/wgpu implementation; they are not a scene graph, shader, palette, full
composition, visual accuracy score or native4K performance guarantee.

A calm swirl and an aggressive swirl can share a construction. Downstream mood/
genre matching needs motion, flashing, palette and response-strength evidence,
alongside editable audience assumptions. This export leaves `mood_labels` and
`genre_labels` empty.

The [complete field/API reference](https://github.com/johnneerdael/ProjectM-TV/blob/6680a910e988b481f4a5fc56bfbd400d7d059b40/tools/milk-analyzer/EFFECT_FAMILIES.md)
and [primary-source research with exact witnesses](https://github.com/johnneerdael/ProjectM-TV/blob/6680a910e988b481f4a5fc56bfbd400d7d059b40/docs/superpowers/research/2026-10-09-static-effect-families.md)
describe the supported constructions and boundaries.

## Structured baseline and audio controls

The continued experimental branch adds `analysis.visual_description` alongside
the mechanism record. It gives source component IDs, numeric form/colour codes,
parameters, contributing transformations and per-element bass/mid/treble control
routes. It is intended for editable preference matching and future approximate
reconstruction of the preset's characteristic look.

Generated RGB phase palettes are described with channel coefficients and control
programs. Inherited image/feedback colours remain conditional. A recognised
fractal plus a generated varied palette can support psychedelic potential;
flashing permission and calm viewing remain separate. Exact positions, screen
coverage, perceived response magnitude and match confidence can still be null.

Each route identifies the changed control—for example shape radius or rotation,
feedback zoom, or one RGB component—with its source unit, available linear gain,
formula/Q bridge and branch/clipping/resource conditions. These are engine
bands and volume inputs, not isolated instruments or vocals.

Supported time-driven RGB oscillators now include nominal rates, periods and
unmasked component-speed estimates. For example `.5+.25*cos(2*time+phase)` has a
period of pi seconds and maximum nominal component slope of.5 per second.
Each channel can abstain separately when its phase depends on audio, textures,
state, integer steps or unsupported math. Estimates exclude frame sampling,
float rounding and the engine's10000-second shader-clock reset. A colour cycle
is not automatically a prominent brightness flash; masks, coverage and final
composition still matter. These fields do not grant a Chill recommendation.

Audio routes also identify supported band-triggered switches. A shape opacity
formula `if(above(bass,1.2),.8,.1)` reports a bass threshold of1.2 and a source
opacity jump of.7. The frequency depends on the music crossing that threshold.
Nested switches retain their trigger but leave the whole-control jump unknown;
later masks and feedback can hide or amplify a change. These are switch candidates
for further interpretation, not measured screen flashes.

Custom shapes now include nominal size and polygon-area formulas. A square with
radius0.2 occupies an unclipped area fraction of `0.02*aspectY`; on a16:9viewport
that is about1.125%. Copies are counted separately, so the summed estimate does
not resolve overlap. Dynamic sizes, opacity, clipping and later shaders can still
prevent a visible-area estimate. Init-only audio captures remain separate from
live reactivity, and changing persistent variables do not masquerade as fixed sizes.

Named shape and feedback controls also describe supported drift and oscillation.
For `x=.5+.1*sin(2*time)`, the source-coordinate excursion is±.1, period pi seconds,
and nominal peak control speed.2 units/s. Audio/state/nonlinear formulas can still
abstain. A constant feedback rotation is applied each feedback step and may keep
moving the picture; zero change in its control value is not a still-image claim.
These source rates do not yet establish perceived screen movement or a mood score.

The composition record explains normal feedback versus display paths, candidate
drawing order and source texture reads. It preserves hidden feedback drawings
when a composite replaces the displayed image. Blur ages, native/authored detail
and effective texture bindings remain conditional. Warp discard can retain stale
composite pixels, so the record does not promise that display operations can never
affect later feedback. This is useful pipeline context, not a finished scene graph.

Shape materials now describe centre-to-edge RGBA gradients, border colours,
source-alpha blend style and texture requests. Dynamic colour channels retain
their formulas and unknown values. Colours use the TV engine's wrapping conversion,
so values above1or below0are not simply saturated. Named-image requests retain
unverified binding/hash fields and the previous-main fallback. These inputs help
an independent approximation choose a fill/material; later shaders still determine
the final palette. Audio routes also cover edge, border and texture controls.

For known untextured fills, `fill_contribution` combines polygon area with the
interpolated colour/opacity gradient. It reports nominal average alpha and
source-alpha-weighted RGB, including their covariance, then supplies per-aspect
area coefficients. A fully opaque polygon and one fading to a transparent edge
can therefore have different predicted contributions despite the same radius.
Copies sum with overlap counted repeatedly. Textured or unresolved values remain
unknown, and clipping, borders, destination colour and later shaders still
determine what appears on screen. This is a source contribution model; final
prominence and mood eligibility remain pending.

Supported audio-dependent radii now have nominal area formulas and band
sensitivities. For a square with `rad=.2+.1*bass`, the area coefficient is
`.02+.02*bass+.005*bass²` per aspectY. The JSON records which bands participate,
their cross terms and available opacity/colour factors. This helps an independent
renderer reproduce size response from supplied audio values. Clipped screen
coverage, later feedback and perceived bass response are still separate; state,
nonlinear or unresolved radius programs retain unknowns.

Supported warp expressions now describe how previous-image RGB is weighted or
mixed, including spatial copies and constant colour injection. An ideal.98colour
gain halves a floating-colour perturbation after about34.3warp evaluations;
stored pixels need not follow that decay because rounding and new drawings matter.
Image-driven coordinate maps can add nonlinear feedback response and remain
outside that persistence estimate. These source coefficients help describe
feedback character, while actual trail lifetime and mood confidence remain unknown.
Conditional colour bounds now retain each sample's signs and channel weights.
They can estimate an ideal perturbation decay bound for multiple copies or
negative/channel-mixed gains. The premise keeps sampling nonexpansive and
independent of image contents; pixel rounding, new drawings and later processing
remain outside it. This describes part of feedback character without declaring
the complete preset stable, calm or nonflashing.
Custom warp programs that explicitly use the engine's supplied vertex colour
also receive its known decay factor. Dynamic factors remain unknown; this does
not add decay to programs that omit it or claim a measured GPU binding.

Texture lookup records now describe supported scaled, translated, reflected
and sheared image copies with matrices and inverse feature placement. They keep
the warp mesh separate from original coordinates, and link supported offsets to
audio bands or time curves. For example, sampling at twice the distance from the
centre makes an isolated feature half as wide. Wrap, clipping, colour weights and
feedback still determine how many copies become visible. These records give a
consumer spatial context without claiming screen speed or dominance.

Supported polar lookup records describe reciprocal/logarithmic depth and angular
wrapping, with shared-centre/metric checks and source repetition rates. They keep
small authored numerical differences rather than claiming perfect symmetry.
Mixed polar records also describe constant matrices that combine angle and depth
into both texture axes. Axis swaps retain the authored angle orientation while
proving the unchanged radius; literal matrix argument order is preserved.
These parameters help an approximation choose a radial layout; texture contents,
colour weights and feedback still decide whether it looks like a visible tunnel
or kaleidoscope.

Procedural-form records now identify supported repeating radial glow fields:
bright-core and inverse-radius falloff math, cell centres, mapping programs and
phase/audio controls. Distinct generator formulas retain separate records;
identical repeated formulas may share one, so this is not a layer count. This helps distinguish
mathematically generated spot fields from sampled images or independent particles.
Local core area does not establish visible screen coverage or final brightness.

Supported image-driven flow records now quantify how sampled colour changes
lookup coordinates, retaining individual positive/negative channel weights and
conditional displacement ranges. This explains gradient and feedback-flow math
without reading an image. Nested image lookups can add nonlinear response, so
these direct coefficients do not establish visible movement speed or intensity.

When all authored blur ranges are constant, source analysis now derives the
engine's repaired scale/bias inputs. That resolves more blur-driven flow formulas
without rendering. Dynamic ranges remain unknown, and known decode inputs do not
prove the final image's colours or movement.

Raw texture-colour transfer records now preserve supported RGB mixtures of
main imagery, blur and noise, including signed channel weights and source bias.
These coefficients help explain colour mixing and contrast operations. They do
not certify a final palette, softness or sharpness: image history, coordinates,
clipping and later passes still matter.

Native roam/slow-roam inputs now carry their sine/cosine formulas and clock
identity into source programs. Their unwrapped float32 render clock remains
separate from wrapped shader time. These can explain modulation without
simulation, though combined final colour programs may still lack a complete
palette-cycle or flash description.

Presets that consume the native hue input now describe its four time-driven
corner colours, shared-channel normalization and mesh interpolation. Random
phases remain explicit inputs. This adds a colour ingredient to the mental map
without claiming the shader's final palette; red-only use can still be grayscale.

Built-in waveform records now distinguish supported circle, stereoXY, momentum,
angled/two-channel and spectrum constructions with their source controls and
audio-channel roles. Draw style and mode conversion follow the target engine.
Actual shape still depends on sample data, opacity, clipping and later feedback;
extended-mode names do not guarantee a star or flower silhouette.

Ordered colour-processing records show supported tone steps per RGB channel:
power/gamma, inversion, tint/bias and clipping, with channel permutations and
unknown base programs retained. They follow the patched translator's abs/domain
power handling. A known tone suffix can help an independent renderer adapt a
material, but underlying sampled colours and mixed/nonlinear shading can still
be unresolved. This does not verify the resulting palette or recognizable look.

The [machine contract and numeric dictionaries](https://github.com/johnneerdael/ProjectM-TV/blob/feat/predictor-static-output-bounds/tools/milk-analyzer/SOURCE_APPEARANCE.md)
and [JSON Schema](https://github.com/johnneerdael/ProjectM-TV/blob/feat/predictor-static-output-bounds/tools/milk-analyzer/export-contract/source-appearance.schema.json)
explain how to read every field. Successful source extraction is not a calibrated
image match, a complete scene graph or a confident Chill recommendation.

## Reducing numerical work

Static proof can also reduce execution. The experimental `uniform-proof-v1`
shader policy evaluates spatially independent subexpressions once per update,
while retaining spatial and texture-dependent work. It remains opt-in; it does
not change the exported metric definitions.

The separate `shader_lowering_policy: cached-program-v1` reuses static shader
programs instead of lowering their source again each update. Runtime inputs,
state and texture reads still execute; source/context changes rebuild the
affected program. Texture-history metadata remains update-specific. The initial
fixed100-source check matched172 contributing graphs across five updates and
reduced lowering time by4×. Complete short forecasts had mixed timing results,
so this remains opt-in and is not a claimed corpus speedup. See the
[program-reuse evidence](https://github.com/johnneerdael/ProjectM-TV/blob/6680a910e988b481f4a5fc56bfbd400d7d059b40/docs/superpowers/evidence/predictor-program-reuse/README.md).

A separate uniform final-expression primitive can calculate colour and sampled
flashing descriptors without constructing display frames. Its caller must prove
that this is the selected complete final composite and supply matching inputs
and storage settings. It retains unknown motion values and rejects unsupported
dependencies. The current numerical qualification is OpenCV5.0.0 optimized
ARM64/NEON; other backends abstain.

None of the fixed100 sources in the initial dependency census qualified for
that narrow final-expression route. Its synthetic speedup therefore cannot be
applied to the pack. General feedback and spatial shaders still require broader
reasoning or execution. See the
[controls and measurement scope](https://github.com/johnneerdael/ProjectM-TV/blob/6680a910e988b481f4a5fc56bfbd400d7d059b40/docs/superpowers/evidence/predictor-uniform-descriptors/README.md).
