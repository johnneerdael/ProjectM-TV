from pathlib import Path
import tempfile
import shutil
import subprocess

from preset_lab.build_worker import _instrument, prepare_engine
from preset_lab.build_worker import NATIVE
from preset_lab.identity import file_digest


def test_preparation_instruments_only_a_private_copy(tmp_path):
    repo = Path(__file__).parents[3]
    original = repo / "third_party/projectm/src/libprojectM/TimeKeeper.cpp"
    before = file_digest(original)
    snapshot, identity = prepare_engine(repo, tmp_path)
    assert snapshot != repo / "third_party/projectm"
    assert file_digest(original) == before
    instrumented_clock = file_digest(snapshot / "src/libprojectM/TimeKeeper.cpp")
    assert instrumented_clock != before
    assert "lab::clock_seconds" in (snapshot / "src/libprojectM/TimeKeeper.cpp").read_text()
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


def test_instrumentation_preserves_native_time_and_hooks_historical_snapshots(tmp_path):
    # Keep both clock implementations usable: old snapshots are comparison oracles.
    clock = ("auto currentTime = std::chrono::high_resolution_clock::now();\n\n"
             "    double currentFrameTime = std::chrono::duration<double>(currentTime - m_startTime).count();")
    files = {
        "TimeKeeper.cpp": clock,
        "TimeKeeper.hpp": "m_randomGenerator{m_randomDevice()}",
        "ProjectM.cpp": "srand(time(nullptr));",
        "Renderer/MilkdropNoise.cpp": "\n".join([
            "static_cast<uint32_t>(std::chrono::system_clock::now().time_since_epoch().count())"] * 2),
        "Renderer/TextureManager.cpp": ("std::random_device rndDevice;\n"
                                       "    std::default_random_engine rndEngine(rndDevice());\n"
                                       "m_filesScanned = true;"),
        "Renderer/TransitionShaderManager.cpp": "m_mersenneTwister(m_randomDevice())",
        "MilkdropPreset/PresetState.cpp": ("std::random_device randomDevice;\n"
                                          "    std::mt19937 randomGenerator(randomDevice());"),
        "MilkdropPreset/MilkdropShader.cpp": (
            "static auto floatRand = []() { return static_cast<float>(rand() % 7381) / 7380.0f; };"),
    }
    for native_time in (False, True):
        engine = tmp_path / ("current" if native_time else "historical")
        library = engine / "src/libprojectM"
        for relative, text in files.items():
            target = library / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if relative == "TimeKeeper.cpp" and native_time:
                text = ("double currentFrameTime{m_userSpecifiedTime};\n"
                        "if (m_userSpecifiedTime < 0.0) {\n"
                        "    auto currentTime = std::chrono::high_resolution_clock::now();\n"
                        "        currentFrameTime = std::chrono::duration<double>(currentTime - m_startTime).count();\n"
                        "}\n")
            target.write_text(text)
        (library / "ProjectM.hpp").write_text("void SetFrameTime(double seconds);" if native_time else "class ProjectM;")
        evaluator = engine / "vendor/projectm-eval/projectm-eval/TreeFunctions.c"
        evaluator.parent.mkdir(parents=True)
        evaluator.write_text("uint32_t s = 0x4141f00d; // Initial Mersenne Twister seed")
        _instrument(engine)
        if native_time:
            hooked = (library / "TimeKeeper.cpp").read_text()
            assert "currentFrameTime = lab::clock_seconds;" in hooked
            assert "double currentFrameTime{m_userSpecifiedTime};" in hooked
            assert "high_resolution_clock::now()" not in hooked
            assert (library / "ProjectM.cpp").read_text() == files["ProjectM.cpp"]
        else:
            assert "double currentFrameTime = lab::clock_seconds;" in (library / "TimeKeeper.cpp").read_text()
            assert "srand(lab::Seed(1));" in (library / "ProjectM.cpp").read_text()
            assert "lab::ResetShaderRandom();" in (library / "ProjectM.cpp").read_text()
        assert "lab::Seed(11)" in (library / "TimeKeeper.hpp").read_text()
        assert "lab::ShaderRandom()" in (library / "MilkdropPreset/MilkdropShader.cpp").read_text()


def test_constructor_and_preset_origin_use_frozen_clock_across_delayed_processes(tmp_path):
    repo = Path(__file__).parents[3]
    snapshot, _ = prepare_engine(repo, tmp_path / "snapshot")
    library = snapshot / "src/libprojectM"
    source = tmp_path / "clock_origin.cpp"
    executable = tmp_path / "clock_origin"
    source.write_text(r'''#include "TimeKeeper.hpp"
#include "analysis_hooks.hpp"
#include <chrono>
#include <iomanip>
#include <iostream>
#include <thread>
int main(int argc, char** argv) {
    lab::clock_seconds = 0;
    libprojectM::TimeKeeper keeper(30, 3, 1, 0);
    const double initializationTime = keeper.GetRunningTime();
    std::this_thread::sleep_for(std::chrono::milliseconds(std::stoi(argv[1])));
    keeper.StartPreset();
    lab::clock_seconds = 1.0 / 30;
    keeper.SetFrameTime(lab::clock_seconds);
    keeper.UpdateTimers();
    std::cout << std::setprecision(17) << initializationTime << " "
              << keeper.SecondsSinceLastFrame() << " " << keeper.PresetProgressA() << " "
              << keeper.PresetTimeA();
    lab::clock_seconds = 10;
    keeper.SetFrameTime(0.5);
    keeper.UpdateTimers();
    std::cout << " " << keeper.GetRunningTime();
    lab::clock_seconds = 2;
    keeper.SetFrameTime(-1);
    keeper.UpdateTimers();
    std::cout << " " << keeper.GetRunningTime() << "\n";
}
''')
    subprocess.run(["c++", "-std=c++17", "-I", str(library), str(source),
                    str(library / "TimeKeeper.cpp"), "-o", str(executable)], check=True)
    outputs = [subprocess.check_output([str(executable), str(delay)], text=True)
               for delay in (5, 40)]
    assert outputs[0] == outputs[1]
    values = [float(value) for value in outputs[0].split()]
    assert values[0] == 0
    assert values[1] == 1.0 / 30
    assert values[2] == (1.0 / 30) / 30
    assert values[3] == 0
    assert values[4] == 0.5
    assert values[5] == 2
