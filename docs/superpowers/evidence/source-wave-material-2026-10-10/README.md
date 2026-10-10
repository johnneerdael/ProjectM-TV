# Native built-in waveform material

Contributing builtin_wave elements now export wave_material: raw RGB/alpha
source curves, finite float32 endpoint domains, native clamp/normalization,
constant vertex RGB when supported and mode/volume opacity recipes. Wave colours
clamp0..1, distinct from custom-shape modulo. Optional brightening divides by
clamped max only above float32(.01); a smooth dim curve can cross that hard gate.
Conditional jump risks are neither observed flashes nor whole-preset no-flash
certificates. Dynamic flags/timing and invalid domains preserve unknowns.

Source34 Waveform.cpp227–352 establishes native processing. Original
MilkDrop2.25c milkdropfs.cpp2832–2840 and mode1branch2930confirm intended colour
normalization/alpha ordering. Native float vertex colours remain distinct from
MilkDrop2's packed display storage. Mode1alpha boosts1.25 before final clamp;
modes2/5attenuate by MaximizeColorsTextureSize; mode3replaces authored alpha
with reference_base*1.3*native_audioData.treb². The native input is not an
EEL treb reassignment. Enabled volume multiplies an UNCLAMPED(vol-start)/(end-
start) ramp before final alpha clamp. Missing audio/history stays unresolved.
Invalid active ramp denominator does not discard independent RGB data; disabled
invalid configuration does not discard valid authored alpha.

Review caught a scope mistake in the alpha<.004 drawing gate. Both DrawQuadLines
and DrawPrepared/hardware lines/points use it before scaled-dot alpha adjustment.
A failing point-draw fixture preceded the repair. Fifteen material controls cover
clamps/normalization, strict threshold equality/crossing, finite conversion,
mode1/mode3alpha, volume ordering/invalid/disabled domains, dynamic flags and
draw-path scope.172producer focused controls pass. Independent final review
passed29material/waveform controls with no actionable findings.

All100unchanged source exports complete with exact byte/hash joins and ZIP CRC.
87contributing built-in waveforms gain material data;50constant vertexRGB,
75RGB envelopes,53final alpha envelopes without audio/history,31enabled volume
ramps and3mode3authored-alpha replacements.302of348raw material channel rates
are known; consumed mode3authored-alpha rows remain explicitly unconsumed.
Normalization jump risk is false77, unknown7, possible3. These only concern this
specific gate; no whole-preset flashing/mood accuracy follows. The three sites
are ShadowHarlequin - Tunneling (glitch mix) - [Geiss - 3 layers], TonyMilkdrop -
This Is A Painting [Flexi - let go + alien complex] --- Isosceles edit, and
TonyMilkdrop - Tricolors [Flexi - feedback accomplishment + techstyle] ---
Isosceles edit; exact filenames/hashes/domains are in census.json.

No image, waveform/audio/time sample or equation/shader execution feeds the
producer. Preset-operation time totals35.453375seconds, maximum1.752405seconds
on this host, not a corpus/hardware guarantee. Final palette, coverage, geometry,
feedback/composite transformation and displayed flashing remain separate.
No native engine/preset/shared device/full corpus was changed.

Raw paired archive: `build/preset-corpus/source-wave-material-2026-10-10/batch-000001.zip`.
SHA256 `e06fd90bbb02e4e1b81b3d4dc7bc273b66423a6098595d9de1067efc04181e09`.
Reader SHA256 `754e4f4129db585cb4f7d5bee915d6bb24ac10ab25901ee7ef0832ce50744afc`.
Matching source34targets published2.3.36bytes; runtime qualification remains
independently pending. Mood and actual appearance accuracy remain unverified.

Final prepared suite: **2,645tests and92subtests pass in145.42seconds**.
Strict MkDocs and whitespace checks pass. Latest GitHub release rechecked as
2.3.36/90b5bf9d, full AAR SHA256a2af1e99f81e6130c77167c11460b0bc9a02306b5fac7fc1b0a1d8c1e33b73a3.
These are source interpretation checks, not whole-preset visual/mood accuracy.
