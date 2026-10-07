#!/usr/bin/env python3
"""Build isolated, instrumented *actual Android Core* AARs for corpus jobs.

The source and engine checkouts are read-only inputs. Only newly exported scratch
repositories are transformed; all transformations and compiled inputs are recorded.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import asdict
import zipfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "tools/preset-lab/src"))
from preset_lab.build_worker import prepare_engine
from preset_lab.identity import canonical_json, digest, file_digest

BASELINE = "5681852f9497f320e57b8a5dd40c076d0f5a6b18"
PUBLISHED_BASELINE_AAR_SHA256 = "4c960385cd0afb7007ed08f99e0e04836c243f950e61f3e6e5dc4d9e77c8a440"
ENGINE = "e0b0a967f0ffd7d332106c366668ed271718472b"
EVALUATOR = "da885dcdf33620ef26aa04cac9e215378b80252e"
CPP = "core/src/main/cpp/"
CORE_INPUTS = [CPP + name for name in (
    "native-lib.cpp", "snapshot_fade.cpp", "snapshot_fade.h", "preset_prewarm.cpp",
    "preset_prewarm.h", "CMakeLists.txt")]
CORE_INPUTS += ["core/src/main/java/nl/neerdael/projectm/core/ProjectMJNI.java",
                "core/build.gradle", "build.gradle", "settings.gradle",
                "gradle/wrapper/gradle-wrapper.properties"]
CLOCK_BODY = """double NowSeconds() {
    using namespace std::chrono;
    return duration<double>(steady_clock::now().time_since_epoch()).count();
}"""


def run(command: list[str], *, cwd: Path | None = None) -> str:
    return subprocess.check_output(command, cwd=cwd, text=True).strip()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"expected exactly one {label}; found {text.count(old)}")
    return text.replace(old, new)


def set_native_frame_time(text: str, clock: str) -> str:
    pattern = r"(?m)^([ \t]*)(projectm_opengl_render_frame(?:_fbo)?\(g_engine\.pm(?:,[^;\n]+)?\);)$"
    text, count = re.subn(pattern, lambda match: match[1] +
                         "projectm_set_frame_time(g_engine.pm, " + clock + ");\n" +
                         match[1] + match[2], text)
    if count == 0:
        raise ValueError("No actual Core render call found for frame time")
    return text


def transform_core_native(text: str, native_frame_time: bool = False) -> str:
    text = replace_once(text, '#include "snapshot_fade.h"',
                        '#include "snapshot_fade.h"\n#include "lab_bridge.hpp"', "bridge include")
    text = replace_once(text, CLOCK_BODY,
                        "double NowSeconds() {\n    return lab::clock_seconds;\n}", "core clock")
    text = replace_once(text,
                        "projectm_opengl_set_line_reference_size(g_engine.pm, 1024, 768);",
                        "projectm_opengl_set_line_reference_size(g_engine.pm, "
                        "core_corpus::reference_width, core_corpus::reference_height);",
                        "line reference dimensions")
    return set_native_frame_time(text, "lab::clock_seconds") if native_frame_time else text


def relocate_shader_hook(text: str) -> str:
    # Patch 0024's first hunk is anchored to line 1. Keep its reverse-check valid
    # without changing the deterministic hook or the immutable lab snapshot.
    include = '#include "../analysis_hooks.hpp"\n'
    if not text.startswith(include) or text.count(include) != 1:
        raise ValueError("expected exactly one prepended shader hook")
    return replace_once(text[len(include):], "\nnamespace libprojectM {",
                        "\n" + include + "\nnamespace libprojectM {", "shader namespace")


def export_commit(source: Path, commit: str, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
        archive = Path(temporary) / "source.tar"
        subprocess.run(["git", "-C", str(source), "archive", commit, "-o", str(archive)], check=True)
        with tarfile.open(archive) as stream:
            stream.extractall(destination, filter="data")


def gitlink(repo: Path, revision: str, path: str) -> str:
    row = run(["git", "-C", str(repo), "ls-tree", revision, "--", path]).split()
    if len(row) != 4 or row[0:2] != ["160000", "commit"] or row[3] != path:
        raise ValueError(f"missing pinned submodule {path} in {revision}")
    return row[2]


def checkout_pinned_engine(repo: Path, commit: str, destination: Path) -> tuple[Path, str, str]:
    """Resolve requested gitlinks without changing either live submodule checkout."""
    source = repo / "third_party/projectm"
    engine_pin = gitlink(repo, commit, "third_party/projectm")
    subprocess.run(["git", "clone", "--shared", "--no-checkout", str(source), str(destination)],
                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def checkout(cached: Path, private: Path, pin: str) -> None:
        present = subprocess.run(["git", "-C", str(private), "cat-file", "-e", pin + "^{commit}"],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if present.returncode:
            url = run(["git", "-C", str(cached), "remote", "get-url", "origin"])
            subprocess.run(["git", "-C", str(private), "fetch", url, pin], check=True)
        subprocess.run(["git", "-C", str(private), "checkout", "--detach", pin],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    checkout(source, destination, engine_pin)
    evaluator_pin = gitlink(destination, engine_pin, "vendor/projectm-eval")
    evaluator = destination / "vendor/projectm-eval"
    subprocess.run(["git", "clone", "--shared", "--no-checkout",
                    str(source / "vendor/projectm-eval"), str(evaluator)],
                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    checkout(source / "vendor/projectm-eval", evaluator, evaluator_pin)
    return destination, engine_pin, evaluator_pin


def hashes(root: Path, paths: list[str]) -> dict[str, str]:
    return {name: file_digest(root / name) for name in paths}


def diff_text(before: str, after: str, name: str) -> str:
    return "".join(difflib.unified_diff(before.splitlines(keepends=True),
                                      after.splitlines(keepends=True),
                                      fromfile="original/" + name, tofile="instrumented/" + name))


def patch_manifest(root: Path, expected_count: int | None) -> list[dict]:
    patches = sorted((root / "tools/projectm-patches").glob("*.patch"))
    if expected_count is not None and len(patches) != expected_count:
        raise ValueError(f"expected {expected_count} patches, got {len(patches)}")
    if not patches or [int(p.name[:4]) for p in patches] != list(range(1, len(patches) + 1)):
        raise ValueError("patch series is not consecutive and ordered")
    return [{"name": p.name, "sha256": file_digest(p)} for p in patches]


def build_variant(source_repo: Path, work: Path, variant: str, commit: str,
                  sdk: Path, abis: list[str], prepare_only: bool) -> dict:
    destination = work / ("core-" + variant)
    if destination.exists():
        raise ValueError(f"scratch repository already exists: {destination}")
    export_commit(source_repo, commit, destination)
    original_inputs = hashes(destination, CORE_INPUTS)
    patches = patch_manifest(destination, 24 if variant == "baseline" else None)
    source_engine, engine_pin, evaluator_pin = checkout_pinned_engine(
        source_repo, commit, work / ("engine-checkout-" + variant))
    if variant == "baseline" and (engine_pin != ENGINE or evaluator_pin != EVALUATOR):
        raise ValueError("historical corpus baseline pins changed")
    exported_engine = destination / "third_party/projectm"
    # prepare_engine reads commit archives rather than the live patched tree.
    shutil.rmtree(exported_engine)
    exported_engine.symlink_to(source_engine.resolve(), target_is_directory=True)
    snapshot, engine_identity = prepare_engine(destination, work / "engine-snapshots")
    exported_engine.unlink()
    shutil.copytree(snapshot, exported_engine)
    native_frame_time = "projectm_set_frame_time(" in (
        exported_engine / "src/api/include/projectM-4/parameters.h").read_text()
    apply_env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(destination.parent))
    if variant == "baseline":
        shader = exported_engine / "src/libprojectM/MilkdropPreset/MilkdropShader.cpp"
        shader.write_text(relocate_shader_hook(shader.read_text()))
        # Retain the frozen historical corpus source/patch acceptance control.
        subprocess.run(["git", "apply", "--reverse", "--check",
                        str(destination / "tools/projectm-patches" / patches[-1]["name"])],
                       cwd=exported_engine, env=apply_env, check=True)

    # Independently preserve all engine clock/RNG transformation diffs and input hashes.
    engine_original = work / ("engine-original-" + variant)
    export_commit(source_engine, engine_pin, engine_original)
    (engine_original / "vendor/projectm-eval").rmdir()
    export_commit(source_engine / "vendor/projectm-eval", evaluator_pin,
                  engine_original / "vendor/projectm-eval")
    for patch in patches:
        subprocess.run(["git", "apply", str(destination / "tools/projectm-patches" / patch["name"])],
                       cwd=engine_original, env=apply_env, check=True)
    engine_diffs, engine_transforms = [], {}
    for path in sorted(exported_engine.rglob("*")):
        if not path.is_file() or path.name == "preset-lab-identity.json":
            continue
        relative = path.relative_to(exported_engine).as_posix()
        original = engine_original / relative
        if not original.exists() or file_digest(original) != file_digest(path):
            old_text = original.read_text() if original.exists() else ""
            engine_diffs.append(diff_text(old_text, path.read_text(), "third_party/projectm/" + relative))
            engine_transforms[relative] = {
                "original_sha256": file_digest(original) if original.exists() else None,
                "instrumented_sha256": file_digest(path)}

    transformations = []
    def update(name: str, text: str) -> None:
        path = destination / name
        transformations.append(diff_text(path.read_text(), text, name))
        path.write_text(text)
    native_path = CPP + "native-lib.cpp"
    update(native_path, transform_core_native((destination / native_path).read_text(), native_frame_time=native_frame_time))
    cmake_name = CPP + "CMakeLists.txt"
    cmake = (destination / cmake_name).read_text()
    if variant != "baseline":
        start = cmake.index("find_package(Git REQUIRED)")
        end_marker = 'file(LOCK ${PROJECTM_PATCH_LOCK} RELEASE)'
        end = cmake.index(end_marker) + len(end_marker)
        cmake = cmake[:start] + "# Frozen engine: complete series applied by prepare_engine.\n" + cmake[end:]
    cmake = replace_once(cmake,
                         "add_library(projectmtv SHARED native-lib.cpp snapshot_fade.cpp preset_prewarm.cpp)",
                         "add_library(projectmtv SHARED native-lib.cpp snapshot_fade.cpp preset_prewarm.cpp lab_bridge.cpp)\n"
                         "target_include_directories(projectmtv PRIVATE ${PROJECTM_SOURCE}/src/libprojectM)",
                         "production native target")
    update(cmake_name, cmake)
    for name in ("lab_bridge.cpp", "lab_bridge.hpp"):
        target = destination / CPP / name
        shutil.copyfile(HERE / "native-lab" / name, target)
        transformations.append(diff_text("", target.read_text(), CPP + name))
    build_name = "core/build.gradle"
    if abis != ["armeabi-v7a", "arm64-v8a"]:
        update(build_name, replace_once((destination / build_name).read_text(),
               'abiFilters "armeabi-v7a", "arm64-v8a"',
               "abiFilters " + ", ".join(json.dumps(abi) for abi in abis), "ABI filters"))
    (destination / "local.properties").write_text(f"sdk.dir={sdk}\n")
    (destination / "gradlew").chmod(0o755)
    (destination / "core-transformation.diff").write_text("".join(transformations))
    (destination / "engine-transformation.diff").write_text("".join(engine_diffs))
    instrumented_inputs = hashes(destination, CORE_INPUTS + [CPP + "lab_bridge.cpp", CPP + "lab_bridge.hpp"])
    metadata = {
        "schema_version": 1, "backend": "projectmtv-core-android-v1", "variant": variant,
        "source_commit": commit, "published_baseline_source_commit": BASELINE,
        "published_baseline_aar_sha256": PUBLISHED_BASELINE_AAR_SHA256,
        "shipping_byte_identity": False, "abis": abis, "build_type": "release",
        "engine_identity": asdict(engine_identity), "engine_commit": engine_pin,
        "evaluator_commit": evaluator_pin, "native_frame_time_api": native_frame_time,
        "ordered_patches": patches,
        "patch_series_sha256": digest([(p["name"], p["sha256"]) for p in patches]),
        "original_core_input_sha256": original_inputs,
        "instrumented_core_input_sha256": instrumented_inputs,
        "engine_transforms": engine_transforms,
        "engine_hook_include_relocation": ("MilkdropShader.cpp: unchanged analysis_hooks include moved before namespace to preserve patch0024 reverse-check"
                                          if variant == "baseline" else None),
        "core_transformation_sha256": file_digest(destination / "core-transformation.diff"),
        "engine_transformation_sha256": file_digest(destination / "engine-transformation.diff"),
        "builder_sha256": file_digest(Path(__file__)),
        "core_repository": str(destination), "engine_snapshot": str(snapshot),
        "tool_versions": {
            "java": subprocess.run(["java", "-version"], capture_output=True, text=True, check=True).stderr.strip(),
            "python": sys.version, "git": run(["git", "--version"]),
            "ndk": (sdk / "ndk/27.3.13750724/source.properties").read_text(),
            "cmake": run([str(sdk / "cmake/3.22.1/bin/cmake"), "--version"]),
            "gradle_wrapper_properties": (destination / "gradle/wrapper/gradle-wrapper.properties").read_text(),
            "android_gradle_plugin": "8.12.0",
        },
    }
    identity_path = destination / "source-identity.json"
    identity_path.write_text(canonical_json(metadata) + "\n")
    if not prepare_only:
        with (destination / "assemble-release.log").open("w") as log:
            subprocess.run(["./gradlew", ":core:assembleRelease", "--no-daemon", "--console=plain"],
                           cwd=destination, check=True, stdout=log, stderr=subprocess.STDOUT)
        aar = destination / "core/build/outputs/aar/core-release.aar"
        with zipfile.ZipFile(aar) as archive:
            native = {name: hashlib.sha256(archive.read(name)).hexdigest()
                      for name in archive.namelist() if name.startswith("jni/") and name.endswith(".so")}
            if set(native) != {f"jni/{abi}/libprojectmtv.so" for abi in abis}:
                raise ValueError(f"unexpected native AAR contents: {native}")
            packaged_assets = {name: hashlib.sha256(archive.read(name)).hexdigest()
                               for name in archive.namelist() if name.startswith("assets/") and not name.endswith("/")}
        metadata.update({"aar_path": str(aar), "aar_sha256": file_digest(aar),
                         "aar_native_sha256": native,
                         "packaged_assets_sha256": digest(packaged_assets),
                         "packaged_preset_count": sum(name.startswith("assets/presets/") for name in packaged_assets),
                         "packaged_texture_count": sum(name.startswith("assets/textures/") for name in packaged_assets),
                         "assemble_log_sha256": file_digest(destination / "assemble-release.log")})
        nm = sdk / "ndk/27.3.13750724/toolchains/llvm/prebuilt/darwin-x86_64/bin/llvm-nm"
        compiled = {}
        for abi in abis:
            libraries = list((destination / "core/build/intermediates/cxx").glob(f"*/**/obj/{abi}/libprojectmtv.so"))
            if len(libraries) != 1:
                raise ValueError(f"expected one unstripped native library for {abi}: {libraries}")
            symbols = run([str(nm), "-C", str(libraries[0])]) + "\n"
            for required in ["SnapshotFade::Capture(", "PresetPrewarmer::Run(",
                             "Java_nl_neerdael_projectmtv_corpus_LabBridge_initialize",
                             "Java_nl_neerdael_projectmtv_corpus_LabBridge_setFrameClock",
                             "libprojectM::TimeKeeper::UpdateTimers()"]:
                if required not in symbols:
                    raise ValueError(f"missing real linked native symbol: {required}")
            if sum(line.endswith(" lab::clock_seconds") for line in symbols.splitlines()) != 1:
                raise ValueError("Core and engine must share exactly one lab::clock_seconds symbol")
            symbol_file = destination / f"native-symbols-{abi}.txt"
            symbol_file.write_text(symbols)
            commands_paths = list((destination / "core/.cxx").glob(f"RelWithDebInfo/*/{abi}/compile_commands.json"))
            if len(commands_paths) != 1:
                raise ValueError(f"expected actual Core compile database: {commands_paths}")
            commands = json.loads(commands_paths[0].read_text())
            units = {}
            for name in ["native-lib.cpp", "snapshot_fade.cpp", "preset_prewarm.cpp", "lab_bridge.cpp"]:
                rows = [entry for entry in commands if Path(entry["file"]) == destination / CPP / name]
                if len(rows) != 1:
                    raise ValueError(f"missing or duplicate actual Core translation unit: {name}")
                units[name] = rows[0]
            compiled[abi] = {"production_and_bridge_compile_commands": units,
                             "compile_commands_sha256": file_digest(commands_paths[0]),
                             "unstripped_native_sha256": file_digest(libraries[0]),
                             "native_symbols_sha256": file_digest(symbol_file),
                             "one_shared_clock_symbol": True}
        metadata["compiled_native_provenance"] = compiled
        metadata["tool_versions"]["gradle"] = run(["./gradlew", "--version", "--console=plain"], cwd=destination)
        if metadata["packaged_preset_count"] != 9606:
            raise ValueError(f"wrong corpus size: {metadata['packaged_preset_count']}")
        (destination / "packaged-assets.json").write_text(canonical_json(packaged_assets) + "\n")
        identity_path.write_text(canonical_json(metadata) + "\n")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--work", type=Path, default=REPO / "build/core-corpus")
    parser.add_argument("--variant", choices=["baseline", "candidate", "both"], default="both")
    parser.add_argument("--candidate-commit", default="HEAD")
    parser.add_argument("--sdk", type=Path, default=Path(os.environ.get("ANDROID_HOME", str(Path.home() / "Library/Android/sdk"))))
    parser.add_argument("--abis", nargs="+", choices=["arm64-v8a", "armeabi-v7a"], default=["arm64-v8a"])
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    repo, work = args.repo.resolve(), args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    commit = run(["git", "-C", str(repo), "rev-parse", args.candidate_commit])
    variants = ["baseline", "candidate"] if args.variant == "both" else [args.variant]
    for variant in variants:
        result = build_variant(repo, work, variant, BASELINE if variant == "baseline" else commit,
                               args.sdk.resolve(), args.abis, args.prepare_only)
        print(canonical_json({"variant": variant, "source_identity": str(work / ("core-" + variant) / "source-identity.json"),
                              "aar_path": result.get("aar_path"), "aar_sha256": result.get("aar_sha256")}))


if __name__ == "__main__":
    main()
