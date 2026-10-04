# ProjectM TV core: native evaluator/loading engineering handoff

Date: 2026-10-04. Task: reconcile MilkDrop numbered equation records with our native loader/evaluator. The source-reader’s own parser results must remain separate from actual AAR load outcomes.

## Resolution update

[PR #27](https://github.com/johnneerdael/ProjectM-TV/pull/27) is merged at
`f435dd7c58ea1f16d9d182ecfc5632b77f5b6f98`. Patches0033–0035 extend retry to all
equation phases, add lone-dot numeric compatibility and preserve preset loading
when a defective block is omitted with a warning. Its reported corpus result is
9,600 clean loads and6 warning-only loads, with zero failed loads. Do not treat
the historical27 remaining failures below as current release failures or ask an
engineer to reimplement these fixes. The analyzer's35-patch source snapshot is
built; selected-assembly and omission-policy adoption remain in progress.

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

## Priority and already-shipped correction

The historical 66 native equation rejections divide into 53 programs accepted after MilkDrop line/comment assembly and 13 programs rejected by the same evaluator in both forms.

**Core 2.2.6 already ships [patch 0029](https://github.com/johnneerdael/ProjectM-TV/blob/v2.2.6/tools/projectm-patches/0029-per-frame-record-compatibility.patch).** It retries legacy assembly in `PerFrameContext::CompilePerFrameCode` only after the original per-frame program fails. Of our 53 witnesses,39 are `per_frame_` and are candidates for that existing fix. Revalidate these; do not ask another engineer to reimplement patch 0029.

The other 14 witnesses are 8 `per_frame_init_` and 6 `per_pixel_`. Patch 0029 does not change those compilation entry points. Extending compatibility safely across the remaining phases is the main actionable loader issue.

These are historical source-bound results from our 2.2.4-era CPU adapter, not proof that all 66 remain rejected by core 2.2.6. Our adapter’s direct raw evaluator check does not invoke the new retry wrapper; update that instrumentation before using its old counts to describe current AAR loading.

## E1 — consistent legacy record assembly across loading phases

**Observed difference:** MilkDrop’s `ReadCode` plus `StripLinefeedCharsAndComments` removes numbered-record separator characters and strips `//` and double-backslash line comments. Our earlier loader preserved LF boundaries and fed those directly to the evaluator. Split identifiers and numeric literals can then become invalid tokens or different programs.

Minimal reproduction:

```ini
per_frame_1=is_beat=2;
per_frame_2=q1=is_
per_frame_3=beat;
```

The raw evaluator rejects the split identifier. MilkDrop assembly produces `q1=is_beat;`. Current patch 0029 supplies the retry for per-frame code; analogous failures in init/per-pixel remain outside its scope.

**Expected repair direction:** share a well-defined compatibility assembler across the appropriate loader phases, retry only after raw compilation fails, and preserve already-accepted program behavior. Remove record boundaries after handling line comments; do not invent spaces, append semicolons or rewrite preset files. Check CR/LF handling and comments explicitly. Decide phase coverage from production loader calls, not from whether a custom wave/shape is enabled.

**Code locations:** `src/libprojectM/MilkdropPreset/{PerFrameContext,PerPixelContext,WaveformPerFrameContext,WaveformPerPointContext,ShapePerFrameContext}.cpp`, `PresetFileParser::GetCode`, and the native evaluator wrappers. Reference implementation: user-provided `MilkDrop3/code/vis_milk2/state.cpp`, `ReadCode` and `StripLinefeedCharsAndComments`. Its prose comment mentioning replacement spaces differs from its executable separator-removal body.

**Regression requirements:** split identifiers, split decimal/exponent literals, both line-comment forms, CR/LF variants, empty/comment-only records, accepted raw programs, genuine invalid syntax and retained error locations. Test each compilation phase independently, including disabled components: the pinned loader compiles their code and can abort initialization even if they do not draw.

### E1 affected presets — 53 historical witnesses

Status column: **existing retry** means section is covered by patch 0029’s per-frame path; **outside retry** means init/per-pixel and needs investigation/extension. This is source inspection of patch scope, not a complete 2.2.6 runtime pass.

| Preset | Source SHA-256 | Section | Patch 0029 coverage |
|---|---|---|---|
| 161.milk | `abc94b9d0ea3820eb8f08aaf6061511146da51014f43d3f1ba8ddc7a2cfc224b` | `per_frame_` | existing retry — revalidate |
| 2009 4th of July with AdamFX n Martin - into the fireworks E.milk | `d526e7d69f3948fe37482aff9dbe0047e0c029b590a8f35c52e3e81a473da763` | `per_frame_` | existing retry — revalidate |
| 430.milk | `a1cec1b62bf14f0792d46ac20716cbb78608a367894e3cf8baa961c65f0d9e63` | `per_frame_` | existing retry — revalidate |
| A Tribute to Martin - bombyx mori - Ft Flexi - AdamFX - StahlRegen - Hd In Milk Ailen FX P.milk | `10aac1bcf86b1b7c5ed94adab8b422de2fce9559f13b0a12008a3a7f672ee9e6` | `per_frame_` | existing retry — revalidate |
| Adam Eatit Mashup FX 2 martin - disco mix + Lodus + Geiss + Fruits Machine .milk | `5f985a4495b0c413df0d8965d8b3a64e22b89a005669ecea9fa8cf3b31651df1` | `per_frame_` | existing retry — revalidate |
| AdamFX Enterz Tha Mash With Martin + stahlregen - AdamFX - In Tha Mash Effectz .milk | `d47f1195105b7b7a618c30f29796b3a6853547433e669b50c43c5c874a1061ed` | `per_frame_` | existing retry — revalidate |
| AdamFX Enterz Tha Mash With Martin + stahlregen - AdamFX - In Tha Mash Effectz A.milk | `3954f2b4c566a193350b6da400eed11819d949e6cf29fa78ed241e3179774290` | `per_frame_` | existing retry — revalidate |
| AdamFX Enterz Tha Mash With Martin + stahlregen - AdamFX - In Tha Mash Effectz B.milk | `9787a2a09f7257a53a74cb1246282dd3a20dfd2f4310bc3f7b6b1435d27240a4` | `per_frame_` | existing retry — revalidate |
| AdamFX Enterz Tha Mash With Martin + stahlregen - AdamFX - In Tha Mash Effectz nz splatter bare.milk | `c473fed44a3de5a27c0fe10a97c7476461497f965905228218be34efcb2163f0` | `per_frame_` | existing retry — revalidate |
| AdamFX Enterz Tha Mash With Martin + stahlregen - AdamFX - In Tha Mash Effectz nz splatter.milk | `49e9f79c4357c2786e0c75daf99968e1f1defdd3b55dfdf745a29c958ca47a7a` | `per_frame_` | existing retry — revalidate |
| Bdrv Aderrasi - Chromatic Voyage bdrv etAL.milk | `8645c091f2282ef67856abec768036fdb17580917e98d59e167f4e55bec0fa43` | `per_pixel_` | outside retry — extend/investigate |
| EVET - Hypraxis.milk | `61fdb1019e0a02884dd3aae0737f723bfe8c3a2c9c453249dd7bd4d1b50f9d2c` | `per_frame_` | existing retry — revalidate |
| EoS + Redi Jedi - frequency analysis + glowsticks -  glow - o - scope female (Milkdrop beta ver).milk | `f1f2431f6db132e6da6b9a3b799c53809f274d3cf1012e35907d06e57cca819b` | `per_frame_init_` | outside retry — extend/investigate |
| EoS + Redi Jedi - frequency analysis + glowsticks -  glow - o - scope male (Milkdrop beta ver).milk | `7581d5fd243f07c05761b61b3bef1782ed83d9f94983aca23e27df5783325e14` | `per_frame_init_` | outside retry — extend/investigate |
| EoS + Redi Jedi - frequency analysis + glowsticks -  glow - o - scope pat (Milkdrop beta ver).milk | `129ff8d6d5b5acf72931e1a02dccf6df4d0646fdaef2f296b40325677973558a` | `per_frame_init_` | outside retry — extend/investigate |
| EoS + Redi Jedi - frequency analysis + glowsticks - demon's dream (Milkdrop beta ver).milk | `8cac947e4b3a174b0e4737eabc29fecd5b68882fafe9ffb379a63590d94d0c69` | `per_frame_init_` | outside retry — extend/investigate |
| EoS + Redi Jedi - frequency analysis + glowsticks - long armed raver (Milkdrop beta ver).milk | `cb4419a9b253fa56c93504144010fc7c7eecb9b0c92930289620637827bc898f` | `per_frame_init_` | outside retry — extend/investigate |
| EoS - sectorLoc B_phat_ugly remix 01 EoS7p nz+ crab lardvae.milk | `4026209d29ea95435d0398f7bf5b58756c51dd9e2de70eaa2dbc99fbdfc17b6d` | `per_frame_` | existing retry — revalidate |
| Goody's Datura Bloom.milk | `54a41dd9c3a93e4912bab58418912b60c75f4e1428a4aa8b71711cacae12e3cd` | `per_pixel_` | outside retry — extend/investigate |
| Halfbreak - EFFECTAMT 4PORT (Seizure Techno).milk | `3b2e6bd3ab0f1e85dccab2551438a769d9e1984a7d1a87b2b7d139bd14d2e8fd` | `per_frame_` | existing retry — revalidate |
| Idiot24-7-mindbender7(superbendmix1).milk | `15aef727b786aa21601ec7fd341c7b9e580fbff254e2883c68443baeebb6d339` | `per_pixel_` | outside retry — extend/investigate |
| Liquid Glowsticks - ATwisted Pre Set Mix By AdamFX 2 martin - disco mix Ft Hexocollie 27.milk | `4da3fdb54c995d3a222340bc708ec3b44f6d9cab4f9903eae222feb2926ee788` | `per_frame_` | existing retry — revalidate |
| LuxXx - A Sober Life (wasted).milk | `ad1d4a2c1df3f223d7c018206d71e958ccb65dfae6a06eb1f9eb84c6c0bd099e` | `per_frame_` | existing retry — revalidate |
| LuxXx - All That I Am.milk | `f60b1f1839f202811701c6d9b8184c415207bd2250d3efccad7492aae2619a85` | `per_pixel_` | outside retry — extend/investigate |
| LuxXx - Beat Machina III.milk | `e10e8083d95d65324c4d23ca660871960483cc6a2fb0d5b57f733e2d2fc9d8d3` | `per_pixel_` | outside retry — extend/investigate |
| LuxXx - Burnwheel I.milk | `4072df6bbd14e058beb781afe8472d88c2b72072649a7534987d329e137bd10e` | `per_frame_` | existing retry — revalidate |
| LuxXx - Fuck ur Fractal Muscles II.milk | `3c68f3ff8f902a55a189ec4ea2b08583b298d2499390d7d3e5b69c7f67c7c284` | `per_frame_` | existing retry — revalidate |
| LuxXx - electric cell park a.milk | `0e7c9add23496dd64455ab4117cf5c524bb7a2ed8d4ad32d588352ed04ba6580` | `per_frame_` | existing retry — revalidate |
| LuxXx - electric cell park b nz+.milk | `4c42076ffa0d011269691add9f3d86171902a8dd1807fb8c8938cad313b143a0` | `per_frame_` | existing retry — revalidate |
| LuxXx - electric cell park b.milk | `39fe5c98aec5833051becc4daded6e159d53d386fe20353738cdf4d4e23d0954` | `per_frame_` | existing retry — revalidate |
| Milk Artist At our Best - FED - SlowFast Ft AdamFX n Martin - HD CosmoFX Also Ft Mstress n Armandio  - Thought About YouFX.milk | `ae6547209756c79a3b3b17e9ab78997fd9257b5f9805eca25a67de1be31bcc61` | `per_frame_` | existing retry — revalidate |
| ORB - Toy Snakes Starry Night.milk | `5808eea5bb3e78e87f9d7a9cef09a0f7c315d73f80ad0c43e611f02b5bb0447c` | `per_frame_init_` | outside retry — extend/investigate |
| Rarian Rakista - On the Water.milk | `bef0955dbaee656bebceeb9b784500271572693ba2908d1c7b59d4d7ec365434` | `per_frame_` | existing retry — revalidate |
| Rozzor & Neuro - Starover (Semicolon Mix).milk | `cfc114ebac787513cd136d9716391c2164191c6ff8cfcbc348ee94b2074a63dc` | `per_frame_` | existing retry — revalidate |
| Starz in MilkHDFX - Stahlregen & Aderrasi + EoS + Geiss + Unchained + Zylot + Flexi + Martin + AdamFX A.milk | `821693b322e1767360505cef09654778dcdcd334462133d8915ed98f542bcf73` | `per_frame_` | existing retry — revalidate |
| Zylot & Idiot24-7 - Unknown Power Source.milk | `93ba841ab75cba25a94ee1b073fb79ee761113360cf0aad4f84dda546b3a619f` | `per_pixel_` | outside retry — extend/investigate |
| all death angel watch Erd 3y3 mBetraeqx.milk | `661e494948cc529ff91c5c1292214a8f58dbccd1763ab4450a99c45c0a1ba26a` | `per_frame_init_` | outside retry — extend/investigate |
| martin + stahlregen - martin in da mash 12a.milk | `5d351b29598f9ab9f4090be14356866fd07871559bcaebd8fa6994cf28947d9b` | `per_frame_` | existing retry — revalidate |
| martin + stahlregen - martin in da mash 12b.milk | `290dedb0d6166755779a138cdde332a5078a8392210eb08c1a43198f031146e1` | `per_frame_` | existing retry — revalidate |
| martin + stahlregen - martin in da mash 13.milk | `428dbb6315a9709952964b92a9b6483dc390cb1ab57af1e8218094da07454623` | `per_frame_` | existing retry — revalidate |
| martin - purple pulsator - mom - ns2w nz.milk | `523ca37b2804c315a67fe45dd474b870f48f0083abde7deaa00d44ca2644b2eb` | `per_frame_` | existing retry — revalidate |
| martin - purple pulsator - mom - ns2w.milk | `b485a6c83f9a8ee908f4e1d63c524255b8c8b70d37384aec35cde12576297dc0` | `per_frame_` | existing retry — revalidate |
| martin - purple pulsator nz+.milk | `3274fe069d7cffd4ea17fbae4ac0b900423abf61674ad5141863579459c78402` | `per_frame_` | existing retry — revalidate |
| martin - purple pulsator.milk | `11459b5cf4b250c8b9d51225cd8d4aa102f7c51b4904de7b6624bc8aee0f3815` | `per_frame_` | existing retry — revalidate |
| martin - sparky caleidoscope.milk | `9ef89f10346e0b06d5f570513dfb088e6c5cd116fee26a10bf43f283fd630750` | `per_frame_` | existing retry — revalidate |
| suksma - Hexcollie - Julian Carnival - shimmy dumb grid dogmaklyasm nz+5.milk | `549accc0164b9b6bca92c54af71ecd990cd35ebfa7c397b96f3f341cd410478c` | `per_frame_` | existing retry — revalidate |
| suksma - Hexcollie - Julian Carnival - shimmy dumb grid dogmaklyasm nz+6.milk | `193ac4c7b6257e9570b28e0f25bd16cbfe61819f1e4add2686d4a71352e8c3fe` | `per_frame_` | existing retry — revalidate |
| suksma - dicked.milk | `be873c0f864738e254f8a90f707466751740ae91ddf8d38b4482802e0029e42f` | `per_frame_init_` | outside retry — extend/investigate |
| there is gum stuck to my hate.milk | `41b71270aea8799680b79378bd8c3a6e7893b901aafde91bfff6ca057a07ff64` | `per_frame_` | existing retry — revalidate |
| va ultramix - 290_3.milk | `bf5e8c435d0032ccc40caf88eddab658f0d536bd61364a7791bee16004e5390b` | `per_frame_` | existing retry — revalidate |
| va ultramix2 - 532_2.milk | `97af8c946901213d1b2f7aa88c679d0129589372bb30bcd239496d0a4f51b470` | `per_frame_` | existing retry — revalidate |
| va ultramix2 - 533_1.milk | `bf6b095f2d6a6c8ac3b893475ea82eb8b94f20200abea0ce2c628c0af22978e4` | `per_frame_` | existing retry — revalidate |
| va ultramix2 - 534.milk | `765028fc69780859a2ad2ca0ceac25fe7c415c49d9a987f7ce9ae6c2a7fcaf66` | `per_frame_` | existing retry — revalidate |

## E2 — thirteen other rejections require diagnosis, not automatic repair

Both the raw and legacy-assembled forms fail the native evaluator in these 13 historical cases. Some contain suspicious literals/operators. That does **not** prove the author’s file is invalid in official MilkDrop/NSEEL; it could still expose dialect incompatibility. Do not silently sanitize the input or call this a confirmed evaluator defect without an official-reference or source-based reproduction.

Use the exact compiler message, loaded code and physical line in the diagnostic fixture. Compare official MilkDrop/NSEEL acceptance and behavior where needed. Classify each as source defect, unsupported dialect, phase-loader mismatch or evaluator bug before proposing a fix.

### E2 affected presets — 13 triage cases

| Preset | Source SHA-256 | Section | Native diagnostic / file line |
|---|---|---|---|
| EoS_Phat_PeterP_Sentinel_Aware_6 EoS edit C.milk | `3d30b54a6ac7e3e01062e4bfaab4e9e8013fdd8f376cd56dc1dfb7fb6d03d882` | `shape_0_per_frame` | syntax error, unexpected VAR; line 505 |
| EoS_Phat_PeterP_Sentinel_Aware_6 EoS edit C_b.milk | `5dc95c5a9f8e7bd0b8d015c3b6cfcea6c54926c1c574dc01f2549a3aa0aeed58` | `shape_0_per_frame` | syntax error, unexpected VAR; line 505 |
| EoS_Phat_PeterP_Sentinel_Aware_6 EoS edit slice into your beautiful love.milk | `591567f0029068f4f1f7ec3b50d7a8fabd8c1658ece6c981a7f60cfd6f3317ea` | `shape_0_per_frame` | syntax error, unexpected VAR; line 517 |
| Hexcollie - Ultra daze.milk | `fc6ff5d5591868ae366b619230a5533479913bf0a55f118bdacd7442a558c147` | `per_frame_init_` | syntax error, unexpected end of file; EOF; physical line unavailable |
| LuxXx - Brain Grind i.milk | `2068f26f9e312c7a98b3fb5d1fb4e28005bf36e97ee877c7b8982b13edc63aa3` | `per_pixel_` | syntax error, unexpected '*', expecting '('; line 373 |
| Stahlregen - funky Blur (lotus mix) the genius in me lies right at the heart of the flacc nz+.milk | `8f3b1f942e7ce9bbb1b85aed22188550fae2c0a3427ede79726bc7af468dc84f` | `per_pixel_` | syntax error, unexpected invalid token; line 332 |
| Stahlregen - funky Blur (lotus mix) the genius in me lies right at the heart of the flacc.milk | `02916538c0e5dd5bdb866f6ecf79ab510f68884218b26444459d3304dcb4657c` | `per_pixel_` | syntax error, unexpected invalid token; line 315 |
| amandio c - codex 4 - cabasal dandelioness nz+wp2.milk | `08f76b88828a54b296aa126bc5652c55c45d8acb7c1f1ea5748c3367b26e84ef` | `shape_0_per_frame` | syntax error, unexpected invalid token; line 177 |
| amandio c - codex 4 - cabasal dandelioness nz+wp3.milk | `dc104ae6119f0807817f8024921585fb82db1d3679aa9fb014cf872a60e84c1a` | `shape_0_per_frame` | syntax error, unexpected invalid token; line 177 |
| amandio c - codex 4 - plot wag nz+ necrophors gadget lard.milk | `0e46602e0347aba8356999918287dce07178d6a514dd1c78b6e2a1a6ca6dcc4e` | `shape_0_per_frame` | syntax error, unexpected invalid token; line 177 |
| martin - beamer code 22h - lines - rhythmic and fast.milk | `a3e3024d243ba980583ead6bea44f1afd2d8dd7d1abaf7adc92dea11199b836f` | `per_frame_` | syntax error, unexpected '*'; line 434 |
| more breedre presets.milk | `eb9f26d612212b99d40c4feec3d064d10a20ad2d5b82a43e548fb42d77e739c4` | `shape_0_per_frame` | syntax error, unexpected invalid token; line 177 |
| sonar cow.milk | `289a57aea3b7bde6324a98596ee5f4178dc4a6da9dd831c1fafb7ee5c500861d` | `shape_1_per_frame` | syntax error, unexpected end of file; EOF; physical line unavailable |

## Failure handling and evidence

A native equation compilation failure throws during preset initialization. Shader fallback cannot rescue it. The analyzer now refuses a source pipeline with explicit native equation rejection, preventing a false “calm” prediction from a preset that never loaded. Missing rejection metadata is not proof of success; version the loader policy and artifacts.

- `fixtures/focused-parsing-diagnostics-2026-10-04.json`: exact 66 equation witnesses,16 separate shader-reader parsing gaps, raw/assembled statuses, compiler line/column diagnostics and source hashes.
- All 42 exact-source matches for the 66 equation rejections in the saved 2.2.4-era shared baseline failed to load; none succeeded in that snapshot. The generic baseline error alone does not prove the precise cause.
- Shared baseline, read-only: `.worktrees/quad-lines-follow-ups/build/follow-ups/core-corpus/measurements-core-emu-baseline-v1/`. Match name, source hash, core identity, protocol and owner epoch. Do not stop or restart the other agent’s run and do not rerender the full collection.
- The 2.2.6 patch diff also includes patch 0027 for preserving exception diagnostics. Retain its `what()` fix; investigate actual errors rather than treating an empty historical failure message as shader incompatibility.

## Acceptance and reporting

The analyzer now exposes an explicit `projectmtv-core-2.2.6-v1` equation-loader
policy. A source-matched audit of the original 315 witnesses resolves all 39
per-frame cases listed above, reducing the audit from 217 to 178. Two frozen
synthetic retry/raw-preservation controls matched the published 2.2.6 native
library across 60 RGB8 frames with zero error. This is not a full runtime pass of
the 39 named presets and does not clear the 14 other-phase witnesses or the 13
triage cases. The shader CPU adapter still has a historical engine identity.
See `fixtures/focused-blockers-178-2026-10-04.json` and
`fixtures/equation-policy-core-2.2.6-proof.json`.

Reproduce against published core 2.2.6 first. Keep raw evaluator status, loader retry status, selected assembly and final preset-load outcome separate. Verify exact source hashes and AAR/native-library identity in each result. Fix only the missing behavior, rerun the affected named presets plus negative controls, and report which entries actually change. Update analyzer target-loader policy accordingly. Preserve the historical 2.2.4 evidence instead of relabeling it as current-release results.
