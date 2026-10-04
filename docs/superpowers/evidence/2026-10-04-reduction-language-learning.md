# Reduction semantics and shader interactions

Continue language and interaction work independently of the shared rendered
corpus. The user explicitly authorized isolated Android emulator checks where
native behavior needs validation. No corpus completion is a prerequisite for
these targeted mathematical investigations.

## What was learned

The gap labelled `nonterminal shader helper return not lowered: all` was not
evidence that these authors wrote early-return helpers. The data-only reader
injects standard HLSL declarations for `all`, because the pinned HLSL parser
lacks that intrinsic. Their bodies are empty. The lowering model incorrectly
treated the synthetic declarations as authored helper implementations.

The same adapter also injected `any` declarations even though the pinned parser
already declares that intrinsic. This produced parse failures on focused valid
`any` examples. Only `all` now receives the language-extension declarations.

The lowerer accepts synthetic reduction semantics only when the section carries
the reader's explicit `language_extensions` provenance. Real helper bodies and
untagged empty declarations retain their original handling. A caller cannot
infer standard semantics merely from a function name. Genuine early returns
remain a separate unresolved feature.

## Calculations and interaction evidence

`all` is true when every component is nonzero; `any` is true when at least one
component is nonzero. Scalar, vector and matrix reductions preserve this rule
without normalization. Grid evaluation reduces components within each pixel,
not across pixels. Negative nonzero components count as true.

Fixtures verify scalar/grid agreement, independent pixel lanes, zeros within
matrices, a real helper named `all` returning false, and missing provenance.
A composed field test uses the reduction to divide warp feedback into black
and white regions, then samples that feedback in the composite stage. It also
checks the half-intensity boundary columns produced by wrapped bilinear sampling
at the declared composite coordinates. This tests an interaction rather than
only an isolated function name.

The source pipeline carries extension provenance separately for warp and
composite, and the source audit uses the same binding rules.

## Measured impact and limits

Reparsed 176 presets selected from the previous `all` and unavailable-parser
gap witnesses with the rebuilt reader. No previously unparsed corpus section
became parsed in this selected set. All 27 shader sections previously blocked
by the synthetic `all` binding now lower completely. Do not extrapolate this
to a new whole-corpus behavioral percentage.

The minimal `all(uv)` and numeric `any(uv)` shaders were separately checked
against the pinned translator and offline GLSL330/GLES300 compiler profiles.
All four checks reject those examples. Language-level understanding must not
be confused with native shader acceptance: stage selection still uses separate,
source-bound compiler evidence and models fallback conditionally on that profile.
No emulator rendering or appearance accuracy claim was required for this step.

Full evidence, source/binary identities and compiler diagnostics are retained in
`tools/milk-analyzer/fixtures/reduction-binding-proof-2026-10-04.json`.
The complete analyzer suite passes 544 tests and 33 subtests.
