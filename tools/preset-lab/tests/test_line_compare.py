from dataclasses import asdict

import numpy as np
import pytest

from preset_lab.line_compare import (LineRunConfig, ladder_drift, line_features, luma_ratio,
                                     exit_code, mean_luma, summarize)


def test_mean_luma_of_white_is_one_and_of_black_zero():
    assert mean_luma(np.full((4, 4, 3), 255, np.uint8)) == pytest.approx(1)
    assert mean_luma(np.zeros((4, 4, 3), np.uint8)) == 0


def test_mean_luma_weights_green_most():
    green = np.zeros((2, 2, 3), np.uint8)
    green[..., 1] = 255
    blue = np.zeros((2, 2, 3), np.uint8)
    blue[..., 2] = 255
    assert mean_luma(green) == pytest.approx(.7152, abs=1e-4)
    assert mean_luma(blue) == pytest.approx(.0722, abs=1e-4)


def test_mean_luma_rejects_non_rgb_frames():
    with pytest.raises(ValueError):
        mean_luma(np.zeros((2, 2), np.uint8))
    with pytest.raises(ValueError):
        mean_luma(np.zeros((2, 2, 3), np.float32))


def test_ratio_and_drift_skip_black_images():
    assert luma_ratio(0.0, .5) is None
    assert luma_ratio(.2, .3) == pytest.approx(1.5)
    assert ladder_drift(.1, 0.0) is None
    assert ladder_drift(.09, .1) == pytest.approx(.1)


def test_run_config_carries_line_reference_height():
    assert asdict(LineRunConfig(width=1920, height=1080, line_reference_height=1080))["line_reference_height"] == 1080
    assert asdict(LineRunConfig())["line_reference_height"] == 0


def test_features_use_first_key_and_enabled_elements():
    text = ("bWaveThick=1\nbWaveThick=0\n"
            "wavecode_0_enabled=1\nwavecode_0_bDrawThick=1\n"
            "wavecode_1_enabled=1\nwavecode_1_bUseDots=1\n"
            "shapecode_0_enabled=1\nshapecode_0_border_a=0.5\nshapecode_0_thickOutline=1\n"
            "mv_a=0.4\n")
    assert line_features(text) == ["main_thick", "custom_dots", "custom_thick", "shape_thick", "motion_vectors"]


def test_disabled_waves_and_borderless_shapes_have_no_features():
    text = ("wavecode_0_enabled=0\nwavecode_0_bDrawThick=1\n"
            "shapecode_0_enabled=1\nshapecode_0_border_a=0\nshapecode_0_thickOutline=1\n")
    assert line_features(text) == ["main_thin"]


def test_motion_vectors_from_the_legacy_switch_unless_mv_a_is_zero():
    assert "motion_vectors" in line_features("bMotionVectorsOn=1\n")
    assert "motion_vectors" not in line_features("bMotionVectorsOn=1\nmv_a=0\n")


def test_features_ignore_unparsable_values():
    assert line_features("bWaveThick=e\nbWaveDots=1\n") == ["main_dots"]


def _entry(name, ratio, legacy_hash="a", features=("main_thin",), drift=None):
    runs = {"legacy-1080": {"status": "success", "mean_luma": .2, "frames_sha256": legacy_hash},
            "quad-1080": {"status": "success", "mean_luma": .2 * (ratio or 0), "frames_sha256": "q"}}
    entry = {"preset": name, "status": "success", "features": list(features), "runs": runs, "ratio": ratio}
    if drift is not None:
        entry["drift"] = drift
    return entry


def test_summary_flags_presets_beyond_tolerance_and_groups_by_feature():
    entries = [_entry("a", 1.0), _entry("b", 1.05), _entry("c", 1.2, features=("main_thick",)), _entry("d", None)]
    summary = summarize(entries, None)
    assert summary["beyond_tolerance"] == ["c"]
    assert summary["share_beyond_tolerance"] == pytest.approx(1 / 3)
    assert summary["median_deviation"] == pytest.approx(.05)
    assert summary["median_ratio_by_feature"] == {"main_thick": pytest.approx(1.2), "main_thin": pytest.approx(1.025)}
    assert summary["failed"] == 0


