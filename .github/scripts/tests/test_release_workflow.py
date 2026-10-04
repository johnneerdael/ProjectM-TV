"""Exercise the workflow's real packaging scripts with tagged Gradle output files."""
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


WORKFLOW = Path(__file__).resolve().parents[2] / "workflows/android.yml"


def packaging_scripts(release):
    text = WORKFLOW.read_text().split("\n  apk:\n", 1)[1].split("\n  release:\n", 1)[0]
    for match in re.finditer(r"^      - name: ([^\n]+)\n(.*?)(?=^      - |\Z)", text, re.M | re.S):
        name, block = match.groups()
        if not (name.startswith("Build release APK") or name == "Name APK" or "core AAR" in name):
            continue
        run = re.search(r"^        run: (.+)$", block, re.M)
        if run is None:
            continue
        if run.group(1) == "|":
            body = block[run.end():].splitlines()
            script = "\n".join(line[10:] for line in body if line.startswith("          "))
        else:
            script = run.group(1)
        script = script.replace("${{ steps.version.outputs.release }}", "true" if release else "false")
        script = script.replace("${{ steps.version.outputs.version }}", "2.1.5")
        yield name, script


class ArtifactPackagingTests(unittest.TestCase):
    def test_native_core_is_saved_before_capped_build_overwrites_gradle_output(self):
        for release in (True, False):
            with self.subTest(release=release), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "gradlew").write_text(f"#!{sys.executable}\n" + """
import sys
from pathlib import Path
policy = next((a.split('=', 1)[1] for a in sys.argv if a.startswith('-PprojectmCoreRenderingPolicy=')), 'native')
core = Path('core/build/outputs/aar/core-release.aar')
core.parent.mkdir(parents=True, exist_ok=True)
core.write_bytes((policy + ' engine').encode())
if 'assembleRelease' in sys.argv:
    apk = Path('app/build/outputs/apk/release/app-release.apk')
    apk.parent.mkdir(parents=True, exist_ok=True)
    apk.write_bytes((policy + ' apk').encode())
    mapping = Path('app/build/outputs/mapping/release/mapping.txt')
    mapping.parent.mkdir(parents=True, exist_ok=True)
    mapping.write_text('native mapping')
""")
                (root / "gradlew").chmod(0o755)
                fake_bin = root / "bin"
                fake_bin.mkdir()
                (fake_bin / "git").write_text("#!/bin/sh\nprintf '%s\\n' abc1234\n")
                (fake_bin / "git").chmod(0o755)
                env = dict(os.environ, PATH=str(fake_bin) + os.pathsep + os.environ["PATH"],
                           GITHUB_OUTPUT=str(root / "outputs.txt"), GITHUB_RUN_NUMBER="42")
                for name, script in packaging_scripts(release):
                    subprocess.run(["bash", "-eu", "-c", script], cwd=root, env=env,
                                   check=True, capture_output=True, text=True)
                suffix = "" if release else "-ci.42-abc1234"
                capped = root / f"dist-aar/projectM-TV-core-2.1.5{suffix}.aar"
                native = root / f"dist-aar/projectM-TV-core-native-2.1.5{suffix}.aar"
                self.assertEqual(capped.read_bytes(), b"capped engine")
                self.assertEqual(native.read_bytes(), b"native engine")
                self.assertEqual((root / f"dist/projectM-TV-2.1.5{suffix}.apk").read_bytes(), b"native apk")
                self.assertEqual(len(list((root / "dist-aar").glob("*.aar"))), 2)


if __name__ == "__main__":
    unittest.main()
