"""Streaming, resumable Mac baseline for every bundled preset.

Run with build/preset-lab-venv/bin/python; --pilot checks accepted controls,
--run schedules the entire immutable corpus. No raw full-size frames are saved.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import sys
import threading
import time
import unittest

import cv2
import numpy as np
from measure import ROOT, Config
from preset_lab.bass_screen import bass_signals
from preset_lab.identity import canonical_json, digest, file_digest
from preset_lab.models import EngineIdentity, JobSpec, PresetRecord
from preset_lab.worker import render_job

WORK = ROOT / "build/follow-ups/corpus-baseline"
PRESETS = ROOT / "core/src/main/assets/presets"
TEXTURES = ROOT / "core/src/main/assets/textures"
CONFIG = Config(width=2364, height=1330, fps=30, warmup_seconds=4,
                measurement_seconds=4, seed=12345,
                line_reference_width=1024, line_reference_height=768)
PICKS = (120, 180, 239)
CONTROLS = (
    "$$$ Royal - Mashup (191).milk",
    "suksma - ed geining hateops - Matrix Moral Infinite.milk",
    "A Remixed Digital Echasketch  Again 2 martin - no religion  + disco Fruits Machine + Raron + mstress + 8.milk",
)
LUMA = np.array([.2126, .7152, .0722], dtype=np.float32)
TERMINAL = {"success", "failed", "timeout", "nondeterministic"}
STOP = threading.Event()


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(canonical_json(value) + "\n")
    os.replace(temp, path)


def key_for(protocol_hash, record):
    return digest({"protocol_sha256": protocol_hash, "preset": record})


def read_cached(path, protocol_hash, record):
    if not path.is_file():
        return None
    try:
        row = json.loads(path.read_text())
        if (row.get("key") == key_for(protocol_hash, record)
                and row.get("protocol_sha256") == protocol_hash
                and row.get("preset") == record
                and row.get("status") in TERMINAL
                and row.get("payload_sha256") == digest({k: v for k, v in row.items() if k != "payload_sha256"})):
            return row
    except (OSError, ValueError, TypeError):
        pass
    return None


def save_record(path, value):
    row = dict(value)
    row["payload_sha256"] = digest(value)
    atomic(path, row)
    return row


def inventory():
    records = [{"path": p.relative_to(PRESETS).as_posix(), "sha256": file_digest(p),
                "size_bytes": p.stat().st_size}
               for p in sorted(PRESETS.rglob("*.milk"))]
    if len(records) != 9606:
        raise ValueError(f"expected entire 9606-preset corpus; found {len(records)}")
    return {"count": len(records), "presets": records, "corpus_sha256": digest(records)}


def setup():
    WORK.mkdir(parents=True, exist_ok=True)
    worker = json.loads((ROOT / "build/follow-ups/worker-deterministic-baseline.json").read_text())
    exe = Path(worker["exe"])
    if worker["identity"]["instrumentation_sha256"] != "254db5d7418da6162c8db449ed400df19e9b6391ba405c0d20a0e19c3a005ef8":
        raise ValueError("baseline must use accepted private deterministic RNG instrumentation")
    corpus = inventory()
    pcm = bass_signals(CONFIG, WORK / "signals")["bass-0.30"]
    texture_records = [(p.relative_to(TEXTURES).as_posix(), file_digest(p))
                       for p in sorted(TEXTURES.rglob("*")) if p.is_file() and p.name != ".DS_Store"]
    protocol = {
        "version": "mac-corpus-baseline-v1", "config": asdict(CONFIG),
        "corpus_sha256": corpus["corpus_sha256"], "worker": worker,
        "worker_executable_sha256": file_digest(exe), "texture_sha256": digest(texture_records),
        "texture_files": texture_records, "pcm_sha256": file_digest(pcm), "stimulus": "bass-0.30",
        "platform": {"system": platform.system(), "release": platform.release(),
                     "machine": platform.machine(), "python": platform.python_version(),
                     "numpy": np.__version__, "opencv": cv2.__version__},
        "runner_sha256": file_digest(Path(__file__)),
        "worker_api_sha256": file_digest(ROOT / "tools/preset-lab/src/preset_lab/worker.py"),
        "timeout_seconds_per_repeat": 600, "repeats": 2, "frames_per_repeat": 240,
        "hash_protocol": "SHA256 concatenated native RGB8 frames (all 240); individual SHA256 every native frame",
        "thumbnail_protocol": {"repeat": 1, "zero_based_frames": list(PICKS),
                               "size": [256, 144], "resize": "OpenCV INTER_AREA", "encoding": "lossless PNG"},
        "metric_protocol": {
            "measurement_window": "zero-based native frames 120..239 inclusive",
            "window_mean_thumbnail": "256x144 INTER_AREA RGB8 each measurement frame; normalized RGB/luma and mean absolute consecutive-frame difference",
            "sampled_native": "native RGB8 at frames 120,180,239; normalized RGB/luma, bright/black/clipped fractions",
            "sampled_thumbnail": "same three 256x144 RGB8 thumbnails; HSV saturation mean, luma spatial std, Laplacian variance, 8x8 RGB grid",
            "luma_definition": "dot(RGB/255,[0.2126,0.7152,0.0722]); encoded RGB weighted brightness, no transfer-function linearization",
            "limitations": "one seed, controlled stimulus and 8s Mac OpenGL run; not TV performance or universal musical behavior"},
    }
    protocol_hash = digest(protocol)
    for name, data in (("inventory.json", corpus), ("protocol.json", {"sha256": protocol_hash, **protocol})):
        path = WORK / name
        if path.exists() and canonical_json(json.loads(path.read_text())) != canonical_json(data):
            raise ValueError(f"immutable {name} differs; existing evidence must not be overwritten")
        if not path.exists():
            atomic(path, data)
    return worker, pcm, corpus, protocol_hash


def compact_text(path):
    """Retain generated text evidence losslessly, reducing corpus disk footprint."""
    if not path.exists():
        return None
    target = path.with_suffix(path.suffix + ".gz")
    with path.open("rb") as source, target.open("wb") as output:
        with gzip.GzipFile(fileobj=output, mode="wb", mtime=0) as zipped:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                zipped.write(chunk)
    path.unlink()
    return str(target.relative_to(WORK))


def run_repeat(record, repeat, worker, pcm, protocol_hash):
    key = key_for(protocol_hash, record)
    target = WORK / "runs" / key / f"repeat-{repeat}.json"
    cached = read_cached(target, protocol_hash, record)
    if cached is not None:
        return cached, True
    start = time.monotonic()
    row = {"key": key, "protocol_sha256": protocol_hash, "preset": record,
           "repeat": repeat, "status": "failed", "warnings": [], "frames_observed": 0}
    try:
        if file_digest(PRESETS / record["path"]) != record["sha256"]:
            raise ValueError("source preset changed after immutable inventory")
        spec = JobSpec(PresetRecord(record["path"], record["sha256"], 0), "bass-0.30", pcm, CONFIG,
                       EngineIdentity(**worker["identity"]), PRESETS, TEXTURES,
                       WORK / "jobs" / key / f"repeat-{repeat}")
        sha, hashes, sampled, thumbnails = hashlib.sha256(), [], [], []
        rgb_sum, luma_sum, motion_sum = np.zeros(3, dtype=np.float64), 0., 0.
        previous, measured, motion_count = None, 0, 0

        def observe(frame):
            nonlocal rgb_sum, luma_sum, motion_sum, previous, measured, motion_count
            index = row["frames_observed"]
            row["frames_observed"] += 1
            sha.update(frame)
            hashes.append(hashlib.sha256(frame).hexdigest())
            if index < 120:
                return
            small = cv2.resize(frame, (256, 144), interpolation=cv2.INTER_AREA)
            values = small.astype(np.float32) / 255
            rgb = values.mean(axis=(0, 1))
            rgb_sum += rgb
            luma_sum += float(rgb @ LUMA)
            measured += 1
            if previous is not None:
                motion_sum += float(np.abs(values - previous).mean())
                motion_count += 1
            previous = values
            if index not in PICKS:
                return
            native_rgb = frame.mean(axis=(0, 1)) / 255
            native_max = frame.max(axis=2)
            grey = values @ LUMA
            hsv = cv2.cvtColor(small, cv2.COLOR_RGB2HSV)
            sample = {"frame": index, "native_rgb_mean": native_rgb.tolist(),
                      "native_luma_mean": float(native_rgb @ LUMA),
                      "native_black_fraction": float((native_max <= 2).mean()),
                      "native_bright_fraction": float((native_max >= 230).mean()),
                      "native_clipped_fraction": float((native_max == 255).mean()),
                      "thumbnail_saturation_mean": float(hsv[:, :, 1].mean() / 255),
                      "thumbnail_luma_spatial_std": float(grey.std()),
                      "thumbnail_laplacian_variance": float(cv2.Laplacian(grey, cv2.CV_32F, ksize=3).var()),
                      "thumbnail_grid_8x8_rgb": cv2.resize(values, (8, 8), interpolation=cv2.INTER_AREA).round(6).tolist()}
            sampled.append(sample)
            if repeat == 1:
                path = WORK / "thumbnails" / key / f"frame-{index:03d}.png"
                path.parent.mkdir(parents=True, exist_ok=True)
                if not cv2.imwrite(str(path), cv2.cvtColor(small, cv2.COLOR_RGB2BGR)):
                    raise IOError("failed writing lossless thumbnail")
                thumbnails.append(str(path.relative_to(WORK)))

        result = render_job(Path(worker["exe"]), spec, observe, 600)
        log = result.diagnostics_path.read_text(errors="replace")
        row["warnings"] = sorted(set(line for line in log.splitlines() if any(term in line.lower()
                                      for term in ("warning", "failed", "unable", "could not", "error"))))
        row.update(status=result.status, sha256_all_frames=sha.hexdigest(), sha256_frames=hashes,
                   sampled_metrics=sampled, thumbnails=thumbnails,
                   window_mean_thumbnail={"count": measured, "rgb": (rgb_sum / max(1, measured)).tolist(),
                                          "luma": luma_sum / max(1, measured),
                                          "consecutive_frame_rgb_difference": motion_sum / max(1, motion_count),
                                          "motion_pairs": motion_count},
                   worker_manifest=result.manifest,
                   manifest_path=str((result.diagnostics_path.parent / "manifest.json").relative_to(WORK)),
                   stderr_gzip=compact_text(result.diagnostics_path),
                   bands_gzip=compact_text(Path(result.manifest["bands_path"])))
        # Validate the source again so mid-render mutations never qualify for reuse.
        if file_digest(PRESETS / record["path"]) != record["sha256"]:
            row.update(status="failed", error="source changed during render")
    except Exception as error:
        row.update(status="failed", error=f"{type(error).__name__}: {error}")
    row["elapsed_seconds"] = time.monotonic() - start
    return save_record(target, row), False


def classify_runs(runs):
    statuses = [r["status"] for r in runs]
    if "timeout" in statuses:
        return "timeout"
    if statuses != ["success", "success"]:
        return "failed"
    return "success" if runs[0]["sha256_all_frames"] == runs[1]["sha256_all_frames"] else "nondeterministic"


def run_preset(record, worker, pcm, protocol_hash):
    key = key_for(protocol_hash, record)
    target = WORK / "rows" / f"{key}.json"
    if file_digest(PRESETS / record["path"]) == record["sha256"]:
        cached = read_cached(target, protocol_hash, record)
        if cached is not None:
            return cached, 0
    runs, fresh = [], 0
    for repeat in (1, 2):
        if STOP.is_set():
            return None, fresh
        row, reused = run_repeat(record, repeat, worker, pcm, protocol_hash)
        runs.append(row)
        fresh += not reused
    row = {"key": key, "protocol_sha256": protocol_hash, "preset": record,
           "status": classify_runs(runs), "runs": [str((WORK / "runs" / key / f"repeat-{i}.json").relative_to(WORK)) for i in (1, 2)],
           "warnings": sorted(set(w for r in runs for w in r["warnings"])),
           "repeat_exact": runs[0].get("sha256_frames") == runs[1].get("sha256_frames") if all(r["status"] == "success" for r in runs) else None,
           "window_mean_thumbnail": runs[0].get("window_mean_thumbnail"),
           "sampled_metrics": runs[0].get("sampled_metrics"), "thumbnails": runs[0].get("thumbnails", []),
           "elapsed_render_seconds": sum(r["elapsed_seconds"] for r in runs)}
    return save_record(target, row), fresh


def run_scan(worker, pcm, corpus, protocol_hash, workers, pilot=False):
    records = corpus["presets"]
    if pilot:
        records = [next(r for r in records if r["path"] == name) for name in CONTROLS]
        accepted = json.loads(Path(__file__).with_name("preset-sets.json").read_text())
        for record in records:
            if accepted["preset_sha256"][record["path"]] != record["sha256"]:
                raise ValueError(f"accepted control source changed: {record['path']}")
    start, completed, fresh_runs = time.monotonic(), [], 0
    suffix = "pilot" if pilot else "progress"
    def snapshot(state):
        elapsed = time.monotonic() - start
        rate = fresh_runs / elapsed if elapsed else 0
        data = {"state": state, "pid": os.getpid(), "protocol_sha256": protocol_hash,
                "inventory_count": corpus["count"], "requested_presets": len(records),
                "terminal_presets": len(completed), "fresh_render_runs": fresh_runs,
                "statuses": dict(Counter(r["status"] for r in completed)),
                "warning_presets": sum(bool(r["warnings"]) for r in completed),
                "elapsed_seconds": elapsed, "fresh_render_runs_per_second": rate,
                "active_workers_limit": workers,
                "estimated_remaining_seconds_observed_throughput": ((len(records)-len(completed))*2/rate if rate else None),
                "rows_directory": "rows", "inventory_file": "inventory.json",
                "complete_coverage": len(completed) == len(records),
                "updated_unix_seconds": time.time()}
        atomic(WORK / f"{suffix}.json", data)
        return data
    print(f"starting {'pilot' if pilot else 'entire corpus'}: {len(records)} presets; {workers} concurrent presets", flush=True)
    snapshot("running")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending = {pool.submit(run_preset, r, worker, pcm, protocol_hash): r for r in records}
        for future in as_completed(pending):
            record = pending[future]
            try:
                row, fresh = future.result()
            except Exception as error:
                # Keep every preset in coverage even when the orchestration itself fails.
                key = key_for(protocol_hash, record)
                row = save_record(WORK / "rows" / f"{key}.json", {
                    "key": key, "protocol_sha256": protocol_hash, "preset": record,
                    "status": "failed", "warnings": [], "error": f"orchestration {type(error).__name__}: {error}"})
                fresh = 0
            fresh_runs += fresh
            if row is not None:
                completed.append(row)
                info = snapshot("cancelling" if STOP.is_set() else "running")
                print(f"{len(completed)}/{len(records)} {row['status']}: {record['path']} | elapsed={info['elapsed_seconds']:.1f}s renders/s={info['fresh_render_runs_per_second']:.4f}", flush=True)
            if STOP.is_set():
                for remaining in pending:
                    remaining.cancel()
                break
    info = snapshot("interrupted" if STOP.is_set() else "complete")
    atomic(WORK / f"{suffix}-index.json", {"protocol_sha256": protocol_hash,
           "requested_presets": len(records), "complete_coverage": info["complete_coverage"],
           "rows": [{"preset": r["preset"]["path"], "status": r["status"], "row": f"rows/{r['key']}.json"} for r in sorted(completed, key=lambda r: r["preset"]["path"])]})
    if pilot:
        canonical = ROOT / "build/follow-ups/verification/sampler-impact-private-rng/jobs"
        comparisons = []
        for row in completed:
            for repeat in (1, 2):
                prior_path = canonical / f"{row['preset']['path']}-q1330-deterministic-baseline-r{repeat}/metrics.json"
                prior = json.loads(prior_path.read_text())
                current = json.loads((WORK / row["runs"][repeat-1]).read_text())
                comparisons.append({"preset": row["preset"]["path"], "repeat": repeat,
                                    "canonical_metrics_path": str(prior_path),
                                    "canonical_full_stream_sha256": prior["sha256_all_frames"],
                                    "observed_full_stream_sha256": current.get("sha256_all_frames"),
                                    "exact": prior["sha256_all_frames"] == current.get("sha256_all_frames")})
        atomic(WORK / "pilot-results.json", {"protocol_sha256": protocol_hash, "rows": completed,
                                             "canonical_comparisons": comparisons, "progress": info})
        if not all(item["exact"] for item in comparisons):
            raise RuntimeError("pilot does not match canonical accepted baseline streams")
        if any(r["status"] != "success" or r["repeat_exact"] is not True for r in completed) or len(completed) != 3:
            raise RuntimeError("pilot did not produce three successful exact repeats")
    return info


class RunnerTests(unittest.TestCase):
    def test_immutable_protocol_json_roundtrip(self):
        value = {"texture_files": [("x.png", "abc")]}
        self.assertEqual(canonical_json(json.loads(canonical_json(value))), canonical_json(value))

    def test_resume_key_includes_protocol_and_preset_bytes(self):
        record = {"path": "x.milk", "sha256": "a", "size_bytes": 1}
        self.assertNotEqual(key_for("p1", record), key_for("p2", record))
        self.assertNotEqual(key_for("p1", record), key_for("p1", dict(record, sha256="b")))

    def test_corruption_and_stale_protocol_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory(dir=WORK) as directory:
            target = Path(directory) / "row.json"
            record = {"path": "x.milk", "sha256": "a", "size_bytes": 1}
            row = {"key": key_for("p1", record), "protocol_sha256": "p1", "preset": record, "status": "failed"}
            save_record(target, row)
            self.assertIsNotNone(read_cached(target, "p1", record))
            self.assertIsNone(read_cached(target, "p2", record))
            damaged = json.loads(target.read_text()); damaged["status"] = "success"
            atomic(target, damaged)
            self.assertIsNone(read_cached(target, "p1", record))

    def test_failures_and_repeat_drift_have_explicit_status(self):
        self.assertEqual(classify_runs([{"status": "timeout"}, {"status": "success"}]), "timeout")
        self.assertEqual(classify_runs([{"status": "failed"}, {"status": "success"}]), "failed")
        self.assertEqual(classify_runs([{"status": "success", "sha256_all_frames": "a"},
                                        {"status": "success", "sha256_all_frames": "b"}]), "nondeterministic")
        self.assertEqual(classify_runs([{"status": "success", "sha256_all_frames": "a"}] * 2), "success")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pilot", action="store_true")
    group.add_argument("--run", action="store_true")
    group.add_argument("--self-test", action="store_true")
    parser.add_argument("--workers", type=int, default=3, choices=(1, 2, 3))
    args = parser.parse_args()
    cv2.setNumThreads(1)
    WORK.mkdir(parents=True, exist_ok=True)
    if args.self_test:
        unittest.main(argv=[sys.argv[0]], exit=True)
        return
    # Exclusive scan lock prevents duplicate renderers from sharing row paths.
    import fcntl
    with (WORK / "scan.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for signum in (signal.SIGINT, signal.SIGTERM):
            signal.signal(signum, lambda *_: STOP.set())
        worker, pcm, corpus, protocol_hash = setup()
        print(canonical_json(run_scan(worker, pcm, corpus, protocol_hash, args.workers, args.pilot)), flush=True)


if __name__ == "__main__":
    main()
