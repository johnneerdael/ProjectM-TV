"""Compare an RGBA16F diffusion target with identical RGBA8 diffusion and reference jobs."""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from measure import ROOT, run_one


def main():
    original = ROOT / "build/follow-ups/verification/diffusion-focus"
    work = ROOT / "build/follow-ups/verification/diffusion-float"
    work.mkdir(parents=True, exist_ok=True)
    baseline = json.loads((original / "raw.json").read_text())
    names = ("$$$ Royal - Mashup (103).milk", "$$$ Royal - Mashup (191).milk",
             "suksma - penattrition - geiss crossfire shaders.milk", "rce-ordinary - want.milk",
             "TonyMilkdrop - Nuclear [Flexi - help out + alien complex].milk",
             "TonyMilkdrop - I Like Cartoon --- Isosceles edit.milk")
    pcm = next((original / "signals").glob("bass-0.30-*.f32"))
    jobs = [(name, None, "float"+str(height), width, height, True, "diffusion-float-on", repeat, work, pcm)
            for name in names for width, height in ((2364, 1330), (3840, 2160)) for repeat in (1, 2)]
    rows, pending = [], []
    for job in jobs:
        path = work / "jobs" / f"{job[0]}-{job[2]}-{job[6]}-r{job[7]}" / "metrics.json"
        if path.exists():
            rows.append(json.loads(path.read_text()))
        else:
            pending.append(job)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for row in pool.map(run_one, pending):
            rows.append(row)
            (work / "raw.json").write_text(json.dumps(rows, indent=2))
    data = {(r["name"], r["key"], r["repeat"]): r for r in baseline + rows}
    nondeterministic, comparisons = [], []
    for name in names:
        for height in (1330, 2160):
            key = "float"+str(height)
            candidate = data[(name, key, 1)]
            if candidate["sha256_all_frames"] != data[(name, key, 2)]["sha256_all_frames"]:
                nondeterministic.append([name, height])
            def frames(key, directory):
                return np.load(directory / data[(name, key, 1)]["five_frames"])["frames"].astype(np.float32) / 255
            ground = frames("c665", original)
            before = frames("diff"+str(height), original)
            after = frames(key, work)
            reference = data[(name, "c665", 1)]
            byte_target = data[(name, "diff"+str(height), 1)]
            item = {"name": name, "height": height,
                    "rgba8_img_err": float(np.abs(before-ground).mean()),
                    "rgba16f_img_err": float(np.abs(after-ground).mean()),
                    "target_format_img_difference": float(np.abs(before-after).mean()),
                    "rgba8_luma_ratio": byte_target["luma"] / reference["luma"],
                    "rgba16f_luma_ratio": candidate["luma"] / reference["luma"],
                    "rgba8_center_rgb": byte_target["center_rgb"], "rgba16f_center_rgb": candidate["center_rgb"],
                    "rgba8_saturation": byte_target["saturation"], "rgba16f_saturation": candidate["saturation"],
                    "rgba8_motion_mae": float(np.abs(np.diff(before, axis=0)).mean()),
                    "rgba16f_motion_mae": float(np.abs(np.diff(after, axis=0)).mean())}
            comparisons.append(item)
            print(f"{name}@{height}: {item['rgba8_img_err']:.4f} -> {item['rgba16f_img_err']:.4f}; luma {item['rgba8_luma_ratio']:.3f} -> {item['rgba16f_luma_ratio']:.3f}", flush=True)
    result = {"jobs": len(rows), "nondeterministic": nondeterministic, "comparisons": comparisons}
    Path(__file__).with_name("results-diffusion-float.json").write_text(json.dumps(result, indent=2))
    print("nondeterministic", nondeterministic, flush=True)


if __name__ == "__main__":
    main()
