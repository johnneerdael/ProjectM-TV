# Static effect families from MilkDrop source

Research date: 2026-10-09. Workspace: `predictor-memory-repair`, initial head `ac914c0b2fb8374e7c2f899bcc1d707b627b5a94`. This is source research for extending the predictor after its library migration. No shader simulation, native capture, device run, renderer change, or generated corpus was performed.

## Recommendation

Start with live texture-coordinate transforms and active drawing primitives, then recognize symmetry and temporal self-similarity, then explicit fractal loops. Emit multiple mechanism labels with exact source evidence. Keep **code-family evidence**, **output reachability**, and **visible contribution** separate. A source family can be recognized without certifying that viewers will see it: masks, empty feedback, audio inputs, color cancellation, clipping, and later composition can hide it.

The strongest economical building block is a backward slice of final output components plus their live sample-coordinate graphs. A token or filename match is only a search candidate. Treat unrecognized live operations as a reason to abstain from an appearance conclusion, rather than as absence of an effect.

## Primary references and access boundary

* Ryan Geiss's [MilkDrop 2 authoring guide](https://www.geisswerks.com/hosted/milkdrop2/milkdrop_preset_authoring.html) explains that per-vertex equations produce interpolated sampling coordinates; warp carries the previous image forward; composite produces display output. It documents `uv`, `uv_orig`, `rad`, `ang`, custom waves, and `ret`. Use these stage distinctions in detector evidence.
* Geiss's [How Geiss Worked](https://www.geisswerks.com/geiss/secrets.html) describes the waveform-seed and image-warp cycle. Feedback content and the transformation together determine the evolving picture; a coordinate transformation alone does not establish an illuminated tunnel or visible fractal.
* Tom Lowe's [What is a Mandelbox](https://sites.google.com/site/mandelbox/what-is-a-mandelbox) gives the repeated box fold, ball fold, scale, and translation construction. His [background page](https://sites.google.com/site/mandelbox/background) establishes authorship. Detect this sequence on one evolving spatial state, rather than classifying every `abs` or `clamp` as a folding fractal.
* Patricio Gonzalez Vivo and Jen Lowe's [polar-coordinate discussion](https://thebookofshaders.com/06/), [shapes and radial fields](https://thebookofshaders.com/07/), [2D transformations](https://thebookofshaders.com/08/), and [patterns](https://thebookofshaders.com/09/) provide author-published shader explanations. Radius/angle fields can drive color, geometry, or sampling; the destination of the field matters. Coordinate scaling followed by fractional wrapping repeats a domain, while centered rotation changes a sampling frame. These do not by themselves imply a fractal.
* Official projectM source at the pinned upstream commit `6f64807467e312034883a4389e6aa80a675458bc`: [frame pipeline](https://github.com/projectM-visualizer/projectm/blob/6f64807467e312034883a4389e6aa80a675458bc/src/libprojectM/MilkdropPreset/MilkdropPreset.cpp), [custom waves](https://github.com/projectM-visualizer/projectm/blob/6f64807467e312034883a4389e6aa80a675458bc/src/libprojectM/MilkdropPreset/CustomWaveform.cpp), [built-in waveform drawing](https://github.com/projectM-visualizer/projectm/blob/6f64807467e312034883a4389e6aa80a675458bc/src/libprojectM/MilkdropPreset/Waveform.cpp), and [wave modes](https://github.com/projectM-visualizer/projectm/blob/6f64807467e312034883a4389e6aa80a675458bc/src/libprojectM/MilkdropPreset/WaveformMode.hpp). Custom waves have enabled/sample-count gates, and dots use a point primitive. Built-in mode 0 is Circle; mode 1 is XYOscillationSpiral. Preserve the release's patched pipeline and mode policy when applying these observations.

The requested [Inigo Quilez article index](https://iquilezles.org/articles/) and Mandelbrot/IFS/folding/mandelbulb article requests were attempted. The web tool returned inaccessible/403 responses and ultimately a non-retryable robots restriction; article bodies were not available. Shadertoy examples also failed to load. No assertion below is attributed to unread IQ articles or an unauthenticated shader repost. The concrete formulas below are supported by inspected bundled source and the accessible primary references above.

## Pack census: implementation priority, not prevalence of visible families

Read all **9,606** bundled `.milk` sources. Inventory SHA256: `8d9dca6a3aa1a85d66b15fa52a65a3daa5f767775112d0b97232ff48ca96bcee`. Algorithm: sort exact UTF-8 filenames by Python string order, append each filename's UTF-8 bytes, NUL, and raw 32-byte SHA256 of file bytes to a SHA256 stream. All files were direct children of `core/src/main/assets/presets/`.

Join the `warp_N` and `comp_N` values in source order, remove their backtick prefixes and `//`/`/* ... */` comments, then count sources matching the following lexical predicates. Wave settings use the exact matching wave index; no cross-index combination is allowed. These counts include dead values, unreachable helpers, and masked contributions. They are **candidate workload estimates**, not outputs of a semantic family detector.

| Priority substrate | Candidate sources | Search predicate |
|---|---:|---|
| Main image / feedback sampling | 8,097 | `GetPixel(` or `tex2D(sampler_*main, ...)` in shader code |
| Mesh warp equations | 5,962 | A `per_pixel_N` key exists |
| Custom waveform primitive | 4,641 | At least one `wavecode_i_enabled=1` |
| Absolute-value spatial candidates | 2,894 | Shader `abs(` |
| Custom dot primitive | 1,875 | Same wave has `enabled=1` and `bUseDots=1` |
| Angle field candidates | 915 | Shader `atan2(` |
| Parametric ring/curve candidates | 659 | Same enabled, non-dot custom wave contains `sample`, `x=...cos(...)`, `y=...sin(...)` |
| Complex quadratic candidates | 403 | Component product difference shaped like `z.x*z.x-z.y*z.y` |
| Angular fold candidates | 354 | Shader contains angle input plus `frac`/`fmod` and `abs` |
| Explicit shader recurrence candidates | 294 | Shader `for(` |
| Reciprocal radial projection candidates | 270 | Shader contains `ang/` plus a reciprocal of a `rad...` identifier |
| Literal box-fold candidates | 33 | Shader has `2*clamp(z,-1,1)-z` spelling |

The reciprocal and quadratic searches do not enforce identifier equality or producer-consumer dependency; the semantic pass must. Equivalent spellings are missed. A source with an explicit `while` loop but no `for` is outside the 294 count. Family prevalence requires the final dependency-aware implementation; do not rank fine-grained visible labels using these counts.

## Detection contracts

| Family / mechanism | Mathematical signature on a live graph | Required dependency and contribution checks | Safe output claim |
|---|---|---|---|
| Tunnel / cylindrical projection | Pair an angular coordinate `theta/(2*pi)` or scaled `theta` with a reciprocal/logarithmic radial coordinate, such as `k/(length(p)+eps)`; often add time to depth and wrap the resulting UV | Both coordinates must belong to the same sample/geometry construction and reach output. Check radial singularities, center, aspect correction, wrapping, live masks and sampler content. Radial zoom alone is weaker evidence | `polar_radial_sampling`, with `reciprocal_radius` / `log_radius` subtype; tunnel appearance remains conditional |
| Radial feedback zoom | Previous-frame sample at a centered scaled coordinate, or live native `zoom`/`zoomexp` varying with radius | Resolve the actual mesh UV use, including `uv` vs `uv_orig`. Confirm seed/injection path and final compositing. Separate inverse sampling scale from perceived forward motion | `radial_feedback_transform`; do not force `tunnel` |
| Kaleidoscope | Angle mapped periodically into a sector and reflected, then reconstructed with a paired sine/cosine at the same angle and radius; alternatively reflected Cartesian coordinates sample the same image | Reflection must affect live coordinates, not color magnitude. Sector count must be source-proven; varying count has a domain. Record partial blends and later asymmetry | `angular_mirror_fold`, possibly `sector_count=7`; `cartesian_mirror_fold` separately |
| Rotational symmetry | Shared `sin(N*theta+phase)`/`cos(N*theta+phase)` reaches radial/rotational geometry, or equivalent repeated rotated samples | Require shared frequency/phase provenance and output effect. This can modulate warp without mirroring image sectors | `angular_periodic_warp`; avoid upgrading to kaleidoscope |
| Swirl | Centered rotation matrix with `theta=f(radius,time,audio)`, or native `rot` depends nontrivially on `rad`/position | Rotation must transform live sample/geometry position. A uniform angle is global rotation; a color sine is color animation. Need spatial angular variation for swirl | `radial_twist` plus its time/audio dependencies |
| Flow / advection | Live `uv += v(uv,time,...)`; vector comes from trigonometric/noise fields or sampled image/blur gradients | The computed vector must feed a later contributing sample. Image-derived displacement is content-dependent; distinguish component-color advection from central-difference gradient flow | `uv_advection`, `image_driven_advection`, or `gradient_driven_advection` |
| Complex escape recurrence | Loop-carried state `z -> (zx²-zy²,2*zx*zy)+c`, with norm bailout or orbit/iteration output | Match both lanes to the same prior state, including temporary variables and loop slots. State or bailout must reach output. Classify UV dependence of initial `z` and `c` separately | `complex_quadratic_recurrence`; `julia_style` when z is spatial and c uniform; `mandelbrot_style` when c is spatial and z is fixed |
| Mandelbox / folding recurrence | Loop-carried box reflection, radius-dependent sphere inversion, expansion and translation; equivalent piecewise or clamp form | Fold, norm, sphere factor and affine update must act on the same evolving vector. Loop output must reach geometry, color, sampling, or a live mask. A standalone abs is insufficient | `mandelbox_recurrence` or narrower `iterated_spatial_fold` when sphere fold is unproven |
| Temporal feedback fractal | Nonlinear complex/folding transform samples previous image; or multiple scaled/translated prior-image copies combine repeatedly | Prove previous-frame provenance and nontrivial transformation. For affine copies, distinguish scale recursion from generic echo. Need injection/initial seed, live channels, actual retention, and eventual composite dependencies | `nonlinear_feedback_map` / `multi_copy_feedback_recursion`; visible self-similarity remains conditional |
| Waveform / ring | Built-in source-proven mode, or custom `x=cx+R(sample,...)*cos(theta(sample,...))`, `y=cy+R(...)*sin(theta(...))` with paired radius/phase; implicit radial band in a shader | Wave must be enabled, have effective samples, live opacity, and usable projected positions. A nearly closed loop needs phase traversal and endpoint conditions; audio radius modulation breaks an exact circle | `circular_wave_primitive`, `parametric_radial_curve`, `radial_band` |
| Particle-like points | Enabled dot wave with nontrivial per-sample position; small repeated shape instances with instance-index position/lifetime | Verify actual point/shape primitive, count, opacity/radius, projection, and surviving composition. Randomness is optional; noise in a full-screen shader is not a point primitive. Persistent sample state is not independent particles | `point_cloud_primitive`, possibly `procedural_point_motion`; avoid claiming a particle simulation |

General source motif decisions above are proposed detector rules inferred from the primary mathematics and the examples below. They are not certified visible labels for the pack.

## Exact bundled witnesses

All paths below are relative to `core/src/main/assets/presets/`. Hashes are SHA256 of exact file bytes, calculated in this worktree. Snippets omit `.milk` line prefixes but preserve inspected statements; key names and line ranges locate them.

### 1. Multi-valued quadratic recurrence plus reciprocal tunnel

`cope - mandelbrot (32 iterations) - mrt mangler.milk`

SHA256 `7ccf489af88159857a7a3a862b2f429b7e6140131f300922c8b935ff4fdc7efc`.

Warp lines 249–259 (`warp_4`–`warp_14`):

```hlsl
float2 c = float2(q4, q5);
float2 uxy = (float2(uv.x-q6, uv.y-q7))*zoom;
for (n = 0; n < 32 && dot(uxy,uxy)<4; n++) {
    uxy = float2(uxy.x*uxy.x - uxy.y*uxy.y, uxy.x*uxy.y*2)+c;
}
if (dot(uxy,uxy)>4) {ret = 0;} else {ret=1;}
```

The recurrence is **Julia-style**: starting state depends on UV; `c` is uniform across the screen. The filename is not evidence for Mandelbrot parameter-plane construction. Composite lines 264–287 (`comp_3`–`comp_26`) separately build an angular/reciprocal-radius sample:

```hlsl
float rad2 = length(uv1) + .05;
float rad1 = .1/rad2;
float2 uv2 = float2(ang/3.14, rad1*1.5);
float3 crisp = GetPixel(frac(uv2)) + 2*GetPixel(frac(uv3));
ret = crisp + lay1*mask + mask * GetPixel(frac(uv));
```

Subsequent `pow`/`saturate` operations alter the result. Both code families reach output; neither is guaranteed to be visually dominant.

### 2. Angular kaleidoscope plus content-driven flow

`Geiss - Confetti (Kaleidoscope Mix).milk`

SHA256 `319d04bf16ff3d00bd06840d32256f5652163031575646001df0b2fea24d8392`.

Composite lines 264–272 (`comp_7`–`comp_15`):

```hlsl
float ang2 = frac(ang/6.28*7 + time*0.05);
ang2 = abs(ang2*2-1);
float2 uv2 = 0.5 + rad*0.5*float2(cos(ang2),sin(ang2));
uv = uv2;
ret = tex2D(sampler_main, uv).xyz;
```

This is a seven-sector repeating mirrored angular map. The wedge's reconstruction angle range is authored as `[0,1]` radians; preserve it instead of substituting an ideal textbook wedge. Warp lines 249–253 (`warp_7`–`warp_11`) contain a second family:

```hlsl
float3 blurry_color = tex2D(sampler_main, uv2 + delta2).xyz;
uv2.xy += (blurry_color.xy-0.37) * 0.02;
ret = tex2D(sampler_main, uv2).xyz;
```

The earlier sample drives the later sample coordinates. This is image-driven advection, not an explicit velocity-field or fluid simulation.

### 3. Spatial twist with a built-in circle wave

`Geiss - Mega Swirl 3.milk`

SHA256 `7333edeb0985f99ac8555e446828fab2443d0a5d8b6a3a70238454d911b17617`.

Lines 70–71 (`per_pixel_1`–`per_pixel_2`):

```text
rot=rot+0.16*sin(time*-3.3+rad*11)*(1.3-rad);
zoom=zoom+0.04*sin(time*1.2+ang*6.28*3);
```

Radius and time reach rotation; angle reaches zoom. These are radial twist and angular warp evidence. `nWaveMode=0` (line 8), `bWaveDots=0` (10), `fWaveAlpha=0.5` (21), with no per-frame wave-alpha suppression, provide separate built-in circular-wave evidence. Its drawn seed and feedback can become much less recognizable after repeated warping.

### 4. True box/sphere fold sequence inside a live helper

`martin - mandelbox explorer v1 nz+.milk`

SHA256 `db14c689cde46b655a86bfb568dfc82758547e9ad56caa8037fd2b4ba90c00e8`.

Warp lines 437–443 (`warp_30`–`warp_36`):

```hlsl
zz = uvi; zz0 = zz;
for (int n = 0; n <= 7; n++) {
    zz = 2.0*clamp(zz,-1,1)-zz; tmp = dot(zz,zz);
    if (tmp <= 0.25) {zz *= 4;} else if (tmp <= 1) {zz /= pow(tmp,1);}
    zz = 2.6*zz + zz0;
}
return zz;
```

The helper is called at line 456 (`warp_49`); its norm and structure influence the branch and red-channel update at lines 457–461 (`warp_50`–`warp_54`). Green/blue encode a feedback distance quantity. Composite lines 479–504 transform this intermediate representation strongly. Detect the Mandelbox mechanism without promising a conventional distance-estimator render or a visible 3D Mandelbox silhouette.

### 5. Temporal rational complex map, without an escape-time loop

`flexi - a julia fractal for hexcollie.milk`

SHA256 `80c573e6a7b19baf7127292bf1ee3f53ae61c3ccbfd78dc66139db5fec022a66`.

Warp lines 400–410 (`warp_3`–`warp_13`):

```hlsl
float2 c = float2(-0.12,0.74);
float2 my_uv = (uv-0.5-cntr)*zoom;
float2 u2 = float2(my_uv.x*my_uv.x - my_uv.y*my_uv.y, 2*my_uv.x*my_uv.y);
float2 cu2 = float2(u2.x*c.x - u2.y*c.y, u2.x*c.y + c.x*u2.y);
float denom = 1/((cu2.x+1)*(cu2.x+1)+cu2.y*cu2.y);
my_uv = float2(u2.x*(cu2.x+1)+u2.y*cu2.y,u2.y*(cu2.x+1)-u2.x*cu2.y)*denom;
ret = tex2D(sampler_fc_main, my_uv - floor(my_uv))*0.94;
```

The source map is complex `z²/(1+c*z²)`, followed by coordinate wrapping, sampling, and decay. It supplies nonlinear temporal-feedback evidence; do not invent a Mandelbrot bailout loop. Wave 0 contains apparent random point-cloud code at lines 118–166 but `wavecode_0_enabled=0` (75): suppress its point-family contribution despite `a=0.4` in its unused code.

### 6. Multiple affine feedback copies plus a quadratic feedback map

`Flexi - fractal descent gnesse.milk`

SHA256 `3ec8fe71ad9e9434ff6ab69747edc60ae2789cdab886197095c50f153b0b1aa8`.

Warp lines 533–544 (`warp_3`–`warp_14`) construct four centered scale-2 samples at different `q` translations and combine their red channels with `max`. Lines 548–555 (`warp_18`–`warp_25`) add a distinct quadratic map:

```hlsl
float2 my_uv = (uv_orig-0.5)*zoom;
my_uv = float2(my_uv.x*my_uv.x - my_uv.y*my_uv.y, 2*my_uv.x*my_uv.y) + c;
ret.y = tex2D(sampler_fc_main, my_uv).y + tex2D(sampler_fc_main, 0.5+(uv-0.5)*4).z;
ret.y=1-ret.y;
```

Composite starts with `frac(abs(uv*2-float2(1,1)))` (line 574, `comp_4`) and rearranges feedback channels. Labels can include affine multi-copy recursion, nonlinear complex feedback, and Cartesian mirroring. The final channel inversions and masked color construction prevent a simple guaranteed-fractal claim.

### 7. Active points with procedural sample state

`EoS - particle storm.milk`

SHA256 `28e6f9fd6d6bb60c6ac077b9e18a308f9494252d5e2a495dfebf41d9eb2c766d`.

Wave 0 is enabled (64), dots (68), 512 authored samples (65), alpha 1 (76). Lines 77–100 (`wave_0_per_frame1`–`wave_0_per_point20`) reset `t1/t2` per frame, then create a procedural point walk:

```text
x=t1; y=t2; n=sample*6.283;
xm=sin(n*3)*sin(n*5.7+timeB)*sin(n*11.5+timeA)*sin(n*31);
ym=sin(n*3.5)*sin(n*1.1)*sin(n*23+timeA)*sin(n*13.3+timeB);
x=x+xm*0.1; y=y+ym*0.1;
t1=x; t2=y;
```

This is a point cloud with sequential sample state and time-varying offsets. There is no independent per-particle persistent position/velocity store established by this source. Its `ring` variable at lines 321–326 feeds anisotropic `sx/sy`, not a drawn ring: classify radial warp modulation separately.

### 8. Radial custom curves, disabled dot code, and angular periodic warp

`Shifter-yak(yetanotherkaleidoscope)00.milk`

SHA256 `1970c734a0923def72c7b4e7cfce0588ecfe6ad1a3345928d8b9f8e5e13fab00`.

Wave 1 is enabled (82), non-dot (86), alpha 1 (94). Lines 95–106 contain phase `sp=sample*6.2832-time`, audio-modulated radius, and paired sine/cosine screen positions. This supports an audio-reactive parametric radial curve, not an exact circle. Wave 2 is also enabled and draws a black/alpha-modulated related curve. Wave 0 has random dot code but is disabled (64), so it supplies a useful false-positive fixture.

Per-pixel lines 336–348 modulate zoom and rotation with `sin((ang+phase)*4)`. This is fourfold angular warp evidence. It does not explicitly fold sampling angles into mirrored wedges; a source-only detector should not assign `angular_mirror_fold` solely from the filename.

### 9. Dead tunnel assignment inside a real fractal preset

`martin - mandelbox stepper.milk`

SHA256 `f4ac404bd9e548c503a8c4938ff161e68dd598e1095bfa2260008495c3b1a0a7`.

Composite lines 482–485 (`comp_12`–`comp_15`):

```hlsl
uv2 = float2(1/rad+time/2, ang*2/3.14);
float z = abs(.5/uv.y);
uv2 = float2(z*uv.x, z+time/2);
float2 noise = (tex2D(sampler_noise_hq,uv2)-.5)/z*2;
```

The reciprocal polar assignment is overwritten before use. Its family must not reach output evidence. The replacement is a planar/perspective coordinate map with a horizon singularity, and its noise participates in later live sample offsets. Warp contains a real Mandelbox loop (437–443); multi-family detection must still discard the dead composite tunnel motif.

### 10. Live wormhole-like projection with an unused angle calculation

`EVET - Roach Wormhole.milk`

SHA256 `84a2ebdbb607a5b9a22e322e2ecd4611d883f2cbb53c6b2c2d6bc77cfbe01cbd`.

Composite lines 305–327 (`comp_9`–`comp_31`) compute:

```hlsl
float ang1 = atan2(uv1.y, uv1.x);
float rad2 = length(uv1);
float rad1 = -1*rad2 + 0.05/(rad2-0.08);
float2 uv2 = float2(ang*1.8, clamp(rad1,-8,8));
uv2.y = uv2.y/2 + time/2;
float3 tube = lum(tex2D(sampler_noise_hq, corr*uv2));
float2 uv3 = uv + tube/64;
ret = -1*tube*rad + (1+q24/4)*ret2 * (1-tube/2);
```

`ang1` is dead; the actual angular input is built-in `ang`. The live radial singularity is an offset ring at `rad2=0.08`, bounded by a clamp. The sampled noise drives both displacement and output masks. Recognize polar/radial projection and content-driven contribution; do not claim the angle and radius share the same center or that this is an unobscured texture tunnel. Authored `double3` intermediates also require library support before a complete semantic result.

### Filename-only negative controls

`ORB swirl tunnel.milk` has SHA256 `b0d6242aa199da9a613270e6e181a531d71e283646d65a11f72032146bf12ae2`. Its source uses static zoom/rotation plus per-frame audio rotation, built-in wave mode 1, and no shader polar projection or per-pixel radial twist. Safe evidence is feedback zoom/global rotation/spiral waveform; the name does not prove a tunnel.

`Dbleja - Rings Of Saturn.milk` has SHA256 `6baf285b5b261958dbe8f553c110fb0d2682ef78e00dcc27fe358a957141bda9`. `nWaveMode=1` is a spiral mode, not Circle. Its per-frame source changes native warp/zoom and borders. Do not infer a circle primitive from “Rings”; volume modulation and later feedback can produce ring-like appearance without that exact primitive.

## Fit to `Field` and `LoopPlan`

Inspected `tools/milk-analyzer/shader_fields.py`: `Field` at lines 13–17, `LoopPlan` at 21–27, entry lowering at 367–439, sample construction at 592–620, loop lowering around 880–936, dead-assignment pruning at 955–975. These are recommendations, not changes to those files.

1. **Use the lowered final result, component by component.** A raw AST match can locate a witness, but only a final-result backward slice establishes use. Honor `member`/swizzle, vector construction, per-component stores, `select`/branch predicates, array writes/indexing, helper returns, and `sequence`. Distinguish a value dependency from execution-only effects; an executed dead expression is not visual contribution.
2. **Walk LoopPlan explicitly.** `loop_result` arguments hold initial values, not the whole body. Traverse `detail['plan'].condition`, relevant `updates`, and `effects`, with identity-based cycle protection. Treat `loop_slot(plan,name)` as a recurrence boundary. Compute the backward slice through loop-carried slots to a fixed point: an update of a non-output slot may influence the output slot on the next iteration. Include loop guard dependencies when they affect iteration count or an output-derived bailout. Do not label a loop by tokens in an unused slot update or untouched helper.
3. **Match typed structural motifs without changing execution.** Build a separate recognition view that alpha-renames temporary variables, traces lane provenance, recognizes casts, constructors, swizzles, and aliases, and groups standard mathematical forms. Preserve original `Field` ordering, types, sampler policy, narrow/float32 boundaries, and error evidence. Do not rewrite HLSL execution using associative arithmetic identities; retain sign-sensitive `fmod`, native `frac`, NaN/Inf, and domain distinctions. Normalize `length(p)` vs `sqrt(dot(p,p))` only as recognition categories with domain evidence.
4. **Match same-state recurrences.** Recognize `(zx²-zy²,2*zx*zy)` even through temporaries; ensure all products use the same pre-update state. For box folds require the reflected vector, norm-based factor, scale and translation to be linked, preserving their order. Tag initial-state spatial dependence and recurrence-parameter spatial dependence separately. This avoids the false Mandelbrot inference in witness 1.
5. **Reuse sample provenance.** `Field('sample')` already records `surface`, source `frame`, `site_index`, `canonical_texture`, and `sampling_policy`. Classify warp feedback, composite current-image remapping, blur, external asset, and procedural noise separately. Keep actual sampler address/filter policy, sample channels, coordinate dimensionality, and `uv`/`uv_orig` provenance. A wrap operation in dead code or an unresolved main alias cannot establish visible tiling.
6. **Require a contribution path, with finite-domain proofs.** Track explicit mix weights, additive coefficients, opacity, masks, saturation and final overwrite. Prove a branch impossible or a coefficient zero only within the release's established domains; avoid `0*unknown` and cancellation simplifications when nonfinite values are possible. `saturate` can erase a reachable family. When a mask is variable, emit the family with `contribution=conditional/unknown`, its controlling inputs, and the exact output channels. Unknown masks are not proof of zero.
7. **Bridge mesh and drawing sources.** Shader graphs alone omit native per-pixel zoom/rot and custom wave/shape geometry. Create equally source-bound evidence for those paths, resolve per-frame Q/T dependencies, enabled flags, authored and effective sample count, alpha/radius, instance count, point-vs-line topology, and audio-value inputs. Preserve sample-order state; do not treat a custom wave's `t1` as independent particle storage. Resolve the patched library's built-in mode map rather than duplicating an assumed map.
8. **Treat temporal feedback as a structural cycle.** Refer to the previous-frame surface and the same stage's transform without unrolling frames. Annotate nonlinear map / multiple distinct affine copies / retention / injection source. Repeated ordinary zoom is not sufficient for a generic fractal label. A fold used only once for mirror compositing is symmetry, not an iterated folding fractal. Unknown seed content or retained channel state requires a visibility abstention.

Suggested evidence record, expressed conceptually rather than as a new API contract:

```text
family: [complex_quadratic_recurrence, polar_radial_sampling]
source_identity: {exact_path, sha256, section_keys, line_spans}
stage_and_outputs: {warp:red/green/blue, composite:red/green/blue}
mechanism: {initial_z_dependency, c_dependency, recurrence, sample_surface}
reachability: proven | conditional | unresolved
contribution: potential | conditional | proven_zero | unresolved
controls: [mask, audio, time, external_texture, feedback_content]
abstention_reasons: [...]
```

Avoid a single mutually exclusive category, an invented confidence percentage, or the phrase “guaranteed visible” for code motifs. Source-proven primitive activation is stronger than a shader token, but the final composite still governs visibility.

## Minimal follow-on verification recommendations

After library migration, use source fixtures anchored to the exact hashes above. Verify motif results for reachable variants and semantic negatives: final overwrite, zero/unknown mask, unreachable helper, disabled wave, disabled point primitive, partial-channel write, UV-vs-uniform `c`, loop with an unrelated unused fold update, and the real overwritten tunnel in witness 9. Include equivalent constructor/temporary spellings and deliberately unrelated `abs`/`atan2` calls.

Run a source-only candidate-to-evidence census once these detectors exist. Publish detected, rejected, and abstained counts with reasons, maintaining the same 9,606-source denominator. The current lexical census cannot stand in for that result. Escalate only unresolved live source features to the existing more expensive analysis path when an actual downstream appearance decision requires them; do not make simulation mandatory to report a source-proven mechanism.
