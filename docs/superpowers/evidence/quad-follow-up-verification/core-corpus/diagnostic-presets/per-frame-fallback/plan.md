# Per-frame legacy record fallback

Confirmed cause: MilkDrop expression preprocessing removes record separators and
line comments before compilation. Our parser inserts newlines, splitting the
`is_beat` token in161/430 and related presets. The exact compiler ablation rejects
both current forms and accepts both legacy forms; actual-core candidate28 rejects
both presets twice on the physical device with a per-frame compilation error.

Implement only in PerFrameContext::CompilePerFrameCode. Compile the original
program first; if it fails, strip record newlines and // or double-backslash line
comments as MilkDrop does and retry only if that changes the input. Already
accepted programs, per-frame init, other expression stages and shaders retain
their existing paths. Both compiler failures still raise the existing exception.

Verify split-token execution, both comment forms, preservation of a currently
accepted block-comment program that legacy stripping would damage, and genuine
invalid-code rejection. Run the complete host suite. Preserve RED/GREEN evidence
and generate patch0029 from this isolated scratch source, then commit/push it.
Build a new optimized actual-core candidate with the same private observer. Check
requested-preset acceptance and repeat/capture equivalence on51.53 before the
final candidate corpus. The active baseline, source presets and frozen candidate28
artifacts remain untouched. A component compiler pass alone is not a core render.
