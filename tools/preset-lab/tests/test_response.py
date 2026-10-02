import numpy as np
import pytest

from preset_lab.models import PresetRecord, StaticEvidence
from preset_lab.response import beat_coupling, fingerprint


def trajectory(levels, coverage=1.0, warmup=0, status="success"):
    return {"status": status, "fps": 30, "warmup_frames": warmup, "warnings": [],
            "frames": [{"brightness": float(level), "coverage": coverage,
                        "contrast": 0.2, "saturation": 0.5, "edge_energy": 0.01,
                        "motion_speed": 0.1, "motion_density": 0.4, "rotation": 0,
                        "expansion": 0, "translation_x": 0, "translation_y": 0,
                        "motion_residual": 0.01, "clipping_ratio": 0,
                        "frame_change": 0, "luma_change": 0} for level in levels]}


def characterize(data):
    return fingerprint(PresetRecord("fixture.milk", "a" * 64, 0), data,
                       StaticEvidence(True, [], []))


def test_tiny_dot_does_not_get_full_scene_response_rating():
    base = np.zeros(300)
    pulses = np.zeros(300)
    pulses[::15] = 0.5
    whole = characterize({"steady": trajectory(base), "bass": trajectory(pulses)})
    tiny = characterize({"steady": trajectory(base, 0.0001), "bass": trajectory(pulses, 0.0001)})
    assert whole.raw["spectral_response"]["bass"] > tiny.raw["spectral_response"]["bass"] * 20
    assert not tiny.quality["eligible"]


def test_intrinsic_animation_is_not_audio_response():
    animation = 0.4 + 0.2 * np.sin(np.arange(300) / 4)
    result = characterize({"steady": trajectory(animation), "bass": trajectory(animation)})
    assert result.raw["spectral_response"]["bass"] == pytest.approx(0)


def test_missing_stems_are_unavailable_not_zero():
    result = characterize({"steady": trajectory(np.ones(300) * 0.3)})
    assert result.raw["source_response"]["vocals"] is None
    assert result.raw["source_response"]["drums"] is None
    assert result.raw["source_unavailable_reasons"]["vocals"]


def test_causal_delay_exceeds_shifted_and_shuffled_controls():
    onsets = [20, 61, 103, 150, 202, 261]
    events = np.zeros(300)
    events[np.array(onsets) + 3] = 1
    result = beat_coupling(events, onsets, 30)
    assert result["strength"] > 0.8
    assert result["lag_seconds"] == pytest.approx(0.1)
    assert result["correlation"] > result["control_correlation"]
    assert beat_coupling(np.zeros(300), onsets, 30)["strength"] == 0


def test_flashiness_and_persistence_follow_temporal_evidence():
    calm = characterize({"steady": trajectory(np.ones(300) * 0.3)})
    flashing = characterize({"steady": trajectory(np.tile([0, 1], 150))})
    assert flashing.normalized["flashiness"] > calm.normalized["flashiness"]
    baseline = np.ones(300) * 0.2
    lasting = baseline.copy()
    lasting[:150] += 0.2
    lasting[150:] += 0.2 * np.exp(-np.arange(150) / 80)
    quick = baseline.copy()
    quick[:150] += 0.2
    p = characterize({"steady": trajectory(baseline), "sustained": trajectory(lasting)})
    q = characterize({"steady": trajectory(baseline), "sustained": trajectory(quick)})
    assert p.normalized["persistence"] > q.normalized["persistence"]


def test_warmup_divergence_is_a_quality_failure():
    result = characterize({"steady": trajectory(np.zeros(300), warmup=120),
                           "bass": trajectory(np.ones(300), warmup=120)})
    assert "pre_intervention_drift" in result.quality["reasons"]
    assert not result.quality["eligible"]


def test_missing_probes_do_not_become_complete_measurements():
    result = characterize({"steady": trajectory(np.ones(300) * 0.3)})
    assert not result.quality["eligible"]
    assert "missing_spectral_measurement:bass" in result.quality["reasons"]


def test_still_flat_output_requires_longer_test_then_exclusion():
    def flat(frames):
        item = trajectory(np.ones(frames))
        for frame in item["frames"]:
            frame.update(contrast=0, motion_density=0, motion_speed=0, edge_energy=0)
        return item
    short = characterize({name: flat(300) for name in ("steady", "sub_bass", "bass", "mid", "treble")})
    long = characterize({name: flat(1800) for name in ("steady", "sub_bass", "bass", "mid", "treble")})
    assert not short.quality["eligible"]
    assert short.quality["requires_extension"]
    assert not long.quality["eligible"]
    assert not long.quality["requires_extension"]
    assert "flat_static_output" in long.quality["reasons"]


def test_audio_triggered_flashes_are_not_hidden_by_a_calm_steady_control():
    baseline = trajectory(np.ones(300) * 0.3)
    data = {name: baseline for name in ("steady", "sub_bass", "mid", "treble")}
    data["bass"] = trajectory(np.tile([0, 1], 150))
    result = characterize(data)
    assert result.normalized["flashiness"] > 0.8


def test_image_prefix_drift_is_detected_even_when_feature_means_match():
    data = {name: trajectory(np.ones(300) * 0.3, warmup=120)
            for name in ("steady", "sub_bass", "bass", "mid", "treble")}
    for item in data.values():
        item["prefix_sha256"] = "a" * 64
    data["bass"]["prefix_sha256"] = "b" * 64
    result = characterize(data)
    assert not result.quality["eligible"]
    assert "pre_intervention_drift" in result.quality["reasons"]


def test_beat_visible_scene_is_not_rejected_for_a_dark_steady_carrier():
    data = {name: trajectory(np.zeros(300), coverage=0)
            for name in ("steady", "sub_bass", "mid", "treble")}
    data["bass"] = trajectory(np.tile([0.4, 0.2], 150), coverage=1)
    result = characterize(data)
    assert result.quality["eligible"]
    assert "low_visibility" not in result.quality["reasons"]
