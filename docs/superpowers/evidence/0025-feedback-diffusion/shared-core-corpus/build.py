"""Build an actual :core APK in private scratch; never instrument the live source."""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
WORK = ROOT / "build/follow-ups/core-corpus"
sys.path.insert(0, str(ROOT / "tools/preset-lab/src"))
from preset_lab.build_worker import _archive, _instrument


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def run(cmd, cwd=None, log=None):
    return subprocess.run(cmd, cwd=cwd, check=True, stdout=log,
                          stderr=subprocess.STDOUT if log else None)


def prepare(variant, commit):
    frozen_inputs = {name: (HERE / name).read_bytes() for name in ("build.py", "CorpusInstrumentation.java", "LabBridge.java", "lab_bridge.cpp")}
    harness_digest = digest({name: hashlib.sha256(data).hexdigest() for name, data in frozen_inputs.items()})
    destination = WORK / (variant + "-" + commit[:12] + "-" + harness_digest[:12])
    if destination.exists():
        raise ValueError(f"refuse to overwrite frozen build directory: {destination}")
    destination.mkdir(parents=True)
    frozen_harness = destination / "harness-source"
    frozen_harness.mkdir()
    for name, data in frozen_inputs.items():
        (frozen_harness / name).write_bytes(data)
    source = destination / "repo"
    source.mkdir()
    with tempfile.TemporaryDirectory(dir=destination) as temporary_name:
        temporary = Path(temporary_name)
        archive = temporary / "repo.tar"
        run(["git", "archive", commit, "core", "tools/projectm-patches", "build.gradle",
             "gradlew", "gradle", "gradle.properties", "-o", str(archive)], ROOT)
        with tarfile.open(archive) as stream:
            stream.extractall(source, filter="data")
        upstream_commit = subprocess.check_output(
            ["git", "ls-tree", commit, "third_party/projectm"], cwd=ROOT, text=True).split()[2]
        checkout = ROOT / "build/follow-ups/pristine-source/projectm"
        actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout, text=True).strip()
        if actual != upstream_commit:
            raise ValueError("pristine engine does not match variant pin")
        engine = source / "third_party/projectm"
        _archive(checkout, engine, temporary)
        _archive(checkout / "vendor/projectm-eval", engine / "vendor/projectm-eval", temporary)
    patches = sorted((source / "tools/projectm-patches").glob("*.patch"))
    env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(source))
    for patch in patches:
        subprocess.run(["git", "apply", str(patch)], cwd=engine, env=env, check=True)
    core = source / "core/src/main/cpp"
    original_core = {p.name: sha(p) for p in core.glob("*") if p.is_file()}
    instrumented_paths = ["src/libprojectM/TimeKeeper.cpp", "src/libprojectM/TimeKeeper.hpp", "src/libprojectM/ProjectM.cpp",
                          "src/libprojectM/Renderer/MilkdropNoise.cpp", "src/libprojectM/Renderer/TextureManager.cpp",
                          "src/libprojectM/Renderer/TransitionShaderManager.cpp", "src/libprojectM/MilkdropPreset/PresetState.cpp",
                          "src/libprojectM/MilkdropPreset/MilkdropShader.cpp", "vendor/projectm-eval/projectm-eval/TreeFunctions.c"]
    original_engine_instrumentation = {name: (engine / name).read_text() for name in instrumented_paths}
    _instrument(engine)
    hooks = engine / "src/libprojectM/analysis_hooks.hpp"
    text = hooks.read_text().replace("#include <cstdint>", "#include <cstdint>\n#include <atomic>")
    text = text.replace("inline double clock_seconds = 0.0;", "inline std::atomic<double> clock_seconds{0.0};")
    hooks.write_text(text)
    native = core / "native-lib.cpp"
    original = native.read_text()
    clock = """double NowSeconds() {
    using namespace std::chrono;
    return duration<double>(steady_clock::now().time_since_epoch()).count();
}"""
    if original.count(clock) != 1:
        raise ValueError("core clock instrumentation does not match snapshot")
    native.write_text(original.replace(clock, "double NowSeconds() { return lab::clock_seconds.load(); }"))
    (core / "lab_bridge.cpp").write_bytes(frozen_inputs["lab_bridge.cpp"])
    cmake = core / "CMakeLists.txt"
    text = cmake.read_text()
    text = text.replace("add_subdirectory(${PROJECTM_SOURCE} projectm EXCLUDE_FROM_ALL)",
                        'add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-include' + str(hooks) + '>" )\n'
                        "add_subdirectory(${PROJECTM_SOURCE} projectm EXCLUDE_FROM_ALL)")
    text = text.replace("add_library(projectmtv SHARED native-lib.cpp snapshot_fade.cpp preset_prewarm.cpp)",
                        "add_library(projectmtv SHARED native-lib.cpp snapshot_fade.cpp preset_prewarm.cpp lab_bridge.cpp)")
    text += '\ntarget_include_directories(projectmtv PRIVATE "${PROJECTM_SOURCE}/src/libprojectM")\n'
    cmake.write_text(text)
    core_gradle = source / "core/build.gradle"
    core_gradle_original = core_gradle.read_text()
    if core_gradle_original.count('cppFlags "-std=c++17"') != 1:
        raise ValueError("core native build flags do not match snapshot")
    core_gradle.write_text(core_gradle_original.replace('cppFlags "-std=c++17"',
                            'arguments "-DCMAKE_BUILD_TYPE=RelWithDebInfo"\n                cppFlags "-std=c++17"'))
    app = source / "corpus-app"
    java = app / "src/main/java/nl/neerdael/projectm/corecorpus"
    java.mkdir(parents=True)
    for name in ("CorpusInstrumentation.java", "LabBridge.java"):
        (java / name).write_bytes(frozen_inputs[name])
    (app / "src/main/AndroidManifest.xml").write_text("""<manifest xmlns:android="http://schemas.android.com/apk/res/android">
  <application android:label="ProjectM core corpus" android:extractNativeLibs="true" android:allowBackup="false" />
  <instrumentation android:name="nl.neerdael.projectm.corecorpus.CorpusInstrumentation" android:targetPackage="nl.neerdael.projectmtv.corecorpus" />
</manifest>
""")
    (app / "build.gradle").write_text("""apply plugin: 'com.android.application'
android {
    namespace 'nl.neerdael.projectm.corecorpus'
    compileSdk 34
    ndkVersion '27.3.13750724'
    defaultConfig {
        applicationId 'nl.neerdael.projectmtv.corecorpus'
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName 'core-corpus-v1'
        ndk { abiFilters 'arm64-v8a' }
    }
    buildTypes { release { debuggable true; minifyEnabled false; signingConfig signingConfigs.debug } }
    compileOptions { sourceCompatibility JavaVersion.VERSION_1_8; targetCompatibility JavaVersion.VERSION_1_8 }
}
dependencies { implementation project(':core') }
""")
    (source / "settings.gradle").write_text(
        "pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }\n"
        "dependencyResolutionManagement { repositories { google(); mavenCentral() } }\n"
        "rootProject.name='ProjectMCoreCorpus'\ninclude ':core', ':corpus-app'\n")
    if (ROOT / "local.properties").exists():
        rows = [row for row in (ROOT / "local.properties").read_text().splitlines() if row.startswith("sdk.dir=")]
        (source / "local.properties").write_text("\n".join(rows) + "\n")
    instrumentation = {
        "builder_sha256": sha(frozen_harness / "build.py"),
        "worker_builder_sha256": sha(ROOT / "tools/preset-lab/src/preset_lab/build_worker.py"),
        "analysis_hooks_sha256": sha(hooks),
        "lab_bridge_sha256": sha(core / "lab_bridge.cpp"),
        "core_clock_transformation": "private NowSeconds returns shared atomic logical frame clock; engine TimeKeeper uses same clock",
        "rng_transformation": "private deterministic instrumented engine; no production RNG parity claim",
    }
    identity = {"backend": "projectmtv-core-android-v1", "variant": variant, "source_commit": commit,
                "upstream_commit": upstream_commit,
                "ordered_patches": [{"name": p.name, "sha256": sha(p)} for p in patches],
                "source_patch_sha256": digest([(p.name, sha(p)) for p in patches]),
                "original_core_source_sha256": original_core,
                "instrumented_core_source_sha256": {p.name: sha(p) for p in core.glob("*") if p.is_file()},
                "instrumentation": instrumentation, "instrumentation_sha256": digest(instrumentation),
                "harness_sources_sha256": {"CorpusInstrumentation.java": sha(java / "CorpusInstrumentation.java"),
                                           "LabBridge.java": sha(java / "LabBridge.java"),
                                           "lab_bridge.cpp": sha(core / "lab_bridge.cpp")},
                "core_library_entry": "lib/arm64-v8a/libprojectmtv.so", "core_sha256": None,
                "gradle_variant": "release", "native_build_type": "RelWithDebInfo", "prewarm_setting": "actual onMemoryPressure20s pause; job<20 logicalseconds"}
    assets = app / "src/main/assets"
    assets.mkdir(parents=True)
    (assets / "backend-identity.json").write_text(canonical(identity) + "\n")
    (destination / "private-core-diff.patch").write_text("".join(difflib.unified_diff(
        original.splitlines(True), native.read_text().splitlines(True),
        fromfile="original/native-lib.cpp", tofile="instrumented/native-lib.cpp")))
    (destination / "private-engine-diff.patch").write_text("".join(
        "".join(difflib.unified_diff(original_engine_instrumentation[name].splitlines(True), (engine / name).read_text().splitlines(True),
                                   fromfile="original/" + name, tofile="instrumented/" + name)) for name in instrumented_paths))
    (destination / "private-cmake-diff.patch").write_text("".join(difflib.unified_diff(
        subprocess.check_output(["git", "show", commit + ":core/src/main/cpp/CMakeLists.txt"], cwd=ROOT, text=True).splitlines(True),
        cmake.read_text().splitlines(True), fromfile="original/CMakeLists.txt", tofile="instrumented/CMakeLists.txt")))
    (destination / "identity.json").write_text(canonical(identity) + "\n")
    identity["clock_instrumentation_diff_sha256"] = sha(destination / "private-core-diff.patch")
    identity["engine_instrumentation_diff_sha256"] = sha(destination / "private-engine-diff.patch")
    identity["cmake_instrumentation_diff_sha256"] = sha(destination / "private-cmake-diff.patch")
    (assets / "backend-identity.json").write_text(canonical(identity) + "\n")
    (destination / "identity.json").write_text(canonical(identity) + "\n")
    return destination, source, identity


