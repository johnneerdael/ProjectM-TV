# I16 fullpipeline owner controls — source-only, not a generic repair

The original DESIGN.md/proposal-interface and their failures/limits remain. New disabled_uv_pipeline_controls.cpp, CMakeLists.txt and TEST-ONLY-eager-publication-oracle.patch are uncompiled proposals. No configure/build, GPU/device, Git or canonical/helper edit was performed. There is no production GetUV API. Source owner preparation is complete only as a proposal; runtime, Native images/cost and any generic fix remain open.

## Decisive fullpipeline sequence

Invoke actual ProjectM::RenderFrame with a loaded finite preset and explicit clock. Engine frame count is read through the existing test-friend access and checked, not guessed from screenshot labels. The source profile is affine/finite: zoom/exponent/stretch1, rotation/warp0, dy0, dx=−.0625×max(1,min(4,frame)). mv_x/y2 and diversions(.3,−.3) admit one center start(.5,.5). Per-pixel reg00 increments exactly1617 times per48×32 mesh frame; no diagnostic GetUV or EEL volume substitution occurs.

| Frame | Vectors | Current center UV computed by warp | Consumer must use |
|---|---|---|---|
| 0 warm | enabled, first-frame guard | .5625,.5 | no motion draw |
| 1 A | enabled | .5625,.5 | warm .5625,.5 |
| 2 B | disabled | .625,.5 | no motion draw |
| 3 C | reenabled | .6875,.5 | B .625,.5, never current C |
| 4 D | enabled | .75,.5 | published C .6875,.5 |

Current gating leaves A published across B, so C's actual endpoint is.5625. The eager temporal oracle publishes B, so C's endpoint is.625. Both use.6875 at D. Displacements.0625/.125/.1875 are well above all current I15 thresholds, including Native diffusion scaling; the witness avoids confusing stale fields with minimum-length behavior. Current triangle/float16/arithmetic policies are shared between roles; this is temporal proof, not I14/full original CPU parity.

Those table values are ideal producer centers. Actual RG16F raster/storage/filtering can bias even affine center samples, especially at the1280×720 canvas. The control records actual four-texel centers, admits a bounded6e−4 storage/producer difference from the ideal values, then compares actual TF endpoints tightly against the **actual stored** A/B/C values and publication provenance. It does not replace GPU conversion with a guessed half mode or silently sanitize Y to.5.

The CGL control reuses the ignored motion-style test's actual production-vertex TF observer by inclusion; it does not alter that support file. At the fullpipeline warp draw it additionally records actual COLOR_ATTACHMENT1 texture and enabled draw-buffer1, deriving publication generation from actual MRT submission. It queries the published RG16F texture storage through a **test-only temporary readback FBO**, averaging the actual four center texels corresponding to the existing linear sampler query. This is readback instrumentation of the owned attachment, not a new GetUV API or a fabricated mesh array.

The motion TF record identifies the bound texture lease and actual shader endpoint before current warp; the post-frame published storage confirms which generation became visible. Assertions cover current/eager declared roles, enabled/disabled sequences, default warp and a bounded no-discard compiled GetPixel(uv) custom warp, below-reference256×144 and Native/ref3840×2160→1280×720. Native detail requires two consumers, native and later authored; both must sample the previous published field before the current canvas warp publishes C. First warm detail initialization may replace native-sized UV storage with the canvas allocation; that first-frame lease replacement is admitted only under its authoritative no-motion guard.

No shader-copy endpoint producer is used. The existing TF support forwards actual indexed production drawing once, then captures a verified continuous-index shadow through the same program/VAO; array/instanced paths capture the actual forwarded draw. Those test-only queries/maps/shadows add work and are not shipping timing samples. CGL's binary-cache/tie-bias admission differs from GLES; Android qualification remains separate. Controls depend on the current ignored TF support file hash, which the parent must refreeze after its own setup fixes.

## TEST-ONLY eager oracle and cost

The eager patch makes the existing actual writeMotionUV decision true every frame. It changes neither equations nor warp/fragment producer, requires no added pass, and preserves the real fragment's current coverage/discard semantics. In the five-frame disabled sequence it produces five UV publications versus current four; enabled control produces five in either role. This is an explicit **temporal expectation/cost oracle**, not an accepted production fix, generic lazy catch-up, or unchanged-library evidence.

Every disabled frame regains4×Wuv×Huv logical RG16F payload bytes. At256×144:147456 bytes; actual1280×720:3686400 bytes(3.515625MiB); actual3840×2160:33177600 bytes(31.640625MiB). Additional MRT store/invalidation/driver behavior needs clean timing. Native Standard with active detail normally writes the actual1280×720 canvas map; native fallback/no detail can own a native-sized map. Do not budget every Native4K frame as full4K UV or claim no performance impact. A continuously disabled run is necessary to quantify the work that current gating removed; the CGL instrumented run cannot supply that timing.

## Future lazy repair requires a stronger owner contract

Before the first active motion consumer, previous prepared mesh attributes still belong to completed B until current CalculateMesh/InitializeMesh replaces them. A narrow replay might reuse those buffers, but must explicitly retain/generation-check:

