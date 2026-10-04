"""Locate ORB's yellow/static state over 64 simulated seconds at 30 and 60 fps."""

import argparse
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np

from measure import Config, EngineIdentity, JobSpec, LUMA, PresetRecord, ROOT, bass_signals, canvas_preset, render_job

NAME = "ORB - Toffie Grider.milk"
WORK = ROOT / "build/follow-ups/verification/orb-lifetime"


def run(case):
    key, width, height, quad, fps, repeat, pcm, *extra = case
    text, worker_name = extra if extra else (None, "diagnostics-fixed")
    label = f"{key}-{fps}fps-r{repeat}"
    directory = WORK / label
    directory.mkdir(parents=True, exist_ok=True)
    worker = json.loads((ROOT / f"build/follow-ups/worker-{worker_name}.json").read_text())
    preset_root = ROOT / "core/src/main/assets/presets"
    if text is not None:
        (directory / NAME).write_text(text)
        preset_root = directory
    config = Config(width=width, height=height, fps=fps, warmup_seconds=4, measurement_seconds=60,
                    line_reference_width=1024 if quad else 0,
                    line_reference_height=768 if quad else 0)
    spec = JobSpec(PresetRecord(NAME, "", 0), "bass-0.30", pcm, config,
                   EngineIdentity(**worker["identity"]), preset_root,
                   ROOT / "core/src/main/assets/textures", directory / "worker")
    full_hash = hashlib.sha256()
    samples = []
    previous = None
    index = 0

    def observe(frame):
        nonlocal previous, index
        full_hash.update(frame)
        index += 1
        if index % fps:
            return
        small = cv2.resize(frame, (1182, 665), interpolation=cv2.INTER_AREA)
        values = small.astype(np.float32) / 255
        rgb = values.mean(axis=(0, 1), dtype=np.float64)
        seconds = index / fps
        samples.append({"seconds": seconds, "sha256": hashlib.sha256(frame).hexdigest(),
                        "mean_rgb": rgb.tolist(), "luma": float(rgb @ LUMA),
                        "center_rgb": values[299:366, 531:650].mean(axis=(0, 1), dtype=np.float64).tolist(),
                        "spatial_std_rgb": values.std(axis=(0, 1), dtype=np.float64).tolist(),
                        "motion_one_second_mae": None if previous is None else float(np.abs(values-previous).mean())})
        previous = values
        if seconds in (4, 8, 16, 32, 64):
            cv2.imwrite(str(directory / f"{int(seconds)}s.png"), cv2.cvtColor(small, cv2.COLOR_RGB2BGR))

    result = render_job(Path(worker["exe"]), spec, observe, 1200)
    if result.status != "success":
        raise RuntimeError(f"{label}: {result.status}: {result.diagnostics_path}")
    item = {"label": label, "config": {"size": [width, height], "fps": fps, "seconds": 64,
                                      "line_reference": [config.line_reference_width, config.line_reference_height]},
            "identity": worker["identity"], "worker": worker_name,
            "preset_sha256": hashlib.sha256((preset_root / NAME).read_bytes()).hexdigest(),
            "pcm_sha256": hashlib.sha256(pcm.read_bytes()).hexdigest(),
            "diagnostics": str(result.diagnostics_path.relative_to(WORK)),
            "sha256_all_frames": full_hash.hexdigest(), "frames": index, "samples": samples}
    (directory / "metrics.json").write_text(json.dumps(item, indent=2))
    print(f"{label}: final RGB={samples[-1]['mean_rgb']}, motion={samples[-1]['motion_one_second_mae']:.6f}", flush=True)
    return item


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ablations", action="store_true")
    group.add_argument("--upstream", action="store_true")
    args = parser.parse_args()
    phase = "upstream" if args.upstream else "ablations" if args.ablations else "lifetime"
    raw_path = WORK / f"raw-{phase}.json"
    WORK.mkdir(parents=True, exist_ok=True)
    # FPS does not change the signal. Every job receives the same 64-second PCM.
    pcm = bass_signals(Config(fps=30, warmup_seconds=4, measurement_seconds=60), WORK / "signals")["bass-0.30"]
    cases = [(key, width, height, quad, fps, repeat, pcm)
             for key, width, height, quad in (("classic665", 1182, 665, False),
                                               ("classic1080", 1920, 1080, False),
                                               ("quad1080", 1920, 1080, True))
             for fps in (30, 60) for repeat in (1, 2)]
    if args.ablations:
        original = (ROOT / "core/src/main/assets/presets" / NAME).read_text()
        no_comp = re.sub(r"^comp_\d+=.*\n?", "", original, flags=re.MULTILINE)
        variants = [("canvas665", canvas_preset(no_comp, 1182, 665), "diagnostics-fixed"),
                    ("border-off665", original.replace("ob_a=0.200000", "ob_a=0.000000"), "diagnostics-fixed"),
                    ("blur-offset-off665", original.replace("GetBlur1((uv - 0.5)*0.9 + 0.5)*0.1*(0.96 * bass_att)", "float2(0,0)"), "diagnostics-fixed"),
                    ("prequad665", None, "classic-points")]
        cases = [(key, 1182, 665, False, 30, repeat, pcm, text, worker)
                 for key, text, worker in variants for repeat in (1, 2)]
    if args.upstream:
        cases = [("upstream665", 1182, 665, False, fps, repeat, pcm, None, "upstream")
                 for fps in (30, 60) for repeat in (1, 2)]
    rows, pending = [], []
    for case in cases:
        path = WORK / f"{case[0]}-{case[4]}fps-r{case[5]}" / "metrics.json"
        if path.exists():
            rows.append(json.loads(path.read_text()))
        else:
            pending.append(case)
    with ThreadPoolExecutor(max_workers=2) as pool:
        for row in pool.map(run, pending):
            rows.append(row)
            raw_path.write_text(json.dumps(rows, indent=2))
    data = {r["label"]: r for r in rows}
    nondeterministic = [r["label"] for r in rows if r["label"].endswith("r1")
                        and r["sha256_all_frames"] != data[r["label"][:-1]+"2"]["sha256_all_frames"]]
    result = {"jobs": len(rows), "nondeterministic": nondeterministic, "runs": sorted(rows, key=lambda r: r["label"])}
    Path(__file__).with_name(f"results-orb-{phase}.json").write_text(json.dumps(result, indent=2))
    print("nondeterministic", nondeterministic, flush=True)


if __name__ == "__main__":
    main()
