import gzip
import json
from pathlib import Path
import tempfile
import unittest

import capture_provenance_snapshot as snapshot
import run


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.work = self.root / "dataset"
        self.protocol = {"roles": {"baseline": {"core_sha256": "core"}},
                         "config": {"measurement_frames": 360, "capture_frames": run.capture_indices(360)}}
        self.protocol["sha256"] = run.digest(self.protocol)
        run.atomic(self.work / "protocol.json", self.protocol)
        self.output = self.root / "snapshot.json"

    def tearDown(self):
        self.temp.cleanup()

    def add_job(self, name):
        record = {"path": name, "sha256": "preset"}
        key = run.job_key(self.protocol["sha256"], record, "baseline", "selected", 1, 360)
        row = {"key": key, "role": "baseline", "preset": record,
               "capture_mode": "selected", "measurement_frames": 360,
               "status": "timeout", "error": "transport failed before producer", "retained_files": []}
        run.save_row(self.work / "jobs" / key / "row.json", row)
        return key

    def test_exact_input_membership_and_hashes_survive_later_scanner_progress(self):
        key = self.add_job("first.milk")
        report = snapshot.snapshot(self.work, self.output)
        manifest_path = self.output.with_suffix(".inputs.json.gz")
        frozen = manifest_path.read_bytes()
        manifest = json.loads(gzip.decompress(frozen))
        self.assertEqual(report["jobs_checked"], 1)
        self.assertEqual(manifest["jobs"][0]["key"], key)
        self.assertEqual(report["input_records_sha256"], run.digest(manifest["jobs"]))
        self.assertEqual(report["input_manifest_sha256"], run.file_hash(manifest_path))
        for item in manifest["jobs"][0]["inputs"]:
            self.assertEqual(item["sha256"], run.file_hash(self.work / item["path"]))
        self.add_job("second.milk")
        later = snapshot.snapshot(self.work, self.root / "later.json")
        self.assertEqual(later["jobs_checked"], 2)
        self.assertEqual(frozen, manifest_path.read_bytes())

    def test_invalid_producer_never_creates_a_clean_snapshot(self):
        key = self.add_job("bad.milk")
        path = self.work / "jobs" / key / "row.json"
        row = json.loads(path.read_text())
        row.pop("payload_sha256")
        row.pop("error")
        run.save_row(path, row)
        with self.assertRaisesRegex(ValueError, "explicit host failure"):
            snapshot.snapshot(self.work, self.output)
        self.assertFalse(self.output.exists())

    def test_empty_snapshot_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            snapshot.snapshot(self.work, self.output)

    def test_output_cannot_modify_measurement_dataset(self):
        self.add_job("first.milk")
        with self.assertRaisesRegex(ValueError, "outside"):
            snapshot.snapshot(self.work, self.work / "snapshot.json")


if __name__ == "__main__":
    unittest.main()
