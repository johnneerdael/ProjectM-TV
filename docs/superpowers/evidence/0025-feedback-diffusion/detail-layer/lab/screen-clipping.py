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
from capture_frames import PICKS

LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def verify_workers(path):
    workers = json.loads(path.read_text())
    if set(workers["workers"]) != {"authored", "before", "fixed"}:
        raise ValueError("expected authored, before and fixed workers")
    for label, record in workers["workers"].items():
        actual = hashlib.sha256(Path(record["path"]).read_bytes()).hexdigest()
        if actual != record["sha256"]:
            raise ValueError(f"worker checksum mismatch: {label}")
    picks = workers["capture_frames"]
    if not picks or picks != sorted(set(picks)) or any(type(f) is not int or not 0 <= f < 480 for f in picks):
        raise ValueError("invalid capture frame list")
    if picks != PICKS:
        raise ValueError("capture metadata does not match the worker frame contract")
    return workers


def require_empty_output(out):
    if out.exists() and any(out.iterdir()):
        raise ValueError("screen output must be empty; choose a fresh --out directory")


def kill_process(process):
    try:
        process.kill()
    except ProcessLookupError:
        pass


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
    parser.add_argument("--save-frames", action="store_true", help="save every selected temporal capture")
    parser.add_argument("--timeout", type=float, default=600, help="seconds allowed per worker")
    args = parser.parse_args()
    repo = Path.cwd().resolve()
    here = Path(__file__).resolve().parent
    records = here.parent / "results/broad-main"
    indices = sorted(int(p.stem) for p in records.glob("*.json"))
    if args.indices:
        indices = [int(i) for i in args.indices.split(",")]
    if args.jobs < 1 or not np.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--jobs and --timeout must be positive")
    if len(indices) != len(set(indices)) or any(not (records / f"{i}.json").is_file() for i in indices):
        parser.error("indices must identify distinct presets in the 68-preset screen")
    workers = verify_workers(args.workers)
    picks = workers["capture_frames"]
    out = args.out.resolve()
    require_empty_output(out)
    out.mkdir(parents=True, exist_ok=True)
    # Public, reproducible replacement for the original screen's unavailable
    # PCM. The old JSON stays historical; compare all new variants on this PCM.
    t = np.arange(16 * 44100) / 44100
    carrier = sum(0.04 * np.sin(2 * np.pi * f * t) for f in (80, 440, 5000))
    pcm = carrier + 0.15 * ((t % 0.5) < 0.2) * np.sin(2 * np.pi * 80 * t)
    pcm_path = out / "screen.f32"
    pcm.astype("<f4").tofile(pcm_path)
    asset_root = repo / "core/src/main/assets"
    presets = {i: json.loads((records / f"{i}.json").read_text())["preset"] for i in indices}
    texture_records = [(p.relative_to(asset_root / "textures").as_posix(), hashlib.sha256(p.read_bytes()).hexdigest())
                       for p in sorted((asset_root / "textures").rglob("*")) if p.is_file()]
    assets = {"presets": {name: hashlib.sha256((asset_root / "presets" / name).read_bytes()).hexdigest()
                           for name in presets.values()},
              "textures_sha256": hashlib.sha256(json.dumps(texture_records).encode()).hexdigest(),
              "texture_count": len(texture_records)}
    protocol = {"workers": workers, "pcm_sha256": hashlib.sha256(pcm_path.read_bytes()).hexdigest(),
                "signal": "0.04*sin(80,440,5000 Hz) + 0.15*sin(80 Hz) for first 0.2 s of each 0.5 s",
                "frames": 480, "fps": 30, "seed": 12345, "capture_frames": picks,
                "metrics_size": [1182, 665], "indices": indices, "assets": assets,
                "before_controls": args.before, "saved_frames": picks if args.save_frames else [300]}
    (out / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
    cancelled = threading.Event()
    process_lock = threading.Lock()
    active_processes = set()

    def cancel_renders():
        cancelled.set()
        with process_lock:
            for process in active_processes:
                kill_process(process)

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
            with process_lock:
                if cancelled.is_set():
                    raise RuntimeError("screen cancelled after a render failure")
                process = subprocess.Popen([worker, "--job", str(run / "job.json")], env=env,
                                           stdout=subprocess.PIPE, stderr=log)
                active_processes.add(process)
            timed_out = threading.Event()

            def timeout():
                timed_out.set()
                kill_process(process)

            deadline = threading.Timer(args.timeout, timeout)
            deadline.start()
            try:
                for frame in picks:
                    raw = read_exact(process.stdout, w * h * 3)
                    image = np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 3)
                    if args.save_frames or frame == 300:
                        if not cv2.imwrite(str(run / f"frame-{frame}.png"), cv2.cvtColor(image, cv2.COLOR_RGB2BGR)):
                            raise RuntimeError(f"capture export failed: {run}, frame={frame}")
                    small = cv2.resize(image.astype(np.float32) / 255, (1182, 665), interpolation=cv2.INTER_AREA)
                    frames.append(small)
                if process.stdout.read(1):
                    raise RuntimeError("worker emitted unexpected extra captures")
                rc = process.wait(timeout=60)
                manifest = json.loads((run / "manifest.json").read_text())
                if rc or manifest["status"] != "success" or manifest["gl_error_frames"]:
                    raise RuntimeError(f"render failed: {run}, exit={rc}, manifest={manifest}")
            except Exception as error:
                cancel_renders()
                if timed_out.is_set():
                    raise RuntimeError(f"render timed out after {args.timeout}s: {run}") from None
                rc = process.wait(timeout=60)
                raise RuntimeError(f"{run}: {error}; worker exit={rc}; stderr={run / 'stderr.txt'}") from error
            finally:
                deadline.cancel()
                if process.poll() is None:
                    kill_process(process)
                process.wait()
                process.stdout.close()
                with process_lock:
                    active_processes.discard(process)
        return np.stack(frames)

    def one(index):
        if cancelled.is_set():
            raise RuntimeError("screen cancelled after a render failure")
        preset = presets[index]
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
        result_path = out / f"{index}.json"
        temporary = result_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(result, indent=2) + "\n")
        temporary.replace(result_path)
        print(index, preset[:55], {k: round(v["luma_ratio"], 4) if v["luma_ratio"] is not None else None
                                 for k, v in result.items() if isinstance(v, dict)}, flush=True)

    pool = ThreadPoolExecutor(max_workers=args.jobs)
    try:
        list(pool.map(one, indices))
    except BaseException:
        cancel_renders()
        pool.shutdown(wait=True, cancel_futures=True)
        raise
    else:
        pool.shutdown(wait=True)


if __name__ == "__main__":
    main()
