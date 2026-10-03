"""Exercise version allocation and its GitHub Actions interface without dependencies."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "release_version.py"


def load_helper():
    spec = importlib.util.spec_from_file_location("release_version", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseCliTests(unittest.TestCase):
    def test_existing_old_line_release_can_be_retried_after_a_new_minor(self):
        helper = load_helper()
        result = helper.allocate_version(
            "2.1.5", 37, {"v2.1.7": "old", "v2.2.0": "new"}, "old",
            "workflow_dispatch", "refs/heads/main", 42, ordinal=3)
        self.assertEqual(result["version"], "2.1.7")
        self.assertEqual(result["version_code"], 39)
        self.assertTrue(result["reused_tag"])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.commit_count = 0
        self.git("init", "--quiet")
        self.git("config", "user.name", "Release test")
        self.git("config", "user.email", "release@example.invalid")
        (self.repo / "app").mkdir()
        (self.repo / "app/build.gradle").write_text(
            'versionName "2.1.4"\nversionCode 36\n', encoding="utf-8")
        self.baseline = self.commit()
        self.write_base()
        self.commit()

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.repo), *args], check=True,
            capture_output=True, text=True,
        ).stdout.strip()

    def write_base(self, version="2.1.5", code=37):
        (self.repo / "app/build.gradle").write_text(
            f'def baseVersionName = "{version}"\ndef baseVersionCode = {code}\n'
            f'def baseVersionCommit = "{self.baseline}"\n',
            encoding="utf-8",
        )

    def commit(self):
        self.commit_count += 1
        self.git("add", ".")
        self.git("commit", "--quiet", "--allow-empty", "-m", f"Fixture {self.commit_count}")
        return self.git("rev-parse", "HEAD")

    def run_cli(self, event="push", ref="refs/heads/main", sha=None):
        output = self.repo / "github-output"
        env = self.repo / "github-env"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(self.repo),
             "--sha", sha or self.git("rev-parse", "HEAD"), "--event", event,
             "--ref", ref, "--run-number", "42", "--output", str(output),
             "--env", str(env)], capture_output=True, text=True,
        )
        return result, output, env

    def test_main_build_allocates_next_installable_version_and_actions_files(self):
        self.git("tag", "v2.1.5")
        self.commit()
        result, output, env = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["version_code"], 38)
        self.assertEqual(output.read_text(),
                         "version=2.1.6\nversion_code=38\ntag=v2.1.6\n"
                         "release=true\nprevious_tag=v2.1.5\n")
        self.assertEqual(env.read_text(),
                         "PROJECTM_RELEASE_VERSION=2.1.6\n"
                         "PROJECTM_RELEASE_VERSION_CODE=38\nVERSION_SUFFIX=\n")

    def test_annotated_tag_is_reused_on_rerun_and_excluded_from_previous_tag(self):
        self.git("tag", "v2.1.5")
        self.commit()
        self.git("tag", "-a", "v2.1.6", "-m", "Stable")
        result, output, _ = self.run_cli(event="workflow_dispatch")
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads(result.stdout)
        self.assertEqual(metadata["version"], "2.1.6")
        self.assertEqual(metadata["version_code"], 38)
        self.assertEqual(metadata["previous_tag"], "v2.1.5")
        self.assertIn("release=true\n", output.read_text())

    def test_old_tag_retry_survives_a_later_minor_release(self):
        old = self.git("rev-parse", "HEAD")
        self.git("tag", "v2.1.5")
        self.baseline = old
        self.write_base(version="2.2.0", code=38)
        self.commit()
        self.git("tag", "v2.2.0")
        self.git("checkout", "--quiet", old)
        result, _, _ = self.run_cli(event="workflow_dispatch")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["version"], "2.1.5")
        self.assertEqual(json.loads(result.stdout)["version_code"], 37)

    def test_branch_build_emits_ci_suffix_and_never_publishes(self):
        result, output, env = self.run_cli(ref="refs/heads/topic")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("release=false\n", output.read_text())
        self.assertIn("VERSION_SUFFIX=-ci.42\n", env.read_text())
        self.assertEqual(json.loads(result.stdout)["version"], "2.1.5")

    def test_feature_fixup_commits_do_not_advance_ci_android_code(self):
        self.git("tag", "v2.1.4", self.baseline)
        self.commit()
        self.commit()
        for event, ref in [("push", "refs/heads/topic"),
                           ("pull_request", "refs/pull/9/merge")]:
            with self.subTest(event=event):
                result, _, _ = self.run_cli(event=event, ref=ref)
                self.assertEqual(result.returncode, 0, result.stderr)
                metadata = json.loads(result.stdout)
                self.assertEqual(metadata["version"], "2.1.5")
                self.assertEqual(metadata["version_code"], 37)
                self.assertIsNone(metadata["ordinal"])
                self.assertFalse(metadata["release"])
        result, _, _ = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["version"], "2.1.7")

    def test_bad_floor_fails_without_writing_actions_files(self):
        self.write_base(code=0)
        result, output, env = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())
        self.assertFalse(env.exists())

    def test_invalid_sha_fails_without_writing_actions_files(self):
        result, output, env = self.run_cli(sha="--help")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())
        self.assertFalse(env.exists())

    def test_legacy_tag_code_must_be_exceeded_after_minor_change(self):
        (self.repo / "app/build.gradle").write_text(
            'android {\n defaultConfig {\n versionName "2.1.4"\n'
            ' versionCode 36\n }\n}\n', encoding="utf-8")
        self.baseline = self.commit()
        self.git("tag", "v2.1.4")
        self.write_base(version="2.2.0", code=36)
        self.commit()
        result, output, env = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("versionCode", result.stderr)
        self.assertFalse(output.exists())
        self.assertFalse(env.exists())

    def test_legacy_release_migrates_to_next_installable_floor(self):
        (self.repo / "app/build.gradle").write_text(
            'versionName "2.1.4"\nversionCode 36\n', encoding="utf-8")
        self.baseline = self.commit()
        self.git("tag", "v2.1.4")
        self.write_base()
        self.commit()
        result, _, _ = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads(result.stdout)
        self.assertEqual(metadata["version"], "2.1.5")
        self.assertEqual(metadata["version_code"], 37)

    def test_rerun_rejects_changed_code_floor(self):
        self.git("tag", "v2.1.5")
        self.write_base(code=38)
        result, output, env = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("existing tag", result.stderr)
        self.assertFalse(output.exists())
        self.assertFalse(env.exists())

    def test_unreadable_stable_tag_version_code_fails_explicitly(self):
        (self.repo / "app/build.gradle").write_text("// no version code\n")
        self.baseline = self.commit()
        self.git("tag", "v2.1.4")
        self.write_base()
        self.commit()
        result, output, _ = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("v2.1.4", result.stderr)
        self.assertFalse(output.exists())

    def test_newer_release_first_does_not_change_older_commit_version(self):
        self.git("tag", "v2.1.4", self.baseline)
        older = self.git("rev-parse", "HEAD")
        self.commit()
        self.git("tag", "v2.1.6")
        result, _, _ = self.run_cli(sha=older)
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads(result.stdout)
        self.assertEqual(metadata["version"], "2.1.5")
        self.assertEqual(metadata["version_code"], 37)
        self.assertEqual(metadata["previous_tag"], "v2.1.4")

    def test_first_parent_ordinal_counts_merges_without_feature_commits(self):
        main = self.git("branch", "--show-current")
        self.git("tag", "v2.1.5")
        self.git("checkout", "-q", "-b", "topic")
        self.commit()
        self.commit()
        self.git("checkout", "-q", main)
        self.git("merge", "--no-ff", "-m", "Merge topic", "topic")
        result, _, _ = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads(result.stdout)
        self.assertEqual(metadata["version"], "2.1.6")
        self.assertEqual(metadata["version_code"], 38)

    def test_previous_tag_excludes_higher_unreachable_branch_tag(self):
        main = self.git("branch", "--show-current")
        self.git("tag", "v2.1.5")
        self.git("checkout", "-q", "-b", "unrelated")
        self.commit()
        self.git("tag", "v2.1.7")
        self.git("checkout", "-q", main)
        self.commit()
        result, _, _ = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads(result.stdout)
        self.assertEqual(metadata["version"], "2.1.6")
        self.assertEqual(metadata["previous_tag"], "v2.1.5")

    def test_rejects_anchor_outside_first_parent_history(self):
        main = self.git("branch", "--show-current")
        self.git("checkout", "-q", "-b", "topic")
        self.baseline = self.commit()
        self.git("checkout", "-q", main)
        self.git("merge", "--no-ff", "-m", "Merge topic", "topic")
        self.write_base()
        result, output, env = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("first-parent", result.stderr)
        self.assertFalse(output.exists())
        self.assertFalse(env.exists())

    def test_rejects_missing_invalid_and_current_commit_anchor(self):
        for anchor in [None, "not-a-sha", "0" * 40, self.git("rev-parse", "HEAD")]:
            self.write_base()
            path = self.repo / "app/build.gradle"
            text = path.read_text()
            declaration = f'def baseVersionCommit = "{self.baseline}"\n'
            replacement = "" if anchor is None else f'def baseVersionCommit = "{anchor}"\n'
            path.write_text(text.replace(declaration, replacement))
            with self.subTest(anchor=anchor):
                result, output, env = self.run_cli()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())
                self.assertFalse(env.exists())

    def test_rejects_candidate_tag_collision_on_another_commit(self):
        older = self.git("rev-parse", "HEAD")
        self.commit()
        self.git("tag", "v2.1.5")
        result, output, env = self.run_cli(sha=older)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("different commit", result.stderr)
        self.assertFalse(output.exists())
        self.assertFalse(env.exists())

    def prepare_older_feature(self, merge_main=False):
        main = self.git("branch", "--show-current")
        main_tip = self.git("rev-parse", "HEAD")
        self.git("tag", "v2.1.5")
        self.git("checkout", "-q", "-b", "older-feature", self.baseline)
        self.baseline = main_tip
        self.write_base()
        self.commit()
        if merge_main:
            self.git("merge", "--no-ff", "-s", "ours", "-m", "Merge main into feature", main)

    def test_older_feature_without_baseline_gets_ci_candidate(self):
        self.prepare_older_feature()
        result, output, env = self.run_cli(ref="refs/heads/older-feature")
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads(result.stdout)
        self.assertEqual(metadata["version"], "2.1.6")
        self.assertEqual(metadata["version_code"], 38)
        self.assertFalse(metadata["release"])
        self.assertIsNone(metadata["ordinal"])
        self.assertIn("release=false\n", output.read_text())
        self.assertIn("VERSION_SUFFIX=-ci.42\n", env.read_text())

    def test_feature_with_baseline_only_on_second_parent_gets_ci_candidate(self):
        self.prepare_older_feature(merge_main=True)
        result, output, env = self.run_cli(event="pull_request", ref="refs/pull/9/merge")
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads(result.stdout)
        self.assertEqual(metadata["version"], "2.1.6")
        self.assertFalse(metadata["release"])
        self.assertIsNone(metadata["ordinal"])
        self.assertIn("release=false\n", output.read_text())
        self.assertIn("VERSION_SUFFIX=-ci.42\n", env.read_text())

    def test_main_still_rejects_absent_baseline_for_older_source(self):
        self.prepare_older_feature()
        result, output, env = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("first-parent", result.stderr)
        self.assertFalse(output.exists())
        self.assertFalse(env.exists())

    def test_fallback_ci_candidate_checks_unreachable_latest_android_code(self):
        main = self.git("branch", "--show-current")
        self.prepare_older_feature()
        self.git("checkout", "-q", main)
        (self.repo / "app/build.gradle").write_text(
            'versionName "2.1.5"\nversionCode 99\n', encoding="utf-8")
        self.commit()
        self.git("tag", "-f", "v2.1.5")
        self.git("checkout", "-q", "older-feature")
        result, output, env = self.run_cli(ref="refs/heads/older-feature")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("versionCode", result.stderr)
        self.assertFalse(output.exists())
        self.assertFalse(env.exists())


class AllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helper = load_helper()

    def allocate(self, base="2.1.5", code=37, tags=None, sha="current",
                 event="push", ref="refs/heads/main", run_number=42):
        return self.helper.allocate_version(base, code, tags or {}, sha,
                                            event, ref, run_number)

    def test_no_tags_uses_base_floor(self):
        metadata = self.allocate()
        self.assertEqual(metadata["version"], "2.1.5")
        self.assertEqual(metadata["version_code"], 37)
        self.assertEqual(metadata["previous_tag"], "")

    def test_tags_are_ordered_numerically_and_prereleases_are_ignored(self):
        metadata = self.allocate(tags={"v2.1.9": "old", "v2.1.10": "new",
                                       "v2.1.99-rc.1": "prerelease", "other": "x"})
        self.assertEqual(metadata["version"], "2.1.11")
        self.assertEqual(metadata["version_code"], 43)
        self.assertEqual(metadata["previous_tag"], "v2.1.10")

    def test_base_patch_can_raise_next_version_floor(self):
        metadata = self.allocate(base="2.1.20", code=52, tags={"v2.1.10": "old"})
        self.assertEqual(metadata["version"], "2.1.20")
        self.assertEqual(metadata["version_code"], 52)

    def test_new_minor_uses_base_floor_and_previous_stable_line(self):
        metadata = self.allocate(base="2.2.0", code=43, tags={"v2.1.10": "old"})
        self.assertEqual(metadata["version"], "2.2.0")
        self.assertEqual(metadata["version_code"], 43)
        self.assertEqual(metadata["previous_tag"], "v2.1.10")

    def test_reusing_older_commit_does_not_allocate_again(self):
        metadata = self.allocate(tags={"v2.1.6": "current", "v2.1.7": "later",
                                       "v2.1.5": "old"})
        self.assertEqual(metadata["version"], "2.1.6")
        self.assertEqual(metadata["version_code"], 38)
        self.assertEqual(metadata["previous_tag"], "v2.1.5")

    def test_only_main_push_and_main_manual_run_are_release_candidates(self):
        for event, ref, release in [
            ("push", "refs/heads/main", True),
            ("workflow_dispatch", "refs/heads/main", True),
            ("pull_request", "refs/heads/main", False),
            ("pull_request", "refs/pull/12/merge", False),
            ("push", "refs/heads/topic", False),
            ("workflow_dispatch", "refs/heads/topic", False),
        ]:
            with self.subTest(event=event, ref=ref):
                self.assertEqual(self.allocate(event=event, ref=ref)["release"], release)

    def test_rejects_base_line_older_than_latest_stable(self):
        for tag in ["v2.2.0", "v3.0.0"]:
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                self.allocate(tags={tag: "old"})

    def test_rejects_same_commit_tag_inconsistent_with_base(self):
        for tag in ["v2.1.4", "v2.0.9", "v2.2.0"]:
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                self.allocate(tags={tag: "current"})

    def test_rejects_ambiguous_same_commit_stable_tags(self):
        with self.assertRaises(ValueError):
            self.allocate(tags={"v2.1.5": "current", "v2.1.6": "current"})

    def test_rejects_invalid_versions_codes_and_run_numbers(self):
        for base in ["2.1", "v2.1.5", "2.1.5-rc.1", "2.01.5", "2.1.-1",
                     "2.1.5\nrelease=true"]:
            with self.subTest(base=base), self.assertRaises(ValueError):
                self.allocate(base=base)
        for code in [0, -1, 2100000001, True, "37"]:
            with self.subTest(code=code), self.assertRaises(ValueError):
                self.allocate(code=code)
        for run in [0, -1, True, "42"]:
            with self.subTest(run=run), self.assertRaises(ValueError):
                self.allocate(run_number=run)

    def test_rejects_allocated_android_code_above_limit(self):
        with self.assertRaises(ValueError):
            self.allocate(code=2100000000, tags={"v2.1.5": "old"})

    def test_android_code_limit_is_allowed_at_floor(self):
        self.assertEqual(self.allocate(code=2100000000)["version_code"], 2100000000)

    def test_parses_multiline_version_floor_declarations(self):
        self.assertEqual(self.helper.parse_base_versions(
            'def baseVersionName =\n  "2.1.5" // floor\n'
            'def baseVersionCode =\n  37\n'), ("2.1.5", 37))

    def test_rejects_missing_duplicate_or_nonliteral_floor_declarations(self):
        for content in [
            'versionName "2.1.5"\nversionCode 37\n',
            'def baseVersionName = "2.1.5" + "bad"\ndef baseVersionCode = 37\n',
            'def baseVersionName = "2.1.5\'\ndef baseVersionCode = 37\n',
            'def baseVersionName = "2.1.5"\ndef baseVersionCode = -1\n',
            'def baseVersionName = "2.1.5"\ndef baseVersionCode = 0\n',
            'def baseVersionName = "2.1.5"\ndef baseVersionCode = 37\n'
            'def baseVersionCode = 38\n',
        ]:
            with self.subTest(content=content), self.assertRaises(ValueError):
                self.helper.parse_base_versions(content)

    def test_historical_code_uses_legacy_constants_or_tag_patch_offset(self):
        fixtures = [
            ('versionName "2.1.4" + (System.getenv("VERSION_SUFFIX") ?: "")\n'
             'versionCode 36\n', "v2.1.4", 36),
            ('def baseVersionName = "2.1.5"\ndef baseVersionCode = 37\n',
             "v2.1.8", 40),
        ]
        for content, tag, code in fixtures:
            with self.subTest(tag=tag):
                self.assertEqual(self.helper.version_code_at_tag(content, tag), code)

    def test_historical_code_rejects_missing_or_inconsistent_values(self):
        for content in [
            'versionName "2.1.3"\nversionCode 36\n',
            'versionName "2.1.4"\nversionCode 0\n',
            'versionName "2.1.4"\nversionCode codeFromElsewhere\n',
            'def baseVersionName = "2.2.0"\ndef baseVersionCode = 37\n',
            'def baseVersionName = "2.1.5"\ndef baseVersionCode = 37\n',
        ]:
            with self.subTest(content=content), self.assertRaises(ValueError):
                self.helper.version_code_at_tag(content, "v2.1.4")


if __name__ == "__main__":
    unittest.main()
