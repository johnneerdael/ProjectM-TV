"""Resumable paired corpus screen. No renders occur during init/status/export."""
import argparse
from dataclasses import asdict, dataclass
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tempfile
import threading
import time

import cv2
import numpy as np
from preset_lab.bass_screen import bass_signals
from preset_lab.cache import write_atomic
from preset_lab.identity import digest, file_digest
from preset_lab.inventory import inventory
from preset_lab.models import EngineIdentity, JobSpec, PresetRecord, RunConfig, WorkerResult
from preset_lab.worker import render_job, validate_job

REPO = Path(__file__).resolve().parents[5]
EVIDENCE = Path(__file__).resolve().parent
ROOT_EVIDENCE = EVIDENCE.parent
DEFAULT_WORK = REPO / "build/diffusion/corpus-screen/screen"
LUMA = np.array([.2126, .7152, .0722], dtype=np.float32)
SPARSE_WINDOWS = {4: [120, 150, 180, 210, 239], 12: [120, 210, 300, 390, 479]}
VERSION = "corpus-screen-v1"

@dataclass(frozen=True, slots=True)
class Config(RunConfig):
    line_reference_width: int = 0
    line_reference_height: int = 0

def first_keys(text):
    """Match native ParseLine: first SPACE/=, case-sensitive first occurrence."""
    values = {}
    for line in text.splitlines():
        positions = [n for n in (line.find(" "), line.find("=")) if n >= 0]
        if positions and min(positions) > 0:
            n = min(positions)
            values.setdefault(line[:n], line[n + 1:])
    return values

def get_code(values, prefix):
    lines = []
    for i in range(1, 100000):
        key = f"{prefix}_{i}"
        if key not in values:
            break
        value = values[key]
        lines.append(value[1:] if value.startswith("`") else value)
    return "\n".join(lines)

def shader_expectations(values):
    def number(key, default):
        try:
            return int(values[key].strip())
        except (KeyError, ValueError):
            return default
    version = number("MILKDROP_PRESET_VERSION", 100)
    warp = comp = 0 if version < 200 else 2
    if version == 200:
        warp = comp = number("PSVERSION", 2)
    elif version > 200:
        warp, comp = number("PSVERSION_WARP", 2), number("PSVERSION_COMP", 2)
    return {"warp": warp > 0 and bool(get_code(values, "warp")), "composite": comp > 0}

def compare_metrics(run, authored, dark_floor):
    level, reference = run["luma"], authored["luma"]
    dark = reference < dark_floor
    return {"luma_ratio": None if dark else level / reference,
            "regularized_luma_ratio": (level + dark_floor) / (reference + dark_floor),
            "dark_authored": dark, "luma_absolute_error": abs(level - reference),
            "centre_absolute_error": [abs(a-b) for a, b in zip(run["centre_rgb"], authored["centre_rgb"])]}

class Samples:
    def __init__(self, config, indices, size=(1182, 665)):
        self.config, self.indices, self.size = config, set(indices), size
        self.frames, self.metrics, self.hashes = {}, {}, {}
        self.observed = 0
        self.stream_hash = hashlib.sha256()
    def observe(self, frame, index):
        self.observed += 1
        self.stream_hash.update(frame)
        if index not in self.indices:
            return
        h, w = frame.shape[:2]
        small = cv2.resize(frame, self.size, interpolation=cv2.INTER_AREA)
        values = small.astype(np.float32) / 255
        mx, mn = values.max(axis=2), values.min(axis=2)
        native_luma = frame.astype(np.float32) @ LUMA / 255
        centre = frame[int(h*.45):max(int(h*.55), 1), int(w*.45):max(int(w*.55), 1)]
        self.frames[index] = small
        self.hashes[index] = hashlib.sha256(frame).hexdigest()
        self.metrics[index] = {
            "luma": float(frame.reshape(-1, 3).mean(axis=0) @ LUMA / 255),
            "centre_rgb": (centre.reshape(-1, 3).mean(axis=0)/255).tolist(),
            "saturation": float(((mx-mn)/np.maximum(mx, 1/255)).mean()),
            "lap_native": float(cv2.Laplacian(native_luma, cv2.CV_32F).var()),
            "lap_1182": float(cv2.Laplacian(values @ LUMA, cv2.CV_32F).var())}
    def summary(self, indices):
        values = [self.metrics[i] for i in indices]
        return {key: np.mean([v[key] for v in values], axis=0).tolist() for key in values[0]}

