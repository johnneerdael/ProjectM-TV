"""Build the full production patch series with the explicit warp sampler fix."""

import json
from dataclasses import asdict

from measure import ROOT
from preset_lab.build_worker import build_worker, prepare_engine


def main():
    work = ROOT / "build/follow-ups/lab-samplers-fixed"
    _, identity = prepare_engine(ROOT, work)
    exe = build_worker(ROOT, work)
    metadata = {"exe": str(exe), "identity": asdict(identity)}
    (ROOT / "build/follow-ups/worker-samplers-fixed.json").write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata), flush=True)


if __name__ == "__main__":
    main()
