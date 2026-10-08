# MilkDrop audit repairs — active ledger

The playback target is Native4K Android TV, preserving prior TV fixes. All33 supplied findings remain in scope. Historical evidence baseline120547f3 contains15 TV patches; current integration retains main af164a97 and its released0016 cache patch; the source repair series now adds0017–0027 for twelve finding IDs. I19 and the shared I02/M01 boolean repair are separate deferred proposals, and I22 retains a performance-disposition question. Eighteen other findings still require executable proof, screenshots and a repair or completed owner followup package. The goal is not complete.

All33 handoff hashes and all9,606 bundled preset hashes were verified. Lexical candidate counts below are unconfirmed impact counts. Both MilkDrop2 renderer files are byte-identical; MilkDrop3 remains a separately identified reference.

| ID | Finding | Lexical candidates | Current status |
|---|---|---:|---|
| I17 | Built-in opacity replacement and thresholds differ | 5300 | Implemented0017; source/final4K original proof; integration pending |
| I19 | Line-mode raw sample counts differ at matched canvases | 3643 | Deferred source-cap proposal; final authored/Native comparison and +.158ms cost documented |
| I08 | Custom oscilloscope windows are not centered or channel-separated | 508 | Implemented0018; source/final4K original proof; integration pending |
| I22 | Custom dot waves gain interpolated points | 1875 | Candidate0019; source/original/finite final4K proof; timing disposition pending |
| I10 | Legacy warp deformation sees the opposite physical Y argument | 1737 | Implemented0024; original/finite/custom and cost4K proof; integration pending |
| I11 | Legacy warp physical triangle diagonal is reversed | 878 | Implemented0025; source49/sanitizer49, exact cache pixels, revised cost qualified; integration pending |
| I12 | Stateful per-pixel equations traverse opposite physical rows | 10 | Implemented0026; source50, original/finite/custom final4K repeats, isolated cost qualified; integration pending |
| I14 | Motion reverse propagation uses different interpolation and storage | 794 | Source investigation recorded; execution/captures/disposition pending |
| I05 | Per-pixel aspect inputs use factors instead of inverse factors | 248 | Implemented0022; source/original/finite final4K proof; integration pending |
| I16 | Disabling motion vectors leaves a stale target UV map | 435 | Source investigation recorded; execution/captures/disposition pending |
| I06 | Custom-wave points inherit modified main-frame read-only inputs | 1 | Implemented0022; source/original/finite final4K proof; integration pending |
| I24 | Shape live thick equations do not select target outline style | 14 | Source/cost screening; two stronger originals; execution/captures pending |
| I23 | Thick custom-wave and shape-outline offsets differ | 4951 | Source investigation recorded; execution/captures/disposition pending |
| I20 | Circle angular spacing and closure smoothing differ | 2736 | Candidate0027; actual geometry/GL/replay proof; Native4K/cost pending |
| I13 | Left-axis equation angle seam changes sign | 204 | Source investigation recorded; execution/captures/disposition pending |
| I18 | Wave brightening omits original preliminary clamp | 0 | Source investigation recorded; execution/captures/disposition pending |
| I03 | Small finite divisions and reciprocal powers collapse to zero | 0 | Source investigation recorded; execution/captures/disposition pending |
| I04 | Signed remainder differs from original absolute-value remainder | 0 | Source investigation recorded; execution/captures/disposition pending |
| M02 | Inverted-radius border topology differs from target library | 0 | Source investigation recorded; execution/captures/disposition pending |
| M01 | Negative custom-wave enable executes in predictor but not library | 0 | Deferred shared proposal; source/Native4K proof; +.102ms/+7.503% negative-wave cost |
| I25 | Shape/custom-wave colour fractions survive original byte truncation | 5347 | Source investigation recorded; execution/captures/disposition pending |
| I30 | Display diffuse colours retain floats instead of original byte packing | 155 | Source investigation recorded; execution/captures/disposition pending |
| I29 | Negative odd echo orientation omits original horizontal flip | 0 | Implemented0023; source/finite final4K proof; no confirmed stock trigger |
| I15 | Minimum motion trails are larger and aspect-dependent | 794 | Source investigation recorded; execution/captures/disposition pending |
| I09 | EEL named constants round to float before double evaluation | 0 | Implemented0021; source/finite final4K proof; no confirmed stock trigger |
| I31 | Gamma-only pass-count epsilon differs | 68 | Implemented0020; source/final4K original proof; integration pending |
| I01 | Preset keys are case-insensitive in library/predictor | 2 | Source investigation recorded; execution/captures/disposition pending |
| I02 | Negative boolean settings use >0 rather than nonzero | 0 | Deferred shared proposal; actual sampler/Native4K proof; workload decision documented |
| I07 | Stereo bands average channels rather than left only | 8985 | Source investigation recorded; execution/captures/disposition pending |
| I21 | Extra waveform modes change original modulo aliases | 4 | Source investigation recorded; execution/captures/disposition pending |
| I26 | Shader vol/vol_att differ from original comma expression | 97 | Source investigation recorded; execution/captures/disposition pending |
| I27 | mip_y uses height rather than original repeated width | 0 | Source investigation recorded; execution/captures/disposition pending |
| I28 | Near-equal blur bounds expand instead of collapsing | 8 | Source investigation recorded; execution/captures/disposition pending |

## Current validation

The current shipping-series normal renderer suite passes51/51 after removing the four deferred boolean controls. Their historical53/54/55 source results remain in the proposal evidence. The capture/helper suite passes60 tests and24 subtests. Final-output replay completed32 unchanged-original runs,28 finite diagnostic runs (including four echo runs), and24 additional I19 resolution-band runs, each480 frames. Every role's eight selected RGB captures repeats exactly; this is not an all-frame hash or whole-corpus certification. Source-instrumented engine AARs and private capture APKs are identified separately from shipping binaries. Physical-TV performance remains unmeasured.

Native direct rendering can leave an internal read FBO bound after restoring draw framebuffer0. Historical audit PNGs therefore show intermediate feedback; fresh workers explicitly read framebuffer0 and restore the previous read binding. Preserve original artifacts/helpers and use the new final-output records for appearance claims. The guard test rejects missing/nonzero read-target evidence even with valid PNG/RGB hashes. See [capture correction](capture-correction/README.md).

Source reports under `research/` refine remaining repair boundaries and candidate lists. They are not execution, screenshot or completion evidence. Final combined sanitizer/Android/host/JVM/docs/review/CI/integration gates remain separate from these focused results. See [per-ID identities and state](ledger.json).

Live patch numbering was shifted once to preserve released main0016. Frozen evidence/helpers retain their historical names, source hashes and rendered bytes. Latest-main focused validation remains pending.

Draft [PR61](https://github.com/johnneerdael/ProjectM-TV/pull/61) is open. Main synchronization preserves the released0016 efficiency patch; [original/custom Native4K probes](main-synchronization/results.json) are selected-RGB identical before/after. I12 has original/finite/custom Native proof and isolated12-run cost qualification. I02/M01 now has source/sampler/Native proof and a complete cost-bearing owner decision report; its proposal is outside shipping patches.

The full33 goal remains active. Source-only I18/I24 and compiler-sensitive I03/I04 proposals are isolated, outside the patch series. Android fast-math removes raw arithmetic finite guards; integration requires a verified compiler/implementation disposition.

Current integrated shipping-series ASan/UBSan renderer controls pass51/51, matching normal51/51. ARM64 source-instrumented circle artifact5d721fba builds; original Native4K capture and cost qualification remain active.
