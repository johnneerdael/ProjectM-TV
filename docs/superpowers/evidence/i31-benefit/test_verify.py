"""Bounded adversarial custody checks; no workers, renders, or timing jobs."""
import copy
import gzip
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from benchmark import analyze, digest, gamma_source_calculation, verify_job_summary, summarize_jobs
from verify import ROOT, REPO, verify, verify_visual

class CustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = {name: json.loads((ROOT / name).read_text()) for name in
                    ("workers.json", "schedule.json", "inputs.json", "requests.json", "custody.json", "analysis.json")}
        with gzip.open(ROOT / "timed-runs.json.gz", "rt") as stream:
            cls.base["runs"] = json.load(stream)

    def setUp(self):
        self.data = copy.deepcopy(self.base)
        self.name = self.data["schedule.json"][0]["name"]

    def reject(self, root=ROOT):
        with self.assertRaises((AssertionError, FileNotFoundError)):
            verify(root, REPO, data=self.data, visuals=False)

    def recustody(self, name):
        self.data["custody.json"][name.removesuffix(".json") + "_sha256"] = digest(self.data[name])

    def test_valid_frozen_batch_and_analysis(self):
        self.assertEqual(verify(data=self.data, visuals=False), 28800)

    def change_timings_and_reanalyze(self):
        for run in self.data["runs"].values():
            if run["identity"]["role"] == "with-0019":
                for sample in run["samples"]:
                    if sample["measured"]:
                        sample["gpu_ns"] = int(sample["gpu_ns"] * 0.9)
                        sample["complete_ms"] *= 0.9
                        sample["submit_ms"] *= 0.9
        self.data["analysis.json"] = analyze(self.data["schedule.json"], self.data["runs"])

    def test_correlated_timing_and_rederived_analysis_edit(self):
        self.change_timings_and_reanalyze()
        self.reject()

    def test_correlated_timing_analysis_and_receipt_edit(self):
        self.change_timings_and_reanalyze()
        # Even coherently updating the adjacent receipt cannot replace the
        # independently fixed expected corpus digest in the verifier.
        self.data["custody.json"]["timed_corpus_sha256"] = digest(self.data["runs"])
        self.reject()

    def test_correlated_timing_analysis_job_summary_and_receipt_edit(self):
        self.change_timings_and_reanalyze()
        self.data["job-summary.json"] = summarize_jobs(self.data["schedule.json"], self.data["runs"])
        self.data["custody.json"]["timed_corpus_sha256"] = digest(self.data["runs"])
        self.reject()

    def test_wrong_profile(self):
        self.data["runs"][self.name]["config"]["feedback_detail"] = 0.0
        self.reject()

    def test_wrong_config_type(self):
        self.data["runs"][self.name]["config"]["line_antialiasing"] = 0
        self.reject()

    def test_wrong_seed(self):
        self.data["runs"][self.name]["config"]["seed"] = 42
        self.reject()

    def test_coherently_changed_request_config(self):
        receipt = self.data["requests.json"]["requests"][self.name]
        receipt["request"]["config"]["seed"] = 42
        receipt["request_sha256"] = digest(receipt["request"])
        self.data["runs"][self.name]["config"]["seed"] = 42
        self.recustody("requests.json")
        self.reject()

    def test_wrong_scheduled_preset(self):
        receipt = self.data["requests.json"]["requests"][self.name]
        receipt["request"]["preset_path"] = receipt["request"]["preset_path"].replace("original.milk", "inactive-gamma2.milk")
        receipt["request_sha256"] = digest(receipt["request"])
        self.recustody("requests.json")
        self.reject()

    def test_audio_and_texture_hashes(self):
        for field in ("pcm_sha256", "textures_sha256"):
            with self.subTest(field=field):
                self.data = copy.deepcopy(self.base)
                self.data["requests.json"]["requests"][self.name]["input_hashes"][field] = "0" * 64
                self.recustody("requests.json")
                self.reject()

    def test_missing_run_or_request(self):
        for field in ("runs", "requests.json"):
            with self.subTest(field=field):
                self.data = copy.deepcopy(self.base)
                container = self.data[field] if field == "runs" else self.data[field]["requests"]
                del container[self.name]
                self.reject()

    def test_source_inventory_tamper(self):
        self.data["workers.json"]["with-0019"]["source"]["src/libprojectM/MilkdropPreset/VideoEcho.cpp"] = "0" * 64
        self.recustody("workers.json")
        self.reject()

    def test_worker_identity_tamper(self):
        self.data["runs"][self.name]["identity"]["worker_sha256"] = "0" * 64
        self.reject()

    def test_jointly_changed_worker_receipts(self):
        role = self.data["runs"][self.name]["identity"]["role"]
        self.data["workers.json"][role]["worker_sha256"] = "0" * 64
        self.data["runs"][self.name]["identity"]["worker_sha256"] = "0" * 64
        receipt = self.data["requests.json"]["requests"][self.name]
        receipt["request"]["identity"]["worker_sha256"] = "0" * 64
        receipt["request_sha256"] = digest(receipt["request"])
        self.recustody("requests.json")
        self.recustody("workers.json")
        self.reject()

    def test_warmup_classification(self):
        self.data["runs"][self.name]["samples"][0]["measured"] = True
        self.reject()

    def test_inactive_control_gamma(self):
        name = next(name for name in self.data["runs"] if name.startswith("inactive-classic"))
        self.data["runs"][name]["samples"][200]["gamma"] = 2.000999927520752
        self.reject()

    def test_all_published_statistic_classes(self):
        metric = "gpu_ms"
        for field in ("before_ms", "change_percent", "paired_block_bootstrap95_ms", "all_blocks_faster", "blocks", "jobs"):
            with self.subTest(field=field):
                self.data = copy.deepcopy(self.base)
                case = self.data["analysis.json"]["original-standard"]
                values = case["metrics"][metric]
                if field == "blocks": values[field][0]["delta_ms"] += 0.1
                elif field == "jobs": case[field] -= 1
                elif field == "paired_block_bootstrap95_ms": values[field][0] += 0.1
                elif field == "all_blocks_faster": values[field] = False
                else: values[field] += 0.1
                self.reject()

    def test_missing_and_coherently_tampered_source_proof(self):
        for mutation in ("missing", "extra-edit"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                for directory in ("source-proof", "harness"):
                    shutil.copytree(ROOT / directory, root / directory)
                self.data = copy.deepcopy(self.base)
                file = root / "source-proof/without-0019.cpp"
                if mutation == "missing":
                    file.unlink()
                else:
                    file.write_text(file.read_text() + "\n// arbitrary performance-affecting edit\n")
                    import hashlib
                    value = hashlib.sha256(file.read_bytes()).hexdigest()
                    self.data["custody.json"]["source_files"][file.name] = value
                    self.data["workers.json"]["without-0019"]["source"]["src/libprojectM/MilkdropPreset/VideoEcho.cpp"] = value
                    self.recustody("workers.json")
                self.reject(root)

class VisualCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = {name: json.loads((ROOT / name).read_text()) for name in
                    ("workers.json", "inputs.json", "visual-jobs.json", "visual-workers.json", "visual-results.json", "observer-replay.json",
                     "historical-observer/visual-jobs.json", "historical-observer/visual-results.json", "custody.json")}

    def setUp(self):
        self.data = copy.deepcopy(self.base)
        self.name = "classic-with-0019-0"

    def check(self):
        return verify_visual(ROOT, self.data["workers.json"], self.data["inputs.json"],
                             self.data["visual-jobs.json"], self.data["visual-workers.json"],
                             self.data["visual-results.json"], self.data["observer-replay.json"],
                             historical_jobs=self.data["historical-observer/visual-jobs.json"],
                             historical_results=self.data["historical-observer/visual-results.json"],
                             history_anchor=self.data["custody.json"]["historical_observer"])

    def reject(self):
        with self.assertRaises((AssertionError, KeyError)):
            self.check()

    def test_valid_independent_selected_frame_receipts(self):
        self.assertEqual(self.check(), 24)

    def change_current_rgb_and_summary(self):
        for role in ("with-0019", "without-0019"):
            for repeat in (0, 1):
                self.data["visual-jobs.json"][f"classic-{role}-{repeat}"]["frame_sha256"][0] = "0" * 64
                self.data["visual-results.json"]["classic"][role]["hashes"][repeat][0] = "0" * 64

    def test_false_historical_preservation_flag(self):
        self.data["observer-replay.json"]["selected_hashes_equal_historical"] = False
        self.reject()

    def test_correlated_current_rgb_and_summary_edit(self):
        self.change_current_rgb_and_summary()
        self.reject()

    def test_changed_historical_receipt(self):
        self.data["historical-observer/visual-jobs.json"][self.name]["selected_pngs"]["frame-119.png"] = "0" * 64
        self.reject()

    def test_coordinated_current_history_and_anchor_edit(self):
        self.change_current_rgb_and_summary()
        for role in ("with-0019", "without-0019"):
            for repeat in (0, 1):
                self.data["historical-observer/visual-results.json"]["classic"][role]["hashes"][repeat][0] = "0" * 64
        self.data["custody.json"]["historical_observer"]["visual-results.json_sha256"] = digest(self.data["historical-observer/visual-results.json"])
        self.reject()

    def test_missing_visual_job(self):
        del self.data["visual-jobs.json"][self.name]
        self.reject()

    def test_wrong_role_and_coherent_identity(self):
        record = self.data["visual-jobs.json"][self.name]
        identity = copy.deepcopy(self.data["visual-jobs.json"]["classic-without-0019-0"]["job"]["identity"])
        record["job"]["identity"] = identity
        record["manifest"]["identity"] = identity
        record["observer_worker_sha256"] = identity["observer_worker_sha256"]
        record["linked_engine_library_sha256"] = identity["engine_library_sha256"]
        self.reject()

    def test_wrong_visual_profile(self):
        record = self.data["visual-jobs.json"][self.name]
        record["job"]["config"]["feedback_detail"] = 0.0
        record["manifest"]["config"]["feedback_detail"] = 0.0
        self.reject()

    def test_caller_framebuffer_buffer_and_pack_restoration(self):
        for field in ("read_framebuffer", "read_buffer", "pack_alignment"):
            with self.subTest(field=field):
                self.data = copy.deepcopy(self.base)
                self.data["visual-jobs.json"][self.name]["manifest"]["readback_states"][1]["after_" + field] = -1
                self.reject()

    def test_wrong_state_frame_or_capture_target(self):
        for mutation in ("frame", "target"):
            with self.subTest(mutation=mutation):
                self.data = copy.deepcopy(self.base)
                state = self.data["visual-jobs.json"][self.name]["manifest"]["readback_states"][1]
                if mutation == "frame": state["frame"] = 120
                else: state["capture_framebuffer"] = state["before_read_framebuffer"]
                self.reject()

    def test_observed_input_snapshots(self):
        for snapshot in ("inputs_before", "inputs_after"):
            with self.subTest(snapshot=snapshot):
                self.data = copy.deepcopy(self.base)
                self.data["visual-jobs.json"][self.name][snapshot]["pcm_sha256"] = "0" * 64
                self.reject()

    def test_changed_second_visual_repeat(self):
        self.data["visual-jobs.json"]["classic-with-0019-1"]["frame_sha256"][0] = "0" * 64
        self.reject()

    def test_changed_summary_despite_matching_job_hashes(self):
        self.data["visual-results.json"]["classic"]["with-0019"]["hashes"][0][0] = "0" * 64
        self.reject()

    def test_changed_difference_statistic(self):
        self.data["visual-results.json"]["classic"]["frame_differences"]["119"]["mae"] = 0.1
        self.reject()

    def test_changed_visual_worker_or_engine_library(self):
        for field in ("observer_worker_sha256", "engine_library_sha256"):
            with self.subTest(field=field):
                self.data = copy.deepcopy(self.base)
                self.data["visual-workers.json"]["with-0019"][field] = "0" * 64
                self.reject()

    def test_missing_selected_png_and_worker_role(self):
        for mutation in ("png", "worker"):
            with self.subTest(mutation=mutation):
                self.data = copy.deepcopy(self.base)
                if mutation == "png": self.data["visual-jobs.json"][self.name]["selected_pngs"] = {}
                else: del self.data["visual-workers.json"]["with-0019"]
                self.reject()

class DerivedRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schedule = json.loads((ROOT / "schedule.json").read_text())
        cls.summary = json.loads((ROOT / "job-summary.json").read_text())
        with gzip.open(ROOT / "timed-runs.json.gz", "rt") as stream:
            cls.runs = json.load(stream)

    def test_complete_ordered_original_job_summary(self):
        verify_job_summary(self.schedule, self.runs, self.summary)

    def test_per_job_mean(self):
        for field in ("submit_ms", "complete_ms"):
            with self.subTest(field=field):
                summary = copy.deepcopy(self.summary)
                summary[0][field] += 0.1
                with self.assertRaises(AssertionError):
                    verify_job_summary(self.schedule, self.runs, summary)

    def test_per_job_identity(self):
        for field, value in (("role", "with-0019"), ("name", "another-job"), ("preset", "inactive-gamma2.milk"), ("block", 9)):
            with self.subTest(field=field):
                summary = copy.deepcopy(self.summary)
                summary[0][field] = value
                with self.assertRaises(AssertionError):
                    verify_job_summary(self.schedule, self.runs, summary)

    def test_correlated_whole_record_order_swap(self):
        summary = copy.deepcopy(self.summary)
        summary[0], summary[1] = summary[1], summary[0]
        with self.assertRaises(AssertionError):
            verify_job_summary(self.schedule, self.runs, summary)

    def test_missing_or_duplicate_job(self):
        for summary in (self.summary[:-1], [self.summary[0], *self.summary[:-1]]):
            with self.assertRaises(AssertionError):
                verify_job_summary(self.schedule, self.runs, summary)

    def test_gamma_sets_and_timer_flag(self):
        for field, value in (("gamma", [2.0]), ("gamma_draws", [2]), ("gamma_invocations", [0]), ("gpu_timer_valid", False)):
            with self.subTest(field=field):
                summary = copy.deepcopy(self.summary)
                summary[0][field] = value
                with self.assertRaises(AssertionError):
                    verify_job_summary(self.schedule, self.runs, summary)

    def test_float32_pass_and_8bit_calculation(self):
        purpose = json.loads((ROOT / "source-purpose.json").read_text())
        calculated = gamma_source_calculation((ROOT / "original.milk").read_text(),
                      (ROOT / "source-proof/without-0019.cpp").read_text(),
                      (ROOT / "source-proof/with-0019.cpp").read_text())
        self.assertEqual(calculated, {key: purpose[key] for key in calculated})
        self.assertEqual(calculated["passes_upstream_epsilon"], 3)
        self.assertEqual(calculated["passes_milkdrop_epsilon"], 2)
        self.assertEqual(calculated["milkdrop_white_channel_for_extra_pass"], 0)

    def test_calculation_depends_on_fixture_and_source(self):
        before = (ROOT / "source-proof/without-0019.cpp").read_text()
        after = (ROOT / "source-proof/with-0019.cpp").read_text()
        inactive = gamma_source_calculation((ROOT / "inactive-gamma2.milk").read_text(), before, after)
        self.assertEqual(inactive["loaded_float_gamma"], 2.0)
        self.assertEqual(inactive["passes_upstream_epsilon"], inactive["passes_milkdrop_epsilon"])
        changed_source = gamma_source_calculation((ROOT / "original.milk").read_text(), after, after)
        self.assertEqual(changed_source["passes_upstream_epsilon"], changed_source["passes_milkdrop_epsilon"])

if __name__ == "__main__":
    unittest.main()