def valid_sparse_manifest(manifest, simulation_frames, indices, observed):
    return (manifest.get("frames") == simulation_frames
            and manifest.get("captured_frames") == len(indices)
            and manifest.get("capture_frame_indices") == indices and observed == len(indices))

def sparse_render(worker, spec, observe, timeout, indices):
    simulation_frames = validate_job(spec, timeout)
    directory = Path(tempfile.mkdtemp(prefix="run-", dir=spec.work))
    diagnostic = directory / "stderr.log"
    job = {"schema_version": 1, "preset_path": str(spec.preset_root / spec.preset.path),
           "texture_root": str(spec.texture_root), "pcm_path": str(spec.pcm_path),
           "config": asdict(spec.config), "identity": asdict(spec.identity),
           "manifest_path": str(directory / "manifest.json"), "bands_path": str(directory / "bands.jsonl"),
           "capture_frame_indices": indices}
    write_atomic(directory / "job.json", job)
    expired = threading.Event()
    with diagnostic.open("wb") as log:
        process = subprocess.Popen([str(worker), "--job", str(directory / "job.json")],
                                   stdout=subprocess.PIPE, stderr=log,
                                   env=dict(os.environ, PRESET_LAB_SEED=str(spec.config.seed)))
        timer = threading.Timer(timeout, lambda: (expired.set(), process.kill()))
        timer.start()
        count = 0
        try:
            size = spec.config.width * spec.config.height * 3
            while True:
                data = process.stdout.read(size)
                if not data:
                    break
                if len(data) != size or count >= len(indices):
                    process.kill()
                    break
                observe(np.frombuffer(data, np.uint8).reshape(spec.config.height, spec.config.width, 3), indices[count])
                count += 1
            code = process.wait()
        finally:
            timer.cancel()
            if process.poll() is None:
                process.kill()
            process.wait()
            process.stdout.close()
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    okay = code == 0 and not expired.is_set() and manifest.get("status") == "success" and valid_sparse_manifest(manifest, simulation_frames, indices, count)
    manifest.update(status="success" if okay else "timeout" if expired.is_set() else "failed",
                    exit_code=code, observed_frames=count, job_directory=str(directory))
    return WorkerResult(manifest["status"], manifest, diagnostic)

