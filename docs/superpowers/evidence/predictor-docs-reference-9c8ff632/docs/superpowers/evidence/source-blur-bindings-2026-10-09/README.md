# Source-derived constant blur decoding inputs

Source GetBlur decoding multiplies raw samples by packed range scale/bias values.
Treating all of those inputs as unknown blocked constant-affine flow formulas,
even when their authored main-frame ranges are fixed. source_uniforms.py now
reuses the tested target blur.native_ranges CORE_2315_BLUR policy and derives
float32_c5/_c6 components only when all6main-frame fields are supported constants.
Any missing/dynamic/unsupported value withholds the entire triplet because a
later invalid level can trigger coherent default ranges for every level.

Source31 BlurTexture.cpp353–448 defines narrowing, close-gap repair, hierarchy
and normalization fallback. MilkdropShader.cpp234–241 packs_c5 as
[gap1,min1,gap2,min2] and_c6 as[gap3,min3,min1,max1]. Existing uniform-component
injection respects declarations/local shadows. A generic component-binding
annotation now names its actual source/context basis instead of falsely calling
blur components untouched-mainQ. observed_runtime_binding remainsfalse.

Original MilkDrop2.25c milkdropfs.cpp1551–1583 assigns both close-range endpoints
average-minus-half-gap. The patched TV library repairs this old bug and adds
unsupported-range guards. This change preserves patched target fidelity; it does
not restore the original bug or modify native/preset code. The original source
is an authored reference, not the target execution policy. Full published2.3.33
AAR/source31 identities remain the qualified reference.

Seven focused controls cover default ranges, frame overrides, dynamic-level
withholding, minimum-gap hierarchy, extreme finite fallback, init/frame resets
and lexical local shadowing. The local-shadow case preserves its authored
constructor DAG; the separate colour descriptor still leaves that member opaque
rather than inventing a constant palette. Independent correctness review checked
range arithmetic, lifecycle, triplet fallback and uniform-only injection.
The complete prepared analyzer suite passes2274tests and92subtests in
137.54seconds. Strict MkDocs and whitespace checks pass. Final independent
annotation/shadow/contract review has no findings and re-ran all7uniformcontrols.

Final same100originals:100computed,91source-constant blur bindings;9records have
no derived binding because no authored shader was lowered. Direct sampled-colour
coordinate-response coverage rises6→23presets and6→64maps. All prior descriptors
remain. Exact source/record/model hashes, safe/raw/packed values and the17newly
supported filenames are in census.json. Full coordinate programs remain in the
hash-bound raw batch. This is source extraction coverage, not visual accuracy,
whole-corpus fidelity, observed GPU binding or certified blur-history behaviour.
Mean per-preset source export.31006002s,sum31.006002s; no performance improvement
is claimed from this single timing checkpoint.

Paired raw source/JSON batch:
`build/preset-corpus/source-blur-bindings-final-2026-10-09/batch-000001.zip`

SHA256: `6cfa66e72e3dc9b403639d276ea6d667af6c97517cdbab3fe5d5830448de693d`.
ZIP CRC and all100 original source bytes/hash joins were verified. No audio/frame/
image execution, devices or shared corpus were used. No47numeric output changes.
Known blur inputs do not certify final palette, flow speed, mood fit or the user's
independently recognizable-look milestone. Those gates remain unmet.
