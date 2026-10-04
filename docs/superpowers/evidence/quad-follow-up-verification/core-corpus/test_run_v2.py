import json
from pathlib import Path
import shutil
import unittest

import test_run
import run_v2 as run


class AttemptOutputTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_run.HostTests()
        self.fixture.setUp()
        self.work = self.fixture.work
        self.job = dict(self.fixture.job, output_directory="/sdcard/Android/data/test/files/jobs/job/output")
        self.directory = self.work / "attempt-job"
        self.directory.mkdir()

    def tearDown(self):
        self.fixture.tearDown()

    def incoming(self):
        path = self.directory / "incoming/output"
        path.mkdir(parents=True)
        for name in ["frames.jsonl", "frame-0000.rgb", "frame-0001.rgb"]:
            shutil.copy2(self.work / name, path / name)
        (path / "result.json").write_text(json.dumps(self.fixture.result))
        return path

    def test_previous_success_is_preserved_but_not_current_output(self):
        old = self.directory / "output"
        old.mkdir()
        (old / "result.json").write_bytes(b"old successful producer")
        _, incoming = run.begin_output_attempt(self.job, self.directory)
        self.assertFalse((self.directory / "output").exists())
        self.assertFalse(incoming.exists())
        previous = list(self.directory.glob("previous-attempt-*/output/result.json"))
        self.assertEqual(len(previous), 1)
        self.assertEqual(previous[0].read_bytes(), b"old successful producer")

    def test_each_attempt_uses_a_fresh_remote_directory(self):
        first, _ = run.begin_output_attempt(self.job, self.directory)
        second, _ = run.begin_output_attempt(self.job, self.directory)
        self.assertNotEqual(first["output_directory"], second["output_directory"])
        self.assertNotEqual(first["output_directory"], self.job["output_directory"])

    def test_crash_before_atomic_result_cannot_publish_previous_success(self):
        incoming = self.directory / "incoming/output"
        incoming.mkdir(parents=True)
        (incoming / "frames.jsonl").write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "result"):
            run.verify_and_promote_output(self.job, incoming, self.directory)
        self.assertFalse((self.directory / "output").exists())

    def test_result_with_wrong_provenance_stays_in_unpublished_attempt(self):
        incoming = self.incoming()
        result = dict(self.fixture.result, job_id="other")
        (incoming / "result.json").write_text(json.dumps(result))
        with self.assertRaisesRegex(ValueError, "provenance"):
            run.verify_and_promote_output(self.job, incoming, self.directory)
        self.assertFalse((self.directory / "output").exists())
        self.assertTrue((incoming / "result.json").exists())

    def test_verified_complete_output_is_promoted_without_old_files(self):
        incoming = self.incoming()
        status = run.verify_and_promote_output(self.job, incoming, self.directory)
        self.assertEqual(status, "success")
        self.assertTrue((self.directory / "output/result.json").exists())
        self.assertFalse(incoming.exists())

    def test_failed_attempt_metadata_and_logs_survive_retry_without_promoted_output(self):
        (self.directory/"row.json").write_bytes(b"old failed row")
        (self.directory/"job.json").write_bytes(b"old job packet")
        (self.directory/"instrumentation.log").write_bytes(b"old invocation result")
        run.begin_output_attempt(self.job,self.directory)
        archived=list(self.directory.glob("previous-attempt-*/row.json"))
        self.assertEqual(len(archived),1)
        self.assertEqual(archived[0].read_bytes(),b"old failed row")
        self.assertEqual((archived[0].parent/"instrumentation.log").read_bytes(),b"old invocation result")


if __name__ == "__main__":
    unittest.main()