def build(variant, commit):
    destination, source, identity = prepare(variant, commit)
    with (destination / "gradle.log").open("w") as log:
        run([str(source / "gradlew"), "--no-daemon", ":corpus-app:assembleRelease"], source, log)
    built = source / "corpus-app/build/outputs/apk/release/corpus-app-release.apk"
    with zipfile.ZipFile(built) as archive:
        core = archive.read(identity["core_library_entry"])
    identity["core_sha256"] = hashlib.sha256(core).hexdigest()
    caches = list((source / "core/.cxx/RelWithDebInfo").glob("*/*/CMakeCache.txt"))
    if not caches:
        raise ValueError("missing native compile cache evidence")
    cache_evidence = []
    for cache in caches:
        lines = cache.read_text().splitlines()
        actual_type = next((row.split("=", 1)[1] for row in lines if row.startswith("CMAKE_BUILD_TYPE:")), None)
        flags = next((row.split("=", 1)[1] for row in lines if row.startswith("CMAKE_CXX_FLAGS_RELWITHDEBINFO:")), None)
        if actual_type != "RelWithDebInfo" or flags is None or "-O2" not in flags or "-O0" in flags:
            raise ValueError("native cache does not prove optimized RelWithDebInfo")
        commands = cache.parent / "compile_commands.json"
        if not commands.is_file():
            raise ValueError("missing native compilation command evidence")
        units = json.loads(commands.read_text())
        wrapper_units = [row for row in units if Path(row["file"]).name in ("native-lib.cpp", "snapshot_fade.cpp", "preset_prewarm.cpp")]
        if {Path(row["file"]).name for row in wrapper_units} != {"native-lib.cpp", "snapshot_fade.cpp", "preset_prewarm.cpp"}:
            raise ValueError("compiled core translation-unit topology is incomplete")
        if any("-O2" not in row.get("command", " ".join(row.get("arguments", []))) for row in wrapper_units):
            raise ValueError("core compilation commands do not prove O2")
        cache_evidence.append({"abi": cache.parent.name, "build_type": actual_type, "flags": flags,
                               "cache_sha256": sha(cache), "compile_commands_sha256": sha(commands),
                               "core_translation_units": [Path(row["file"]).name for row in wrapper_units]})
    identity["native_compile_evidence"] = cache_evidence
    if sha(Path(__file__)) != identity["instrumentation"]["builder_sha256"]:
        raise ValueError("builder changed after snapshot; refuse to repackage with ambiguous provenance")
    (source / "corpus-app/src/main/assets/backend-identity.json").write_text(canonical(identity) + "\n")
    with (destination / "repackage.log").open("w") as log:
        run([str(source / "gradlew"), "--no-daemon", ":corpus-app:assembleRelease"], source, log)
    with zipfile.ZipFile(built) as archive:
        if hashlib.sha256(archive.read(identity["core_library_entry"])).hexdigest() != identity["core_sha256"]:
            raise ValueError("native library changed while embedding its identity")
        if json.loads(archive.read("assets/backend-identity.json")) != identity:
            raise ValueError("embedded source identity differs")
    apk = destination / (variant + "-core-corpus.apk")
    shutil.copyfile(built, apk)
    (destination / "identity.json").write_text(canonical(identity) + "\n")
    metadata = {"apk": str(apk), "apk_sha256": sha(apk), "package": "nl.neerdael.projectmtv.corecorpus",
                "instrumentation_component": "nl.neerdael.projectm.corecorpus.CorpusInstrumentation", "backend_identity": identity}
    (WORK / ("worker-" + variant + ".json")).write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"apk": str(apk), "apk_sha256": sha(apk), "core_sha256": identity["core_sha256"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", choices=("baseline", "candidate"))
    parser.add_argument("--commit")
    args = parser.parse_args()
    commit = args.commit or ("a59b4e5" if args.variant == "baseline" else "HEAD")
    commit = subprocess.check_output(["git", "rev-parse", commit], cwd=ROOT, text=True).strip()
    build(args.variant, commit)
