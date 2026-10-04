"""Reproduce geometry and low-height evidence with linear metrics and lossless frames.

Use the preset-lab Python environment. Each job renders twice, 30 fps, bass-0.30,
4 seconds warm-up and 4 seconds measurement. Geometry reads the canvas through a
point sampler snapped using actual render dimensions, independent of virtual texsize.
"""

import argparse
import hashlib
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools/preset-lab/src"))
from preset_lab.bass_screen import bass_signals
from preset_lab.models import EngineIdentity, JobSpec, PresetRecord, RunConfig
from preset_lab.worker import render_job
from synthetic_source import presets

LUMA = np.array([0.2126, 0.7152, 0.0722])


@dataclass(frozen=True, slots=True)
class Config(RunConfig):
    line_reference_width: int = 0
    line_reference_height: int = 0


def synthetic():
    result = presets()
    for shape in ("circle", "wiggle"):
        result[f"blend-cw-{shape}-thick"] = result[f"hit-cw-{shape}-thick"].replace(
            "wavecode_0_bAdditive=1", "wavecode_0_bAdditive=0"
        ).replace("wavecode_0_a=0.125", "wavecode_0_a=0.5")
    for thick in ("thin", "thick"):
        result[f"dot-mw-circle-{thick}"] = result[f"hit-mw-circle-{thick}"].replace(
            "bWaveDots=0", "bWaveDots=1"
        )
        result[f"dot-cw-circle-{thick}"] = result[f"hit-cw-circle-{thick}"].replace(
            "wavecode_0_bUseDots=0", "wavecode_0_bUseDots=1"
        )
    return result


def canvas_preset(text, width, height):
    text = text.replace("PSVERSION=0", "PSVERSION=2").replace("PSVERSION_COMP=0", "PSVERSION_COMP=2")
    return text + (
        "comp_1=`shader_body\ncomp_2=`{\n"
        f"comp_3=`float2 size = float2({width}.0, {height}.0);\n"
        "comp_4=`ret = tex2D(sampler_pc_main, (floor(uv*size - 0.5) + 0.5)/size).xyz;\n"
        "comp_5=`}\n"
    )


