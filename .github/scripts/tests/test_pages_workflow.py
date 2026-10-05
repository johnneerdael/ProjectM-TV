"""Exercise the shared Pages deployment guard with real shell execution."""
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


WORKFLOWS = Path(__file__).resolve().parents[2] / "workflows"
HEAD = "a" * 40
NEW_HEAD = "b" * 40


class PagesDeploymentTests(unittest.TestCase):
    def freshness_script(self):
        source = WORKFLOWS / "pages-deploy.yml"
        self.assertTrue(source.exists(), "The shared Pages deployment workflow is missing")
        match = re.search(r"^      - name: Check deployment is still current main\n(.*?)(?=^      - |\Z)",
                          source.read_text(), re.M | re.S)
        self.assertIsNotNone(match, "The Pages freshness check is missing")
        block = match[1].split("        run: |\n", 1)[1]
        return "\n".join(line[10:] for line in block.splitlines() if line.startswith("          "))

    def run_guard(self, main_sha, fail=False):
        script = self.freshness_script()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gh = root / "gh"
            gh.write_text(f"#!{sys.executable}\n" + """
import os
import sys
if os.environ.get('FAIL_GH') == '1':
    sys.exit(1)
print(os.environ['MAIN_SHA'])
""")
            gh.chmod(0o755)
            output = root / "output"
            env = dict(os.environ, PATH=str(root) + os.pathsep + os.environ["PATH"],
                       GITHUB_SHA=HEAD, GITHUB_REPOSITORY="owner/repo", GITHUB_OUTPUT=str(output),
                       MAIN_SHA=main_sha, FAIL_GH="1" if fail else "0")
            result = subprocess.run(["bash", "-c", script], env=env, text=True, capture_output=True)
            return result, output.read_text() if output.exists() else ""

    def test_latest_main_revision_can_deploy(self):
        result, output = self.run_guard(HEAD)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output, "current=true\n")

    def test_older_manual_or_main_run_cannot_replace_newer_site(self):
        result, output = self.run_guard(NEW_HEAD)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output, "current=false\n")

    def test_failed_main_lookup_never_allows_deployment(self):
        result, output = self.run_guard(HEAD, fail=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("current=true", output)

    def test_manual_and_main_use_same_deployer_while_prs_only_build(self):
        main = (WORKFLOWS / "android.yml").read_text()
        manual = (WORKFLOWS / "docs.yml").read_text()
        reviewed_pr = (WORKFLOWS / "pr-builds.yml").read_text()
        self.assertIn("uses: ./.github/workflows/pages-deploy.yml", main)
        self.assertIn("uses: ./.github/workflows/pages-deploy.yml", manual)
        self.assertIn("uses: ./.github/workflows/docs-build.yml", reviewed_pr)
        self.assertNotIn("pages-deploy.yml", reviewed_pr)


if __name__ == "__main__":
    unittest.main()
