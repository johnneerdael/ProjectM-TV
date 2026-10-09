# I28 retained blur-bound policy: source-only owner packet

## Provenance correction / retain decision

Original MilkDrop2 GetSafeBlurMinMax at1551–1581 has avg-minus for both min andmax; zero/near/reversed intervals collapse.1660 onward divides by resulting gaps. Pre0005 projectM has the SAME typo, shown by ordered0005 diff. Expansion is a TV safety correction, NOT a backport of already-safe upstream behavior; the patch also identifies the same MilkDrop3 typo. Retain0005-blur-range-interval.patch and existing0001 direct blur-target/dimension/performance policies. No canonical patch/change proposed here.

Current GetSafeBlurMinMaxValues and actual Update share GetBlurScaleAndBias. Shader LoadVariables uses the same safe adjusted bounds for `_c5/_c6` decode uniforms; GetBlurN samples stored normalized blur and multiplies adjustedgap+adjustedmin. Finite storage and matching decode form one policy. Fixing only one caller or restoring a zero-gap renderer would break coherence.

## Numerical contract / guards

Narrow each equation DOUBLE tofloat32 only after rejecting NaN,±Inf orabs>FLT_MAX; any one invalid value falls back ALL three levels to[0,1]. Adjust level1 then clamp child maximum/minimum to parent then expand child if floatgap<.1 around floataverage. Preserve this order:expansion can extend beyond parent; do not silently impose strict containment or unit clamping. Reversed finite bounds also trigger centered expansion, not sorted endpoints. Ordinary[0,1],valid nested and representable huge ranges retain their arithmetic.

Before division require finitepositive eachfloatgap. Progressive tempMin/tempMax are computed using previous bounds; then theirdifference must be finitepositive;reciprocal andbias must be finite,positive scale. Equal hugefloat inputs may make.1 unrepresentable;finite opposite extrema can overflowgap;positive child gaps can disappear after normalization to hugeparent range. Reject entiretriplet coherently, not per-level epsilon/abs/zero substitution. Existing blur_range_test.cpp explicitly covers equal1,near.4/.45,reversed.8/.2,nested coefficients1/2/2,clamp-then-expand,neighborfloats around.1,representableextremes,FLT_MAX equal/opposite,1e30equal,[-1e30,1e30]withchild.5/.6,1e300 andevery-positionNaN/Inf. These are existing control definitions; no tests run in this packet.

Six scalar cases retain exact Python float32 source-rounding witnesses only. With all min=max.5,original levels collapse to approximately.45,.425,.4125 due progressive childclamps, while retained levels stay[.45,.55]. A singlelevel witness .45/.45 must not be extrapolated to alloriginal levels. No original Windows/GPU NaN orpixel behavior inferred from zero denominator.

## Safe screenshot siblings

Eleven diagnostic presets use SAME current safe renderer. Warp writes finiteRGB(.25+.5*uv.x,.25+.5*uv.y,.5), no externaltextures/random/audio/shapes/waves/echo/borders/motion. Composite GetBlur1 is amplified8*(decoded-low) to show the narrow decoded range. Allow>=2frames with explicit actualclock:blur reads previousfeedback; frame0 uninitialized/black image is not a meaningful rangeproof.

For equalhalf/nearquarter/reversed cases:actual-retained inputbounds .5/.5,.4/.45,.8/.2; explicit-expanded-oracle siblings supply their finite expected adjusted intervals[.45,.55],[.375,.475],[.45,.55]. These should have the same adjusted producer under the SAME backend, allowing equivalent-body captures. The finite-collapsed-decode-oracle sibling multiplies a CURRENT SAFE finite blur sample by0 and adds originallevel1collapsedlow, then amplifies; it shows the zero-gap decoder's constant coefficient result UNDER A DECLARED finite storedtexture assumption. It does NOT run original zero-division pipeline and is NOT original appearance proof; do not label it original-engine screenshot. Shader may optimize zero sample away; qualify it as coefficient-only reference, not blur allocation/transport execution.

Unsupported-finite-fallback fixture assigns live EELdoubleblur1_min/max=1e300, with ordinaryfloat filekeys0/1, then actualGetBlur1. Explicit-default-oracle uses[0,1]. Actualdouble producer must be traced before claiming fallback:putting1e300 into float32 b1n filekey could parser-default and would not establish the domain guard. Compare every storage/decode level normalized coefficients and finalRGB to explicit-default sibling. Nonfinite/reversed failures staydiagnostics, not generated Windows pixel promises.

Expected retainedfinitepalette: equalhalf/reversed R/G transition around source.45..55 with final0..≈.8,blue≈.4 whenfiniteconstant.5 survives convolution; collapsedfinitecoefficient referenceblack afteramplification. Nearquarter thresholdwindow.375..475 similarly shiftsgradient response. Kernel weights,edge darkening,UVsampler/storagequantization and exact rounding must be traced; qualitative gradient/constant distinction is not all-pixel equivalence. Freeze edge_darken actualsetting for siblings; no new edge policy.

Match256x144/mesh48x32,30FPS,knownfrozenunsignedmonoPCM,NativeStandard,no transitions/detail/diffusion; record actualblurlevel/allocation,size/filtering,clock/frame/sourcefieldhash and compiled warp/composite. Native4K is separate. Capture finalREAD framebuffer0 withdraw/readbindings and exactsource/APK/native/preset/asset/PCM hashes. Root screenshots and actualstagecontrols are stillpending; packet does not completeI28.

## Strong exact originals / reject false premises

Stock-candidates.json records exactbytes/lines for eighthandoff originals. Cope - The Cloud:b1equal1,warpGetBlur2+GetPixel; progression makeslevel2affected. Flexi emergencey4a/4b:allbounds1, actualGetBlur1 derivatives plusdirectsample inwarp with1280/1024 scaling. $$$ Royal Mashup29:level1equal1 propagates to actualfinalGetBlur3. Mig015:level2equal0; earlier GetBlur2*0 is not its onlyconsumer, laterGetBlur2 additive term is nonzero. Goody wovenbeads variants:level2equal0,actualGetBlur2 UV displacement; outlinedvariant also warps withit. No main-framebound overrides found in these inspectedsources, but backendcompile/material/scene/clock determines visibleeffect.

EVET Scanazoic collapses onlylevel3 whileactualshaderusesGetBlur1/2. In itsordinaryfinite domain,level3expansion does not change earliercoefficients;unusedlevel3 is not visibleeffect proof. A true unsupported normalization can triggercoherent globalfallback, but thissourcecase does not establishit. Do notturn eightstaticmentions into an affectedcensus.

## Owner gates / preservation

Retain expansionandcoherentfallback. Thispacket requests no new passes,targets,buffers orpolicyselector. Existing blurpasscount followsactualhighestreferencedblurlevel andremainsunchanged; numerical safety CPU cost exists butisnot measuredhere. Parent shouldqualify exactadjustedbounds/storagecoefficients/decodeuniforms,finite knownfieldrawblurimages and finalGetBlurimages; compile actualstock consumers and verify no fallback. Reversed/threshold/nonfinite domains and default equivalent siblings are separatecontrols. Originalcollapsed denominator is excluded fromimageacceptance, not replaced witha fabricated originalvisual. No performance,corpusfidelity orcompletion claim.