def run_one(args):
    name, text, key, width, height, quad, worker_name, repeat, work, pcm, *timing = args
    fps, warmup_seconds, measurement_seconds = timing[0] if timing else (30, 4, 4)
    warmup_frames = round(fps * warmup_seconds)
    measurement_frames = round(fps * measurement_seconds)
    picks = {warmup_frames + round(i * (measurement_frames-1) / 4) for i in range(5)}
    label = f"{name}-{key}-{worker_name}-r{repeat}"
    directory = work / "jobs" / label
    directory.mkdir(parents=True, exist_ok=True)
    if text is not None:
        preset_root = directory
        content = canvas_preset(text, width, height) if name.startswith(("hit-", "dot-", "blend-")) else text
        (directory / f"{name}.milk").write_text(content)
        filename = f"{name}.milk"
    else:
        preset_root = ROOT / "core/src/main/assets/presets"
        filename = name
    worker = json.loads((ROOT / f"build/follow-ups/worker-{worker_name}.json").read_text())
    config = Config(width=width, height=height, fps=fps, warmup_seconds=warmup_seconds, measurement_seconds=measurement_seconds,
                    line_reference_width=1024 if quad else 0,
                    line_reference_height=768 if quad else 0)
    spec = JobSpec(PresetRecord(filename, "", 0), "bass-0.30", pcm, config,
                   EngineIdentity(**worker["identity"]), preset_root,
                   ROOT / "core/src/main/assets/textures", directory / "worker")
    sha = hashlib.sha256()
    frame_hashes, lumas, centers, saturation, five = [], [], [], [], []
    geometry = []
    sharpness_native, sharpness_reference, sharpness_picture = [], [], []
    count = 0

    def observe(frame):
        nonlocal count
        index = count
        count += 1
        sha.update(frame)
        if index < warmup_frames:
            return
        frame_hashes.append(hashlib.sha256(frame).hexdigest())
        lumas.append(float(frame.mean(axis=(0, 1)) @ LUMA / 255))
        center = frame[int(height*.45):int(height*.55), int(width*.45):int(width*.55)]
        centers.append((center.mean(axis=(0, 1)) / 255).tolist())
        if index in picks:
            small = cv2.resize(frame, (1182, 665), interpolation=cv2.INTER_AREA)
            five.append(small.copy())
            values = small.astype(np.float32) / 255
            maximum, minimum = values.max(axis=2), values.min(axis=2)
            saturation.append(float(((maximum-minimum) / np.maximum(maximum, 1e-6)).mean()))
            for data, destination in ((frame, sharpness_native), (small, sharpness_reference),
                                      (cv2.resize(frame, (591, 332), interpolation=cv2.INTER_AREA), sharpness_picture)):
                grey = data @ LUMA / 255
                destination.append(float(cv2.Laplacian(grey, cv2.CV_64F, ksize=3).var()))
            green = frame[..., 1].astype(np.float64)
            item = {"linear_green_share": float(green.mean() / 255),
                    "lit_share": float((green > 0).mean())}
            if name.startswith("hit-"):
                # Only decode discrete hits after verifying point-sampled, quantized values.
                hits = green / 31.875
                lit = hits > .02
                non_integer = (np.abs(hits - np.rint(hits)) > .02) & lit
                item["non_integer_share_of_lit"] = float(non_integer.sum() / max(1, lit.sum()))
                if not non_integer.any():
                    integers = np.rint(hits[lit]).astype(np.int32)
                    hist = np.bincount(np.minimum(integers, 8), minlength=9)[1:]
                    item["hit_histogram"] = (hist / max(1, hist.sum())).tolist()
            geometry.append(item)

    result = render_job(Path(worker["exe"]), spec, observe, 600)
    if result.status != "success":
        raise RuntimeError(f"{label}: {result.status}, {result.diagnostics_path}")
    frames_path = directory / "five.npz"
    np.savez_compressed(frames_path, frames=np.stack(five))
    metrics = {"name": name, "key": key, "worker": worker_name, "repeat": repeat,
               "size": [width, height], "reference": [config.line_reference_width, config.line_reference_height],
               "identity": worker["identity"], "frames": count, "sha256_all_frames": sha.hexdigest(),
               "timing": {"fps": fps, "warmup_seconds": warmup_seconds, "measurement_seconds": measurement_seconds},
               "diagnostic_switches": worker.get("diagnostic_switches", {}),
               "sha256_measurement_frames": frame_hashes, "luma": float(np.mean(lumas)),
               "center_rgb": np.mean(centers, axis=0).tolist(), "saturation": float(np.mean(saturation)),
               "sharpness": {"native": float(np.mean(sharpness_native)), "reference": float(np.mean(sharpness_reference)),
                             "picture": float(np.mean(sharpness_picture))},
               "five_frames": str(frames_path.relative_to(work)), "canvas_metrics": geometry,
               "diagnostics": str(result.diagnostics_path.relative_to(work))}
    (directory / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"{label}: {metrics['luma']:.6f}", flush=True)
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("geometry", "low-real", "low-nosmooth", "diffusion-focus"))
    parser.add_argument("--filter", default="")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--classic-worker", default="classic")
    parser.add_argument("--extra-preset", action="append", default=[])
    args = parser.parse_args()
    work = ROOT / "build/follow-ups/verification" / args.phase
    work.mkdir(parents=True, exist_ok=True)
    pcm = bass_signals(RunConfig(fps=30, warmup_seconds=4, measurement_seconds=4), work / "signals")["bass-0.30"]
    if args.phase == "geometry":
        selected = synthetic()
    elif args.phase == "diffusion-focus":
        selected = {name: None for name in (
            "$$$ Royal - Mashup (103).milk", "$$$ Royal - Mashup (191).milk", "Serge circles005b.milk",
            "suksma - ed geining hateops - Matrix Moral Infinite.milk",
            "Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk",
            "TonyMilkdrop - I Like Cartoon --- Isosceles edit.milk",
            "TonyMilkdrop - Nuclear [Flexi - help out + alien complex].milk",
            "suksma - penattrition - geiss crossfire shaders.milk", "rce-ordinary - want.milk",
            "Flexi - alien complex 03.milk", "fat cancer tour meant t nz+.milk",
        )}
    else:
        selected = {name: None for name in (
            "$$$ Royal - Mashup (103).milk", "$$$ Royal - Mashup (191).milk",
            "Serge circles005b.milk", "Flexi - alien complex 03.milk",
            "fat cancer tour meant t nz+.milk", "TonyMilkdrop - I Like Cartoon --- Isosceles edit.milk",
            "Geiss - Surface (1-02 Version).milk",
        )}
    for name in args.extra_preset:
        selected[name] = None
    selected = {name: value for name, value in selected.items() if re.search(args.filter, name)}
    configurations = [("c665", 1182, 665, False, "final"), ("old-c665", 1182, 665, False, "classic")]
    for width, height in ((640, 360), (854, 480), (960, 540)):
        configurations += [(f"c{height}", width, height, False, "final"),
                           (f"old-c{height}", width, height, False, "classic"),
                           (f"q{height}", width, height, True, "final")]
    if args.phase == "low-nosmooth":
        configurations = [(key, w, h, q, "nosmooth") for key, w, h, q, _ in configurations
                          if not key.startswith("old-")]
    else:
        configurations = [(key, w, h, q, args.classic_worker if worker == "classic" else worker)
                          for key, w, h, q, worker in configurations]
    if args.phase == "geometry":
        configurations += [("q665", 1182, 665, True, "final"),
                           ("q1080", 1920, 1080, True, "final"),
                           ("q2160", 3840, 2160, True, "final")]
    if args.phase == "diffusion-focus":
        configurations = [("c665", 1182, 665, False, "diagnostics-fixed"),
                          ("c656", 1166, 656, False, "diagnostics-fixed"),
                          ("c675", 1200, 675, False, "diagnostics-fixed")]
        for key, width, height in (("1330", 2364, 1330), ("2160", 3840, 2160)):
            configurations += [("q" + key, width, height, True, "diagnostics-fixed"),
                               ("diff" + key, width, height, True, "diffusion-safe-on")]
    jobs = [(name, text, *config, repeat, work, pcm) for name, text in selected.items()
            for config in configurations for repeat in (1, 2)]
    results = []
    pending = []
    for job in jobs:
        name, _, key, _, _, _, worker, repeat, *_ = job
        path = work / "jobs" / f"{name}-{key}-{worker}-r{repeat}" / "metrics.json"
        if path.exists():
            results.append(json.loads(path.read_text()))
        else:
            pending.append(job)
    print(f"{len(pending)} pending jobs; {len(results)} cached", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for metrics in pool.map(run_one, pending):
            results.append(metrics)
            (work / "raw.json").write_text(json.dumps(results, indent=2))
    (work / "raw.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
