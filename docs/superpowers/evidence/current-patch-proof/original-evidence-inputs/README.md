# Original evidence inputs for the current components

This closes the gap between the23-row current-component matrix and the original
PR experiments. The PR bodies/comments and linked committed records supply
preset classes, exact assets where available, activation settings and controls.
Those historical runs keep their original source/driver identities; this map
selects inputs for fresh upstream/current4.2 captures rather than reusing their
screenshots or performance figures as current proof.

Research read25 PR bodies and their comments, the named regression inventory,
linked shader/sampler/trails/history records, and seven early optimization commit
messages. The commit-to-PR API returned no associated PR for those seven original
commits; their commit records provide the available primary provenance. Exact
benchmark preset names are absent from several early messages. That absence does
not make them new bugs or justify inventing original witness names.

The [machine map](map.json) retains source links, PR body/comment receipts,
current component names, original profiles and SHA256 of verified named assets.
Its profiles are historical input contracts, not a claim that the present harness
already exposes every setting or that every listed original still fails in4.2.

| Current component | Original evidence/input type | Profile to recover before replay |
|---|---|---|
| High-resolution lines/AA | [PR #14](https://github.com/johnneerdael/ProjectM-TV/pull/14): Royal Mashup103/191; Serge circles005b; synthetic thin/thick/dot controls | 854x480/1920x1080/3840x2160; original final reference1024x768; bass-0.30; 4s warm-up +4s measure,30fps; AAoff |
| Reference sample/fade/blur/canvas policy | [PR #14](https://github.com/johnneerdael/ProjectM-TV/pull/14#issuecomment-5971576653): Royal103 sample count; Nuclear/fat cancer blur; Fvese-mvfun2 MaximizeColors; sawtooth grin/penattrition virtual texsize | 1024x768 reference; authored16:9 area1182x665 versus1080/4K; separate ablations, fDecay0 canvas-hit diagnostics |
| Fragment-failure shader cleanup | [PR #23](https://github.com/johnneerdael/ProjectM-TV/pull/23): Intentional valid-vertex/invalid-fragment failures;16 attempts and valid retry | Driver shader-object lifetime queries; healthy render preservation |
| Fresh/reused feedback history | [PR #23](https://github.com/johnneerdael/ProjectM-TV/pull/23): Valid controlled-allocation bytes; fresh clear; cached FBO-name collision after context recreation | Nondefault mask/scissor/clear color; caller FBO; fresh and pooled attachment reads |
| Qualified warp sampler reservation | [PR #23](https://github.com/johnneerdael/ProjectM-TV/pull/23): Fractional/out-of-bounds samples; ADAMFX2, Matrix Moral Infinite, Mood Rings original suite | Point/linear and clamp/wrap aliases;33 originals at authored665/reference-scaled1330/2160 |
| Ordered shape batching | [commit e563f860](https://github.com/johnneerdael/ProjectM-TV/commit/e563f8603e2e8824c339d1296bffceeebc119c71): 46 shape presets; shape-heavy instances; exact identities not listed in commit | 184 deterministic Mesa frames; fills/outlines and blending in instance order; upload once per batch |
| Evaluate-once geometry replay | [PR #40](https://github.com/johnneerdael/ProjectM-TV/pull/40): Waltra particles; Hexcollie spiral; faint recurrence and stateful equations/RNG | 3840x2160;480frames;frame300; seed12345/frame30; authored/native-off/Standard repeats plusMedium/High; resize/re-enable |
| Texture pooling | [commit 651a9fea](https://github.com/johnneerdael/ProjectM-TV/commit/651a9fea01b03a978b395660dbb9227b563599bc): 40-preset Mesa single/multi-instance with/without pool; names not listed in commit | Same-size retirement/reload; host pool limit; pressure release; mip-level accounting added in PR14 |
| Translated GLSL cache | [commit 0195cb16](https://github.com/johnneerdael/ProjectM-TV/commit/0195cb16f443b2b702fa4d1eaab8695039f192b4): Custom warp/composite shaders prepared in foreground/prewarm engine instances | Identical shader type/source/sampler/texsize declarations; bounded cross-instance cache |
| Program-binary cache | [commit 45dcbb9b](https://github.com/johnneerdael/ProjectM-TV/commit/45dcbb9b84600af7d8483c6ac21805baa1f71399): Foreground load and shared-context prewarm linked warp/composite programs | Cold/warm linked programs; cache source/driver/context keys; resize/history preservation |
| Uniform-location/program-bind caches | [commit 45dcbb9b](https://github.com/johnneerdael/ProjectM-TV/commit/45dcbb9b84600af7d8483c6ac21805baa1f71399): Custom shapes repeatedly binding same program per instance | Repeated same-frame shape uniforms/program binds; foreground/prewarm instances |
| Flip reuse | [commit 54e9f14d](https://github.com/johnneerdael/ProjectM-TV/commit/54e9f14dc91d9a1d4b5dda30a2f079a3eb526c62): Five preset kinds; cached y-flipped previous frame | No-motion-vector phase versus vector drawing and resize invalidation |
| Direct blur attachment rendering | [PR #34](https://github.com/johnneerdael/ProjectM-TV/pull/34): midgit warp blur; isolated known TGA; separate read/draw FBOs | First allocation, unchanged size, resize/scaled blur; four full-preset frames includingresize; constant-color control |
| Visibility-gated vector UV output | [commit 54e9f14d](https://github.com/johnneerdael/ProjectM-TV/commit/54e9f14dc91d9a1d4b5dda30a2f079a3eb526c62): Motion vectors hidden/shown; Royal103 from PR28 | Runtime visibility phases; invalidate UV history when vector rendering changes |
| Final-orientation video echo | [commit 54e9f14d](https://github.com/johnneerdael/ProjectM-TV/commit/54e9f14dc91d9a1d4b5dda30a2f079a3eb526c62): Legacy video echo preset class in five-kind comparison; exact filename not listed | Nonzero echo alpha; all orientation values; final y-orientation without third flip |
| Discard and authored blur timing | [commit 54e9f14d](https://github.com/johnneerdael/ProjectM-TV/commit/54e9f14dc91d9a1d4b5dda30a2f079a3eb526c62): Warp shaders reading blur; composites using clip() | Preserve target contents; avoid invalidation/merged pass when read/discard needs prior frame |
| Direct composite/switch history | [commit 2ac06c72](https://github.com/johnneerdael/ProjectM-TV/commit/2ac06c7253fb2956df3645779bf688c07d617419): Custom and legacy composites; classic transitions; host preset switches; clip() exclusion | Caller direct FBO vs stored history; store a frame before remote/blank-skip switch; transitions remainstored |
| Array initializer layout | [PR #26](https://github.com/johnneerdael/ProjectM-TV/pull/26): PR26 original Glass Ocean flat arrays; current Quicksand is a later, clearer witness of the same retained initializer class; local diagnostic | Global flat float4[5] initialized from20scalars; local typed elements; whole-array initialization |
| Writable uniform initialization | [PR #26](https://github.com/johnneerdael/ProjectM-TV/pull/26): Royal324 black-on-Mali; q18/q19 bank; compoundtime/helper; ++/--/out/inout | Incoming initialized bank copy shared acrossfunctions; partial write preserves othercomponents |
| Contextual identifiers/macros/postfix | [PR #29](https://github.com/johnneerdael/ProjectM-TV/pull/29): 16 hash-pinned originals including Rainbox Splash Poolz/Hedgehog/Flexi; local sample identifier | Direct authored shader compilation plus12numerical rendercontrols; parser/macro/postfix distinct |
| Float emission and implicit globals | [PR #33](https://github.com/johnneerdael/ProjectM-TV/pull/33): crystal palace tunnel003/wreck diver/organic light; mus/dist_c/uv3; ludicrous selector; PR41 literal fixtures | Explicit silence128x72/30fps/60frames; implicit-zero vs explicit-zero/nonzero controls;95literal sections/99ASTwitnesses |
| Evaluator lone-dot numbers | [PR #27](https://github.com/johnneerdael/ProjectM-TV/pull/27): PR27 code-phase/lone-dot fixtures and unchanged161/430; the current Stahlregen funky Blur original witness was added later | Preset/wave/shape equation phases; lone dot must compile aszero; tolerant omission distinguished |
| Evaluator thread-local RNG | [commit 3295518a](https://github.com/johnneerdael/ProjectM-TV/commit/3295518a6f8f9fd769403850d37239ccd58b6f32): Prewarm and foreground evaluator contexts/threads; no exact original named preset recovered here | Independent fresh-thread RNG streams; concurrent evaluation and rendered state |

## Concrete changes to the remaining capture sequence

1. Recover the original reference dimensions and input window, not just the
   preset filename. PR14's final1024×768 reference differs from the earlier
   1920×1080 thick-wave control. Current Geiss4K proof is a valid separate API
   control; it does not replace Royal103's sample-count experiment.
2. Use midgit with first-use/resize and distinct caller targets for blur, then
   Waltra/Hexcollie with explicit authored/native-off/Standard/Medium/High profiles
   for geometry replay. The current image harness needs those host settings and
   event sequences before an otherwise healthy still can prove these components.
3. Reuse the original shader parser/initializer and sampler fixtures. Retain
   undefined-input, shader fallback, ambiguity and non-activation results instead
   of replacing them with selected attractive frames.
4. For batching/pool/cache/pass work, pair actual rendered preservation images
   with measured operations/resources. The original commits describe image parity
   and performance experiments, not an appearance defect in every preset.

Short names such as fat cancer tour, Fvese-mvfun2 and Serge circles005b still need
the exact linked historical JSON/catalog join; do not choose a similarly named
variant silently. The older Tantalum report has an ellipsis and two verified
candidate assets, already recorded as ambiguity controls in the regression inventory.
