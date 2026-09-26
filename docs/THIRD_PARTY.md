# Third-party content

| Content | Source | License |
|---|---|---|
| projectM 4.1.7, built from source with the app: git submodule `third_party/projectm` at tag `v4.1.7` (commit `e0b0a967`, with projectm-eval as its own submodule), plus the patches in `tools/projectm-patches/` (upstream commit `0227b7a6`, plasma transition fix for NVIDIA SHIELD); linked statically into `libprojectmtv.so`. Up to 1.9.4 the app shipped a prebuilt master snapshot, commit `d89c09ef` (August 2025); 1.9.5 shipped prebuilt 4.1.7. | [projectM](https://github.com/projectM-visualizer/projectm) | LGPL 2.1 |
| Cream of the Crop presets (`app/src/main/assets/presets`) | [presets-cream-of-the-crop](https://github.com/projectM-visualizer/presets-cream-of-the-crop), curated by Jason Fletcher | CC0 1.0 as distributed by this project, see [Presets and textures](#presets-and-textures) |
| MilkDrop texture pack (`app/src/main/assets/textures`, 64 of its 67 images; `prayerwheel`, `VITRIOL` and `kaite` removed, see below) | [presets-milkdrop-texture-pack](https://github.com/projectM-visualizer/presets-milkdrop-texture-pack) at commit `6368812f27bc747b517218fbf89d21d59afce4d9`: textures originally released with MilkDrop plus community textures used by many presets | CC0 1.0 as distributed by this project, see [Presets and textures](#presets-and-textures). The upstream repository has no licence file; its README says: "It is highly recommended including this texture pack in any projectM application that ships with bundled presets." |
| 10 more textures (`app/src/main/assets/textures`: `rose`, `shub1`, `grad3`, `test`, `skull`, `plane`, `AbalonyStosich`, `noise64`, `chloemall`, `chloemallCornerMask`) | "MilkDrop 135k+ Presets MegaPack 2026", collected by Incubo_ (Winamp forums), folder `textures/`. Referenced by 206 bundled presets and missing from the pack above. `plane` and `AbalonyStosich` are byte-identical to the copies in SourceForge [mdpresetpack](https://sourceforge.net/projects/mdpresetpack/files/) (2019). `noise64`, `chloemall` and `chloemallCornerMask` are the MegaPack's PNG versions, not the DXT-compressed DDS files, which most Android TV GPUs cannot use. | CC0 1.0 as distributed by this project, see [Presets and textures](#presets-and-textures). The MegaPack states no licence for its textures; its `PRESET LICENSE.txt` covers only ShaderToy-converted presets, none of which are bundled. |

## Presets and textures

This project distributes the bundled presets (`app/src/main/assets/presets`) and textures (`app/src/main/assets/textures`) under **CC0 1.0 Universal** ([LICENSES/CC0-1.0.txt](../LICENSES/CC0-1.0.txt)): free for any use, without conditions.

- CC0 covers what this project holds: the selection and curation of the collection and any changes made to it (presets removed, textures converted from DDS to PNG).
- The individual presets and textures are the work of their authors, who released them freely over the past two decades. Like projectM, whose preset repository treats them as public domain, this project distributes them on that basis and does not claim rights in them.
- Authors who do not want their work included can open an issue in this repository; it will be removed.

## Removed content

`Nivush - Spiking Mandelbrot.milk` was removed: it was the only preset whose texture (`colors3`) could not be found. Every remaining preset now has all the textures it references.

Removed in 1.9 because they show text, logos or people: `Suff5`, `prayerwheel`, `winamp_woofer`, `VITRIOL`, `kaite`, `portal1`, `portal2`. The presets that used them were removed as well. `tools/check-presets.py` (run by CI) keeps them out.
