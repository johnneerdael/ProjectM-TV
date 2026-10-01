import math
import os
import subprocess
import tempfile
import threading
from dataclasses import asdict
from pathlib import Path
from typing import Callable

import numpy as np

from .identity import canonical_json, load_json
from .inventory import valid_filename
from .models import JobSpec, WorkerResult


def validate_job(spec: JobSpec, timeout_seconds: float) -> int:
    config = spec.config
    if not all(type(value) is int for value in (config.width, config.height, config.fps, config.seed)):
        raise ValueError("dimensions, frame rate and seed must be integers")
    if (config.width <= 0 or config.height <= 0 or config.width > 4096 or config.height > 4096
            or config.fps not in (30, 60) or not 0 <= config.seed <= 0xffffffff):
        raise ValueError("invalid render dimensions, frame rate or seed")
    durations = [config.warmup_seconds, config.measurement_seconds, timeout_seconds]
    if not all(math.isfinite(value) for value in durations):
        raise ValueError("non-finite job timing")
    if config.warmup_seconds < 0 or config.measurement_seconds <= 0 or timeout_seconds <= 0:
        raise ValueError("invalid job duration")
    if not valid_filename(spec.preset.path):
        raise ValueError("unsafe preset filename")
    frames = (config.warmup_seconds + config.measurement_seconds) * config.fps
    if not math.isclose(frames, round(frames), abs_tol=1e-8):
        raise ValueError("duration must contain complete frames")
    expected_bytes = round(frames) * (44100 // config.fps) * 4
    if spec.pcm_path.stat().st_size != expected_bytes:
        raise ValueError("PCM length does not match complete job frames")
    return round(frames)


def render_job(worker: Path, spec: JobSpec, on_frame: Callable[[np.ndarray], None],
               timeout_seconds: float) -> WorkerResult:
    frames = validate_job(spec, timeout_seconds)
    spec.work.mkdir(parents=True, exist_ok=True)
    job_dir = Path(tempfile.mkdtemp(prefix="run-", dir=spec.work))
    manifest_path = job_dir / "manifest.json"
    diagnostics = job_dir / "stderr.log"
    job = {"schema_version": 1, "preset_path": str((spec.preset_root / spec.preset.path).resolve()),
           "texture_root": str(spec.texture_root.resolve()), "pcm_path": str(spec.pcm_path.resolve()),
           "config": asdict(spec.config), "identity": asdict(spec.identity),
           "manifest_path": str(manifest_path), "bands_path": str(job_dir / "bands.jsonl")}
    job_path = job_dir / "job.json"
    job_path.write_text(canonical_json(job))
    env = dict(os.environ, PRESET_LAB_SEED=str(spec.config.seed))
    timed_out = threading.Event()
    observed = 0
    with diagnostics.open("wb") as log:
        process = subprocess.Popen([str(worker), "--job", str(job_path)], stdout=subprocess.PIPE,
                                   stderr=log, env=env)
        def expire():
            if process.poll() is None:
                timed_out.set()
                process.kill()
        timer = threading.Timer(timeout_seconds, expire)
        timer.start()
        try:
            frame_size = spec.config.width * spec.config.height * 3
            while True:
                data = process.stdout.read(frame_size)
                if not data:
                    break
                if len(data) != frame_size or observed >= frames:
                    process.kill()
                    break
                frame = np.frombuffer(data, dtype=np.uint8).reshape(spec.config.height, spec.config.width, 3)
                on_frame(frame)
                observed += 1
            exit_code = process.wait()
        finally:
            timer.cancel()
            if process.poll() is None:
                process.kill()
            process.wait()
            process.stdout.close()
    manifest = load_json(manifest_path) if manifest_path.is_file() else {}
    status = "timeout" if timed_out.is_set() else "failed"
    if (not timed_out.is_set() and exit_code == 0 and observed == frames
            and manifest.get("status") == "success" and manifest.get("frames") == frames):
        status = "success"
    manifest.update(status=status, exit_code=exit_code, observed_frames=observed,
                    job_directory=str(job_dir), bands_path=job["bands_path"])
    manifest_path.write_text(canonical_json(manifest))
    return WorkerResult(status, manifest, diagnostics)
