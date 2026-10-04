"""Prove sparse readback matches saved full-readback frame bytes."""
import hashlib
import json
import subprocess
import sys
import threading
import time
from dataclasses import asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE))
from measure import Config, REPO, signal


def main():
    sparse = json.loads((HERE / "sparse-workers.json").read_text())
    set24 = json.loads((EVIDENCE / "set24-corrected-12s-report.json").read_text())["presets"]
    gradients = json.loads((EVIDENCE / "gradient-corrected-12s-report.json").read_text())["presets"]
    acid = "Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk"
    cases = [(acid, "baseline", label, set24[acid]) for label in ["authored", "baseline-1330", "baseline-2160"]]
    cases += [(acid, "reviewed", label, set24[acid]) for label in ["corrected-1330", "corrected-2160"]]
    royal = "$$$ Royal - Mashup (191).milk"
    fed = "Fed - quadratrail.milk"
    rhythm = "TonyMilkdrop - Rhythm Of My Life [Flexi - multiverse] --- Isosceles edit.milk"
    cases += [(royal, "reviewed", "corrected-2160", set24[royal]),
              (fed, "reviewed", "corrected-2160", gradients[fed]),
              (rhythm, "reviewed", "corrected-1330", set24[rhythm])]
    indices = sparse["capture_frame_indices"]
    scratch = REPO / "build/diffusion/corpus-screen/sparse-proof"
    scratch.mkdir(parents=True, exist_ok=True)
    results = []
    for number, (name, worker, label, original) in enumerate(cases):
        expected = json.loads((Path(original["runs"][label]["output"]) / "metrics.json").read_text())
        cfg = expected["config"]
        config = Config(width=cfg["width"], height=cfg["height"], fps=30, warmup_seconds=4,
                        measurement_seconds=12, line_reference_width=cfg["reference"][0],
                        line_reference_height=cfg["reference"][1])
        item = sparse["workers"][worker]
        assert hashlib.sha256(Path(item["exe"]).read_bytes()).hexdigest() == item["worker_sha256"]
        directory = scratch / f"case-{number}"
        directory.mkdir(exist_ok=True)
        job = {"schema_version": 1, "preset_path": str(REPO / "core/src/main/assets/presets" / name),
               "texture_root": str(REPO / "core/src/main/assets/textures"), "pcm_path": str(signal(12)),
               "config": asdict(config), "identity": item["identity"],
               "capture_frame_indices": indices, "manifest_path": str(directory / "manifest.json"),
               "bands_path": str(directory / "bands.jsonl")}
        job_path = directory / "job.json"
        job_path.write_text(json.dumps(job))
        # Use the same evaluator seed environment as preset_lab.worker.render_job.
        import os
        env = dict(os.environ, PRESET_LAB_SEED=str(config.seed))
        start = time.monotonic()
        with (directory / "stderr.log").open("wb") as log:
            process = subprocess.Popen([item["exe"], "--job", str(job_path)], stdout=subprocess.PIPE,
                                       stderr=log, env=env)
            timer = threading.Timer(1800, process.kill)
            timer.start()
            hashes = []
            try:
                size = config.width * config.height * 3
                for index in indices:
                    data = process.stdout.read(size)
                    assert len(data) == size, f"incomplete capture at {index}"
                    hashes.append(hashlib.sha256(data).hexdigest())
                assert process.stdout.read(1) == b"", "unexpected captures"
                assert process.wait() == 0
            finally:
                timer.cancel()
                if process.poll() is None:
                    process.kill()
                process.wait()
                process.stdout.close()
        manifest = json.loads((directory / "manifest.json").read_text())
        assert manifest["frames"] == 480 and manifest["captured_frames"] == len(indices)
        assert manifest["capture_frame_indices"] == indices and manifest["gl_error_frames"] == 0
        matches = hashes == [expected["frame_hashes"][index] for index in indices]
        row = {"preset": name, "worker": worker, "label": label, "width": config.width,
               "height": config.height, "simulation_frames": 480, "captures": len(indices),
               "byte_identical_to_full_capture": matches, "elapsed_seconds": time.monotonic() - start,
               "diagnostics": str(directory / "stderr.log")}
        results.append(row)
        print(name[:30], label, "exact", matches, "seconds", round(row["elapsed_seconds"], 2), flush=True)
        (HERE / "sparse-validation.json").write_text(json.dumps(results, indent=2) + "\n")
        assert matches, row


if __name__ == "__main__":
    main()
