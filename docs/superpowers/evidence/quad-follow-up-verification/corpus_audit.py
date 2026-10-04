"""Verify saved baseline records and export a snapshot joined to source families.

Read-only with respect to render evidence; safe to run while the scan advances.
"""
from collections import Counter
import json
from pathlib import Path

from corpus_baseline import ROOT, WORK, atomic, key_for, read_cached
from preset_lab.identity import digest


def main():
    protocol = json.loads((WORK / "protocol.json").read_text())
    protocol_hash = protocol.pop("sha256")
    assert digest(protocol) == protocol_hash, "protocol checksum mismatch"
    inventory = json.loads((WORK / "inventory.json").read_text())
    families_path = ROOT / "build/follow-ups/corpus-family-review/preset-index.json"
    families = json.loads(families_path.read_text())
    family_index = {r["filename"]: r for r in families["presets"]}
    assert len(family_index) == inventory["count"] == 9606
    expected = {r["path"] for r in inventory["presets"]}
    assert expected == set(family_index), "corpus membership mismatch"
    rows, issues, group_counts = [], [], {}
    for record in inventory["presets"]:
        name = record["path"]
        family = family_index[name]
        assert family["sha256"] == record["sha256"], f"source mismatch: {name}"
        relative = f"rows/{key_for(protocol_hash, record)}.json"
        target = WORK / relative
        row = read_cached(target, protocol_hash, record)
        if row is None:
            if target.exists():
                issues.append({"preset": name, "error": "invalid row checksum/provenance"})
            continue
        if row["status"] == "success":
            repeats = [read_cached(WORK / path, protocol_hash, record) for path in row["runs"]]
            valid = (len(repeats) == 2 and all(
                r is not None and r["status"] == "success"
                and r["frames_observed"] == 240 and len(r["sha256_frames"]) == 240
                and r["window_mean_thumbnail"]["count"] == 120 for r in repeats))
            valid = valid and row["repeat_exact"] is True
            if valid:
                valid = (repeats[0]["sha256_all_frames"] == repeats[1]["sha256_all_frames"]
                         and repeats[0]["sha256_frames"] == repeats[1]["sha256_frames"])
            if not valid:
                issues.append({"preset": name, "error": "successful row lacks exact complete repeats"})
        item = {"preset": name, "preset_sha256": record["sha256"], "status": row["status"],
                "row": relative, "features": family["feature_names"],
                "shader_hashes": family["shader_hashes"], "unclassified": family["unclassified"]}
        rows.append(item)
        for feature in family["feature_names"]:
            group_counts.setdefault(feature, Counter())[row["status"]] += 1
    report = {"protocol_sha256": protocol_hash, "inventory_count": inventory["count"],
              "verified_terminal_presets": len(rows), "remaining_presets": inventory["count"] - len(rows),
              "complete_coverage": len(rows) == inventory["count"],
              "statuses": dict(Counter(r["status"] for r in rows)), "integrity_issues": issues,
              "source_family_index": str(families_path), "source_family_index_sha256": digest(families),
              "feature_status_counts": {k: dict(v) for k, v in sorted(group_counts.items())},
              "limitations": "Source features overlap and are not fault verdicts. This is an advancing snapshot, not a candidate comparison or authored-reference fidelity result.",
              "rows": rows}
    atomic(WORK / "verified-family-index.json", report)
    print(json.dumps({k: report[k] for k in ("protocol_sha256", "verified_terminal_presets", "remaining_presets", "complete_coverage", "statuses", "integrity_issues")}))
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
