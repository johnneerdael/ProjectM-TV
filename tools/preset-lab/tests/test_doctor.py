import os
from pathlib import Path

import pytest

from preset_lab.doctor import doctor


@pytest.mark.native
def test_doctor_checks_all_native_cases_and_common_prefix(tmp_path):
    worker = os.environ.get("PRESET_LAB_WORKER")
    if not worker:
        pytest.skip("real OpenGL worker required")
    report = doctor(Path(__file__).parents[3], tmp_path, Path(worker))
    assert report["healthy"]
    assert {case["case"] for case in report["repeatability"]} == {"waveform", "noise", "shader"}
    assert all(case["same_input_equal"] and case["common_prefix_equal"]
               for case in report["repeatability"])
    assert report["backend"]["gl_renderer"]
