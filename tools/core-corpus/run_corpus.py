#!/usr/bin/env python3
"""Resumable actual Android Core corpus oracle. init/status/summary never render."""
from __future__ import annotations

import argparse
from contextlib import closing, contextmanager
from dataclasses import asdict
import fcntl
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "tools/preset-lab/src"))
from preset_lab.identity import canonical_json, digest, file_digest as file_hash
from preset_lab.inventory import inventory, valid_filename

PROTOCOL = "projectmtv-core-corpus-v1"
BASELINE = "5681852f9497f320e57b8a5dd40c076d0f5a6b18"
PUBLISHED_AAR = "4c960385cd0afb7007ed08f99e0e04836c243f950e61f3e6e5dc4d9e77c8a440"
CANDIDATE_PATCH_SHA = "44381ce5cd09e605e4393bd5b2de3fe9273d59b916e0f5bb96010107c8b18479"
WINDOWS = {4: [120, 150, 180, 210, 239], 12: [120, 210, 300, 390, 479]}
CAPTURES = sorted(set(WINDOWS[4] + WINDOWS[12]))
PROFILES = [("authored", "baseline", 1182, 665, 0, 0),
            ("authored_repeat", "baseline", 1182, 665, 0, 0),
            ("candidate_authored", "candidate", 1182, 665, 0, 0),
            ("baseline_cap", "baseline", 2364, 1330, 1024, 768),
            ("candidate_cap", "candidate", 2364, 1330, 1024, 768),
            ("baseline_native", "baseline", 3840, 2160, 1024, 768),
            ("candidate_native", "candidate", 3840, 2160, 1024, 768)]
SUMMARY_SOURCE = REPO / "docs/superpowers/evidence/0025-feedback-diffusion/corpus-screen/summarize_screen.py"


def atomic_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def write_json(path, value):
    atomic_bytes(path, (canonical_json(value) + "\n").encode())


def to_unsigned_pcm(samples):
    import numpy as np
    return np.clip(np.rint(128 + 127 * samples), 0, 255).astype(np.uint8)


def signal():
    """Exact existing bass-.30 float32 generator, common 16-second conversion."""
    import numpy as np
    count = 16 * 44100
    seconds = np.arange(count) / 44100
    carrier = sum(.04 * np.sin(2 * np.pi * f * seconds) for f in (80, 440, 5000))
    spectrum = np.fft.rfft(np.random.default_rng(12345).standard_normal(count))
    frequencies = np.fft.rfftfreq(count, 1 / 44100)
    spectrum[(frequencies < 20) | (frequencies > 250)] = 0
    bass = np.fft.irfft(spectrum, n=count)
    bass /= max(float(np.max(np.abs(bass))), 1e-12)
    relative = np.maximum(seconds - 4, 0) % 1
    envelope = np.minimum(relative / .01, 1) * np.exp(-relative / .12) * (seconds >= 4)
    floating = (carrier + .30 * envelope * bass).astype("<f4")
    return floating.tobytes(), to_unsigned_pcm(floating).tobytes()


def preset_prefix(name):
    if not valid_filename(name):
        raise ValueError("Unsafe preset filename")
    prefix = name.encode("utf-8")[:80].decode("utf-8", errors="ignore")
    if not prefix:
        raise ValueError("Empty preset prefix")
    return prefix


def validate_source_pair(baseline, candidate):
    if baseline["source_commit"] != BASELINE:
        raise ValueError("Baseline is not the published v2.2.1 source")
    for source in (baseline, candidate):
        if source.get("published_baseline_source_commit") != BASELINE or source.get("published_baseline_aar_sha256") != PUBLISHED_AAR:
            raise ValueError("Published baseline provenance mismatch")
    first, second = baseline["ordered_patches"], candidate["ordered_patches"]
    if len(first) != 24 or len(second) != 25 or first != second[:24]:
        raise ValueError("Expected common patches 1–24 and candidate-only patch 25")
    for patches in (first, second):
        if [int(p["name"][:4]) for p in patches] != list(range(1, len(patches) + 1)):
            raise ValueError("Patch series is not consecutive")


def zip_hashes(path, prefix):
    with zipfile.ZipFile(path) as archive:
        return {name: hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist()
                if name.startswith(prefix) and not name.endswith("/")}


