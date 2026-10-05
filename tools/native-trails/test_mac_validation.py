"""Selection and receipt trust-boundary checks without a GL device."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import cv2
import numpy as np

MODULE = Path(__file__).with_name("mac_validation.py")
spec = importlib.util.spec_from_file_location("mac_validation", MODULE)
mac = importlib.util.module_from_spec(spec) if MODULE.exists() else None
if mac is not None:
    spec.loader.exec_module(mac)


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(mac, "Mac validation harness is not implemented")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.corpus, self.assets = self.root / "history", self.root / "assets"
        self.corpus.mkdir(); self.assets.mkdir()
        self.rows = []
        for i in range(200):
            name = "preset-%03d.milk" % i
            text = "[preset00]\nfDecay=0.99\n" + ("bMotionVectorsOn=1\n" if i % 3 == 0 else "")
            text += ("warp_1=ret=GetBlur1(uv);\n" if i % 4 == 0 else "")
            text += "fWarpShaderVersion=%d\nfCompShaderVersion=%d\n" % (i % 4, i % 2)
            (self.assets / name).write_text(text)
            record = {"path": name, "sha256": mac.file_digest(self.assets / name), "bytes": len(text.encode())}
            runs = []
            for repeat in (1, 2):
                path = self.corpus / "jobs" / ("%03d-%d" % (i, repeat)) / "row.json"
                path.parent.mkdir(parents=True)
                row = {"preset": record, "status": "success", "protocol_sha256": "pending",
                       "result": {"status": "success", "selected_files": [
                           {"frame": 120, "metrics": {"native_luma_mean": i / 200,
                            "native_clipped_fraction": .9 if i == 198 else 0,
                            "native_bright_fraction": .5 if i == 197 else 0}}]}}
                if i == 0 and repeat == 1:
                    row.update(status="failed", error="owned app-created external output pull failed; partials preserved")
                    row.pop("result")
                if i == 1:
                    row.update(status="failed", result={"status": "failed", "error": "requested preset failed or fallback occurred"})
                path.write_text(json.dumps(row))
                runs.append(path.relative_to(self.corpus).as_posix())
            self.rows.append({"preset": record, "status": "failed" if i < 2 else "success",
                              "runs": runs, "protocol_sha256": "pending", "key": str(i)})
        protocol = {"schema_version": 1, "config": {"width": 2364, "height": 1330},
                    "roles": {"baseline": {"backend_identity": {"ordered_patches": [{"name": "%04d-test.patch" % i} for i in range(1, 25)]}}}}
        protocol["sha256"] = mac.digest(protocol)
        (self.corpus / "protocol.json").write_text(json.dumps(protocol))
        inventory = {"presets": [r["preset"] for r in self.rows], "count": 200}
        (self.corpus / "inventory.json").write_text(json.dumps(inventory))
        for row in self.rows:
            row["protocol_sha256"] = protocol["sha256"]
            for name in row["runs"]:
                path = self.corpus / name
                data = json.loads(path.read_text()); data["protocol_sha256"] = protocol["sha256"]
                path.write_text(json.dumps(data))
        self.index = {"complete_coverage": True, "terminal_presets": 200,
                      "protocol_sha256": protocol["sha256"], "rows": self.rows,
                      "statuses": {"failed": 2, "success": 198},
                      "inventory_sha256": mac.file_digest(self.corpus / "inventory.json")}
        (self.corpus / "baseline-completion-index.json").write_text(json.dumps(self.index))

    def select(self):
        history = mac.load_historical(self.corpus, self.assets, expected_count=200)
        return mac.select_presets(history, ["preset-002.milk", "preset-003.milk"], 128)

    def test_reproducible_risk_selection_includes_all_failed_and_witnesses(self):
        first, second = self.select(), self.select()
        self.assertEqual(first, second)
        self.assertEqual(len(first["presets"]), 128)
        records = {r["preset"]: r for r in first["presets"]}
        self.assertTrue({"preset-000.milk", "preset-001.milk", "preset-002.milk", "preset-003.milk"} <= records.keys())
        self.assertEqual(records["preset-000.milk"]["historical_failure"]["classification"], "transport_with_successful_repeat")
        self.assertEqual(records["preset-001.milk"]["historical_failure"]["classification"], "render_or_preset_failure")
        self.assertTrue(any("stratified_sample" in r["reasons"] for r in first["presets"]))
        self.assertEqual(len(first["authored_repeats"]), 13)
        self.assertIn("preset-198.milk", records)

    def test_current_preset_drift_cannot_silently_change_the_historical_join(self):
        (self.assets / "preset-004.milk").write_text("changed")
        with self.assertRaisesRegex(ValueError, "preset.*changed"):
            self.select()

    def test_historical_protocol_drift_or_incomplete_index_is_rejected(self):
        path = self.corpus / "protocol.json"
        original = path.read_text(); data = json.loads(original); data["config"]["width"] = 3840
        path.write_text(json.dumps(data))
        with self.assertRaises(ValueError): self.select()
        path.write_text(original)
        self.index["complete_coverage"] = False
        (self.corpus / "baseline-completion-index.json").write_text(json.dumps(self.index))
        with self.assertRaisesRegex(ValueError, "incomplete"): self.select()

    def test_mandatory_failures_cannot_starve_later_risk_categories(self):
        records = []
        for i in range(200):
            records.append({"preset": str(i), "preset_sha256": "%064x" % i,
                "historical_status": "failed" if i < 80 else "success",
                "historical_ranking_metrics": {"native_luma_mean": None, "native_clipped_fraction": 0, "native_bright_fraction": 0},
                "features": {"shader_stratum": "plain", "feedback_score": 0, "motion_score": 0, "blur_score": 0, "complexity": 0}})
        # Eight disjoint tails after84 mandatory cases; priority filling would
        # exhaust its20-slot risk budget before reaching blur/complex-source.
        for category in range(8):
            for offset in range(8):
                record = records[84 + category * 8 + offset]
                if category in (0, 1): record["historical_ranking_metrics"]["native_luma_mean"] = .01 if category == 0 else .99
                elif category in (2, 3): record["historical_ranking_metrics"][("native_clipped_fraction", "native_bright_fraction")[category - 2]] = .9
                else: record["features"][("feedback_score", "motion_score", "blur_score", "complexity")[category - 4]] = 100
        selected = mac.select_presets({"records": records, "provenance": {}}, [str(i) for i in range(80, 84)], 128)
        for reason in ("historical_dark", "historical_bright", "historical_clipped", "historical_bright_pixels",
                       "complex_feedback", "motion_vectors", "blur", "complex_source"):
            self.assertGreater(selected["reason_counts"].get(reason, 0), 0, reason)


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(mac, "Mac validation harness is not implemented")
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.request = {"identity": {"protocol_sha256": "frozen", "worker_sha256": "worker"},
                        "config": {"width": 2, "height": 2, "feedback_detail": 0, "fps": 30,
                                   "warmup_seconds": 4, "measurement_seconds": 12, "seed": 12345}}
        self.manifest = {"status": "success", "frames": 480, "fps": 30, "width": 2, "height": 2,
                         "identity": self.request["identity"], "seed": 12345, "gl_error_frames": 0,
                         "gl_checks": 480, "captures": mac.CAPTURES, "detail_statuses": [3],
                         "gl_renderer": "Apple M4", "gl_version": "4.1 Metal", "selected_bytes": 96}
        self.receipt = {"status": "success", "request_sha256": mac.digest(self.request),
                        "worker_manifest_sha256": mac.digest(self.manifest), "captures": []}
        for frame in mac.CAPTURES:
            rgb = np.full((2, 2, 3), 20, np.uint8)
            path = self.path / ("frame-%03d.png" % frame)
            cv2.imwrite(str(path), rgb)
            self.receipt["captures"].append({"frame": frame, "native_rgb_sha256": "a" * 64,
                                              "reduced_rgb_sha256": hashlib.sha256(rgb.tobytes()).hexdigest(),
                                              "png_sha256": mac.file_digest(path), "path": path.name,
                                              "metrics": {"luma": 20 / 255}})
        mac.write(self.path / "request.json", self.request)
        mac.write(self.path / "manifest.json", self.manifest)
        mac.write(self.path / "receipt.json", self.receipt)
        (self.path / "receipt.sha256").write_text(mac.file_digest(self.path / "receipt.json") + "\n")

    def test_complete_receipt_verifies_all_eight_retained_pngs(self):
        result = mac.verify_job(self.path, self.request, reduced_size=(2, 2))
        self.assertEqual(len(result["captures"]), 8)

    def test_mutated_png_and_mixed_request_fail(self):
        (self.path / "frame-479.png").write_bytes(b"mutation")
        with self.assertRaisesRegex(ValueError, "PNG"): mac.verify_job(self.path, self.request, reduced_size=(2, 2))
        other = dict(self.request, identity={"protocol_sha256": "other", "worker_sha256": "worker"})
        with self.assertRaisesRegex(ValueError, "request"): mac.verify_job(self.path, other, reduced_size=(2, 2))

    def test_incomplete_capture_sequence_or_gl_error_is_not_success(self):
        self.receipt["captures"].pop(); mac.write(self.path / "receipt.json", self.receipt)
        (self.path / "receipt.sha256").write_text(mac.file_digest(self.path / "receipt.json") + "\n")
        with self.assertRaisesRegex(ValueError, "Incomplete"): mac.verify_job(self.path, self.request, reduced_size=(2, 2))
        self.manifest["gl_error_frames"] = 1; mac.write(self.path / "manifest.json", self.manifest)
        with self.assertRaises(ValueError): mac.verify_job(self.path, self.request, reduced_size=(2, 2))

    def test_native_identity_gate_uses_every_hash_and_not_reduced_preview_hashes(self):
        before = {"captures": [{"native_rgb_sha256": "a"} for _ in range(8)]}
        off = {"captures": [{"native_rgb_sha256": "a"} for _ in range(8)]}
        off["captures"][-1]["native_rgb_sha256"] = "b"
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            mac.compare_identity(before, off, "before/off")

    def test_native_hash_receipt_cannot_be_mutated_on_resume(self):
        self.receipt["captures"][-1]["native_rgb_sha256"] = "b" * 64
        mac.write(self.path / "receipt.json", self.receipt)
        with self.assertRaisesRegex(ValueError, "Receipt checksum"):
            mac.verify_job(self.path, self.request, reduced_size=(2, 2))

    def test_frozen_protocol_refuses_changed_source_clock_or_workers(self):
        path = self.path / "protocol.json"
        protocol = {"source": "source-a", "clock": "frame/30.0", "worker": "worker-a"}
        mac.freeze(path, protocol)
        mac.freeze(path, protocol)
        for field in protocol:
            with self.assertRaisesRegex(ValueError, "Frozen protocol"):
                mac.freeze(path, dict(protocol, **{field: "changed"}))

    def test_terminal_coverage_never_promotes_partial_or_failed_fidelity(self):
        expected = [{"key": "one", "preset": "witness", "profile": "authored"},
                    {"key": "two", "preset": "witness", "profile": "high"}]
        results = {"one": {"status": "success"}}
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            mac.audit_results(expected, results)
        partial = mac.audit_results(expected, results, partial=True)
        self.assertFalse(partial["terminal_complete"])
        self.assertFalse(partial["fidelity_complete"])
        results["two"] = {"status": "failed", "error": "shader fallback"}
        final = mac.audit_results(expected, results)
        self.assertTrue(final["terminal_complete"])
        self.assertFalse(final["fidelity_complete"])
        self.assertEqual(final["failed_jobs"], 1)


if __name__ == "__main__": unittest.main()
