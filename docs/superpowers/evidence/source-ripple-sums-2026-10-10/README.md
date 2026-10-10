# Shared uniform controls across ripple-wave sums

Uniform multipliers/divisors now distribute over supported scalar add/subtract
branches in the periodic lookup model. Signed weights remain symbolic Field
programs. Products of spatial fields are not linearized. Distribution has its
own512-visit/depth64 and64-result-term bounds; failure keeps the model unknown.
Original unsimplified scalar/vector arithmetic still receives domain checks
before certification. Native arithmetic reordering/rounding is not certified.

Four new controls establish shared bass weighting, uniform divisors/signs,
spatial-product rejection and the unchanged authored Zylot source. Missing
features failed before implementation; no source file was repaired or rerolled.
Zylot's two warp lookups now each describe four waves. Treble attenuation scales
horizontal displacement, bass attenuation scales vertical displacement, and
bass/mid attenuation controls the respective spatial frequencies.

Independent scalar checks at declared bass_att2,mid_att3,treb_att4verify
horizontal weights-.012and vertical weights+.006/-.006, with horizontal
frequency7and vertical frequency9. The test reconstructs public coefficient
DAGs using numeric parent types to restore the internal evaluator's swizzle
flag; the export retains field selectors/type, not that internal boolean.
This exercises scalar formulas only, not an image/frame or native shader.

Independent review found no actionable algebra/domain/budget findings;
55periodic/Q/polar checks pass. Final complete prepared suite:
**2,803tests and92subtests pass in161.51seconds**. Strict MkDocs and
whitespace checks pass.

All100fixed originals retain structured descriptions, source/hash joins,
paired JSON bytes and ZIP CRC. No source-gap changes or new budget failures.
Supported maps grow5→7and matching presets2→3, with18wave records. Four
maps have symbolic amplitude/frequency programs; three have constant Jacobian
bounds. The two new Zylot maps carry real source audio routes. These are source
coverage counts, not visible response, appearance or mood accuracy percentages.

Raw archive: build/preset-corpus/source-ripple-sums-2026-10-10/batch-000001.zip.
SHA256a6a0441561497f655764e2174cc426adaa7448a86bf9121b9d447a659ae9f6ff.
Exact source/model, reader, patch and sealed compile-manifest identities are
in census.json. Sum of export per-preset times39.757808seconds, maximum
2.411531seconds on this host. No hardware or corpus performance promise.

Latest published release rechecked as2.3.36at90b5bf9d9f60a13e9e271cc021a7d1133aa8fb3d.
Full AAR SHA256a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3
matches our verified source34artifact. This producer does not consume images,
audio/time samples, rendered labels or equation/shader execution. Published-AAR
numerical runtime qualification and whole-appearance/mood assessment remain
separately pending. No native engine, authored preset, shared corpus or device
was changed; the existing47-field simulation export remains separate.
