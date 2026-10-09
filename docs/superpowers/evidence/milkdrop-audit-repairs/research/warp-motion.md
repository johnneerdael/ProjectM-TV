## Read-only warp/motion report

Inspected the task worktree, patched engine and handoffs. **No files were edited; no builds, tests, GL rendering or devices were used.** Screenshots below are capture designs, not completed evidence.

All seven differences remain in the inspected source. I05 has a straightforward bounded repair. I10–I13 can be repaired within the proven legacy path. I16 has a plausible re-enable-only repair that avoids continuous UV writes, but requires a dedicated replay path. I14 needs a separate motion-coordinate implementation or an explicit deferral; changing warp topology or RG16F alone cannot resolve it.

### Inspected identity and boundaries

- Ordered patches: **0001–0017**, concatenated-byte SHA256 `21ee17d19ce803bacda39d54f9e43b1060f9aee5042789d1e9a94146883ed0a8`.
- `PerPixelContext.cpp`: `18914393695f2c22f7df7a26516662d1aa4ef76b80de4efc538842650d1dcd3a`.
- `PerPixelMesh.cpp`: `1f95b181583ef7974225d42c135eb89f696e1be1c10f44b491f7efc400c8999a`.
- `MilkdropPreset.cpp`: `6a7074f383832fad96754ef93e8a596dd0d15b8720a16be025e7febf60e74c82`.
- Warp VS: `b44d18c7cc50714b3b324d3934ed09be5299b1558386f76ff637df452eb99831`.

`milkdropfs.cpp`, `plugin.cpp` and `support.cpp` under `/Users/jneerdael/Scripts/milkdrop2/src/vis_milk2` are byte-identical to the original reference:

| File | SHA256 |
|---|---|
| `milkdropfs.cpp` | `68749d31bb6b3020ca89b1e7630fd704e58a5de8dd6275c9f5ea005c6586a7d9` |
| `plugin.cpp` | `c768b9a3a2f434a1a29155eceea32ade812c7cd65f73bf05f63823b9f7dc7d65` |
| `support.cpp` | `501e85a89794cbcd40f1e6c1017d4e279004a480d1deb32ee32dd1cfe3ee18a5` |

Original custom warp compilation requests `data\warp_vs.fx`; that shader is absent from the examined source trees. Consequently:

- The physical Y, diagonal and traversal conclusions below apply to **legacy fixed-function warp**.
- Preserve the existing custom-warp path until its projection contract is independently established.
- Gate legacy behavior on the **actual compiled path**, including shader compilation fallback, rather than only `PSVERSION_WARP`.
- Preserve current CPU sine/cosine production, negative zoom power, raw/nonfinite equations, authored/native canvas ownership and `DrawAgain` replay without equation re-execution.

All candidate names/hashes below were checked against current bundled assets. Counts are the handoff’s **lexical candidate counts**, not confirmed affected presets.

## I05 — Per-pixel inverse aspect inputs

**Source proof.** Original per-pixel inputs receive `m_fInvAspectX/Y` at [milkdropfs.cpp:655](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:655). Current per-pixel inputs receive `renderContext.aspectX/Y` at [PerPixelContext.cpp:94](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/PerPixelContext.cpp:94). The existing context already supplies both inverse fields.

**Safe repair.** Change only these two per-pixel read-only assignments to inverse aspect. Preserve main-frame/shader aspect inputs and `ShaderCanvasSize()` pixel inputs. This source contract does not depend on the missing original VS.

**Best static original witness.** [163.milk:487](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/core/src/main/assets/presets/163.milk:487), SHA256 `ee1c2c11cc38844dfa185cc64d67afd69f97c2f803262cac94c47eeb416a0b5d`.

Its only two active per-pixel expressions multiply coordinates by `pixelsx*aspectx` and `pixelsy*aspecty`; comments explicitly describe aspect-independent square sizes. `PSVERSION_WARP=0`. Init uses random `q3/q4/q5`, so freeze the actual RNG lifecycle rather than substituting chosen Q values for original-preset screenshots. Handoff count: **248 candidates**.

**Focused regression.**

