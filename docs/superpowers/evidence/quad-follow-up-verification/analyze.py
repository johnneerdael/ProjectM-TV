"""Compare lossless measurement outputs; keep reference fidelity and same-size parity separate."""

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def analyze(phase):
    work = ROOT / "build/follow-ups/verification" / phase
    rows = json.loads((work / "raw.json").read_text())
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["name"], row["key"])].append(row)
    nondeterministic = []
    for key, repeats in grouped.items():
        if len(repeats) != 2:
            raise ValueError(f"missing repeat: {key}")
        if repeats[0]["sha256_all_frames"] != repeats[1]["sha256_all_frames"]:
            nondeterministic.append(key)
    metrics = {key: repeats[0] for key, repeats in grouped.items()}
    names = sorted({key[0] for key in metrics})
    legacy_changed, comparisons = [], []
    legacy_comparisons = 0

    def image_error(a, b):
        first = np.load(work / a["five_frames"])["frames"].astype(np.float32)
        second = np.load(work / b["five_frames"])["frames"].astype(np.float32)
        return float(np.abs(first-second).mean() / 255)

    def ratio(a, b):
        return a / b if b else None

    for name in names:
        ground = metrics[(name, "c665")]
        for key in ("c665", "c360", "c480", "c540"):
            old = metrics.get((name, "old-" + key))
            if old is None:
                continue
            new = metrics[(name, key)]
            legacy_comparisons += 1
            if new["sha256_all_frames"] != old["sha256_all_frames"]:
                legacy_changed.append({"name": name, "key": key})
        for key in ("q360", "q480", "q540", "q665", "q1080", "q2160"):
            row = metrics.get((name, key))
            if row is None:
                continue
            same = metrics.get((name, "c" + key[1:]))
            item = {"name": name, "key": key,
                    "authored_img_err": image_error(row, ground),
                    "authored_luma_ratio": ratio(row["luma"], ground["luma"]),
                    "luma": row["luma"], "center_rgb": row["center_rgb"],
                    "saturation": row["saturation"]}
            if same is not None:
                item.update(same_size_img_err=image_error(row, same),
                            same_size_luma_ratio=ratio(row["luma"], same["luma"]))
            if phase == "geometry":
                def mean_metric(record, metric):
                    return float(np.mean([m[metric] for m in record["canvas_metrics"]]))
                item["authored_energy_ratio"] = ratio(mean_metric(row, "linear_green_share"),
                                                     mean_metric(ground, "linear_green_share"))
                item["authored_lit_ratio"] = ratio(mean_metric(row, "lit_share"), mean_metric(ground, "lit_share"))
                if same is not None:
                    item["same_size_energy_ratio"] = ratio(mean_metric(row, "linear_green_share"),
                                                          mean_metric(same, "linear_green_share"))
                    item["same_size_lit_ratio"] = ratio(mean_metric(row, "lit_share"), mean_metric(same, "lit_share"))
                if "non_integer_share_of_lit" in row["canvas_metrics"][0]:
                    item["non_integer_share_of_lit"] = mean_metric(row, "non_integer_share_of_lit")
                if all("hit_histogram" in m for m in row["canvas_metrics"] + ground["canvas_metrics"]):
                    item["histogram_max_absolute_difference"] = float(np.abs(
                        np.mean([m["hit_histogram"] for m in row["canvas_metrics"]], axis=0) -
                        np.mean([m["hit_histogram"] for m in ground["canvas_metrics"]], axis=0)).max())
            comparisons.append(item)
    result = {"phase": phase, "render_jobs": len(rows), "presets": len(names),
              "legacy_comparisons": legacy_comparisons,
              "nondeterministic": nondeterministic, "legacy_changed": legacy_changed,
              "comparisons": comparisons}
    (OUT / f"results-{phase}.json").write_text(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != "comparisons"}, indent=2))
    for item in comparisons:
        if phase == "geometry":
            print(item["name"], item["key"], "energy", round(item["authored_energy_ratio"], 4),
                  "same", round(item.get("same_size_energy_ratio", 0), 4))
        else:
            print(item["name"], item["key"], "err", round(item["authored_img_err"], 4),
                  "same", round(item.get("same_size_img_err", 0), 4))
    return result


if __name__ == "__main__":
    import sys
    analyze(sys.argv[1])
