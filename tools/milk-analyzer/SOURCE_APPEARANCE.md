# Structured source appearance contract

`analysis.visual_description` extends the existing static effect-family record.
Schema1, policy `source-appearance-and-control-traits-v1`. It describes approximate
baseline constructions and per-element audio controls for preference matching
and future reconstruction. It does not replace the47-field numerical contract.
No equations, shaders, images or display frames are executed by this producer.
Machine shape schema: `export-contract/source-appearance.schema.json`; source,
context, digest and reconstruction-readiness checks remain separate.

## Produce and locate

Use `effect_family_export.py` as documented in `EFFECT_FAMILIES.md`. Each paired
`.milk`/JSON result contains `analysis.visual_description`. The outer analysis
and envelope identify exact preset/source/parser/model/profile/compatibility
hashes. Use a fresh process and new output folder after code changes.

The descriptor has its own `record_sha256`: canonical JSON with sorted keys,
compact separators, no NaN, and only that hash key omitted. It is a content
identity, not a signature or calibrated confidence. `schema_version` and
`policy` identify the interpretation contract.

## Top-level fields

| Field | Meaning |
|---|---|
| `elements` | Stable source component/layer IDs, approximate forms, colour and control links |
| `execution_unknowns` | Unresolved loading, branches, loops/domains and interpretation conditions; these are not rendered failures |
| `uses_rendered_images`, `uses_shader_execution`, `uses_equation_execution` | All false for this source-only producer |
| `appearance_match_accuracy` | Null until separately validated; do not infer it from a successful parse/test |
| `native_warp_recipe` | Nominal uniform native feedback sampling map with runtime aspect/texel inputs; dynamic/radial controls remain unknown |
| `native_warp_transport` | Uniform affine-component scale/area envelopes from supported varying controls; aspect-corrected geometry, not screen motion |
| `native_radial_zoom` | Positive uniform-control radial zoom component, nominal factor/derivative envelopes; no tunnel or full-map label |
| `native_warp_displacement` | Per-step backward-sampling RMS expression/bound in aspect-corrected source coordinates; not visible speed |
| `elements[].wave_material` | Built-in wave RGB clamp/normalization and mode/volume alpha recipe; threshold jump candidates are not visible flashes |
| `native_input_bindings.main_frame_q` | Source main-frame q1..q32 snapshots packed into shader float32 banks, with unknown dynamic values retained |
| `feedback_envelope` | Conditional varying affine-in-main RGB coefficient/gain envelopes; colour-only, not full feedback persistence |
| `texture_colour_envelopes` | Independent affine texture-input RGB boxes and history/external input norms; not shared-history recurrence gain |
| `nonlinear_texture_colour_bounds` | Per-channel nominal ranges through supported nonlinear scalar operations on declared texture inputs; no sensitivity or mood score |
| `sampling_geometry.stages.*[].oscillatory_displacement` | Symbolic uniform-controlled wave amplitudes, spatial phase gradients and baseline lookup map; conditional nominal deformation bounds |
| `sampling_geometry.stages.*[].sample_value_offset_envelope` | Conditional nonlinear local sample-value offset ranges; no image-gradient or whole-feedback sensitivity |
| `elements[].audio_routes[].nominal_audio_response` | Sufficient nominal scalar control-change bound per audio input unit, with other inputs fixed; no time-rate or visible response score |
| `motion_controls[].time_switch_events` and material raw curves | Supported nominal threshold/floor event schedules; nonexhaustive and independent of displayed flashes |
| `activity.flashing`, `activity.motion_intensity` | Conditional blackout mechanisms, feedback-step components and polygon speed bounds; overall visible intensity remains unknown |
| `mood_matches.chill.eligible` | Null until sufficient activity evidence exists |
| `mood_matches.psychedelic.candidate` | True when contributing fractal and generated phase-palette constructions coexist through the recognized final colour path; otherwise null |
| `limitations` | Consumer-relevant boundaries |

An appearance-specific work-budget failure may instead return schema1,
`status:"unknown"`, and `unknown_reasons`, preserving the outer family record.
Consumers must handle that variant before reading `elements`.

## Element identity and baseline forms

IDs: `shape_0`…`shape_3`, custom `wave_0`…`wave_3`, `builtin_wave`,
`shader_warp`, `shader_composite`, and `mesh_warp`. IDs refer to source roles;
they are not tracked particle identities. A later RGB-independent composite
removes disconnected earlier elements. Position, radius or other dynamic
parameters remain null when no source constant is established.

| Family code | Approximate construction |
|---:|---|
| 1 | Built-in/custom line waveform |
| 2 | Points/point cloud; independent particles are not established |
| 3 | Polygon/custom-shape primitive |
| 4 | Circular/radial curve or band |
| 5 | Polar-depth image sampling: tunnel candidate |
| 6 | Angular/cartesian mirror construction: kaleidoscope/symmetry candidate |
| 7 | Recognized complex quadratic or iterated folding recurrence: fractal construction |
| 8 | Feedback transport, rotation, scaling, advection or nonlinear transformation |
| 9 | Repeating two-dimensional radial glow field; particle identities are not established |
| 10 | Raw planar or native-radius sine/cosine band generator; masks and dominance remain separate |

Multiple codes can coexist. Read `mechanisms`, `parameters` and `conditions`
before choosing a reconstruction. An empty list means no supported construction
was recorded for this element, not a proven absence of interesting appearance.
`approximate_screen_coverage` is currently null. Dominance, shape location,
layer density, exact palette and full image reconstruction remain incomplete.

Existing parameters include polygon sides/instances, complex recurrence subtype
(`julia_style`, `mandelbrot_style`, `unclassified`), bailout evidence, depth-map
kind and sampling scales where proved. Preserve nulls and original units.

### Custom-shape footprint

Shape elements add `geometry`, policy `source-custom-shape-footprint-v1`. This
describes nominal unclipped primitives, not perceived prominence or displayed
coverage. Source31 and MilkDrop2 both construct a regular polygon using
`center=(2*x-1,1-2*y)` and radius `rad` in normalized device coordinates, with
horizontal radius multiplied by renderer `aspectY=min(1,height/width)`.

| Field | Unit / interpretation |
|---|---|
| `radius_ndc` | Signed constant radius after native float32 conversion; null if dynamic/unknown |
| `effective_sides` | Native truncation to int32, then clamp3…100; null outside the conversion domain |
| `configured_instances` | Draw-loop count from preset configuration; equation-written `num_inst` does not change this count |
| `nominal_area_fraction_per_aspect_y` | `n*r*r*sin(2*pi/n)/8`; multiply by target aspectY for one polygon's nominal viewport-area fraction |
| `summed_nominal_area_fraction_per_aspect_y` | Above coefficient times configured count; overlaps counted repeatedly, not union coverage |
| `circumcircle_width_fraction_per_aspect_y` | `abs(r)`; multiply by aspectY for a containing-circle width fraction |
| `circumcircle_height_fraction` | `abs(r)`; containing-circle height fraction |
| `center_source_xy` | Authored source coordinates or per-coordinate nulls; not post-composite screen positions |
| `visible_coverage_fraction` | Null until clipping, opacity, overlap and later composition are resolved |

The denominator8 comes from regular-polygon area `n*r*r*sin(2*pi/n)/2` and
the NDC viewport area4. These nominal geometric estimates omit float32 trig
rounding and raster edges; circle extents need not be the polygon's exact box.
Dynamic radius/sides and instance-dependent sizes retain nulls and reasons.
No target aspect is silently assumed. Borders, texture/opacity conversion,
blend order, feedback and composite shaders can change the visible contribution.

Static equations now honor target frame resets: config/audio fields reload,
main Q reloads init snapshots, shape Q reloads main frame Q, and shape T reloads
init snapshots each instance. Mutable initialized custom locals become previous
state inputs; assignments before reads can reestablish constants. Shared registers
remain inputs. Bare/local state reads carry `equation_phase` and `value_binding`
metadata, retaining unknown values. Main/init scalar snapshots are uniform
across the mesh; pixel-local state, random/memory operations and shared-register
reads do not gain that proof. Uniformity is independent of rates/continuity.
A main local named `rad`/`ang` is not a geometric coordinate solely by name.
Structural input identity includes phase/binding/scope so conditional branches
cannot collapse a main scalar snapshot into a same-named pixel coordinate. Initial audio/time captures use `init:<section>:<variable>` input
names and are not current-frame audio routes. Plain EEL `vol`/`vol_att` are local
names, not registered aggregates; shader packed volume lanes remain codes7/8.
Native EEL `_if` assignments merge branch environments before geometry inference.
Compound assignments update their destinations and count as persistent writes.
EEL division has its own node `eel_divide`: the qualified evaluator returns0
when `abs(denominator)<0.00001`; a proved constant denominator outside that guard
can use ordinary division. Unresolved denominators retain the native guarded
operation. EEL `equal(a,b)` / `_equal` use the distinct exported node
`eel_equal`, returning1 for `abs(a-b)<0.00001` and0 otherwise under finite
operand conditions. The boundary is strict: exactly0.00001 is false. Shader
`equal` remains exact typed equality. Consumers must preserve this distinction;
the shader numerical evaluators do not provide an EEL interpreter. Known
finite EEL operands can resolve a source branch without executing a frame;
unbound operands retain the comparison and its causal routes. Nonfinite
operands remain unresolved by constant folding.
Nested assignment/reference-alias expressions remain explicit gaps
rather than being folded as copied values. No native engine policy is changed.

### Named motion-control curves

Shape and contributing mesh elements add `motion_controls[]`, policy
`source-time-control-curves-v1`. Each entry names its control, source unit,
application and bounded formula export. Supported `curve_kind` values are
`constant`, `linear_time`, `sinusoidal_time` and `unknown`. These describe the
control formula rather than tracking a visible object.

For `a*time+b`, `offset_value=b`, `signed_linear_rate_per_second=a`, and
`maximum_absolute_control_rate_per_second=abs(a)`. No lifetime range is inferred
for an unbounded drift. Constants have zero control derivative, not necessarily
zero image motion. A single `b+A*sin/cos(w*time+p)` exports the original signed
amplitude, full phase program, function code1cos/2sin, phase rate, period/frequency,
range `[b-abs(A),b+abs(A)]` and maximum absolute control derivative `abs(A*w)`.
`rate_unit` is `control_unit/source-time second`; rates are continuous nominal
formula values, excluding clock jumps, rounding, rasterization and frame sampling.

Scalar time phases may select a lane from a constructed vector, nested swizzle
or supported componentwise arithmetic. For example, `float2(time*2+.25,bass).x`
has nominal rate 2 radians/second when used as a trigonometric phase; the unused
bass lane does not change that rate. Dynamic integer conversions, unknown inputs,
texture samples and unexpanded cross-lane operations remain unresolved. Explicit
constant float32 narrowing is preserved, including abstention on overflow; a
failed constant conversion cannot fall back to its unconverted double value.
The projection follows [HLSL component selection](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-per-component-math)
through the existing typed graph rather than executing shader values.

Authored shader add/subtract/multiply/divide nodes carry
`detail.numeric_domain="shader-float32"` in exported expression graphs. Literal
folding narrows each such operation to float32, preserves explicit scalar casts,
and rejects nonfinite conversions. Untagged EEL arithmetic retains its double
domain. This distinction prevents overflowing shader expressions from falsely
cancelling to zero and hiding texture dependencies. It does not certify GPU
constant folding, fused operations or bit-identical runtime values.

Shape x/y units are authored coordinates, radius is the source radius/NDC unit,
and angle is radians. Mesh rotation's control unit is radians per feedback step;
its time derivative changes that per-step amount. `application` explicitly marks
mesh controls as `feedback sampling transform each step`. A constant rot.02 can
rotate sampled feedback every step despite a zero control derivative. FPS, native
warp-time math, feedback composition and visibility are still needed for image
speed; `visible_motion_speed` and activity/mood scores remain null.

Shape elements add `center_trajectory`, policy
`source-planar-control-trajectory-v1`, joining supported x/y curves. Known
constant axes produce a stationary centre; affine-time axes produce a drift
vector and its Euclidean speed. Stationary centres do not imply stationary
radius, rotation or feedback.

For supported common-absolute-frequency sin/cos axes, the descriptor writes
`center_source_xy + harmonic_matrix_source_xy * [cos(w*time),sin(w*time)]`.
The matrix retains signed amplitudes, phase offsets and negative-rate orientation;
`motion_controls[].phase_offset_rad` supplies the nominal constant phase.
The path can be a source-coordinate circle, ellipse or line oscillation.
Common-phase identities and exact matrix rank/Gram checks avoid tolerance-based
geometry labels; a nearly correlated ellipse is not silently turned into a line.
`semiaxis_lengths_source_units` are the descending singular values, and
`maximum_source_speed_units_per_second=w*largest_semiaxis` is an exact nominal
peak, subject to the stated continuous-source model.

Different rates or mixed drift/oscillation keep `independent_axis_curves`, no
guessed global period, and the upper bound `hypot(peak_axis_rate_x,peak_axis_rate_y)`.
`speed_estimate_kind` distinguishes `exact_nominal`, `upper_bound` and `unknown`.
Unsupported axes or nonfinite joint estimates abstain. All positions, dimensions
and speeds remain authored-coordinate quantities before projection, floating
trig/rounding, clock discontinuities, clipping and feedback. Viewport aspect can
make a source circle physically elliptical; `visible_motion_speed` remains null.

Audio/state/nonlinear time and unsupported combined oscillators retain unknown
rates and reasons. Do not infer stationary images from unknowns or constant
controls. The previous per-element audio routes remain alongside these curves.
Native mesh families and control curves share the canonical `mesh_warp` element.
Earlier experimental records could split this role into `shader_mesh_warp` and
`mesh_warp`; `legacy_ids` preserves the former alias when its families are merged.
Do not count those aliases as two independent visible layers. Frozen older records
retain their original IDs and model hashes.

Per-pixel EEL has its own variable context. Only the ten native warp controls,
Q values, registered readonly values, dimensions and coordinates seed its
analysis; private main locals do not transfer. Readonly values copy before main
frame equations, Q values afterward. Warp controls/coordinates reload per vertex;
writable Q/readonly/custom state can evolve between vertices and stays unknown
without an invariant. `state:<section>:<name>` inputs identify those unresolved
state slots; shared-register inputs use `shared:<name>`. Frozen older outputs are
not relabelled with corrected bindings.

### Shape vertex materials and texture requests

Shape elements add `material`, policy `source-custom-shape-material-v1`.
`source_rgba` keeps raw centre/perimeter/border source values; per-channel nulls
remain for dynamic/unresolved expressions. `channel_expressions` preserves their
programs. `centre_vertex_rgba`, `perimeter_vertex_rgba` and `border_vertex_rgba`
apply the existing qualified native float32 Euclidean colour modulo256/255.
These are vertex attributes before texture multiplication, fragment blending and
storage; modulo can approach256/255 rather than saturating to1. Do not treat them
as verified final pixel colours or a complete palette.

The fill is a triangle fan interpolating centre RGBA toward perimeter RGBA;
the border uses its own RGBA. `border_draw_enabled` follows raw source border_a
greater than the float32 literal0.0001f (about0.00009999999747), exported as
`border_enable_threshold`. A double equation assignment.0001 is above that limit,
while a float32 configuration value.0001 is equal and disabled. Negative border_a can wrap positive in the colour conversion
while still disabling the border. Blend style truncates a finite source value to
native int32, then tests nonzero: `source_alpha_additive` uses source-alpha/one,
`source_alpha_over` uses source-alpha/one-minus-source-alpha; unknown flags stay null.

`texture.role` is untextured vertex gradient, named image request, previous main,
or unresolved style. Requested names are author inputs, not observed successful
bindings; `actual_asset_sha256` stays null and `actual_binding_verified=false`.
Named lookup failure falls back to previous main under the selected render path.
The source31 geometry path uses previous-main/authored history, not a newly
observed image. Texture zoom/angle values and programs are retained in source
units. Perimeter UV is centred on.5,.5, with half-radius divided by tex_zoom and
angle `2*pi*j/sides+tex_ang+pi/4`; horizontal radius uses aspectY for main fallback
and1for a successfully resolved named image. Texture/image history and sampling
policy still require their context before reconstruction.

Additional audio routes identify perimeter/border colour, perimeter opacity and
texture zoom/rotation. Known untextured texture controls and disabled border RGB
are not exported as live material responses. Final palette verification and visible
colour contribution remain false/null; later shaders and opacity can hide them.

### Nominal shape fill contribution

Shape elements also export `fill_contribution`, policy
`source-custom-shape-fill-integrals-v1`. For known untextured vertex RGBA in
`[0,1]`, this integrates the incoming source-alpha blend term over the nominal
unclipped polygon fan. It joins the existing geometry and material descriptors;
it does not execute shaders or sample pixels.

Let `C` and `P` be centre and perimeter RGB, with alpha `a0` and `a1`.
Each fan triangle has one centre and two equal perimeter vertices. Uniform
barycentric moments give:

