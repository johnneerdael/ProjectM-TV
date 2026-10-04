"""Check actual presets before/after the sampler fix, preserving both reference renders."""

import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from measure import Config, ROOT, bass_signals, run_one


def main():
    manifest = json.loads(Path(__file__).with_name("preset-sets.json").read_text())
    work = ROOT / "build/follow-ups/verification/sampler-impact-private-rng"
    work.mkdir(parents=True, exist_ok=True)
    pcm = bass_signals(Config(fps=30, warmup_seconds=4, measurement_seconds=4), work / "signals")["bass-0.30"]
    configs = (("c665", 1182, 665, False), ("q1330", 2364, 1330, True), ("q2160", 3840, 2160, True))
    workers = ("deterministic-baseline", "deterministic-samplers")
    jobs = [(name, None, *config, worker, repeat, work, pcm) for name in manifest["all"]
            for config in configs for worker in workers for repeat in (1, 2)]
    rows, pending = [], []
    previous_work = ROOT / "build/follow-ups/verification/diffusion-focus"
    for job in jobs:
        filename = f"{job[0]}-{job[2]}-{job[6]}-r{job[7]}/metrics.json"
        path = work / "jobs" / filename
        if path.exists():
            rows.append(json.loads(path.read_text()))
        elif job[6] == "diagnostics-fixed" and (previous_work / "jobs" / filename).exists():
            cached = json.loads((previous_work / "jobs" / filename).read_text())
            cached["five_frames"] = str((previous_work / cached["five_frames"]).resolve())
            cached["diagnostics"] = str((previous_work / cached["diagnostics"]).resolve())
            rows.append(cached)
        else:
            pending.append(job)
    print(f"{len(jobs)} cases: {len(pending)} pending renders, {len(rows)} cached", flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for row in pool.map(run_one, pending):
            rows.append(row)
            (work / "raw.json").write_text(json.dumps(rows, indent=2))
    (work / "raw.json").write_text(json.dumps(rows, indent=2))
    data = {(r["name"], r["key"], r["worker"], r["repeat"]): r for r in rows}
    nondeterministic, comparisons = [], []
    for name in manifest["all"]:
        path = ROOT / "core/src/main/assets/presets" / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["preset_sha256"][name]:
            raise ValueError(f"preset changed since manifest: {name}")
        warp = "\n".join(line for line in path.read_text().splitlines() if line.startswith("warp_"))
        stripped = re.sub(r"/\*.*?\*/|//[^\n]*", "", warp, flags=re.DOTALL)
        samplers = set(re.findall(r"\bsampler_(\w+)", stripped)) | {"main"}
        main_samplers = sorted(s for s in samplers if s == "main" or s.endswith("_main"))
        before_first = main_samplers[0]
        def record(key, worker):
            return data[(name, key, worker, 1)]
        def frames(key, worker):
            return np.load(work / record(key, worker)["five_frames"])["frames"].astype(np.float32) / 255
        ground_before = frames("c665", workers[0])
        ground_after = frames("c665", workers[1])
        for key, *_ in configs:
            for worker in workers:
                if record(key, worker)["sha256_all_frames"] != data[(name, key, worker, 2)]["sha256_all_frames"]:
                    nondeterministic.append([name, key, worker])
            before, after = frames(key, workers[0]), frames(key, workers[1])
            old, new = record(key, workers[0]), record(key, workers[1])
            row = {"name": name, "key": key, "static_first_main_descriptor_before": before_first,
                   "byte_identical": old["sha256_all_frames"] == new["sha256_all_frames"],
                   "direct_change_img_err": float(np.abs(before-after).mean()),
                   "baseline_vs_old_reference": float(np.abs(before-ground_before).mean()),
                   "candidate_vs_corrected_reference": float(np.abs(after-ground_after).mean()),
                   "candidate_vs_old_reference": float(np.abs(after-ground_before).mean()),
                   "old_luma": old["luma"], "new_luma": new["luma"],
                   "old_center_rgb": old["center_rgb"], "new_center_rgb": new["center_rgb"],
                   "old_saturation": old["saturation"], "new_saturation": new["saturation"]}
            comparisons.append(row)
            print(f"{name}@{key}: direct={row['direct_change_img_err']:.4f}, same={row['byte_identical']}, reference err {row['baseline_vs_old_reference']:.4f} -> {row['candidate_vs_corrected_reference']:.4f}", flush=True)
    result = {"jobs": len(rows), "presets": len(manifest["all"]), "nondeterministic": nondeterministic,
              "sets": {k: manifest[k] for k in ("control18", "capped24", "prior_virtual_size_regressions")},
              "comparisons": comparisons}
    Path(__file__).with_name("results-sampler-impact.json").write_text(json.dumps(result, indent=2))
    print("nondeterministic", nondeterministic, flush=True)


if __name__ == "__main__":
    main()