def freeze_workers(metadata_path, corpus, library, index_sha):
    metadata_path = Path(metadata_path).resolve()
    raw = json.loads(metadata_path.read_text())
    workers = raw.get("workers", raw)
    result = {}
    for role in ("baseline", "candidate"):
        record = workers[role]
        package = record["package"]
        if package != "nl.neerdael.projectmtv.corpus" + role:
            raise ValueError("Use only the owned corpusbaseline/corpuscandidate packages")
        def location(value):
            path = Path(value)
            return path.resolve() if path.is_absolute() else (metadata_path.parent / path).resolve()
        apk = location(record["apk_path"])
        source_path = location(record["source_identity"])
        source = json.loads(source_path.read_text())
        aar = Path(source["aar_path"])
        if not aar.is_absolute():
            aar = source_path.parent / aar
        if file_hash(aar) != source["aar_sha256"] or file_hash(apk) != record["apk_sha256"]:
            raise ValueError("APK/AAR artifact hash differs from metadata")
        assets = zip_hashes(aar, "assets/")
        apk_assets = zip_hashes(apk, "assets/")
        if assets != apk_assets or digest(assets) != source["packaged_assets_sha256"]:
            raise ValueError("Actual AAR and worker APK assets differ")
        expected = {"assets/presets/" + p["path"]: p["sha256"] for p in corpus}
        expected.update({"assets/textures/" + p["path"]: p["sha256"] for p in library["textures"]})
        expected["assets/presets.idx"] = index_sha
        if any(assets.get(name) != fingerprint for name, fingerprint in expected.items()):
            raise ValueError("Packaged assets differ from frozen host inventory")
        native = zip_hashes(aar, "jni/")
        apk_native = zip_hashes(apk, "lib/")
        if native != source["aar_native_sha256"] or any(apk_native.get(name.replace("jni/", "lib/", 1)) != sha for name, sha in native.items()):
            raise ValueError("APK does not contain the supplied actual Core native libraries")
        if source.get("backend") != "projectmtv-core-android-v1" or source.get("variant") != role or source.get("packaged_preset_count") != 9606:
            raise ValueError("Source metadata is not this instrumented actual Core corpus")
        result[role] = {"package": package, "apk_path": str(apk), "apk_sha256": record["apk_sha256"],
                        "source_identity_path": str(source_path), "source_identity_sha256": file_hash(source_path),
                        "source_identity": source, "aar_path": str(aar), "aar_sha256": source["aar_sha256"],
                        "native_sha256": native}
    validate_source_pair(result["baseline"]["source_identity"], result["candidate"]["source_identity"])
    candidate = result["candidate"]["source_identity"]
    if candidate["patch_series_sha256"] != CANDIDATE_PATCH_SHA:
        raise ValueError("Candidate patch-series identity differs from recovered patch 25")
    if raw.get("expected_candidate_source_commit") and candidate["source_commit"] != raw["expected_candidate_source_commit"]:
        raise ValueError("Candidate source commit differs from explicit pin")
    return result


def initialize(args):
    records, library = inventory(REPO / "core/src/main/assets/presets", REPO / "core/src/main/assets/presets.idx", REPO / "core/src/main/assets/textures")
    corpus = [asdict(record) for record in records]
    if len(corpus) != 9606:
        raise ValueError("Expected the complete 9606-preset corpus")
    index_sha = file_hash(REPO / "core/src/main/assets/presets.idx")
    workers = freeze_workers(args.metadata, corpus, library, index_sha)
    floating, unsigned = signal()
    manifest = {"schema_version": 1, "protocol": PROTOCOL, "oracle": "actual Android ProjectM TV Core AAR via production JNI",
                "runner_sha256": file_hash(Path(__file__)), "summary_sha256": file_hash(SUMMARY_SOURCE),
                "device": args.device, "adb_port": args.adb_port,
                "namespace": "projectmtv_core_corpus_" + digest(str(args.work.resolve()))[:16],
                "workers": workers, "corpus": corpus, "library": library, "index_sha256": index_sha,
                "windows": [4, 12], "capture_windows": {str(k): v for k, v in WINDOWS.items()},
                "rounds": [0, 1], "frames": 480, "fps": 30, "seed": 12345, "dark_floor": .001,
                "profiles": PROFILES, "clock": "frame / 30.0 (not (frame + 1) / 30)",
                "metrics_scope": "five selected frames per 4/12-second window under one common 16-second unsigned-8 PCM signal; not whole-window means",
                "audio_delivery": "1470 unsigned bytes per frame through production ProjectMJNI.addWaveform; core retains latest 512",
                "pcm": {"float32_sha256": hashlib.sha256(floating).hexdigest(), "uint8_sha256": hashlib.sha256(unsigned).hexdigest(),
                        "bytes": len(unsigned), "conversion": "clip(rint(128 + 127 * float32_samples), 0, 255).astype(uint8)",
                        "generator": "bass-.30, seed 12345, 4s warmup +12s measurement, 44100Hz mono"}}
    with Store(args.work, manifest):
        for name, data in (("bass-.30.f32", floating), ("bass-.30.u8", unsigned)):
            path = args.work / name
            if path.exists() and file_hash(path) != hashlib.sha256(data).hexdigest():
                raise ValueError("Frozen PCM file changed")
            atomic_bytes(path, data)
    write_json(args.work / "manifest.json", manifest)
    return manifest