```text
mean_fill_alpha = (a0 + 2*a1) / 3
mean_source_rgb_times_alpha = ((a0+a1)*C + (a0+3*a1)*P) / 6
```

The second formula includes colour/alpha covariance. Multiplying average RGB by
average alpha would be incorrect: a red opaque centre fading to a green
transparent perimeter contributes nominal mean red and green of `1/6` each,
before storage, rather than `1/9` red and `2/9` green.

`nominal_alpha_area_fraction_per_aspect_y` and
`nominal_source_rgb_integral_per_aspect_y` multiply those means by
`geometry.nominal_area_fraction_per_aspect_y`. Multiply the coefficients by
the declared target aspectY for a nominal viewport fraction/integral. The
`summed_nominal_*` counterparts multiply by configured instance count, counting
overlap repeatedly. Values can exceed a whole viewport; they are not union
coverage or a normalized prominence score. RGB integrals are viewport fraction
times encoded source RGB, weighted by source alpha.

Dynamic radius leaves material means available while area integrals stay null.
Dynamic colour channels abstain independently. Unknown alpha, unresolved
texture colour/alpha, or values outside the admitted unclamped domain remain
unknown. Native float32 modulo colours are retained, including small deviations
from authored literals. Borders, clipping, raster coverage, destination colours,
storage clamping and later feedback/composite are excluded;
`visible_screen_contribution` remains null. The blend mode is carried separately:
the incoming RGB term uses source alpha in both supported modes, while the
destination term differs. See the [Khronos blending reference](https://wikis.khronos.org/opengl/Draw_Buffer_Blend).

### Audio-dependent shape area

`audio_area_response`, policy `source-custom-shape-audio-area-v1`, reuses the
constant-affine source analysis for the six EEL band inputs. It accepts a radius
`r=b+k·a` with constant effective polygon side count. The ordered `input_codes`
identify the active bands; `radius_bias` and `radius_gains` give `b` and `k`.
Nonlinear, state/time-dependent and unresolved radius programs abstain. Init
audio snapshots are not current inputs; plain EEL `vol` is not a registered band.

For `c=n*sin(2*pi/n)/8`, the nominal viewport-area fraction per aspectY is
`c*(b+k·a)^2`. `nominal_area_polynomial_per_aspect_y` exports:

```text
area(a) = constant + linear·a + a^T quadratic_matrix a
constant = c*b*b
linear = 2*c*b*k
quadratic_matrix = c*k*k^T
```

The symmetric matrix includes both off-diagonal entries, so cross terms occur
twice. `area_derivative_constant_per_aspect_y` is `linear`, and
`area_derivative_linear_matrix_per_aspect_y` is `2*quadratic_matrix`:
the area gradient is the former vector plus the latter matrix times `a`.
Multiply by target aspectY; derivatives use declared band units. These are
nominal real-valued formulas before float32 radius projection, trig/raster
rounding and clipping, valid only for finite source intermediates and a radius
within the exported finite-float32 magnitude. They are not an exact derivative
of discrete GPU pixels or a response to BPM.

Example: a four-sided shape with `rad=.2+.1*bass` has area polynomial
`.02+.02*bass+.005*bass^2` per aspectY, and derivative `.02+.01*bass`.
At bass2 its nominal area coefficient is.08. Actual clipped coverage may behave
differently. Negative radii retain their squared nominal area.

`area_to_alpha_integral_factor` and `area_to_rgb_integral_factors` independently
carry known fill means from `fill_contribution`. Multiplying area/derivatives by
these factors gives nominal injection coefficients when material is independent
and known. Textured/dynamic material keeps the corresponding factors null even
with known geometry. Instance sums count overlap repeatedly. Constant radius
uses an empty active-band list; unknown radius uses null. Nonfinite coefficient
or derivative estimates remain unknown, and
`visible_bass_response_strength` stays null.

### Reader identity during source34 migration

The static exporter supports an explicit source34 reader as well as the
qualified source31 reference. Its run identity comes from a minimal parser
preflight, and each record retains the actual reader, engine and archive hashes.
`engine_profiles.matches` compares exact identities; `math_matches` separately
admits the known source31-to34 math lineage. Source34 changes only cache/API
files in the prepared snapshot. This does not transfer published-AAR runtime,
actual sampler binding or appearance evidence. Defaults remain source31 until
the candidate v2.3.34 runtime qualification passes.

## Logical composition and sampler flow

`composition`, policy `source-logical-composition-v1`, explains the logical normal
engine path. Previous main goes through warp, drawings/filters and retained main;
display reads an orientation/diffusion exact copy through the final composite.
It is not a complete executable scene graph or a certified recurrence.

`configured_drawing_order` lists candidate shapes0…3, custom waves0…3 and the
built-in wave, preserving native order. Opacity, audio, compilation, termination
and projection remain conditions. `display_elements` links retained description
IDs; an independent composite can hide those drawings while the engine still
draws them into feedback. These lists do not prove prominence or actual visibility.
Motion vectors may modify previous main before warp; darken-center and borders
follow the drawing stages.

`shader_sample_reads` records contributing/conditional source samples by stage:
sampler/canonical texture, logical source role, coordinate/extra-argument DAGs,
intrinsic/LOD, source site/path and sampling policy. Native fixed/legacy stages
record their implicit main input. An unresolved stage has null reads rather than
an empty list. Dead data samples disappear, while execution/domain obligations
remain separate. Typed integer zero masks use the same constant rules as the
effect-family and contribution traversal.

`frame_age` remains null: blur timing and authored/native detail histories depend
on effective render context. `render_context_resolved=false`, conditional detail
path and discard/incomplete-write fields prevent a fixed physical-buffer claim.
Normally the composite changes display only; warp discard can preserve stale
backing pixels containing a previous composite, giving an indirect feedback path.
The record retains that caveat universally instead of promising unconditional
composite/feedback separation. Sampling policies are source interpretations,
not certified runtime units/assets. No complete blend/material graph, recurrence
solution, screen coverage or reconstruction readiness follows from these edges.

## Nominal warp colour transfer

`feedback_transfer`, policy `source-warp-colour-transfer-v1`, describes supported
warp RGB expressions before storage/drawing/detail, holding sampling coordinates
fixed. It is not the complete recurrence or measured trail lifetime.

Native fixed warp uses `min(float32(decay),1)` as a diagonal main-colour gain.
Custom warp receives its authored returned RGB; configured decay is not silently
multiplied unless the program uses the supplied colour factor. Supported custom
expressions are constant-affine combinations of previous-main RGB samples.
`vertex_colour_binding.rgba` describes the native warp input `_vDiffuse`:
RGB is `min(float32(main-frame decay),1)` and alpha is one. Unsupported dynamic
or nonfinite decay leaves the RGB entries null while alpha remains known. The
binding is a source contract (`observed_runtime_binding=false`), not a captured
GPU value. It applies to warp only; unused factors do not multiply custom output.
`matrix_rgb` sums channel-mixing coefficients across sample sites and
`constant_offset_rgb` records a source injection. `sample_contributions` keeps
each site's matrix, coordinate program and sampling policy, so different spatial
copies are not treated as one uniform transformation.

`direct_colour_gain_norm` is the maximum RGB row sum of absolute per-site/channel
coefficients. It bounds direct colour sensitivity with coordinates held fixed,
treating distinct sampled values independently; sample overlap/cancellation can
make actual sensitivity smaller. It does not measure on-screen reactivity.
`uniform_diagonal_gain` is available only for an equal diagonal single-sample
transfer (or zero samples). Image/blur-dependent coordinates mark nonlinear
feedback; unknown coordinate effects retain unknown dependency.

For a supported positive uniform gain `0<g<1` and coordinates independent of
feedback, `nominal_half_life_warp_evaluations=log(.5)/log(g)` describes an ideal
floating-colour perturbation. It does not say when an actual image disappears.
UNORM rounding can preserve dim pixels; constant/drawing injection, clipping,
blur, motion vectors and authored/native detail alter evolution. Negative gain,
nonlinear/pulse gains, blur-colour mixing and unsupported operations abstain
instead of granting a persistence/mood claim. `actual_feedback_persistence` is
always null. Conditions still require valid sampler/input domains, target-stage
selection, complete writes and source termination; discard/stale pixels remain
an unresolved separate feedback route. Composite/display gain is excluded.

### Conditional warp colour bounds

`feedback_transfer.colour_bounds`, policy
`source-fixed-coordinate-colour-bounds-v1`, adds per-channel raw-output intervals
under the explicit premise that each previous-main sampled RGB component lies
independently in `[0,1]`. Lower bounds add negative coefficients to the bias;
upper bounds add positive coefficients. Distinct sample sites remain separate.
For `.1+.6*main(uv)-.2*main(uv*.5)`, each raw channel has interval `[-.1,.7]`;
the direct difference bound is.8 rather than the net gain.4.

`maximum_colour_difference_gain` uses the infinity norm: the largest absolute
RGB change across all sampled values bounds each output change by that norm
times the exported gain. It holds coordinates/non-image inputs fixed.
`sufficient_contraction_bound=true` means the gain is below one, conditional on
image-independent nonexpansive sampling and identical external inputs. False
means this sufficient bound failed, not that the system is unstable; unknown
coordinate feedback leaves it null. The colour-only operator excludes the
actual draw/storage/detail recurrence.

For `0<k<1`, the conditional ideal perturbation half-life upper bound is
`log(.5)/log(k)` warp evaluations. This supports signed/channel-mixed and
multiple-sample operators beyond the single positive diagonal case. Zero gain
does not receive a fake finite half-life. Storage quantization, clipping, drawing
injection, blur, masks/discard and actual frame scheduling are not included.
These are nominal real-valued estimates, not a GPU rounding guarantee.
`actual_feedback_stability` remains null; the bounds establish neither visible
flashing nor a mood category.

## Ordered shader colour processing

`colour_processing`, policy `source-ordered-colour-processing-v1`, records RGB
channels for warp/composite source fields. Each channel has a base constant,
sample channel or unresolved/source expression and `steps_from_base` in execution
order. This is a known outer processing suffix, not a complete shader/material
implementation or a verified final palette. Missing native/default/custom fields
retain null channels and reasons rather than inventing a shader chain.

Recognized steps: power with constant exponent, absolute value, domain guard,
one-minus/constant-minus, constant gain/bias/division, saturate and ordered clamp.
Per-channel sample indexes expose RGB permutation/repetition. Program/coordinate
exports preserve unresolved inputs/resources. Dynamic powers and mixed spatial/
colour formulas can remain in the base expression while known outer steps survive.

The qualified translator inserts abs/domain handling for most pow calls, with
its literal pow(x,1) exception. Those lowered operations are retained in order;
do not silently reconstruct raw-HLSL power semantics. Power's usual bright/dark
interpretation requires usable encoded RGB inputs and a valid exponent/domain.
RGB is source encoded colour, not a verified linear-light/colorimetric space.
Alpha-only/discarded values do not become RGB tone operations. No palette entropy,
warm/cold classification, contrast or appearance score follows from step presence.

## Colour modes

| `colour.mode_code` | Interpretation |
|---:|---|
| 0 | Source-constant RGB, clipped to0…1; actual store/profile remains a condition |
| 1 | All RGB lanes share one signal: monochrome construction |
| 2 | One signal multiplied by a fixed RGB tint; nonnegative/nonsaturating domain required for fixed chromaticity |
| 3 | Shared-phase sin/cos RGB oscillator with distinct channel phase offsets |
| 4 | Colour depends on sampled image/feedback contents |
| 5 | RGB oscillators have independent phase programs/rates; read all three exported programs |
| null | This colour construction is not sufficiently recognized |

Mode3 describes `bias_rgb + amplitude_rgb*cos(common_phase + phase_offsets_rad)`.
`common_phase_expression` exports the shared variable argument without the
constant phase offsets; evaluate that program before adding the RGB offsets.
Sine is expressed as cosine with a−π/2 offset. Arrays are RGB ordered, offsets
are radians, and coefficients follow the parsed source values. A common scalar
mask/feedback multiplier is retained in `shared_multiplier_expressions` and its
visibility condition. Statically zero masks or fully clipped white/black
oscillators cannot establish a varied generated palette.
Mode5 retains each **full** oscillator argument in `channel_phase_expressions`.
`oscillator_function_codes` are1=cos,2=sin; evaluate the corresponding function
on that argument. Its `phase_offsets_rad` are descriptive normalized offsets,
already represented by those programs/functions; do not add them again. There
is no implied shared period or hue count.

Mode3 normalizes cosine's even symmetry and a negative amplitude into a positive
amplitude plus a pi phase shift. It merges identical typed phase terms without
discarding integer conversions. Mode5 keeps original signed amplitudes with the
original function/program; descriptive offsets must never be applied again.
An oversized phase export cannot establish shared phase identity. The colour
record retains `unknown_reasons` for that gap; other understood elements and
inherited texture-colour evidence remain available. Literal folding memoizes
shared nodes and has a65536-distinct-node and64-depth limit.

### Nominal oscillator timing

Recognized modes3/5 additionally export `colour.temporal`, policy
`nominal-affine-shader-time-v1`. Each RGB-ordered entry can be null independently.
The producer derives the scalar phase slope for supported `a*time+b` formulas
with finite constant coefficients; it never samples time or executes a shader.

| Field | Unit / interpretation |
|---|---|
| `angular_rate_rad_per_second_rgb` | Signed nominal slope `a` of each original source oscillator argument, rad/s |
| `cycle_frequency_hz_rgb` | `abs(a)/(2*pi)`, cycles/s |
| `period_seconds_rgb` | `2*pi/abs(a)`, seconds; null for zero/unknown rates |
| `unmasked_component_slope_rgb_per_second` | `abs(amplitude*a)`, nominal maximum absolute oscillator-component slope before masks/storage |
| `channel_status` | `computed`, `constant` (zero phase slope), or `unknown` |
| `shader_time_wrap_seconds` |10000 for the qualified source31 shader clock |
| `visible_flash_frequency_hz` | Null; colour-cycle rate alone is not a visible flash measurement |
| `unknown_reasons_rgb` | Per-channel abstention reason |

These are continuous authored-formula estimates between clock wraps, not strict
float32 derivatives or presented-frame measurements. `_c2.x` supplies shader
time in seconds; `_c2.y` is FPS and does not qualify as time. The published
source31 clock resets every10000seconds; reset discontinuities and frame aliasing
are excluded. Integer casts, nonlinear time, audio/state/texture-dependent phases
remain unknown in this first timing extractor. A shared mask can still vary or
hide the oscillation. No Chill eligibility or flash contrast follows from rates.
Scalar conversions remain in exported phase programs: `int(time)` must not
silently become continuous time.
Mode3's common phase can reverse orientation through cosine-even normalization;
its signed derivative need not equal every original channel's signed rate.
Use the common program/offsets to reconstruct mode3, and full original
programs/functions to reconstruct mode5. Timing arrays are descriptive estimates.

`distinct_channel_phases` is a source-form count, not rendered hue entropy.
`depends_on_time` is1/0 when identified, not a measured rate; FPS/frame input is
not automatically time. `palette_diversity` remains null. Generated colour plus
fractal structure supports psychedelic **potential**; speed, flashing permission,
dominance and user taste remain separate. `guaranteed_visible` remains false.

## Audio routes

Each `audio_routes[]` entry links one input code to one control of its containing
element. There are no stem/instrument/vocal claims.

| Input code | Engine input |
|---:|---|
| 1 | bass |
| 2 | mid |
| 3 | treb/high band |
| 4 | bass_att |
| 5 | mid_att |
| 6 | treb_att |
| 7 | vol: derived band aggregate |
| 8 | vol_att: attenuated aggregate |

Input units are the engine's declared band/attenuated values, not normalized song
volume, dB, an identified kick/vocal or PCM amplitude. Cold start, input level and
history can change them. Explicit Q bridges connect packed shader lanes to main
equation expressions; shape per-frame Q reads use the complete main frame-Q
snapshot, replacing shape-init Q values. Local shape frame writes still override.

Controls: `position_x/y`, `radius`, `rotation`, `colour_r/g/b`, `opacity`,
`outline_opacity`, `zoom`, `radial_zoom`, `translation_x/y`, `scale_x/y`,
`deformation`. Shape coordinates/radius retain MilkDrop source units. Shape
rotation is radians; mesh rotation is radians per feedback step. Zoom/exponent,
UV translation/scale and warp are source controls, not visible speeds.

`linear_gain` is the coefficient of a directly proved linear input term. Unit is
`control_unit / declared audio input unit`. It is null for nonlinear, threshold,
stateful or not-yet-composed relationships. `visible_response_strength` remains
null: an authored gain does not establish screen area, clipping or perceived
reactivity. `has_threshold_or_clamp` identifies contributing conditional/clamping
code; it is not a measured flash event.

### Audio switch sites

Each audio route additionally exports `switch_triggers[]`, policy
`direct-band-switch-sites-v1`. This first extractor recognizes contributing
strict/non-strict greater/less comparisons with a direct band operand, including
reversed operands. `int(bass)` and transformed/state/Q-only inputs do not establish
a direct-band threshold. An empty list is not proof of no switching or flashing.

`threshold_value` is a finite typed source constant when known; otherwise null,
with `threshold_expression` retaining the program if exportable. Its unit is the
declared engine band unit. `comparison` applies to the route's band on the left.
`control_true_value`/`control_false_value` and `absolute_control_jump` use the
route's control unit and are available only for a complete scalar comparison or
conditional with known branches. Nested/masked/composed switches retain null
whole-control levels. Identical constant branches do not contribute a jump.

`scope`, `source_graph_path`, `conditions` and `limitations` qualify the finding.
These are source predicate sites, not certified discontinuities of the final
screen image. Branch reachability, domains, clock/state and later composition
still matter. `trigger_frequency_hz` remains null without declared audio history.
Threshold analysis does not grant Chill eligibility or visible flash confidence.

## Control expression DAG

`expression` and `q_bridge_expressions` use `{root,nodes,complete,resources_resolved}`.
Node indexes start at0. Each node has `op`, `dtype`, `args` (node indexes) and
`detail`. This is a bounded authored control formula, not an exported GPU shader.
At most256 nodes are exported; budget exhaustion returns null.

Common operations: constant/input, arithmetic, negate/unary, construct/components,
cast, member/swizzle, comparisons/select, clamp/saturate, sin/cos and other
recognized source operations. `dtype` preserves source IR type information;
native EEL versus shader arithmetic/profile comes from the control's source
stage/evidence. It must not be inferred as one universal floating-point policy.
Numeric-vector `member` nodes retain `detail.field` and the parent `dtype`;
xyzw/rgba selectors on a numeric vector describe swizzling. The export does not
carry the internal evaluator's separate boolean swizzle flag. Struct/matrix
members must not be treated as vector swizzles merely because their names match.

Unexpanded loops carry `unresolved_loop_plan:true` and `complete:false`.
Direct sample nodes retain sampler/canonical texture, surface/frame, sampling
policy, intrinsic and coordinate convention. Sampled/hidden-loop resource contexts
set `resources_resolved:false`; selected image contents/lifetime, actual bindings,
initial feedback and random inputs must be supplied separately. Consumers must
not execute unresolved DAGs as though they were closed formulas.

## Example interpretation

A shape route with input1, control`radius`, gain.05 says:
"The authored radius grows by.05 MilkDrop radius units per extra bass-input unit,
provided its branch/visibility and later composition retain that change."
It does not promise a5% screen-size increase. A source recurrence7 plus mode3
with RGB phase offsets[0,2,4] suggests a colourful fractal construction; it does
not certify one exact rendered frame or calm viewing.

Future reconstruction should combine element forms, source parameters, palette
generators, relationships and matching declared audio/time/resource context.
This first descriptor does not yet export every geometry map, state recurrence,
shader morph, blob contour, spatial layout or measured response curve. Expand
those obligations based on failed baseline descriptions, not fabricated values.

## Texture sampling geometry

`sampling_geometry`, policy `source-affine-sampling-geometry-v1`, explains the
source's two-dimensional texture lookup maps. Each live RGB-dependent sample
keeps its sampler, canonical texture, site identity, coordinate program and
wrap/filter policy. No texture is loaded or shader executed. Native/unresolved
stages have null sample lists rather than a fabricated identity shader.

`matrix_uv4` is a 2-by-4 matrix with columns `_uv.x`, `_uv.y`, `_uv.z`, `_uv.w`.
For supported expressions, `sample_uv = matrix_uv4 * input_uv4 + offset`.
Offsets retain independent source programs, known constants (null otherwise),
nominal time curves and specific audio routes. The matrix uses constant
coefficients; dynamic scales/rotations, nonlinear/quantized maps, image-driven
offsets and interpolated vertex-colour offsets abstain. Calculations describe
nominal real-valued algebra, not exact GPU interpolation/rounding.

In warp, xy is the native mesh-transformed UV and zw is the original UV. A
`shader_uv` basis therefore inherits the native mesh; `original_uv` bypasses it.
Composite `uv` and `uv_orig` both alias xy. `mixed_uv` retains all four columns
but cannot have a single-basis inverse. `uniform_lookup` has zero spatial
coefficients and likewise does not receive an inverse.

For an invertible single-basis 2-by-2 map M, `inverse_matrix=M^-1` and a known
constant b yields `inverse_offset_uv=-M^-1*b`. A consumer locates an isolated
source feature at s using `p=M^-1*s-M^-1*b`. This reverses the lookup direction:
`(uv-.5)*2+.5` makes a feature half as wide around .5, with local area ratio .25.
`determinant` and `orientation_reversed` describe coordinate handedness; singular
maps have no inverse/area ratio and no orientation-reversal assertion.
`nominal_feature_area_ratio=abs(1/det(M))` is in that coordinate basis, not pixel
area, coverage or final visible size.

Sampling wrap can introduce repeated feature copies; clamp can stretch edge
values. Clipping, masks, source colour weights, texture contents, feedback
history, native mesh and subsequent stages determine which features appear.
Neither repeated-layer count nor `visible_screen_motion` is certified. A bass
route on sample_offset_x means texture lookup shifts along x; apparent isolated
feature motion follows the inverse and can differ from final scene movement.

The basis distinction matches [MilkDrop's authoring guide](https://www.geisswerks.com/milkdrop/milkdrop_preset_authoring.html)
and original MilkDrop2 `vis_milk2/plugin.cpp:3486-3491`; the target patched
source31 binds the same macros in `MilkdropPreset/MilkdropShader.cpp:573-580`.

## Polar projection parameters

Each sample's `polar_projection` describes supported separable angular/radial
texture lookups. It is `not_recognized`, `unresolved`, or `separable_angle_depth`.
`coordinate_lanes` preserves whether angle is texture x or y. The producer must
prove that both use the same native `_rad_ang` input or the same authored affine
plane, including scale, shear and offset programs. A dynamic/nonlinear authored
plane may retain an exact canonical typed plane program with unknown matrix and
centre; it does not become a resolved screen metric. Equal centres with different
radius metrics do not count as a shared anchor. An authored plane exports its
2-by-4 matrix and offset programs; `centre_in_basis_uv` is known only for an
invertible single basis with constant offsets. Native radius/angle retain their
projection/aspect/interpolation obligations and no direct shader-UV centre metric.

For `angle.function=affine`, the angle output is
`input_scale*theta + offset`. `turn_span_uv=abs(input_scale)*2*pi` is its nominal
span across a turn. `frac` describes `output_scale*frac(input_scale*theta+phase)
+output_offset`. `triangular_frac` describes
`output_scale*abs(2*frac(input_scale*theta+phase)-1)+output_offset`. Phase/offset
programs include available time curves and band-specific audio routes with units.
Wrapped angular period is `1/abs(input_scale)` radians; cycles per turn is
`abs(input_scale)*2*pi`. These use the authored numerical divisor rather than a
rounded sector count. `exact_closed_turn_symmetry` remains null: finite precision,
atan2 seams, input transformations and later sampling can break exact symmetry.

Let `u=radius_scale*r+radius_bias`. The depth functions are
`output_scale/u+offset`, `output_scale*log(u)+offset`, corresponding log2/log10
forms, or a linear radius form. The patched translator uses absolute input for
logarithms; `input_absolute=true` then means log(abs(u)), with
`domain_guard_retained=true`. Reciprocal requires u!=0; log(abs(u)) also requires
u!=0. These domains are explicit conditions, not proven reachable-radius bounds.
Dynamic radius coefficients, image/spatial offsets and unsupported nonlinear
functions remain unresolved. `appearance_guaranteed` is always false.

`radial_derivative` provides nominal `coefficient / u**denominator_power`,
using -output_scale*radius_scale and power2 for reciprocal,
output_scale*radius_scale/ln(base) and power1 for log base, and the linear slope
with power0 for affine radius. This describes how sampling density changes with
radius; it is not pixel speed, dominance, trail intensity or final ring spacing.
Authored atan2/radius also require a usable plane and valid origin/domain handling.

This adds reconstruction parameters to a contributing construction without
certifying a dominant tunnel, spiral, number of visible layers or kaleidoscope.
The creator's [authoring guide](https://www.geisswerks.com/milkdrop/milkdrop_preset_authoring.html)
describes warp/composite UV and wrap/clamp sampling. Target log handling comes
from source31 `vendor/hlslparser/src/GLSLGenerator.cpp:1028-1043`; original
MilkDrop2 D3DX intent is kept separate from this patched target policy.

## Mixed polar layouts and literal matrices

`polar_projection.kind=mixed_angle_depth` retains a two-basis texture lookup
`sample_uv = polar_to_sample_matrix * [theta, depth(r)] + sample_offset`.
The angle profile describes raw theta; the depth profile describes the selected
reciprocal/logarithmic/radial kernel. The matrix therefore owns the subsequent
angular/depth weighting and mixing. The two sample-offset programs retain known
values, time curves and band-specific audio routes. This layout can describe
rotated/slanted radial texture repetitions without falsely requiring the final
texture axes to stay separately angular and radial. It does not count visible
repetitions or prove source visibility. Other spatial terms, dynamic matrix
coefficients, quantized maps and unsupported kernels remain unresolved.

A swap of the authored plane's two axes leaves Euclidean radius unchanged. The
shared-radius proof may use that identity while the angle retains its original
ordered plane, including its atan2 argument order. Different centres or metrics
remain separate. Dynamic planes compare typed scalar-axis program identities;
constant-affine planes compare the corresponding rows and offsets. This is a
nominal norm equivalence, not a generic rewrite or exact GPU-arithmetic proof.

Constant matrix/vector products are expanded through the existing typed matrix
arithmetic in `field_math`, with explicit vector*matrix versus matrix*vector
argument order. Matrix graphs containing any input, sample, unresolved storage,
effect or loop are rejected even if native bindings have zero defaults. Only
literal matrix expressions are folded; no audio, texture, equation frame or
preset shader is executed. Nonfinite or unsupported constant operations abstain.
The sampled source coordinate basis, wrap/filter, domain and visibility conditions
from the preceding sections still apply.

## Procedural radial glow fields

`elements[].procedural_forms` retains each distinct recognized generator formula
within its parent element. Identical repeated formulas may deduplicate; neither
record count nor ID is a usage, drawing-layer or particle count. Form
code9, policy `source-periodic-radial-glow-v1`, is the raw scalar
`saturate(gain / length(frac(mapping)-cell_centre))`. Optional per-axis absolute
value inside Euclidean length leaves the generator's radius unchanged. The full
generator and mapping DAGs, source evidence and target identity remain available.
Later RGB masks, tint, inversion, powers or feedback can change its final look.

`radial_gain` and `core_radius_cell_units` are the supported positive constant
gain. The raw generator reaches its saturation limit for radius<=gain in valid
nonzero reciprocal domains; the exact zero-radius sample is not certified.
`cell_centre` is a constant interior point of the unit cell. When the radius fits
inside the cell, `core_disk_area_per_cell=pi*gain^2`; otherwise it is null and
`core_clipped_by_cell=true`. This is area in the generator plane, not a visible
screen fraction. Outer inverse-radius tails remain nonzero, so core area is not
the whole luminous footprint. Gains saturating the entire valid cell are ignored.

`mapping_matrix_uv4` and `mapping_rank_uv4` describe supported constant-affine
mappings. Rank uses exact row minors of the exported nominal coefficients,
not an SVD tolerance that might erase a highly stretched map. GPU precision and
projection remain separate. Known rank below2 and nonspatial phases do not claim a two-dimensional
grid. The spatial guard uses typed native shader `_uv`/`_rad_ang` inputs, never
ordinary shader uniforms named like EEL x/y/rad/ang. Unresolved/dynamic/nonlinear
mappings keep explicit dimensionality
conditions. Phase offsets retain supported motion curves and precise audio
control routes, not pixel speed. Multiple generators retain distinct IDs and
records. `actual_screen_coverage`, `visible_motion_speed` and final mood/flash
confidence remain unknown; `appearance_guaranteed=false`.

[HLSL frac](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-frac)
defines the repeating unit-cell range, and
[HLSL length](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-length)
defines the radial magnitude. The target translator maps frac to fract in
source31 `vendor/hlslparser/src/GLSLGenerator.cpp:1217-1219`. Original MilkDrop2
compiles authored HLSL through D3DX; this source construction needs no repaired
preset, texture label or rendered-frame observation.

## Direct sampled-colour coordinate response

Each texture lookup's `sampled_coordinate_response`, policy
`source-direct-sampled-coordinate-response-v1`, decomposes supported coordinates
into `base_matrix_uv4 * input_uv4 + uniform_offset + sum(M_i * sample_i.rgba)`.
`sample_contributions` retains each input sample's site, sampler/texture name,
coordinate program, sampling policy and2-by-4 `matrix_uv_rgba`. The native UV
bases remain distinct as in the preceding sampling-geometry contract. Source
RGBA samples are opaque inputs; no texture is loaded or pixel inspected.

`direct_sample_gain_norm` is the maximum output-axis sum of absolute per-site/
channel coefficients. It bounds direct coordinate sensitivity to independently
perturbed sample values with their locations fixed. Source dot products with
constant channel weights are expanded into scalar coefficients. Ordinary shader
globals x/y remain uniform offsets; EEL coordinate names do not create shader
spatial inputs. Nonlinear/quantized products and dynamic coefficients abstain.

`conditional_sample_offset_range_uv` sums negative coefficients for each lower
bound and positive coefficients for each upper bound. Its explicit premise is
that each directly sampled RGBA component independently lies in[0,1]. This is
not certified by source and excludes base UV and uniform offsets. Samples may
be correlated, which tightens the range. GetBlur decoding, HDR/external textures
and resource configuration must not be assumed to meet this premise.

`coordinate_sample_dependency` records whether a directly sampled input's own
lookup coordinates read other samples; unresolved loops/storage retain null
when no affirmative nested dependency is known. That indirect route can add
nonlinear response. `full_coordinate_sensitivity` and `visible_motion_speed`
remain null. A pure UV map may have direct sample gain0 while its content still
moves strongly through time/audio, native mesh or feedback. None of these
coefficients is a bass-response, screen-motion, flashing or mood score.

The analysis has64direct-sample and4096node budgets; exhaustion remains unknown
and does not imply an inactive preset. Generated input names are outside HLSL
identifier syntax. `observed_runtime_bindings=false`: this is source causality,
not an observed texture binding. Full source/parser/model/target identities stay
attached to the outer export.

[HLSL dot](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-dot)
defines the channel-weighted dot product. The target source31 header's lum macro
uses(.32,.49,.29), whose weights sum to1.10. Original MilkDrop2's D3DX authored
semantics remain a separate reference. Matrix/layout/floating-storage policies
follow the qualified ProjectM TV target rather than generic shader assumptions.

## Source-derived native blur inputs

`native_input_bindings.blur_decode` records source-proven native packed inputs
with policy `source31-constant-blur-decode-v1`. It is `source_constant` only if
all six main-frame blur min/max values are supported finite constants after
configuration resets and per-frame equations. Any missing/dynamic/unsupported
value withholds the whole triplet: an invalid later level can trigger the target's
coherent default policy for all levels. No partial triplet or guessed zero/default
input is supplied. The record may be absent where no authored shader is lowered.

The producer reuses `blur.native_ranges` with the qualified target policy. That
applies float32 narrowing, minimum-gap repair, progressive hierarchy and the
whole-triplet fallback. `_c5` is `[gap1,min1,gap2,min2]`; `_c6` is
`[gap3,min3,min1,max1]`. `raw_ranges`, `safe_ranges` and `packed_components` retain
the exact derived values. The existing component-binding interface injects them
into uniform declarations; authored local shadows still use their local values.
`observed_runtime_binding=false` distinguishes this source contract from a GPU
capture. No frame, shader, audio or image is executed to derive these constants.

The original MilkDrop2.25c `milkdropfs.cpp:1551-1583` contains a close-range bug
that assigns both endpoints average-minus-half-gap. The patched TV target repairs
that behaviour and adds coherent unsupported-range handling. This predictor
preserves the target repair rather than restoring the original bug. Source31
`BlurTexture.cpp:353-448` and `MilkdropShader.cpp:234-241` define normalization
and packing. Existing native-range numerical/regression controls remain required.

GetBlur decoding uses these scale/bias inputs, so resolving them can unblock
affine colour and coordinate coefficients. It does not identify kernel history,
actual texture contents, closed-loop flow speed, final colour palette or mood.
The independent sample-range premise from the previous section still applies.

## Raw texture-colour transfer

`texture_colour_transfer`, policy `source-affine-texture-colour-transfer-v1`,
exports per-stage raw RGB as `UV_matrix*input_uv4 + uniform_offset +
sum(sample_matrix_i*sample_i.rgba)`. It shares the typed affine analyzer and
bounded opaque-sample substitution with the coordinate-response model. Native
or unresolved stages retain unknown rather than an invented authored shader.

Each contribution has a3-by-4 `matrix_rgb_rgba`, source site/sampler/texture,
coordinate program and sampling policy. `base_uv_matrix_rgb` preserves source
UV gradients. `constant_offset_rgb` is null per channel where a uniform offset
is dynamic; its source program remains available. Dynamic texture multipliers,
nonlinear products, powers and quantized sampled colour remain unsupported.

`direct_colour_gain_norm` is the maximum RGB row sum of absolute per-site/
channel coefficients, treating directly read sample values independently while
holding their locations fixed. Correlations/cancellation can reduce actual
response; image-dependent coordinates can add indirect nonlinear response.
`full_colour_sensitivity`, `actual_sharpness` and `actual_feedback_persistence`
remain null. `final_palette_verified=false`. No texture/content is inspected.

`source_mixture_kind` describes coefficient signs: `signed_main_blur_mix` means
main and at least one blur are present and some coefficient in the entire sample
mixture is negative; `nonnegative_main_blur_mix` means all sample coefficients
are nonnegative with main/blur present. Other textures may participate in either
case; inspect their individual matrices. `other_affine_source_mix` covers other
sample combinations or the degenerate UV/uniform-only case. These are source
mixture facts, not sharpening/softness, brightness or mood classifications.
Kernel/history/coordinate alignment, decode ranges, clipping/storage, source
injection and subsequent passes determine the final image.

Warp `_vDiffuse` uses the earlier source-bound vertex colour contract, resolving
only known consumed lanes. Dynamic decay keeps RGB unknown and alpha one;
composite hue/vertex colours are never replaced with warp decay. Source stages
and native binding inputs retain their qualification/context obligations. This
model does not replace the main-only feedback-transfer or47numeric contracts.

## Native roaming-time inputs

`native_input_bindings.time_oscillators`, policy
`source31-native-time-oscillators-v1`, describes the sixteen native components
behind roam_cos, roam_sin, slow_roam_cos and slow_roam_sin (_c8–_c11). Each is
`.5+.5*cos(rate*t+phase)` or its sine counterpart with float32 coefficients.
The private input `:native-render-time-f32` represents float32(renderContext.time)
before the separately wrapped shader time. The clock origin/resets/jumps are
caller context, not inferred preset elapsed time. It is not a fixed zero clock.

The source formulas are injected only into float4 uniform declarations via
`known_uniform_component_fields`. Explicit numeric bindings retain precedence,
and authored local shadows remain local. Numeric component fields, component
domains and symbolic component fields remain distinct. Only scalarfloat lane
indices0–3 are supported. No native code or shader/audio/frame execution is
required to expose the formulas. observed_runtime_binding staysfalse.

Palette timing adds `clock_kinds_rgb`: shader_time_wrapped or
native_render_time_float32 per channel. `shader_time_wrap_seconds` is10000only
when a phase actually consumes the wrapped shader clock; native-only formulas
do not inherit that reset. Native/mixed clock timing uses a continuity-domain
scope while the previous shader-only scope remains unchanged. Rates, periods
and component slopes are nominal algebra, excluding CPU float32 rounding/FMA,
transcendental approximation, GPU/interpolation, sampling and clock discontinuity.
No visible flash frequency or calibrated brightness/mood claim follows.

Source31 MilkdropShader.cpp247–268 and original MilkDrop2.25c
milkdropfs.cpp3975–3994 supply the same roaming rates, offsets and functions.
The target's uniform binding/dataflow policy stays authoritative. Single-
oscillator channel recognition remains limited: combined oscillators, texture
masks and nonlinear final colour may still leave a palette description unknown.

## Native composite hue recipe

A composite element that consumes _vDiffuse RGB (including the hue_shader macro)
may include `native_colour_generators`. Generator code10, policy
`source31-native-composite-hue-v1`, describes the engine's four-corner colour
recipe; this is a separate generator dictionary, not familycode10. Only actual
consumed RGB lanes are listed. Alpha-only, source-dead and warp-decay uses do not
create this record. A red-only grayscale return therefore does not acquire a
guaranteed multicolour scene.

For corner i and channel c, raw colour is
`bias_c + amplitude_c*sin(time*30*rate_constant_c + base_phase_c +
i*corner_step_c + preset_random_phase[index_c])`. Exported coefficients retain
float32 constants and the native operation order. Each corner normalizes its
channels using `.5+.5*(raw_channel/max(raw_rgb))`. Channels are coupled by this
maximum, so they are not independent output sinusoids. Preset random phases are
explicitly unknown, with preset-instance lifetime; no values are guessed.

The nominal native input RGB range is[2/3,1] per channel, subject to finite valid
phase inputs and excluding CPU/transcendental/interpolation error. At mesh
vertices, weights are xy,(1-x)y,x(1-y),(1-x)(1-y), with
x=vertex_position.x*.5+.5,y=vertex_position.y*.5+.5. GPU triangle interpolation
then determines fragment colour. This is not exact per-fragment bilinear
evaluation, and shader texture UV is not substituted for mesh position.

`actual_palette` staysnull, `final_multicolour_guaranteed=false` and
`observed_runtime_binding=false`. Later powers, permutations, masks, sampled
colours and feedback can make the final scene darker, monochrome, vivid or partly
hidden. No brightness, warm/cold preference, flash or dominance classification
follows solely from this recipe. Clock/context and grid/projection obligations
remain explicit. This record helps reconstruct a source colour ingredient, not
a complete final image.

Source31 FinalComposite.cpp328–375, PresetState.cpp25–28 and
PresetCompVertexShaderGlsl330.vert establish generation, random lifetime and
interpolation. Original MilkDrop2.25c milkdropfs.cpp4408–4450 uses the same
corner-generation/max-normalization construction.

## Static built-in waveform construction

A retained builtin_wave element now has `waveform_recipe`, policy
`source31-static-builtin-waveform-v1`. The evaluated mode follows the target's
checked float-to-int truncation and signed remainder modulo16. Known invalid
modes omit the native wave; dynamic modes retain unknown form/style. The mode
dictionary describes source constructions, not actual silhouettes or audio stems:
0circle,1stereo polar trace,2/3stereoXY,4momentum line,5quadratic stereo trace,
6angled line,7parallel stereo,8log spectrum,9extended line,10crossed stereo,
11parallel vertical stereo,12skewed polar,13star-named radial,14flower-named
polar and15lasso-named nonlinear. Read the recipe's source qualification before
using extended-mode names as visual labels.

Known mode0 uses radius.5+.4*preprocessedRightSample+mystery, angular sample
span6.28 and nominal rotation.2rad/second. It appends a closing endpoint but
has strip path topology; actual draw may use GL lines or quad triangles. Mode1uses right samples for radius and offset left samples for
angle with nominal2.3rad/second rotation. Mode2/3use stereoXYgeometry; mode3
changes opacity rather than geometry. Line modes use clipped endpoints and mode-
specific mystery angles; mode7uses squared wave_y as normal separation. Mode8
uses spectrum_left log amplitude and requires a valid positive log argument.
Source waveScale/128 and the one-pole audio smoothing recurrence are supplied,
followed by common four-tap geometry interleaving. No audio sample, equation
frame or native waveform adapter is executed by this source export.

The source-gating correction is important: mode3 replaces authored wave_a with
a reference-size coefficient*1.3*treb² before optional volume modulation. Thus
wave_a=0 does not prove mode3inactive; a dynamic mode also cannot be excluded
from that value alone. Composition and element admission share this rule.
Dots, thickness and additive flags use evaluated nonzero semantics, including
negative fractional values. `path_topology` describes points/strip/loop, while
non-dot `hardware_draw_primitive` remainsnull without renderer context and
`hardware_draw_candidates` retains line versus quad-triangle possibilities.
Known modes suppress audio routes for unused controls (including mode3wave_a);
dynamic modes retain possible routes. Render context, alpha clamps/threshold, native
projection and subsequent shader/feedback still determine visibility.

Extended mode9 allocates secondary vertex storage without explicit assignments
in its source body. `path_count` remainsnull while the primary generated path is
recorded; actual secondary draw behaviour is an open investigation, not an
asserted engine bug. Nonfinite float32-narrowed controls leave derived angle/
separation unknown and preserve other descriptor data. `native_control_domains_verified`
staysfalse; `actual_screen_coverage`, `visible_motion_speed` and calibrated mood
confidence remain unknown. Source/control expressions and audio causal routes
remain available even where final geometry is unresolved.

References: source31 Waveform.cpp90–110/246–295, WaveformMode.hpp, Waveforms/Factory.cpp
and mode-specific GenerateVertices bodies. These are patched TV source rules,
including16modes and authored-reference sample limits; original MilkDrop2's
legacy wave math remains a separate reference.

## Literal vector component projection

Source constant folding now follows supported single-component vector members
through constructors, typed conversions and literal arithmetic. Nested swizzles
retain their declared channel order; int-vector truncation remains before float
output. Input/sample vectors, unsupported projections, nonfinite results and
exhausted recursion budgets stay unknown. A discarded fourth lane does not
prevent literal RGB from resolving. This corrects raw-colour extraction, not
shader execution or final palette/visibility certification.

For example, a local float4(.2,.3,.4,.5).rgb can expose its declared RGB values
even when shadowing a native uniform name. Lexical lowering already preserved
that source value; the former opaque colour was a descriptor-folding gap. Source/
target/context conditions and downstream shading/storage still apply.

### Nominal custom-shape vertex motion

`vertex_motion` joins the centre trajectory with radius and angular control
curves. The native and original MilkDrop2 perimeter equation is
`P=(2*x-1,1-2*y)+r*(aspectY*cos(theta),sin(theta))`, where
`theta=ang+2*pi*i/sides+pi/4`. For constant effective side count, fixed viewport/aspectY and
`0<aspectY<=1`, its continuous nominal vertex speed has the bound
`2*centre_speed + hypot(max_abs_dr_dt, max_abs_r*max_abs_dang_dt)`
in NDC units per source-time second. Radial and tangential derivatives are
orthogonal before aspect scaling; the centre/local combination uses triangle
inequality. Peak factors need not occur simultaneously, so this is an upper
bound even when the separate control peaks are known exactly.

Constant and single-sinusoid radii have a magnitude envelope. Linear radius
with static angle can have finite speed despite unbounded lifetime size;
rotating linear radius has no global speed bound without a time window.
Unknown radius, centre, angle or effective sides withholds the combined bound.
Known constants outside their native float32 domains also withhold it, including
centre overflow after the `2*x-1` / `1-2*y` projection and zero radius with
a nonfinite angle; multiplication by zero cannot repair `cos(inf)` / `sin(inf)`.
A collapsed zero-radius perimeter has no angular contribution. Individual
known factors remain available when the combined bound is unknown.

This model excludes float32 conversion/trig error, clipping, rasterization,
textures/material changes, composite and feedback, and requires finite source
intermediates and native conversions. It neither certifies visual smoothness
nor provides a calibrated mood or flash score. `visible_motion_speed` stays
null. NDC speed can be converted to a resolution-dependent geometric estimate
by a downstream consumer under explicit viewport conditions; it is not a
measured physical-screen movement rate.

### Static native-instance motion specialization

Shapes whose position/radius/angle/sides depend on the original `instance`
input add `instance_motion`. The native loop sets index0through count-1 before
each source equation phase. Symbolic substitution replaces that original input;
it does not change local writes, incoming audio or persistent custom state.
Supported finite literals, literal sin/cos, EEL zero-guarded division and known
conditional branches can simplify afterwards. No time/audio samples, native
equation execution or image rendering are used. Trig-derived constants use
nominal double formulas, not a claim of native libm bit identity.

`instances[]` contains compact paths and vertex-speed bounds indexed by native
iteration. `known_path_instances`, `known_speed_instances` and
`processed_instances` count independently. `expansion_complete` means every
configured instance was processed; it does not mean all paths are known. The
aggregate vertex-speed bound is available only when every instance has one.
One unknown member leaves the aggregate null; there is no renormalization or
extrapolation. Existing aggregate source geometry is unchanged.

The source expansion limit is1024instances with262144distinct-node visits
across their substitutions and a depth limit64. These are processing budgets,
not native language bounds or evidence that a larger native count is clamped.
A larger count retains the authored configured value with incomplete expansion;
a node/depth budget stop retains finished rows and withholds the group bound.
Per-instance literal caches are isolated so they cannot exhaust the parent's
source cache. Metadata documents conditions and budgets for consumers.

Original authoring guidance describes repeated shapes controlled by `instance`:
[MilkDrop authoring guide, custom shapes](https://www.geisswerks.com/milkdrop/milkdrop_preset_authoring.html).
The target behavior is verified separately in patched `CustomShape::Draw` and
`ShapePerFrameContext::LoadStateVariables`: Q reloads the main-frame snapshot,
T reloads the shape init snapshot, and configured shape values/index reload
each iteration. Unmodeled custom state stays an explicit input. Native/MilkDrop
projection, finite conversions, clipping and feedback conditions still apply.

### Compound source-time control bounds

`motion_controls[].curve_kind` adds `compound_time` for supported scalar
compositions with a finite lifetime nominal rate bound. `rate_estimate_kind`
and `nominal_value_range_kind` distinguish `exact_nominal`, `upper_bound` and
`unknown`. Existing constant, affine-time and single-oscillator rules retain
exact nominal estimates. Compound periods and harmonic path labels are not
guessed; their original source expression DAG stays available.

For envelopes M_f=max_abs(f), M_g=max_abs(g), and rate bounds D_f,D_g,
addition uses D_f+D_g, product uses D_f*M_g+D_g*M_f, and sine/cosine use the
phase-rate bound by the chain rule. Division with a denominator envelope
strictly away from zero uses D_f/min_abs(g)+D_g*M_f/min_abs(g)^2. A missing
needed magnitude or rate leaves the resulting rate unresolved. Unbounded
affine values can still have finite rates; sin(time*time) can have bounded
values while retaining an unknown lifetime rate. Bounds are conservative,
not estimates of the true peak or a typical percentile.

The trigonometric identities and derivatives are documented by
[NIST DLMF4.20](https://dlmf.nist.gov/4.20) and
[NIST DLMF4.21](https://dlmf.nist.gov/4.21). Actual target EEL scalar functions
are checked in the prepared projectm-eval TreeFunctions.c and original
MilkDrop2source; this layer implements the understood formulas without
copying a native renderer or executing expression programs.

`abs`, `min` and `max` can preserve a Lipschitz variation bound while allowing
cusps. `nominal_continuity` is `smooth_nominal`, `piecewise_lipschitz` or
`unknown`, and propagates to centre, vertex and per-instance joins. The weaker
piecewise class allows cusps; it does not prove that a cusp actually occurs.
These are regularity facts about nominal control formulas, not a visible
smoothness score. Unknown side-count domains and known invalid native float32
conversions prevent a smooth-vertex claim.

EEL division's zero guard is kept separate from ordinary division. If an
entire known denominator envelope lies strictly inside(-0.00001,0.00001),
the qualified finite-input result is zero. Guard crossings remain unresolved;
a denominator exactly on the boundary is outside the zero guard. Random,
state/audio inputs, integer steps, branches and unsupported operations have
no invented time derivative. No audio waveform or time/frame samples are used.

Scalar calculations expand computed envelope endpoints and nonnegative rate
operations outward with `nextafter`. Positive-to-zero rate underflow and
nonfinite derived rates remain unknown. A rounded singleton envelope alone
does not establish a constant trig function. These safeguards do not certify
native float32/libm parity, frame quantization or complete interval execution
of a shader; the source-math premise remains continuous nominal formulas
between clock discontinuities and before native precision/clipping/feedback.

Consumers must handle the additive curve category and estimate/regularity
fields. Never substitute a rate bound for measured visible motion or a mood
score. Existing47field simulation exports are unchanged.

### Shape colour and opacity temporal risk

`material_temporal.channels` covers centre, perimeter and border RGBA controls.
Each channel keeps a compact raw time-curve summary and a float32 endpoint
domain from its supported nominal lifetime envelope. A singleton domain can
provide `native_value_if_singleton` using the established native colour
conversion, even when a tiny raw oscillation remains nonzero mathematically.
Missing envelopes and nonfinite native conversions retain unknown values.
The full source DAG is already in `material.channel_expressions`; it is not
duplicated here.

The target colour period is float32 `256/255`, with CPU mapping
`fmod(fmod(float32(x),m)+m,m)`. This differs from MilkDrop2's packed8bit
integer conversion; the predictor preserves the TV engine's target policy.
`possible_native_wrap_jump` identifies a modulo-boundary candidate within
the supplied endpoint domain, including a two-period-ULP margin below each
boundary for remainder-plus-period rounding near zero. Rational boundary
comparison avoids inaccurate modulo-cell division for large finite floats.
This is conditional candidate risk, not an observed jump, its timing, or a
certificate that every possible floating-point step is absent.

`border_gate` separately models raw double `border_a > float32(.0001)`. It
exports nominal always-on/off versus a possible state change. This draw gate
does not use modulo alpha: a negative raw alpha can convert positive while
the border remains disabled. Disabled border channel risks are excluded from
`possible_consumed_wrap_jump`. Both native fan endpoint alphas must be proved zero to exclude fill channels
under ordinary finite source-alpha blending. One zero-alpha endpoint still
affects intermediate RGB/alpha interpolation, so it cannot be excluded alone.
Other centre/perimeter consumption depends on opacity, primitive coverage
and the later pipeline. Unknown active channels
keep the aggregate unknown unless another active channel already supplies a
positive possible-risk candidate.

Raw oscillator rate/period are not converted into a visible flash frequency.
`visible_flashing` and `visible_flash_frequency_hz` stay null. A threshold or
wrap candidate can be faint, masked, textured, clipped or replaced later; it
does not classify the preset as Intense or disqualify it from Chill by itself.
All conclusions depend on the declared nominal envelope and finite conversion
premises; native appearance/precision qualification remains separate.

### Conditional scalar value envelopes with unknown timing

When the time-curve rules cannot bound a control's value, `value_envelope` can
provide a separate conditional range. The same bounded walker supports a
value-only mode: named scalar inputs represent arbitrary finite values, with
`assumed_finite_input_names` recorded explicitly. No audio range, defaultzero
or state history is invented. Relevant source intermediates must remain finite.

Sine/cosine can bound values regardless of unknown phase timing; nested
min/max can bound a clamped input; understood comparisons return0..1 and
conditional branches use the union of their supported value ranges. Square
and safe arithmetic preserve required denominator domains. Internal extended
intervals model unbounded finite values; infinities never appear in exported
ranges. Known overflow, singular denominators, opaque operations, random calls,
uninitialized nodes, unsupported typed casts and effectful loops retain gaps.

The separate value envelope can populate `nominal_value_range` with an upper
bound while `curve_kind`, `maximum_absolute_control_rate_per_second` and
`nominal_continuity` remain unknown. A control confined to[.2,.8] can still
jump abruptly between its endpoints. Finite values are not smooth values,
and a possible-wrap result is not a complete flash result. Native float32/libm
certification and final appearance remain separate; `native_numeric_certified`
is false. No frame/time/audio samples or expression-program execution occur.

The shader-specific `shader_bounds` walker remains separate because its typed
float32, declared sampler and stored-UNORM8 contract is different from these
nominal EEL control envelopes. The implementation reuses source-control
calculus rather than introducing another parser or generic execution engine.

### Conditional incoming fill contribution envelopes

`fill_envelope` complements the existing exact constant `fill_contribution`.
It bounds mean source blend alpha and RGB-times-alpha for untextured polygon
fans with supported native channel domains. Textured fills remain unresolved
without a matching texture contract, and RGB channels retain independent gaps.

Singleton native channels retain their exact established conversion. For a
finite endpoint interval in one stable modulo cell, rational residual bounds
are padded by the declared float32 margin; crossings use the full finite
modulo colour range. Missing conversion domains remain unknown. These colour
envelopes inherit all input/intermediate/source-calculus assumptions.

For centre/edge alpha bounds A0,A1, mean clipped alpha is at least
`(min(A0.lower,1)+2*min(A1.lower,1))/3` and at most
`min((A0.upper+2*A1.upper)/3,1)`. The lower bound follows concavity of
positive alpha clipping; the upper follows its mean bound. Neither clips
vertex alpha and then incorrectly treats the actual interpolated result as
linear. For RGB-times-alpha, the same nonnegative fan second-moment formula
uses clipped lower vertex bounds and unclipped upper bounds; an independent
`max(RGB.upper)*mean_alpha.upper` cap can tighten the upper side. This remains
valid whether source RGB is clipped or retained, without assuming its stage.
[OpenGL ES blend factors](https://raw.githubusercontent.com/KhronosGroup/OpenGL-Refpages/main/es3.0/glBlendFunc.xml)
describe source-alpha scaling and its0..1factor range.

A finite radius range and constant effective sides give a nominal area range
from squared float32 radius endpoints. A range crossing zero has area lower0;
negative radius alone does not mean negative area. The regular-polygon
coefficient stays per aspectY and excludes trig/projection/raster precision.
Multiplying nonnegative area and material intervals gives incoming integral
bounds without assuming their extrema coincide. Repeated-instance sums count
overlap repeatedly and are not union coverage or stored scene brightness.

`visible_screen_contribution` remains null. Clipping, borders, texture content,
actual overlap, destination colour, storage, later shaders and feedback stay
separate. Bounds can be loose; they are not point estimates, visible response
strength or calibrated Chill/Normal/Intense scores.

### Periodic sampling-coordinate preimages

Each supported sampling map adds `copy_lattice`. If repeat sampling uses
`M*u+b`, a fixed source feature at s has candidate coordinates
`u=inv(M)*(s+n-b)` for integer pair n. Generator columns are `inv(M)`;
`origin_from_offset_matrix=-inv(M)` maps the existing offset programs, and
`origin_for_source_feature_zero_uv` is available for known constant offsets.
Fundamental-cell area is `1/abs(det(M))` in the declared UV basis; its inverse
is the nominal lattice-point density per unit UV area. Density is not a
finite-window or visible copy count, and source content can be uniform/empty.

Clamp sampling is `not_periodic`. Unknown wrap becomes
`conditional_on_repeat_wrap`, preserving the required context rather than
assuming it. Singular/mixed-basis/nonfinite inverse maps stay unknown.
[OpenGL ES repeat wrapping](https://raw.githubusercontent.com/KhronosGroup/OpenGL-Refpages/main/es3.0/glTexParameter.xml)
uses periodic texture coordinates; this supplies a geometric preimage model,
not an observed rendering. Filter/LOD, masks and colour weights can change
which source features are recognizable. Warp shader UV already incorporates
native mesh transformation, so that basis's inverse is not a physical-screen
inverse. Existing native/original basis distinctions are preserved.

With a fixed matrix and source feature/index, affine time offsets yield origin
velocity `-inv(M)*db/dt`. Other supported offset-rate bounds yield a
conservative Euclidean speed bound from `abs(inv(M))*[Dx,Dy]`. Product
underflow and nonfinite derived estimates retain unknown speed. Units are
declared basis UV per source-time second, not pixels or measured screen motion.
`actual_visible_copy_count` and `visible_screen_motion` remain null. Full
feedback evolution, overlaps, content/history and appearance remain open.


## Uniform native feedback map

`native_warp_recipe` provides nominal sampling geometry for known uniform
float32-converted mesh controls with zoomexp=1. Dynamic/radial, singular and
nonfinite controls stay unknown; disconnected native mesh is marked separately.
For output source UV u, let A=diag(aspectX,aspectY), c=(cx,cy), d=(dx,dy),
S=diag(1/sx,1/sy), R the nominal rotation of the emitted float32 angle, and z=zoom.
The affine sampling map is:

```
q = S * (A*(u-.5)/z + .5-c)
v = inv(A) * (R*q + c-d-.5) + .5 + texel_offset_uv
```

The JSON matrix coefficient basis is [1,aspectY/aspectX,aspectX/aspectY];
offset basis is [1,1/aspectX,1/aspectY,aspectY/aspectX,aspectX/aspectY].
Area ratio abs(z*z*sx*sy) belongs only to the affine source-to-output component.
Identity likewise excludes procedural warp and texel alignment. Neither implies
stationary visible feedback. The four native waves are added before rotation,
using pos=2*u-1 and an explicit 2x4 axis/factor coefficient matrix in each phase.
`shader_branch` distinguishes legacy/default from accepted custom warp. Custom
warp negates the legacy second-axis coefficients; unresolved nonzero warp
stays unknown. Offline branch acceptance remains conditional on native profile.
The per-axis displacement bound before rotation is 2*abs(warp)*float32(.0035).
Wave factors expose their bias/amplitude/frequency/phase and render-time scaling.
No time samples are evaluated by the producer.

The authored MilkDrop2 reference in milkdropfs.cpp (lines1870–1929) reverses
projection Y; the current legacy vertex shader already uses source UV Y and
reverses oscillator signs accordingly. The recipe preserves that convention.
Current source34 PerPixelMesh.cpp supplies emitted controls, CPU rotation and
warp factors; PresetWarpVertexShaderGlsl330.vert supplies operation order.
Aspect and texel inputs must be supplied by the renderer. Trigonometry,
intermediate rounding, precision, triangle interpolation, transition blending,
feedback contents and later shaders remain distinct conditions. This is a
source construction recipe, not a whole-preset image or mood certification.


## Uniform affine transport envelopes

`native_warp_transport` retains ten independent source control rows and bounds
an affine component when every control has a pure uniform expression, zoomexp
converts to1, and zoom/sx/sy have finite sign-definite native endpoint domains
with finite nonzero reciprocals. Declared readonly frame/configuration inputs and explicitly scoped main/init
scalar snapshots establish uniformity; spatial, pixel-local/shared state, random/memory
and opaque operations cannot establish it from a dependency list alone. Even
per-frame random expressions abstain until execution-phase provenance is added.

In aspect-corrected coordinates, the inverse affine sampling matrix is
zoom*diag(sx,sy)*transpose(R), giving singular scales abs(zoom*sx) and
abs(zoom*sy), and area ratio abs(zoom*zoom*sx*sy). Native endpoint products are
computed as exact binary-rational products and rounded outwards for JSON.
Independent envelopes can overestimate correlated extremes. Reflection parity
is sign(sx*sy); negative zoom flips both axes and leaves that parity unchanged.
Axis behavior reports expansion, contraction, neutral or a neutral-crossing
range. These describe per-step feedback transport, not parameter-change rates.
Finite-input assumptions and unknown timing/continuity survive audio envelopes.

Procedural warp, physical-screen aspect, source content, clipping, texture
wrapping, later shaders and feedback accumulation remain separate. A nonlinear
spatial control is not a uniform affine map: its area needs derivatives of
its varying controls. `complete_sampling_map_area_ratio` and
`visible_screen_motion` remain null. This descriptor does not certify moods.
The native/reference operation order is the same source cited by the uniform
recipe; the creator's [authoring guide](https://www.geisswerks.com/milkdrop/milkdrop_preset_authoring.html)
explains zoom/rotation/stretch as repeated image motion rather than control
variation. Current patched-native semantics remain the target.


## Initial radial zoom component

`native_radial_zoom` uses independent uniform zoom/zoomexp source rows. Later
spatial rotation/translation need not hide the understood initial radial
component. Require positive finite native endpoint domains; retain negative,
unbounded, spatial/state/random or float32 power/reciprocal overflow/underflow
as unknown. Under current normalized aspect inputs, nominal source radius r
is in [0,sqrt(2)]; the emitted mesh radius is not the authoring guide's claimed
corner radius1. The current source34 PerPixelMesh.cpp uses hypot(pos.x*aspectX,
pos.y*aspectY), while ProjectM.cpp normalizes each aspect to at most1.

For z=zoom and e=zoomexp, the native nominal nested-power construction is:

```
P = e^(2*r-1)
F = z^P
sampling_radius = r/F
log_factor_derivative = 2*ln(e)*ln(z)*P
radial_sampling_derivative = (1-r*log_factor_derivative)/F
```

Monotone positive-power endpoint bounds supply F and 1/F, with independent
control correlation conservatively ignored. Exact binary-rational products
bound nominal derivative terms after the real log/power functions. Positive
radial derivative is reported only when the upper bound on
r*log_factor_derivative is strictly below1. Failure is undecided, not proof of
a fold. Bounds are nominal calculus with outward endpoint arithmetic, not
formal GPU/libm error intervals. Native radius/intermediate rounding, mesh
triangle interpolation and finite sampled frames remain separate.

`visible_effect_family`, `actual_fold_present` and complete-map area remain
null. Curved radial feedback can contribute perspective-like layouts, but
contents, wrapping, other transformations and shaders determine a tunnel or
ring appearance. This source-math addition cannot confer a mood label.


## Native sampling displacement

`native_warp_displacement` measures nominal backward-sampling displacement
per feedback step in aspect-corrected source coordinates. For the uniform
affine component, let p=A*(u-.5), B=R*diag(1/(zoom*sx),1/(zoom*sy)), and
h=(R*diag(1/sx,1/sy)-I)*(.5-center)-distance. Displacement is(B-I)*p+h.
Uniform original UV in[0,1]^2 has centred coordinate covariance
 diag(aspectX^2,aspectY^2)/12. Constant float32 control domains therefore supply:

```
RMS_affine^2 = dot(h,h)
             + aspectX^2 * squared_norm(column0(B-I))/12
             + aspectY^2 * squared_norm(column1(B-I))/12
```

`affine_rms_squared_aspect_coefficients` uses basis[1,aspectX^2,aspectY^2].
The mean affine displacement is h. Its centre terms use the factored form
with exact binary-rational products/sums of emitted controls and nominal
sin/cos coefficients before finite serialization; expanded large-centre sums
must not erase tiny translations. No source-coordinate/frame samples are
needed to produce these coefficients. A fixed zoom can have nonzero RMS even
though its temporal control rate is zero. Backward sampling direction does
not equal forward movement of an arbitrary source feature.

Varying control domains retain an upper bound using spectral-norm/triangle
inequalities: norm(R*D-I)<=norm(R-I)*max_abs(D)+max_abs(D-I), with
norm(R-I)=2*abs(sin(rot/2)); a conservative angle-range bound is used. Apply
the same inequality to the centre/stretch contribution and add translation.
The upper RMS is centre_bound + geometry_bound*sqrt(aspectX^2+aspectY^2)
+ procedural_warp_bound. The last term is sqrt(2)*2*abs(warp)*float32(.0035),
using the pre-rotation four-wave envelope and invariance of norm under rotation.
This term is independent of legacy/custom oscillator signs. It does not claim
that all oscillator peaks occur together. Finite warp-scale reciprocal is
required even for zero warp, preserving the native expression's domain.

Texel alignment is excluded and must be added as A*texel_offset_uv by the
consumer. Native precision, mesh interpolation, clipping/wrapping, feedback
contents, composition and transitions remain separate. The measure integrates
the sampling field, not image brightness or feature tracking. Multiplication
by an assumed FPS cannot certify visible speed; motion intensity and moods
remain unknown until the complete contributing path is understood/calibrated.


## Built-in waveform colour and opacity

Contributing `builtin_wave` elements include `wave_material`. Raw channel
source curves retain ranges, rates and continuity separately from native
material processing. Wave RGB converts to float32, comparison-clamps to[0,1],
then optional brightening divides by the clamped maximum only when max exceeds
float32(.01). This is not the custom-shape modulo policy. Constant supported
channels export `constant_vertex_rgb`; dynamic independent envelopes remain
nominal before division/rounding and final storage/feedback. A maximum envelope
crossing the hard threshold is a possible normalization jump, not a proven
visible flash. Dynamic brighten flags retain unknown risk rather than a no-jump
certificate. Constant/rate-zero controls do not acquire temporal gate changes.

Opacity order is mode adjustment, optional unbounded volume-ramp multiplication,
then final comparison-clamp[0,1]. Mode1boosts authored alpha by1.25; modes2/5
attenuate it by the reference-size table. Mode3replaces authored alpha with
reference_base*float32(1.3)*pow(native_audioData.treb,2). Its input is native
engine audioData, not an authored EEL `treb` reassignment. Audio/history-free
bounds stay unknown for mode3and enabled volume modulation. The ramp uses
(native_audioData.vol-start)/(end-start), without clamping it first. Invalid
active denominator domains stay unknown without losing RGB or disabled-ramp
alpha data. Reference size follows MaximizeColorsTextureSize, preserving
ProjectM-TV's authored line reference instead of assuming physical4K size.
The alpha<.004 material skip applies to both quad-line and hardware line/point
paths before scaled-dot alpha adjustment. Later coverage/drawing can still vary.

Evidence: source34 Waveform.cpp227–352 supplies this order, and original
MilkDrop2.25c milkdropfs.cpp2832–2840 / mode branches2930onward confirm intended
normalization and opacity handling. Target float vertex colours remain distinct
from MilkDrop2's packed display representation. Generated audio geometry,
coverage, draw mode, alpha, blending, feedback and later shaders determine
what reaches the screen. No mood, displayed-flash frequency, final palette or
whole-preset no-flash promise follows from this material descriptor.


## Nominal time-switch events

Raw source control curves include `time_switch_events` and explicitly mark the
list nonexhaustive. The producer checks at most2048source nodes and32events per
curve, with per-analysis caching. Supported sinusoidal comparisons use an affine
source-time phase, known offset/amplitude and an interior normalized threshold.
Negative amplitude reverses the comparison; signed phase rates retain event
phase. Duty cycle is acos(threshold)/pi for the normalized greater predicate,
complemented for less. Two roots per period supply event cadence2/period and
supported offsets modulo the period. The inverse-trig basis is documented in
[NIST DLMF4.23](https://dlmf.nist.gov/4.23); the duty/contact formulas are our
source-math derivation, checked with independent controls.

Only complete comparison/constant-branch controls supply a whole-control jump.
Nested sites preserve their own nominal predicate cadence but not an inferred
outer jump. Equal branches are omitted. Tangent thresholds at±1, unreachable
thresholds, audio/state/nonlinear phases and unproved domains get no crossing
schedule. An empty list does not certify continuity or absence of flashing.

Affine real-floor sites have a step interval1/abs(phase slope). A supported
scalar linear transfer can supply scaled jump magnitude, while absolute levels
remain unbounded/unknown. The step train is periodic in event cadence, not
periodic control values. Current source34 projectm-eval TreeFunctions.c87–88
binds EEL int and floor to the same real floor function, and its negative-value
control expects floor(-1.5)=-2. The source reader emits int for that shared
function. Shader integer casts retain conversion semantics and cannot borrow
a floor site's whole-control jump. A cadence at an inner site can be hidden by
clamps, material conversion or other outer operations.

The schedules use nominal continuous source time. Shader-wrapped versus
native/equation clocks are identified; resets/wrap, native rounding and finite
frame cadence remain outside these event counts. Event offsets can remain null
when arithmetic cannot resolve distinct contacts. Visible-flash frequency is
always null. Later execution gates, projection, opacity, blend/feedback and
composition determine visible consequences; this is not a mood certificate.


## Main-frame Q shader bindings

`native_input_bindings.main_frame_q` records q1..q32 as _qa.._qh scalar lanes.
The source model reuses the already interpreted main equations, with preset-init
Q reloaded before each frame. Source34 PerPixelContext.cpp98–106 copies the
main Q values to both frameQVariables and the pixel context before vertex code.
MilkdropShader.cpp336–344 uploads frameQVariables, an array of doubles, through
float4 uniforms. Pixel/custom-context Q writes do not replace that shader snapshot.
Original MilkDrop2.25c milkdropfs.cpp493/675/4004–4007 confirms this pool/copy intent.

Supported constants convert to float32 after main expression evaluation. Dynamic
Q programs are inserted as explicit `narrow` fields with `native_uniform_role`
metadata, preserving the precision boundary and source/input dependencies.
Known nonfinite uploads remain unknown; no zero default replaces overflow.
Shader-local shadows retain their own values. Each lane's contract includes
its source expression, binding status, packed location and known converted value,
with runtime binding unobserved. Unsupported dynamic EEL operations remain
symbolic gaps; imported source expressions are not executed as GPU or equation
code by the static exporter.

Audio routes retain `q_bridge_expressions` after replacing the packed bank read,
and the expression DAG preserves the native Q role. Q-mediated scalar gain stays
unqualified across float32 upload; direct raw-source band coefficients and the
final shader transfer are different facts. This can clarify constant feedback
weights and colour recipes, but does not certify dynamic values, native temporal/
rounding parity, whole feedback or appearance/mood accuracy.


## Varying feedback colour envelopes

`feedback_envelope` is additive to the existing constant point-transfer model.
It factors supported RGB expressions into source offset plus per-main-sample
coefficient expressions. Coefficients/offsets may vary with non-image time,
audio, spatial or Q inputs when their nominal scalar envelopes are finite.
Distinct sample sites remain independent. Products of sampled colours,
unbounded/singular coefficients, blur/history or unresolved nodes remain unknown.

For each output RGB row, sum the maximum absolute coefficient across input RGB
lanes/sites to bound the fixed-coordinate infinity-norm colour response. Sample
premises of independently bounded[0,1]RGB give a raw output box, including signed
coefficients and supported offsets. Coefficient correlations can tighten these
conservative independent envelopes; the producer does not sample frames/time.
Image-driven coordinates keep contraction unknown. Otherwise a gain upper bound
below1 is sufficient only under nonexpansive image-independent sampling and
identical non-image inputs; log(.5)/log(gain) is a nominal perturbation half-life
upper bound in operator evaluations. A failed sufficient condition is not
amplification/instability. Native rounding, storage, drawing, blur/detail,
discard and the complete feedback loop remain separate.

Native Q/fixed-decay narrow nodes first require finite endpoint conversion to
float32. Their derived ranges become explicitly bounded local scalar inputs
while subsequent nominal arithmetic is analyzed. `scalar_value_envelope` accepts
input_domains and reports consumed declared domains as premises; these cannot
be silently generalized to arbitrary runtime inputs. Known upload overflow and
invalid domains abstain. Fixed warp preserves min(float32(decay),1), including
negative values; it does not add a lower zero clamp.

Actual persistence, visible flashing/motion and mood labels remain unresolved.
The source/program/target contracts and sampling/drawing stages must be joined
before a colour-only bound can establish a complete scene behaviour.


## Independent texture colour-input envelopes

`texture_colour_envelopes` consumes the existing per-stage affine texture-colour
matrices. Under an explicit independently bounded[0,1]RGBA premise, coefficient
signs and finite constant offsets give a raw RGB box. Nonzero coordinate-colour
terms or unresolved offsets keep this box null while preserving valid sampled-
input norms. Exact binary-rational coefficient sums are outward-rounded once.
Each output row's sum of absolute weights bounds fixed-coordinate texture-input
perturbations in the infinity norm; the maximum row supplies the reported norm.

All-texture, main/blur-history and external-texture input norms remain separate.
Source texture identities are not observed GPU bindings or fallback decisions.
Random/external assets must remain fixed for a history-only comparison. Different
blur levels may contain different history/normalization; summing their input
weights does not solve the actual shared recurrence. Coordinates, kernels,
clipping, native precision/storage, drawing/detail and final display remain
separate. Full sensitivity, whole-feedback contraction and actual persistence
stay null; these colour boxes cannot alone establish final brightness, palette
or a mood. This is a supported mixture description, not a new image simulation.


## Nonlinear declared-texture colour ranges

`nonlinear_texture_colour_bounds` reuses sample-value substitution and the
bounded scalar walker. Each sample RGBA lane receives a declared[0,1]domain;
texture identity and input domains remain source contracts, not observed uploads.
The producer computes per-channel nominal ranges through supported nonlinear
operations and retains partial channels without a complete RGB box. It never
samples time, audio or pixels and does not assign a nonlinear sensitivity gain.

Value-only rules cover saturate/clamp, positive-domain constant-exponent powers,
sqrt, interpolation and dot products, alongside supported scalar arithmetic,
trig and comparison ranges. Interpolation checks all endpoint combinations,
including extrapolation; weights are not implicitly clamped. Constant clamp
limits and nonnegative power ranges survive outward rounding. Domain guards
remain active for singular powers, negative roots and invalid/nonfinite uploads.
Native Q narrow nodes prove finite conversion before later clamps; a clamp
cannot hide an unproved upload domain. Unsupported guarded operations stay
unknown rather than dropping their checks.

The shader graph already includes projectM's compatibility abs lowering for
powers/roots and its literal pow(x,1)sign exception. These semantics remain
intact. Native lum() uses dot weights(.32,.49,.29), summing1.1, not a generic
normalized luminance transform. The [Khronos power reference](https://raw.githubusercontent.com/KhronosGroup/OpenGL-Refpages/main/gl4/pow.xml)
defines the underlying positive/zero-base domain; the pinned translator's
lowering is the target-specific step before that operation.

Raw ranges retain correlation/native precision/history/coordinate uncertainty.
They do not measure colour distribution, dominance, palette, brightness,
continuity, flashing or mood. Full nonlinear sensitivity and shared recurrence
remain separate work; complete channel bounds are not appearance certification.

## Nominal audio control-response bounds

Each causal route may additionally export `nominal_audio_response`. Its
`maximum_absolute_control_change_per_audio_unit` is a sufficient upper bound
for the nominal scalar formula. The example `.2*sin(3*bass)` has bound `.6`:
the chain rule multiplies amplitude .2 by phase gain3 and maximum cosine1.
For `.2*sin(3*bass+2*mid+time)`, bass has bound.6 and mids bound.4 while
other inputs stay fixed. These are not average or minimum response estimates,
nor proof of response direction, displayed flashes, beat timing or visibility.

The existing bounded calculus supplies addition, product and quotient rules,
trig, absolute value and min/max continuous clamps. Declared input domains,
where supplied to the scalar helper, stay explicit; ordinary route exports
invent no audio ranges. `sin(bass*mid)` has no global bass-response bound
without a bound for mids. Threshold jumps, singular denominators, unknown
effects, dynamic casts/narrowing, unsupported operators and calculation budget
exhaustion keep the bound null. Raw value ranges cannot substitute for it.

Packed shader bands keep scalar identities such as `_c3.x`; EEL bands retain
their authored names. `varying_input_names` lists aliases varied together by
the same delta; `held_fixed_input_names` lists visited external inputs held
constant. Holding a previous-frame state variable fixed is an instantaneous
partial response, not a derivative of its recurrent evolution. Quantized Q
uploads therefore remain unresolved in this continuity-based model.

`nominal_continuity` refers only to the supported scalar map with the listed
premises. All native/storage rounding, shader sampling, drawing order, screen
area, real audio trajectories and final composition remain outside the bound.
The result includes `native_numeric_certified:false`, null visible response
and null maximum time-rate. Existing signed `linear_gain` and switch-trigger
records remain separate. No mood score follows from a Lipschitz upper bound.

## Procedural oscillatory bands

`elements[].procedural_forms[]` includes form/family code10 for supported scalar
sine/cosine generators whose phase is constant-affine in one declared native
UV basis, or solely in the native radial varying. The phase must reach RGB data
or its mask/control graph; a sine that only bends texture sampling coordinates
does not establish a colour-band generator. Discarded fourth lanes, zero/dead
terms, uniform-only phases, mixed coordinate bases, varying spatial scales and
unsupported non-affine phases do not establish this descriptor.

Proved complete nominal clamps/saturation and dominating min/max branches
disconnect generators from this colour traversal. Constant-affine sums of
bounded sine/cosine/saturate terms use exact binary-rational range arithmetic
for that decision; unknown and partial masks retain conditional forms. The
same colour-data guard applies to the existing radial-glow form9. Known
singular uniform phase operations and established out-of-float32 upload
envelopes reject form10; arbitrary finite unknown phase inputs remain
conditional. Existing native abs lowering stays intact for roots/powers.

For `sin(kx*u+ky*v+b)`, `phase_coefficients` and `phase_normal_uv` retain the
signed nominal phase gradient. `nominal_period_in_basis_units` is
`2*pi/hypot(kx,ky)`, measured along the phase normal. The perpendicular tangent
is the nominal stripe direction. Native-radius phases use `2*pi/abs(kr)` in
radial varying units, retaining the signed coefficient. These periods describe
the raw sine/cosine generator, not the fundamental period after abs, thresholds,
products or other later transformations.

`basis` distinguishes shader UV, original UV and native radial varying.
Warp shader UV includes mesh warping; original UV bypasses it. Native radial
input is supplied and interpolated by the engine; do not reconstruct it as a
pixel-exact analytic circle from this descriptor. The record retains the full
generator/phase programs and its uniform `phase_motion_control`/`audio_routes`.
Those control the phase shift, not colour amplitude or physical screen speed.

Canonical formula IDs are generators, not layer counts or identities of objects.
Distinct generators can coexist and masks, tint, clipping, projection, native
precision, sampling or feedback can suppress/change them. Screen coverage,
visible speed, ring count, calibrated mood and appearance remain unverified.
Code10 is an additive vocabulary item; consumers must handle unfamiliar codes
explicitly rather than treating an unsupported code as absence of an effect.

## Oscillatory texture displacement

Each sampling-site record may contain `oscillatory_displacement`, with model
`uniform_affine_plus_oscillators` when the complete supported lookup decomposes
into a uniform-affine baseline plus sine/cosine displacement waves. This is
texture deformation, separate from the colour-band form10. A supported map is
nominally `lookup = base + sum(amplitude_uv * oscillator(phase))`.

`base_coefficient_programs` contains two rows in the six-column order listed by
`phase_gradient_column_order`: mesh UV x/y, original UV x/y, and native radial/
angular varyings. `base_offset_programs` supplies the two uniform offsets.
`base_matrix_uv4` is available only when the baseline has constant UV coefficients
and no radial/angular contribution. Dynamic baseline coefficients remain programs.

Each `waves[]` record contains two `amplitude_uv_programs`, six
`phase_gradient_programs`, a `phase_offset_program`, and corresponding constant
values when established. Thus `.01*bass*sin(uv.y*(3+2*mid)+time)` records bass
as horizontal displacement amplitude, mids as vertical spatial frequency, and
time as phase shift. The producer invents no audio range or constant wavelength
for this formula. Shared scalar phases combine their signed contributions into
one vector wave; canonical wave records are not visible-object or layer counts.
`audio_routes` links named amplitude/frequency/phase controls to band inputs.
Uniform multipliers and divisors distribute through supported sums/subtractions
before extraction. For example, `bass*(sin(p)+cos(q))` preserves a shared bass
weight on both wave records. Products of two spatial oscillators are not
linearized. This algebra describes nominal real formulas; native reordered
floating-point arithmetic is not certified. Original-domain checks still run
on the untouched graph before a complete-map claim.
`phase_motion_control` describes the uniform phase offset with native-clock and
precision qualifications retained from the existing source-time model.

For constant waves in a single UV basis, the producer bounds the Jacobian of
the displacement with the row sums `sum_w(abs(a_w[i])*sum_j(abs(k_w[j])))`.
The largest row gives `jacobian_perturbation_infinity_norm_upper_bound`; exact
binary-rational sums are rounded outward. If the baseline is identity in that
same UV basis and this bound is below1, the unwrapped nominal map has a
sufficient no-fold/injectivity condition. Failing that condition does not prove
a fold. Dynamic coefficients, mixed/radial bases and nonidentity baselines
retain null certificates; `actual_fold_present` remains null.

Unsupported nonlinear products, image-driven phases, spatial integer casts,
known singular/upload domains and missing required export programs keep the
model unknown. Unknown denominators/inputs retain the declared usable-finite
source-domain premise; they are not certified by absence of a known failure.
Candidate maps check the untouched original scalar/vector arithmetic before
certification, retaining zero-product operands so simplification cannot hide
a singular intermediate. Structurally unsupported maps require no such extra
preflight; this preserves the shared traversal budget for existing descriptors.
Extraction uses512distinct-node/depth64 phase budgets,64product factors,
32waves and the existing256-node expression-export bound. Native interpolation,
rounding, wrap/filter, mesh transforms, texture/history contents and later stages
are outside these nominal formula bounds. No visible speed, feedback stability,
dominant screen structure, flash permission or mood score follows from them.

Uniform distribution separately limits traversal to512visits/depth64 and64
result terms. A budget rejection stays unknown; it does not increase the
shared source-analysis budget or silently discard unexpanded terms.

## Ripple deformation envelopes

Supported periodic maps additionally export `deformation_envelope`. Its
`maximum_absolute_displacement_uv` has separate x/y upper bounds on the
oscillatory component only, excluding baseline mapping/offset. It sums the
maximum absolute uniform amplitude of each wave, using `abs(sin/cos)<=1`.
Unknown amplitudes retain nulls per axis; unknown phase frequency does not
erase an independently bounded displacement amplitude.

The same record bounds Jacobian row sums using amplitude and phase-gradient
value envelopes, including supported bounded dynamic formulas. For example,
`.02*sin(time)*sin(8*v)` has displacement bound.02and Jacobian perturbation
bound.16. `.02*sin(v*(3+sin(time)))` uses frequency range[2,4]and bound.08.
These are sufficient global nominal bounds with uniform inputs held fixed
over space, not average deformation or measured screen motion.

`amplitude_value_envelopes` and `phase_gradient_value_envelopes` follow the
parent `waves[]` order and declared six-column spatial order. Each includes
finite-input assumptions and unresolved reasons. Numeric vector input lanes
retain qualified names. Explicit native float32 uploads use monotone converted
endpoint domains, rejecting unproved/nonfinite conversion; subsequent arithmetic
is still nominal and native accuracy remains unqualified. No arbitrary audio
range is supplied. Known scalar ranges and phase correlations can tighten the
bound in later work, but missing knowledge never becomes zero response.

Exact binary-rational magnitude products/sums are rounded outward. An
unrepresentable gradient bound remains null while independently known
displacement survives. A positive underflow result rounds up to a positive
representable upper bound. Mixed/radial bases withhold UV Jacobian certificates.
`identity_no_fold_sufficient` requires identity baseline, a single UV basis and
finite perturbation bound below1. Failing the condition is not a fold proof.
`visible_motion_intensity`, actual folds, temporal rates/continuity, prominence,
full feedback behavior and mood remain separate open work.

## Opt-in declared input scenarios

The source exporter accepts `--input-scenario FILE.json`. With no scenario,
source descriptions retain their unconstrained input assumptions. A scenario
adds `analysis.input_scenario` and each supported ripple's separate
`scenario_deformation_envelope`, leaving the ordinary `deformation_envelope`
and all source programs intact. Currently this scenario affects only ripple
deformation bounds, not every field or the existing47-field numerical export.

Example of a **declared mathematical test domain**, not measured music:

```json
{
  "schema_version": 1,
  "name": "bounded-band-example",
  "audio_band_ranges": {
    "bass": [0, 2], "mid": [0, 2], "treb": [0, 2],
    "bass_att": [0, 2], "mid_att": [0, 2], "treb_att": [0, 2]
  },
  "shader_canvas_size": [854, 480]
}
```

Intervals are finite, ordered and nonnegative. Supported names are the eight
engine band/attenuated/volume inputs. EEL aliases apply only to its six native
band variables; `vol`/`vol_att` bind packed shader inputs, never custom EEL
registers of those names. Arbitrary state/Q/source-variable domains are rejected.
Cross-band correlations, waveform reachability and actual music distributions
remain unverified. Relative bands depend on running averages and clock steps;
the producer does not label0–2as a natural/global range.

`shader_canvas_size` supplies actual declared shader-canvas width/height, not
physical display or render-target dimensions. `_c7` dimensions and reciprocals
follow target float32 conversion. Native4K can retain an authored canvas, so
inferring these inputs from the screen resolution would be incorrect. This
declaration does not verify allocation, target selection or runtime binding.

Validated scenarios have a semantic `record_sha256`; each extra envelope cites
it. CLI run manifests also bind the raw scenario-file hash, checking the file
before/after every preset. Cache keys separate scenario/default results. The
API copies validated request data before reading a preset. Changing the file
during a run aborts instead of mixing assumptions. A scenario record explicitly
sets `observed_runtime_inputs:false` and `runtime_binding_verified:false`.
Conditional test-domain bounds are not measured or calibrated mood/genre scores.

## Nonlinear sampled-value coordinate offsets

`sample_value_offset_envelope` reuses typed sample substitution and scalar
value bounds to describe supported nonlinear local image/noise-driven offsets.
Each directly sampled RGBA lane receives an explicit independent[0,1]input
premise. The producer extracts a pointwise-affine spatial baseline and residual
offset, requiring baseline coefficients to be independent of sampled values.
It bounds the residual only; sampled values remain local parameters, not
spatially uniform images or observed texture contents.

For `.05*pow(GetBlur1(uv).r,2)`, a usable unit-input domain gives nominal
offset range[0,.05]. `.03*sin(noise.r*6)` gives[-.03,.03]. These scalar rules
retain blur decoding, domain checks, native upload endpoints and per-axis
unknowns. A singular reciprocal can leave x unresolved while y stays zero.
Image-dependent spatial scale withholds this offset-only model. Original
known-invalid scalar/vector arithmetic is checked before a positive claim,
including zero-product operands, without changing native rendering policy.

`base_coefficient_programs` uses the same six declared spatial columns as the
periodic lookup model; `offset_programs` and per-axis value envelopes preserve
the algebra. `sample_sites` retains local input identity, original sample-site
index, texture name, sampling policy and its coordinate program.
`coordinate_sample_dependency` reports whether a sampled-value input itself
uses image-dependent coordinates; false does not mean its colours are uniform
over the screen. The output ranges include other uniform offsets where bounded.
Native texture binding/decoding and the[0,1]premise remain conditional.

Full coordinate sensitivity, image spatial gradients, feedback evolution,
screen motion/intensity, actual structure/dominance and mood stay unresolved.
An offset range is a magnitude ingredient, not a fluid simulation or a proof
that a particular texture appears on screen. Opt-in declared input scenarios add `scenario_offset_envelope` alongside the
unchanged ordinary bounds. It records the scenario semantic hash, per-axis
value reports and source model. Named audio intervals and explicit shader-canvas
uniforms can constrain audio-scaled or texel-sized offsets. Local sampled RGBA
premises remain independent [0,1] inputs; missing texture contents, singular
image reciprocals and image-dependent spatial scale are not resolved by a
scenario. Observed-input and runtime-binding flags remain false.

For `12*texsize.zw*(GetPixel(uv).rg-.5)` with declared shader canvas 854x480,
the nominal offset intervals are approximately [-6/854,6/854] and
[-6/480,6/480]. They describe source UV displacement, not display pixel speed.
A Native4K panel does not determine these uniforms. Ordinary output stays
unbounded when the caller does not declare canvas dimensions.

## Coordinate-map interpolation

Uniform scalar `lerp(a,b,t)` weights can be distributed across supported ripple
branches. Their spatial phases also support uniform interpolation between
uniform-affine maps. The nominal coefficient rule is `A+t*(B-A)`; offsets retain
an explicit lerp node. Thus equal spatial baselines cancel exactly in symbolic
real arithmetic, even when a local sampled colour drives the blend between two
image offsets. Image-dependent spatial coefficients remain outside the
sample-offset-only model; spatial blend weights are not promoted to uniform.

The original graph is checked for invalid domains before certification, including
branches with zero weights. No interpolation branch is discarded as proof of
finite native behavior. Native HLSL/GLES rounding remains unqualified.

Reference: [Microsoft HLSL lerp](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-lerp).
Original MilkDrop 2.25c `vis_milk2/plugin.cpp` uses the D3DX shader compiler;
the source34 patched GLSL generator maps lerp to mix. This predictor addition
performs nominal source algebra and does not change either renderer.

## Explicit planar periodic folds

`sampling_geometry.stages.*[].folded_coordinate_map` describes supported explicit
coordinate wrapping and mirror-fold kernels. Each axis retains either `frac`
or `triangular_frac` (`abs(2*frac(phase)-1)` or its reversed sign form), an affine
output scale/offset, four planar phase coefficients and a uniform phase offset.
Partial axes remain separate; a supported x axis does not prove the y map.

The phase programs can retain audio/time controls and named audio routes.
A constant, finite, invertible phase matrix in a single shader/original UV basis
provides `repeat_lattice_basis_uv = inverse(M)` and nominal fundamental cell area
`1/abs(det(M))`. Columns translate the source coordinate by complete phase cycles.
Mixed mesh/original bases, dynamic matrices and singular matrices provide no
constant inverse lattice. Dynamic scale can collapse, even when a formula exists.

`fold_output_range` is the unscaled kernel's [0,1] enclosure; frac excludes its
upper endpoint, the triangular kernel includes it. Their derivatives away from
seams are respectively 1 and +/-2. These describe the kernel before exported
output scale and downstream operations. Frac has jumps at integer phases;
triangular folds are continuous nominally with derivative corners. Uniform
inputs are held fixed for these spatial claims. Time/audio changes can still
introduce discontinuities. Negative frac phases use floor, not truncation.

The producer projects supported scalar lanes with a strong memo and bounded
traversal. Original singular arithmetic, including zero-product operands, is
checked before positive results. Image-driven phases, nonlinear spatial phase
products and radial/angular coordinates do not acquire a planar lattice.
Sampler repeat alone does not imply an explicit authored frac operation.

No visible tile count, source coverage, final kaleidoscopic appearance, screen
velocity, feedback stability or mood is certified. Texture content, filtering,
clipping, colour weights, warp mesh and later stages remain separate.

References: [HLSL frac semantics](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-frac)
and [The Book of Shaders: Patterns](https://thebookofshaders.com/09/).
Original MilkDrop2.25c delegates the intrinsic to D3DX; the pinned source34 GLSL
generator maps frac to fract. Neither renderer changes in this increment.

## Quantized colour and declared colour scenarios

Scalar value envelopes support `floor` and `frac` separately from rate calculus.
Floor uses the monotonic endpoint integer levels when the input enclosure is
finite. Frac uses floor-based negative semantics: a range within one floor bin
retains its local fractional interval; a crossing or arbitrary finite interval
gets the conservative [0,1] enclosure. The upper endpoint is an enclosure, not
an assertion that ideal frac reaches 1. Outward interval padding can cross an
integer boundary and conservatively include an extra floor level.

These are value rules only. A seam-crossing fractional or quantized expression
does not acquire a continuous derivative, flash count or motion rate. Known
invalid expressions and nonfinite native uploads remain unresolved. Independent
texture lanes, relevant finite intermediates and native precision conditions stay
explicit.

With an opt-in input scenario, each nonlinear colour stage adds
`scenario_colour_envelope`. It retains separate RGB/channel ranges, unknowns,
the scenario hash and false observed/runtime-binding flags. The ordinary stage
result remains alongside it. For declared bass [0,2] and independent sampled
RGB [0,1], `GetPixel(uv)*bass` has a nominal [0,2] range per channel; this does not
predict average brightness, a palette or flashing. Missing other bands and
nonfinite Q uploads are not supplied by the scenario.

References: [HLSL floor](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-floor),
[HLSL frac](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-frac).
MilkDrop2 delegates shader intrinsics to D3DX; the patched GLSL generator uses
floor and fract. These bounds do not change native semantics.

Floor integer endpoints convert outward when the exact level is not representable
as a float. Caller-declared original finite input names survive native upload
projection; local sampled and derived upload placeholders are excluded from that
summary. The scenario identity retains the corresponding declared intervals.

## Direct raw RGB response to audio bands

Each nonlinear colour stage exports `direct_colour_audio_response`, also inside
its optional scenario record. Each resolved direct band path lists the existing
input code, RGB channel order and three nominal scalar response envelopes.
These reuse the continuous control-response calculus: selected band aliases vary
by the same delta while sampled RGBA values and all other inputs stay fixed.
Independent sampled channels retain the declared [0,1] premise.

`GetPixel(uv)*bass*.2` yields a sufficient raw component-change ceiling of
approximately .2 per bass unit. A product with another band may remain unbounded
until that band's range is explicitly supplied. The result is an upper bound,
not a minimum, typical strength, response direction or time-rate. Reports and
caller scenarios retain their original finite input/domain identities.

Samples are substituted before direct band discovery, so an audio band used
only in sampling coordinates does not become a direct colour route. Such paths
belong to sampling/motion descriptors. Coordinate effects on sampled colours,
image gradients, evolving feedback and native storage are excluded here.

Native upload placeholders keep their original band dependencies. If an
uploaded value depends on the selected band, its per-channel continuous bound
is withheld; it must not masquerade as a held-fixed input with zero gain.
Quantized casts, floor/frac, unsupported/discontinuous operations and unresolved
native domains likewise receive no continuous response credit. A colour range
can remain available while its continuous audio gain is unresolved.

A parsed stage with no discovered direct band paths does not prove the absence
of audio reaction in its coordinates, drawing, feedback or later stages. Unknown
stages retain unknown status. Visible response strength, affected screen area,
brightness, flashes and mood remain uncertified.

Supported nominal continuous response operations include constant-limit
clamp/saturate (nonexpansive), interpolation with product-rule triangle bounds,
and positive constant powers over finite nonnegative base domains. A root or
power below one needs a strictly positive lower base bound; otherwise its
unbounded derivative at zero remains unresolved. Powers retain guarded source
lowering, exact exponent-one identity, and overflow/underflow safeguards.
These rules do not make quantized native uploads continuous.

## Fixed predicates in nominal audio response

A supported conditional can have a continuous response bound for a selected
band when its predicate inputs stay fixed during that variation. This does not
mean the mask is spatially uniform: different fixed coordinates may choose
different branches. For each allowed coordinate/state, the response bound is
the maximum of the two branch bounds. Finite predicate premises are retained.
Both branches must have usable bounds; no inactive branch is discarded to hide
a singular or unsupported domain.

For `uv.x>.5 ? sample*bass : .25*sample*bass`, unit sampled colours held fixed
give a nominal component response ceiling of1. A predicate on mids can stay
fixed for bass variation but remains a discontinuity for mid variation. A
predicate that uses the selected band, unsupported/quantized predicate storage,
or known invalid arithmetic does not receive this continuous-response rule.
Generic unsplit vector input identities conservatively reject any selected lane;
the colour projector's scalar identities permit distinct band lanes.

Audio-dependent native upload placeholders are still checked before this rule.
Fixed band response does not establish fixed masks over time, flash timing,
whole-screen continuity, visibility, feedback stability or a mood score.

## Declared partial source-time response

Eligible shape geometry controls, native mesh controls, texture-sampling offsets,
polar offsets and periodic phase controls add `scenario_time_component` when a
caller supplies an input scenario. The ordinary motion curve is unchanged.
The new record reuses nominal response calculus for source-time aliases advancing
together (`time`, `:native-render-time-f32`, `_c2.x`) and explicitly renames the
upper-bound unit to the control unit per source-time second.

For `.01*sin(time*bass)` and declared bass [0,2], the partial translation-rate
ceiling is approximately .02 source UV per second. Missing band bounds can leave
this rate unbounded. Time-dependent switches, quantized native Q uploads,
unsupported operations and singular domains retain unknown results.

Audio levels, other clocks (frame counters, FPS/progress), state and coordinates
are held fixed. Consequently this is a partial time component, not a total
clock/state/audio motion estimate. For `time+frame`, its time component is1
while `frame` is held fixed; this says nothing about the frame counter's actual
movement. `total_control_rate_per_second` and `visible_motion_speed` stay null.
Geometry trajectories, source-area prominence and feedback are not inferred
from a single control derivative. Existing trajectory/vertex-speed records do
not automatically inherit these bounds.

Finite/input-domain records, caller scenario identity and false observed/native
binding flags accompany each result. Clock jumps, source-to-native rounding,
discrete frames, viewport projection and visibility remain unqualified. A zero
partial time derivative does not mean stationary visuals or a calm preset.

## Vector norm and point-distance bounds

Nominal scalar envelopes support `length` and `distance` over one to four float
components. Distance retains componentwise subtraction before the norm. Raw
vector input components use qualified scalar names/domains. Matrices, mismatched
vector types/widths, unsupported components and quantized response operands stay
unresolved. Colour projection preserves original lane/domain/upload guards.

The component box gives a norm lower bound from each interval's minimum absolute
value (zero when it crosses zero), and an upper bound from maximum absolute
values. Hypot avoids a direct squared-sum overflow/underflow. Endpoint padding is
outward and norm values remain nonnegative. For independent x,y in [-1,1], the
nominal norm enclosure is [0,sqrt(2)]. Missing component-value bounds can leave
values unbounded without necessarily preventing a continuous response bound.

If component response ceilings are L_i, reverse triangle inequality gives norm
response ceiling hypot(L_i). Thus length((x,y)) is1-Lipschitz for x variation,
including at the origin; it does not need the singular derivative of sqrt at0.
This is a sufficient bound, not a positive minimum or actual response. Correlated
components can make it loose; no normalization or final visible geometry follows.
Singular source components and nonfinite/quantized native uploads remain guarded.

References: [HLSL length](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-length),
[HLSL distance](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-distance).
MilkDrop2 delegates these shader intrinsics to D3DX; the patched GLSL generator
retains the corresponding built-ins. Native arithmetic and appearance remain
separate from these nominal source rules.

## Nonzero normalized colour components

The colour projector preserves scalar lanes of `normalize(v)` as an internal
`normalized_component` range/response node, keeping the original shader domain
guard. This internal node is not a shader language extension or exported shader
program. Its typed vector width/index must be valid. The component box must prove
a strictly positive norm minimum after outward padding; a zero-touching box
withholds the normalized component.

Ratio enclosures use component and norm ranges and the unit-component bound
[-1,1], retaining nonnegative/nonpositive signs. For independent sampled RGB
[0,1], `normalize(sample.rgb+.1)` has a nonzero domain and nonnegative unit
component enclosures. `normalize(sample.rgb)` cannot exclude zero length and
remains unknown. A domain-checked normalization is discharged only through this
specific nonzero component proof, not a generic guard bypass.

For vectors with norms at least m>0, normalized-vector difference is at most
original-vector difference divided by m. Thus component response ceiling is
hypot(L_i)/m, where L_i are component response ceilings. This is sufficient,
not a minimum/typical response, direction or final palette. Correlations can
make it loose. Quantized/dynamic native uploads, singular component programs,
invalid shapes and numeric overflow/underflow stay guarded.

Reference: [HLSL normalize](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-normalize).
MilkDrop2 delegates this intrinsic to D3DX and the patched GLSL built-in retains
the same division-by-length domain. Native finite-precision/storage/sampling
behavior, visual geometry, feedback and mood remain separate.

## Flashing mechanisms and feedback movement

`activity.flashing.hazards` now identifies supported periodic full-composite
blackout gates: the same spatially uniform binary source-time comparison
multiplies each contributing RGB channel, leaving raw RGB zero in the off state.
All contributing RGB intermediates must be finite, not just the shader inputs:
for example, finite `bass=0` does not make `1/bass` finite. Known singular
contributing expressions prevent certification; unknown domains retain this premise.
Records contain switch-event rate, blackout cycle rate, period and off fraction.
A spatial mask or added background does not receive that whole-stage claim.
A blackout mechanism is not a verified visible flash: nonblack on-state content,
shader selection, cadence, storage, transitions and trails must retain it.
An empty list is not proof of flash-safe absence.

`activity.motion_intensity.feedback_step_components` reports known native
rotation radians per feedback step and positive uniform zoom factors per step.
Rotation uses the effective matrix angle `atan2(sin(rot),cos(rot))` after native
float32 control conversion, retaining the authored native angle separately.
Full turns therefore do not masquerade as large step movement. Every known mesh
control is domain-checked even when an earlier unknown prevents a complete recipe.
Their rate coefficients can be multiplied by actual feedback FPS under steady
controls/cadence. A constant rot or zoom parameter has zero parameter derivative
but its repeated feedback mapping still moves content. These components do not
certify combined screen motion: other transforms, shader UV changes, texel
alignment, wrapping, clipping and visible feedback content remain separate.
Disconnected and known-invalid native maps do not receive component credit.

`geometry_speed_bounds` exposes already derived polygon-perimeter vertex bounds
in NDC per second, before later mapping/visibility. This does not silently promote
centre-only or partial clock bounds into whole-preset screen speed. Overall
flashing/motion values and mood conclusions remain null pending complete path
and prominence handling. Status describes supported mechanisms, not confidence.

References:

- [Geiss preset authoring](https://www.geisswerks.com/milkdrop/milkdrop_preset_authoring.html): zoom/translation per frame.
- Local projectM authoring guide, `content/1.docs/3.preset-authoring/4.effects/04.image-warp.md`: transforming the previous frame.
- Original MilkDrop2 `vis_milk2/milkdropfs.cpp`, lines 1877–1924: zoom reciprocal, stretch, oscillator displacement, sin/cos rotation and translation.
- Published-core source snapshot `MilkdropPreset/PerPixelMesh.cpp`, lines 250–251 and 305–306: native float rotation sine/cosine.
- [Khronos GLSL specification](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf), section 8.1: radians, sin/cos and two-argument atan. Desktop semantics are a math reference, not GLES runtime qualification.
- [Microsoft HLSL step](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-step) and [smoothstep](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-smoothstep): discontinuous binary switching versus smooth Hermite interpolation, guiding subsequent source flash extraction.

## Shape colour/opacity transfer rates and local jump sources

`activity.flashing.material_change_bounds` links each shape fill or border to
three conditional incoming RGB rate ceilings. For fixed barycentric coordinates,
the interpolated channel magnitude and rate do not exceed the largest endpoint
ceiling. With colour `C` and clamped blend alpha `a`, the incoming term is `a*C`:

```text
incoming_rate <= alpha_max * colour_rate + alpha_rate * colour_max
additive, fixed destination: blended_rate <= incoming_rate
source-alpha-over, fixed destination D in [0,1]:
    blended_rate <= incoming_rate + alpha_rate
```

All operations remain nominal continuous source math, with rate sums rounded
outward. Native upload/storage quantization, clock jumps, moving coverage and
later feedback/shaders remain separate. A source envelope must stay in a stable
modulo cell and have supported continuity/rate. Known native singleton domains
give zero material rate. Texture colour/alpha and coordinates prevent a fill
rate claim; borders are untextured, and their rate applies only while drawn.
Centre colours remain included when centre alpha is zero but perimeter alpha is
nonzero: alpha and colour interpolate independently before multiplication.

Two local hazards are exported separately: `shape_channel_modulo_crossing` and
`shape_border_draw_gate`. They identify possible consumed discontinuity sources,
not reached events or verified screen flashes. Their event frequency stays null.
Disabled borders and fully transparent fills retain the existing consumption
guards. A bounded slow colour term does not certify a calm entire preset.

Original MilkDrop2 `milkdropfs.cpp`, lines 2373–2395, establishes the same
source-alpha/additive-or-over blend factors, but packs authored channels into
8-bit vertex colours. The patched core `CustomShape.cpp`, lines 398–401, uses
those blend factors with the maintained native floating modulo conversion.
This model follows the declared core conversion, not legacy packed-byte steps.
See [Microsoft blending factors](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dblend)
for the source-alpha and inverse-source-alpha definitions.

## Direct shader RGB partial time response

`nonlinear_texture_colour_bounds.stages.{warp,composite}.direct_colour_time_response`
exports three raw RGB partial rate ceilings. The same records are linked by stage
under `activity.flashing.shader_change_bounds`, with default and declared-scenario
records kept separate. The selected aliases `time`, `_c2.x` and
`:native-render-time-f32` advance together at one source second per second within
their continuous clock domains. Audio, state, frame counters, FPS, progress and
spatial coordinates stay fixed, as do the explicit sampled RGBA inputs `[0,1]`.

For `sample*(.5+.5*sin(3*time))`, each raw RGB partial rate is at most 1.5 per
source second. For `sample*sin(3*time)*bass`, a caller-declared bass domain `[0,2]`
gives a ceiling of 6; without an amplitude domain no finite lifetime ceiling is
claimed. These upper bounds need not be reached and are not typical activity.
The native oscillator uniform formulas are followed rather than held fixed.

Time inside a sample coordinate contributes no direct colour multiplier rate
when sampled values are held fixed. A zero direct rate therefore does not certify
a static image. `includes_sampling_coordinate_response=false`,
`samples_are_held_fixed=true`, null total rate and null visible flash frequency
make that boundary machine-readable. Image/feedback history and later passes
remain separate. Quantized time-dependent Q uploads retain taint through scalar
projection and cannot masquerade as zero-rate fixed inputs. Discontinuous gates,
singular arithmetic and unsupported domains retain null channel ceilings.

The clocks may reset or wrap; native CPU/GPU float32 sampling and storage steps
are outside continuous nominal rates. This is source response math, not an AAR
runtime or visual qualification. [Microsoft's HLSL sin reference](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-sin)
specifies radians; the original MilkDrop2 `milkdropfs.cpp` uniform binding and
the current `source_uniforms.native_time_contract` define clock/oscillator inputs.

## Affine sampling motion and texture-gradient coefficients

Each `sampling_geometry.stages.*` lookup now has `sampling_motion`. For a
constant affine map `s=M*p+b(t)`, offset curves bound the lookup-axis speeds in
source texture UV per second. When a single two-dimensional basis is invertible,
an isolated fixed texture feature moves as `p(t)=M^-1*(s-b(t))`. Thus its signed
velocity is `-M^-1*b'` for supported constant-velocity offsets. Otherwise,
`abs(M^-1)*axis_rate_bounds` gives a conservative feature-speed ceiling in that
declared basis. Exact rational determinant/inverse arithmetic avoids treating a
rounded singularity as an invertible map. Mixed bases and singular maps retain
lookup rates but no inverse feature velocity. Native mesh/spatial inputs stay fixed.

`activity.motion_intensity.texture_motion_bounds` links those rates to constant
affine RGB sample weights. For bilinear base-level sampling of fixed texels in
`[0,1]`, each sampled RGBA component changes no faster than:

```text
sample_rate <= W * abs(du/dt) + H * abs(dv/dt)
RGB_i sampling contribution <= sum_j abs(weight_ij) * sample_rate
```

The export stores two dimension coefficients per RGB component; callers supply
the actual uploaded texture width `W` and height `H`. Canvas dimensions are not
silently reused as texture sizes. Rate sums/products round outwards, and overflow
or unrepresentable inverse quantities remain unknown. The formula is a worst-case
adjacent-texel-contrast ceiling: a constant image can produce zero variation.
Nearest filtering, mipmapped/unresolved sampling and non-affine colour mixtures
do not receive bilinear coefficients. Separate sites retain their own weights
and motion; summing their ceilings allows independent or correlated content.

Default and declared-scenario records retain separate identities. Scenario rates
are partial source-time components with audio/state/frame/FPS/progress fixed,
not total movement. Time-dependent sample values, image history, native mesh
motion, direct RGB changes and later composite/feedback terms remain separate.
Wrapping/clipping can change which feature is seen. Neither a lookup rate nor
its inverse feature speed certifies visible screen motion, flashing or mood.

[Microsoft's bilinear filtering reference](https://learn.microsoft.com/en-us/windows/win32/direct3d9/bilinear-texture-filtering)
defines weighted interpolation of neighbouring texels. The dimension factors
above follow from adjacent centres being separated by `1/W` and `1/H` UV units.
Original MilkDrop2 and declared core sampler policies determine the applicable
filter/address mode; native GPU rounding remains outside nominal derivatives.

## Nonlinear sampled-colour response

`nonlinear_texture_colour_bounds.stages.*.direct_sample_colour_response.samples`
exports a 3-by-4 matrix of upper Lipschitz coefficients for each directly sampled
RGBA input. Each column varies one sample lane while all other sampled lanes,
audio/time/state and sampling coordinates remain fixed. Sum column ceilings for
independent simultaneous changes within the declared `[0,1]` input box. This is
not a signed Jacobian, minimum/typical reaction or a complete feedback gain.

Supported powers, products, absolute values, clipping and mixture weights can
therefore propagate sampled-image changes beyond the constant affine RGB model.
For `sample.rgb^2`, the diagonal gain ceiling is 2 on `[0,1]`; a zero-touching
square root has no finite active-lane ceiling. For a clipped mask controlling
`lerp(a,b,mask)`, its influence is bounded by the mask rate times the maximum
`abs(b-a)`, plus endpoint responses. Source finite-intermediate and valid-domain
premises remain explicit. Thresholds, quantized sample-dependent uploads,
singular arithmetic and unresolved vector paths retain null coefficients.

Ordinary float-width casts use the existing typed scalar/broadcast/truncation
policy; a float-vector-to-scalar conversion selects the first lane. Integer/bool
casts and native Q narrowing remain distinct. An unresolved vector sample input
cannot be mistaken for an absent scalar-lane dependency with zero gain.

`texture_motion_bounds.colour_response_model` identifies either
`affine_sample_colour` or `nonlinear_sample_lipschitz`. For the nonlinear path,
column ceilings replace absolute affine row weights in the bilinear dimension
formula. Unknown active column coefficients keep the affected output bound
unknown. Default and scenario response models retain their separate input domains.

Nested samples used only inside another lookup's coordinates are excluded from
these direct colour matrices. Their image-gradient chain is still required:
changing an inner sample can move an outer lookup even if it has no direct RGB
term. No coefficient or null total-rate field claims that nested influence is zero.
See [Microsoft's HLSL lerp definition](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-lerp)
for the mixture formula. The native typed coercion rules and original MilkDrop2
shader expressions determine which lanes reach that formula.

## Nested sample-coordinate motion chains

`sampling_geometry.stages.*.coordinate_sample_response` now supplies a 2-by-4
UV response ceiling matrix for each directly nested sample. Each column varies
one inner RGBA lane, holding other sample lanes and native/time/audio/spatial
inputs fixed. Coordinate products, supported powers and native-upload envelopes
use the existing coefficient projection/calculus. Quantized sample-dependent
coefficients, singular arithmetic and unsupported paths retain null ceilings.
Native aspectX/Y have explicit `[0,1]` domain premises under positive finite
viewport dimensions: source34 `ProjectM.cpp` lines 675–676 computes one or the
ratio of the smaller dimension to the larger, and `MilkdropShader.cpp` binds `_c0`.
Original MilkDrop2 `milkdropfs.cpp` lines 3952–3967 uses the same aspect rule.
This is a source-context premise, not an observed binding or screen size.

`activity.motion_intensity.nested_texture_motion.chains` composes those edges
with linear base-level sampling and direct RGB response. If a root lookup moves
with axis ceilings `u,v`, its sampled component rate is bounded by `Wroot*u +
Hroot*v`. The outer lookup's UV response matrix converts that sampled change into
two coordinate-rate ceilings; multiplying by `Wouter,Houter` gives an outer sampled
component ceiling. Continue through the finite lookup DAG, then multiply by each
output RGB row's summed independent sampled-lane response ceilings.

The result is a nonnegative polynomial, exported as terms with `coefficient` and
`dimension_factors` identifying stage, sample site, sampler/texture and width/height.
Actual uploaded dimensions remain caller inputs. For a root moving at `.1 UV/s`
on x and an outer offset `.2*root.rg`, each RGB path contributes
`.02*Wroot*Wouter + .02*Wroot*Houter` under the declared image/filter premises.
Three lookups produce terms with three dimension factors. Distinct paths are
summed conservatively; cancellation or correlation is not assumed.

Only supported positive lookup-motion paths are exported. `paths_are_exhaustive`
and `full_sampling_motion_bound_verified` are false. Sum terms for modeled
contributions; omitted/unsupported paths, direct time variation in coefficients
or colour, changing textures/history, native mesh and later passes must be added
before any total bound. Nearest/mipmap/unresolved filters receive no smooth
bilinear chain credit. Cycles are excluded and explicit 64-site/4096-term budgets
retain incomplete outcomes. This does not establish typical motion or a mood.

References remain the shader and bilinear filtering guides above; chain products
use exact rational coefficients followed by outward finite conversion. No frame
is constructed and no sample value or image is observed.

## Nearest lookup motion and possible jumps

`activity.flashing.hazards` now includes `nearest_lookup_temporal_jumps` for
declared base-level nearest lookups with a positive supported source-time motion
ceiling and a possible direct RGB or nested-coordinate route. A proved zero gain
does not count as a direct route; dead and stationary lookups do not get this
time-motion claim. The record remains a possible local mechanism, not a verified
flash or an assertion that its movement ceiling is reached.

Nearest selection changes discontinuously at texel cell boundaries when adjacent
texels differ. Constant textures, dimension-one axes, clamping outside the useful
range, masks and sampling/rounding can preserve values. A direct sampled-colour
gain matrix supplies a jump-size ceiling per RGB row by summing its independent
RGBA column bounds over the `[0,1]` input box. Nested or unsupported jump sizes
remain null; no bilinear derivative is assigned to the nearest filter.

`grid_crossing_rate_coefficients_per_uploaded_dimension` is provided only for
nominal constant drift with repeat addressing. For uploaded W/H and drift speeds
`u,v`, the sum `W*abs(u)+H*abs(v)` describes long-run grid-boundary crossings per
source second between clock resets/wraps; simultaneous axis events can coincide.
This is not a count of distinct texel-value changes or visible flashes. Finite
interval endpoint counts and native precision/cadence remain separate.
Sine/compound motion and clamped addressing keep this formula null: a small, fast
oscillation can repeatedly recross one boundary even with a small UV-speed ceiling.

The possible RGB route follows direct sample responses and active/unknown nested
coordinate edges. Actual jump contrast, final coverage, composition and texture
history still determine visible intensity. These hazards must not become an
automatic Party verdict or a claim that an empty list proves Chill suitability.
[Microsoft's nearest-point sampling reference](https://learn.microsoft.com/en-us/windows/win32/direct3d9/nearest-point-sampling)
describes abrupt transitions at texel boundaries. Original MilkDrop2
`milkdropfs.cpp` lines 3921–3927 selects point versus bilinear/anisotropic filtering;
the analyzer retains the declared patched-core sampler policy.

## Native feedback displacement through shader lookups

`activity.motion_intensity.native_lookup_transport` propagates the existing
uniform native mesh displacement envelope into constant-affine authored warp
lookups. If the native displacement is `d` in aspect-corrected coordinates and
the lookup's mesh-UV columns are `M_x,M_y`, then:

```text
RMS lookup displacement <= native_RMS_bound(aspectX,aspectY)
    * (norm(M_x)/aspectX + norm(M_y)/aspectY)
```

Column norms use exact rational squares with outward finite square-root
conversion. Renderer aspects remain explicit finite positive inputs. This
triangle/operator bound may be loose, but remains usable with varying uniform
control domains and procedural-warp envelopes. It integrates over uniform
original UV area and excludes texel alignment and finite-precision interpolation.
It is not a pointwise jump bound, per-second derivative or forward feature speed.

The comparison holds native/control and uniform shader-offset values fixed:
mesh-warped lookup versus the same lookup using original UV. Original-UV-only
and composite lookups bypass this contribution; mixed warp/original mappings
propagate only their mesh-UV columns. Unsupported maps, known-invalid authored
coordinate domains and unresolved native control domains retain null bounds.

`nearest_native_feedback_displacement` records a possible local nearest-main
feedback jump source when the composed RMS ceiling is positive. A positive
ceiling does not prove displacement, a texel crossing or visible flashing.
The retained main image must have differing texels and the shader/coverage path
must preserve their difference. External textures alone do not establish repeated
feature transport. Texture history, offsets, masks, storage and later composition
remain separate. These records do not automatically assign a mood.

Geiss's authoring guide specifies zoom as a per-frame transform; original
MilkDrop2 `milkdropfs.cpp` lines 1877–1924 applies zoom/stretch/warp/rotation and
translation to previous-image sampling coordinates. The declared patched-core
native displacement and shader-coordinate basis models remain the numeric target.
