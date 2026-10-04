"""Exercise diagnostics option validation without a TV, APK build or network."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().with_name("tv-diagnostics.sh")
PACKAGE = "nl.neerdael.projectmtv"
PROFILE = PACKAGE + ".profile"


class DiagnosticsTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        tools = self.root / "tools"
        tools.mkdir()
        self.script = tools / SCRIPT.name
        shutil.copyfile(SCRIPT, self.script)
        self.calls = self.root / "adb-calls.txt"
        self.output = self.root / "diagnostics"
        binary = self.root / "bin"
        binary.mkdir()
        # An unreachable fake device ends accepted runs at connect(), before installation.
        adb = binary / "adb"
        adb.write_text(
            '#!/bin/sh\n'
            'printf "%s\\n" "$*" >> "$DIAGNOSTICS_TEST_CALLS"\n'
            'echo offline\n'
        )
        adb.chmod(0o755)
        sleep = binary / "sleep"
        sleep.write_text("#!/bin/sh\nexit 0\n")
        sleep.chmod(0o755)
        self.environment = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ["PATH"],
                                DIAGNOSTICS_TEST_CALLS=str(self.calls))

    def run_script(self, options):
        return subprocess.run(
            ["/bin/bash", str(self.script), "test-tv:5555", "--out", str(self.output), *options],
            cwd=self.root, env=self.environment, capture_output=True, text=True, timeout=20,
        )


class PackageModeTests(DiagnosticsTestCase):
    def test_alternate_package_is_rejected_before_device_access(self):
        cases = [
            ["--package", PROFILE],
            ["--release", "--package", PROFILE],
            ["--package", PROFILE, "--release"],
            ["--apk", "profile.apk", "--package", PROFILE, "--release"],
            ["--no-install", "--package", PROFILE, "--release"],
            ["--package", PACKAGE, "--package", PROFILE],
        ]
        for options in cases:
            with self.subTest(options=options):
                result = self.run_script(options)
                self.assertEqual(result.returncode, 1)
                self.assertIn("--package", result.stdout)
                self.assertIn(PROFILE, result.stdout)
                self.assertIn("--apk", result.stdout)
                self.assertIn("--no-install", result.stdout)
                self.assertFalse(self.calls.exists(), result.stdout)
                self.assertFalse(self.output.exists())

    def test_supported_modes_reach_connection_using_final_options(self):
        cases = [
            [],
            ["--package", PACKAGE],
            ["--release", "--package", PACKAGE],
            ["--package", PROFILE, "--no-install"],
            ["--no-install", "--package", PROFILE],
            ["--package", PROFILE, "--apk", "profile.apk"],
            ["--apk", "profile.apk", "--package", PROFILE],
            ["--release", "--package", PROFILE, "--no-install"],
            ["--release", "--package", PROFILE, "--apk", "profile.apk"],
            ["--package", PROFILE, "--package", PACKAGE],
        ]
        for options in cases:
            with self.subTest(options=options):
                result = self.run_script(options)
                self.assertEqual(result.returncode, 1)
                self.assertIn("could not connect to test-tv:5555", result.stdout)
                self.assertIn("connect test-tv:5555", self.calls.read_text().splitlines())
                self.assertFalse(self.output.exists())
                self.calls.unlink()


class AndroidUserTests(DiagnosticsTestCase):
    def setUp(self):
        super().setUp()
        self.state = self.root / "device-state.json"
        self.state.write_text(json.dumps({"pid": 101, "starts": 0, "listener": True}))
        self.environment["DIAGNOSTICS_TEST_STATE"] = str(self.state)
        fake = Path(__file__).with_name("tv_diagnostics_fake_adb.py")
        adb = self.root / "bin" / "adb"
        adb.write_text(f"#!{sys.executable}\n" + fake.read_text())
        adb.chmod(0o755)

    def run_diagnostics(self, failure="", launch_state="COLD"):
        self.environment["DIAGNOSTICS_TEST_FAILURE"] = failure
        self.environment["DIAGNOSTICS_TEST_LAUNCH_STATE"] = launch_state
        return self.run_script(["--no-install", "--duration", "30"])

    def adb_calls(self):
        return [json.loads(line) for line in self.calls.read_text().splitlines()]

    def test_secondary_user_process_is_measured_without_other_user_process(self):
        for launch_state in ("", "COLD"):  # Android 9 has no LaunchState line; Android 14 does.
            with self.subTest(launch_state=launch_state):
                result = self.run_diagnostics(launch_state=launch_state)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                summary = (self.output / "summary.md").read_text()
                self.assertIn("cold start: new process 309 for the activity", summary)
                self.assertIn("App process ids during the run: 410 ", summary)
                calls = self.adb_calls()
                self.assertEqual(calls.count(["shell", "am", "get-current-user"]), 1)
                for call in calls:
                    if call[:3] == ["shell", "am", "force-stop"]:
                        self.assertEqual(call, ["shell", "am", "force-stop", "--user", "10", PACKAGE])
                    if call[:3] == ["shell", "am", "start"]:
                        self.assertIn("--user", call)
                        self.assertEqual(call[call.index("--user") + 1], "10")
                    if call[:3] == ["shell", "cmd", "notification"]:
                        self.assertEqual(call[-1], "10")
                    if call[:2] == ["shell", "settings"]:
                        self.assertEqual(call[2:4], ["--user", "10"])
                    self.assertNotEqual(call[:2], ["shell", "pidof"])
                self.assertTrue(json.loads(self.state.read_text())["listener"])
                shutil.rmtree(self.output)
                self.calls.unlink()
                self.state.write_text(json.dumps({"pid": 101, "starts": 0, "listener": True}))

    def test_invalid_user_or_process_lookup_stops_before_app_mutation(self):
        for failure in ("user-error", "user-malformed", "user-empty", "user-whitespace", "user-negative",
                        "ps-error", "ps-malformed", "ps-empty", "ps-bad-row", "ps-ambiguous"):
            with self.subTest(failure=failure):
                result = self.run_diagnostics(failure)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("ERROR:", result.stdout)
                self.assertFalse(any(call[:3] in (["shell", "am", "force-stop"],
                                                  ["shell", "pm", "grant"],
                                                  ["shell", "cmd", "notification"])
                                     for call in self.adb_calls()))
                self.assertFalse((self.output / "summary.md").exists())
                self.calls.unlink()

    def test_process_lookup_failure_after_stop_restores_captured_user_listener(self):
        result = self.run_diagnostics("ps-after-stop")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("ERROR:", result.stdout)
        self.assertFalse((self.output / "summary.md").exists())
        self.assertTrue(json.loads(self.state.read_text())["listener"])
        restores = [call for call in self.adb_calls()
                    if call[:4] == ["shell", "cmd", "notification", "allow_listener"]]
        self.assertEqual(restores, [["shell", "cmd", "notification", "allow_listener",
                                    PACKAGE + "/com.example.projectm.visualizer.TrackListenerService", "10"]])


if __name__ == "__main__":
    unittest.main()
