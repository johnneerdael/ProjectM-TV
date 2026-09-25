# Third-party content

| Content | Source | License |
|---|---|---|
| projectM 4.1 libraries (`app/src/main/jniLibs`) | [projectM](https://github.com/projectM-visualizer/projectm) | LGPL 2.1 |
| Cream of the Crop presets (`app/src/main/assets/presets`) | [presets-cream-of-the-crop](https://github.com/projectM-visualizer/presets-cream-of-the-crop), curated by Jason Fletcher | See the repository's `LICENSE.md` |
| MilkDrop texture pack (`app/src/main/assets/textures`, 67 images) | [presets-milkdrop-texture-pack](https://github.com/projectM-visualizer/presets-milkdrop-texture-pack) at commit `6368812f27bc747b517218fbf89d21d59afce4d9`: textures originally released with MilkDrop plus community textures used by many presets | **No license file in the repository.** Its README says: "It is highly recommended including this texture pack in any projectM application that ships with bundled presets." Check with the projectM maintainers before distributing commercially. |
| 14 more textures (`app/src/main/assets/textures`: `rose`, `shub1`, `grad3`, `portal1`, `portal2`, `test`, `skull`, `plane`, `AbalonyStosich`, `Suff5`, `winamp_woofer`, `noise64`, `chloemall`, `chloemallCornerMask`) | "MilkDrop 135k+ Presets MegaPack 2026", collected by Incubo_ (Winamp forums), folder `textures/`. Referenced by 216 bundled presets and missing from the pack above. Five of them are byte-identical to the copies in SourceForge [mdpresetpack](https://sourceforge.net/projects/mdpresetpack/files/) (2019). `noise64`, `chloemall` and `chloemallCornerMask` are the MegaPack's PNG versions, not the DXT-compressed DDS files, which most Android TV GPUs cannot use. | **No license stated for the textures.** The MegaPack's `PRESET LICENSE.txt` covers only its ShaderToy-converted presets (CC-BY-NC-SA 3.0). |

`Nivush - Spiking Mandelbrot.milk` was removed: it was the only preset whose texture (`colors3`) could not be found. Every remaining preset now has all the textures it references.