def planned_jobs(manifest, start=0, limit=None):
    manifest_hash = digest(manifest)
    for record in manifest["corpus"][start:start + limit if limit is not None else None]:
        for round_index in (0, 1):
            yield from group_jobs(record, round_index, manifest_hash)


def group_jobs(record, round_index, manifest_hash):
    for profile, role, width, height, rw, rh in PROFILES:
        job = {"preset": record, "profile": profile, "role": role, "round": round_index,
               "config": {"width": width, "height": height, "measurement_seconds": 12,
                          "referenceWidth": rw, "referenceHeight": rh}, "protocol": PROTOCOL}
        job["key"] = digest({"manifest": manifest_hash, "job": job})
        yield job


def should_execute(saved, profile, group_complete, has_reference, retry_failed):
    if saved is None or retry_failed and saved.get("status") != "success":
        return True
    return profile == "authored" and saved.get("status") == "success" and not group_complete and not has_reference


def request_for(manifest, job):
    package = manifest["workers"][job["role"]]["package"]
    directory = f"/data/user/0/{package}/files/jobs/{manifest['namespace']}/{job['key']}"
    config = job["config"]
    return {"preset": job["preset"]["path"], "seed": 12345, "referenceWidth": config["referenceWidth"],
            "referenceHeight": config["referenceHeight"], "width": config["width"], "height": config["height"],
            "pcmPath": directory + "/audio.u8", "outputDir": directory + "/output",
            "instrumented": True, "expectedPresetCount": len(manifest["corpus"])}


