"""Preserve the exact PR14 control sets and named virtual-size regressions."""

import hashlib
import json
import subprocess
from pathlib import Path

from measure import ROOT


def main():
    commit = subprocess.check_output(["git", "rev-parse", "evidence/quad-lines"], cwd=ROOT, text=True).strip()
    sources = {}
    def read(relative):
        raw = subprocess.check_output(["git", "show", commit+":"+relative], cwd=ROOT)
        sources[relative] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)
    control = list(read("data/5-blur/blur.json")["rows"])
    capped = [name.removeprefix("cen-") for name in read("data/8-render-cap/render-cap-results.json")["per_preset"]]
    adverse = read("data/7-virtual-texsize/virtual-texsize-results.json")["worsened"]
    extra = ["ORB - Toffie Grider.milk", "suksma - penattrition - geiss crossfire shaders.milk"]
    all_names = sorted(set(control+capped+adverse+extra))
    hashes = {}
    for name in all_names:
        path = ROOT / "core/src/main/assets/presets" / name
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    result = {"evidence_commit": commit, "source_sha256": sources, "control18": control,
              "capped24": capped, "prior_virtual_size_regressions": adverse,
              "additional_cases": extra, "all": all_names, "preset_sha256": hashes}
    Path(__file__).with_name("preset-sets.json").write_text(json.dumps(result, indent=2))
    print("control", len(control), "capped", len(capped), "prior adverse", len(adverse), "union", len(all_names))


if __name__ == "__main__":
    main()
