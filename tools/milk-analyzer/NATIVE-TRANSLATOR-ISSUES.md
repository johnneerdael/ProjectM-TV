# ProjectM TV core: native translator engineering handoff

Date: 2026-10-04. Task: investigate native HLSL preprocessing/GLSL emission failures that block source predictions. Keep this separate from analyzer-only scope and liveness fixes.

## Resolution update

[PR #26](https://github.com/johnneerdael/ProjectM-TV/pull/26) is merged at
`ce9b80aa65860a81efa7ca90ad4763fcd96a2f58`. Patches0030–0032 implement T1–T3;
do not reimplement the historical issues below. Its evidence reports54/56 array
and48/51 sampler-state witnesses compiling, and eliminates uninitialized
uniform-copy declarations. The analyzer now models the initialized global copies
and grouped arrays with matching engine provenance. Unverified random-sampler
association remains blocked even when explicit types make offline compilation
succeed. After adopting PR #27, the bounded source audit retains 27 known gaps.
The affected tables and2.2.4 evidence below remain historical reproductions.

## Artifact scope and release status

These findings concern **our patched ProjectM TV native engine shipped in `ProjectM-TV:core`**, not an unpatched upstream projectM binary. Attribution to projectM identifies the embedded code lineage only.

The original diagnostics and numerical controls used the pinned published **core 2.2.4** and the analyzer’s private copy of projectM 4.1.7 plus our then-current patches. They do not establish current-release failures automatically.

| Artifact | SHA-256 |
|---|---|
| Published core 2.2.4 AAR | `75e8cbb9ce4ab9340ac9514c16812bbf79e5b3dfa8f29db22d653c601323ce60` |
| Its ARM 64 native library | `11169fb1a75ee9ccfe607db44bee5022a42410486605a3eb01f43e0e65221755` |
| Current published core 2.2.6 AAR, downloaded and hashed | `0e61b2ad0de62a71a1cf837706821c14a536568fa85b6359a5e8321b63226b3e` |
| Core 2.2.6 ARM 64 native library | `cd66617d35c266e862324163931262e2478a9eb658ecaa227fddabbd4a6eece4` |
| Private CPU adapter engine archive used for original diagnostics | `1209ee81dacbc772931e2d66337d1e574d8ebf1b806c5f575eccfc812eceedb4` |

[Release 2.2.6](https://github.com/johnneerdael/ProjectM-TV/releases/tag/v2.2.6) was checked on 2026-10-04. Its native library differs from 2.2.4; revalidate on 2.2.6 before declaring a current AAR bug. Do not conflate the shared corpus’s instrumented baseline library with either release library.

All preset names below are exact filenames relative to `core/src/main/assets/presets/`. Hash the file before using an affected-list entry. Lists identify historical witnesses, not a promise that every named preset still fails in the current release.

## Priority and boundaries

| Issue | Historical affected presets | Evidence | Current 2.2.6 status |
|---|---:|---|---|
| T1: array constructor/layout emission | 56 | Native translator output rejected by offline target compiler; one numerical family control selects fallback in core 2.2.4 | No array-emission change appears in the 2.2.4→2.2.6 patch diff; revalidate AAR |
| T2: sampler-state preprocessing/binding | 51 | Copied native CPU preprocessing/transpilation rejects source; one numerical family control selects fallback in core 2.2.4 | Patch 0026 changes warp unit ordering, not this syntax preprocessing; revalidate AAR |
| T3: packed uniform replacement leaves other components unwritten | 23 | Exact native AST rewrite and generated GLSL lose initialization of untouched components | No uniform-rewrite change appears in that patch diff; revalidate AAR |

Counts are per-preset witnesses; do not add them as distinct visual-validation results. No human/AI image classification was used to establish these findings. Compiler acceptance is not an appearance prediction.

## T1 — array initialization is emitted with the wrong layout

**Observed:** `GLSLGenerator::OutputDeclarationAssignment` emits an element-array constructor from the raw HLSL expression list, without flattening/grouping into vector elements or preserving partial-initialization semantics. All 56 saved witnesses fail the GLES 300 offline check under explicit reader-derived descriptors. Do not assume every rejected initializer is valid in official MilkDrop; distinguish legal HLSL layouts from genuinely malformed input.

Representative preset: `EoS+Phat - spectrum bubble new colors - orb sth go4-ret brothers organs.milk`, composite section. It declares `float4 samples[5]` using 20 scalar initializer expressions. Native GLSL emission does not produce the intended five vector elements; the compiler reports an array-size/index error.

Minimal family reproduction:

```hlsl
shader_body {
    float2 a[2] = {1, 2, 3, 4};
    ret = a[0].xxx;
}
```

**Intended investigation:** validate the grouping rules against MilkDrop’s HLSL compiler, then emit explicit per-element constructors with the declared length and element type. Diagnose insufficient/excess elements rather than guessing. Preserve integer/float conversion rules for GLSL 330 and GLES 300, unsized arrays, matrix arrays and helper arguments.

**Code locations in the embedded engine:** `vendor/hlslparser/src/GLSLGenerator.cpp` (`OutputDeclaration`, `OutputDeclarationAssignment`); the tree’s aggregate/array type representation. Submit fixes through `tools/projectm-patches/`, not by committing edited submodule files.

**Regression requirements:** flat scalar-to-vector grouping, already-grouped vectors, partial/overfilled lists, unsized arrays, array helpers and desktop/ES conversion differences. Capture compiler diagnostics and verify current AAR loads the authored shader rather than its fallback. Compare paired source-derived numerical controls; do not certify every visual from one control.

### T1 affected presets — 56

| Preset | Source SHA-256 | Section |
|---|---|---|
| EoS+Phat - spectrum bubble new colors - orb sth go 4-ret brothers organs.milk | `244b7e7589bc6bf58242b85041e3cb97b800614a0d73b1dc71fa90e76d8398a3` | `comp_` |
| Flexi - wave function collapse - major dick.milk | `0d79247a8de280e66e69c0fadac127ed5219b197803010d754e35acf4277b88a` | `comp_` |
| Flexi - wave function collapse - majorly dickless combatanth.milk | `d376201257624655b93459c8b247978d6a16c1e99a867c05b4f3e4c6145231e0` | `comp_` |
| Flexi - wave function collapse - majorly dickless nz+ puke mash.milk | `866131d9c4557ceb4f36949c29135842a8b3648305c7c25ca13d53e56da71dc1` | `comp_` |
| Flexi - wave function collapse - majorly dickless nz+.milk | `ddad1d6ab3507fbf7b1ce0b3756cd2743e3095f9bd202eac8051137b64938884` | `comp_` |
| Flexi - wave function collapse - majorly dickless.milk | `b17fee8006e59220ee3ace8f32cda438bb223511371d1017845d3863eb666a45` | `comp_` |
| Geiss - Flexi - Redi Jedi - Shifter - Phat - Rovastar - 120287110113(457) - orb sth go 4-ret cataclysmi.milk | `e0d1baa67c16c336bb88400a1ff0fa09d049a2447238a96c5387b8fe9ba315bd` | `comp_` |
| Geiss - Flexi - Redi Jedi - Shifter - Phat - Rovastar - 120287110113(457) - orb sth go 4-ret cataclysmic sound roam2.milk | `c697ae8b4a3b5039ca1111271dcbcd7960617621d60d34a54c4269de05ca7367` | `comp_` |
| Geiss - Flexi - Redi Jedi - Shifter - Phat - Rovastar - 120287110113(457) - orb sth go 4-ret cataclysmic sound.milk | `41701fb2f25a1b4628a6eaf025a4441bc6b5424082142dd0d74941febda34052` | `comp_` |
| Geiss - Iris Storm - greyed-out options.milk | `ad88e3cd3c80de58b9bb1fe421514b2bbc6fbfaace10af426eee2566b9aef149` | `comp_` |
| NeW Adam Master Mashup FX 2 Geiss and Zylot - Reaction Diffusion 3 (Overload Mix 2) AMAZING MASUP  - orb sth go 4-ret tork.milk | `4f8fd8e1e657dc0d87ed4d8bc2a3ee4e15efa5310223d53a125434582ecb47d1` | `comp_` |
| ORB - 3 Pointed Flame.milk | `c4cc4236b7c7a8ed0023c83e4b3855ca6c734e752ef60240158a6165dde13d83` | `comp_` |
| ORB - Planetary Alignment vs Martin - sparky caleidoscope.milk | `8456cc311aec289dbfdef0e345367f98c5fb4ac87888a1511dfb3de46d98c8db` | `warp_` |
| ORB - Planetary Alignment.milk | `436abe81fe0615642bca8706981e6b6d1c378628177ecd75edbb9f0473ba54bc` | `warp_` |
| ORB - Quicksand Lab.milk | `80f11873f7e81063020a9d21f58e255d2efd4bcddb183d05c8b41dd16215ffeb` | `comp_` |
| ORB - Sandblade.milk | `1233f931653927c6446b09ed10019c15fd948884dc79f1adaedaa283f3d644ca` | `warp_` |
| ORB - Solar Fire.milk | `854d9145964d8d3740ec095bd7253c54d3235c274a44c1ffb7dfe346a75128f5` | `comp_` |
| ORB - Stahl - Fire Worm.milk | `9e839def6d8ae9755a923939c8e0ae0717b7b0950bc540ee98279b66aec676a8` | `comp_` |
| ORB - Stahl - Glass Ocean.milk | `499d464efca2e65d04c943ee4877c46d4dc533b70b2ba42fcb1c923d2cd64d9c` | `comp_` |
| ORB - Stahl - Liquid Eyeball.milk | `ab1c819230e84ceb86ae4b29afe287379842bebe0d8174057b80804102989f3c` | `comp_` |
| ORB - Stahl - Sunburn.milk | `47dd7a418dd51994432554bfac05924587fe752c3b7174f2f6c248357785b394` | `comp_` |
| ORB - Stahl - Tantalum Gran random tex not worthy to comment on your potential love life failth.milk | `7658991f83afc743775ca9a8ff0eb55473182a8cd185df5fc45caee15eaa4b04` | `comp_` |
| ORB - Stahl - Tantalum Gran sky.milk | `68d137f51da4e51b944b00ca909d29a636dcf32a940d209f218b885a305e42b6` | `comp_` |
| ORB - Stahl - The Claw.milk | `3e5772297ffb05b3afbd086af9197e9e107f4774d99e831259ebad6bfe4608c1` | `comp_` |
| Stahlregen & Boz - Machine Code (Reaction Diffusion) genial cores.milk | `d0fd1f809045b02e33c002b8da53ff56407c12dc5918cdc0dcf0f82817e50d52` | `comp_` |
| Syst3mFailur - satanic ring V2 nz+ toby f-zero.milk | `5e79eb3005b114342f9cf07ca397424726e02a621596a920dc506ded632ffdc4` | `comp_` |
| amandio c - prime forms 2 minor full.milk | `db751a78480f59343867ac9cab2ff23fa558c681920b531c057e7375f4ceceec` | `comp_` |
| blood red raw holy - i am an insulted prude and a concerned parent and a disappearing goat.milk | `e9b498556e073a206d8c1029b55a5e9ee4d03deaf028eafb39ebe8ad7d741132` | `comp_` |
| cpe domains flacc - portable massation segway nz+.milk | `0244f2bb90dfaa4327dcda0adf47410f85c73c68835a21ab3f7d9f1f1c7eb71f` | `comp_` |
| cpe domains flacc - portable massation segway nz.milk | `ab27fb421fc04c35227fd7abb6b1f0f0aae3ac6bc4fc5254b5d8f62e5083516e` | `comp_` |
| cpe domains flacc - portable massation segway roam nz+.milk | `c3550aedd7a3dd73f3ea60334246f53632801e166ccee93bdf3ef384ae7ee8cb` | `comp_` |
| cpe domains flacc - portable massation segway roam.milk | `9f9ef68b701623f7f7128ab24406f1e76f2e1c12560d23d611a198bce97bead5` | `comp_` |
| cpe domains flacc - portable massation segway.milk | `7b63b17da8495b37e15c5340dc3e6483be47192394e5ba0d4172d56404cacef0` | `comp_` |
| do not fear me, but eat me braqre briq awakened to infinite disappointment my believers follow me to a land.milk | `1c63490faa1ba880e1b4735a9f9438fc8713f56686769e1007c99dfe093279af` | `comp_` |
| fat cancer cun cet.milk | `f0662191c1c1d91b96df8a31d782e21c531a63619a8c29bac69c9505a4e02e3d` | `comp_` |
| flertiveneth ov model stain.milk | `5e467f8248bd0f41c048f24ca55ffc74890775fec16f6cdba3d25635f3c17202` | `comp_` |
| flexi, stahlregen, geiss + tobias wolfboi - space gelatine burst [golden brilliance rmx]_1 - orb sth go .milk | `fbc79608ce42ab8544e65a1e9a2bc2f106babc74892e0adb9c6ec74c8389f99a` | `comp_` |
| hexcollie, ti@n, suksma, zylot, orb n flexi - blarffff bubble.milk | `2ad621b5196980729d2f9249f106d06949217ab510b1371c786f034025d42b78` | `comp_` |
| mouthful o sand.milk | `a45105e86ee41b1bcfacc0e29119458e4891d8785e1595e92f254ddc0f6bbcdc` | `comp_` |
| nontuplet corpse sterility.milk | `7f89564b479e42e01f82061ca69020c0c022647460446e1c15903406d542e3f1` | `comp_` |
| orb - quicksand sharp.milk | `02edab80c5cf8c8e3bdd6a16be70c8283213c20dfa40e16e89cae77ecf548b8a` | `comp_` |
| pair up gnothing knew nz.milk | `de5deed49ba06c946215781245e4c853363f504701ec4cc62808e41ef603a69d` | `comp_` |
| pair up gnothing knew nz2.milk | `b94e63c46e808a106948713f09c14425c7ce025f74b24842c513a17b1f5e004d` | `comp_` |
| pair up gnothing knew nz3.milk | `f7b8b7f7dc9990a6b6ce28a49a59af682b2be769a89f7c916c6e3ca2c46462cb` | `comp_` |
| pair up gnothing knew.milk | `b9d395f575a0b66fc4c82e4d1f70ecb4795791dfcb76c6933365802aba86de97` | `comp_` |
| sonar cow.milk | `289a57aea3b7bde6324a98596ee5f4178dc4a6da9dd831c1fafb7ee5c500861d` | `comp_` |
| suksma - dotes hostile undertake - frazzle.milk | `23b49eeacef9f2340f9a9d9a168d0637cd0da108f56e6d7db7a66f8d532269f6` | `comp_` |
| suksma - dotes hostile undertake - mash vs expand - flacc - orb sth go 4-ret bowel studies.milk | `d622954d5f9e0da40171114bc8166433f3927ad9a9fbc41ac0f8792587a5a951` | `comp_` |
| suksma - dotes hostile undertake - mess - orb sth go 4-ret raygun anti-masturbation.milk | `2f2699d87d522e7945c42fec84026275bdd4ef0f9a0ae0d12072e49f121b2acb` | `comp_` |
| suksma - ed geining hateops - flx matilda nz.milk | `2c728b04a7774ad7fbdf125ddadcc72f27d0dcebcb5370f79123c73a25e71387` | `comp_` |
| suksma - ed geining hateops - flx matilda roam3- nz+.milk | `6dee7ee43e26708cb4cc00f85d9c34c9d79103454d5e05d2782c36faebd9003e` | `comp_` |
| suksma - ed geining hateops - flx matilda roam3-2.milk | `ad433c65e94a95d9a84a000ab67d8ae0bcb0c059053070db9fc3a27ebcc56848` | `comp_` |
| suksma - ed geining hateops - flx matilda.milk | `dd37abaaf03c47c2304c3ce9d537d355cabcb9e47e6b6feabc9f0818d7b67a6c` | `comp_` |
| suksma - flexi coheres vacuum energy - shf fab in miatas - orb sth go tableaux.milk | `f0e8fd6939bc38f4a45db340a309bd690576ad469d49f65215986d4c46be1186` | `comp_` |
| suksma - kabbalih yao hymanifolder - frazzle.milk | `5e7dc14b45e39b85697238058dc4bc5cff6bdfe3c46f9fc96078bc92ea730565` | `comp_` |
| suksma - negative infinity for not flinching - orb.milk | `062aab485ffa1d1dcec3c0d929e02e2baa74f93397e3f567ca8c1de958c35953` | `comp_` |

## T2 — sampler-state source is corrupted or rejected during native preprocessing

**Observed:** declarations such as `sampler sampler_main = sampler_state {...};` are parsed by the analyzer’s source reader, but the native preprocessing/transpilation path rejects the 51 saved source sections. Native reference scanning can also treat an unspaced `=` as part of the sampler name. Declaration removal and choosing the shader-body braces can leave state fields in the generated function/header or use the state block as the shader body.

Minimal family reproduction:

```hlsl
sampler sampler_main = sampler_state {
    AddressU = CLAMP;
    AddressV = WRAP;
};
shader_body { ret = .8; }
```

A separate spaced declaration **inside** `shader_body` has previously compiled with explicit native descriptors. Preserve accepted cases; do not globally ban or silently remove all state blocks.

**Intended investigation:** parse declaration and state-block boundaries safely, anchor the actual `shader_body`, normalize scanner delimiters without corrupting texture names, and establish which state fields are honored versus replaced by our name-based texture/sampler policy. Determine behavior for `Texture`, filter/address fields, aliases/macros, global/local declarations and spaced/unspaced assignments. Avoid fabricating missing textures or sizes.

**Code locations:** `src/libprojectM/MilkdropPreset/MilkdropShader.cpp` (`GetReferencedSamplers`, `PreprocessPresetShader`, `LoadTexturesAndCompile`); `vendor/hlslparser/src/HLSLParser.cpp`. Inspect and retain [patch 0026](https://github.com/johnneerdael/ProjectM-TV/blob/v2.2.6/tools/projectm-patches/0026-custom-warp-sampler-binding.patch): it reserves warp unit zero for implicit main. That ordering fix does not itself fix sampler-state syntax.

**Regression requirements:** both stages; global/local state; comments/macros; spaced/unspaced `=`; default and explicitly named main samplers; 2 D/3 D/external textures; absent material inputs; exact source/descriptor/profile provenance. Keep process crashes/timeouts unknown, not presumed fallback.

### T2 affected presets — 51

| Preset | Source SHA-256 | Section |
|---|---|---|
| EoS - glowsticks v2 04 music minimal - swim  - dictatutorial rt roam3 2.milk | `5dd383cf79e1aacbed944ded85d70a365dde2c51f2ca7646ed0b7fde0cf4c79f` | `comp_` |
| EoS - glowsticks v2 04 music minimal - swim  - dictatutorial rt roam3.milk | `06b84ff69c3aeeb88eff3dea63dd3c1f5b146b4c2afb9df204f5f2561e7aee15` | `comp_` |
| EoS - glowsticks v2 04 music minimal - swim  - dictatutorial.milk | `5f2e3c5732513d8f2c14a6c6dd2255fc38e1f7034a1906dc02726e47fc8585ad` | `comp_` |
| ORB - Arctic Chill.milk | `6baf4215af49e53e20ccd810497ed72b0d59347236546e5438a5edde638ad13f` | `comp_` |
| ORB - Flexi - Chilled Element.milk | `e1cbf8d01bc0e37234d8ed2c7ca1413c8af7d4dbd11dd1d59f7bf4b545e6e8dc` | `warp_` |
| ORB - Flexi - Eleventh Element.milk | `343a22ab6e971222d3baea473b9d16a5c8598ef4378bbba5ceee5467201bce2a` | `warp_` |
| ORB - Flexi - Ninth Element.milk | `94b518dc38d136b265b6493b4bc3fd32faaaf2abf14b9a7a31b24ea51886a465` | `warp_` |
| ORB - Flexi - Tenth Element.milk | `537501c8a8ac320c39c6a7519f78ee076a5068848b3429fb20e9ac6d71af6b6e` | `warp_` |
| ORB - Smoke and Fire.milk | `5b79ec3443c5dc54b89d148e8e2f88fd0b39917797abb22b25c57826ad4bcab1` | `comp_` |
| ORB - Smoke and Ice.milk | `e26af58e2ab773d1021de5af1e475a2de5938812a036e19dfc98cff4036e5f97` | `comp_` |
| midgitstraights of majillaen - featy sweet.milk | `d4cd997dedc57ab34c7247fee1ba94d4061528d12d16cde5a468145fb216ebba` | `comp_` |
| shifter - mosaic mitosis - j4 all servants left to gare.milk | `b9212257a4199186202a1d6fba5d46e0fbb581db1a8f5645414323f6189651cc` | `comp_` |
| suksma - amental ruiner broach2.milk | `007a3729feffc0baf0debd44e56458976abad241ae4a01e7be87f4d293f0e2db` | `comp_` |
| suksma - anti-tank tamm 1-50.milk | `f22b913aa3d8d260cdd5a800b2f1644cd64c752b1983a30785ec059cba2cfec2` | `comp_` |
| suksma - astral project x.milk | `3f3562873e8ebd57435da5fcd3cd42a0a21c028bfc923a075e1a8ea527e26352` | `comp_` |
| suksma - bonnie self.milk | `f2e83d0b868d7e609588777c03f30dd827dda1753679c1be01d3bd0e6659137e` | `comp_` |
| suksma - borat pubis jokulars.milk | `e74a28440be792d6fc8ef83087b8eb5acd8b89492826bff6b4cff2759e3ff62b` | `comp_` |
| suksma - care puts us through more pain, which is doubly ironically good.milk | `41f127b78ac58610438013e80fe91034d126b1210a406a141ae53920b005c97b` | `comp_` |
| suksma - chernobyl pie for dessert - more lateral shade of masueality.milk | `c9f6b2b167de683e64426cadc684b1a76f43a91728f03c72070d93f29162dd21` | `comp_` |
| suksma - chernobyl pie for dessert - sanguine lococlustarz banefilamanes.milk | `913f45a044dae4b6aa342560754e846d3c8729fbf68c837a026ae82ee9d9e9c2` | `comp_` |
| suksma - dikso lactose.milk | `74d9b1050f5ed14df424b30a2886032e0dfe3e90fcf2e4d9ed44039636ee184f` | `comp_` |
| suksma - do get your hopes down.milk | `556d402c9f021e1e9292a2085fb38e24a9904e93ad108ded7ee9e0f14b239267` | `comp_` |
| suksma - egg space ad hoc kludge regurge.milk | `98ea6d655b9c427e67b131f878d251ffcda6333974fa39913f49285cee5b1814` | `comp_` |
| suksma - eyes that will not see.milk | `c050efb6fce70abe6b12c73d70f081de34cbfec7aeae5f050a0d90a867682826` | `comp_` |
| suksma - fiShbRaiN - witchcraft (phugly megalopolish remix)2 - horse mane mattresside.milk | `d1d2be17abeb05c12361834ba340fee7cdbf53d98b302a6711256bbd4988e83d` | `comp_` |
| suksma - for all your banking needs.milk | `16a5559295292f17cc0895354d2a47a9d9acdf685f610457739fda9293d987db` | `comp_` |
| suksma - fram oil filter ad.milk | `78cc704d86e901d69198a98d7aa21fc4875015c162b4bd3d7b9a0fabec085596` | `comp_` |
| suksma - gambling with my life is ok, go for it.milk | `b763050f5b3c019eb2dfee64a09114aa9d0506653ad5fe905fbdc2cf3e37fc3b` | `comp_` |
| suksma - infinitely versatile virtual stringed biofeedback instrument.milk | `210a0931e2761bfb782695a658bab04d936dc558770c51e733cd05c23a57cf61` | `comp_` |
| suksma - insect coarse hair poizen stingers - southern cross jupiter misalignment --- Isosceles edit.milk | `768710055fd0bb96eeba51cb87ce4beca03970044b061136435a2d802194554f` | `comp_` |
| suksma - involuntarily sliding up the dimly lit floorless corroded walls.milk | `4b5c31124f349a9752e4ce2ddba9b8fe23870bb7a4d9f24f102afedfb8307a4b` | `comp_` |
| suksma - kakafonouz larquidark --- Isosceles edit.milk | `30b0c90dce1da1a8dbaae8311af70a8f00446411d593e7ccc47ef9ab4a2fe881` | `comp_` |
| suksma - keep up with invalid retrogress.milk | `f48efa525d19c4ebb58f9ffd7a18e059d0cedfbc122cab568a285b446e9a0f13` | `comp_` |
| suksma - lackstastique.milk | `1ce72df71ec6f4208dc7384b46443a67022a638d3cc761862790ca114b7cf8b4` | `comp_` |
| suksma - league fathom slide molech.milk | `06c5f803dc5c71eddadfd176737b5d58deb3c239ab2ec90af20b4516cb785180` | `comp_` |
| suksma - my pal, ball.milk | `3a5c8760f3d0551d35b2e2f1330948b077d606a2399521f41ce2cabdb9453aca` | `comp_` |
| suksma - negative infinity for not flinching - neg3.milk | `cb76c1c73afec3b6f87436090b3318fd29215e84c057a0023200a960e1cdce96` | `comp_` |
| suksma - never bam.milk | `1e75702b33ce57180bb57aaf06bc5da0f221509d7255df1714388342ca573b01` | `comp_` |
| suksma - no beat forensic.milk | `9d710acfe4856fca848e908eaec7013b29ca09ccdd82a90ac57e16ba50610955` | `comp_` |
| suksma - not like this, not like this.milk | `b2998ce6a2c6992ce7fe97850ec8db54c5bb9b5de700e5dd9fceaa4f0d28d24c` | `comp_` |
| suksma - outre seepia sweyy lurk memephetase (2).milk | `1964ec095a1a4821d896c35494ff6125de983eded24371a9f5989a4fd9d9047d` | `comp_` |
| suksma - popart death smock leftbrain.milk | `d0041e489835fc537211a8582f3370b8ce81d37c4d7563f9f0dd88f9e7aeb99e` | `comp_` |
| suksma - shadowgate melt ghoul.milk | `8c880c5a33ebc8d873118b3344eb9d6927363fc7dd87f8e154e97a4e0a176d92` | `comp_` |
| suksma - shiny-bladed homicide machine at dusk - occult calendar time lapse slice.milk | `0773fc7b69a44545b4b4e0f5e6a9945868c06e5a57e3204e9284043ec82b24d1` | `comp_` |
| suksma - shiny-bladed homicide machine at dusk - quantum liquid beads riding cosmic strings.milk | `cc85b04956f4e9aa97c6e336d578e12c400ce3898cdbc625f22fe2f9907836d9` | `comp_` |
| suksma - thought she knew something about the middle east because she grew up there.milk | `bec08797e519d44196fafa29821a1530c4d5fe01e945f795a486d3658721f5c3` | `comp_` |
| suksma - to finally feel like a cyborg.milk | `027a136d3330b5f384bb562d9b5af39b28c906fef29cc8fbbcdf3f0acc95c11e` | `comp_` |
| suksma - water + god roam3.milk | `fe77f903e21fd5eb9a4e7a3bbffd1dc9c7e9b91af5b9a89b63f8dbf86908bd05` | `comp_` |
| suksma - water + god.milk | `1634fdb50f1ada951996a3a0898056332a10819a2b3c2afeb7d4f462d576bbc3` | `comp_` |
| suksma - water god.milk | `47ec30203c9ed7f2015d059e563b65b3cf5a19cf1ecccb1cbbfa79588a91c42e` | `comp_` |
| suksma - yaqui mirage master.milk | `4fcd6be698a29ecb680d3f1933c62c9bbcc37f79f1ffa4a55e5b51a7e39b28b3` | `comp_` |

## T3 — replacing a packed uniform bank loses untouched components

**Observed:** `HLSLTree::ReplaceUniformsAssignments` adds a function-local replacement with no initializer, then routes subsequent references through it. Assigning one component can therefore turn untouched components of the same bank into undefined reads.

Minimal reproduction:

```hlsl
shader_body {
    q18 = 1;
    ret = q19;
}
```

The native rewrite creates `new_qe` without copying `_qe`; writing its Y component leaves its Z component unwritten. Equivalent issues occur for `_c2`, `_c7`, `_qg` and other packed banks in the list below. The analyzer must not guess these values as zero.

**Intended investigation:** preserve the original bank when introducing a writable per-invocation replacement, while retaining the first-assignment RHS’s original binding and correct function-local lifetime. Check compound assignments, helper calls, branches and component writes. Verify official MilkDrop semantics before selecting the repair.

**Code location:** `vendor/hlslparser/src/HLSLTree.cpp`, `ReplaceUniformsAssignments`; generated declarations and renamed variable bindings in `GLSLGenerator.cpp`.

**Regression requirements:** write one component/read another; first `q18=q18+1`; compound assignment; helper-local replacement lifetime; conditional writes; all packed components and scalar uniforms. Do not mask genuinely uninitialized authored variables.

### T3 affected presets — 23

| Preset | Source SHA-256 | Section | Unwritten replacement origins |
|---|---|---|---|
| $$$ Royal - Mashup (324).milk | `70c428f595882862b346f55bb7b6cf342ce30e1f7e1ffe9d58299cbc80051f78` | `comp_` | new_qe[2] |
| $$$ Royal - Mashup (377).milk | `91d5b37a54d070815e77191cf02ab31760da9ddc0a0d114e0f7385d59dfdae23` | `comp_` | new_qe[2] |
| $$$ Royal - Mashup (395).milk | `1197c33d8c73a0a6573619dd336a8bec20e3b89f667c50663d06fcd9e3ff01fa` | `comp_` | new_qe[2] |
| $$$ Royal - Mashup (403).milk | `c3b8e33c71b28ea315da975e6baa7ffc14e8f0e8f5be095493833b50c623062f` | `comp_` | new_qe[2] |
| $$$ Royal - Mashup (444).milk | `d7ba09e73f8c94e411b729391444c467b9b3e06071be3f8a7f2a9a63f24de1f2` | `comp_` | new_qe[2] |
| 374 nz+.milk | `fa190092643c4c2824b791ec30f6bc2c2936701ef0dd3f4606e184858385f622` | `warp_` | new_qg[1], new_qg[2] |
| Chemlock - Spot mod(Zylot & Aderrasi equations) nz+ caring aethmatique slumberdengullion.milk | `5b482458682fd7557d7a1bfb990220266006fe220d968932d61148e0aa1b29d3` | `warp_` | new_qg[1], new_qg[2] |
| EVET - Spiracology 2.milk | `2204cee597e4ebe6e9b5dae1ccdf89f2b0b49f41eeeb9a041a526c07116ffa95` | `warp_` | new_c 7[2], new_c 7[3] |
| Martin - QBikal - Surface Turbulence IIeeeee hakanh mash-up k10.milk | `5d7e6434c83ab2285b71d346114e3fb57547d7f5c811f8a49f35b4f4d2bfbd56` | `comp_` | new_c 2[0] |
| Martin - QBikal - Surface Turbulence IIeeeee hakanh mash-up k8.milk | `7e85c8d05450e0086cfa9a2ca75178acbd19f84243db7868ef760c1417549911` | `comp_` | new_c 2[0] |
| accept reptile paradigm nz+.milk | `158338ca963f91edb93bc6b81ace476a27580dcada6ccddc7a7da25c4d86ae3e` | `warp_` | new_qg[1], new_qg[2] |
| boobs - tithypno.milk | `07dffa334fbedd13bb5986d79336f8078937c9e3a9d01b09325a44f8418abd9b` | `comp_` | new_c 2[0] |
| craving 'spinach man' action figures suppositoric nutrition - cryingkey nz+.milk | `1eae20e2715576e5854318501253b6c22668c0564494fa1b2d639e522f5cfad6` | `warp_` | new_qg[1], new_qg[2] |
| fed - fumez.milk | `95cdcd88fef37dd82f9889ef5f5489c45d1c980add9b41b984e95a5914007e5e` | `warp_` | new_c 7[2], new_c 7[3] |
| goadzoan nz+.milk | `556c401b87fed58fd9fa035d23010826e82c0544344c5007ae79a545493599e0` | `warp_` | new_qg[1], new_qg[2] |
| martin + stahlregen - martin in da mash 4 nz+ compeckts system of agitation.milk | `5ada1d3d967aff091a17c87aeb5ab3fcd6242deb4dde01847bfffe1257c773f4` | `warp_` | new_qg[1], new_qg[2] |
| martin - mandelbox explorer - high speed demo version (LamersAss Remix)(1).milk | `4b830f72514c785594bcf279265d27ea5ba49a2ce6bf3156a3647a036db1c3fa` | `comp_` | new_qe[2] |
| martin - mandelbox explorer - high speed demo version (LamersAss Remix).milk | `b89e791fe064ec304b3ca8b750c0870e3baa2ace14575846b57137e105d9c5e5` | `comp_` | new_qe[2] |
| suksma - coal drapes - mrt fsh behooval roam3- nz+ gene qreemqron.milk | `c892db1e81122a2942baa82a7f25387d2ed1c73c0bb2de0fdc8df3b94036fc35` | `comp_` | new_c 2[0] |
| suksma - n19 3 layer overlap opt 3 flx nz+ loqo satan rises from the pit via the hateful thoughts of man.milk | `ec89412f4256099493edf06c5a5e998eccdef49da00c5e0df3e0c445d380a258` | `warp_` | new_qg[1], new_qg[2] |
| yin - 100 - Through the ether qansre phevre nz+ exhoneration by disassociation.milk | `2f914ff0968d779f2876cb6c9e2bb2f9a33c1e9f2a8f4f94603ac428e9d7a0a1` | `warp_` | new_qg[1], new_qg[2] |
| yin - 100 - Through the ether qansre phevre nz+ if love is so important, maybe we should show it.milk | `4076a79fcc0dbb634e646fe82be2ad7f96672c93c31f56f22249ae23a794e3a2` | `warp_` | new_qg[1], new_qg[2] |
| yin - 100 - Through the ether qansre phevre nz+ phlegmtastiq.milk | `e36e81ae438ce2b4dacd7155b67627b72cfff60846eb42655350be9ba1a4fdf4` | `warp_` | new_qg[1], new_qg[2] |

## Evidence and handoff use

- `fixtures/array-state-fallback-native-proof-2026-10-04.json`:107 source-bound offline stage plans and two frozen published-core 2.2.4 controls,60 frames total, zero maximum RGB 8 error. One affected preset also has a fatal equation rejection; shader fallback alone cannot make it load.
- `fixtures/focused-blockers-220-2026-10-04.json`: committed blocker inventory before the pending component-lane analyzer correction.
- `fixtures/helper-return-source-proof-2026-10-04.json` and `test_shader_components.py`: packed-uniform/source binding evidence and regression reproductions.
- Local full compiler reports: `build/milk-analyzer/focused-array-binding-2026-10-04/compatibility.json`; local source trees under `build/milk-analyzer/focused-315-loader-ignored-2026-10-04/trees/`.

The latest release already includes shader exception diagnostics, warp sampler ordering and fresh feedback initialization fixes. Do not report those as new open issues. This document concerns the distinct failures above. Do not borrow core 2.2.4 or instrumented-baseline captures as current 2.2.6 acceptance evidence.


## Current remaining parser cases (35-patch snapshot)

The original 315-preset subset now has **27 known source interpretation gaps**.
All 16 remaining shader parsing witnesses also reject in the CPU adapter that
uses the unchanged translator bodies from the merged 35-patch engine snapshot.
These are not merely failures of our independent field interpreter. Descriptor
inputs are explicit; this is not a current AAR driver or visual certification.
Exact engine/source hashes and minimal controls are recorded in
`fixtures/remaining-native-parser-16-2026-10-04.json`.

### T4 — local identifier `sample` consumed as an interpolation modifier (14 presets)

`HLSLParser::AcceptInterpolationModifier` unconditionally accepts the identifier
`sample` while probing a type. An expression statement using a previously declared
local called `sample` is consequently consumed as a type/modifier attempt. The
parser then reports `expected identifier near '*'` or near `';'`.

```hlsl
shader_body {
    float3 sample = tex2D(sampler_main, uv);
    ret = sample*sample*sample;
}
```

The unchanged native translator rejects this minimal control. Renaming the local
and all its references to `sampled` translates successfully. The same isolated
rename in diagnostic copies of all 14 exact witnesses makes them translate;
all 14 generated GLES shaders pass the offline compiler. Original preset files
are unchanged and remain blocked. Diagnose speculative type parsing / token
rollback so expressions using an existing local remain expressions; preserve
legitimate interpolation qualifiers. Verify against the legacy D3D compiler
before introducing broader identifier rules.

### T5 — object macro containing a sampler declaration loses token boundaries (1 preset)

`Fed + Geiss - Color Pox Remix.milk`, warp, contains
`#define smp sampler sampler_manyfish;` followed by `smp`. The native preprocessor
emits `(samplersampler_manyfish;)`, appended after the header's last declaration,
and reports `expected ';' near '('`. A minimal macro declaration reproduces this;
the equivalent direct sampler declaration translates. Expanding the authored
macros in a diagnostic copy makes the full shader translate. Inspect object-macro
whitespace retention and expression-parenthesis wrapping in `HLSLParser`;
declaration and statement macros cannot be treated as scalar expressions.
Do not silently rewrite the authored source or claim a visual match.

### T6 — member selection on a parenthesized expression (1 preset)

`suksma - crisco orgy - rosvell roams nz+.milk`, warp, uses nested coordinate
expressions with `.xyy` and `.xyz`. With the required built-in blur descriptor
context supplied, the native translator rejects near `'.'`. Minimal control
`ret=(float3(1,2,3)*2).xyy;` rejects, while direct constructor member selection
`ret=float3(1,2,3).xyy;` translates. Materializing the constructor and parenthesized
coordinate expression into locals before applying the same swizzles makes the
full diagnostic copy translate. Inspect postfix/member parsing after a closing
parenthesis in `HLSLParser`; retain type checking and repeated-component swizzles.
Do not mistake missing adapter blur declarations for this second, real failure.

### Exact current parser witnesses

| Issue | Exact preset filename | SHA-256 | Section |
|---|---|---|---|
| T4 | EVET + Flexi - Rainbox Splash Poolz.milk | `be239e68191d98dc976e8bf3c1551162f7bf98b058f218f92e4f1800dbaaefdf` | composite |
| T4 | EVET - Brainsplolz.milk | `ca7f632030a524c044bcf6b3387fe97a3b28f72edaa9ef93988b036ac5ff0a31` | composite |
| T5 | Fed + Geiss - Color Pox Remix.milk | `acae4b876741a1fa0962a8894633bca09c6e22c27b367945de3825f5dfebf2d1` | warp |
| T4 | Flexi - dimension window.milk | `ca23e254c3bea2a8e59fc07fec1ddc993a9fada9469c2c0f2557610fc5b1016d` | composite |
| T4 | Flexi - ianus portal.milk | `c6f7140722af728dedd6630659fd3e940634880d7c095386a28caa051d4028ef` | composite |
| T4 | Flexi - madness portal.milk | `e02d91b828f75316042cade88768cdbe962e59a35ca6281eac1b50a71f8a5e4e` | composite |
| T4 | Flexi - rorschach bomb.milk | `ea5c6343586c38d7b77cb1f92d69e91b3cb8fe6ec1c24f8a61fc896830e58801` | composite |
| T4 | Flexi - spirally caterpillar coop mode.milk | `83a21c74a7affda7c9ed85da05fc652b988b22eb2596a394e78e5ec86f84dd22` | composite |
| T4 | Flexi - spirally repetative 2.milk | `a0e1f244b13156627e3df8b50db2f47e67e7e3b4ce2571b5cb464f2a470417bd` | composite |
| T4 | Flexi - truly soft piece of software - topology - cohere perfectly normal people stopped functioning.milk | `249b57cb667831ef86d09fda33c3c7c35a74d3f818cfa916bd47e8d718c75233` | composite |
| T4 | Flexi - truly soft piece of software - topology - cohere.milk | `a6dd160c7fd71b64707bb25724bee5645a87bc75e3436766b665966a19034362` | composite |
| T4 | Flexi, Geiss and Rovastar - tokamak, the ultimate plasma torus.milk | `12064864d58f8337ca1ede72f20ce2ead38a1a591c75cf810cdcbed167db670b` | composite |
| T4 | Hexcollie - Hedgehog dreams.milk | `9b7d343de88e5a59363152b2161ae4aa98d8b4f323eb4cdd0fdb91374f3887c7` | composite |
| T4 | lice - veritubule.milk | `fd1e37383cb6c78a6d1eb906ca7982db7fc0d69d8b891f71be259341029c481b` | composite |
| T6 | suksma - crisco orgy - rosvell roams nz+.milk | `f99c8383eb1010a257c9188776b734edf6438c307a72f777f442b5479aad61b6` | warp |
| T4 | suksma - fuck retro anything.milk | `d57fea66d8addb123af5327e19d7410ed923d0a64416b448fee2458510730883` | composite |


## Remaining read-before-write cases (5 presets; not all confirmed native bugs)

These require separate attribution from T4–T6. Do not initialize arbitrary shader
storage to zero to clear a diagnostic. The current typed lowering traces the
following authored storage into reads. A successful baseline render or repeat
does not prove the value is defined. Exact source hashes and read-only baseline
joins are in `fixtures/remaining-uninitialized-5-2026-10-04.json`.

| Exact preset filename | Storage | Investigation |
|---|---|---|
| New Creation Sensation -  AdamFx,Flexi,Amandio c n Martin - Star to Another World ft Hexocollie,ShadowH,Geiss Bewitchcrafted A.milk | local `arg` | Prove incoming q29/default and selector range before concluding an unassigned path is reachable |
| martin - ludicrous speed.milk | local `arg` | Prove nonnegative index4 recurrence across init/frame updates and native conversion/remainder domains |
| Serge + martin - crystal palace tunnel003.milk | global `mus` | Added to crisp/dots without a prior assignment; determine legacy external/global default versus translated GLSL storage |
| martin - mandelbox explorer - wreck diver nz+ liquititty.milk | global `dist_c` | Used in focus before its later assignment in the entry function; a later assignment cannot initialize an earlier read |
| martin - organic light.milk | global `uv3` | Reads its old value in `uv3=.4*cos(42*uv3)+64*dz`; distinguish per-invocation shader storage from feedback texture persistence |

The two `arg` shaders cover k1 values 0–3, where k1 is `int(q29)%4`.
A finite nonnegative input proves branch exhaustiveness; without an input/domain
proof, guessing that negative or non-finite values never occur would hide a gap.
The ludicrous-speed source initializes index4 using `rand(12)` and updates it
modulo 8 before binding q29. The New Creation source has no EEL mention of q29;
component-level untouched-Q inference is a potential analyzer improvement, since
another component in its packed bank prevents the existing whole-bank proof.

The supplied MilkDrop3 source compiles with D3DX and binds named known constants;
source inspection alone has not yet established a matching current-core zero
policy for these three uninitialized globals. Preserve uncertainty pending a
versioned translator/default policy and corresponding native numerical controls.


### Component-default follow-up

The component-level untouched-Q rule now clears the New Creation `arg` case:
q29 is absent from selected main equation trees and native initialization is zero,
so k1=0 selects an initializing branch. Other packed-bank components remain
symbolic. This is an analyzer input-context correction, not a native translator
patch. The remaining source-gap count is **26**; the other four read-before-write
cases above remain unresolved. See
`fixtures/focused-blockers-26-partial-q-2026-10-04.json`.
