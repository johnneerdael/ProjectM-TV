# Sampler aliases and native declaration deletion

Rechecking the historical 149 target-parse witnesses found 83 shader failures,
53 equation sections accepted by MilkDrop-style assembly but rejected by native
projectM assembly, and 13 equation sections rejected by both. These are distinct
compatibility and interpretation obligations, not 149 missing maths functions.

The shader reader retained sampler declarations after object-macro expansion.
An alias such as `#define sampler_pic sampler_cells` produces
`sampler2D(sampler_cells);`, which cannot parse as a declaration. Native projectM
removes sampler declarations before rebuilding descriptor bindings. The reader
now removes plain generic/2D/3D named declarations before injecting bindings,
while retaining sampler-state initializers for their separate model/gate.

Native deletion also removes everything after the declaration through the end
of its line. A same-line colour assignment therefore disappears; preserving it
would silently invent coloured output where native output is black. Conversely,
the deletion starts at `sampler`, preserving a preceding qualifier such as
`uniform`. That qualifier can spill into the next declaration and change its
storage semantics. Unused declaration identities are retained during rebuilding:
they can affect texture binding order and the warp stage's wrap policy. These
cases have regression coverage. Original preset source
remains recorded separately from the resulting execution tree.

The final targeted recheck makes 67 of the 83 historical shader witnesses parse;
63 lower completely. Four newly parsed sections still have uninitialized reads, and
16 still fail parsing. The checked fixture contains preset hashes, reader and
implementation identities, remaining reasons and diagnostics. This is source
interpretation evidence, not native-driver or whole-preset appearance accuracy.

Fixture: `tools/milk-analyzer/fixtures/sampler-alias-source-proof-2026-10-04.json`.
Primary runtime trace: pinned `MilkdropShader::TranspileHLSLShader`, copied into
`build/milk-analyzer/native/cpu_shader_adapter.hpp` as `targetTranslate`.