def test_summary_reports_changed_legacy_frames_against_baseline():
    baseline = {"presets": [_entry("a", 1.0, legacy_hash="old"), _entry("b", 1.0)]}
    summary = summarize([_entry("a", 1.0, legacy_hash="new"), _entry("b", 1.0), _entry("new", 1.0)], baseline)
    assert summary["legacy_changed"] == ["a legacy-1080"]


def test_summary_medians_drift_per_mode():
    entries = [_entry("a", 1.0, drift={"legacy": .3, "quad": .02}),
               _entry("b", 1.0, drift={"legacy": .1, "quad": None})]
    assert summarize(entries, None)["median_drift"] == {"legacy": pytest.approx(.2), "quad": pytest.approx(.02)}


def test_failed_presets_are_counted():
    entry = _entry("a", 1.0)
    entry["status"] = "failed"
    summary = summarize([entry], None)
    assert summary["failed"] == 1
    assert summary["median_deviation"] is None


def _nondeterministic(name, ratio=1.3, legacy_hash="new", features=("main_thick",)):
    entry = _entry(name, ratio, legacy_hash=legacy_hash, features=features, drift={"legacy": .5, "quad": .4})
    entry["runs"]["legacy-1080-repeat"] = {"status": "success", "mean_luma": .2, "frames_sha256": "other"}
    entry["nondeterministic"] = True
    return entry


def test_nondeterministic_entries_are_listed_and_excluded_from_statistics():
    entries = [_entry("a", 1.0, drift={"legacy": .1, "quad": .1}), _nondeterministic("z"), _nondeterministic("b")]
    summary = summarize(entries, None)
    assert summary["nondeterministic"] == ["b", "z"]
    assert summary["beyond_tolerance"] == []
    assert summary["median_deviation"] == 0
    assert summary["share_beyond_tolerance"] == 0
    assert summary["median_ratio_by_feature"] == {"main_thin": pytest.approx(1.0)}
    assert summary["median_drift"] == {"legacy": pytest.approx(.1), "quad": pytest.approx(.1)}
    assert summary["failed"] == 0


def test_nondeterministic_entries_never_count_as_changed_legacy_frames():
    baseline = {"presets": [_entry("n", 1.0, legacy_hash="old")]}
    assert summarize([_nondeterministic("n")], baseline)["legacy_changed"] == []


def test_repeat_run_is_not_compared_against_the_baseline():
    old = _entry("a", 1.0)
    old["runs"]["legacy-1080-repeat"] = {"status": "success", "mean_luma": .2, "frames_sha256": "old"}
    new = _entry("a", 1.0)
    new["runs"]["legacy-1080-repeat"] = {"status": "success", "mean_luma": .2, "frames_sha256": "new"}
    new["nondeterministic"] = False
    assert summarize([new], {"presets": [old]})["legacy_changed"] == []


def test_deterministic_entries_report_no_nondeterminism():
    assert summarize([_entry("a", 1.0)], None)["nondeterministic"] == []


def _failed(name):
    entry = _entry(name, 1.0)
    entry["status"] = "failed"
    return entry


def test_failures_already_failed_in_the_baseline_are_not_new():
    baseline = {"presets": [_failed("broken"), _entry("a", 1.0)]}
    summary = summarize([_failed("broken"), _entry("a", 1.0)], baseline)
    assert summary["failed"] == 1
    assert summary["new_failures"] == []
    assert exit_code(summary) == 0


def test_failures_that_succeeded_or_were_missing_in_the_baseline_are_new():
    baseline = {"presets": [_entry("a", 1.0), _failed("broken")]}
    summary = summarize([_failed("a"), _failed("unknown"), _failed("broken")], baseline)
    assert summary["new_failures"] == ["a", "unknown"]
    assert exit_code(summary) == 1


def test_without_a_baseline_every_failure_is_new():
    summary = summarize([_failed("b"), _failed("a"), _entry("c", 1.0)], None)
    assert summary["new_failures"] == ["a", "b"]
    assert exit_code(summary) == 1


def test_changed_legacy_frames_fail_the_run():
    baseline = {"presets": [_entry("a", 1.0, legacy_hash="old")]}
    summary = summarize([_entry("a", 1.0, legacy_hash="new")], baseline)
    assert exit_code(summary) == 1
    assert exit_code(summarize([_entry("a", 1.0)], None)) == 0
