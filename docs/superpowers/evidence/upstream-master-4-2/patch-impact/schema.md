# Compact patch impact schema and export

`impact.json.gz` (deterministic gzip, JSON inside) stores one `preset_catalog`. IDs are zero-based in exact sorted filename order. Each entry retains its filename, asset SHA256, byte count, source features and reader-process status. IDs are artifact-local; never reuse an ID from a different catalog hash.

Each of the 44 ordered `patches` retains the original filename/SHA, legacy applied commit, touched paths, activation condition, current port/upstream mapping, confidence, witness/control metadata and counts.

- `potential_scope.kind == "all"` references every catalog entry, subject to activation conditions. It means potentially affected by a shared path, not confirmed changed output.
- `potential_scope.kind == "candidate_ids"` lists source-domain priority IDs. It is not an exclusion certificate; the full fidelity gate still includes all presets.
- `positive_source_matches` gives IDs plus the original matching feature labels. `unresolved_priority.ids` preserves unresolved membership. `known_witnesses` preserves evidence basis/stage/limits against catalog IDs; witnesses are not full-render certificates.
- `all_preset_fidelity_gate_exemptions` remains empty for every patch.
- `source_full_artifact_sha256` and `compaction_validation` bind this export to the ignored explicit-list artifact. All memberships/features/witnesses were expanded and compared exactly during export.

Expand exact filenames and hashes for a patch from the repository root:

```python
import gzip
import json
from pathlib import Path

report = json.loads(gzip.decompress(Path("docs/superpowers/evidence/upstream-master-4-2/patch-impact/impact.json.gz").read_bytes()))
catalog = {row["id"]: row for row in report["preset_catalog"]}
patch = next(row for row in report["patches"] if row["historical_patch"].startswith("0040-"))
scope = patch["potential_scope"]
ids = list(catalog) if scope["kind"] == "all" else scope["ids"]
for preset_id in ids:
    preset = catalog[preset_id]
    print(preset["filename"], preset["asset_sha256"], sep="\t")
```

This expands source candidates only. Exact visual fidelity requires the separate same-role repeat, paired every-frame RGB and unchanged-release runtime gates. AST/frontend/token evidence cannot be promoted to visual certification by exporting or compressing it.
