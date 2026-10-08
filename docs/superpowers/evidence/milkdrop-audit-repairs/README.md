# MilkDrop audit repairs — active ledger

The playback target is Native4K Android TV, preserving prior TV fixes. All33 supplied findings remain in scope. Historical evidence baseline120547f3 contains15 TV patches; current integration retains main af164a97 and its released0016 cache patch; the source repair series now adds0017–0027 for twelve finding IDs. I19, I20, I22 and the shared I02/M01 boolean repair are separate deferred proposals, and I22 retains a performance-disposition question. Six other findings still require executable proof, screenshots and a repair or completed owner followup package. The goal is not complete.

All33 handoff hashes and all9,606 bundled preset hashes were verified. Lexical candidate counts below are unconfirmed impact counts. Both MilkDrop2 renderer files are byte-identical; MilkDrop3 remains a separately identified reference.

| ID | Finding | Lexical candidates | Current status |
|---|---|---:|---|
| I17 | Built-in opacity replacement and thresholds differ | 5300 | Implemented0017; source/final4K original proof; integration pending |
| I19 | Line-mode raw sample counts differ at matched canvases | 3643 | Deferred source-cap proposal; final authored/Native comparison and +.158ms cost documented |
| I08 | Custom oscilloscope windows are not centered or channel-separated | 508 | Implemented0018; source/final4K original proof; integration pending |
| I22 | Custom dot waves gain interpolated points | 1875 | Deferred complete proposal; source/finite/original4K proof; controlled mosaic+.105ms/+5.038% |
| I10 | Legacy warp deformation sees the opposite physical Y argument | 1737 | Implemented0023; original/finite/custom and cost4K proof; integration pending |
| I11 | Legacy warp physical triangle diagonal is reversed | 878 | Implemented0024; source49/sanitizer49, exact cache pixels, revised cost qualified; integration pending |
| I12 | Stateful per-pixel equations traverse opposite physical rows | 10 | Implemented0025; source50, original/finite/custom final4K repeats, isolated cost qualified; integration pending |
| I14 | Motion reverse propagation uses different interpolation and storage | 794 | Source investigation recorded; execution/captures/disposition pending |
| I05 | Per-pixel aspect inputs use factors instead of inverse factors | 248 | Implemented0021; source/original/finite final4K proof; integration pending |
| I16 | Disabling motion vectors leaves a stale target UV map | 435 | Source investigation recorded; execution/captures/disposition pending |
| I06 | Custom-wave points inherit modified main-frame read-only inputs | 1 | Implemented0021; source/original/finite final4K proof; integration pending |
| I24 | Shape live thick equations do not select target outline style | 14 | Source/cost screening; two stronger originals; execution/captures pending |
| I23 | Thick custom-wave and shape-outline offsets differ | 4951 | Source investigation recorded; execution/captures/disposition pending |
| I20 | Circle angular spacing and closure smoothing differ | 2736 | Deferred; source/GL/all finite styles/two original4K proof; +.058ms/+3.393% mean cost, mixed cycles |
| I13 | Left-axis equation angle seam changes sign | 204 | Implemented0026; source/GL/sanitizer/original/finite/custom4K/cost proof; integration pending |
| I18 | Wave brightening omits original preliminary clamp | 0 | Implemented0027 RGB-only; actual GL/sanitizer52, original/finite4K and cost proof; integration pending |
| I03 | Small finite divisions and reciprocal powers collapse to zero | 0 | Source investigation recorded; execution/captures/disposition pending |
| I04 | Signed remainder differs from original absolute-value remainder | 0 | Source investigation recorded; execution/captures/disposition pending |
| M02 | Inverted-radius border topology differs from target library | 0 | Source investigation recorded; execution/captures/disposition pending |
| M01 | Negative custom-wave enable executes in predictor but not library | 0 | Deferred shared proposal; source/Native4K proof; +.102ms/+7.503% negative-wave cost |
| I25 | Shape/custom-wave colour fractions survive original byte truncation | 5347 | Source investigation recorded; execution/captures/disposition pending |
| I30 | Display diffuse colours retain floats instead of original byte packing | 155 | Source investigation recorded; execution/captures/disposition pending |
| I29 | Negative odd echo orientation omits original horizontal flip | 0 | Implemented0022; source/finite final4K proof; no confirmed stock trigger |
| I15 | Minimum motion trails are larger and aspect-dependent | 794 | Source investigation recorded; execution/captures/disposition pending |
| I09 | EEL named constants round to float before double evaluation | 0 | Implemented0020; source/finite final4K proof; no confirmed stock trigger |
| I31 | Gamma-only pass-count epsilon differs | 68 | Implemented0019; source/final4K original proof; integration pending |
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

Latest disposition: circle I20 is withdrawn after the positive overall timing delta; its complete owner packet retains all evidence. Four IDs are now deferred (I19/I20/I02/M01). Current shipping-series50 normal/sanitizer reruns and26-patch application are pending after withdrawal.

