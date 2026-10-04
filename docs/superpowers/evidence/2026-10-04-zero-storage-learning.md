# Literal zero and plain uninitialized storage

All 39 source-audit rs origins contain an explicit 0*rs term. The target GLSL
generator does not emit a plain multiply: its scalar mult0 helper returns 0.0
when either argument is zero; vector helpers apply that rule per component.
Whole-matrix helpers instead use matrix multiplication and are excluded.

The interpreter previously rejected the unwritten rs value before applying that
generated rule. It now recognizes literal-zero products only when the other AST
operand is a plain variable/member and its graph contains unwritten storage plus
only simple storage/components/casts/constants. The resulting product is zero;
the underlying variable stays unwritten. This is a pinned generated-helper rule,
not a general assumption that zero hides every unknown expression.

Helpers, textures, indices, external inputs, branch-dependent graphs and whole
matrix products are not discarded by this rule. Existing missing-input/texture
checks remain in place. Tests cover both operand orders, swizzles, scalar/vector
storage, partly written constant components, later live reads, array bounds,
missing inputs and preservation of shared helper updates.

All 39 targeted original source sections now lower completely. Two predictions
were frozen before native capture against unchanged published core2.2.4 on the
owned API34 emulator: .25+0*global_rs and .25+local_rs*0, with the specified RGB
constructor, both yield [.25,.25,.75]. All 30 frames each match with zero RGB8
error. This supports the bounded rule; other domains/materials and whole-preset
appearance remain separate obligations.

Evidence: `tools/milk-analyzer/fixtures/zero-storage-source-proof-2026-10-04.json`
and `tools/milk-analyzer/fixtures/zero-storage-native-proof-2026-10-04.json`.
The last full 371-preset structural gap count is a dated snapshot preceding this
fix and the 16-section texture-size fix; no new full count is claimed here.
