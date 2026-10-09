#!/usr/bin/env python3
"""Reproduce the frozen catalog's two native desktop rendering workers."""

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tarfile
from dataclasses import asdict
from pathlib import Path


SOURCE_COMMIT = "8a15996e8510533113a44e26feaddc3a7d6e85f5"
ENGINE_COMMIT = "6f64807467e312034883a4389e6aa80a675458bc"
UPSTREAM_COMMIT = "e98fca85e57802d27a6d11499642de2a1d5e994e"
EVALUATOR_COMMIT = "22fb0cfd8f2dfbcd2b68f2443e7f44e19b32c09a"


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def inventory(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): file_hash(p)
            for p in sorted(root.rglob("*")) if p.is_file()}


def verify_cache(cache: Path, expected: str) -> None:
    if git(cache, "rev-parse", "HEAD") != expected:
        raise ValueError(f"cache HEAD must be {expected}: {cache}")
    if not (cache / "CMakeLists.txt").is_file():
        raise ValueError(f"cache must contain a checked-out engine: {cache}")
    evaluator = cache / "vendor/projectm-eval"
    tree = git(cache, "ls-tree", "HEAD", "vendor/projectm-eval").split()
    if len(tree) < 3 or tree[2] != EVALUATOR_COMMIT:
        raise ValueError(f"unexpected engine evaluator pin: {cache}")
    if git(evaluator, "rev-parse", "HEAD") != EVALUATOR_COMMIT:
        raise ValueError(f"initialize evaluator at {EVALUATOR_COMMIT}: {evaluator}")


def archive_tooling(repo: Path, destination: Path, work: Path) -> None:
    archive = work / "repository-inputs.tar"
    subprocess.run(["git", "-C", str(repo), "archive", SOURCE_COMMIT,
                    "-o", str(archive), "tools/preset-lab", "tools/projectm-patches"],
                   check=True)
    destination.mkdir()
    with tarfile.open(archive) as stream:
        stream.extractall(destination, filter="data")


def prepare_harness(native: Path, harness: Path) -> dict[str, object]:
    original = inventory(native)
    shutil.copytree(native, harness)
    worker = harness / "worker.cpp"
    old = ("        engine.SetLineReferenceSize(line_reference_width, line_reference_height);\n"
           "        engine.SetLineAntialiasing(cfg.value(\"line_antialiasing\", false));\n")
    new = "#ifdef CATALOG_TV\n" + old + "        engine.SetFeedbackDetail(-1.0f);\n#endif\n"
    source = worker.read_text()
    if source.count(old) != 1:
        raise ValueError("frozen worker TV-control block differs from expected source")
    worker.write_text(source.replace(old, new))
    cmake = harness / "CMakeLists.txt"
    cmake.write_text(cmake.read_text() + "\nif(CATALOG_TV)\n"
                     " target_compile_definitions(preset-lab-worker PRIVATE CATALOG_TV)\n"
                     "endif()\n")
    return {
        "original": original,
        "modified": inventory(harness),
        "modifications": [
            "Guard SetLineReferenceSize and SetLineAntialiasing with CATALOG_TV.",
            "Inside that guard call SetFeedbackDetail(-1.0f), disabling TV feedback detail.",
            "CMake defines CATALOG_TV for the patched role only.",
        ],
    }


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True,
                        help="ProjectM TV git checkout containing the frozen source commit")
    parser.add_argument("--engine-cache", type=Path, required=True,
                        help=f"engine checkout at {ENGINE_COMMIT}, evaluator initialized")
    parser.add_argument("--upstream-cache", type=Path, required=True,
                        help=f"upstream checkout at {UPSTREAM_COMMIT}, evaluator initialized")
    parser.add_argument("--work", type=Path, required=True,
                        help="new, nonexistent output directory; existing workers are never overwritten")
    parser.add_argument("--jobs", type=int, default=6, help="parallel native build jobs (default: 6)")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    for name in ("repo", "engine_cache", "upstream_cache", "work"):
        setattr(args, name, getattr(args, name).expanduser().resolve())
    return args


