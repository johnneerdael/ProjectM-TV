import hashlib
import io
import json
from pathlib import Path
import sqlite3
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import cv2
import numpy as np

import run_corpus as runner


def manifest_fixture():
    return {"protocol": runner.PROTOCOL, "workers": {
        "baseline": {"package": "nl.neerdael.projectmtv.corpusbaseline"},
        "candidate": {"package": "nl.neerdael.projectmtv.corpuscandidate"}},
        "corpus": [{"path": "a 'quoted'.milk", "sha256": "preset"}],
        "index_sha256": "index", "pcm": {"uint8_sha256": "audio"},
        "namespace": "projectmtv_core_corpus_test", "windows": [4, 12],
        "capture_windows": {str(k): v for k, v in runner.WINDOWS.items()}, "dark_floor": .001}


def worker_manifest(request, request_hash="request"):
    return {"protocol": runner.PROTOCOL, "status": "ok", "applicationId": "nl.neerdael.projectmtv.corpusbaseline",
            "job": request, "requestSha256": request_hash, "pcmSha256": "audio", "indexSha256": "index",
            "presetAssetSha256": "preset", "framesRendered": 480, "frameCountExpected": 480,
            "presetNameChecks": 480, "glErrorChecks": 480, "verifiedPresetName": request["preset"],
            "eligiblePresetCountBeforeFrame0": 1, "eligiblePresetCountAfterFrame479": 1, "presetChangeCounter": 1,
            "coreReleased": True, "eglDestroyed": True, "determinism": "instrumented-fixed-clock-seed",
            "bundledPresetCount": 1, "forcedPresetPrefix": runner.preset_prefix(request["preset"]),
            "captures": [{"frame": i, "width": request["width"], "height": request["height"],
                          "path": request["outputDir"] + f"/frame-{i:03d}.png",
                          "rgbSha256": "a" * 64, "pngSha256": "b" * 64} for i in runner.CAPTURES]}


