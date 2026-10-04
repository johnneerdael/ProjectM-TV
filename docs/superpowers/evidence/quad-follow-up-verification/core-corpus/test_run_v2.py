import json
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import checkpoint
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

    def test_post_promotion_timeout_keeps_one_checkpointable_producer(self):
        record = {"path": "exact.milk", "sha256": "source", "bytes": 1}
        protocol = {"sha256": "protocol", "device_serial": "192.168.51.53:5555",
                    "config": {"width": 2, "height": 1, "fps": 30, "seed": 12345},
                    "roles": {"baseline": {"core_sha256": "core"}},
                    "pcm": {"122": {"path": str(self.work / "pcm.u8")}}}
        key = run.job_key("protocol", record, "baseline", "selected", 1, 2)
        job = dict(self.job, job_id=key)
        result = dict(self.fixture.result, job_id=key)
        args = SimpleNamespace(work=self.work, timeout=600)
        stops = 0

        def adb(serial, *arguments, **kwargs):
            nonlocal stops
            if arguments[:3] == ("shell", "am", "force-stop"):
                stops += 1
                if stops == 2:
                    raise subprocess.TimeoutExpired("post-promotion force-stop", 120)
            return subprocess.CompletedProcess(arguments, 0, b"", b"")

        def pull(serial, remote, destination):
            destination.mkdir(parents=True, exist_ok=True)
            for name in ("frames.jsonl", "frame-0000.rgb", "frame-0001.rgb"):
                shutil.copy2(self.work / name, destination / name)
            (destination / "result.json").write_text(json.dumps(result))

        original_hash = run.file_hash

        def file_hash(path):
            if Path(path) == run.ROOT / "core/src/main/assets/presets/exact.milk":
                return "source"
            return original_hash(path)

        with (patch.object(run, "make_job", return_value=job),
              patch.object(run, "require_awake"), patch.object(run, "push_private"),
              patch.object(run, "adb", side_effect=adb),
              patch.object(run, "pull_external", side_effect=pull) as transfer,
              patch.object(run, "file_hash", side_effect=file_hash)):
            row = run.run_one(args, protocol, record, "baseline", "selected", 1, 2, native=True)

        self.assertEqual(row["status"], "timeout")
        verified = checkpoint.verify_job(self.work, protocol, {"presets": [record]}, key)
        self.assertEqual(verified["status"], "timeout")
        self.assertEqual(transfer.call_count, 1)
        self.assertEqual(len(list((self.work / "jobs" / key).rglob("result.json"))), 1)

    def test_repeated_force_stop_timeout_records_terminal_metadata(self):
        record={"path":"exact.milk","sha256":"source","bytes":1}
        protocol={"sha256":"protocol","device_serial":"192.168.51.53:5555",
                  "config":{"width":2,"height":1,"fps":30,"seed":12345},
                  "roles":{"baseline":{"core_sha256":"core"}},"pcm":{}}
        key=run.job_key("protocol",record,"baseline","selected",1,2)
        job=dict(self.job,job_id=key)
        args=SimpleNamespace(work=self.work,timeout=600)
        original_hash=run.file_hash
        def file_hash(path):
            if Path(path)==run.ROOT/"core/src/main/assets/presets/exact.milk":return "source"
            return original_hash(path)
        with (patch.object(run,"make_job",return_value=job),patch.object(run,"require_awake"),
              patch.object(run,"file_hash",side_effect=file_hash),
              patch.object(run,"adb",side_effect=subprocess.TimeoutExpired("sustained outage",120))):
            try:row=run.run_one(args,protocol,record,"baseline","selected",1,2)
            except subprocess.TimeoutExpired:row=None
        self.assertIsNotNone(row,"sustained outage must preserve terminal metadata")
        self.assertEqual(row["status"],"timeout")
        self.assertIn("remote_partial_recovery_error",row)
        self.assertTrue((self.work/"jobs"/key/"row.json").is_file())
        self.assertEqual(checkpoint.verify_job(self.work,protocol,{"presets":[record]},key)["status"],"timeout")


if __name__ == "__main__":
    unittest.main()
