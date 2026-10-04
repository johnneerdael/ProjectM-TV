import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

import summarize_screen as report


def fixture(paths=("one.milk",), rounds=(0, 1), protocol="sparse"):
    manifest = {"protocol": protocol, "windows": [4, 12], "dark_floor": .001,
                "capture_windows": {"4": [120, 150, 180, 210, 239],
                                    "12": [120, 210, 300, 390, 479]},
                "corpus": [{"path": path, "sha256": path} for path in paths]}
    jobs = []
    for path in paths:
        for round_index in rounds:
            for seconds in ([12] if protocol == "sparse" else [4, 12]):
                windows = [4, 12] if protocol == "sparse" else [seconds]
                indices = sorted({i for w in windows for i in report.window_indices(manifest, w)})
                for profile in report.PROFILES:
                    authored = profile in ("authored", "authored_repeat", "candidate_authored")
                    candidate = profile.startswith("candidate")
                    level = .5 if authored else .6 if candidate else .8
                    summaries = {str(w): {"luma": level, "centre_rgb": [level] * 3,
                                          "saturation": level, "lap_native": level,
                                          "lap_1182": level} for w in windows}
                    jobs.append({"key": f"{path}-{round_index}-{seconds}-{profile}",
                                 "preset": {"path": path, "sha256": path},
                                 "profile": profile, "round": round_index,
                                 "config": {"measurement_seconds": seconds}, "status": "success",
                                 "capture_indices": indices,
                                 "sample_hashes": {str(i): "auth" if authored else profile for i in indices},
                                 "summaries": summaries, "comparison_eligible": True,
                                 "comparisons": {str(w): {"img_err": 0 if authored else .1 if candidate else .3}
                                                 for w in windows},
                                 "diagnostics": {"stages": {"warp": "success_reported", "composite": "not_expected"}}})
    return manifest, jobs


