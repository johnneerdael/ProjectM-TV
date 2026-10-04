"""Diagnostic parity check for the rejected classic-at-unit-scale candidate.

This checks same-size GL parity, not authored fidelity; passing it does not justify the candidate.
It runs against saved paired jobs from measure.py low-real or low-nosmooth.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def main():
    phase = sys.argv[1]
    path = ROOT / "build/follow-ups/verification" / phase / "raw.json"
    rows = json.loads(path.read_text())
    grouped = {(r["name"], r["key"], r["repeat"]): r for r in rows}
    mismatches = []
    pairs = 0
    for (name, key, repeat), row in grouped.items():
        if key not in ("q360", "q480", "q540", "q665"):
            continue
        classic = grouped[(name, "c" + key[1:], repeat)]
        pairs += 1
        if row["sha256_all_frames"] != classic["sha256_all_frames"]:
            mismatches.append({"name": name, "key": key, "repeat": repeat})
    print(json.dumps({"pairs": pairs, "mismatches": mismatches}, indent=2))
    if pairs == 0 or mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
