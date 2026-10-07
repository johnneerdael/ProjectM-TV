# Aurora Ownership — SOL / LUNA

An original sound-reactive portal animation and visual witness for ProjectM-TV
patch0010. SOL is a warm solar spiral at x=.30. LUNA is an icy crystalline portal
at x=.70. Bass expands the core and halos, increases radial light, and kicks the
feedback outward; middle/treble audio animates the surrounding waveform detail.
Twelve orbiting triangles,a256-sample spark wave, a128sample spectrum ring, travelling
light ribbons and procedural stars add motion beyond the identity image.

## Critical ownership path

Only shape0 references `aurora_ownership_core` through `shapecode_0_image`.
Each pack has a different `textures/aurora_ownership_core.png`. No warp/composite
shader binds that image as a cached sampler. The custom shape performs the native
per-frame named-image lookup. Background shaders use only main feedback/blur.
A rectangular warp mask clears old image colour beneath the core before the new
shape draws, so image history cannot disguise a wrong-pack lookup.

## Required host sequence

Use the same512x288(or another16:9 size),48x32mesh,30Hz audio blocks, frozen PCM,
clock, seed12345 and engine settings for every role. Render120frames, indexed0..119.
Before initial load, set texture roots to `pack-a/textures` and load
`pack-a/presets/Aurora Ownership - SOL.milk` as a hard cut.
Before rendering frame20,set texture roots to `pack-b/textures` while SOL remains
alive. Before frame21,set the soft-cut duration to2seconds and load
`pack-b/presets/Aurora Ownership - LUNA.milk` with a soft cut. Before frame40,reset
textures. Inspect19,20,40,59 and completion(81 and119). Record transition status;
exact retirement frame depends on the host's frame-time/update ordering.
The .milk files do not and cannot perform these host API calls.

## Frozen failure prediction

Without0010,frame20's outgoing warm portal replaces its solar spiral with the icy
LUNA image, before any transition begins. The orbit geometry/palette remains warm.
During transition both named-shape lookups useB; cache reset does not restoreA.
With0010,the outgoing core staysSOL and the incoming core isLUNA. Reset reloads
A/B from their retained roots. Completion leaves onlyLUNA. Random transition
shaders can move or hide either portal temporarily; inspect retained preset
surfaces if needed and freeze the transition shader before asserting exact
blended RGB at40/59. Frame20is the unambiguous visible distinction.

## Predictive bass envelope

`kick=max(.78*kick,min(1.5,max(0,(bass-.95)*1.6)))`.
Core radius=.74+.12*kick:maximum.92,24.3% larger diameter and54.6% larger area
than the zero-kick core. Halo radius and particles move outward with the same kick;
ray amplitude grows from.03 to.0825. These are source parameter bounds, not claims
that every input track reaches the maximum. On the frozen one-second test PCM,
computed kick spans.152871..1.5. The supplied packs share equations except palette
and centre, and the host must use exactly the same PCM for each engine role.

## Scope

Source-only forecasts are frozen before standalone full-AAR captures. These are
creation checks, not credit toward the random-preset streak. The separate host
root-switch/soft-cut/reset ablation is still required to certify the bug witness.

## Verified delivery

Both final originalpresets compiled and rendered through the unchanged published
core2.3.23 AAR. Frozen30frame motion/colour/flash estimates all pass the5% rule;
worst relativeerror0.0758%,with exactflash-event timing. No pixel-perfect or
whole-program accuracy claim is made. The final assetrevision also passed the
separate GPU ownershipablation:roles match through19 and firstdiffer at20;
unpatched outgoingcore turnsblue whilepatched stayswarm. Both120frame
roles repeat byte-for-byte and reportzeroGL errors.

The10second demo uses300real native frames at960x540/30fps through the fullAAR,
with an original120BPM synthetic kick,bass,hats,snare andpad track. Its centred
SOL variant changes only the centre configuration for presentation. MP4 duration
and both audio/video streams verified10.000seconds. See verification-summary.json
and the Downloads delivery for the video.
