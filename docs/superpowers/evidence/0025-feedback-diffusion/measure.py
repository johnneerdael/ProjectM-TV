"""Lossless fidelity measurement against classic 1182x665, with full frame hashes."""
import argparse
import fcntl
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
import cv2
import numpy as np
from preset_lab.bass_screen import bass_signals
from preset_lab.models import EngineIdentity, JobSpec, PresetRecord, RunConfig
from preset_lab.worker import render_job

REPO = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
SCRATCH = REPO / "build/diffusion"
LUMA = np.array([.2126, .7152, .0722], dtype=np.float32)

def signal(seconds):
    directory = SCRATCH / f"signals-common-{seconds}"
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        marker = directory / "ready.json"
        if marker.exists():
            pcm = Path(json.loads(marker.read_text())["pcm"])
        else:
            config = RunConfig(width=1920, height=1080, fps=30, warmup_seconds=4,
                               measurement_seconds=seconds)
            pcm = bass_signals(config, directory)["bass-0.30"]
            marker.write_text(json.dumps({"pcm": str(pcm)}) + "\n")
        assert pcm.stat().st_size == (4 + seconds) * 44100 * 4
        return pcm

@dataclass(frozen=True, slots=True)
class Config(RunConfig):
    line_reference_width: int = 0
    line_reference_height: int = 0

def measure(preset, worker, width, height, reference=(1024, 768), seconds=4, repeat=0, preset_root=None):
    info = json.loads((EVIDENCE / f"worker-{worker}.json").read_text())
    key = hashlib.sha256(json.dumps([preset, worker, width, height, reference, seconds, repeat, info["identity"]]).encode()).hexdigest()
    locks = SCRATCH / "measurement-locks"
    locks.mkdir(parents=True, exist_ok=True)
    # Sets overlap. Serialize identical jobs across processes so metrics/PNGs cannot race.
    with (locks / key).open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _measure(preset, worker, width, height, reference, seconds, repeat, preset_root)

def _measure(preset, worker, width, height, reference, seconds, repeat, preset_root):
    info = json.loads((EVIDENCE / f"worker-{worker}.json").read_text())
    config = Config(width=width, height=height, fps=30, warmup_seconds=4,
                    measurement_seconds=seconds, line_reference_width=reference[0],
                    line_reference_height=reference[1])
    pcm = signal(seconds)
    key = hashlib.sha256(json.dumps([preset, worker, width, height, reference, seconds, repeat, info["identity"]]).encode()).hexdigest()
    output = EVIDENCE / "runs" / key
    output.mkdir(parents=True, exist_ok=True)
    result_file = output / "metrics.json"
    if result_file.exists():
        try:
            saved = json.loads(result_file.read_text())
        except (OSError, json.JSONDecodeError):
            saved = {}
        def complete_png(path):
            try:
                with path.open("rb") as stream:
                    if stream.read(8) != b"\x89PNG\r\n\x1a\n": return False
                    stream.seek(-12, 2)
                    return stream.read() == b"\x00\x00\x00\x00IEND\xaeB`\x82"
            except (OSError, ValueError):
                return False
        if saved.get("status") == "success" and all(complete_png(output / f"frame-{i}.png") for i in range(5)):
            return saved
    job = JobSpec(PresetRecord(preset, "", 0), "diffusion", pcm, config,
                  EngineIdentity(**info["identity"]), preset_root or REPO / "core/src/main/assets/presets",
                  REPO / "core/src/main/assets/textures", SCRATCH / "jobs")
    warm = config.fps * 4
    picks = {warm + round(i * (config.fps * seconds - 1) / 4): i for i in range(5)}
    index, total, hashes = 0, hashlib.sha256(), []
    lumas, centres, saturations, lap_native, lap_small = [], [], [], [], []
    def observe(frame):
        nonlocal index
        total.update(frame)
        hashes.append(hashlib.sha256(frame).hexdigest())
        if index >= warm:
            lumas.append(float(frame.reshape(-1, 3).mean(axis=0) @ LUMA / 255))
            centres.append(frame[int(height*.45):int(height*.55), int(width*.45):int(width*.55)].reshape(-1, 3).mean(axis=0)/255)
            small = cv2.resize(frame, (1182, 665), interpolation=cv2.INTER_AREA)
            values = small.astype(np.float32)
            mx, mn = values.max(axis=2), values.min(axis=2)
            saturations.append(float(((mx-mn)/np.maximum(mx, 1)).mean()))
            if index in picks:
                lap_native.append(float(cv2.Laplacian(frame.astype(np.float32) @ LUMA / 255, cv2.CV_32F).var()))
                lap_small.append(float(cv2.Laplacian(values @ LUMA / 255, cv2.CV_32F).var()))
                assert cv2.imwrite(str(output / f"frame-{picks[index]}.png"), cv2.cvtColor(small, cv2.COLOR_RGB2BGR)), "PNG write failed"
        index += 1
    start = time.monotonic()
    result = render_job(Path(info["exe"]), job, observe, 1800)
    data = {"preset": preset, "worker": worker, "identity": info["identity"],
            "config": {"width": width, "height": height, "reference": reference, "window_s": seconds,
                       "warmup_s": 4, "fps": 30, "repeat": repeat, "audio": "bass-0.30", "seed": config.seed},
            "status": result.status, "frames": index, "sha256": total.hexdigest(), "frame_hashes": hashes,
            "diagnostics": str(result.diagnostics_path), "output": str(output), "elapsed_s": time.monotonic()-start}
    if lumas:
        data.update(luma=float(np.mean(lumas)), min_luma=min(lumas), centre_rgb=np.mean(centres,axis=0).tolist(),
                    saturation=float(np.mean(saturations)), lap_native=float(np.mean(lap_native)),
                    lap_1182=float(np.mean(lap_small)))
    result_file.write_text(json.dumps(data, indent=2) + "\n")
    return data

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("worker"); p.add_argument("preset")
    p.add_argument("--size", default="2364x1330"); p.add_argument("--reference", default="1024x768")
    p.add_argument("--seconds", type=int, default=4); p.add_argument("--repeat", type=int, default=0)
    args = p.parse_args()
    data = measure(args.preset, args.worker, *map(int,args.size.split("x")),
                   reference=tuple(map(int,args.reference.split("x"))), seconds=args.seconds, repeat=args.repeat)
    print(json.dumps({k:v for k,v in data.items() if k not in ["frame_hashes", "identity"]},indent=2))
    assert data["status"] == "success", Path(data["diagnostics"]).read_text()
