import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import audit
import run


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.work = Path(self.temp.name)
        self.record = {"path": "fixture.milk", "sha256": "preset", "bytes": 10}
        self.family = {"filename": "fixture.milk", "sha256": "preset",
                       "feature_names": ["main_feedback_sampling"],
                       "shader_hashes": {"warp": "shader"}, "unclassified": False}
        inventory = {"count": 1, "presets": [self.record]}
        inventory["corpus_sha256"] = run.digest(inventory["presets"])
        run.atomic(self.work / "inventory.json", inventory)
        self.protocol = {"backend": "production-projectm-tv-core-ProjectMJNI-EGL-GLES3",
                         "device_serial": "emulator-5580", "device": {"model": "fixture"},
                         "roles": {"baseline": {"apk_sha256": "apk", "core_sha256": "core",
                                   "backend_identity": {"instrumentation_sha256": "observer"}}},
                         "textures_sha256": "textures", "corpus_sha256": inventory["corpus_sha256"],
                         "pcm": {"480": {"sha256": "pcm"}},
                         "config": {"width": 2364, "height": 1330, "fps": 30, "seed": 12345,
                                    "warmup_frames": 120, "measurement_frames": 360,
                                    "capture_frames": run.capture_indices(360)}}
        self.protocol["sha256"] = run.digest(self.protocol)
        run.atomic(self.work / "protocol.json", self.protocol)
        self.families = self.work / "families.json"
        run.atomic(self.families, {"presets": [self.family]})
        driver = {"gl_renderer": "fixture GPU"}
        paths = []
        for repeat in (1, 2):
            key = run.job_key(self.protocol["sha256"], self.record, "baseline", "selected", repeat)
            directory = self.work / "jobs" / key
            directory.mkdir(parents=True)
            frames = [{"frame": i, "preset_filename": "fixture.milk", "change_counter": 1,
                       "pcm_bytes": 1470, "captured": i in run.capture_indices(360),
                       "sha256": "f" * 64 if i in run.capture_indices(360) else None} for i in range(480)]
            raw = "".join(run.canonical(f) + "\n" for f in frames).encode()
            trace = directory / "frames.jsonl.gz"
            trace.write_bytes(gzip.compress(raw))
            samples = [{"frame": i, "sha256": "f" * 64, "metrics": {"native_luma_mean": 0.4}}
                       for i in run.capture_indices(360)]
            result = {"status": "success", "core_sha256": "core", "requested_preset_sha256": "preset",
                      "frames_metadata_sha256": hashlib.sha256(raw).hexdigest(),
                      "rendered_frames": 480, "selected_files": samples, "gl_renderer": "fixture GPU",
                      "schema_version": 2, "job_id": key, "protocol_sha256": self.protocol["sha256"],
                      "preset_filename": "fixture.milk", "capture_mode": "selected",
                      "capture_frames": run.capture_indices(360), "width": 2364, "height": 1330,
                      "fps": 30, "seed": 12345}
            job = {"key": key, "protocol_sha256": self.protocol["sha256"], "preset": self.record,
                   "role": "baseline", "repeat": repeat, "measurement_frames": 360,
                   "capture_mode": "selected", "status": "success", "result": result,
                   "selected_native_sha256": {str(i): "f" * 64 for i in run.capture_indices(360)},
                   "frame_trace": {"path": "frames.jsonl.gz"},
                   "retained_files": [{"path": "frames.jsonl.gz", "sha256": run.file_hash(trace)}]}
            self.save_job(directory / "row.json", job)
            paths.append(str((directory / "row.json").relative_to(self.work)))
        self.pair = {"key": run.digest({"protocol_sha256": self.protocol["sha256"],
                                        "preset": self.record, "role": "baseline"}),
                     "protocol_sha256": self.protocol["sha256"], "preset": self.record, "role": "baseline",
                     "status": "success", "runs": paths, "driver": driver,
                     "repeat_exact_selected": True, "hash_coverage": run.capture_indices(360)}
        self.pair["render_input_sha256"] = run.render_input_signature(
            self.protocol, "baseline", self.record, driver)
        self.pair_path = self.work / "rows" / (self.pair["key"] + ".json")
        run.save_row(self.pair_path, self.pair)

    def tearDown(self):
        self.temp.cleanup()

    def save_job(self, path, job):
        job.pop("payload_sha256", None)
        result_path = path.parent / "output/result.json"
        run.atomic(result_path, job["result"])
        job["retained_files"] = [f for f in job["retained_files"] if f["path"] != "output/result.json"]
        job["retained_files"].append({"path": "output/result.json", "sha256": run.file_hash(result_path)})
        run.save_row(path, job)

    def fail_pair(self):
        for rel in self.pair["runs"]:
            path = self.work / rel
            job = json.loads(path.read_text())
            job["status"] = "failed"
            job["result"].update(status="failed", error="requested load failed")
            self.save_job(path, job)
        run.save_row(self.pair_path, dict(self.pair, status="failed", repeat_exact_selected=False))

    def test_complete_verified_export_preserves_original_provenance_and_metrics(self):
        before = self.pair_path.read_bytes()
        report = audit.export(self.work, self.families, "baseline")
        self.assertTrue(report["complete_coverage"])
        self.assertEqual(report["rows"][0]["render_input_sha256"], self.pair["render_input_sha256"])
        self.assertEqual(report["rows"][0]["features"], ["main_feedback_sampling"])
        self.assertEqual(len(report["rows"][0]["samples"]), 16)
        self.assertEqual(before, self.pair_path.read_bytes())

    def test_missing_preset_is_pending_not_successful(self):
        self.pair_path.unlink()
        report = audit.export(self.work, self.families, "baseline")
        self.assertFalse(report["complete_coverage"])
        self.assertEqual(report["remaining_presets"], 1)

    def test_family_source_mismatch_is_rejected(self):
        family = dict(self.family, sha256="different")
        run.atomic(self.families, {"presets": [family]})
        with self.assertRaisesRegex(ValueError, "source"):
            audit.export(self.work, self.families, "baseline")

    def test_corrupt_trace_cannot_become_verified_coverage(self):
        job = self.work / self.pair["runs"][0]
        (job.parent / "frames.jsonl.gz").write_bytes(b"corrupt")
        report = audit.export(self.work, self.families, "baseline")
        self.assertFalse(report["complete_coverage"])
        self.assertEqual(len(report["integrity_issues"]), 1)

    def test_rehashed_but_incomplete_frame_trace_is_rejected(self):
        path = self.work / self.pair["runs"][0]
        job = json.loads(path.read_text())
        trace = path.parent / "frames.jsonl.gz"
        raw = b'{"frame":0}\n'
        trace.write_bytes(gzip.compress(raw))
        job.pop("payload_sha256")
        job["retained_files"][0]["sha256"] = run.file_hash(trace)
        job["result"]["frames_metadata_sha256"] = hashlib.sha256(raw).hexdigest()
        self.save_job(path, job)
        report = audit.export(self.work, self.families, "baseline")
        self.assertFalse(report["complete_coverage"])
        self.assertEqual(len(report["integrity_issues"]), 1)

    def test_wrong_input_signature_is_rejected_even_with_valid_row_checksum(self):
        pair = dict(self.pair, render_input_sha256="different")
        run.save_row(self.pair_path, pair)
        report = audit.export(self.work, self.families, "baseline")
        self.assertFalse(report["complete_coverage"])
        self.assertEqual(len(report["integrity_issues"]), 1)

    def test_failed_pair_remains_explicit_and_counts_as_attempted(self):
        self.fail_pair()
        report = audit.export(self.work, self.families, "baseline")
        self.assertTrue(report["complete_coverage"])
        self.assertEqual(report["statuses"], {"failed": 1})
        self.assertEqual(report["rows"][0]["samples"], [])

    def test_rehashed_failed_result_with_wrong_provenance_is_rejected(self):
        for field, value in [("job_id", "other"), ("protocol_sha256", "other"),
                             ("core_sha256", "other"), ("requested_preset_sha256", "other"),
                             ("status", "invented")]:
            with self.subTest(field=field):
                self.fail_pair()
                path = self.work / self.pair["runs"][0]
                job = json.loads(path.read_text())
                original = dict(job["result"])
                job["result"][field] = value
                self.save_job(path, job)
                report = audit.export(self.work, self.families, "baseline")
                self.assertFalse(report["complete_coverage"])
                self.assertEqual(len(report["integrity_issues"]), 1)
                job["result"] = original
                self.save_job(path, job)

    def test_removed_row_result_cannot_hide_retained_producer_result(self):
        self.fail_pair()
        path = self.work / self.pair["runs"][0]
        job = json.loads(path.read_text())
        job.pop("payload_sha256")
        job.pop("result")
        run.save_row(path, job)
        report = audit.export(self.work, self.families, "baseline")
        self.assertFalse(report["complete_coverage"])
        self.assertEqual(len(report["integrity_issues"]), 1)

    def test_failed_row_cannot_differ_from_original_producer_json(self):
        self.fail_pair()
        path = self.work / self.pair["runs"][0]
        job = json.loads(path.read_text())
        job.pop("payload_sha256")
        job["result"]["error"] = "rewritten message"
        run.save_row(path, job)
        report = audit.export(self.work, self.families, "baseline")
        self.assertFalse(report["complete_coverage"])
        self.assertEqual(len(report["integrity_issues"]), 1)

    def test_real_pre_engine_failure_needs_no_unavailable_runtime_core(self):
        self.fail_pair()
        for rel in self.pair["runs"]:
            path = self.work / rel
            job = json.loads(path.read_text())
            job["result"].pop("core_sha256")
            job["result"].pop("requested_preset_sha256")
            job["result"]["error"] = "PCM checksum mismatch before init"
            self.save_job(path, job)
        report = audit.export(self.work, self.families, "baseline")
        self.assertTrue(report["complete_coverage"])

    def test_missing_producer_without_host_failure_evidence_is_rejected(self):
        self.fail_pair()
        path = self.work / self.pair["runs"][0]
        job = json.loads(path.read_text())
        job.pop("payload_sha256")
        job.pop("result")
        (path.parent / "output/result.json").unlink()
        job["retained_files"] = [f for f in job["retained_files"] if f["path"] != "output/result.json"]
        run.save_row(path, job)
        report = audit.export(self.work, self.families, "baseline")
        self.assertFalse(report["complete_coverage"])
        self.assertEqual(len(report["integrity_issues"]), 1)

    def test_explicit_host_transport_failure_preserves_attempted_coverage(self):
        self.fail_pair()
        for rel in self.pair["runs"]:
            path = self.work / rel
            job = json.loads(path.read_text())
            job.pop("payload_sha256")
            job.pop("result")
            job["error"] = "RuntimeError: external output pull failed"
            (path.parent / "output/result.json").unlink()
            job["retained_files"] = [f for f in job["retained_files"] if f["path"] != "output/result.json"]
            run.save_row(path, job)
        report = audit.export(self.work, self.families, "baseline")
        self.assertTrue(report["complete_coverage"])
        self.assertEqual(report["rows"][0]["samples"], [])


if __name__ == "__main__":
    unittest.main()
