import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

from preset_lab.models import EngineIdentity, JobSpec, PresetRecord, RunConfig
from preset_lab.worker import render_job


def make_job(tmp_path, **changes):
    pcm = tmp_path / "input.f32"
    np.zeros(4410, dtype="<f4").tofile(pcm)
    preset = tmp_path / "fixture.milk"
    preset.write_text("[preset00]\nfWaveAlpha=1\nfWaveScale=1\n")
    return JobSpec(PresetRecord(preset.name, "a" * 64, 0), "silence", pcm,
                   RunConfig(width=2, height=2, warmup_seconds=0,
                             measurement_seconds=0.1, **changes),
                   EngineIdentity("b" * 40, "c" * 64, "d" * 64),
                   preset_root=tmp_path, texture_root=tmp_path, work=tmp_path / "jobs")


def fake_worker(tmp_path, mode):
    path = tmp_path / "fake-worker"
    path.write_text(f"#!{sys.executable}\n" + """
import json,sys,time
from pathlib import Path
job=json.loads(Path(sys.argv[2]).read_text())
""" + {
        "success": "sys.stdout.buffer.write(bytes([42]) * 36)\nPath(job['manifest_path']).write_text(json.dumps({'status':'success','frames':3,'width':2,'height':2}))\n",
        "truncated": "sys.stdout.buffer.write(bytes([42]) * 12)\n",
        "error": "print('deliberate load failure',file=sys.stderr)\nsys.exit(3)\n",
        "timeout": "time.sleep(10)\n",
        "noisy": "sys.stderr.write('diagnostic' * 100000)\nsys.stdout.buffer.write(bytes([42]) * 36)\nPath(job['manifest_path']).write_text(json.dumps({'status':'success','frames':3,'width':2,'height':2}))\n",
    }[mode])
    path.chmod(0o755)
    return path


def test_worker_streams_complete_frames(tmp_path):
    frames = []
    result = render_job(fake_worker(tmp_path, "success"), make_job(tmp_path), frames.append, 2)
    assert result.status == "success"
    assert len(frames) == 3
    assert frames[0].shape == (2, 2, 3)
    assert np.all(frames[0] == 42)


@pytest.mark.parametrize("mode,status", [("error", "failed"), ("truncated", "failed"),
                                        ("timeout", "timeout")])
def test_worker_reports_failures_without_success(tmp_path, mode, status):
    result = render_job(fake_worker(tmp_path, mode), make_job(tmp_path), lambda f: None,
                        0.25 if mode == "timeout" else 2)
    assert result.status == status
    assert result.manifest["status"] == status
    assert result.diagnostics_path.is_file()


def test_verbose_worker_does_not_deadlock(tmp_path):
    result = render_job(fake_worker(tmp_path, "noisy"), make_job(tmp_path), lambda f: None, 2)
    assert result.status == "success"
    assert result.diagnostics_path.stat().st_size >= 900000


@pytest.mark.parametrize("changes", [{"fps": 0}, {"width": -1}, {"width": 1.5}, {"fps": True}, {"fps": 59},
                                    {"seed": -1}, {"measurement_seconds": float("nan")}])
def test_invalid_job_rejected_before_launch(tmp_path, changes):
    fields = dict(width=2, height=2, warmup_seconds=0, measurement_seconds=0.1)
    fields.update(changes)
    job = make_job(tmp_path)
    from dataclasses import replace
    job = replace(job, config=RunConfig(**fields))
    with pytest.raises(ValueError):
        render_job(tmp_path / "must-not-launch", job, lambda f: None, 1)


@pytest.mark.native
def test_actual_native_frames_are_repeatable(tmp_path):
    path = os.environ.get("PRESET_LAB_WORKER")
    if not path:
        pytest.skip("set PRESET_LAB_WORKER for the real OpenGL check")
    from dataclasses import replace
    job = make_job(tmp_path)
    job = replace(job, config=RunConfig(width=64, height=36, warmup_seconds=0,
                                       measurement_seconds=0.1))
    hashes = []
    for _ in range(2):
        frames = []
        result = render_job(Path(path), job, lambda f: frames.append(f.copy()), 30)
        assert result.status == "success", result.manifest
        assert len(frames) == 3
        hashes.append(hashlib.sha256(b"".join(f.tobytes() for f in frames)).hexdigest())
    assert hashes[0] == hashes[1]
