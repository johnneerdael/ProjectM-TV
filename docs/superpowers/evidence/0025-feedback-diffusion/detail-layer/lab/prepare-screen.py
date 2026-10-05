"""Build isolated original/fixed engines and a worker that emits eight captures."""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from preset_lab.build_worker import prepare_engine
from capture_frames import PICKS


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, default=Path("build/detail-clipping/screen"))
    parser.add_argument("--before-ref", default="a98b932ae40c01ed6ad853f55bb56f64c15d4b60")
    args = parser.parse_args()
    repo = Path.cwd().resolve()
    work = args.work.resolve()
    if work.exists() and any(work.iterdir()):
        parser.error("--work must be empty; choose a fresh directory")
    work.mkdir(parents=True, exist_ok=True)
    base, identity = prepare_engine(repo, work / "base")
    native = work / "native"
    shutil.copytree(repo / "tools/preset-lab/src/preset_lab/native", native)
    # Keep the same frame clock, PCM and engine calls. Avoid reading/exporting
    # 472 unused 4K frames per job; only capture the historical eight picks.
    worker = native / "worker.cpp"
    source = worker.read_text()
    old = "            auto pixels = capture.Read();"
    predicate = " || ".join(f"frame == {frame}" for frame in PICKS)
    new = f"""            const bool selected = {predicate};
            std::vector<unsigned char> pixels;
            if (selected) pixels = capture.Read();"""
    if source.count(old) != 1:
        raise ValueError("capture instrumentation does not match worker")
    worker.write_text(source.replace(old, new))
    relative = "docs/superpowers/evidence/0025-feedback-diffusion/detail-layer/detail-layer-prototype.diff"
    original = subprocess.check_output(["git", "show", f"{args.before_ref}:{relative}"])
    (work / "original.diff").write_bytes(original)
    workers = {}
    for label in ("authored", "before", "fixed"):
        engine = base if label == "authored" else work / f"{label}-engine"
        if label != "authored":
            shutil.copytree(base, engine)
            patch = work / "original.diff" if label == "before" else repo / relative
            subprocess.run(["patch", "--batch", "-p1", "-i", str(patch)], cwd=engine,
                           check=True, stdin=subprocess.DEVNULL)
        build = work / f"{label}-build"
        with (work / f"{label}-build.log").open("w") as log:
            subprocess.run(["cmake", "-S", str(native), "-B", str(build),
                            f"-DPROJECTM_SOURCE={engine}", "-DCMAKE_BUILD_TYPE=Release"],
                           check=True, stdout=log, stderr=subprocess.STDOUT)
            subprocess.run(["cmake", "--build", str(build), "-j", "4"],
                           check=True, stdout=log, stderr=subprocess.STDOUT)
        executable = build / "preset-lab-worker"
        workers[label] = {"path": str(executable), "sha256": sha(executable)}
        print(f"Built {label}", flush=True)
    result = {"engine": asdict(identity), "before_ref": args.before_ref, "capture_frames": PICKS,
              "before_prototype_sha256": sha(work / "original.diff"),
              "fixed_prototype_sha256": sha(repo / relative),
              "capture_worker_source_sha256": sha(worker), "workers": workers}
    (work / "workers.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
