"""Compare each diffusion result and preserve separate authored-size noise and motion measures."""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
WORK = ROOT / "build/follow-ups/verification/diffusion-focus"


def main():
    rows = json.loads((WORK / "raw.json").read_text())
    data = {(r["name"], r["key"], r["repeat"]): r for r in rows}
    names = sorted({r["name"] for r in rows})
    nondeterministic = []
    comparisons = []
    for name in names:
        for key in {r["key"] for r in rows if r["name"] == name}:
            if data[(name, key, 1)]["sha256_all_frames"] != data[(name, key, 2)]["sha256_all_frames"]:
                nondeterministic.append([name, key])
        def record(key):
            return data[(name, key, 1)]
        def frames(key):
            return np.load(WORK / record(key)["five_frames"])["frames"].astype(np.float32) / 255
        ground = frames("c665")
        noise = {key: float(np.abs(frames(key)-ground).mean()) for key in ("c656", "c675")}
        for height in (1330, 2160):
            baseline, diff = "q"+str(height), "diff"+str(height)
            before, after = frames(baseline), frames(diff)
            before_err = float(np.abs(before-ground).mean())
            after_err = float(np.abs(after-ground).mean())
            row = {"name": name, "height": height, "baseline_img_err": before_err,
                   "diffusion_img_err": after_err, "delta_img_err": after_err-before_err,
                   "authored_pairwise_noise": noise,
                   "baseline_luma_ratio": record(baseline)["luma"] / record("c665")["luma"],
                   "diffusion_luma_ratio": record(diff)["luma"] / record("c665")["luma"],
                   "authored_center_rgb": record("c665")["center_rgb"],
                   "baseline_center_rgb": record(baseline)["center_rgb"],
                   "diffusion_center_rgb": record(diff)["center_rgb"],
                   "authored_saturation": record("c665")["saturation"],
                   "baseline_saturation": record(baseline)["saturation"],
                   "diffusion_saturation": record(diff)["saturation"],
                   "authored_motion_mae": float(np.abs(np.diff(ground, axis=0)).mean()),
                   "baseline_motion_mae": float(np.abs(np.diff(before, axis=0)).mean()),
                   "diffusion_motion_mae": float(np.abs(np.diff(after, axis=0)).mean()),
                   "authored_unique_measurement_frames": len(set(record("c665")["sha256_measurement_frames"])),
                   "baseline_unique_measurement_frames": len(set(record(baseline)["sha256_measurement_frames"])),
                   "diffusion_unique_measurement_frames": len(set(record(diff)["sha256_measurement_frames"]))}
            comparisons.append(row)
            print("{name} @{height}: {baseline_img_err:.4f} -> {diffusion_img_err:.4f} ({delta_img_err:+.4f})".format(**row))
    result = {"render_jobs": len(rows), "presets": len(names), "nondeterministic": nondeterministic,
              "comparisons": comparisons}
    target = Path(__file__).with_name("results-diffusion-focus.json")
    target.write_text(json.dumps(result, indent=2))
    print("summary", len(rows), len(names), "nondeterministic", nondeterministic)


if __name__ == "__main__":
    main()
