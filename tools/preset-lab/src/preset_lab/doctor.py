import hashlib
import shutil
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .build_worker import build_worker, prepare_engine
from .identity import file_digest
from .models import JobSpec, PresetRecord, RunConfig
from .worker import render_job


def doctor(repo: Path, work: Path, worker: Path | None = None) -> dict:
    tools = {name: shutil.which(name) for name in ("cmake", "ffmpeg", "ffprobe")}
    if not all(tools.values()):
        return {"healthy": False, "tools": tools, "repeatability": [], "error": "required tools missing"}
    _, identity = prepare_engine(repo, work)
    worker = worker or build_worker(repo, work)
    assets = work / "doctor"
    assets.mkdir(parents=True, exist_ok=True)
    base = ("MILKDROP_PRESET_VERSION=201\n[preset00]\nfGammaAdj=1\nfDecay=0.98\nnWaveMode=0\nfWaveScale=1\n"
            "fWaveAlpha=1\nwave_r=1\nwave_g=0.4\nwave_b=0.2\n")
    cases = {
        "waveform": base + "per_frame_1=zoom=1+0.01*bass;\n",
        "noise": base + "PSVERSION_WARP=2\nwarp_1=`shader_body\nwarp_2=`{\n"
                 "warp_3=`ret=tex2D(sampler_noise_lq,uv).xyz;\nwarp_4=`}\n",
        "shader": base + "PSVERSION_WARP=2\nwarp_1=`shader_body\nwarp_2=`{\n"
                  "warp_3=`ret=tex2D(sampler_rand00,uv).xyz*(0.5+0.2*sin(time)+0.1*bass);\nwarp_4=`}\n",
    }
    config = RunConfig(width=64, height=36, measurement_seconds=2)
    times = np.arange(6 * 44100) / 44100
    steady = sum(0.04 * np.sin(2 * np.pi * frequency * times) for frequency in (80, 440, 5000))
    intervention = steady.copy()
    intervention[times >= 4] += (0.12 * np.sin(2 * np.pi * 80 * times[times >= 4])
                                 * ((times[times >= 4] * 2) % 1 < 0.25))
    steady.astype("<f4").tofile(assets / "steady.f32")
    intervention.astype("<f4").tofile(assets / "intervention.f32")
    checks, backend = [], {}
    for name, code in cases.items():
        preset = assets / f"{name}.milk"
        preset.write_text(code)
        record = PresetRecord(preset.name, file_digest(preset), 0)
        hashes, prefixes, statuses = [], [], []
        for stimulus in ("steady", "steady", "intervention"):
            full, prefix = hashlib.sha256(), hashlib.sha256()
            observed = 0
            def observe(frame):
                nonlocal observed
                full.update(frame.tobytes())
                if observed < config.warmup_seconds * config.fps:
                    prefix.update(frame.tobytes())
                observed += 1
            job = JobSpec(record, stimulus, assets / f"{stimulus}.f32", config, identity,
                          assets, repo / "core/src/main/assets/textures", assets / "jobs")
            result = render_job(worker, job, observe, 120)
            statuses.append(result.status)
            hashes.append(full.hexdigest())
            prefixes.append(prefix.hexdigest())
            if result.status == "success":
                backend = {key: result.manifest.get(key) for key in ("gl_version", "gl_renderer")}
        checks.append({"case": name, "same_input_equal": hashes[0] == hashes[1],
                       "common_prefix_equal": len(set(prefixes)) == 1,
                       "statuses": statuses, "hashes": hashes})
    healthy = all(c["same_input_equal"] and c["common_prefix_equal"]
                  and c["statuses"] == ["success"] * 3 for c in checks)
    return {"healthy": healthy, "tools": tools, "worker": str(worker),
            "identity": asdict(identity), "backend": backend, "repeatability": checks,
            "desktop_discard_hint": "no-op on Apple OpenGL; timings are desktop-only"}
