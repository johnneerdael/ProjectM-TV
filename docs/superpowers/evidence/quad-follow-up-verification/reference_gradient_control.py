"""Positive control: copying onto a smaller grid must preserve a full-frame gradient."""

import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

from measure import Config, EngineIdentity, JobSpec, PresetRecord, ROOT, render_job


PRESET = """MILKDROP_PRESET_VERSION=201
PSVERSION_WARP=3
PSVERSION_COMP=3
[preset00]
fDecay=1
fGammaAdj=1
fWaveAlpha=0
fVideoEchoAlpha=0
fShader=0
zoom=1
rot=0
warp=0
fZoomExponent=1
bTexWrap=0
warp_1=`shader_body { if (frame < 2) ret = float3(uv_orig.x,uv_orig.y,0.25); else ret = tex2D(sampler_main,uv_orig).xyz; }
comp_1=`shader_body { ret = tex2D(sampler_main,uv).xyz; }
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--linear", action="store_true")
    args = parser.parse_args()
    worker_prefix = "reference-feedback-linear" if args.linear else "reference-feedback"
    work = ROOT / "build/follow-ups/verification" / (worker_prefix+"-gradient-control")
    work.mkdir(parents=True, exist_ok=True)
    pcm = work / "silence.f32"
    np.zeros(3*1470, dtype="<f4").tofile(pcm)
    rows = []
    for variant in ("off", "on"):
        for repeat in (1, 2):
            directory = work / f"{variant}-r{repeat}"
            directory.mkdir(parents=True, exist_ok=True)
            name = "reference-gradient.milk"
            (directory / name).write_text(PRESET)
            worker = json.loads((ROOT / f"build/follow-ups/worker-{worker_prefix}-{variant}.json").read_text())
            config = Config(width=2364, height=1330, fps=30, warmup_seconds=0, measurement_seconds=.1,
                            line_reference_width=1024, line_reference_height=768)
            spec = JobSpec(PresetRecord(name, "", 0), "silence", pcm, config, EngineIdentity(**worker["identity"]),
                           directory, ROOT / "core/src/main/assets/textures", directory / "worker")
            hashes, frames = [], []
            def observe(frame):
                hashes.append(hashlib.sha256(frame).hexdigest())
                frames.append(cv2.resize(frame, (1182, 665), interpolation=cv2.INTER_AREA))
            result = render_job(Path(worker["exe"]), spec, observe, 120)
            if result.status != "success":
                raise RuntimeError(str(result.diagnostics_path))
            rgb = frames[-1].mean(axis=(0, 1))/255
            mae = float(np.abs(frames[-1].astype(np.float32)-frames[1].astype(np.float32)).mean()/255)
            assert .49 < rgb[0] < .51 and .49 < rgb[1] < .51, rgb
            assert mae < .002, mae
            for i, frame in enumerate(frames):
                cv2.imwrite(str(directory / f"frame-{i}.png"), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            rows.append({"variant": variant, "repeat": repeat, "identity": worker["identity"],
                         "frame_hashes": hashes, "final_rgb": rgb.tolist(), "copy_difference_mae": mae})
    for variant in ("off", "on"):
        pair = [r for r in rows if r["variant"] == variant]
        assert pair[0]["frame_hashes"] == pair[1]["frame_hashes"], variant
    Path(__file__).with_name("results-"+worker_prefix+"-gradient-control.json").write_text(json.dumps(rows, indent=2))
    print("Full-frame gradient and repeat controls pass", flush=True)


if __name__ == "__main__":
    main()
