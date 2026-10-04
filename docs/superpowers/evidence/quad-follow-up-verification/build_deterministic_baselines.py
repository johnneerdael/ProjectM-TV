"""Build immutable before/after sampler workers using the corrected lab RNG."""

import json
import shutil
from dataclasses import asdict

from measure import ROOT
from preset_lab.build_worker import build_worker, prepare_engine


def main():
    work = ROOT / "build/follow-ups"
    repo = work / "repo-deterministic-baseline"
    patches = repo / "tools/projectm-patches"
    patches.mkdir(parents=True, exist_ok=True)
    for path in (ROOT / "tools/projectm-patches").glob("*.patch"):
        if int(path.name[:4]) <= 25:
            shutil.copyfile(path, patches / path.name)
    if not (repo / "third_party").exists():
        (repo / "third_party").symlink_to(work / "pristine-source", target_is_directory=True)
    for name, source in (("deterministic-baseline", repo), ("deterministic-samplers", ROOT)):
        target = work / ("lab-"+name)
        _, identity = prepare_engine(source, target)
        exe = build_worker(source, target)
        metadata = {"exe": str(exe), "identity": asdict(identity)}
        (work / ("worker-"+name+".json")).write_text(json.dumps(metadata, indent=2))
        print(name, json.dumps(metadata), flush=True)


if __name__ == "__main__":
    main()
