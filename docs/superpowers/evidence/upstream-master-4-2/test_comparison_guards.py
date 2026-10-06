import importlib.util
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