- Matched 256×144, mesh48×32: per-pixel `aspecty` must change `.5625 → 1.7777778`; `dx=aspecty/10` changes `.05625 → .17777778`.
- Assert square-aspect equality and unchanged main-frame aspect.
- Add portrait inverse-aspect control.
- Verify geometry evaluation happens once with Native canvas replay.

**Pixel captures.** Seed a known feedback field for the synthetic displacement control. Capture before/candidate/source-expected at the matched canvas. Then capture exact `163.milk` at Native Standard 4K with identical seed/PCM/time and actual authored canvas recorded. Show full output plus the square-cell region; expected behavior is restored authored aspect scaling, not global pixel identity.

**Cost.** No added pass, attachment, vertex work or meaningful memory. Two assignments change.

## I10 — Legacy physical warp Y argument

**Source proof.**

- Original mesh stores `y=2*row/gridY-1`; UV equations use `-m_verts[n].y` for initial V but **unnegated** Y in warp oscillators: [milkdropfs.cpp:1881](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:1881).
- Legacy draw negates emitted Y: [milkdropfs.cpp:2056](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:2056).
- Fixed-function projection has negative height: [support.cpp:180](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/support.cpp:180).
- Current flipped projection directly draws unflipped mesh positions: [PresetState.cpp:15](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/PresetState.cpp:15).
- Current warp oscillators use `pos.y`: [warp VS:64](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/Shaders/PresetWarpVertexShaderGlsl330.vert:64).

Thus matched physical points have opposite oscillator Y arguments in the proven legacy path.

**Safe repair.** Introduce a legacy-only oscillator coordinate `warpY=-pos.y`. Use it only in the four deformation arguments. Preserve `gl_Position`, initial UV, equation coordinates, original-UV varyings, rotation and negative-power attributes. Both custom and default programs currently consume the same VS; a blanket sign change would exceed the evidence.

**Best static original witness.** [BrainStain-sunrays.milk:37](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/core/src/main/assets/presets/BrainStain-sunrays.milk:37), SHA256 `b3ebf1ab3f1132d2215e493fe9942693b0e70361c5c269cf86cff890520e2ef5`.

Legacy preset, no per-pixel code, `warp=50`, `fWarpScale=62`, no later warp assignment. This is stronger than a small literal warp in a complex mashup. Handoff count: **1,737 candidates**.

**Focused regression.**

- Square/unit-aspect control, physical normalized point `(.6,.7)`, time/rotation0, warp1, zoom1.
- Reproduce before UV approximately `(.6032275,.7047434)` versus original legacy `(.6032086,.6974467)`, before texel offsets.
- Test positive/negative warp and multiple times; warp0 must remain unchanged.
- Re-run CPU rotation and negative-power controls, including nonfinite fractional cases.
- Require custom-warp control unchanged.

**Pixel captures.** Known asymmetric grid feedback isolates Y deformation; include upper/lower mirrored crops. Capture original `BrainStain-sunrays` before/candidate at identical Native Standard 4K conditions. Original-source expected GPU captures must be labelled source-derived, not Windows/D3D recordings.

**Cost.** No added pass or storage. One sign/coordinate choice per existing vertex; same four trig evaluations.

## I11 — Legacy physical triangle diagonal

**Source proof.** Original and current index arithmetic is nominally the same:

- [plugin.cpp:2346](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/plugin.cpp:2346).
- [PerPixelMesh.cpp:212](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/PerPixelMesh.cpp:212).

But the original legacy Y emission flip reverses which physical corners those indices join. Changing only oscillator Y cannot fix this geometry difference.

**Safe repair.** Select the opposite cell diagonal only for the actual legacy path. Preserve mesh positions, per-vertex values and custom-warp topology. Either maintain separate legacy/custom index sets or rebuild indices when the compiled path changes. Preserve triangle winding/culling and quadrant draw order.

**Best static original witness.** [07.milk:438](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/core/src/main/assets/presets/07.milk:438), SHA256 `ec440dc5d1409388d8b55c17e683bbe8e1cd5effac1060faefdb71e222ad7849`.

