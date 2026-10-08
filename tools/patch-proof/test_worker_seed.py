"""Exercise the worker's seed setup without requiring a GL device."""
import json
from pathlib import Path
import os
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
WORKER = ROOT / "tools/patch-proof/native/worker.cpp"
HOOKS = ROOT / "tools/preset-lab/src/preset_lab/native"


class WorkerSeedContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.binary = Path(cls.temporary.name) / "worker-seed-control"
        subprocess.run(
            ["c++", "-std=c++17", "-DPATCH_PROOF_SEED_TEST", "-I", str(HOOKS),
             str(WORKER), "-o", str(cls.binary)],
            check=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def run_seed(self, seed, environment_seed, mode="job"):
        environment = dict(os.environ, PRESET_LAB_SEED=str(environment_seed))
        command = [str(self.binary), mode]
        if mode == "job":
            command.append(json.dumps({"seed": seed}))
        result = subprocess.run(command, env=environment, text=True, capture_output=True)
        return result

    def test_job_seed_overrides_environment_for_all_worker_random_sources(self):
        first = self.run_seed(12345, 77)
        second = self.run_seed(12345, 987654)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        first_result, second_result = json.loads(first.stdout), json.loads(second.stdout)
        self.assertEqual(first_result, second_result)
        self.assertEqual(first_result["seed"], 12345)
        self.assertEqual(first_result["environment_seed"], "12345")
        self.assertNotEqual(first_result["libc_random"], 0)
        self.assertNotEqual(first_result["shader_random"], 0)

    def test_job_seed_changes_worker_random_sources(self):
        first = self.run_seed(12345, 77)
        second = self.run_seed(12346, 77)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertNotEqual(json.loads(first.stdout), json.loads(second.stdout))

    def test_rejects_non_integer_and_out_of_range_job_seeds(self):
        for seed in (True, 1.5, -1, 2**32):
            with self.subTest(seed=seed):
                result = self.run_seed(seed, 77)
                self.assertNotEqual(result.returncode, 0)

    def test_evaluator_control_uses_an_explicit_seed(self):
        first = self.run_seed(None, 77, mode="evaluator-control")
        second = self.run_seed(None, 987654, mode="evaluator-control")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(json.loads(first.stdout), json.loads(second.stdout))
        self.assertEqual(json.loads(first.stdout)["seed"], 12345)


if __name__ == "__main__":
    unittest.main()