Current shipping series after both proposal withdrawals passes50/50 normal,50/50 ASan/UBSan and fresh26-patch application. [Normal](review-checkpoint/current-normal50.txt) · [Sanitizer](review-checkpoint/current-asan50.txt) · [Patch application](review-checkpoint/current-patch26.txt). I13/I14/I16 source-only proposals and precise open Native/cost limits are now durable; they do not count as completed findings.

I13 candidate0027 now passes51 normal renderer controls and27-patch application with actual GL path/attribute/vertex-output proof. Native4K/cost acceptance remains open.

I13 focused acceptance is complete:16 Native4K runs repeat exactly, custom unchanged,12 isolated cost runs show no consistent slowdown. Final integration remains open.

Current52 normal renderer controls/28-patch application pass. I18 RGB-only is source-qualified; its Native/cost acceptance remains open. Negative-darken policy remains a separate unaccepted proposal.

I18 RGB-only is focused-qualified; selected unbrightened captures remain identical on the tested RGBA8 backend, positive brightening/negative dim normalization provide visible proof. No corpus-wide affected count follows.

I22 is now a complete deferred owner packet after fresh controlled mosaic cost+.105ms/+5.038% with all cycles increasing. The dot proposal is outside shipping patches; subsequent live numbering shifts down one while historical evidence stays frozen. Five deferred IDs and16 other unfinished IDs remain; shipping normal50/sanitizer50/27-patch reruns are pending.

After I22 withdrawal, current shipping source passes50 normal/50 ASan/UBSan and27-patch application. Dot-specific controls remain archived with the proposal; window/read-only/replay controls stay in the shipping suite.

I01 retained casing policy is now qualified: production parser controls pass;40 Native/matched256×144 runs repeat selected RGB exactly. The finite border witness distinguishes tolerantZOOM2 from original defaultzoom1; both supplied stock pairs remain selected-RGB identical. No engine patch is added. Twelve IDs are repaired by11 new patches; five IDs have complete deferred packets; I01 has a complete retained-policy packet;15 findings remain unfinished. Current shipping50/50 normal,50/50 sanitizer and27-patch application are passed, as recorded in review-checkpoint/shipping-post-i22-*.txt.

I28 retained blur safety correction is qualified: production numeric/GL normal and sanitizer controls pass;24Native4K runs repeat exactly; equal/near/reversed ranges match explicit-expanded siblings and unsupportedfinite inputs match default siblings. Originalcollapsed storage has no defined finite image oracle. Two retained-policy IDs(I01/I28), five deferredIDs,12repairedIDs and14unfinishedIDs remain.

I07 retained stereo policy is qualified: actualPCM commonmono480frames/576tails hasexactaveraged-leftcombinationinvariance; controlledstereo step/swap/right-only executesanddiffers. SixNative4Kruns/3repeatsqualifyexplicitexecutedstagecoefficientsandunchangedSjadohmono preservation. Three retained-policyIDs(I01/I07/I28), five deferredIDs,12repairedIDs and13unfinishedIDs remain.

I21 retained16-modepolicy is qualified with actualGLselection/replay, matchedARM64sourceproducer576tail/.75smoothing and38Native4K runs(includingblue marker). FourretainedpolicyIDs,5deferredIDs,12repairedIDs and12unfinishedIDs remain. No newenginepatch.

I25/I30 retainedfloatpolicy owner decisions are qualified: realgeometry/displayattributes/pass/replay andvalidcompleted-grid sourcebyte replay pass;48Native4Kruns repeat. Sixgeometrypairs differ;gamma pairs identical;echo uniform-white current255vslabelledfinal-gain254. Androidbyte-grid/dynamic-double followup boundaries explicit. SixretainedpolicyIDs,5deferredIDs,12repairedIDs and10unfinishedIDs remain. No newenginepatch.

I26/I27 correctedinputpolicies qualified:actualcompileduniform/source/PCM/injection tests pass;34Native4K jobs repeat. MutableEELvol cannotoverwrite shaderaudio, miplive matches1280x720reference, Cope sourcecomma-scalar sibling visiblydiffers(maxMAE30.550332). EightretainedpolicyIDs,5deferredIDs,12repairedIDs and8unfinishedIDs remain.

I23 retainedoffsetpolicy qualified: actualshaderpositions/pass/replay andNative live=current-offset siblings all8framesexact;originalreference offsets differ. I15 remainsseparate/open. Nine retainedpolicyIDs,5deferredIDs,12repairedIDs and7unfinishedIDs remain.

I03 now has a complete deferred owner packet:198combined source/ARM controls,12Nativefinitejobs and36verifiedruntimeQcostjobs. Tiny-power+7.50%/allcyclesincrease failscostgate; compiler-scope effects explicit. I04remainsindependent/open. Twelve repairedIDs,nine retainedpolicyIDs,six deferredIDs andsix unfinishedIDs remain.