Only per-pixel expression: `zoom=1+(sin(ang*6)*.5+.5)*.04`; per-frame warp is explicitly0. This removes I10 and stateful traversal as competing explanations. Handoff count: **878 candidates**.

**Focused regression.**

- Inject physical cell corners A=B=C=0,D=1; at local `(.25,.25)`, before interpolation0, original diagonal `.25`.
- Inspect all quadrants, both triangle interiors, boundaries and winding.
- Affine UV fields must remain equal.
- Verify custom-warp indices unchanged.
- Check authored/native replay uses identical prepared attributes and intended topology.

**Pixel captures.** Render the injected cell field against a contrasting known texture, capturing the cell’s two interiors. Capture exact `07.milk` at Native4K with a mesh-cell crop overlay. Avoid promising visible differences at every chosen frame: the original screenshot must establish the nonlinear field actually exposes the diagonal.

**Cost.** Same draw/pass, vertices, triangles and index count. A second index set adds `6*gridX*gridY*sizeof(index)` storage if used; rebuilding one set requires no persistent second allocation. At48×32, 9,216 indices; byte count depends on the actual index type.

## I12 — Stateful per-pixel physical traversal

**Source proof.**

- Original Q copied once before mesh traversal: [milkdropfs.cpp:675](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:675).
- Original source rows execute ascending: [milkdropfs.cpp:1824](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:1824); the proven legacy projection places those physical rows opposite current ascending traversal.
- Current sequential evaluation: [PerPixelMesh.cpp:245](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/PerPixelMesh.cpp:245), with Q copied once at [PerPixelContext.cpp:98](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/PerPixelContext.cpp:98).

**Safe repair.** For legacy, evaluate current mesh rows descending, X ascending. Address buffers by `row*(gridX+1)+column` instead of the present sequential `vertex++`. Do not reset Q/ordinary locals/registers between vertices; do not parallelize evaluation. Preserve custom-warp traversal until its original physical mapping is known.

**Best static original witness.** [shifter - neon pulse.milk:282](</Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/core/src/main/assets/presets/shifter - neon pulse.milk:282>), SHA256 `605d80e5c1480be3fd21ef57cbd2780cbff192f06be5b6a4268ddf2d80aafcf2`.

This is stronger than merely seeing `q1=q1+1`: `q1` resets per frame; `coy` tracks row changes via `below(y,oy)`, `cox` advances through rows, and `dx/dy` use the counters before `oy/ocoy/q1` update. It is an actual source-level route from traversal state to geometry. Per-frame warp0 removes I10. Handoff count: **10 candidates**.

**Focused regression.**

- Fresh mesh8×8, Q0, `q1+=1; dx=q1*.001`: physical top-left before Q1/dx`.001`; original legacy Q73/dx`.073`.
- Trace every vertex order and ordinary-local recurrence, not just final Q81.
- Assert Q copied once/frame and stateless `dx=x*.001` equality.
- Count equation evaluations across authored/native replay; must remain81 in the8×8 case.
- Include reg/gmegabuf recurrence and a custom-warp unchanged control.

**Pixel captures.** Synthetic ordinal displacement over a labelled grid produces an interpretable before/expected row difference. Capture exact `shifter - neon pulse` after stable nonzero time steps; its per-frame `1/tic` expressions make a malformed startup clock unsuitable evidence. Show the counter-driven tile region with full output.

**Cost.** No added evaluations, pass or memory. Same vertex count, with different CPU buffer access order. Cache effects require measurements; no timing inference is justified.

## I13 — Exact left-axis angle seam

**Source proof.**

- Original stored angle is `atan2f(y*aspectY,x*aspectX)`: [plugin.cpp:2285](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/plugin.cpp:2285).
- Original uses it directly in equations: [milkdropfs.cpp:1842](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:1842).
- Current equations negate stored angle: [PerPixelMesh.cpp:263](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/PerPixelMesh.cpp:263).

At the legacy physical left-middle axis, original positive-zero numerator yields `+pi`; current negation yields `-pi`.

