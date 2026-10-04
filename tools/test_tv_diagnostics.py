"""Exercise diagnostics option validation without a TV, APK build or network."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().with_name("tv-diagnostics.sh")
PACKAGE = "nl.neerdael.projectmtv"
PROFILE = PACKAGE + ".profile"


class PackageModeTests(unittest.TestCase):
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
            cwd=self.root, env=self.environment, capture_output=True, text=True, timeout=10,
        )

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


if __name__ == "__main__":
    unittest.main()
