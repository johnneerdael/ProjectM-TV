"""Check sparse capture against full capture using identical frozen inputs."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from measure import REPO, signal
from preset_lab.models import EngineIdentity, JobSpec, PresetRecord
from preset_lab.worker import render_job
from screen import Config, sparse_render


def main():
    sparse = json.loads((HERE / "sparse-workers.json").read_text())
    indices = sparse["capture_frame_indices"]
    acid = "Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk"
    cases = [(acid, role, w, h, ref) for role in ["baseline", "reviewed"]
             for w, h, ref in [(1182, 665, (0, 0)), (2364, 1330, (1024, 768)),
                               (3840, 2160, (1024, 768))]]
    cases += [("$$$ Royal - Mashup (191).milk", "reviewed", 3840, 2160, (1024, 768)),
              ("Fed - quadratrail.milk", "reviewed", 3840, 2160, (1024, 768)),
              ("TonyMilkdrop - Rhythm Of My Life [Flexi - multiverse] --- Isosceles edit.milk",
               "reviewed", 2364, 1330, (1024, 768))]
    work = REPO / "build/diffusion/corpus-screen/sparse-proof"
    work.mkdir(parents=True, exist_ok=True)
    results = []
    for name, role, w, h, ref in cases:
        full = json.loads((HERE.parent / f"worker-{role}.json").read_text())
        item = sparse["workers"][role]
        assert item["identity"] == full["identity"]
        assert hashlib.sha256(Path(item["exe"]).read_bytes()).hexdigest() == item["worker_sha256"]
        config = Config(width=w, height=h, fps=30, warmup_seconds=4, measurement_seconds=12,
                        line_reference_width=ref[0], line_reference_height=ref[1])
        spec = JobSpec(PresetRecord(name, "", 0), "bass-0.30", signal(12), config,
                       EngineIdentity(**item["identity"]), REPO / "core/src/main/assets/presets",
                       REPO / "core/src/main/assets/textures", work)
        expected, actual, counter = {}, {}, 0
        def observe_full(frame):
            nonlocal counter
            if counter in indices:
                expected[counter] = hashlib.sha256(frame).hexdigest()
            counter += 1
        start = time.monotonic()
        baseline = render_job(Path(full["exe"]), spec, observe_full, 120)
        full_seconds = time.monotonic() - start
        def observe_sparse(frame, index):
            actual[index] = hashlib.sha256(frame).hexdigest()
        start = time.monotonic()
        sampled = sparse_render(Path(item["exe"]), spec, observe_sparse, 120, indices)
        row = {"preset": name, "role": role, "width": w, "height": h,
               "identity": item["identity"], "full_status": baseline.status,
               "sparse_status": sampled.status, "simulation_frames": counter,
               "capture_indices": indices, "expected_hashes": expected, "actual_hashes": actual,
               "byte_identical": expected == actual and len(actual) == len(indices),
               "full_seconds": full_seconds, "sparse_seconds": time.monotonic() - start}
        results.append(row)
        (HERE / "sparse-validation.json").write_text(json.dumps(results, indent=2) + "\n")
        print(name[:28], role, h, row["byte_identical"], round(row["sparse_seconds"], 2), flush=True)
        assert baseline.status == sampled.status == "success" and counter == 480 and row["byte_identical"], row
        for result in [baseline, sampled]:
            shutil.rmtree(result.diagnostics_path.parent)


if __name__ == "__main__":
    main()