- Grid/topology/actual compiled path, instance/context/configuration generations, completion and publication generations, allocated UV dimensions and first-frame admission.
- GPU mesh positions/indices/radius-angle, evaluated zoom/rotation/warp/center/distance/stretch, CPU cosine and negative zoom-power buffers. No second equation execution or mutable Q/RNG reload is allowed.
- Actual prior bound vertex transformation, warp time/factors/scale, aspect/inverse aspect, normalized texel offsets and effective viewport. Cache **actual bound values**: authored GL viewport/UV allocation can differ from render-context dimensions used by WarpedBlit's texel-offset denominator.
- The correct per-preset UV attachment/texture ownership and retirement. Handle identity is insufficient across context loss/reuse. Resize, grid change, authored/native policy change, shader failure/path change, preset switch, transitions and memory-pressure cleanup must invalidate or authoritatively suppress motion, not manufacture valid old geometry.
- Default shader/program resources and leases under the GL thread's ordered command stream. Shared shader uniforms are mutable across instances/passes; merely retaining a shader pointer does not retain B's uniform state. Two preset instances need separate producer metadata.

`DrawAgain` is a current-frame replay: it recomputes live uniforms, binds live fragment/sampler inputs and invalidates attachments. Calling it before C's motion cannot safely recreate B. A dedicated UV-only operation must avoid color sampling/writing/invalidation and preserve/readjust FBO/draw buffers/viewport/program/VAO/buffer/sampler/blend state. It must run before replacement of B's buffers and before either native/authored consumer, publishing only after compatible reconstruction succeeds.

Custom limits are material: the transpiler initializes _mv_tex_coords from _uv before user body, but clip/discard can preserve older map pixels, explicit injected-coordinate writes can change the output, and sampling/RNG/Q/blur/main-texture state can affect discard. Generic UV-only coverage does not reproduce this. Reexecuting the old fragment would need the exact prior inputs and texture leases, potentially large memory/resource retention, and can repeat side effects/random work. No such generic reconstruction or reliable no-discard/output-write classifier is qualified here. Bounded default/no-discard tests do not certify arbitrary custom/fallback/discard paths.

Prove failure/fallback and invalid generations preserve the current first-frame/visibility rules. Do not silently continuously publish for unknown custom programs while calling that a lazy no-cost repair. Eager fallback is a separate performance/policy decision. All fields/buffers must remain instance-owned and follow existing custom-pack/texture-reader/context lifetimes.

## Finite Native diagnostic and expected source sibling

New biased default/custom fixtures use the same five-frame equation protocol as the CGL source. Preserve feedback with the actual warp producer; a constant-black warp would erase the pre-warp motion overlay. Seed/verify a known dark feedback field, retain completed frame/clock/PCM/RNG/preset/native identities and record actual motion map dimensions plus both consumer viewports. C is red; earlier frames are blue. Capture motion endpoint/UV publication first, final output second, then D.

Current and eager source-oracle runs use identical preset bytes; only the explicitly test-only eager engine patch differs. The source expectation is latest previous B rather than current C. On the affine default below-reference context, C's warp shifts the red overlay left by.1875, so current endpoint-model final X is.375 while eager is.4375; these are stage-derived locations, not original Windows pixel equality. Actual texture filter/storage/composite/Native detail can alter final coverage; do not substitute the modeled crop for real captures.

If a generic lazy repair cannot preserve all producer domains/lifetimes while meeting cost gates, disposition should remain an explicit I16 deviation/deferred repair with this owner packet. No global Native/reference/trails rollback is proposed.

## Original candidate and further gates

Exact101.milk hash is a901944f8f1d668e38fac317dff5e596b3f4d80e837a6083695bc58b3278154c. Legacy warp0 and nonlinear zoom depend on q1 while mv_a follows bass. A real on/off/on bass journey crossing1.2 must be recorded from actual analysis, evaluated alpha/Q and produced fields; mono PCM transport is still the actual TV path. Filename/lexical candidacy does not establish that a chosen PCM crosses it. No unchanged original was executed here and the435 handoff candidates are not an affected census.

Additional source/Native gates remain: multiple disabled frames with changing B, count-based off/on and alpha threshold, A=B, all-enabled/all-disabled, nonzero texel offsets, changing warp time/rotation/negative zoom, two preset instances, resize/context/detail/generation invalidation, actual compiled fallback and custom discard/output-write domains. Preserve all prior field/mesh/preset/texture policies. Root owns builds, actual CGL results, captures and clean cost; this proposal does not close I16.

Root actual CGL exposed a filter/return-precision difference: CPU average of four RG16F texels at the centre is(.562255859,.499877930), while actual vertex texture sampling returns endpoint(.5625,.5). The initial2e-5exact-average assertion was invalid on this backend. Temporal tests use the alreadydeclared6e-4storage/filter bound, while preserving actual texture leases, publication generations and .0625-separated fields. This qualifies temporal provenance, not exactfloat32filter reconstruction. Initial failure and values are retained.
