"""Compile and exercise the worker's effective host-control manifest helper."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
WORKER = ROOT / "tools/patch-proof/native/worker.cpp"
HOOKS = ROOT / "tools/preset-lab/src/preset_lab/native"


class WorkerAppliedControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.binaries = {}
        for role, tv in (("patched", True), ("upstream", False)):
            binary = Path(cls.temporary.name) / role
            command = ["c++", "-std=c++17", "-DPATCH_PROOF_CONTROLS_TEST"]
            if tv:
                command.append("-DPATCH_PROOF_TV")
            command.extend(["-I", str(HOOKS), str(WORKER), "-o", str(binary)])
            subprocess.run(command, check=True)
            cls.binaries[role] = binary

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def applied(self, role, config):
        result = subprocess.run([str(self.binaries[role]), json.dumps(config)],
                                text=True, capture_output=True, check=True)
        report = json.loads(result.stdout)
        self.assertEqual(report["applied_controls"], report["setter_state"])
        return report["applied_controls"]

    def test_patched_default_width_tracks_requested_16_by_9_reference(self):
        self.assertEqual(self.applied("patched", {
            "line_reference_height": 1080,
            "line_antialiasing": True,
            "feedback_detail": 1.5,
        }), {
            "line_reference_width": 1920,
            "line_reference_height": 1080,
            "line_antialiasing": True,
            "feedback_detail_alpha": 1.0,
        })

    def test_patched_explicit_and_invalid_reference_values_report_setter_state(self):
        self.assertEqual(self.applied("patched", {
            "line_reference_width": 1280,
            "line_reference_height": 720,
            "line_antialiasing": False,
            "feedback_detail": -0.25,
        }), {
            "line_reference_width": 1280,
            "line_reference_height": 720,
            "line_antialiasing": False,
            "feedback_detail_alpha": -1.0,
        })
        self.assertEqual(self.applied("patched", {
            "line_reference_width": 1280,
            "line_reference_height": 0,
            "line_antialiasing": True,
        }), {
            "line_reference_width": 0,
            "line_reference_height": 0,
            "line_antialiasing": True,
            "feedback_detail_alpha": -1.0,
        })

    def test_upstream_reports_classic_effective_controls_despite_job_requests(self):
        self.assertEqual(self.applied("upstream", {
            "line_reference_height": 1080,
            "line_antialiasing": True,
            "feedback_detail": 0.75,
        }), {
            "line_reference_width": 0,
            "line_reference_height": 0,
            "line_antialiasing": False,
            "feedback_detail_alpha": -1.0,
        })


if __name__ == "__main__":
    unittest.main()
