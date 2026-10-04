"""Offline fixtures exercise native evidence rather than mock validation."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import shutil
import unittest
import zipfile

from PIL import Image
import run

spec = importlib.util.find_spec("compare")
compare = __import__("compare") if spec else None
DRIVER = dict(gl_vendor="test", gl_renderer="GLES3", gl_version="3.0", egl_version="1.0",
              android_fingerprint="fixture", abi="arm64-v8a")


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(compare, "comparison tool is not implemented")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.baseline = self.dataset("baseline")
        self.candidate = self.dataset("candidate")

    def dataset(self, role):
        work = self.root / role
        work.mkdir()
        presets = [{"path": "one.milk", "sha256": hashlib.sha256(b"preset").hexdigest(), "bytes": 6},
                   {"path": "two.milk", "sha256": hashlib.sha256(b"second").hexdigest(), "bytes": 6}]
        textures = [{"path": "test.png", "sha256": hashlib.sha256(b"texture").hexdigest()}]
        inventory = dict(count=2, presets=presets, textures=textures,
                         corpus_sha256=run.digest(presets), textures_sha256=run.digest(textures))
        core = (role + " core").encode()
        identity = dict(variant=role, backend="projectmtv-core-android-v1",
                        source_commit="a59b4e5-fixture" if role == "baseline" else "candidate-fixture",
                        ordered_patches=[dict(name=role, sha256="f" * 64)],
                        instrumentation_sha256="a" * 64, harness_sources_sha256={"observer": "b" * 64},
                        clock_instrumentation_diff_sha256="c" * 64, engine_instrumentation_diff_sha256="d" * 64,
                        core_library_entry="lib/arm64-v8a/libprojectmtv.so", prewarm_setting="pause",
                        core_sha256=hashlib.sha256(core).hexdigest())
        apk = work / "fixture.apk"
        with zipfile.ZipFile(apk, "w") as z:
            z.writestr("assets/backend-identity.json", run.canonical(identity))
            z.writestr(identity["core_library_entry"], core)
            for name, data in (("presets/one.milk", b"preset"), ("presets/two.milk", b"second"), ("textures/test.png", b"texture")):
                z.writestr("assets/" + name, data)
        pcm = {}
        for count in (240, 480):
            path = work / (str(count) + ".u8")
            path.write_bytes(b"x" * (count * 1470))
            pcm[str(count)] = dict(path=str(path), sha256=run.file_hash(path), bytes=path.stat().st_size)
        protocol = dict(schema_version=2, backend="production-projectm-tv-core-ProjectMJNI-EGL-GLES3",
                        roles={role: run.artifact(apk, role, inventory)}, config=dict(width=2364, height=1330,
                        fps=30, seed=12345, warmup_frames=120, measurement_frames=360, capture_frames=run.capture_indices(360)),
                        device_serial="emulator-5580", device={"fingerprint": "fixture"}, pcm=pcm,
                        pcm_protocol="fixture signal", capture_format="RGB8", capture_hash_coverage="selected",
                        retention="PNG", corpus_sha256=inventory["corpus_sha256"], textures_sha256=inventory["textures_sha256"],
                        runner_sha256=hashlib.sha256(role.encode()).hexdigest(), limitations="fixture")
        run.atomic(work / "protocol.json", dict(protocol, sha256=run.digest(protocol)))
        run.atomic(work / "inventory.json", inventory)
        return work

    def pair(self, work, colour=10, status="success", repeat_colour=None, driver=None):
        protocol = json.loads((work / "protocol.json").read_text())
        record = json.loads((work / "inventory.json").read_text())["presets"][0]
        role = work.name
        jobs = []
        for repeat in (1, 2):
            job = run.make_job(protocol, record, role, "selected", repeat, 360)
            directory = work / "jobs" / job["job_id"]
            output = directory / "output"
            if directory.exists():
                shutil.rmtree(directory)
            output.mkdir(parents=True)
            run.atomic(directory / "job.json", job)
            result = dict(job)
            result.update(status=status, preset_filename=record["path"], core_sha256=job["expected_core_sha256"],
                          requested_preset_sha256=record["sha256"], backend_identity=protocol["roles"][role]["backend_identity"],
                          pcm_uint8_sha256=protocol["pcm"]["480"]["sha256"], **(DRIVER if driver is None else driver))
            if status == "success":
                samples = []
                value = repeat_colour if repeat == 2 and repeat_colour is not None else colour
                for frame in job["capture_frames"]:
                    path = output / (str(frame) + ".png")
                    Image.new("RGBA", (256, 144), (value + frame % 2, value, value, 255)).save(path)
                    samples.append(dict(frame=frame, sha256=hashlib.sha256(bytes([value, frame % 256])).hexdigest(),
                                        bytes=2364 * 1330 * 3, thumbnail_path=path.name, thumbnail_sha256=run.file_hash(path),
                                        thumbnail_bytes=path.stat().st_size, metrics={"native_rgb_mean": [value / 255] * 3}))
                hashes = {s["frame"]: s["sha256"] for s in samples}
                frames = [dict(frame=i, preset_filename=record["path"], change_counter=1, pcm_bytes=1470,
                               captured=i in hashes, sha256=hashes.get(i)) for i in range(480)]
                raw = "".join(run.canonical(f) + "\n" for f in frames).encode()
                (output / "frames.jsonl.gz").write_bytes(gzip.compress(raw))
                result.update(selected_files=samples, rendered_frames=480, eligible_count=1,
                              frames_metadata_sha256=hashlib.sha256(raw).hexdigest())
            else:
                result["error"] = "load failed"
            run.atomic(output / "result.json", result)
            row = dict(key=job["job_id"], protocol_sha256=protocol["sha256"], preset=record, role=role,
                       repeat=repeat, capture_mode="selected", measurement_frames=360, status=status,
                       result=result, selected_native_sha256={str(s["frame"]): s["sha256"] for s in result.get("selected_files", [])},
                       retained_files=[dict(path=p.relative_to(directory).as_posix(), bytes=p.stat().st_size, sha256=run.file_hash(p))
                                       for p in directory.rglob("*") if p.is_file()])
            if status == "success":
                trace = output / "frames.jsonl.gz"
                row["frame_trace"] = dict(path="output/frames.jsonl.gz", compressed_sha256=run.file_hash(trace),
                                          compressed_bytes=trace.stat().st_size, uncompressed_sha256=hashlib.sha256(raw).hexdigest(),
                                          uncompressed_bytes=len(raw), encoding="gzip-lossless-jsonl")
            run.save_row(directory / "row.json", row)
            jobs.append(row)
        exact = status == "success" and jobs[0]["selected_native_sha256"] == jobs[1]["selected_native_sha256"]
        key = run.digest(dict(protocol_sha256=protocol["sha256"], preset=record, role=role))
        pair = dict(key=key, protocol_sha256=protocol["sha256"], preset=record, role=role,
                    status=("success" if exact else "nondeterministic") if status == "success" else status,
                    repeat_exact_selected=exact, runs=["jobs/" + j["key"] + "/row.json" for j in jobs],
                    hash_coverage=run.capture_indices(360), driver=DRIVER if driver is None else driver)
        pair["render_input_sha256"] = run.render_input_signature(protocol, role, record, pair["driver"])
        path = work / "rows" / (key + ".json")
        run.save_row(path, pair)
        return path

    def report(self, limit=1):
        return compare.compare_datasets(self.baseline, self.candidate, limit=limit)

    def category(self):
        return self.report()["cases"][0]["category"]

    def rewrite(self, path, update):
        row = json.loads(path.read_text())
        row.pop("payload_sha256", None)
        update(row)
        run.save_row(path, row)

    def test_equal_native_samples_allow_different_core_source_and_runner(self):
        self.pair(self.baseline)
        self.pair(self.candidate)
        report = self.report()
        self.assertEqual(report["cases"][0]["category"], "unchanged_native_samples")
        self.assertFalse(report["complete_coverage"])
        self.assertEqual(report["unselected_presets"], 1)
        self.assertNotEqual(report["datasets"]["baseline"]["protocol"]["sha256"], report["datasets"]["candidate"]["protocol"]["sha256"])

    def test_changed_native_samples_rank_rgb_and_adjacent_motion(self):
        self.pair(self.baseline, colour=10)
        self.pair(self.candidate, colour=20)
        case = self.report()["cases"][0]
        self.assertEqual(case["category"], "changed_needs_visual_review")
        self.assertAlmostEqual(case["thumbnail_rgb_mae"], 10 / 255)
        self.assertEqual(len(case["adjacent_thumbnail_motion"]), 8)
        self.assertEqual(case["samples"][0]["baseline"]["metrics"]["native_rgb_mean"], [10 / 255] * 3)

    def test_missing_candidate_is_pending(self):
        self.pair(self.baseline)
        report = self.report()
        self.assertEqual(report["counts"]["missing_pending"], 1)
        self.assertEqual(report["verified_pairs"], {"baseline": 1, "candidate": 0})

    def test_recovered_and_new_and_both_failed(self):
        for first, second, expected in (("failed", "success", "recovered_load_compatibility"),
                                         ("success", "failed", "new_failure"), ("failed", "failed", "both_failed")):
            with self.subTest(first=first, second=second):
                self.pair(self.baseline, status=first)
                self.pair(self.candidate, status=second)
                self.assertEqual(self.category(), expected)

    def test_nondeterministic_repeat_cannot_be_changed(self):
        self.pair(self.baseline, repeat_colour=11)
        self.pair(self.candidate)
        self.assertEqual(self.category(), "nondeterministic_uncomparable")

    def test_corrupt_thumbnail_is_integrity_issue(self):
        p = self.pair(self.baseline)
        self.pair(self.candidate)
        row = json.loads(p.read_text())
        thumb = self.baseline / Path(row["runs"][0]).parent / "output/120.png"
        thumb.write_bytes(b"corrupt")
        report = self.report()
        self.assertEqual(report["cases"][0]["category"], "nondeterministic_uncomparable")
        self.assertTrue(report["integrity_issues"])

    def test_missing_repeat_is_pending(self):
        p = self.pair(self.baseline)
        self.pair(self.candidate)
        row = json.loads(p.read_text())
        (self.baseline / row["runs"][1]).unlink()
        self.assertEqual(self.category(), "missing_pending")

    def test_pair_driver_mismatch_is_uncomparable(self):
        self.pair(self.baseline)
        self.pair(self.candidate, driver=dict(DRIVER, gl_renderer="other GPU"))
        self.assertEqual(self.category(), "nondeterministic_uncomparable")

    def test_failed_unknown_driver_is_uncomparable(self):
        self.pair(self.baseline, status="failed", driver={})
        self.pair(self.candidate)
        self.assertEqual(self.category(), "nondeterministic_uncomparable")

    def test_duplicated_repeat_rejected(self):
        p = self.pair(self.baseline)
        self.pair(self.candidate)
        self.rewrite(p, lambda r: r.update(runs=[r["runs"][0]] * 2))
        self.assertTrue(self.report()["integrity_issues"])

    def test_forged_pair_repeat_status_rejected(self):
        p = self.pair(self.baseline, repeat_colour=11)
        self.pair(self.candidate)
        self.rewrite(p, lambda r: r.update(status="success", repeat_exact_selected=True))
        self.assertTrue(self.report()["integrity_issues"])

    def test_protocol_checksum_mismatch_fails_closed(self):
        p = self.candidate / "protocol.json"
        protocol = json.loads(p.read_text())
        protocol["config"]["width"] = 1
        run.atomic(p, protocol)
        with self.assertRaisesRegex(ValueError, "protocol checksum"):
            self.report()

    def test_corrupt_pcm_fails_closed(self):
        (self.candidate / "480.u8").write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError, "PCM"):
            self.report()

    def test_runtime_input_mismatch_rejected_even_failure(self):
        p = self.pair(self.baseline, status="failed")
        self.pair(self.candidate)
        row = json.loads(p.read_text())
        job_path = self.baseline / Path(row["runs"][0]).parent / "job.json"
        packet = json.loads(job_path.read_text())
        packet["pcm_uint8_sha256"] = "e" * 64
        run.atomic(job_path, packet)
        job_row = self.baseline / row["runs"][0]
        def refresh(r):
            for f in r["retained_files"]:
                if f["path"] == "job.json":
                    f.update(sha256=run.file_hash(job_path), bytes=job_path.stat().st_size)
        self.rewrite(job_row, refresh)
        self.assertTrue(self.report()["integrity_issues"])

    def test_output_inside_dataset_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            compare.write_report(self.baseline, self.candidate, self.candidate / "comparison.json", limit=1)

    def test_default_covers_every_inventory_record_including_pending(self):
        self.pair(self.baseline)
        self.pair(self.candidate)
        report = compare.compare_datasets(self.baseline, self.candidate)
        self.assertEqual(report["selected_presets"], 2)
        self.assertEqual(report["counts"]["missing_pending"], 1)
        self.assertEqual(report["unselected_presets"], 0)
        self.assertFalse(report["complete_coverage"])

    def test_successful_producer_driver_mismatch_is_integrity_issue(self):
        p = self.pair(self.baseline)
        self.pair(self.candidate)
        pair = json.loads(p.read_text())
        path = self.baseline / pair["runs"][1]
        result_path = path.parent / "output/result.json"
        result = json.loads(result_path.read_text())
        result["gl_renderer"] = "changed GPU"
        run.atomic(result_path, result)
        def update(r):
            r["result"] = result
            for f in r["retained_files"]:
                if f["path"] == "output/result.json":
                    f.update(sha256=run.file_hash(result_path), bytes=result_path.stat().st_size)
        self.rewrite(path, update)
        report = self.report()
        self.assertTrue(report["integrity_issues"])
        self.assertEqual(report["cases"][0]["category"], "nondeterministic_uncomparable")

    def test_failed_producer_available_wrong_identity_is_integrity_issue(self):
        p = self.pair(self.baseline, status="failed")
        self.pair(self.candidate)
        pair = json.loads(p.read_text())
        path = self.baseline / pair["runs"][0]
        result_path = path.parent / "output/result.json"
        result = json.loads(result_path.read_text())
        result["requested_preset_sha256"] = "0" * 64
        run.atomic(result_path, result)
        def update(r):
            r["result"] = result
            for f in r["retained_files"]:
                if f["path"] == "output/result.json":
                    f.update(sha256=run.file_hash(result_path), bytes=result_path.stat().st_size)
        self.rewrite(path, update)
        self.assertTrue(self.report()["integrity_issues"])

    def test_observer_mismatch_fails_closed(self):
        a = compare.load_dataset(self.baseline, "baseline")
        b = compare.load_dataset(self.candidate, "candidate")
        b["protocol"]["roles"]["candidate"]["backend_identity"]["instrumentation_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "observer"):
            compare.verify_compatible(a, b)

    def test_render_settings_mismatch_fails_closed(self):
        a = compare.load_dataset(self.baseline, "baseline")
        b = compare.load_dataset(self.candidate, "candidate")
        b["protocol"]["config"]["width"] = 1182
        with self.assertRaisesRegex(ValueError, "config"):
            compare.verify_compatible(a, b)

    def test_apk_asset_bytes_mismatch_fails_closed(self):
        apk = self.candidate / "fixture.apk"
        with zipfile.ZipFile(apk) as z:
            entries = {name: z.read(name) for name in z.namelist()}
        entries["assets/presets/one.milk"] = b"wrong!"
        with zipfile.ZipFile(apk, "w") as z:
            for name, data in entries.items():
                z.writestr(name, data)
        with self.assertRaisesRegex(ValueError, "APK asset"):
            self.report()

    def test_v2_failed_attempt_result_preserves_original_path(self):
        p = self.pair(self.baseline, status="failed")
        self.pair(self.candidate)
        pair = json.loads(p.read_text())
        for relative in pair["runs"]:
            path = self.baseline / relative
            incoming = path.parent / "attempts/token/output"
            incoming.mkdir(parents=True)
            (path.parent / "output/result.json").rename(incoming / "result.json")
            def update(r):
                r["result_path"] = "attempts/token/output/result.json"
                for f in r["retained_files"]:
                    if f["path"] == "output/result.json":
                        f["path"] = r["result_path"]
            self.rewrite(path, update)
        case = self.report()["cases"][0]
        self.assertEqual(case["category"], "recovered_load_compatibility")
        self.assertEqual(case["baseline"]["runs"][0]["result_path"], "attempts/token/output/result.json")

    def test_failed_producer_without_diagnostic_is_integrity_issue(self):
        p = self.pair(self.baseline, status="failed")
        self.pair(self.candidate)
        pair = json.loads(p.read_text())
        path = self.baseline / pair["runs"][0]
        result_path = path.parent / "output/result.json"
        result = json.loads(result_path.read_text())
        result.pop("error")
        run.atomic(result_path, result)
        def update(r):
            r["result"] = result
            for f in r["retained_files"]:
                if f["path"] == "output/result.json":
                    f.update(sha256=run.file_hash(result_path), bytes=result_path.stat().st_size)
        self.rewrite(path, update)
        self.assertTrue(self.report()["integrity_issues"])

    def test_declared_embedded_backend_must_be_actual_core(self):
        path = self.candidate / "protocol.json"
        protocol = json.loads(path.read_text())
        protocol["roles"]["candidate"]["backend_identity"]["backend"] = "direct-projectM"
        protocol.pop("sha256")
        run.atomic(path, dict(protocol, sha256=run.digest(protocol)))
        with self.assertRaisesRegex(ValueError, "embedded backend"):
            self.report()

    def test_native_proof_retention_flag_does_not_change_render_inputs(self):
        p = self.pair(self.baseline)
        self.pair(self.candidate)
        pair = json.loads(p.read_text())
        path = self.baseline / pair["runs"][0]
        packet_path = path.parent / "job.json"
        packet = json.loads(packet_path.read_text())
        packet["retain_native_frames"] = True
        run.atomic(packet_path, packet)
        def update(r):
            for f in r["retained_files"]:
                if f["path"] == "job.json":
                    f.update(sha256=run.file_hash(packet_path), bytes=packet_path.stat().st_size)
        self.rewrite(path, update)
        self.assertEqual(self.category(), "unchanged_native_samples")

    def test_preinit_host_failure_then_success_is_valid_uncomparable_evidence(self):
        p = self.pair(self.baseline)
        self.pair(self.candidate)
        pair = json.loads(p.read_text())
        path = self.baseline / pair["runs"][0]
        (path.parent / "output/result.json").unlink()
        def update(r):
            r.pop("result")
            r.update(status="failed", error="transport failure")
            r["retained_files"] = [f for f in r["retained_files"] if f["path"] != "output/result.json"]
        self.rewrite(path, update)
        protocol = json.loads((self.baseline / "protocol.json").read_text())
        def update_pair(r):
            r.update(status="failed", repeat_exact_selected=False, driver={k: None for k in DRIVER})
            r["render_input_sha256"] = run.render_input_signature(protocol, "baseline", r["preset"], r["driver"])
        self.rewrite(p, update_pair)
        report = self.report()
        self.assertFalse(report["integrity_issues"])
        self.assertEqual(report["cases"][0]["category"], "nondeterministic_uncomparable")

    def test_bound_required(self):
        with self.assertRaises(ValueError):
            self.report(limit=0)


if __name__ == "__main__":
    unittest.main()