def main() -> None:
    args = arguments()
    if args.work.exists():
        raise ValueError(f"--work must not already exist: {args.work}")
    if git(args.repo, "rev-parse", f"{SOURCE_COMMIT}^{{commit}}") != SOURCE_COMMIT:
        raise ValueError("frozen ProjectM TV source commit is unavailable")
    verify_cache(args.engine_cache, ENGINE_COMMIT)
    verify_cache(args.upstream_cache, UPSTREAM_COMMIT)
    args.work.mkdir(parents=True)
    frozen = args.work / "repository-inputs"
    archive_tooling(args.repo, frozen, args.work)
    sys.path.insert(0, str(frozen / "tools/preset-lab/src"))
    from preset_lab.build_worker import NATIVE, prepare_engine

    patches = sorted((frozen / "tools/projectm-patches").glob("*.patch"))
    if len(patches) != 34:
        raise ValueError(f"frozen source must contain 34 patches, found {len(patches)}")
    ordered_patches = [{"name": p.name, "sha256": file_hash(p)} for p in patches]
    harness = args.work / "harness"
    harness_receipt = prepare_harness(NATIVE, harness)
    write_json(args.work / "harness-identity.json", harness_receipt)

    for role, cache in (("upstream", args.upstream_cache), ("patched", args.engine_cache)):
        role_work = args.work / role
        inputs = role_work / "inputs"
        (inputs / "third_party").mkdir(parents=True)
        # prepare_engine uses git archive HEAD for engine and evaluator; cache files
        # and working-tree modifications are never copied, patched or compiled.
        (inputs / "third_party/projectm").symlink_to(cache, target_is_directory=True)
        patch_inputs = inputs / "tools/projectm-patches"
        patch_inputs.mkdir(parents=True)
        if role == "patched":
            for patch in patches:
                shutil.copyfile(patch, patch_inputs / patch.name)
        source, engine_identity = prepare_engine(inputs, role_work)
        source_tree = inventory(source)
        write_json(role_work / "source-tree.json", source_tree)
        output = role_work / "native-build"
        output.mkdir()
        configure = ["cmake", "-S", str(harness), "-B", str(output), "-G", "Ninja",
                     "-DCMAKE_BUILD_TYPE=Release", f"-DPROJECTM_SOURCE={source}",
                     "-DCATALOG_TV=" + ("ON" if role == "patched" else "OFF")]
        build = ["cmake", "--build", str(output), "-j", str(args.jobs)]
        with (role_work / "build.log").open("w") as log:
            subprocess.run(configure, check=True, stdout=log, stderr=subprocess.STDOUT)
            subprocess.run(build, check=True, stdout=log, stderr=subprocess.STDOUT)
        binary = output / "preset-lab-worker"
        receipt = {
            "role": role,
            "source_commit": SOURCE_COMMIT,
            "engine": asdict(engine_identity),
            "evaluator_commit": EVALUATOR_COMMIT,
            "ordered_patches": ordered_patches if role == "patched" else [],
            "source_tree_sha256": hashlib.sha256(canonical(source_tree)).hexdigest(),
            "source_tree_manifest_sha256": file_hash(role_work / "source-tree.json"),
            "worker_sha256": file_hash(binary),
            "harness": harness_receipt["modified"],
            "harness_original": harness_receipt["original"],
            "harness_modifications": harness_receipt["modifications"],
            "catalog_reference_controls": {
                "line_reference_width": 0,
                "line_reference_height": 0,
                "line_antialiasing": False,
                "patched_feedback_detail": -1.0,
                "window_dimensions": "exact request width/height; no TV shader-canvas override",
            },
            "builder_sha256": file_hash(Path(__file__).resolve()),
            "repository_inputs_archive_sha256": file_hash(args.work / "repository-inputs.tar"),
            "host": {"system": platform.system(), "machine": platform.machine()},
            "configure_command": configure,
            "build_command": build,
            "source": str(source),
            "worker": str(binary),
            "qualification": "source-instrumented desktop worker; not shipping binary or TV performance proof",
        }
        write_json(role_work / "identity.json", receipt)
        print(f"{role}: {binary}", flush=True)


if __name__ == "__main__":
    main()
