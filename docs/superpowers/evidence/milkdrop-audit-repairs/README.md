# MilkDrop audit repairs — active ledger

Native4K Android TV remains the target, preserving prior TV fixes. All33 supplied findings remain in scope:29 are classified, with13 repaired IDs in12 new patches0017–0028,10 retained policies and6 complete deferred packets. Four remain open: I04,I14,I16,I24. Final combined integration/review/CI gates remain open; PR61 is a draft.

All33 handoff hashes and all9,606 bundled preset hashes were verified. Lexical candidate counts below are unconfirmed impact counts. Both MilkDrop2 renderer files are byte-identical; MilkDrop3 remains a separately identified reference.

| ID | Finding | Lexical candidates | Current status |
|---|---|---:|---|
| I17 | Built-in opacity replacement and thresholds differ | 5300 | [implemented source repair; focused source/final-output original Native4K acceptance passed; final integration pending](I17/README.md) |
| I19 | Line-mode raw sample counts differ at matched canvases | 3643 | [deferred for owner: source-correct cap preserves authored/Native fidelity but clean4K mean cost +0.158ms /2.56%](I19/README.md) |
| I08 | Custom oscilloscope windows are not centered or channel-separated | 508 | [implemented source repair; focused source/final-output original Native4K acceptance passed; final integration pending](I08/README.md) |
| I22 | Custom dot waves gain interpolated points | 1875 | [deferred complete custom-dot proposal; source/original/finite final4K proof; fresh12ABBA mosaic+.105ms/+5.038%, all cycles increase; owner packet complete](I22/README.md) |
| I10 | Legacy warp deformation sees the opposite physical Y argument | 1737 | [implemented0023; focused source/original/finite/custom unchanged4K and12-run cost acceptance passed; final integration pending](I10/README.md) |
| I11 | Legacy warp physical triangle diagonal is reversed | 878 | [implemented revised0024;49 normal/49 sanitizer, exact original/finite/custom Native4K cache equivalence and12-run cost acceptance passed; final integration pending](I11/README.md) |
| I12 | Stateful per-pixel equations traverse opposite physical rows | 10 | [implemented0025; production state-order and original/finite/custom final4K repeated proof; isolated12-run cost no consistent slowdown; final integration pending](I12/README.md) |
| I14 | Motion reverse propagation uses different interpolation and storage | 794 | [three-layer causal finite/source feasibility packet; actual1280x720 UV canvas cost distinguished; production GL/Native/cost/disposition pending](I14/README.md) |
| I05 | Per-pixel aspect inputs use factors instead of inverse factors | 248 | [implemented source repair; focused source/final-output original Native4K acceptance passed; final integration pending](I05/README.md) |
| I16 | Disabling motion vectors leaves a stale target UV map | 435 | [source ordering confirms stale previous texture on re-enable; retained previous-state/UV-only-pass proposal; discard/ownership/Native/cost/disposition pending](I16/DESIGN.md) |
| I06 | Custom-wave points inherit modified main-frame read-only inputs | 1 | [implemented source repair; focused source/final-output original Native4K acceptance passed; final integration pending](I06/README.md) |
| I24 | Shape live thick equations do not select target outline style | 14 | [source/per-instance cost investigation recorded; two strong original candidates; execution/final screenshots and disposition pending](I24/README.md) |
| I23 | Thick custom-wave and shape-outline offsets differ | 4951 | [retained Native thick-offset policy; complete owner packet with actual vertex/replay controls and matched Native4K style images](I15-I23/I23-OWNER-DECISION.md) |
| I20 | Circle angular spacing and closure smoothing differ | 2736 | [deferred circle proposal; source/GL/sanitizer and two originals/all finite styles Native4K proof; isolated12-run mean+.058ms/+3.393%, mixed cycles; complete owner decision packet](I20/README.md) |
| I13 | Left-axis equation angle seam changes sign | 204 | [implemented0026; actual CGL/normal51/sanitizer51 and original/finite/custom Native4K repeated proof; isolated12-run cost no consistent slowdown; final integration pending](I13/README.md) |
| I18 | Wave brightening omits original preliminary clamp | 0 | [implemented0027 RGB-only;52normal/52sanitizer, qualified original/finite Native4K palette/nonzero proof; isolated12-run cost no consistent slowdown; integration pending](I18/README.md) |
| I03 | Small finite divisions and reciprocal powers collapse to zero | 0 | [deferred complete owner packet; combined finite recovery passes source/ARM/Native proof but runtime tiny-power cost +7.50%](I03-I04/I03-OWNER-DECISION.md) |
| I04 | Signed remainder differs from original absolute-value remainder | 0 | [isolated bits-v2: unchanged flags;76 remainder+12 preservation host/ARM controls and20 baseline boundaries pass; guard IR reviewed; Native sign captured; cost pending](I04-bits-v2/ROOT-QUALIFICATION.md) |
| M02 | Inverted-radius border topology differs from target library | 0 | [implemented0028; 46 fan profiles,51 normal/51 sanitizer,24 Native4K repeat runs and12 isolated cost qualification; final integration pending](M02/README.md) |
| M01 | Negative custom-wave enable executes in predictor but not library | 0 | [deferred shared nonzero-boolean proposal; source/actual sampler/Native4K repeated proof complete; clean12-run negative-wave cost+.102ms/+7.503%; owner decision documented](I02-M01/README.md) |
| I25 | Shape/custom-wave colour fractions survive original byte truncation | 5347 | [retained float precision; complete owner decision with actual production controls and repeated Native4K images](I25-I30/OWNER-DECISION.md) |
| I30 | Display diffuse colours retain floats instead of original byte packing | 155 | [retained float precision; complete owner decision with actual production controls and repeated Native4K images](I25-I30/OWNER-DECISION.md) |
| I29 | Negative odd echo orientation omits original horizontal flip | 0 | [implemented0022; focused source/finite final-output Native4K acceptance passed; final integration pending](I29/README.md) |
| I15 | Minimum motion trails are larger and aspect-dependent | 794 | [retained aspect-aware visibility minimum; complete owner packet with actual endpoint controls and unchanged-original Native4K width-threshold reference](I15-I23/I15-OWNER-DECISION.md) |
| I09 | EEL named constants round to float before double evaluation | 0 | [implemented0020; focused source/finite final-output Native4K acceptance passed; no confirmed stock trigger; final integration pending](I09/README.md) |
| I31 | Gamma-only pass-count epsilon differs | 68 | [implemented source repair; focused source/final-output original Native4K acceptance passed; final integration pending](I31/README.md) |
| I01 | Preset keys are case-insensitive in library/predictor | 2 | [retained tolerant loading; completed owner policy packet with production parser controls and repeated Native4K/matched-resolution images](I01/README.md) |
| I02 | Negative boolean settings use >0 rather than nonzero | 0 | [deferred shared nonzero-boolean proposal; source/actual sampler/Native4K repeated proof complete; clean12-run negative-wave cost+.102ms/+7.503%; owner decision documented](I02-M01/README.md) |
| I07 | Stereo bands average channels rather than left only | 8985 | [retained upstream stereo averaging; complete owner packet with actual PCM controls and Native4K source-stage/preservation images](I07/README.md) |
| I21 | Extra waveform modes change original modulo aliases | 4 | [retained 16-mode extension; complete owner packet with production GL, matched ARM64 input and repeated Native4K images](I21/README.md) |
| I26 | Shader vol/vol_att differ from original comma expression | 97 | [retained upstream corrected shader input; complete owner packet with actual compile/uniform controls and repeated Native4K images](I26-I27/OWNER-DECISION.md) |
| I27 | mip_y uses height rather than original repeated width | 0 | [retained upstream corrected shader input; complete owner packet with actual compile/uniform controls and repeated Native4K images](I26-I27/OWNER-DECISION.md) |
| I28 | Near-equal blur bounds expand instead of collapsing | 8 | [retained TV blur safety correction; complete owner packet with production numeric/storage/decode tests and repeated Native4K images](I28/README.md) |

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

I15 retainedvisibilityminimum qualified: actualendpoint/diffusion/ownershipcomponentcontrols plus4unchangedRovastarNative current/width-onlyoracle runs exactrepeats. Previousshared44Nativefinite/stock runs remainseparate. Twelve repairedIDs,ten retainedpolicyIDs,six deferredIDs andfive unfinishedIDs remain.

Latest M02 check:51 normal and51 ASan/UBSan controls pass; all28 patches apply. [Border repair evidence](M02/README.md) includes repeated Native4K images and isolated cost. Earlier numbered checkpoints below retain historical source identities.