class Store:
    def __init__(self, work, manifest):
        Path(work).mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(Path(work) / "screen.sqlite")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)")
        self.db.execute("CREATE TABLE IF NOT EXISTS jobs (key TEXT PRIMARY KEY, payload TEXT)")
        frozen = canonical_json(manifest)
        old = self.db.execute("SELECT value FROM metadata WHERE key='manifest'").fetchone()
        if old and old[0] != frozen:
            self.db.close()
            raise ValueError("Frozen manifest differs; use a new work directory")
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO metadata VALUES ('manifest', ?)", (frozen,))
    def __enter__(self):
        return self
    def __exit__(self, *exc):
        self.db.close()
    def get(self, key):
        row = self.db.execute("SELECT payload FROM jobs WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else None
    def put(self, key, payload):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO jobs VALUES (?, ?)", (key, canonical_json(payload)))
    def invalidate_reference(self, key):
        with self.db:
            for stored_key, payload in self.db.execute("SELECT key,payload FROM jobs").fetchall():
                job = json.loads(payload)
                if job.get("reference_job_key") == key:
                    job.pop("comparisons", None)
                    job["comparison_eligible"] = False
                    job["comparisons_invalidated"] = "Actual Core authored reference regenerated with different sampled hashes"
                    self.db.execute("UPDATE jobs SET payload=? WHERE key=?", (canonical_json(job), stored_key))


def read_frozen(work):
    path = (Path(work) / "screen.sqlite").resolve()
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
        row = db.execute("SELECT value FROM metadata WHERE key='manifest'").fetchone()
        if row is None:
            raise ValueError("Initialize this corpus work directory first")
        manifest = json.loads(row[0])
        if manifest.get("protocol") != PROTOCOL:
            raise ValueError("This directory is not the actual Android Core oracle")
        return manifest


def status(work):
    manifest = read_frozen(work)
    path = (Path(work) / "screen.sqlite").resolve()
    counts, covered = {}, set()
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
        for (payload,) in db.execute("SELECT payload FROM jobs"):
            job = json.loads(payload)
            state = job.get("status", "unknown")
            counts[state] = counts.get(state, 0) + 1
            covered.add(job.get("preset", {}).get("path"))
    return {"protocol": PROTOCOL, "corpus_presets": len(manifest["corpus"]), "covered_presets": len(covered),
            "expected_jobs": len(manifest["corpus"]) * 14, "stored_jobs": sum(counts.values()), "statuses": counts,
            "device": manifest.get("device"), "clock": manifest.get("clock")}


def remote_command(arguments):
    return " ".join(shlex.quote(str(arg)) for arg in arguments)


class Adb:
    def __init__(self, device, port, timeout=60):
        self.prefix = ["adb", "-P", str(port), "-s", device]
        self.timeout = timeout
    def call(self, *arguments, timeout=None, check=True, stdout=None):
        return subprocess.run(self.prefix + list(map(str, arguments)), check=check, timeout=timeout or self.timeout,
                              stdout=stdout if stdout is not None else subprocess.PIPE, stderr=subprocess.PIPE)
    def shell(self, *arguments, check=True, timeout=None):
        result = self.call("shell", remote_command(arguments), check=check, timeout=timeout)
        return result.stdout.decode("utf-8", errors="replace").strip()
    def exists(self, *arguments):
        return self.call("shell", remote_command(arguments), check=False).returncode == 0


def require_awake(adb):
    power = adb.shell("dumpsys", "power")
    if not re.search(r"\bmWakefulness=Awake\b", power) or "mInteractive=false" in power:
        raise RuntimeError("Device is not confirmed awake; wake it manually before starting the oracle")


@contextmanager
def session_lock(device, port):
    # One user-wide lock also covers runners launched from different worktrees.
    path = Path.home() / ".cache/projectmtv-core-corpus" / ("tv-session-" + digest([device, port])[:16] + ".lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("Another actual-Core runner holds this device session") from error
        yield


def restore_session(adb, workers, previous_prefix):
    errors = []
    commands = [("setprop", "debug.projectmtv.preset", previous_prefix)]
    commands.extend(("am", "force-stop", worker["package"]) for worker in workers.values())
    for command in commands:
        try:
            adb.shell(*command)
        except (OSError, subprocess.SubprocessError) as error:
            errors.append(str(error))
    return errors


def validate_manifest(value, frozen, job, request, request_hash):
    expected = {"protocol": PROTOCOL, "status": "ok", "applicationId": frozen["workers"][job["role"]]["package"],
                "requestSha256": request_hash, "pcmSha256": frozen["pcm"]["uint8_sha256"],
                "indexSha256": frozen["index_sha256"], "presetAssetSha256": job["preset"]["sha256"],
                "framesRendered": 480, "frameCountExpected": 480, "presetNameChecks": 480, "glErrorChecks": 480,
                "verifiedPresetName": request["preset"], "eligiblePresetCountBeforeFrame0": 1,
                "eligiblePresetCountAfterFrame479": 1, "presetChangeCounter": 1, "coreReleased": True,
                "eglDestroyed": True, "determinism": "instrumented-fixed-clock-seed",
                "bundledPresetCount": len(frozen["corpus"]), "forcedPresetPrefix": preset_prefix(request["preset"]), "job": request}
    for field, wanted in expected.items():
        if value.get(field) != wanted:
            raise ValueError(f"Actual Core manifest mismatch: {field}")
    captures = value.get("captures", [])
    if len(captures) != 8 or sorted(c.get("frame", -1) for c in captures) != CAPTURES:
        raise ValueError("Incomplete or duplicate actual Core capture set")
    for capture in captures:
        wanted_path = request["outputDir"] + f"/frame-{capture['frame']:03d}.png"
        # Android canonicalizes user-0 app files through /data/data in File APIs.
        owned_prefix = "/data/user/0/" + expected["applicationId"] + "/"
        allowed_paths = {wanted_path}
        if wanted_path.startswith(owned_prefix):
            allowed_paths.add("/data/data/" + expected["applicationId"] + "/" + wanted_path[len(owned_prefix):])
        if (capture.get("width"), capture.get("height")) != (request["width"], request["height"]) or capture.get("path") not in allowed_paths:
            raise ValueError("Capture dimensions/path differ from the owned request")
        if any(not isinstance(capture.get(key), str) or not re.fullmatch(r"[0-9a-f]{64}", capture[key]) for key in ("rgbSha256", "pngSha256")):
            raise ValueError("Capture is missing full RGB/PNG SHA256 identities")


def safe_extract(archive, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    seen = set()
    with tarfile.open(archive) as stream:
        members = stream.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            if (path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != "output"
                    or member.name in seen or not (member.isfile() or member.isdir())):
                raise ValueError("Unsafe member in owned job archive")
            seen.add(member.name)
        for member in members:
            target = destination / member.name
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with stream.extractfile(member) as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output)


def decode_capture(path, capture):
    import cv2
    import numpy as np
    if file_hash(path) != capture["pngSha256"]:
        raise ValueError("Captured PNG SHA256 differs from worker manifest")
    decoded = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if decoded is None or decoded.dtype != np.uint8 or decoded.shape[:2] != (capture["height"], capture["width"]) or decoded.ndim != 3 or decoded.shape[2] not in (3, 4):
        raise ValueError("Capture is not the declared full-size RGB(A)8 PNG")
    rgb = decoded[:, :, [2, 1, 0]].copy()
    if hashlib.sha256(rgb.tobytes()).hexdigest() != capture["rgbSha256"]:
        raise ValueError("Decoded top-down RGB SHA256 differs from worker")
    return rgb


def sample_summaries(frames):
    import cv2
    import numpy as np
    luma = np.array([.2126, .7152, .0722], dtype=np.float32)
    metrics = {}
    for index, rgb in frames.items():
        h, w = rgb.shape[:2]
        small = cv2.resize(rgb, (1182, 665), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        mx, mn = small.max(axis=2), small.min(axis=2)
        centre = rgb[int(h * .45):max(int(h * .55), int(h * .45) + 1),
                     int(w * .45):max(int(w * .55), int(w * .45) + 1)]
        metrics[index] = {"luma": float(rgb.reshape(-1, 3).mean(axis=0) @ luma / 255),
                          "centre_rgb": (centre.reshape(-1, 3).mean(axis=0) / 255).tolist(),
                          "saturation": float(((mx - mn) / np.maximum(mx, 1 / 255)).mean()),
                          "lap_native": float(cv2.Laplacian(rgb.astype(np.float32) @ luma / 255, cv2.CV_32F).var()),
                          "lap_1182": float(cv2.Laplacian(small @ luma, cv2.CV_32F).var())}
    return {str(window): {key: np.mean([metrics[i][key] for i in picks], axis=0).tolist() for key in metrics[picks[0]]}
            for window, picks in WINDOWS.items()}


def reduced_frames(frames):
    import cv2
    return {i: cv2.resize(frame, (1182, 665), interpolation=cv2.INTER_AREA) for i, frame in frames.items()}


def compare_samples(frames, authored_frames, summaries, authored_summaries, dark_floor):
    import numpy as np
    result = {}
    for window, picks in WINDOWS.items():
        run, authored = summaries[str(window)], authored_summaries[str(window)]
        dark = authored["luma"] < dark_floor
        result[str(window)] = {"dark_authored": dark, "luma_ratio": None if dark else run["luma"] / authored["luma"],
                               "luma_absolute_error": abs(run["luma"] - authored["luma"]),
                               "centre_absolute_error": [abs(a - b) for a, b in zip(run["centre_rgb"], authored["centre_rgb"])],
                               "img_err": float(np.mean([np.abs(frames[i].astype(np.float32) - authored_frames[i].astype(np.float32)).mean() / 255 for i in picks]))}
    return result


def bounded_diagnostics(text):
    data = text.encode("utf-8", errors="replace")
    failure_lines = [line.lower() for line in text.splitlines() if "shader" in line.lower()
                     and any(term in line.lower() for term in ("error", "fallback", "failed"))]
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "tail": text[-8192:],
            "stages": {stage: "failure_reported" if any(stage in line or not any(name in line for name in ("warp", "composite")) for line in failure_lines)
                       else "unknown_no_confirmation" for stage in ("warp", "composite")}}


def run_one(adb, frozen, job, work, timeout):
    """Always fresh process. Return verified result; caller commits before capture cleanup."""
    package = frozen["workers"][job["role"]]["package"]
    request = request_for(frozen, job)
    private = str(PurePosixPath(request["pcmPath"]).parent)
    stage = "/data/local/tmp/" + frozen["namespace"] + "/" + job["key"]
    local = Path(work) / "transient" / job["key"]
    if local.exists():
        shutil.rmtree(local)
    local.mkdir(parents=True)
    request_data = (canonical_json(request) + "\n").encode()
    request_hash = hashlib.sha256(request_data).hexdigest()
    atomic_bytes(local / "request.json", request_data)
    result = dict(job, status="failed", request=request, request_sha256=request_hash, sample_hashes={}, summaries={},
                  capture_indices=CAPTURES, source_identity=frozen["workers"][job["role"]]["source_identity_sha256"],
                  native_sha256=frozen["workers"][job["role"]]["native_sha256"])
    started, diagnostic, frames = time.monotonic(), "", {}
    try:
        require_awake(adb)
        adb.shell("am", "force-stop", package)
        # Refuse symlinked namespace/parent paths before private staging or deletion.
        for path in (f"/data/user/0/{package}/files/jobs", f"/data/user/0/{package}/files/jobs/{frozen['namespace']}", private):
            if adb.exists("run-as", package, "test", "-L", path):
                raise ValueError("Owned private staging path is a symlink")
        if adb.exists("test", "-L", "/data/local/tmp/" + frozen["namespace"]) or adb.exists("test", "-L", stage):
            raise ValueError("Owned shell staging namespace is a symlink")
        adb.shell("run-as", package, "rm", "-rf", private)
        adb.shell("mkdir", "-p", stage)
        adb.call("push", local / "request.json", stage + "/request.json")
        adb.call("push", Path(work) / "bass-.30.u8", stage + "/audio.u8")
        adb.shell("run-as", package, "mkdir", "-p", private)
        adb.shell("run-as", package, "cp", stage + "/request.json", private + "/request.json")
        adb.shell("run-as", package, "cp", stage + "/audio.u8", private + "/audio.u8")
        adb.shell("setprop", "debug.projectmtv.preset", preset_prefix(request["preset"]))
        instrument = adb.call("shell", remote_command(["am", "instrument", "-w", "-e", "job", private + "/request.json",
                              package + "/nl.neerdael.projectmtv.corpus.CorpusInstrumentation"]), timeout=timeout, check=False)
        diagnostic = instrument.stdout.decode(errors="replace") + "\n" + instrument.stderr.decode(errors="replace")
        if instrument.returncode:
            raise ValueError(f"Instrumentation command exited {instrument.returncode}")
        with (local / "output.tar").open("wb") as output:
            adb.call("exec-out", "run-as", package, "tar", "cf", "-", "-C", private, "output", stdout=output)
        extracted = local / "extracted"
        safe_extract(local / "output.tar", extracted)
        native = json.loads((extracted / "output/manifest.json").read_text())
        result["native_manifest"] = native
        if native.get("pid"):
            logs = adb.call("logcat", "-d", "--pid", str(native["pid"]), "-v", "threadtime", check=False)
            diagnostic += "\n" + logs.stdout.decode(errors="replace")
        validate_manifest(native, frozen, job, request, request_hash)
        for capture in native["captures"]:
            frame = capture["frame"]
            frames[frame] = decode_capture(extracted / "output" / f"frame-{frame:03d}.png", capture)
        result.update(status="success", sample_hashes={str(c["frame"]): c["rgbSha256"] for c in native["captures"]},
                      summaries=sample_summaries(frames), observed_frames=8, simulation_frames=480,
                      hash_scope="eight_captured_frames_only")
        frames = reduced_frames(frames)
    except subprocess.TimeoutExpired as error:
        result.update(status="timeout", error=str(error))
        diagnostic += "\nActual Core host timeout"
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        result["error"] = str(error)
        diagnostic += "\n" + str(error)
    finally:
        result["elapsed_seconds"] = time.monotonic() - started
        result["diagnostics"] = bounded_diagnostics(diagnostic)
        log_path = Path(work) / "diagnostics" / (job["key"] + ".log.gz")
        atomic_bytes(log_path, gzip.compress(diagnostic.encode(), mtime=0))
        result["diagnostics"]["log"] = str(log_path)
        # Stop only the owned worker, even if its process timed out or crashed.
        try:
            adb.shell("am", "force-stop", package)
        except (OSError, subprocess.SubprocessError) as error:
            result.update(status="failed", cleanup_error=str(error))
    return result, frames, local


def cleanup_device_job(adb, frozen, job):
    request = request_for(frozen, job)
    package = frozen["workers"][job["role"]]["package"]
    private = str(PurePosixPath(request["pcmPath"]).parent)
    adb.shell("run-as", package, "rm", "-rf", private)
    adb.shell("rm", "-rf", "/data/local/tmp/" + frozen["namespace"] + "/" + job["key"])


def save_reference(path, frames):
    import numpy as np
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        np.savez_compressed(stream, **{str(i): frame for i, frame in frames.items()})
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def summary(work, json_path=None, csv_path=None):
    spec = importlib.util.spec_from_file_location("core_corpus_summary", SUMMARY_SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    frozen, jobs = module.read_snapshot(Path(work) / "screen.sqlite")
    if frozen.get("protocol") != PROTOCOL:
        raise ValueError("Cannot mix this actual Core oracle with desktop results")
    # Only measurement-window arithmetic is shared. Backend identity remains explicit.
    result = module.summarize(dict(frozen, protocol="sparse"), jobs, repeat_all=True)
    result["protocol"] = PROTOCOL
    result["provenance"]["frozen_manifest_sha256"] = digest(frozen)
    result["provenance"]["backend"] = frozen["oracle"]
    result["provenance"]["clock"] = frozen["clock"]
    module.write_reports(result, json_path, csv_path)
    return result


def checkpoint(work, store):
    write_json(Path(work) / "progress.json", status(work))
    with tempfile.NamedTemporaryFile(dir=work, delete=False) as stream:
        temporary = Path(stream.name)
        for (payload,) in store.db.execute("SELECT payload FROM jobs ORDER BY key"):
            stream.write((payload + "\n").encode())
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, Path(work) / "checkpoint-jobs.jsonl")
    summary(work, Path(work) / "summary.json", Path(work) / "presets.csv")


def run(args):
    import numpy as np
    frozen = read_frozen(args.work)
    if frozen["runner_sha256"] != file_hash(Path(__file__)) or frozen["summary_sha256"] != file_hash(SUMMARY_SOURCE):
        raise ValueError("Runner/summary changed since initialization; use a new work directory")
    if args.device != frozen["device"] or args.adb_port != frozen["adb_port"]:
        raise ValueError("Device/ADB server differs from frozen protocol")
    if file_hash(args.work / "bass-.30.u8") != frozen["pcm"]["uint8_sha256"] or file_hash(args.work / "bass-.30.f32") != frozen["pcm"]["float32_sha256"]:
        raise ValueError("Frozen common16 PCM changed")
    for worker in frozen["workers"].values():
        for path, sha in ((worker["apk_path"], worker["apk_sha256"]), (worker["aar_path"], worker["aar_sha256"]),
                          (worker["source_identity_path"], worker["source_identity_sha256"])):
            if file_hash(Path(path)) != sha:
                raise ValueError("Frozen actual Core artifact/source identity changed")
    adb = Adb(args.device, args.adb_port)
    keep = set(args.keep_presets.read_text().splitlines()) if args.keep_presets else set()
    with session_lock(args.device, args.adb_port), Store(args.work, frozen) as store:
        require_awake(adb)
        fingerprint = adb.shell("getprop", "ro.build.fingerprint")
        old = store.db.execute("SELECT value FROM metadata WHERE key='device_fingerprint'").fetchone()
        if old and old[0] != fingerprint:
            raise ValueError("Device firmware fingerprint differs from first actual Core job")
        with store.db:
            store.db.execute("INSERT OR IGNORE INTO metadata VALUES ('device_fingerprint', ?)", (fingerprint,))
        # Verify installed worker bytes; never install or touch release preferences here.
        for worker in frozen["workers"].values():
            package_path = adb.shell("pm", "path", worker["package"])
            paths = [line[8:] for line in package_path.splitlines() if line.startswith("package:")]
            if len(paths) != 1 or not paths[0].startswith("/data/app/"):
                raise ValueError("Expected one installed owned corpus APK")
            actual_sha = adb.shell("sha256sum", paths[0]).split()[0]
            if actual_sha != worker["apk_sha256"]:
                raise ValueError("Installed worker APK differs from frozen artifact")
        previous_prefix = adb.shell("getprop", "debug.projectmtv.preset")
        progress = status(args.work)
        covered_paths = {json.loads(row[0]).get("preset", {}).get("path") for row in store.db.execute("SELECT payload FROM jobs")}
        manifest_hash = digest(frozen)
        count = 0
        try:
            active_group, authored, reference_frames, group_complete = None, None, None, False
            for job in planned_jobs(frozen, args.start, args.limit):
                if args.max_jobs is not None and count >= args.max_jobs:
                    break
                group = (job["preset"]["sha256"], job["preset"]["path"], job["round"])
                reference_path = args.work / "references" / (digest(group) + ".npz")
                if group != active_group:
                    active_group, authored, reference_frames = group, None, None
                    existing = [store.get(item["key"]) for item in group_jobs(job["preset"], job["round"], manifest_hash)]
                    group_complete = all(item is not None for item in existing)
                    if reference_path.exists():
                        saved_authored = existing[0]
                        if saved_authored and file_hash(reference_path) == saved_authored.get("reference_cache_sha256"):
                            with np.load(reference_path, allow_pickle=False) as archive:
                                reference_frames = {int(i): archive[i] for i in archive.files}
                saved = store.get(job["key"])
                if not should_execute(saved, job["profile"], group_complete, reference_frames is not None, args.retry_failed):
                    if job["profile"] == "authored":
                        authored = saved
                    if job["profile"] == "candidate_native" and group_complete:
                        reference_path.unlink(missing_ok=True)
                    continue
                if shutil.disk_usage(args.work).free < args.minimum_free_gb * 1024 ** 3:
                    raise RuntimeError("Disk-free guard stopped before next actual Core job")
                result, frames, local = run_one(adb, frozen, job, args.work, args.timeout)
                if job["profile"] == "authored":
                    if saved and saved.get("sample_hashes") != result.get("sample_hashes"):
                        store.invalidate_reference(job["key"])
                        result["reference_regeneration_changed"] = True
                    if saved and saved.get("reference_regeneration_changed"):
                        result["reference_regeneration_changed"] = True
                    authored, reference_frames = result, frames if result["status"] == "success" else None
                    if reference_frames:
                        save_reference(reference_path, reference_frames)
                        result["reference_cache_sha256"] = file_hash(reference_path)
                result["reference_job_key"] = authored["key"] if authored else None
                result["comparison_eligible"] = bool(authored and authored["status"] == "success" and not authored.get("reference_regeneration_changed"))
                if result["status"] == "success" and result["comparison_eligible"] and reference_frames:
                    result["comparisons"] = compare_samples(frames, reference_frames, result["summaries"], authored["summaries"], frozen["dark_floor"])
                if job["profile"] in ("authored_repeat", "candidate_authored"):
                    result["authored_repeat_same_sample_hashes" if job["profile"] == "authored_repeat" else "candidate_off_same_sample_hashes"] = bool(authored and authored["sample_hashes"] == result["sample_hashes"])
                store.put(job["key"], result)  # FULL SQLite commit before removing owned captures.
                count += 1
                if saved:
                    previous_status = saved.get("status", "unknown")
                    progress["statuses"][previous_status] -= 1
                else:
                    progress["stored_jobs"] += 1
                progress["statuses"][result["status"]] = progress["statuses"].get(result["status"], 0) + 1
                covered_paths.add(job["preset"]["path"])
                progress["covered_presets"] = len(covered_paths)
                write_json(args.work / "progress.json", dict(progress, last_job={"key": job["key"], "preset": job["preset"]["path"], "profile": job["profile"], "round": job["round"], "status": result["status"]}))
                if args.keep_all_captures or job["preset"]["path"] in keep:
                    target = args.work / "retained" / job["key"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.move(str(local), target)
                else:
                    shutil.rmtree(local)
                cleanup_device_job(adb, frozen, job)
                if job["profile"] == "candidate_native":
                    reference_path.unlink(missing_ok=True)
                if count % 100 == 0:
                    checkpoint(args.work, store)
                print(canonical_json({"preset": job["preset"]["path"], "profile": job["profile"], "round": job["round"], "status": result["status"], "new_jobs": count}), flush=True)
        finally:
            # Restore shared debug property and stop only these two owned instrumentation apps.
            cleanup_errors = restore_session(adb, frozen["workers"], previous_prefix)
            checkpoint(args.work, store)
            if cleanup_errors:
                raise RuntimeError("Device cleanup could not complete: " + "; ".join(cleanup_errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "run", "status", "summary"))
    parser.add_argument("--work", type=Path, default=REPO / "build/core-corpus/screen")
    parser.add_argument("--metadata", type=Path, help="baseline/candidate actual AAR + APK metadata JSON (init only)")
    parser.add_argument("--device", default="192.168.51.53:5555")
    parser.add_argument("--adb-port", type=int, default=5038)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, help="Limit presets, each gets seven profiles and both complete rounds")
    parser.add_argument("--max-jobs", type=int, help="Stop after this many newly executed jobs; resume preserves frozen identities")
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--minimum-free-gb", type=float, default=4)
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--keep-presets", type=Path, help="Keep owned full-size captures for exact preset names in this file")
    parser.add_argument("--keep-all-captures", action="store_true")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()
    args.work = args.work.resolve()
    if args.start < 0 or args.limit is not None and args.limit < 0 or args.max_jobs is not None and args.max_jobs < 0 or args.timeout <= 0 or args.minimum_free_gb <= 0:
        parser.error("Invalid range/timeout/free-space controls")
    try:
        if args.command == "init":
            if not args.metadata:
                parser.error("init requires --metadata")
            initialize(args)
            print(json.dumps(status(args.work), indent=2))
        elif args.command == "run":
            run(args)
        elif args.command == "status":
            print(json.dumps(status(args.work), indent=2))
        else:
            result = summary(args.work, args.json or args.work / "summary.json", args.csv or args.work / "presets.csv")
            print(json.dumps({key: result[key] for key in ("protocol", "counts", "coverage", "metrics", "populations")}, indent=2))
    except (OSError, ValueError, RuntimeError, sqlite3.Error, subprocess.SubprocessError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
