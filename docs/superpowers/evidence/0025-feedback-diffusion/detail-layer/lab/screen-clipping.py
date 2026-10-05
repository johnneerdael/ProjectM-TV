"""Compare authored, Standard, original and fixed detail with deterministic PCM."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading

import cv2
import numpy as np

PICKS = [120, 150, 180, 210, 239, 300, 390, 479]
LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def read_exact(stream, count):
    chunks = bytearray()
    while len(chunks) < count:
        chunk = stream.read(count - len(chunks))
        if not chunk:
            raise RuntimeError(f"truncated capture: {len(chunks)}/{count} bytes")
        chunks.extend(chunk)
    return chunks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--indices", help="comma-separated indices; omit for all 68")
    parser.add_argument("--before", action="store_true")
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()
    repo = Path.cwd().resolve()
    here = Path(__file__).resolve().parent
    records = here.parent / "results/broad-main"
    indices = sorted(int(p.stem) for p in records.glob("*.json"))
    if args.indices:
        indices = [int(i) for i in args.indices.split(",")]
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    workers = json.loads(args.workers.read_text())
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    # Public, reproducible replacement for the original screen's unavailable
    # PCM. The old JSON stays historical; compare all new variants on this PCM.
    t = np.arange(16 * 44100) / 44100
    carrier = sum(0.04 * np.sin(2 * np.pi * f * t) for f in (80, 440, 5000))
    pcm = carrier + 0.15 * ((t % 0.5) < 0.2) * np.sin(2 * np.pi * 80 * t)
    pcm_path = out / "screen.f32"
    pcm.astype("<f4").tofile(pcm_path)
    protocol = {"workers": workers, "pcm_sha256": hashlib.sha256(pcm_path.read_bytes()).hexdigest(),
                "signal": "0.04*sin(80,440,5000 Hz) + 0.15*sin(80 Hz) for first 0.2 s of each 0.5 s",
                "frames": 480, "fps": 30, "seed": 12345, "capture_frames": PICKS,
                "metrics_size": [1182, 665], "indices": indices}
    (out / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")

    def render(index, preset, label, worker, alpha):
        w, h = (1280, 720) if alpha is None else (3840, 2160)
        run = out / "runs" / f"{index}-{label}"
        run.mkdir(parents=True, exist_ok=True)
        config = {"width": w, "height": h, "fps": 30, "warmup_seconds": 4,
                  "measurement_seconds": 12, "line_reference_width": 0 if alpha is None else 1280,
                  "line_reference_height": 0 if alpha is None else 720, "seed": 12345}
        job = {"schema_version": 1, "config": config, "pcm_path": str(pcm_path),
               "preset_path": str(repo / "core/src/main/assets/presets" / preset),
               "texture_root": str(repo / "core/src/main/assets/textures"),
               "bands_path": str(run / "bands.jsonl"), "manifest_path": str(run / "manifest.json"),
               "identity": {"preset": preset, "label": label}}
        (run / "job.json").write_text(json.dumps(job, indent=2) + "\n")
        env = {k: v for k, v in os.environ.items() if not k.startswith("PM_")}
        env["PRESET_LAB_SEED"] = "12345"
        if alpha is not None:
            env["PM_DETAIL"] = str(alpha)
        frames = []
        with (run / "stderr.txt").open("w") as log:
            process = subprocess.Popen([worker, "--job", str(run / "job.json")], env=env,
                                       stdout=subprocess.PIPE, stderr=log)
            deadline = threading.Timer(600, process.kill)
            deadline.start()
            try:
                for frame in PICKS:
                    raw = read_exact(process.stdout, w * h * 3)
                    image = np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 3)
                    if frame == 300:
                        cv2.imwrite(str(run / "frame-300.png"), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                    small = cv2.resize(image.astype(np.float32) / 255, (1182, 665), interpolation=cv2.INTER_AREA)
                    frames.append(small)
                if process.stdout.read(1):
                    raise RuntimeError("worker emitted unexpected extra captures")
                rc = process.wait(timeout=60)
                manifest = json.loads((run / "manifest.json").read_text())
                if rc or manifest["status"] != "success" or manifest["gl_error_frames"]:
                    raise RuntimeError(f"render failed: {run}, exit={rc}, manifest={manifest}")
            finally:
                deadline.cancel()
                if process.poll() is None:
                    process.kill()
                process.wait()
                process.stdout.close()
        return np.stack(frames)

    def one(index):
        preset = json.loads((records / f"{index}.json").read_text())["preset"]
        authored = render(index, preset, "authored", workers["workers"]["authored"]["path"], None)
        reference_luma = float((authored @ LUMA).mean())
        result = {"preset": preset, "authored_luma": reference_luma}
        configs = [("standard", "fixed", 0), ("medium", "fixed", 0.5), ("high", "fixed", 1)]
        if args.before:
            configs += [("before-medium", "before", 0.5), ("before-high", "before", 1),
                        ("before-standard", "before", 0)]
        for label, engine, alpha in configs:
            image = render(index, preset, label, workers["workers"][engine]["path"], alpha)
            luma = float((image @ LUMA).mean())
            result[label] = {"luma": luma, "luma_ratio": luma / reference_luma if reference_luma > 1e-6 else None,
                             "mae": float(np.abs(image - authored).mean()),
                             "frame_luma": [float((f @ LUMA).mean()) for f in image],
                             "capture_digest": hashlib.sha256(image.tobytes()).hexdigest()}
        (out / f"{index}.json").write_text(json.dumps(result, indent=2) + "\n")
        print(index, preset[:55], {k: round(v["luma_ratio"], 4) if v["luma_ratio"] is not None else None
                                 for k, v in result.items() if isinstance(v, dict)}, flush=True)

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        list(pool.map(one, indices))


if __name__ == "__main__":
    main()
