#!/usr/bin/env python3
"""Build frozen actual-core AAR/worker pairs for focused Native trails checks.

Reuse the corpus worker and Preset Lab instrumentation. Export a committed
source revision; never instrument the task checkout or a released binary.
"""
import argparse
from dataclasses import asdict
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/preset-lab/src"))
from preset_lab.build_worker import prepare_engine
from preset_lab.identity import canonical_json, digest, file_digest

CLOCK_BODY = """double NowSeconds() {
    using namespace std::chrono;
    return duration<double>(steady_clock::now().time_since_epoch()).count();
}"""


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("Missing/ambiguous instrumentation anchor: " + old[:80])
    return text.replace(old, new)


def instrument_core(text):
    text = once(text, '#include "snapshot_fade.h"',
                '#include "snapshot_fade.h"\n#include "lab_bridge.hpp"')
    text = once(text, CLOCK_BODY, "double NowSeconds() { return lab::clock_seconds.load(); }")
    # Both initial setup and per-frame mode changes must use the frozen reference.
    pattern = r"projectm_opengl_set_line_reference_size\((g_engine\.pm|pm),[^;]+\);"
    text, count = re.subn(pattern, lambda m: "projectm_opengl_set_line_reference_size(" + m[1]
                         + ", core_corpus::reference_width, core_corpus::reference_height);", text)
    if count == 0:
        raise ValueError("No production line reference setter found")
    return text


def change(path, text, changes, root):
    before = path.read_text()
    name = path.relative_to(root).as_posix()
    changes.append("".join(difflib.unified_diff(before.splitlines(True), text.splitlines(True),
                                              fromfile="a/" + name, tofile="b/" + name)))
    path.write_text(text)


def command(args, cwd=None, log=None):
    return subprocess.run(args, cwd=cwd, check=True, stdout=log,
                          stderr=subprocess.STDOUT if log else None)


def native_hashes(archive):
    return {name: hashlib.sha256(archive.read(name)).hexdigest()
            for name in archive.namelist() if name.startswith("jni/") and name.endswith(".so")}