class RunnerTests(unittest.TestCase):
    def test_unsigned_audio_uses_exact_round_clip_mapping_and_fixed_length(self):
        samples = np.array([-2, -1, 0, .5, 1, 2], dtype=np.float32)
        self.assertEqual(runner.to_unsigned_pcm(samples).tolist(), [0, 1, 128, 192, 255, 255])
        floating, unsigned = runner.signal()
        self.assertEqual(len(unsigned), 705600)
        self.assertEqual(len(floating), 705600 * 4)
        self.assertEqual(runner.signal(), (floating, unsigned))

    def test_utf8_prefix_is_bounded_without_splitting_unicode(self):
        name = "é" * 80 + ".milk"
        prefix = runner.preset_prefix(name)
        self.assertEqual(len(prefix.encode("utf-8")), 80)
        self.assertTrue(name.startswith(prefix))
        for unsafe in ("../a.milk", "a\n.milk", "a\x00.milk"):
            with self.assertRaises(ValueError):
                runner.preset_prefix(unsafe)

    def test_profiles_rounds_and_reference_zero_are_exact(self):
        manifest = manifest_fixture()
        jobs = list(runner.planned_jobs(manifest))
        self.assertEqual(len(jobs), 14)
        self.assertEqual({j["round"] for j in jobs}, {0, 1})
        authored = next(j for j in jobs if j["profile"] == "authored")
        request = runner.request_for(manifest, authored)
        self.assertEqual((request["referenceWidth"], request["referenceHeight"]), (0, 0))
        self.assertEqual((request["width"], request["height"]), (1182, 665))
        native = runner.request_for(manifest, next(j for j in jobs if j["profile"] == "candidate_native"))
        self.assertEqual((native["width"], native["height"], native["referenceWidth"], native["referenceHeight"]), (3840, 2160, 1024, 768))
        self.assertTrue(request["instrumented"])
        self.assertEqual(request["seed"], 12345)

    def test_complete_group_never_regenerates_an_authored_reference(self):
        saved = {"status": "success"}
        self.assertFalse(runner.should_execute(saved, "authored", True, False, False))
        self.assertTrue(runner.should_execute(saved, "authored", False, False, False))
        self.assertFalse(runner.should_execute(saved, "candidate_native", False, False, False))
        self.assertTrue(runner.should_execute({"status": "failed"}, "authored", True, False, True))

    def test_worker_manifest_requires_all_frames_exact_preset_and_cleanup(self):
        frozen = manifest_fixture()
        job = next(runner.planned_jobs(frozen))
        request = runner.request_for(frozen, job)
        manifest = worker_manifest(request)
        runner.validate_manifest(manifest, frozen, job, request, "request")
        for field, bad in (("framesRendered", 479), ("verifiedPresetName", "different.milk"),
                           ("coreReleased", False), ("eglDestroyed", False), ("status", "failed"),
                           ("presetAssetSha256", "changed"), ("pcmSha256", "changed")):
            with self.subTest(field=field), self.assertRaises(ValueError):
                runner.validate_manifest(dict(manifest, **{field: bad}), frozen, job, request, "request")

    def test_worker_capture_duplicate_missing_or_outside_path_is_rejected(self):
        frozen = manifest_fixture()
        job = next(runner.planned_jobs(frozen))
        request = runner.request_for(frozen, job)
        manifest = worker_manifest(request)
        for capture_set in (manifest["captures"][:-1], manifest["captures"] + manifest["captures"][:1],
                            [dict(c, path="/sdcard/capture.png") for c in manifest["captures"]]):
            with self.assertRaises(ValueError):
                runner.validate_manifest(dict(manifest, captures=capture_set), frozen, job, request, "request")

    def test_capture_accepts_only_owned_android_data_alias(self):
        frozen = manifest_fixture()
        job = next(runner.planned_jobs(frozen))
        request = runner.request_for(frozen, job)
        manifest = worker_manifest(request)
        alias = [dict(c, path=c["path"].replace("/data/user/0/", "/data/data/", 1)) for c in manifest["captures"]]
        runner.validate_manifest(dict(manifest, captures=alias), frozen, job, request, "request")
        for bad in (alias[0]["path"].replace("corpusbaseline/", "corpuscandidate/", 1),
                    alias[0]["path"].replace("/files/", "/files/../files/", 1)):
            with self.assertRaises(ValueError):
                runner.validate_manifest(dict(manifest, captures=[dict(alias[0], path=bad)] + alias[1:]),
                                         frozen, job, request, "request")

    def test_safe_tar_rejects_traversal_links_and_duplicate_members(self):
        for name, kind in (("../outside", tarfile.REGTYPE), ("/absolute", tarfile.REGTYPE),
                           ("output/link", tarfile.SYMTYPE), ("output/hard", tarfile.LNKTYPE)):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                archive = Path(directory) / "bad.tar"
                with tarfile.open(archive, "w") as stream:
                    member = tarfile.TarInfo(name)
                    member.type = kind
                    member.linkname = "../../outside"
                    stream.addfile(member)
                with self.assertRaises(ValueError):
                    runner.safe_extract(archive, Path(directory) / "extracted")
                self.assertFalse((Path(directory) / "outside").exists())

    def test_png_rgb_hash_ignores_alpha_but_preserves_channel_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frame.png"
            rgba = np.zeros((2, 3, 4), np.uint8)
            rgba[:, :, :3] = [31, 63, 127]
            rgba[:, :, 3] = 255
            cv2.imwrite(str(path), rgba[:, :, [2, 1, 0, 3]])
            capture = {"width": 3, "height": 2,
                       "rgbSha256": hashlib.sha256(rgba[:, :, :3].tobytes()).hexdigest(),
                       "pngSha256": runner.file_hash(path)}
            frame = runner.decode_capture(path, capture)
            self.assertEqual(frame[0, 0].tolist(), [31, 63, 127])
            with self.assertRaises(ValueError):
                runner.decode_capture(path, dict(capture, rgbSha256="incorrect"))

    def test_window_metrics_use_five_selected_frames_and_dark_ratio_is_undefined(self):
        frames = {i: np.full((3, 4, 3), n, np.uint8) for n, i in enumerate(runner.CAPTURES)}
        summaries = runner.sample_summaries(frames)
        self.assertAlmostEqual(summaries["4"]["luma"], 2 / 255, places=7)
        comparisons = runner.compare_samples(frames, {i: np.zeros_like(f) for i, f in frames.items()}, summaries,
                                             {"4": {"luma": 0, "centre_rgb": [0, 0, 0]}, "12": {"luma": 0, "centre_rgb": [0, 0, 0]}}, .001)
        self.assertIsNone(comparisons["4"]["luma_ratio"])
        self.assertAlmostEqual(comparisons["4"]["img_err"], 2 / 255, places=7)

    def test_store_freezes_manifest_and_status_reads_committed_wal(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            frozen = manifest_fixture()
            with runner.Store(work, frozen) as store:
                store.put("one", {"status": "success", "preset": {"path": "one"}})
                store.db.execute("INSERT INTO jobs VALUES (?, ?)", ("pending", '{}'))
                status = runner.status(work)
                self.assertEqual(status["stored_jobs"], 1)
                store.db.rollback()
            with self.assertRaisesRegex(ValueError, "Frozen manifest"):
                runner.Store(work, dict(frozen, protocol="other"))

    def test_reference_change_invalidates_dependent_comparisons(self):
        with tempfile.TemporaryDirectory() as directory:
            with runner.Store(Path(directory), manifest_fixture()) as store:
                store.put("candidate", {"reference_job_key": "auth", "comparisons": {"4": {"img_err": .2}}, "status": "success"})
                store.invalidate_reference("auth")
                row = store.get("candidate")
                self.assertFalse(row["comparison_eligible"])
                self.assertNotIn("comparisons", row)

    def test_adb_shell_quotes_arguments_including_property_prefix(self):
        command = runner.remote_command(["setprop", "debug.projectmtv.preset", "a 'quoted' $name; .milk"])
        import shlex
        self.assertEqual(shlex.split(command), ["setprop", "debug.projectmtv.preset", "a 'quoted' $name; .milk"])

    def test_sleeping_device_is_rejected_without_wake_command(self):
        class FakeAdb:
            calls = []
            def shell(self, *args, **kwargs):
                self.calls.append(args)
                return "mWakefulness=Asleep\nmInteractive=false"
        adb = FakeAdb()
        with self.assertRaisesRegex(RuntimeError, "awake"):
            runner.require_awake(adb)
        self.assertEqual(adb.calls, [("dumpsys", "power")])

    def test_cleanup_attempts_property_restore_and_both_owned_stops_after_error(self):
        class FakeAdb:
            calls = []
            def shell(self, *args, **kwargs):
                self.calls.append(args)
                if args[0] == "setprop":
                    raise OSError("temporarily unavailable")
        adb = FakeAdb()
        errors = runner.restore_session(adb, manifest_fixture()["workers"], "previous")
        self.assertEqual(len(errors), 1)
        self.assertEqual(adb.calls, [("setprop", "debug.projectmtv.preset", "previous"),
                                    ("am", "force-stop", "nl.neerdael.projectmtv.corpusbaseline"),
                                    ("am", "force-stop", "nl.neerdael.projectmtv.corpuscandidate")])

    def test_each_job_stops_owned_process_before_instrumentation_and_records_stage_failure(self):
        class FakeAdb:
            def __init__(self):
                self.calls = []
            def shell(self, *args, **kwargs):
                self.calls.append(args)
                if args == ("dumpsys", "power"):
                    return "mWakefulness=Awake\nmInteractive=true"
                return ""
            def exists(self, *args):
                self.calls.append(args)
                return False
            def call(self, *args, **kwargs):
                self.calls.append(args)
                if args[0] == "push":
                    import subprocess
                    raise subprocess.CalledProcessError(1, "push")
        frozen = manifest_fixture()
        frozen["workers"]["baseline"].update(source_identity_sha256="source", native_sha256={"jni/arm64-v8a/libprojectmtv.so": "native"})
        adb = FakeAdb()
        with tempfile.TemporaryDirectory() as directory:
            result, frames, local = runner.run_one(adb, frozen, next(runner.planned_jobs(frozen)), Path(directory), 1)
            self.assertEqual(result["status"], "failed")
            self.assertEqual(frames, {})
            self.assertTrue(local.exists())  # retained until the caller's atomic DB commit
            self.assertTrue(Path(result["diagnostics"]["log"]).exists())
        stop = ("am", "force-stop", "nl.neerdael.projectmtv.corpusbaseline")
        self.assertEqual(adb.calls[1], stop)
        self.assertEqual(adb.calls[-1], stop)
        self.assertFalse(any("corpuscandidate" in str(call) or "quadverify" in str(call) for call in adb.calls))

    def test_generic_shader_fallback_diagnostic_blocks_numerical_gain(self):
        diagnostics = runner.bounded_diagnostics("ProjectM: Shader compilation failed; fallback active")
        self.assertTrue(all(value == "failure_reported" for value in diagnostics["stages"].values()))

    def test_source_provenance_rejects_wrong_baseline_or_patch_series(self):
        baseline = {"source_commit": runner.BASELINE, "published_baseline_source_commit": runner.BASELINE,
                    "published_baseline_aar_sha256": runner.PUBLISHED_AAR, "ordered_patches": [
                        {"name": f"{i:04d}-test.patch", "sha256": str(i)} for i in range(1, 25)]}
        candidate = dict(baseline, source_commit="candidate", ordered_patches=baseline["ordered_patches"] + [{"name": "0025-test.patch", "sha256": "25"}])
        runner.validate_source_pair(baseline, candidate)
        with self.assertRaises(ValueError):
            runner.validate_source_pair(dict(baseline, source_commit="wrong"), candidate)
        changed = dict(candidate, ordered_patches=[dict(p, sha256="changed") for p in candidate["ordered_patches"]])
        with self.assertRaises(ValueError):
            runner.validate_source_pair(baseline, changed)


if __name__ == "__main__":
    unittest.main()
