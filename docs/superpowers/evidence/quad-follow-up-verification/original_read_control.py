"""Isolate individual feedback reads using the research-only original sampler."""

import json
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from measure import ROOT, run_one


def main():
    original = ROOT / "build/follow-ups/verification/diffusion-focus"
    work = ROOT / "build/follow-ups/verification/original-read-slot-safe"
    work.mkdir(parents=True, exist_ok=True)
    baselines = json.loads((original / "raw.json").read_text())
    baseline_records = {(r["name"], r["key"]): r for r in baselines if r["repeat"] == 1}
    names = ("TonyMilkdrop - Nuclear [Flexi - help out + alien complex].milk", "rce-ordinary - want.milk")
    pcm = next((original / "signals").glob("bass-0.30-*.f32"))
    jobs = []
    for name in names:
        text = (ROOT / "core/src/main/assets/presets" / name).read_text()
        if "Nuclear" in name:
            old = "tex2D(sampler_main, uv_orig)"
            new = "tex2D(sampler_pmx_original, uv_orig)"
        else:
            old = "tex2D(sampler_fc_main,lerp(uv_orig,uv,0.5))"
            new = "tex2D(sampler_fc_pmx_original,lerp(uv_orig,uv,0.5))"
        assert text.count(old) == 1, name
        for variant, content in (("copy", text), ("retained", text.replace(old, new))):
            for key, width, height, quad, on in (("c665", 1182, 665, False, False),
                                               ("q1330", 2364, 1330, True, False),
                                               ("q2160", 3840, 2160, True, False),
                                               ("diff1330", 2364, 1330, True, True),
                                               ("diff2160", 3840, 2160, True, True)):
                for repeat in (1, 2):
                    worker = "diffusion-original-on" if on else "diffusion-original-off"
                    jobs.append((name, content, variant+"-"+key, width, height, quad, worker, repeat, work, pcm))
    rows, pending = [], []
    for job in jobs:
        path = work / "jobs" / f"{job[0]}-{job[2]}-{job[6]}-r{job[7]}" / "metrics.json"
        if path.exists():
            rows.append(json.loads(path.read_text()))
        else:
            pending.append(job)
    for active in (False, True):
        selected = [job for job in pending if job[6].endswith("-on") == active]
        with ThreadPoolExecutor(max_workers=2) as pool:
            for row in pool.map(run_one, selected):
                rows.append(row)
                (work / "raw.json").write_text(json.dumps(rows, indent=2))
        if not active:
            changed = [r["name"]+":"+r["key"] for r in rows
                       if r["worker"].endswith("-off") and r["sha256_all_frames"] != baseline_records[(r["name"], r["key"].split("-", 1)[1])]["sha256_all_frames"]]
            if changed:
                raise RuntimeError(f"Diffusion-off control changed; do not interpret ablation: {changed}")
            print("All diffusion-off controls byte-identical; proceeding to active diffusion", flush=True)
    data = {(r["name"], r["key"], r["repeat"]): r for r in rows}
    nondeterministic, changed_copy, changed_retained_off, comparisons = [], [], [], []
    for name in names:
        for variant in ("copy", "retained"):
            for key in ("c665", "q1330", "q2160", "diff1330", "diff2160"):
                row = data[(name, variant+"-"+key, 1)]
                if row["sha256_all_frames"] != data[(name, variant+"-"+key, 2)]["sha256_all_frames"]:
                    nondeterministic.append([name, variant, key])
                if variant == "copy" and row["sha256_all_frames"] != baseline_records[(name, key)]["sha256_all_frames"]:
                    changed_copy.append([name, key])
                if variant == "retained" and not key.startswith("diff") and row["sha256_all_frames"] != baseline_records[(name, key)]["sha256_all_frames"]:
                    changed_retained_off.append([name, key])
        ground = np.load(original / baseline_records[(name, "c665")]["five_frames"])["frames"].astype(np.float32) / 255
        for height in (1330, 2160):
            records = {variant: data[(name, variant+"-diff"+str(height), 1)] for variant in ("copy", "retained")}
            item = {"name": name, "height": height}
            for variant, row in records.items():
                frames = np.load(work / row["five_frames"])["frames"].astype(np.float32) / 255
                item[variant] = {"img_err": float(np.abs(frames-ground).mean()),
                                 "luma_ratio": row["luma"] / baseline_records[(name, "c665")]["luma"],
                                 "center_rgb": row["center_rgb"], "saturation": row["saturation"],
                                 "motion_mae": float(np.abs(np.diff(frames, axis=0)).mean())}
            comparisons.append(item)
            print(f"{name}@{height}: {item['copy']['img_err']:.4f} -> {item['retained']['img_err']:.4f}", flush=True)
    result = {"jobs": len(rows), "nondeterministic": nondeterministic,
              "changed_unmodified_copy": changed_copy, "changed_retained_with_diffusion_off": changed_retained_off,
              "comparisons": comparisons}
    (ROOT / "docs/superpowers/evidence/quad-follow-up-verification/results-original-read.json").write_text(json.dumps(result, indent=2))
    print(json.dumps({key: result[key] for key in result if key != "comparisons"}), flush=True)


if __name__ == "__main__":
    main()