def build(commit, policy, role, work, abi="arm64-v8a"):
    if abi not in ("arm64-v8a", "armeabi-v7a"):
        raise ValueError("Unsupported ABI: " + abi)
    commit = subprocess.check_output(["git", "rev-parse", commit], cwd=ROOT, text=True).strip()
    destination = work.resolve() / role
    destination.mkdir(parents=True, exist_ok=False)
    source = destination / "source"
    source.mkdir()
    with tempfile.TemporaryDirectory(dir=destination) as temp:
        archive = Path(temp) / "source.tar"
        command(["git", "archive", commit, "-o", str(archive)], ROOT)
        with tarfile.open(archive) as stream:
            stream.extractall(source, filter="data")
    # prepare_engine archives the pinned submodules and applies this revision's
    # ordered patches before the standard deterministic transformations.
    engine = source / "third_party/projectm"
    engine.rmdir()
    engine.symlink_to((ROOT / "third_party/projectm").resolve(), target_is_directory=True)
    snapshot, engine_identity = prepare_engine(source, destination / "snapshots")
    engine.unlink()
    shutil.copytree(snapshot, engine)
    changes = []
    hooks = engine / "src/libprojectM/analysis_hooks.hpp"
    change(hooks, once(once(hooks.read_text(), "#include <cstdint>",
                           "#include <cstdint>\n#include <atomic>"),
                       "inline double clock_seconds = 0.0;", "inline std::atomic<double> clock_seconds{0.0};"),
           changes, source)
    cpp = source / "core/src/main/cpp"
    native = cpp / "native-lib.cpp"
    change(native, instrument_core(native.read_text()), changes, source)
    for name in ("lab_bridge.cpp", "lab_bridge.hpp"):
        shutil.copyfile(ROOT / "tools/core-corpus/native-lab" / name, cpp / name)
    bridge = cpp / "lab_bridge.cpp"
    change(bridge, once(bridge.read_text(), "lab::clock_seconds = seconds;", "lab::clock_seconds.store(seconds);"),
           changes, source)
    cmake = cpp / "CMakeLists.txt"
    text = cmake.read_text()
    # The immutable scratch engine already contains the entire recorded series.
    # Instrumentation intentionally changes its sources, so production CMake
    # reverse-check/apply cannot be rerun over it.
    start = text.index("find_package(Git REQUIRED)")
    end = text.index('file(LOCK ${PROJECTM_PATCH_LOCK} RELEASE)') + len('file(LOCK ${PROJECTM_PATCH_LOCK} RELEASE)')
    text = text[:start] + "# Frozen engine: complete series applied by prepare_engine.\n" + text[end:]
    text = once(text, "add_library(projectmtv SHARED native-lib.cpp snapshot_fade.cpp preset_prewarm.cpp)",
                "add_library(projectmtv SHARED native-lib.cpp snapshot_fade.cpp preset_prewarm.cpp lab_bridge.cpp)\n"
                "target_include_directories(projectmtv PRIVATE ${PROJECTM_SOURCE}/src/libprojectM)")
    change(cmake, text, changes, source)
    gradle = source / "core/build.gradle"
    change(gradle, once(gradle.read_text(), 'abiFilters "armeabi-v7a", "arm64-v8a"',
                       'abiFilters "' + abi + '"'), changes, source)
    sdk = Path(os.environ.get("ANDROID_HOME", str(Path.home() / "Library/Android/sdk")))
    (source / "local.properties").write_text("sdk.dir=" + str(sdk) + "\n")
    patches = [{"name": p.name, "sha256": file_digest(p)}
               for p in sorted((source / "tools/projectm-patches").glob("*.patch"))]
    if [int(p["name"][:4]) for p in patches] != list(range(1, len(patches) + 1)):
        raise ValueError("Nonconsecutive patch series")
    (destination / "instrumentation.diff").write_text("".join(changes))
    identity = {"source_commit": commit, "policy": policy, "role": role, "abi": abi,
                "ordered_patches": patches, "engine_identity": asdict(engine_identity),
                "builder_sha256": file_digest(Path(__file__)),
                "instrumentation_diff_sha256": file_digest(destination / "instrumentation.diff"),
                "bridge_sha256": {p.name: file_digest(p) for p in (cpp / "lab_bridge.cpp", cpp / "lab_bridge.hpp")},
                "shipping_byte_identity": False,
                "source_files_sha256": {p.relative_to(source).as_posix(): file_digest(p)
                                        for base in (cpp, engine / "src", engine / "vendor/projectm-eval")
                                        for p in sorted(base.rglob("*")) if p.is_file()}}
    with (destination / "aar-build.log").open("w") as log:
        command([str(source / "gradlew"), ":core:assembleRelease", "--console=plain",
                 "-PprojectmCoreRenderingPolicy=" + policy], source, log)
    aar = destination / (role + ".aar")
    shutil.copyfile(source / "core/build/outputs/aar/core-release.aar", aar)
    identity["aar_sha256"] = file_digest(aar)
    with zipfile.ZipFile(aar) as archive:
        identity["native_sha256"] = native_hashes(archive)
        identity["assets_sha256"] = digest({name: hashlib.sha256(archive.read(name)).hexdigest()
                                           for name in archive.namelist() if name.startswith("assets/")})
    worker = source / "tools/core-corpus/android-worker"
    shutil.copyfile(source / "local.properties", worker / "local.properties")
    instrument = worker / "app/src/main/java/nl/neerdael/projectmtv/corpus/CorpusInstrumentation.java"
    text = instrument.read_text()
    text = once(text, "ProjectMJNI.setAutoChange(false);",
                """if (job.has("nativeTrails")) {
            ProjectMJNI.class.getMethod("setNativeTrails", int.class).invoke(null, job.getInt("nativeTrails"));
        }
        ProjectMJNI.setAutoChange(false);""")
    text = once(text, 'manifest.put("verifiedPresetName", ProjectMJNI.getCurrentPresetName());',
                '''try {
            manifest.put("nativeTrailsStatus", ProjectMJNI.class.getMethod("getNativeTrailsStatus").invoke(null));
        } catch (NoSuchMethodException absent) {
            manifest.put("nativeTrailsStatus", "API absent in baseline");
        }
        manifest.put("verifiedPresetName", ProjectMJNI.getCurrentPresetName());''')
    text = once(text, "int nextCapture = 0;",
                "int nextCapture = 0;\n        double[] frameTimesMs = new double[FRAMES - 120];\n"
                '        manifest.put("pssBeforeFramesKB", android.os.Debug.getPss());')
    text = once(text, "ProjectMJNI.onDrawFrame();",
                "long frameStarted = System.nanoTime();\n            ProjectMJNI.onDrawFrame();\n"
                "            GLES30.glFinish();\n"
                "            if (frame >= 120) frameTimesMs[frame - 120] = (System.nanoTime() - frameStarted) / 1e6;")
    text = once(text, 'manifest.put("renderWallDurationMs", SystemClock.elapsedRealtime() - renderStarted);',
                'manifest.put("renderWallDurationMs", SystemClock.elapsedRealtime() - renderStarted);\n'
                '        manifest.put("pssAfterFramesKB", android.os.Debug.getPss());\n'
                '        double total = 0; for (double value : frameTimesMs) total += value;\n'
                '        java.util.Arrays.sort(frameTimesMs);\n'
                '        manifest.put("serializedFrameMeanMs", total / frameTimesMs.length);\n'
                '        manifest.put("serializedFrameP90Ms", frameTimesMs[(int) Math.ceil(.9 * frameTimesMs.length) - 1]);\n'
                '        manifest.put("timingScope", "onDrawFrame plus glFinish; 360 frames; excludes capture/PNG I/O; emulator engine, not TV app fps");')
    instrument.write_text(text)
    identity["worker_java_sha256"] = file_digest(instrument)
    wrapper = [str(source / "gradlew"), "-p", str(worker), ":app:assembleDebug", "--console=plain",
               "-PcoreAar=" + str(aar), "-PcorpusApplicationId=nl.neerdael.projectmtv.corpus" +
               ("baseline" if role.startswith("baseline") else "candidate")]
    with (destination / "worker-build.log").open("w") as log:
        command(wrapper, source, log)
    apk = destination / (role + ".apk")
    shutil.copyfile(worker / "app/build/outputs/apk/debug/app-debug.apk", apk)
    with zipfile.ZipFile(apk) as archive:
        for name, expected in identity["native_sha256"].items():
            if hashlib.sha256(archive.read(name.replace("jni/", "lib/", 1))).hexdigest() != expected:
                raise ValueError("Worker native bytes differ from the supplied AAR")
    identity.update({"aar": str(aar), "apk": str(apk), "apk_sha256": file_digest(apk),
                     "package": "nl.neerdael.projectmtv.corpus" +
                     ("baseline" if role.startswith("baseline") else "candidate")})
    (destination / "identity.json").write_text(canonical_json(identity) + "\n")
    print(canonical_json({key: identity[key] for key in ("source_commit", "policy", "role", "aar", "apk", "apk_sha256")}))
    return identity


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--policy", choices=("native", "capped"), required=True)
    parser.add_argument("--role", choices=("baseline-native", "baseline-capped", "candidate-native", "candidate-capped"), required=True)
    parser.add_argument("--abi", choices=("arm64-v8a", "armeabi-v7a"), default="arm64-v8a")
    parser.add_argument("--work", type=Path, default=ROOT / "build/native-trails/workers")
    args = parser.parse_args()
    build(args.commit, args.policy, args.role, args.work, abi=args.abi)
