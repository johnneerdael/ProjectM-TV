"""Repeat the main fidelity failures over a twelve-second measurement window."""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from measure import Config, ROOT, bass_signals, run_one


def main():
    work = ROOT / "build/follow-ups/verification/diffusion-long"
    work.mkdir(parents=True, exist_ok=True)
    pcm = bass_signals(Config(fps=30, warmup_seconds=4, measurement_seconds=12), work / "signals")["bass-0.30"]
    names = ("$$$ Royal - Mashup (191).milk", "suksma - penattrition - geiss crossfire shaders.milk",
             "TonyMilkdrop - Nuclear [Flexi - help out + alien complex].milk",
             "TonyMilkdrop - I Like Cartoon --- Isosceles edit.milk", "ORB - Toffie Grider.milk")
    configs = [("c665", 1182, 665, False, "diagnostics-fixed")]
    for width, height in ((2364, 1330), (3840, 2160)):
        configs += [("q"+str(height), width, height, True, "diagnostics-fixed"),
                    ("diff"+str(height), width, height, True, "diffusion-safe-on")]
    jobs = [(name, None, *config, repeat, work, pcm, (30, 4, 12))
            for name in names for config in configs for repeat in (1, 2)]
    rows, pending = [], []
    for job in jobs:
        path = work / "jobs" / f"{job[0]}-{job[2]}-{job[6]}-r{job[7]}" / "metrics.json"
        if path.exists():
            rows.append(json.loads(path.read_text()))
        else:
            pending.append(job)
    with ThreadPoolExecutor(max_workers=2) as pool:
        for row in pool.map(run_one, pending):
            rows.append(row)
            (work / "raw.json").write_text(json.dumps(rows, indent=2))
    data = {(r["name"], r["key"], r["repeat"]): r for r in rows}
    nondeterministic, comparisons = [], []
    for name in names:
        for key, *_ in configs:
            if data[(name, key, 1)]["sha256_all_frames"] != data[(name, key, 2)]["sha256_all_frames"]:
                nondeterministic.append([name, key])
        def frames(key):
            return np.load(work / data[(name, key, 1)]["five_frames"])["frames"].astype(np.float32) / 255
        reference = data[(name, "c665", 1)]
        ground = frames("c665")
        for height in (1330, 2160):
            item = {"name": name, "height": height,
                    "reference_motion_mae": float(np.abs(np.diff(ground, axis=0)).mean())}
            for variant, key in (("baseline", "q"+str(height)), ("diffusion", "diff"+str(height))):
                row, images = data[(name, key, 1)], frames(key)
                item[variant] = {"img_err": float(np.abs(images-ground).mean()),
                                 "luma_ratio": row["luma"] / reference["luma"],
                                 "center_rgb": row["center_rgb"], "saturation": row["saturation"],
                                 "motion_mae": float(np.abs(np.diff(images, axis=0)).mean()),
                                 "picture_sharpness_ratio": row["sharpness"]["picture"] / max(reference["sharpness"]["picture"], 1e-12)}
            comparisons.append(item)
            print(f"{name}@{height}: {item['baseline']['img_err']:.4f} -> {item['diffusion']['img_err']:.4f}", flush=True)
    result = {"jobs": len(rows), "nondeterministic": nondeterministic,
              "timing": {"fps": 30, "warmup_seconds": 4, "measurement_seconds": 12}, "comparisons": comparisons}
    Path(__file__).with_name("results-diffusion-long.json").write_text(json.dumps(result, indent=2))
    print("nondeterministic", nondeterministic, flush=True)


if __name__ == "__main__":
    main()