**Safe repair.** Preserve off-axis negation and existing radius/angle varyings; narrowly supply the original positive-zero left-axis angle to per-pixel equations. Do not normalize arbitrary authored angles.

**Important trap:** replacing `-atan2(y,x)` with `atan2(-y,x)` does not by itself fix the seam: negating `+0` supplies `-0` and still selects `-pi`. Original generated midpoint zero must be represented deliberately.

**Best static original witness.** [Illusion & Rovastar - Dotty Mad Space (Jelly).milk:233](</Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/core/src/main/assets/presets/Illusion & Rovastar - Dotty Mad Space (Jelly).milk:233>), SHA256 `ba01ee4a189ddb10a0ad205df0a419494c82210450672c60a88fa812384beb00`.

`sy += if(above(3.14-ang,0),.1,-.1)` selects `-.1` at original `+pi`, versus `+.1` at current `-pi`: a **finite .2 stretch difference**. It has `PSVERSION_WARP=0`, per-frame warp0 and only one other simple per-pixel expression. This is stronger than candidates using periodic sine or a logarithm gated away from the midpoint. Handoff count: **204 candidates**.

**Focused regression.**

- Mesh with exact midpoint: assert float angle sign and equation result using `dx=above(ang,0)`.
- Test left midpoint, center, right midpoint and adjacent rows.
- Test ±0 arithmetic explicitly without converting arbitrary authored nonfinite values.
- Periodic sin/cos controls and custom-warp behavior remain bounded separately.
- Include the original `3.14-ang` stretch expression.

**Pixel captures.** Synthetic seam control over a grid, with left-middle mesh-cell crop; exact original preset gives a finite stretch witness. Capture the same mesh and frame at Native4K. A midpoint vertex’s effect interpolates into neighboring triangles, so the expected evidence should identify that local region.

**Cost.** No pass/storage increase; a narrow per-vertex condition or precomputed seam value.

## I14 — Motion interpolation and half storage

**Source proof.**

Original reverse propagation independently interpolates four float mesh corners and returns `(tu,1-tv)`: [milkdropfs.cpp:1514](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:1514). Current reverse propagation samples a linearly filtered full-canvas texture in both GL-line and Native quad paths:

- [motion VS:26](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/Shaders/PresetMotionVectorsVertexShaderGlsl330.vert:26).
- [quad motion VS:33](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/Shaders/MotionVectorLineVertexShaderGlsl330.vert:33).
- RG16F allocation: [MilkdropPreset.cpp:477](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/MilkdropPreset.cpp:477).

The source divergence has **three layers**: triangle versus bilinear interpolation, finite raster/filter sampling and half storage. RG32F alone only removes the last layer. I11’s diagonal repair still leaves triangle interpolation.

**Coordinate warning.** Original reverse propagation indexes raw `m_verts` rows from `fy`, then inverts V. This is distinct from the proven physical legacy raster mapping. Do not simply sample a bilinear version of the newly corrected I10 physical warp map and claim original motion parity.

**Best isolatable original witness.** [Pithlit - Colourfall (Jelly).milk:226](</Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/core/src/main/assets/presets/Pithlit - Colourfall (Jelly).milk:226>), SHA256 `4128f114ed071efeec6876f0e71a431a7522f84eb3ed58c20460467fe4683dc7`.

Legacy warp, one radial zoom equation, static nonzero `mv_a=.01`, `mv_l=.9`, grid12×9. A stronger visual stress candidate is `fiShbRaiN - city slicker.milk`, SHA256 `382688e31a8e1ed82968f1a2be31d09ce37041d2f104b5171936e452dd7dbc05`: warp5.277905, static active vectors, no per-pixel code. Its changes overlap I10, so it should follow the isolated stage control. Handoff count: **794 candidates**.

Excluded misleading shortlist example: `3dRaGoNs & Rovastar - StarGate rEmIx (Jelly)` sets per-frame warp0 **and `mv_l=0`**, so its endpoints cannot establish this interpolation issue.

**Repair alternatives.**

