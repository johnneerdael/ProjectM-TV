# Initial native radial zoom component

Uniform positive zoom/zoomexp controls produce a radial initial sampling map,
F=z^(e^(2r-1)), sampling radius r/F. The component is understood even if later
rotation/stretch/translation vary spatially. Its nominal log-factor radial
slope is2*ln(e)*ln(z)*e^(2r-1); radial sampling derivative is(1-r*slope)/F.
The upper bound on r*slope below1 is a sufficient positive-derivative check;
failure is undecided, not proof of a fold. Contents/wrapping/other stages decide
whether radial feedback looks like a tunnel, rings or something else.

Current source34 PerPixelMesh.cpp187 constructs radius as hypot(pos.x*aspectX,
pos.y*aspectY); ProjectM.cpp675–676 normalizes both aspect inputs to at most1.
The nominal broad radius domain is[0,sqrt2], not an assumed corner radius1.
The default and custom vertex shader nested-power order agrees with original
MilkDrop2.25c milkdropfs.cpp1875–1887. The creator's
[authoring guide](https://www.geisswerks.com/milkdrop/milkdrop_preset_authoring.html)
explains zoomexp as curvature; its radius description is historical and does
not override the patched target's current construction.

Positive power endpoint envelopes preserve domains across bases above/below1.
Float32 inner/outer power and reciprocal underflow/overflow endpoints abstain;
negative/unbounded/spatial/state/random zoom inputs stay unknown. Inner-power
underflow with z=1 has a failing regression before its guard, preventing the
finite outer power from hiding an invalid native inner domain. Bounds and
calculus are nominal, with outward endpoint arithmetic; they do not certify
GPU/libm error intervals, radius/power rounding or triangle interpolation.

Fourteen radial controls cover neutral/curved zoom, independent formula points,
finite-difference radial derivatives, sufficient no-fold failures, opposite-log
signs, audio timing unknowns, spatial independence and invalid power domains.
Independent review passed48radial/transport/recipe tests with no actionable
issues. No image, audio/time samples, shader/equation execution or human visual
judgment feeds this addition. Complete-map area, actual folds, visible effect
family and mood remain unresolved work.

The unchanged100source sample all exports with exact source-byte/hash joins
and ZIP CRC.58initial zoom components are bounded, including17with nonneutral
exponents;37unknown and5disconnected.55supported cases meet the sufficient
positive-derivative check,3do not.13cases lack positive finite domains;
24lack uniformity. These describe component coverage, not whole-preset appearance
or tunnel/mood accuracy. Preset-operation times total35.529396seconds, maximum
1.755532seconds on this host; no corpus/hardware guarantee follows.

`census.json` preserves exact names/hashes, domains, ranges and source identity.
Raw paired archive: `build/preset-corpus/source-radial-zoom-2026-10-10/batch-000001.zip`.
SHA256 `869b523fbfab28fff03602f26dac6c6a0bac4fd7ea8ff41c0ecc67bf6911c691`.
Reader SHA256 `754e4f4129db585cb4f7d5bee915d6bb24ac10ab25901ee7ef0832ce50744afc`.
Latest release rechecked as2.3.36commit90b5bf9d; full AAR SHA256
`a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3`.
Matching source34adapter is explicit. Published-runtime qualification remains
separate and pending. No native engine/preset/shared device/full corpus changed.

Final prepared suite: **2,603tests and92subtests pass in146.11seconds**.
Strict MkDocs and whitespace checks pass; these are interpretation-rule
checks, not whole-preset visual or mood accuracy.
