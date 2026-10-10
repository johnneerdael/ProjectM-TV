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
| `activity.flashing`, `activity.motion_intensity` | Currently unknown; structural evidence is not a speed/flash measurement |
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
remain inputs. Initial audio/time captures use `init:<section>:<variable>` input
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