1. **CPU original-node UV + bilinear endpoints:** mirror original UV arithmetic after existing evaluated float attributes, retain prior node UVs, bilinearly interpolate motion endpoints. No readback/full-size map required. However, this duplicates four warp trig evaluations and positive zoom powers per vertex and must preserve current positive GPU warp arithmetic for feedback; it is a distinct motion producer needing careful versioning.
2. **GPU compact node UVs:** evaluate nodes using a dedicated vertex path, capture float32 UV via transform feedback, and expose compact nodes to motion shaders for four explicit fetches/weighted sums. This could avoid full-canvas raster/filter/half boundaries while preserving existing GPU arithmetic. It still needs the original reverse-node coordinate contract, high precision, lifecycle ownership and a proven buffer-to-texture path. **Feasibility is not established by this read-only investigation.**
3. Compact RG32F rendered node target is another possibility, but GLES3 texture support does not establish RG32F color-renderability. Do not assume the RG16F backend qualification permits it.
4. If those approaches cannot safely meet Native4K resource/performance gates, defer with the precise current GPU triangle/RG16F policy. This is a genuine source deviation, not a completed repair.

**Focused regression.**

- A=B=C=(0,0),D=(1,1), local `(.25,.25)`: original bilinear `(.0625,.0625)`, current first triangle `(0,0)`.
- Float32 `.173` storage test, separately from interpolation. The handoff’s `.1729736328125` value assumes RTZ half conversion; establish actual backend conversion instead of treating it as universal GLES.
- Affine fields and exactly representable half nodes.
- Assert original node indexing/final V inversion.
- Compare both GL-line and Native quad endpoint producers; preserve minimum-length/style policy as separate I15 work.
- Validate prior-frame lifecycle and prepared replay once.

**Pixel captures.** Draw a deliberately visible vector grid over the injected nonlinear field; capture endpoints before any subsequent warp, plus final image. For storage, choose endpoints away from minimum-length/filter boundaries and magnify the displacement crop. Capture exact Pithlit/fiShbRaiN presets under frozen Native4K protocols; do not brighten their authored vector alpha to manufacture original evidence.

**Costs.**

- CPU route: N additional node UV computations, including up to4 trig evaluations/node plus nested powers; up to3,072 bilinear endpoint calculations at maximum motion grid. RG32F nodes need8N bytes; two retained generations16N.
- At48×32, N=1,617: one node map12,936B; two25,872B.
- GPU transform-feedback route: one additional N-vertex pass when refreshing,8N buffer bytes plus8N texture bytes for a simple implementation; four node fetches per endpoint invocation. Native quad shader repeats endpoint calculation for four vertices/vector.
- Continuous full4K RG16F→RG32F replacement adds31.64MiB persistent memory and31.64MiB logical write payload/frame; at1280×720, adds3.52MiB. It does not resolve triangle/raster sampling and is therefore a poor isolated fix.
- No timing claim is supportable.

## I16 — Stale map on motion re-enable

**Source proof.**

Current code explicitly documents the optimization and one-frame stale result: [MilkdropPreset.cpp:228](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/third_party/projectm/src/libprojectM/MilkdropPreset/MilkdropPreset.cpp:228). The map is written only while alpha/counts enable vectors; both native and authored-canvas paths follow that condition.

Original draws motion vectors using the prior mesh at [milkdropfs.cpp:1048](/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/vis_milk2/milkdropfs.cpp:1048), then recomputes/stores mesh UV every frame at1824–1926. Thus a disabled frame still updates the next motion field.

**Best static original witness.** [101.milk:229](/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/core/src/main/assets/presets/101.milk:229), SHA256 `a901944f8f1d668e38fac317dff5e596b3f4d80e837a6083695bc58b3278154c`.

Legacy, warp0, one nonlinear zoom expression driven by `q1`, and `mv_a` driven by bass. A matched bass sequence crossing1.2 can both disable/re-enable vectors and change the field. This avoids the I10 warp confound. Handoff count: **435 candidates**.

**Re-enable-only update feasibility.**

The previous prepared GPU attribute buffers **are still present** before the first motion draw at175–177; current mesh replacement occurs later at243–244. This permits a bounded design without duplicating mesh attributes:

