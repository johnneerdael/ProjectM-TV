"""Build the isolated RGBA16F diffusion-target hypothesis control."""

import json
import shlex
import shutil
from dataclasses import asdict

from measure import ROOT
from preset_lab.build_worker import build_worker, prepare_engine


def main():
    work = ROOT / "build/follow-ups"
    repo = work / "repo-diffusion-float"
    patches = repo / "tools/projectm-patches"
    patches.mkdir(parents=True, exist_ok=True)
    source = work / "repo-diffusion-safe"
    for path in (source / "tools/projectm-patches").glob("*.patch"):
        shutil.copyfile(path, patches / path.name)
    shutil.copyfile(ROOT / "docs/superpowers/evidence/quad-follow-up-verification/feedback-float-target.patch",
                    patches / "0028-feedback-float-target.patch")
    third_party = repo / "third_party"
    pristine = work / "pristine-source"
    if third_party.is_symlink() and third_party.resolve() != pristine:
        third_party.unlink()
    if not third_party.exists():
        third_party.symlink_to(pristine, target_is_directory=True)
    build = work / "lab-diffusion-float"
    _, identity = prepare_engine(repo, build)
    exe = build_worker(repo, build)
    wrapper = work / "worker-diffusion-float-on.sh"
    wrapper.write_text(f"#!/bin/sh\nexport PMX_DIFF=1\nexec {shlex.quote(str(exe))} \"$@\"\n")
    wrapper.chmod(0o755)
    metadata = {"exe": str(wrapper), "identity": asdict(identity), "diagnostic_switches": {"PMX_DIFF": "1"}}
    (work / "worker-diffusion-float-on.json").write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata), flush=True)


if __name__ == "__main__":
    main()
