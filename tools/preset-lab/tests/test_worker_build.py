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

def test_shader_random_is_private_resettable_and_preserves_mac_oracle(tmp_path):
    import os
    source = tmp_path / "shader_random.cpp"
    executable = tmp_path / "shader_random"
    source.write_text(r'''#include "analysis_hooks.hpp"
#include <array>
#include <cassert>
#include <cstdlib>
int main() {
    const std::array<uint32_t, 10> expected = {1069204390u, 2122508281u,
        1145818450u, 1284826501u, 1130931722u, 191692057u, 542931499u,
        391687590u, 1055947075u, 497630717u};
    lab::ResetShaderRandom();
    for (auto value : expected) assert(lab::ShaderRandom() == value);
    lab::ResetShaderRandom();
    for (auto value : expected) {
        // Simulate another linked dependency consuming the process-global RNG.
        for (int i = 0; i < 6; ++i) (void)rand();
        assert(lab::ShaderRandom() == value);
    }
#ifdef __APPLE__
    srand(lab::Seed(1));
    lab::ResetShaderRandom();
    for (int i = 0; i < 1000; ++i)
        assert(lab::ShaderRandom() == static_cast<uint32_t>(rand()));
#endif
    lab::shader_random_state = 0;
    assert(lab::ShaderRandom() == 520932930u);
}
''')
    result = subprocess.run(["c++", "-std=c++17", "-I", str(NATIVE), str(source),
                             "-o", str(executable)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    env = dict(os.environ, PRESET_LAB_SEED="12345")
    result = subprocess.run([str(executable)], env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