1. Cache previous warp uniform values per `PerPixelMesh` instance after its prepared draw: time/factors/scale/aspect/texel offsets, effective UV size and ownership/generation.
2. Track whether the existing UV map corresponds to the immediately preceding completed prepared frame.
3. After current per-frame alpha/count evaluation, detect enabled vectors with stale valid prior map.
4. Before either native or authored-canvas vector draw, regenerate UV from the **previous prepared attributes and previous uniforms** into a UV-only target.
5. Continue current frame normally; do not execute equations again.

**Why existing `DrawAgain()` is insufficient.** It calls `WarpedBlit()`, which recomputes current time/uniforms, samples current main texture, uses custom fragment shaders, invalidates both attachments and can discard pixels. Shared shader uniforms also cannot safely retain prior instance state through transitions and canvas/native replay. A dedicated UV-only shader/FBO operation is required.

The extra path must preserve/restores viewport, draw buffers, FBO, program, sampler, blend and attachment state. Cache invalidation must cover resize, context recreation, mesh change, authored/native policy changes, shader fallback, first-frame state and both preset instances. The authored pass must use its retained prior canvas values, not the current native viewport.

**Unresolved:** custom fragment `clip()` can suppress current UV writes. A UV-only replay does not reproduce that discard policy. A safe first implementation can repair the proven legacy path and explicitly defer custom clipping/fallback semantics. I14 remains separate even after temporal freshness is corrected.

**Alternative.** Write UV every frame. This is simpler but reinstates the bandwidth optimization’s removed work on all disabled frames. It needs clean matched Native4K timing before acceptance.

**Focused regression.**

- Establish valid A=(.5,.5); one disabled frame produces B=(.6,.5); re-enable must consume B, not A.
- Multiple disabled frames; changing time, Q/warp, rotation and negative zoom.
- Alpha threshold transitions and count-based off/on, including counts0.
- All-enabled/all-disabled/A=B controls.
- Verify no extra per-pixel execution, Q increment or RNG draw.
- Resize/context/detail transitions must keep existing first-frame guard instead of fabricating valid prior UV.
- Two preset instances with distinct times/uniforms catch shared-cache leakage.

**Pixel captures.** On known feedback, capture UV map and vector overlay on the first re-enabled frame, then its successor. Before must visibly use A; source-derived temporal expectation uses B. Capture `101.milk` with a frozen PCM bass sequence establishing an actual on/off/on journey and record the evaluated alpha/Q/field for each selected frame.

**Costs.**

- Continuous-write alternative: no new allocation or pass; added RG16F write on every disabled frame: `4*Wuv*Huv` bytes. Full4K31.64MiB/frame;1280×720 authored3.52MiB/frame.
- Re-enable-only replay: one extra UV raster pass only on stale re-enable, same payload, existing map allocation; no color sample/write in a proper dedicated shader. At48×32:3,072 triangles/9,216 indexed references, with1,617 unique prepared vertices.
- No duplicate mesh required if replay precedes replacement. Cached uniforms/generation metadata are O(1), roughly tens of floats plus flags.
- The re-enable frame also performs its ordinary current-frame UV write; continuous disabled frames retain the existing saving.
- Native4K Standard’s UV size must be observed: source currently writes the authored-canvas map when detail is active. Do not budget every Standard4K frame as a3840×2160 UV map.

## Shared acceptance requirements

For each accepted repair, parent validation should produce **actual before/candidate/expected images** with separate producer identities. “Expected” generated from original arithmetic on GLES is source-derived evidence, not original Windows raster proof.

Use exact handoff canvases first, then Native Standard4K acceptance. Freeze source/patch/artifact/preset/PCM hashes, mesh, clock/FPS/progress, RNG lifecycle and completed-frame numbers. Record effective authored canvas, UV-map size/filter/storage, physical output, viewport, trails and context generation separately.

For I10–I13, retain a custom-warp unchanged control. For all warp changes, rerun rotation0011 and negative-power0015 regressions and prepared-replay evaluation-count checks. I14 and I16 are independent: fresh maps can still have the wrong interpolation/storage policy, and correct interpolation can still be temporally stale.
