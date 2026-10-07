import importlib.util
import json
from contextlib import nullcontext
from pathlib import Path
import sys

import pytest

spec = importlib.util.spec_from_file_location("comparison_guards", Path(__file__).with_name("compare_actual_core.py"))
comparison = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = comparison
spec.loader.exec_module(comparison)


def prepare(monkeypatch, user=0, power="mWakefulness=Awake"):
    helpers = {"runner": "frozen"}
    monkeypatch.setattr(comparison, "helper_hashes", lambda: helpers)
    monkeypatch.setattr(comparison.trails, "current_user", lambda device: user)
    monkeypatch.setattr(comparison.trails, "shell", lambda *args: power)
    return helpers


def test_sleeping_between_jobs_stops_without_wake(monkeypatch):
    helpers = prepare(monkeypatch)
    comparison.require_session("owned-device", 0, helpers)
    monkeypatch.setattr(comparison.trails, "shell", lambda *args: "mWakefulness=Asleep")
    with pytest.raises(ValueError, match="without waking"):
        comparison.require_session("owned-device", 0, helpers)


def test_changed_foreground_user_stops_captured_scope(monkeypatch):
    helpers = prepare(monkeypatch, user=10)
    with pytest.raises(ValueError, match="user changed"):
        comparison.require_session("owned-device", 0, helpers)


def test_changed_helper_refuses_before_device_queries(monkeypatch):
    prepare(monkeypatch)
    monkeypatch.setattr(comparison.trails, "current_user", lambda device: pytest.fail("device queried after helper mismatch"))
    with pytest.raises(ValueError, match="helper source changed"):
        comparison.require_session("owned-device", 0, {"runner": "another-revision"})


@pytest.mark.parametrize("power", ["mWakefulness=AwakeElsewhere", "mWakefulness=Awake\nmInteractive=false"])
def test_ambiguous_or_noninteractive_state_is_not_awake(monkeypatch, power):
    helpers = prepare(monkeypatch, power=power)
    with pytest.raises(ValueError, match="without waking"):
        comparison.require_session("owned-device", 0, helpers)


def test_bounded_resume_counts_new_renders_and_reverifies_cached_jobs(monkeypatch, tmp_path):
    prepare(monkeypatch)
    monkeypatch.setattr(comparison.trails, "check_artifacts", lambda identity: None)
    monkeypatch.setattr(comparison.trails, "install_worker", lambda *args: None)
    monkeypatch.setattr(comparison.trails.corpus, "session_lock", lambda *args: nullcontext())
    monkeypatch.setattr(comparison.trails.corpus, "signal", lambda: (None, b"fixed-pcm"))
    workers = {}
    for role, engine, count, source in (
        ("baseline", "e0b0a967f0ffd7d332106c366668ed271718472b", 44, "b1bb994dbfaa04159630570cd9b2c255b173a6bd"),
        ("candidate", "6f64807467e312034883a4389e6aa80a675458bc", 3, "9f131997ef6aac61b2ada4dd05316113f39a720b"),
    ):
        directory = tmp_path / role
        directory.mkdir()
        (directory / "identity.json").write_text(json.dumps({
            "package": "nl.neerdael.projectmtv.corpusrebase" + role,
            "engine_commit": engine, "ordered_patches": ["patch"] * count,
            "source_commit": source, "abi": "armeabi-v7a", "assets_sha256": "same-assets",
        }))
        workers[role] = directory
    rendered, cached = [], []

    def render(device, identity, request, directory, *args):
        path = directory / "manifest.json"
        if path.exists():
            cached.append(directory.name)
            return json.loads(path.read_text())
        rendered.append(directory.name)
        status = "standard " + ("inactive (render 1080p)" if request["height"] == 1080 else "1280×720")
        manifest = {"status": "ok", "nativeTrailsStatus": status, "captures": [{"rgbSha256": "image-hash"}]}
        comparison.trails.write(path, manifest)
        return manifest

    monkeypatch.setattr(comparison.trails, "render", render)
    work = tmp_path / "comparison"

    def run(limit):
        monkeypatch.setattr(sys, "argv", ["compare_actual_core.py", "--device", "owned-device",
            "--baseline", str(workers["baseline"]), "--candidate", str(workers["candidate"]),
            "--work", str(work), "--limit", str(limit)])
        comparison.main()

    run(4)
    assert len(rendered) == 4
    run(4)
    assert len(rendered) == 8
    assert len(cached) == 4
    assert len(json.loads((work / "progress.json").read_text())["rows"]) == 8
    run(0)
    assert len(rendered) == 32
    run(4)
    assert len(rendered) == 32
    assert len(json.loads((work / "progress.json").read_text())["rows"]) == 32
