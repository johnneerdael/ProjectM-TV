"""Regenerate the frozen analysis from compressed records, or new private run results.

The shared recipe reproduces the original fixed seed/order/100000 paired-block draws.
It performs no rendering and refuses missing run records.
"""
from pathlib import Path
import gzip
import json
from benchmark import analyze

root = Path(__file__).resolve().parent
schedule = json.loads((root / "schedule.json").read_text())
if (root / "timed-runs.json.gz").exists():
    with gzip.open(root / "timed-runs.json.gz", "rt") as stream:
        runs = json.load(stream)
else:
    runs = {job["name"]: json.loads((root / "runs" / job["name"] / "result.json").read_text())
            for job in schedule}
assert set(runs) == {job["name"] for job in schedule}
summary = analyze(schedule, runs)
(root / "analysis.json").write_text(json.dumps(summary, indent=2) + "\n")
for case, data in summary.items():
    print(case)
    for metric, value in data["metrics"].items():
        print(metric, {key: item for key, item in value.items() if key != "blocks"})
