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
operation. Nested assignment/reference-alias expressions remain explicit gaps
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

Shape x/y units are authored coordinates, radius is the source radius/NDC unit,
and angle is radians. Mesh rotation's control unit is radians per feedback step;
its time derivative changes that per-step amount. `application` explicitly marks
mesh controls as `feedback sampling transform each step`. A constant rot.02 can
rotate sampled feedback every step despite a zero control derivative. FPS, native
warp-time math, feedback composition and visibility are still needed for image
speed; `visible_motion_speed` and activity/mood scores remain null.

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