class Store:
    def __init__(self, path, manifest):
        path.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path / "screen.sqlite")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)")
        self.db.execute("CREATE TABLE IF NOT EXISTS jobs (key TEXT PRIMARY KEY, payload TEXT)")
        serialized = json.dumps(manifest, sort_keys=True, allow_nan=False)
        old = self.db.execute("SELECT value FROM metadata WHERE key='manifest'").fetchone()
        if old and old[0] != serialized:
            self.db.close()
            raise ValueError("Frozen manifest differs; use another work directory")
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO metadata VALUES ('manifest', ?)", (serialized,))
        write_atomic(path / "manifest.json", manifest)
    def get(self, key):
        row = self.db.execute("SELECT payload FROM jobs WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else None
    def put(self, key, value):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO jobs VALUES (?, ?)", (key, json.dumps(value, sort_keys=True, allow_nan=False)))
    def invalidate_reference(self, reference_key):
        with self.db:
            for key,payload in self.db.execute("SELECT key,payload FROM jobs").fetchall():
                row=json.loads(payload)
                if row.get("reference_job_key")==reference_key:
                    row.pop("comparisons",None)
                    row["comparisons_invalidated"]="Authored reference regenerated with different selected hashes"
                    row["comparison_eligible"]=False
                    self.db.execute("UPDATE jobs SET payload=? WHERE key=?",(json.dumps(row,sort_keys=True,allow_nan=False),key))
    def close(self):
        self.db.close()

def disk_guard(work, minimum):
    if shutil.disk_usage(work).free < minimum:
        raise RuntimeError("Disk-free guard: stopped before starting/persisting another job")

def load_workers(protocol, path):
    frozen = {role: json.loads((ROOT_EVIDENCE / f"worker-{name}.json").read_text())
              for role, name in [("baseline", "baseline"), ("candidate", "reviewed")]}
    source = json.loads(path.read_text()) if protocol == "sparse" else {}
    workers = source.get("workers", {})
    result = {}
    for role, name in [("baseline", "baseline"), ("candidate", "reviewed")]:
        info = workers[name] if protocol == "sparse" else frozen[role]
        if info["identity"] != frozen[role]["identity"]:
            raise ValueError(f"{role} engine identity differs from frozen evidence")
        actual = file_digest(Path(info["exe"]))
        if info.get("worker_sha256", actual) != actual:
            raise ValueError("Sparse worker metadata is stale; wait for its rebuild")
        result[role] = dict(info, worker_sha256=actual)
    return result, source

def make_manifest(args):
    records, library = inventory(REPO / "core/src/main/assets/presets", REPO / "core/src/main/assets/presets.idx", REPO / "core/src/main/assets/textures")
    corpus = []
    for record in records:
        keys = first_keys((REPO / "core/src/main/assets/presets" / record.path).read_text(errors="replace"))
        corpus.append(dict(asdict(record), first_keys_sha256=digest(keys), shaders=shader_expectations(keys)))
    workers, metadata = load_workers(args.protocol, args.workers)
    return {"version": VERSION, "runner_sha256": file_digest(Path(__file__)), "protocol": args.protocol,
            "metrics_scope": "selected_frames_only; preliminary screen, not full-window means or validated acceptance",
            "windows": args.windows, "fps": 30, "warmup_seconds": 4, "seed": 12345,
            "dark_floor": args.dark_floor, "workers": workers, "sparse_metadata": metadata,
            "capture_windows": SPARSE_WINDOWS if args.protocol == "sparse" else {},
            "corpus": corpus, "library": library}

def diagnostics(result, expected, output):
    path = result.diagnostics_path
    maximum = 1024*1024
    length = path.stat().st_size
    full_hash = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(65536): full_hash.update(block)
        stream.seek(0)
        bounded = stream.read(maximum) if length <= maximum else stream.read(maximum//2)
        if length > maximum:
            stream.seek(-maximum//2,2)
            bounded += b"\n[LOG TRUNCATED]\n" + stream.read()
    text = bounded.decode(errors="replace")
    with gzip.open(output, "wb") as stream:
        stream.write(bounded)
    stages = {}
    for stage in ["warp", "composite"]:
        bad = any(line.startswith(f"[{stage.title()} Shader]") and ("error" in line.lower() or "fallback" in line.lower()) for line in text.splitlines())
        okay = f"Successfully compiled {stage} shader" in text
        stages[stage] = "failure_reported" if bad else "success_reported" if okay else "not_expected" if not expected[stage] else "unknown_no_confirmation"
    return {"stages": stages, "log": str(output), "log_bytes": length,
            "log_sha256": full_hash.hexdigest(), "log_truncated": length > maximum,
            "tail": text[-4096:]}

def run_one(args, manifest, record, profile, round_index, seconds, windows, indices):
    role, width, height, reference = profile
    worker_role = "candidate" if role.startswith("candidate") else "baseline"
    worker = manifest["workers"][worker_role]
    config = Config(width=width, height=height, fps=30, warmup_seconds=4, measurement_seconds=seconds,
                    seed=12345, line_reference_width=reference[0], line_reference_height=reference[1])
    identity = {"preset": record, "profile": role, "round": round_index, "config": asdict(config),
                "protocol": args.protocol, "indices": indices, "worker": worker["worker_sha256"]}
    key = digest(identity)
    sample = Samples(config, indices)
    jobs = args.work / "jobs"
    jobs.mkdir(exist_ok=True)
    signal_config = RunConfig(width=1920, height=1080, fps=30, warmup_seconds=4, measurement_seconds=seconds, seed=12345)
    signal_dir = args.work / f"signal-{seconds}s"
    marker = signal_dir / "signal.json"
    if not marker.exists():
        signals = bass_signals(signal_config, signal_dir)
        pcm = signals["bass-0.30"]
        write_atomic(marker, {"pcm": str(pcm), "sha256": file_digest(pcm), "config": asdict(signal_config)})
        for name, path in signals.items():
            if name != "bass-0.30": path.unlink()
    signal = json.loads(marker.read_text())
    if file_digest(Path(signal["pcm"])) != signal["sha256"]:
        raise ValueError("Frozen signal changed")
    disk_guard(args.work, args.minimum_free)
    spec = JobSpec(PresetRecord(record["path"], record["sha256"], record["weight_mb"]), "bass-0.30",
                   Path(signal["pcm"]), config, EngineIdentity(**worker["identity"]),
                   REPO / "core/src/main/assets/presets", REPO / "core/src/main/assets/textures", jobs)
    started = time.monotonic()
    if args.protocol == "sparse":
        result = sparse_render(Path(worker["exe"]), spec, sample.observe, args.timeout, indices)
    else:
        counter = 0
        def observe(frame):
            nonlocal counter
            sample.observe(frame, counter)
            counter += 1
        result = render_job(Path(worker["exe"]), spec, observe, args.timeout)
    diagnostic_dir = args.work / "diagnostics"
    diagnostic_dir.mkdir(exist_ok=True)
    info = diagnostics(result, record["shaders"], diagnostic_dir / f"{key}.log.gz")
    output = dict(identity, key=key, status=result.status, simulation_frames=round((4+seconds)*30),
                  observed_frames=sample.observed, capture_indices=indices,
                  hash_scope="captured_frames" if args.protocol == "sparse" else "all_simulation_frames",
                  stream_sha256=sample.stream_hash.hexdigest(), sample_hashes={str(k):v for k,v in sample.hashes.items()},
                  elapsed_seconds=time.monotonic()-started, audio=signal, diagnostics=info,
                  native_manifest=result.manifest, summaries={})
    if result.status == "success" and sample.indices <= sample.frames.keys():
        output["summaries"] = {str(window): sample.summary(picks) for window, picks in windows.items()}
    bands_path = Path(result.manifest["job_directory"]) / "bands.jsonl"
    output["selected_bands"] = {}
    if bands_path.exists():
        with bands_path.open() as stream:
            for index,line in enumerate(stream):
                if index in sample.indices: output["selected_bands"][index]=json.loads(line)
    output["transient_job_files_deleted_after_commit"] = True
    return key, output, sample.frames

def profile_plan():
    return [("authored",1182,665,(0,0)), ("authored_repeat",1182,665,(0,0)), ("candidate_authored",1182,665,(0,0)),
            ("baseline_cap",2364,1330,(1024,768)), ("candidate_cap",2364,1330,(1024,768)),
            ("baseline_native",3840,2160,(1024,768)), ("candidate_native",3840,2160,(1024,768))]

def job_key(args, manifest, record, profile, round_index, seconds, indices):
    role,w,h,ref = profile
    config=Config(width=w,height=h,fps=30,warmup_seconds=4,measurement_seconds=seconds,seed=12345,line_reference_width=ref[0],line_reference_height=ref[1])
    worker=manifest["workers"]["candidate" if role.startswith("candidate") else "baseline"]
    return digest({"preset":record,"profile":role,"round":round_index,"config":asdict(config),"protocol":args.protocol,"indices":indices,"worker":worker["worker_sha256"]})

def execute(args, manifest, store):
    requested = set(args.presets.read_text().splitlines()) if args.presets else None
    records = [r for r in manifest["corpus"] if requested is None or r["path"] in requested]
    if requested and requested - {r["path"] for r in records}: raise ValueError("Unknown preset in subset file")
    records = records[args.start:args.start+args.limit if args.limit is not None else None]
    stage = args.work / "current-reference"
    stage.mkdir(exist_ok=True)
    for record in records:
        if file_digest(REPO / "core/src/main/assets/presets" / record["path"]) != record["sha256"]:
            raise ValueError("Preset source changed since freeze")
        for round_index in ([args.repeat, args.repeat+1] if args.repeat_all else [args.repeat]):
            for seconds in ([12] if args.protocol == "sparse" else args.windows):
                windows = {w: SPARSE_WINDOWS[w] for w in args.windows} if args.protocol == "sparse" else {seconds: [120+round(i*(seconds*30-1)/4) for i in range(5)]}
                indices = sorted({i for picks in windows.values() for i in picks})
                profiles = profile_plan()
                keys = [job_key(args,manifest,record,p,round_index,seconds,indices) for p in profiles]
                if all(store.get(key) is not None for key in keys): continue
                cache = stage / (digest([record["sha256"], round_index, seconds, args.protocol])+".npz")
                authored = store.get(keys[0])
                frames = dict(np.load(cache)) if cache.exists() else None
                if frames is not None: frames={int(k):v for k,v in frames.items()}
                for profile,key in zip(profiles,keys):
                    saved = store.get(key)
                    if saved is not None and not (profile[0]=="authored" and frames is None): continue
                    disk_guard(args.work,args.minimum_free)
                    key,result,captured = run_one(args,manifest,record,profile,round_index,seconds,windows,indices)
                    if profile[0]=="authored":
                        if saved and saved["sample_hashes"]!=result["sample_hashes"]:
                            result["reference_regeneration_changed"]=True
                            store.invalidate_reference(key)
                        if saved and saved.get("reference_regeneration_changed"):
                            result["reference_regeneration_changed"]=True
                        authored=result
                        frames=captured
                        with tempfile.NamedTemporaryFile(dir=stage,suffix=".tmp",delete=False) as stream:
                            np.savez_compressed(stream,**{str(k):v for k,v in frames.items()})
                            temporary=Path(stream.name)
                        os.replace(temporary,cache)
                    elif profile[0] in ["authored_repeat","candidate_authored"]:
                        result["authored_repeat_same_sample_hashes" if profile[0]=="authored_repeat" else "candidate_off_same_sample_hashes"]=bool(authored and authored["sample_hashes"]==result["sample_hashes"])
                    result["reference_job_key"]=authored["key"] if authored else None
                    result["comparison_eligible"]=bool(authored and not authored.get("reference_regeneration_changed"))
                    if authored and result["status"]=="success" and authored["status"]=="success" and result["comparison_eligible"]:
                        result["comparisons"]={}
                        for window,picks in windows.items():
                            comparison=compare_metrics(result["summaries"][str(window)],authored["summaries"][str(window)],args.dark_floor)
                            comparison["img_err"]=float(np.mean([np.abs(captured[i].astype(np.float32)-frames[i].astype(np.float32)).mean()/255 for i in picks]))
                            result["comparisons"][str(window)]=comparison
                    disk_guard(args.work,args.minimum_free)
                    store.put(key,result)
                    shutil.rmtree(Path(result["native_manifest"]["job_directory"]),ignore_errors=True)
                    print(json.dumps({"preset":record["path"],"round":round_index,"profile":profile[0],"status":result["status"],"elapsed_seconds":round(result["elapsed_seconds"],2)}),flush=True)
                if all(store.get(key) is not None for key in keys): cache.unlink(missing_ok=True)

def export(store, path):
    with path.open("w") as output:
        for (payload,) in store.db.execute("SELECT payload FROM jobs ORDER BY key"):
            output.write(payload+"\n")

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=["init","run","status","export"])
    parser.add_argument("--protocol",choices=["sparse","full"],default="sparse")
    parser.add_argument("--workers",type=Path,default=EVIDENCE/"sparse-workers.json")
    parser.add_argument("--work",type=Path,default=DEFAULT_WORK)
    parser.add_argument("--windows",default="4,12")
    parser.add_argument("--presets",type=Path)
    parser.add_argument("--start",type=int,default=0)
    parser.add_argument("--limit",type=int)
    parser.add_argument("--repeat",type=int,default=0)
    parser.add_argument("--repeat-all",action="store_true",help="Run two complete seven-profile rounds; sample-hash repeat checks remain preliminary")
    parser.add_argument("--timeout",type=float,default=60)
    parser.add_argument("--minimum-free-gb",type=float,default=4)
    parser.add_argument("--dark-floor",type=float,default=.001)
    args=parser.parse_args()
    args.windows=sorted(set(map(int,args.windows.split(','))))
    if not set(args.windows)<={4,12} or not args.windows or args.dark_floor<=0 or args.minimum_free_gb<=0 or args.repeat<0 or args.start<0:
        parser.error("Invalid protocol/window/floor/range")
    args.minimum_free=int(args.minimum_free_gb*1024**3)
    args.work=args.work.resolve()
    if args.command in ["status","export"]:
        path=args.work/"screen.sqlite"
        if not path.exists(): parser.error("Screen database does not exist; initialize first")
        db=sqlite3.connect(path.as_uri()+"?mode=ro",uri=True)
        try:
            metadata=json.loads(db.execute("SELECT value FROM metadata WHERE key='manifest'").fetchone()[0])
            counts={}
            for (payload,) in db.execute("SELECT payload FROM jobs"):
                status=json.loads(payload).get("status","unknown");counts[status]=counts.get(status,0)+1
            if args.command=="export":
                target=args.work/"jobs.jsonl"
                with tempfile.NamedTemporaryFile(mode="w",dir=args.work,delete=False) as stream:
                    for (payload,) in db.execute("SELECT payload FROM jobs ORDER BY key"): stream.write(payload+"\n")
                    temporary=Path(stream.name)
                os.replace(temporary,target)
            print(json.dumps({"command":args.command,"protocol":metadata["protocol"],"presets":len(metadata["corpus"]),"stored_jobs":sum(counts.values()),"statuses":counts,"work":str(args.work)},indent=2))
        finally: db.close()
        return
    args.work.mkdir(parents=True,exist_ok=True)
    with (args.work/".runner.lock").open("w") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        manifest=make_manifest(args)
        store=Store(args.work,manifest)
        try:
            if args.command=="run": execute(args,manifest,store)
            elif args.command=="export": export(store,args.work/"jobs.jsonl")
            rows=store.db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
            print(json.dumps({"command":args.command,"presets":len(manifest["corpus"]),"stored_jobs":rows,"protocol":args.protocol,"work":str(args.work)},indent=2))
        finally: store.close()

if __name__=="__main__": main()
