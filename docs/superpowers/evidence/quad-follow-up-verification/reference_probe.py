"""Measure the approved reference-grid probe; preserve byte gates and every degradation."""

import argparse
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from measure import Config, ROOT, bass_signals, run_one


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", default="Royal.*191")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--linear", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(Path(__file__).with_name("preset-sets.json").read_text())
    names = [name for name in manifest["all"] if re.search(args.filter, name)]
    worker_prefix = "reference-feedback-linear" if args.linear else "reference-feedback"
    work = ROOT / "build/follow-ups/verification" / (worker_prefix+"-attached")
    work.mkdir(parents=True, exist_ok=True)
    pcm = bass_signals(Config(fps=30, warmup_seconds=4, measurement_seconds=4), work / "signals")["bass-0.30"]
    configs = [("c665", 1182, 665, False), ("q1330", 2364, 1330, True), ("q2160", 3840, 2160, True)]
    jobs = []
    for name in names:
        cases = configs + ([("q540", 960, 540, True), ("qref", 1024, 768, True)] if "Royal - Mashup (191)" in name else [])
        for key, width, height, quad in cases:
            for variant in ("off", "on"):
                for repeat in (1, 2):
                    jobs.append((name, None, key, width, height, quad, worker_prefix+"-"+variant, repeat, work, pcm))
    results, pending = [], []
    for job in jobs:
        path = work / "jobs" / f"{job[0]}-{job[2]}-{job[6]}-r{job[7]}" / "metrics.json"
        if path.exists():
            results.append(json.loads(path.read_text()))
        else:
            pending.append(job)
    print(f"{len(pending)} pending jobs; {len(results)} cached", flush=True)
    raw_path = work / "raw.json"
    existing = json.loads(raw_path.read_text()) if raw_path.exists() else []
    def save():
        merged = {(r["name"], r["key"], r["worker"], r["repeat"]): r for r in existing+results}
        raw_path.write_text(json.dumps(list(merged.values()), indent=2))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for row in pool.map(run_one, pending):
            results.append(row)
            save()
    save()
    data = {(r["name"], r["key"], r["worker"], r["repeat"]): r for r in json.loads(raw_path.read_text())}
    names = sorted({r[0] for r in data})
    nondeterministic, off_gate_changed, comparisons = [], [], []
    for name in names:
        keys = sorted({key for n, key, _, _ in data if n == name})
        def record(key, variant):
            return data[(name, key, worker_prefix+"-"+variant, 1)]
        def frames(key, variant):
            return np.load(work / record(key, variant)["five_frames"])["frames"].astype(np.float32) / 255
        reference = record("c665", "off")
        ground = frames("c665", "off")
        for key in keys:
            for variant in ("off", "on"):
                if record(key, variant)["sha256_all_frames"] != data[(name, key, worker_prefix+"-"+variant, 2)]["sha256_all_frames"]:
                    nondeterministic.append([name, key, variant])
            same = record(key, "off")["sha256_all_frames"] == record(key, "on")["sha256_all_frames"]
            if key in ("c665", "q540", "qref"):
                if not same:
                    off_gate_changed.append([name, key])
                continue
            row = {"name": name, "key": key, "reference_motion_mae": float(np.abs(np.diff(ground, axis=0)).mean())}
            for variant in ("off", "on"):
                metrics, images = record(key, variant), frames(key, variant)
                row[variant] = {"img_err": float(np.abs(images-ground).mean()),
                                "luma_ratio": metrics["luma"] / reference["luma"],
                                "center_rgb": metrics["center_rgb"], "saturation": metrics["saturation"],
                                "motion_mae": float(np.abs(np.diff(images, axis=0)).mean()),
                                "picture_sharpness_ratio": metrics["sharpness"]["picture"] / max(reference["sharpness"]["picture"], 1e-12)}
            comparisons.append(row)
            print(f"{name}@{key}: {row['off']['img_err']:.4f} -> {row['on']['img_err']:.4f}; motion {row['reference_motion_mae']:.4f} / {row['on']['motion_mae']:.4f}", flush=True)
    result = {"jobs": len(data), "nondeterministic": nondeterministic, "off_gate_changed": off_gate_changed,
              "comparisons": comparisons, "status": "experimental; not accepted for production"}
    Path(__file__).with_name("results-"+worker_prefix+".json").write_text(json.dumps(result, indent=2))
    print("nondeterministic", nondeterministic, "off gates changed", off_gate_changed, flush=True)


if __name__ == "__main__":
    main()
