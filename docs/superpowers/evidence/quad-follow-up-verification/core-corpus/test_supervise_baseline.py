import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


class DiskGuardTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("baseline_disk_guard", HERE / "supervise_baseline.py")
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_pause_live_scan_below8gib(self):
        self.assertEqual(self.module.disk_action(7.9 * 1024**3, True, False), "pause")
        self.assertEqual(self.module.disk_action(8 * 1024**3, True, False), "continue")

    def test_wait_hysteresis_then_resume12gib(self):
        for free in (4, 8, 11.9):
            self.assertEqual(self.module.disk_action(free * 1024**3, False, True), "wait")
        self.assertEqual(self.module.disk_action(12 * 1024**3, False, True), "resume")

    def test_low_disk_dead_scan_waits_without_rendering(self):
        self.assertEqual(self.module.disk_action(7 * 1024**3, False, False), "wait")
        self.assertEqual(self.module.disk_action(13 * 1024**3, False, False), "continue")


if __name__ == "__main__":
    unittest.main()
