# Saved offline shader compatibility in static export

`effect_family_export` now accepts --compile-manifest and the direct API
compile_manifest argument. The exporter consumes saved CPU translation/offline
GLSL compile evidence while invoking only the native reader. Exact full-file/
shader/request/profile/stage/engine/archive/tool identity joins are required.
Missing cases stay unknown. Accepted/rejected reports choose conditional custom/
fallback candidates; runtime driver/texture-binding certification claims are
rejected. The seal establishes integrity, not producer authentication. Explicit
sampler/texsize declarations remain assumed inputs, not observed bindings.

Whole-manifest identity joins cache keys and CLI run identity; manifest bytes
are checked before and after each preset, including the last case before result
commit. Failure/tampering/stale/malformed/contradictory records are not reused.
A failing last-case mutation control preceded the guard. Sixteen new actual-
source34translator/glslang controls cover candidate/rejected/missing results,
exact provenance mismatches, bool/status/schema types, malformed input, cache
integrity, paired CLI export and mutation.24focused tests pass. Independent
review found no actionable findings. No shader/equation/render execution is used.

Bounded preparation uses the existing corpus_worker.compatibility_for helper,
source34milk-shader-translate and glslangValidator. Native CPU preprocess,
reference-scan and translation bodies report their source/archive identities.
The helper declares native normalized noisevol names3D, other referenced/authored
aliases2D, and texsize inputs explicitly. Its statement is a descriptor contract:
asset availability, dimensions, upload, random selection, actual GPU bindings,
linking and fallback initialization remain unverified. These assumptions must
not be relabelled as production render observations or source appearance proof.

The unchanged100source sample has174offline reports:86warp/87composite accepted,
one warp rejected. Previously87warp and87composite selections were unknown.
There are now86custom-warp/87custom-composite conditional candidates,14fixed-
warp and13legacy-composite stages including file-configured defaults. All100
exports retain exact source/hash joins and ZIP CRC. Complete uniform native warp
recipes9→21 (15procedural,6affine), with12new cases.74recipes stay unknown and
5disconnected. Family records changed in72presets, often by removing only the
missing-compatibility condition; do not count those as72new recognized pictures.

The rejected authored section is cpe domains flacc - portable massation segway
nz+.milk, full-file SHA2560244f2bb90dfaa4327dcda0adf47410f85c73c68835a21ab3f7d9f1f1c7eb71f.
Native translation reports HLSL parsing failure. This is a preserved offline
fallback candidate, not a newly reproduced GPU/AAR bug or an appearance verdict.
No authored source was altered or rerolled.

Preparation time totals33.77352seconds; source export37.822124seconds, maximum
2.364767seconds per preset, on this host. No whole-corpus/hardware guarantee.
`census.json` records exact presets, before/after branch/recipe states, remaining
source unknowns and producer identity. Raw inputs/evidence remain under
build/preset-corpus/source-compile-manifest-2026-10-10: prepare.py, manifest.json,
preparation.json/log and export/batch-000001.zip. The preparation script uses no
AI, device or rendering API; it freezes actual adapter/validator hashes.

Manifest semantic SHA256a3701de5c868d25e21af9eb2457f0c918746270455870ad32447dee4d835523f.
Manifest file SHA25601e97e69283242d039ad2925e1845b41aa81a96418c758e12a086ca3a899e32f.
Paired ZIP SHA256360d95306ea90d080b95de496a99fd6fb3c5412a7206bec555a5a8c289aa6e6a.
Reader SHA256754e4f4129db585cb4f7d5bee915d6bb24ac10ab25901ee7ef0832ce50744afc.
Matching source34targets published2.3.36bytes; published-runtime qualification
remains separately pending. No shared device/full corpus was operated. Actual
appearance, dominance, flashing, full feedback and mood accuracy remain open.

Final prepared suite: **2,678tests and92subtests pass in151.78seconds**.
Strict MkDocs and whitespace checks pass. These are source/evidence checks,
not native driver/texture or whole-preset appearance/mood certification.
