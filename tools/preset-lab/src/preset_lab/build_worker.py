import os
import shutil
import subprocess
import tarfile
import tempfile
from dataclasses import asdict
from pathlib import Path

from .identity import canonical_json, digest, file_digest, load_json
from .models import EngineIdentity

NATIVE = Path(__file__).parent / "native"


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def _archive(source: Path, target: Path, temporary: Path) -> None:
    archive = temporary / "source.tar"
    subprocess.run(["git", "-C", str(source), "archive", "HEAD", "-o", str(archive)], check=True)
    target.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive) as stream:
        stream.extractall(target, filter="data")


def _replace(root: Path, relative: str, old: str, new: str, count: int = 1) -> None:
    path = root / relative
    text = path.read_text()
    if text.count(old) != count:
        raise ValueError(f"instrumentation does not match pinned source: {relative}")
    path.write_text(text.replace(old, new))


def _instrument(root: Path) -> None:
    library = root / "src/libprojectM"
    shutil.copyfile(NATIVE / "analysis_hooks.hpp", library / "analysis_hooks.hpp")
    paths = ["TimeKeeper.cpp", "TimeKeeper.hpp", "ProjectM.cpp", "Renderer/MilkdropNoise.cpp",
             "Renderer/TextureManager.cpp", "Renderer/TransitionShaderManager.cpp",
             "MilkdropPreset/PresetState.cpp", "MilkdropPreset/MilkdropShader.cpp"]
    for name in paths:
        file = library / name
        relative = os.path.relpath(library / "analysis_hooks.hpp", file.parent)
        file.write_text(f'#include "{relative}"\n' + file.read_text())
    _replace(library, "TimeKeeper.cpp",
             "auto currentTime = std::chrono::high_resolution_clock::now();\n\n    double currentFrameTime = std::chrono::duration<double>(currentTime - m_startTime).count();",
             "double currentFrameTime = lab::clock_seconds;")
    _replace(library, "TimeKeeper.hpp", "m_randomGenerator{m_randomDevice()}",
             "m_randomGenerator{lab::Seed(11)}")
    _replace(library, "ProjectM.cpp", "srand(time(nullptr));",
             "srand(lab::Seed(1));\n    lab::ResetShaderRandom();")
    _replace(library, "MilkdropPreset/MilkdropShader.cpp",
             "static auto floatRand = []() { return static_cast<float>(rand() % 7381) / 7380.0f; };",
             "static auto floatRand = []() { return static_cast<float>(lab::ShaderRandom() % 7381) / 7380.0f; };")
    _replace(library, "Renderer/MilkdropNoise.cpp",
             "static_cast<uint32_t>(std::chrono::system_clock::now().time_since_epoch().count())",
             "lab::Seed(101) ^ static_cast<uint32_t>(size * 31 + zoomFactor)", 2)
    _replace(library, "Renderer/TextureManager.cpp",
             "std::random_device rndDevice;\n    std::default_random_engine rndEngine(rndDevice());",
             "std::mt19937 rndEngine(lab::Seed(103) ^ lab::StringSeed(randomName));")
    _replace(library, "Renderer/TextureManager.cpp", "m_filesScanned = true;",
             "std::sort(m_scannedTextureFiles.begin(), m_scannedTextureFiles.end(),\n"
             "            [](const auto& a, const auto& b) {\n"
             "                return std::tie(a.lowerCaseBaseName, a.filePath) < std::tie(b.lowerCaseBaseName, b.filePath);\n"
             "            });\n        m_filesScanned = true;")
    texture = library / "Renderer/TextureManager.cpp"
    texture.write_text("#include <tuple>\n" + texture.read_text())
    _replace(library, "MilkdropPreset/PresetState.cpp",
             "std::random_device randomDevice;\n    std::mt19937 randomGenerator(randomDevice());",
             "std::mt19937 randomGenerator(lab::Seed(104));")
    _replace(library, "Renderer/TransitionShaderManager.cpp", "m_mersenneTwister(m_randomDevice())",
             "m_mersenneTwister(lab::Seed(105))")
    evaluator = root / "vendor/projectm-eval/projectm-eval/TreeFunctions.c"
    text = evaluator.read_text()
    # This pinned evaluator initializes its Mersenne Twister inline.
    old = "uint32_t s = 0x4141f00d; // Initial Mersenne Twister seed"
    if text.count(old) != 1:
        raise ValueError("evaluator seed initializer not found")
    text = text.replace(old, 'uint32_t s = getenv("PRESET_LAB_SEED") ? (uint32_t)strtoul(getenv("PRESET_LAB_SEED"), NULL, 10) : 0x4141f00d;')
    evaluator.write_text("#include <stdlib.h>\n" + text)


def prepare_engine(repo: Path, work: Path) -> tuple[Path, EngineIdentity]:
    repo, work = repo.resolve(), work.resolve()
    source = repo / "third_party/projectm"
    if not (source / "CMakeLists.txt").is_file():
        raise ValueError("projectM source missing: initialize repository submodules")
    patches = sorted((repo / "tools/projectm-patches").glob("*.patch"))
    commit = _git(source, "rev-parse", "HEAD")
    evaluator = source / "vendor/projectm-eval"
    expected = _git(source, "ls-tree", "HEAD", "vendor/projectm-eval").split()[2]
    if _git(evaluator, "rev-parse", "HEAD") != expected:
        raise ValueError("evaluator checkout differs from the engine's pinned submodule")
    code_identity = {"builder": file_digest(Path(__file__)),
                     "native": [(p.relative_to(NATIVE).as_posix(), file_digest(p))
                                for p in sorted(NATIVE.rglob("*")) if p.is_file()]}
    identity = EngineIdentity(commit, digest([(p.name, file_digest(p)) for p in patches]),
                              digest(code_identity))
    destination = work / "engines" / digest(asdict(identity))
    marker = destination / "preset-lab-identity.json"
    if marker.is_file() and load_json(marker) == asdict(identity):
        return destination, identity
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temporary_name:
        temporary = Path(temporary_name)
        staged = temporary / "engine"
        _archive(source, staged, temporary)
        _archive(evaluator, staged / "vendor/projectm-eval", temporary)
        # Do not let git apply inherit an enclosing repo's index/attributes.
        apply_env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(staged.parent))
        for patch in patches:
            subprocess.run(["git", "apply", str(patch)], cwd=staged, check=True,
                           capture_output=True, env=apply_env)
        _instrument(staged)
        (staged / marker.name).write_text(canonical_json(asdict(identity)))
        if destination.exists():
            raise ValueError(f"incomplete engine snapshot exists: {destination}")
        staged.rename(destination)
    return destination, identity


def build_worker(repo: Path, work: Path) -> Path:
    snapshot, identity = prepare_engine(repo, work)
    output = work.resolve() / "native-build" / digest(asdict(identity))
    executable = output / "preset-lab-worker"
    if executable.is_file():
        return executable
    output.mkdir(parents=True, exist_ok=True)
    with (output / "build.log").open("w") as log:
        subprocess.run(["cmake", "-S", str(NATIVE), "-B", str(output),
                        f"-DPROJECTM_SOURCE={snapshot}", "-DCMAKE_BUILD_TYPE=Release"],
                       check=True, stdout=log, stderr=subprocess.STDOUT)
        subprocess.run(["cmake", "--build", str(output), "-j", "4"], check=True,
                       stdout=log, stderr=subprocess.STDOUT)
    (output / "build-identity.json").write_text(canonical_json(asdict(identity)))
    return executable
