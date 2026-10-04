"""Export actual deterministic preset before/after frames with immutable source hashes."""

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

from measure import ROOT


def main():
    work = ROOT / "build/follow-ups/verification/sampler-impact-private-rng"
    raw = json.loads((work / "raw.json").read_text())
    records = {(r["name"], r["key"], r["worker"], r["repeat"]): r for r in raw}
    summary = json.loads(Path(__file__).with_name("results-sampler-impact.json").read_text())
    names = sorted({r["name"] for r in summary["comparisons"] if not r["byte_identical"]})
    out = Path(__file__).parent / "proofs/sampler-presets"
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for name in names:
        slug = hashlib.sha256(name.encode()).hexdigest()[:12]
        for key in ("c665", "q1330", "q2160"):
            images, sources = [], []
            for worker in ("deterministic-baseline", "deterministic-samplers"):
                record = records[(name, key, worker, 1)]
                source = work / record["five_frames"]
                frame = np.load(source)["frames"][4]
                images.append(frame)
                sources.append({"worker": worker, "identity": record["identity"],
                                "source": str(source.relative_to(ROOT)),
                                "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                                "frame_index": 239, "normalized_frame_sha256": hashlib.sha256(frame).hexdigest(),
                                "full_frame_stream_sha256": record["sha256_all_frames"]})
            panels = []
            for label, frame in zip(("Before: named sampler overwritten", "After: requested sampler retained"), images):
                panel = np.full((731, 1182, 3), 255, dtype=np.uint8)
                cv2.putText(panel, label, (18, 27), cv2.FONT_HERSHEY_SIMPLEX, .7, (30, 30, 30), 2)
                cv2.putText(panel, f"{key}, t=8.0 s; normalized 1182x665", (18, 53), cv2.FONT_HERSHEY_SIMPLEX, .6, (30, 30, 30), 1)
                panel[66:] = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                panels.append(panel)
            target = out / f"{slug}-{key}.png"
            cv2.imwrite(str(target), np.hstack(panels))
            delta = float(np.abs(images[0].astype(np.float32)-images[1].astype(np.float32)).mean()/255)
            manifest.append({"name": name, "key": key, "image": target.name,
                             "image_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                             "direct_change_img_err": delta, "sources": sources,
                             "limit": "Direct semantic correction comparison; does not alone prove authored fidelity."})
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print("Exported", len(manifest), "actual preset comparison images")


if __name__ == "__main__":
    main()
