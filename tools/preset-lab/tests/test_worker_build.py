from pathlib import Path
import tempfile
import shutil
import subprocess

from preset_lab.build_worker import prepare_engine
from preset_lab.build_worker import NATIVE
from preset_lab.identity import file_digest


def test_preparation_instruments_only_a_private_copy(tmp_path):
    repo = Path(__file__).parents[3]
    original = repo / "third_party/projectm/src/libprojectM/TimeKeeper.cpp"
    before = file_digest(original)
    snapshot, identity = prepare_engine(repo, tmp_path)
    assert snapshot != repo / "third_party/projectm"
    assert file_digest(original) == before
    assert file_digest(snapshot / "src/libprojectM/TimeKeeper.cpp") != before
    assert (snapshot / "vendor/projectm-eval/projectm-eval/TreeFunctions.c").is_file()
    assert len(identity.commit) == 40
    assert len(identity.patches_sha256) == 64
    assert len(identity.instrumentation_sha256) == 64
    assert prepare_engine(repo, tmp_path) == (snapshot, identity)


def test_preparation_inside_another_git_worktree_applies_app_patches():
    repo = Path(__file__).parents[3]
    with tempfile.TemporaryDirectory(dir=repo / "build") as work:
        snapshot, _ = prepare_engine(repo, Path(work))
        header = (snapshot / "src/libprojectM/ProjectM.hpp").read_text()
        assert "void SetDirectOutput(bool enabled);" in header


def test_hook_can_be_force_included_and_present_in_private_source(tmp_path):
    copied = tmp_path / "analysis_hooks.hpp"
    shutil.copyfile(NATIVE / "analysis_hooks.hpp", copied)
    result = subprocess.run(["c++", "-std=c++17", "-fsyntax-only", "-include",
                             str(NATIVE / "analysis_hooks.hpp"), "-x", "c++", "-"],
                            input=f'#include "{copied}"\nint main() {{ return lab::Seed(1)==0; }}\n',
                            text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
