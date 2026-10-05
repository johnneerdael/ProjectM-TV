"""Regression tests for screen evidence integrity and process failure handling."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("screen-clipping.py")
SPEC = importlib.util.spec_from_file_location("clipping_screen", SCRIPT)
SCREEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCREEN)


class ScreenTests(unittest.TestCase):
    def workers(self, root, body="pass"):
        records = {}
        for label in ("authored", "before", "fixed"):
            executable = root / label
            executable.write_text(f"#!{sys.executable}\n" + body + "\n")
            executable.chmod(0o755)
            records[label] = {"path": str(executable),
                              "sha256": hashlib.sha256(executable.read_bytes()).hexdigest()}
        protocol = root / "workers.json"
        protocol.write_text(json.dumps({"workers": records, "capture_frames": [120, 150, 180, 210, 239, 300, 390, 479]}))
        return protocol

    def test_truncated_capture_fails(self):
        with self.assertRaisesRegex(RuntimeError, "truncated capture"):
            SCREEN.read_exact(io.BytesIO(b"short"), 10)

    def test_changed_executable_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            protocol = self.workers(root)
            (root / "fixed").write_text("changed")
            with self.assertRaisesRegex(ValueError, "worker checksum mismatch: fixed"):
                SCREEN.verify_workers(protocol)

    def test_capture_order_is_validated(self):
        with tempfile.TemporaryDirectory() as temp:
            protocol = self.workers(Path(temp))
            record = json.loads(protocol.read_text())
            record["capture_frames"] = [300, 120]
            protocol.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "invalid capture frame list"):
                SCREEN.verify_workers(protocol)

    def test_old_evidence_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            sentinel = out / "protocol.json"
            sentinel.write_text("existing evidence")
            with self.assertRaisesRegex(ValueError, "output must be empty"):
                SCREEN.require_empty_output(out)
            self.assertEqual(sentinel.read_text(), "existing evidence")

    def test_sorted_but_wrong_capture_indices_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            protocol = self.workers(Path(temp))
            record = json.loads(protocol.read_text())
            record["capture_frames"][0] = 121
            protocol.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "worker frame contract"):
                SCREEN.verify_workers(protocol)

    def test_failed_worker_stops_queued_presets(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            body = "import pathlib, sys\npathlib.Path(sys.argv[2]).with_name('started').touch()\nsys.stdout.buffer.write(b'short')"
            protocol = self.workers(root, body)
            out = root / "out"
            result = subprocess.run([sys.executable, str(SCRIPT), "--workers", str(protocol),
                                     "--out", str(out), "--indices", "0,1,2", "--jobs", "1"],
                                    capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("truncated capture", result.stderr)
            self.assertIn("worker exit=", result.stderr)
            self.assertIn("stderr.txt", result.stderr)
            self.assertEqual(len(list(out.glob("runs/*/started"))), 1)
            self.assertEqual(list(out.glob("[0-9]*.json")), [])

    def test_hung_worker_is_terminated(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            protocol = self.workers(root, "import time\ntime.sleep(10)")
            result = subprocess.run([sys.executable, str(SCRIPT), "--workers", str(protocol),
                                     "--out", str(root / "out"), "--indices", "0", "--timeout", "0.1"],
                                    capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("render timed out", result.stderr)

    def test_builder_refuses_nonempty_work_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            unrelated = work / "native"
            unrelated.mkdir()
            sentinel = unrelated / "keep.txt"
            sentinel.write_text("unrelated work")
            result = subprocess.run([sys.executable, str(SCRIPT.with_name("prepare-screen.py")),
                                     "--work", str(work)], capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 2)
            self.assertIn("--work must be empty", result.stderr)
            self.assertEqual(sentinel.read_text(), "unrelated work")


if __name__ == "__main__":
    unittest.main()
