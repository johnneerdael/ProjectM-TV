"""Small real PNG/AAR fixtures exercise the final-evidence trust boundary."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import cv2
import numpy as np

MODULE = Path(__file__).with_name("summarize_validation.py")
spec = importlib.util.spec_from_file_location("trails_summary", MODULE)
summary = importlib.util.module_from_spec(spec) if MODULE.exists() else None
if summary is not None:
    spec.loader.exec_module(summary)


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(summary, "The evidence summarizer is not implemented")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.work = self.base / "run"
        self.work.mkdir()
        self.presets = self.base / "presets"
        self.presets.mkdir()
        self.names = ["witness-%02d.milk" % i for i in range(17)]
        # Reduce only expensive image dimensions; keep all 136 actual jobs,
        # eight captures, archive/source identities and production verification.
        self.profiles = [(p, r, 2, 2, rw, rh, level) for p, r, w, h, rw, rh, level
                         in summary.runner.PROFILES]
        self.addCleanup(patch.stopall)
        patch.object(summary.runner, "PROFILES", self.profiles).start()
        patch.object(summary, "METRIC_SIZE", (2, 2)).start()
        records = {}
        for name in self.names:
            (self.presets / name).write_bytes(name.encode())
            records[name] = summary.file_digest(self.presets / name)
        workers = {}
        for role, count in (("baseline-native", 1), ("candidate-native", 2)):
            directory = self.base / role
            source = directory / "source"
            source.mkdir(parents=True)
            (source / "core.cpp").write_bytes(b"frozen source")
            (directory / "instrumentation.diff").write_bytes(b"frozen diff")
            patches = []
            for index in range(1, count + 1):
                path = source / "tools/projectm-patches" / ("%04d-test.patch" % index)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(str(index).encode())
                patches.append({"name": path.name, "sha256": summary.file_digest(path)})
            java = source / summary.WORKER_JAVA
            java.parent.mkdir(parents=True)
            java.write_bytes(b"frozen java")
            for filename in ("worker.apk", "core.aar"):
                with zipfile.ZipFile(directory / filename, "w") as archive:
                    archive.writestr(("lib" if filename.endswith("apk") else "jni")
                                     + "/arm64-v8a/libprojectmtv.so", role.encode())
                    for name in self.names:
                        archive.writestr("assets/presets/" + name, name.encode())
            identity = {"role": role, "policy": "native", "package": "test." + role,
                        "source_commit": role, "apk": str(directory / "worker.apk"),
                        "aar": str(directory / "core.aar"), "ordered_patches": patches,
                        "source_files_sha256": {"core.cpp": summary.file_digest(source / "core.cpp")},
                        "bridge_sha256": {}, "shipping_byte_identity": False,
                        "worker_java_sha256": summary.file_digest(java),
                        "builder_sha256": summary.file_digest(summary.runner.ROOT / "tools/native-trails/build_validation.py"),
                        "instrumentation_diff_sha256": summary.file_digest(directory / "instrumentation.diff"),
                        "native_sha256": {"jni/arm64-v8a/libprojectmtv.so": hashlib.sha256(role.encode()).hexdigest()},
                        "assets_sha256": summary.digest({"assets/presets/" + name: sha for name, sha in records.items()})}
            for artifact in ("apk", "aar"):
                identity[artifact + "_sha256"] = summary.file_digest(Path(identity[artifact]))
            summary.runner.write(directory / "identity.json", identity)
            workers[role] = identity
        (self.work / "audio.u8").write_bytes(b"frozen pcm")
        self.protocol = {"schema": 1, "workers": workers, "presets": records,
                         "profiles": json.loads(json.dumps(self.profiles)), "runner_sha256": summary.file_digest(Path(summary.runner.__file__)),
                         "device": "emulator-fixture", "fingerprint": "fixture-driver", "frames": 480,
                         "pcm_sha256": summary.file_digest(self.work / "audio.u8"),
                         "clock": "frame/30.0", "seed": 12345, "captures": summary.runner.CAPTURES,
                         "limitations": "small fixture"}
        summary.runner.write(self.work / "protocol.json", self.protocol)
        self.jobs = {}
        for name in self.names:
            for profile, role, width, height, rw, rh, level in self.profiles:
                key = summary.digest({"protocol": summary.digest(self.protocol), "preset": records[name], "profile": profile})
                directory = self.work / "jobs" / key
                directory.mkdir(parents=True)
                package = workers[role]["package"]
                private = "/data/user/0/" + package + "/files/native-trails/" + key
                request = dict(summary.runner.request(name, width, height, rw, rh, level),
                               pcmPath=private + "/audio.u8", outputDir=private + "/output")
                manifest = {"status": "ok", "framesRendered": 480, "job": request,
                            "requestSha256": hashlib.sha256((summary.runner.canonical_json(request) + "\n").encode()).hexdigest(),
                            "presetAssetSha256": records[name], "verifiedPresetName": name,
                            "coreReleased": True, "eglDestroyed": True, "glErrorChecks": 480,
                            "presetNameChecks": 480, "eligiblePresetCountAfterFrame479": 1, "presetChangeCounter": 1,
                            "applicationId": package, "device": {"fingerprint": "fixture-driver"},
                            "pcmSha256": self.protocol["pcm_sha256"], "determinism": "instrumented-fixed-clock-seed",
                            "fps": 30, "bundledPresetCount": 9606, "settings": {"autoChange": False},
                            "glRenderer": "fixture", "glVendor": "fixture", "glVersion": "fixture",
                            "serializedFrameMeanMs": 2, "serializedFrameP90Ms": 3,
                            "pssAfterFramesKB": 100, "pssBeforeFramesKB": 80, "renderWallDurationMs": 2000,
                            "timingScope": "onDrawFrame plus glFinish; 360 frames; excludes capture/PNG I/O; emulator engine, not TV app fps",
                            "nativeTrailsStatus": ("standard" if profile == "standard_default" else profile)
                            + " · 1280×720 canvas", "captures": []}
                for frame in summary.runner.CAPTURES:
                    image = np.array([[[10, 20, 30], [20, 30, 40]], [[30, 40, 50], [40, 50, 60]]], np.uint8)
                    path = directory / ("frame-%03d.png" % frame)
                    cv2.imwrite(str(path), image)
                    manifest["captures"].append({"frame": frame, "width": width, "height": height,
                                                  "pngSha256": summary.file_digest(path),
                                                  "rgbSha256": hashlib.sha256(image[:, :, [2, 1, 0]].tobytes()).hexdigest()})
                summary.runner.write(directory / "request.json", request)
                summary.runner.write(directory / "manifest.json", manifest)
                row = {"preset": name, "profile": profile, "key": key, "status": "ok",
                       "frame_hashes": [c["rgbSha256"] for c in manifest["captures"]],
                       "trail_status": manifest["nativeTrailsStatus"], "duration_ms": 2000,
                       "frame_mean_ms": 2, "frame_p90_ms": 3, "pss_kb": 100}
                summary.runner.write(directory / "row.json", row)
                self.jobs[name, profile] = directory

    def collect(self, partial=False):
        return summary.collect_matrix(self.work, self.presets, self.names, partial=partial)

    def change(self, name, value):
        path = self.jobs[self.names[0], "authored"] / name
        data = json.loads(path.read_text())
        data.update(value)
        summary.runner.write(path, data)

    def test_complete_matrix_has_136_verified_jobs(self):
        result = self.collect()
        self.assertEqual(result["verified_jobs"], 136)
        self.assertTrue(result["complete"])
        self.assertEqual(len(result["identity_checks"]), 51)

    def test_missing_job_fails_strict_but_partial_never_claims_completion(self):
        shutil.rmtree(self.jobs[self.names[-1], "high"])
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            self.collect()
        result = self.collect(partial=True)
        self.assertFalse(result["complete"])
        self.assertEqual(result["verified_jobs"], 135)
        self.assertEqual(result["missing_jobs"], [{"preset": self.names[-1], "profile": "high"}])

    def test_failed_or_mixed_manifest_rejected_even_in_partial_mode(self):
        for update in ({"status": "failed"}, {"pcmSha256": "other"},
                       {"device": {"fingerprint": "other"}}, {"glRenderer": "other"}):
            with self.subTest(update=update):
                path = self.jobs[self.names[0], "authored"] / "manifest.json"
                original = path.read_text()
                self.change("manifest.json", update)
                with self.assertRaises(ValueError):
                    self.collect(partial=True)
                path.write_text(original)

    def test_mutated_capture_cannot_be_hidden_by_a_success_row(self):
        (self.jobs[self.names[0], "authored"] / "frame-479.png").write_bytes(b"mutation")
        with self.assertRaisesRegex(ValueError, "PNG checksum"):
            self.collect(partial=True)

    def test_last_capture_identity_mismatch_is_hard_failure(self):
        directory = self.jobs[self.names[0], "authored_repeat"]
        image = np.full((2, 2, 3), 100, np.uint8)
        path = directory / "frame-479.png"
        cv2.imwrite(str(path), image)
        manifest = json.loads((directory / "manifest.json").read_text())
        manifest["captures"][-1].update(pngSha256=summary.file_digest(path),
                                         rgbSha256=hashlib.sha256(image.tobytes()).hexdigest())
        summary.runner.write(directory / "manifest.json", manifest)
        row = json.loads((directory / "row.json").read_text())
        row["frame_hashes"][-1] = manifest["captures"][-1]["rgbSha256"]
        summary.runner.write(directory / "row.json", row)
        with self.assertRaisesRegex(ValueError, "Identity mismatch"):
            self.collect(partial=True)

    def test_stale_row_or_unexpected_job_is_rejected(self):
        self.change("row.json", {"frame_mean_ms": 99})
        with self.assertRaisesRegex(ValueError, "Row differs"):
            self.collect()
        (self.work / "jobs/stale").mkdir()
        with self.assertRaisesRegex(ValueError, "Unexpected job"):
            self.collect(partial=True)

    def test_frozen_protocol_pcm_preset_artifact_and_source_are_checked(self):
        paths = [self.work / "audio.u8", self.presets / self.names[0],
                 Path(self.protocol["workers"]["candidate-native"]["apk"]),
                 self.base / "baseline-native/source/core.cpp"]
        for path in paths:
            with self.subTest(path=path):
                original = path.read_bytes()
                path.write_bytes(b"mutation")
                with self.assertRaises(ValueError):
                    self.collect(partial=True)
                path.write_bytes(original)
        self.protocol["runner_sha256"] = "stale"
        summary.runner.write(self.work / "protocol.json", self.protocol)
        with self.assertRaisesRegex(ValueError, "runner"):
            self.collect(partial=True)

    def test_partial_output_is_labeled_and_strict_failure_writes_nothing(self):
        shutil.rmtree(self.jobs[self.names[-1], "high"])
        output = self.base / "evidence"
        with self.assertRaises(ValueError):
            summary.summarize(self.work, output, preset_root=self.presets, names=self.names)
        self.assertFalse(output.exists())
        summary.summarize(self.work, output, partial=True, preset_root=self.presets, names=self.names)
        data = json.loads((output / "summary.json").read_text())
        self.assertEqual(data["status"], "partial_progress")
        self.assertFalse(data["final_evidence"])
        self.assertEqual(data["expected_jobs"], 136)
        self.assertIn("PARTIAL PROGRESS", (output / "index.html").read_text())
        self.assertTrue((output / "per-preset.csv").exists())

    def test_metrics_are_normalized_and_black_ratios_remain_diagnostics(self):
        black = np.zeros((2, 2, 3), np.uint8)
        white = np.full((2, 2, 3), 255, np.uint8)
        metrics = summary.frame_metrics(white, black)
        self.assertAlmostEqual(metrics["luma"], 1, places=6)
        self.assertAlmostEqual(metrics["mae_authored"], 1, places=6)
        self.assertIsNone(metrics["luma_ratio"])
        self.assertTrue(metrics["near_black_authored"])
        self.assertAlmostEqual(metrics["regularized_luma_ratio"], 1001, places=4)

    def test_complete_export_records_all_hashes_and_measured_medium_high_cost(self):
        directory = self.jobs[self.names[0], "high"]
        manifest = json.loads((directory / "manifest.json").read_text())
        manifest.update(serializedFrameMeanMs=4, serializedFrameP90Ms=6)
        summary.runner.write(directory / "manifest.json", manifest)
        row = json.loads((directory / "row.json").read_text())
        row.update(frame_mean_ms=4, frame_p90_ms=6)
        summary.runner.write(directory / "row.json", row)
        output = self.base / "complete"
        result = summary.summarize(self.work, output, preset_root=self.presets, names=self.names)
        self.assertTrue(result["final_evidence"])
        self.assertEqual(len(result["verified_rows"]), 136)
        self.assertTrue(all(len(row["frame_hashes"]) == 8 for row in result["verified_rows"]))
        costs = result["presets"][0]["medium_high_cost_comparison"]
        self.assertEqual(costs["serializedFrameMeanMs"], {"medium": 2, "high": 4, "high_minus_medium": 2, "high_over_medium": 2})
        self.assertEqual(costs["serializedFrameP90Ms"]["high"], 6)
        self.assertEqual((output / "images/00-authored-300-full.png").read_bytes(),
                         (self.jobs[self.names[0], "authored"] / "frame-300.png").read_bytes())
        self.assertIn("17", result["scope"])

    def test_partial_does_not_hide_a_failed_row_without_a_manifest(self):
        directory = self.jobs[self.names[0], "high"]
        (directory / "manifest.json").unlink()
        row = json.loads((directory / "row.json").read_text())
        row["status"] = "failed"
        summary.runner.write(directory / "row.json", row)
        with self.assertRaisesRegex(ValueError, "Failed rendering"):
            self.collect(partial=True)

    def test_wrong_frozen_profile_set_is_not_partial_coverage(self):
        self.protocol["profiles"].pop()
        summary.runner.write(self.work / "protocol.json", self.protocol)
        with self.assertRaisesRegex(ValueError, "profiles"):
            self.collect(partial=True)

    def test_known_chaotic_and_near_black_cases_have_explicit_visual_flags(self):
        flags = summary.visual_flags("TonyMilkdrop - I Like Cartoon --- Isosceles edit.milk",
                                     {"authored": {"mean": {"near_black_authored": True}}})
        self.assertIn("known_chaotic_preset: compare structure by eye; MAE may reflect divergence", flags)
        self.assertIn("near_black_authored: raw luma ratio omitted; regularized ratio is diagnostic", flags)

    def test_repeat_control_cannot_substitute_a_16_bit_png_with_the_same_decoded_rgb8(self):
        directory = self.jobs[self.names[0], "authored_repeat"]
        path = directory / "frame-479.png"
        original = cv2.imread(str(path))
        cv2.imwrite(str(path), original.astype(np.uint16) * 257)
        manifest = json.loads((directory / "manifest.json").read_text())
        manifest["captures"][-1]["pngSha256"] = summary.file_digest(path)
        summary.runner.write(directory / "manifest.json", manifest)
        with self.assertRaisesRegex(ValueError, "RGB\\(A\\)8"):
            self.collect()


if __name__ == "__main__":
    unittest.main()
