# Native composite hue colour ingredient

source_hue.py exports the engine's four-corner hue recipe when contributing
compositeRGB consumes _vDiffuse, including hue_shader. Generatorcode10 is a
separate native-colour dictionary, not an extension of familycodes. Red-only
consumption remains explicit, and alpha-only/source-dead/unused inputs or warp
vertex decay do not create a hue record. No fragment values are substituted into
the shader interpreter.

Source31 FinalComposite.cpp328–375 generates four cornerRGB signals using native
time, float32coefficients and preset random phases, normalizes each corner by
its maximum channel, then applies.5+.5ratio. PresetState.cpp25–28 chooses random
phases per presetinstance. Mesh vertices blend the four corners using their
position, after which the GPU interpolates triangles. Direct per-fragment
bilinear colour is not exact. PresetCompVertexShaderGlsl330.vert forwards vertex
colour and position. Original MilkDrop2.25c milkdropfs.cpp4408–4450 uses the same
corner signal/max-normalization construction.

The nominal[2/3,1]inputRGB range assumes finite valid phase inputs and omits native
rounding/interpolation. Random phasevalues and actualpalette remainnull; final
multicolour and observedbinding remainfalse. Powers, masks, permutations, textures
and history can change final colour/contrast. No flash, dominance, warmth/coldness
or wholelook certification is granted.

Eight hue controls pass, including exactfloat32coefficients, normalization/range,
red-only/alpha/dead/warp exclusions, independent nominal formula evaluation and
originalHueBurst.27hue/native-time/colour controls pass independently. Correctness
review has no findings. The complete prepared analyzer suite passes2301tests and
92subtests in135.57seconds. Strict MkDocs and whitespace checks pass.

Fixed100 originals:100computed,14presets now carry a consumed native-hue recipe,
all reading RGB in this sample. No earlier descriptor was lost. This measures
source ingredient coverage, not finalpalette, overall appearance or wholepack
accuracy. Source/record/modelhashes and recipes are in census.json; full source
records remain in the hash-bound paired batch. No image/audio/frame execution,
engine/preset edits, devices or shared corpus were used. The qualified full
published2.3.33AAR/source31 remains the target. Existing47numeric contract is
unchanged; the independently recognizable-look gate remains unmet.

Raw paired batch:
`build/preset-corpus/source-composite-hue-2026-10-10/batch-000001.zip`

SHA256: `dd911342d115f387beb7cbcb8f7fa2807ad7d0d6382d86a1d70f2eb618dd132e`.
ZIP CRC and all100original source bytes/hash joins were verified. Mean per-preset
source export.30718215s,sum30.718215s; no performance claim is inferred.
