# Sampler declarations, reference lookup and fallback

This investigation distinguishes language-level sampler declarations from the
behavior of the pinned projectM translator and unchanged published core 2.2.4.
No native renderer or production preset was patched.

## Two runtime constraints learned

The native preprocessing code removes sampler-state assignments from a
comment-stripped working string, then uses the resulting `shader_body` offset
to replace text in the original string. When a real block precedes the entry
point, the offsets disagree and can corrupt the generated shader. Checking
all 51 recorded sampler-state witnesses against the pinned GLES300 path yielded
51 rejections and zero accepted/unknown results. These are not 51 merely missing
calculations in executable native shader stages.

A local one-line declaration can survive preprocessing by being stripped before
GLSL translation. Native reference lookup is a separate constraint: its sampler
identifier delimiter set omits `=`. `sampler_main=sampler_state` is therefore
scanned as the malformed resource name `main=sampler_state`. A checker that uses
only AST identifier names can falsely predict acceptance. Spacing around `=`
avoids this malformed reference in the tested local declaration.

`generate_shader_adapter.py` now copies the native `GetReferencedSamplers` and
blur-requirement update bodies as well as preprocessing/translation. The data-only
bridge records the actual referenced names and their source-body fingerprint.
Malformed names that cannot form native descriptor identifiers are rejected
before a false acceptance can feed the source forecast. The original native
code is unchanged; this additional check supplies a rejection conclusion, not
an exact texture-loading or RNG event trace.

Old source/archive-matching proofs can contain false-positive acceptance from
the previous AST-only adapter. Accepted sampler-state stages therefore also
require the reference-body fingerprint, translated status and valid referenced
names. Missing scanner provenance leaves stage selection unknown; old proofs
must be regenerated before enabling state replacement.

## Accepted bindings and ignored directives

The numerical lowerer can replace sampler-state initialization with an explicitly
supplied native sampler input. This context is not inferred just from the
declaration. `SourcePipeline.from_source` supplies it only for a custom stage
selected by source-matched compatibility evidence. Rejected stages take the
existing fixed-warp/default-composite paths instead of executing authored code.

For accepted native bindings, texture names and their qualifiers determine
filtering/wrapping. The authored state values are retained as ignored-source
metadata. A local `sampler_main` with `CLAMP` still wraps under the tested
composite binding; `sampler_fc_main` clamps despite a declared `WRAP`. Named
random/external textures still require explicit material inputs; this change
does not fabricate a selected texture or its pixels.

## Prediction and native observations

Two initial local-declaration forecasts failed on the owned API34 emulator.
They predicted a uniform texture query but the published core displayed the
warp gradient through fallback. A separate global-state rejection correctly
predicted the passthrough colour with zero RGB8 error.

Controls without state declarations showed that the texture query itself worked.
The mismatch led to the native reference-scan omission described above. The
failed forecasts/captures remain preserved in
`fixtures/sampler-state-native-proof-2026-10-04.json` and the local evidence
directory; they are not recategorized as passes.

Two new sources with correctly delimited local declarations were predicted
before observation. All 30 frames matched with zero RGB8 error:

- `sampler_main` returned `[64,64,191,255]` after wrapping the gradient query.
- `sampler_fc_main` returned `[254,64,191,255]` from the clamped edge.

Those records are separate in `fixtures/sampler-state-spaced-native-proof.json`.
The 51-section compatibility summary is in
`fixtures/sampler-state-corpus-compatibility.json`; full diagnostics remain in
the build evidence directory. Tests cover explicit/absent native context,
name-based policy, source-bound accepted-stage integration, rejection fallback
and malformed native identifiers, including refusal of old acceptance proofs.
The full suite passes 592 tests/33 subtests.

These checks establish the tested declaration/binding/fallback cases under this
profile. They do not establish complete visual prediction or a mood-classification
accuracy percentage. Texture-loading failures and native-driver differences
remain separate acceptance conditions.