class SummaryTests(unittest.TestCase):
    def test_validated_counts_are_unique_and_each_window_is_compared(self):
        manifest, jobs = fixture(("one.milk", "two.milk"))
        result = report.summarize(manifest, jobs, repeat_all=True)
        self.assertEqual(result["counts"]["corpus_presets"], 2)
        self.assertEqual(result["counts"]["eligible_presets"], 2)
        self.assertEqual(result["counts"]["validated_presets"], 2)
        self.assertEqual(result["metrics"]["image_mae"]["preset_classifications"]["gain"], 2)
        self.assertEqual(len(result["comparisons"]), 16)
        self.assertAlmostEqual(result["populations"]["eligible"]["image_mae"]["before_median"], .3)
        self.assertEqual(result["counts"]["all_required_profiles_presets"], 2)
        self.assertEqual(result["coverage"]["windows"]["4"]["complete_presets"], 2)
        self.assertEqual(result["coverage"]["profiles"]["candidate_native"]["successful_presets"], 2)
        self.assertEqual(result["coverage"]["rounds"]["1"]["all_required_profiles_presets"], 2)

    def test_one_pass_is_preliminary(self):
        manifest, jobs = fixture(rounds=(0,))
        result = report.summarize(manifest, jobs)
        self.assertEqual(result["counts"]["preliminary_presets"], 1)
        self.assertEqual(result["counts"]["validated_presets"], 0)
        self.assertEqual(result["presets"][0]["classification_scope"], "preliminary")

    def test_repeat_all_requires_every_profile_not_just_authored(self):
        manifest, jobs = fixture()
        next(j for j in jobs if j["profile"] == "candidate_native" and j["round"] == 1)["sample_hashes"]["120"] = "changed"
        result = report.summarize(manifest, jobs, repeat_all=True)
        self.assertEqual(result["counts"]["eligible_presets"], 0)
        self.assertIn("profile_repeat_hash_mismatch", result["presets"][0]["exclusion_reasons"])

    def test_missing_window_failed_timeout_and_fallback_count_once_per_preset(self):
        manifest, jobs = fixture()
        jobs[3]["status"] = "timeout"
        jobs[4]["status"] = "failed"
        jobs[5]["diagnostics"]["stages"]["warp"] = "failure_reported"
        jobs[6]["summaries"].pop("4")
        result = report.summarize(manifest, jobs, repeat_all=True)
        for name in ("failed_presets", "timeout_presets", "shader_fallback_presets", "incomplete_window_presets"):
            self.assertEqual(result["counts"][name], 1)
        self.assertEqual(result["counts"]["eligible_presets"], 0)
        self.assertEqual(result["coverage"]["windows"]["4"]["complete_presets"], 0)
        self.assertEqual(result["coverage"]["windows"]["12"]["complete_presets"], 1)

    def test_stability_off_identity_and_regenerated_reference_are_all_required(self):
        for profile, field in (("authored_repeat", "authored_repeat_hash_mismatch"),
                               ("candidate_authored", "candidate_off_hash_mismatch")):
            with self.subTest(profile=profile):
                manifest, jobs = fixture()
                next(j for j in jobs if j["profile"] == profile)["sample_hashes"]["120"] = "bad"
                result = report.summarize(manifest, jobs, repeat_all=True)
                self.assertIn(field, result["presets"][0]["exclusion_reasons"])
                self.assertEqual(result["counts"]["eligible_presets"], 0)
        manifest, jobs = fixture()
        jobs[0]["reference_regeneration_changed"] = True
        self.assertEqual(report.summarize(manifest, jobs, repeat_all=True)["counts"]["reference_regenerated_presets"], 1)

    def test_dark_authored_ratio_remains_undefined(self):
        manifest, jobs = fixture()
        for job in jobs:
            if job["profile"] == "authored":
                for summary in job["summaries"].values():
                    summary["luma"] = 0
        result = report.summarize(manifest, jobs, repeat_all=True)
        self.assertTrue(all(c["dark_authored"] for c in result["comparisons"]))
        self.assertTrue(all(c["metrics"]["brightness_ratio_error"]["after"] is None for c in result["comparisons"]))
        self.assertIsNone(result["populations"]["eligible"]["brightness_ratio_error"]["after_median"])

    def test_numeric_tolerance_is_not_noise_or_perceptual_acceptance(self):
        manifest, jobs = fixture()
        for job in jobs:
            if job["profile"].startswith("candidate_") and job["profile"] != "candidate_authored":
                for comparison in job["comparisons"].values():
                    comparison["img_err"] = .30005
        result = report.summarize(manifest, jobs, repeat_all=True)
        self.assertEqual(result["metrics"]["image_mae"]["preset_classifications"]["unchanged_noise_unclassified"], 1)
        self.assertIn("not perceptual", result["methodology"]["numerical_tolerance"])

    def test_full_protocol_needs_distinct_job_for_each_window(self):
        manifest, jobs = fixture(protocol="full")
        result = report.summarize(manifest, jobs, repeat_all=True)
        self.assertEqual(result["counts"]["eligible_presets"], 1)
        jobs = [j for j in jobs if not (j["profile"] == "baseline_native" and j["config"]["measurement_seconds"] == 4)]
        result = report.summarize(manifest, jobs, repeat_all=True)
        self.assertEqual(result["counts"]["all_required_profiles_presets"], 0)
        self.assertIn("missing_required_jobs", result["presets"][0]["exclusion_reasons"])

    def test_mixed_and_significant_regression_report_before_after_values(self):
        manifest, jobs = fixture()
        for job in jobs:
            if job["profile"] == "candidate_native":
                for comparison in job["comparisons"].values():
                    comparison["img_err"] = .8
        result = report.summarize(manifest, jobs, repeat_all=True)
        self.assertEqual(result["metrics"]["image_mae"]["preset_classifications"]["mixed"], 1)
        entry = next(e for e in result["significant_regressions"] if e["metric"] == "image_mae")
        self.assertEqual((entry["before"], entry["after"]), (.3, .8))

    def test_reader_uses_wal_snapshot_while_writer_has_uncommitted_job(self):
        manifest, jobs = fixture()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "screen.sqlite"
            writer = sqlite3.connect(path)
            writer.execute("PRAGMA journal_mode=WAL")
            writer.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT)")
            writer.execute("CREATE TABLE jobs (key TEXT PRIMARY KEY, payload TEXT)")
            writer.execute("INSERT INTO metadata VALUES ('manifest', ?)", (json.dumps(manifest),))
            writer.execute("INSERT INTO jobs VALUES (?, ?)", (jobs[0]["key"], json.dumps(jobs[0])))
            writer.commit()
            writer.execute("INSERT INTO jobs VALUES (?, ?)", (jobs[1]["key"], json.dumps(jobs[1])))
            frozen, stored = report.read_snapshot(path)
            self.assertEqual(frozen, manifest)
            self.assertEqual(len(stored), 1)
            writer.rollback()
            writer.close()

    def test_atomic_exports_include_each_manifest_preset_even_without_jobs(self):
        manifest, jobs = fixture()
        manifest["corpus"].append({"path": "missing.milk", "sha256": "missing"})
        result = report.summarize(manifest, jobs, repeat_all=True)
        with tempfile.TemporaryDirectory() as directory:
            json_path, csv_path = Path(directory) / "report.json", Path(directory) / "presets.csv"
            report.write_reports(result, json_path, csv_path)
            self.assertEqual(json.loads(json_path.read_text())["counts"]["covered_presets"], 1)
            self.assertIn("missing.milk", csv_path.read_text())
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()), ["presets.csv", "report.json"])

    def test_duplicate_logical_jobs_are_not_silently_classified(self):
        manifest, jobs = fixture()
        duplicate = copy.deepcopy(jobs[0])
        duplicate["key"] = "duplicate-key"
        result = report.summarize(manifest, jobs + [duplicate], repeat_all=True)
        self.assertIn("duplicate_logical_jobs", result["presets"][0]["exclusion_reasons"])
        self.assertEqual(result["counts"]["eligible_presets"], 0)

    def test_shards_require_identical_manifest_and_deduplicate_identical_keys(self):
        manifest, jobs = fixture()
        frozen, combined = report.merge_snapshots([(manifest, jobs[:7]), (manifest, jobs[7:]), (manifest, jobs[:1])])
        self.assertEqual(frozen, manifest)
        self.assertEqual(len(combined), len(jobs))
        changed = copy.deepcopy(jobs[0])
        changed["status"] = "failed"
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate job key"):
            report.merge_snapshots([(manifest, jobs), (manifest, [changed])])
        changed_manifest = dict(manifest, protocol="full")
        with self.assertRaisesRegex(ValueError, "Frozen manifests differ"):
            report.merge_snapshots([(manifest, jobs), (changed_manifest, [])])

    def test_missing_image_comparison_is_ineligible_even_with_identical_hashes(self):
        manifest, jobs = fixture()
        jobs[4]["comparisons"].pop("12")
        result = report.summarize(manifest, jobs, repeat_all=True)
        self.assertIn("missing_image_comparisons", result["presets"][0]["exclusion_reasons"])
        self.assertEqual(result["counts"]["eligible_presets"], 0)

    def test_eligible_outlier_has_metric_values_and_unique_preset_count(self):
        manifest, jobs = fixture(tuple(f"{i}.milk" for i in range(10)))
        for job in jobs:
            if job["preset"]["path"] == "9.milk" and job["profile"] == "candidate_native":
                for comparison in job["comparisons"].values():
                    comparison["img_err"] = .9
        result = report.summarize(manifest, jobs, repeat_all=True)
        self.assertEqual(result["counts"]["outlier_presets"], 1)
        entry = next(v for v in result["outliers"] if v["metric"] == "image_mae")
        self.assertEqual((entry["preset"], entry["before"], entry["after"]), ("9.milk", .3, .9))


if __name__ == "__main__":
    unittest.main()
