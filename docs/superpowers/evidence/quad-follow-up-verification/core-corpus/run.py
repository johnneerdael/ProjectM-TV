"""Host runner for the dedicated projectm-tv:core instrumentation APK.

Use prepare, then pilot. A full scan needs the successful pilot report SHA
explicitly supplied after review. Never reuse direct-projectM evidence.
"""
import argparse
from collections import Counter
import fcntl
import gzip
import hashlib
import json
import os
import re
from pathlib import Path
import signal
import subprocess
import struct
import sys
import threading
import time
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[5]
WORK = ROOT / "build/follow-ups/core-corpus/measurements"
PACKAGE = "nl.neerdael.projectmtv.corecorpus"
COMPONENT = PACKAGE + "/nl.neerdael.projectm.corecorpus.CorpusInstrumentation"
REMOTE = "/data/user/0/" + PACKAGE + "/files/jobs"
LEGACY_REMOTE = "/sdcard/Android/data/" + PACKAGE + "/files/jobs"
TERMINAL = {"success", "failed", "timeout", "incorrect_current_preset", "nondeterministic"}
STOP = threading.Event()
CONTROLS = (
    "$$$ Royal - Mashup (191).milk",
    "suksma - ed geining hateops - Matrix Moral Infinite.milk",
    "A Remixed Digital Echasketch  Again 2 martin - no religion  + disco Fruits Machine + Raron + mstress + 8.milk",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(canonical(value) + "\n")
    os.replace(temporary, path)


def save_row(path, row):
    atomic(path, dict(row, payload_sha256=digest(row)))


def frame_picks(measurement_frames):
    if measurement_frames == 120:
        return [120, 150, 180, 210, 239]
    if measurement_frames == 360:
        return [120, 150, 180, 210, 239, 300, 390, 479]
    raise ValueError("measurement must be 120 or 360 frames")


def capture_indices(measurement_frames):
    result = [120, 121, 150, 151, 180, 181, 210, 211, 238, 239]
    return result + ([300, 301, 390, 391, 478, 479] if measurement_frames == 360 else [])


def job_key(protocol_hash, record, role, capture_mode, repeat, measurement_frames=360):
    return digest({"protocol_sha256": protocol_hash, "preset": record, "role": role,
                   "capture_mode": capture_mode, "repeat": repeat, "measurement_frames": measurement_frames})


def validate_device(serial):
    if serial not in ("192.168.51.53", "192.168.51.53:5555"):
        raise ValueError("only device 192.168.51.53 is authorized")
    return serial


def adb(serial, *args, timeout=120, allow_failure=False):
    validate_device(serial)
    result = subprocess.run(["adb", "-s", serial, *args], capture_output=True, timeout=timeout)
    if result.returncode and not allow_failure:
        raise RuntimeError(f"adb {args[0]} failed: {result.returncode}")
    return result


def extract_owned_tar(archive_path, destination):
    with tarfile.open(archive_path) as archive:
        members = archive.getmembers()
        for member in members:
            path = destination / member.name
            if (Path(member.name).is_absolute() or ".." in Path(member.name).parts
                    or not path.resolve().is_relative_to(destination.resolve())
                    or not (member.isfile() or member.isdir())):
                raise ValueError("unsafe/escaping/link member in owned job transfer")
        for member in members:
            path = destination / member.name
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source, path.open("wb") as output:
                    for chunk in iter(lambda: source.read(1024 * 1024), b""):
                        output.write(chunk)


def push_private(serial, source, relative):
    validate_device(serial)
    temporary = "/data/local/tmp/corecorpus-" + digest({"relative": relative, "sha256": file_hash(source)}) + ".tmp"
    # exec-in truncates binary stdin on this installed ADB; use the sync protocol.
    adb(serial, "push", str(source), temporary)
    adb(serial, "shell", "chmod", "0644", temporary)
    adb(serial, "shell", "run-as", PACKAGE, "cp", temporary, relative)
    adb(serial, "shell", "rm", temporary)


def pull_external(serial, remote, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    copied = adb(serial, "pull", remote, str(destination.parent), timeout=300, allow_failure=True)
    (destination.parent / "pull.log").write_bytes(copied.stdout + copied.stderr)
    if copied.returncode:
        raise RuntimeError("owned app-created external output pull failed; partials preserved")


def pull_private(serial, relative, destination):
    validate_device(serial)
    destination.mkdir(parents=True, exist_ok=True)
    archive_path = destination / "owned-transfer.tar"
    with archive_path.open("wb") as output:
        copied = subprocess.run(["adb", "-s", serial, "exec-out", "run-as", PACKAGE,
                                 "tar", "-cf", "-", "-C", relative, "."],
                                stdout=output, stderr=subprocess.PIPE, timeout=300)
    (destination / "transfer.log").write_bytes(copied.stderr)
    if copied.returncode:
        raise RuntimeError("owned private job pull failed; partial transfer preserved")
    extract_owned_tar(archive_path, destination)
    archive_path.unlink()


def cleanup_verified_job(serial, internal, external, row):
    warnings = []
    for label, arguments in (
        ("internal", ("shell", "run-as", PACKAGE, "rm", "-rf", internal)),
        ("external", ("shell", "rm", "-rf", external)),
    ):
        try:
            adb(serial, *arguments)
        except Exception as error:
            warnings.append(f"{label}: {type(error).__name__}: {error}")
    if warnings:
        row["cleanup_warning"] = warnings


def safe_member(directory, relative):
    path = directory / relative
    if not path.resolve().is_relative_to(directory.resolve()) or not path.is_file():
        raise ValueError(f"missing/unsafe retained file: {relative}")
    return path


def validate_result(job, result, frames, directory):
    for field in ("schema_version", "job_id", "protocol_sha256", "capture_mode", "capture_frames",
                  "width", "height", "fps", "seed"):
        if result.get(field) != job[field]:
            raise ValueError(f"result provenance mismatch: {field}")
    if result.get("status") != "success":
        return "failed"
    if result.get("core_sha256") != job["expected_core_sha256"]:
        raise ValueError("runtime core library provenance mismatch")
    if result.get("requested_preset_sha256") != job["preset_sha256"]:
        raise ValueError("packaged preset source provenance mismatch")
    if result.get("status") != "success":
        return "failed"
    trace = directory / "frames.jsonl"
    if not trace.is_file() or file_hash(trace) != result.get("frames_metadata_sha256"):
        raise ValueError("producer frame metadata trace checksum mismatch")
    expected = job["warmup_frames"] + job["measurement_frames"]
    if result.get("rendered_frames") != expected or len(frames) != expected:
        raise ValueError("incomplete rendered frame/name trace")
    if [entry.get("frame") for entry in frames] != list(range(expected)):
        raise ValueError("noncontiguous or duplicate frame trace")
    if result.get("eligible_count") != 1:
        raise ValueError("job did not isolate one eligible preset")
    if any(entry.get("preset_filename") != job["preset_filename"] for entry in frames):
        return "incorrect_current_preset"
    if any(entry.get("change_counter") != frames[0].get("change_counter") for entry in frames):
        return "incorrect_current_preset"
    selected = result.get("selected_files", [])
    if [entry.get("frame") for entry in selected] != job["capture_frames"]:
        raise ValueError("selected frame coverage mismatch")
    if job["capture_mode"] == "selected" and result.get("sha256_all_frames") is not None:
        raise ValueError("selected coverage cannot claim full stream hash")
    for event in frames:
        captured = job["capture_mode"] == "full" or event["frame"] in job["capture_frames"]
        if event.get("captured") != captured:
            raise ValueError("frame readback coverage differs from protocol")
        sha = event.get("sha256")
        if captured and (not isinstance(sha, str) or len(sha) != 64):
            raise ValueError("missing native frame checksum")
        if not captured and sha is not None:
            raise ValueError("unread native frame has invented checksum")
        if event.get("pcm_bytes") != 44100 // job["fps"]:
            raise ValueError("PCM frame block was truncated before production JNI")
    if job["capture_mode"] == "full" and len(result.get("sha256_all_frames", "")) != 64:
        raise ValueError("full mode lacks full stream checksum")
    for sample in selected:
        if sample["sha256"] != frames[sample["frame"]]["sha256"]:
            raise ValueError("selected/native trace checksum mismatch")
        if sample["bytes"] != job["width"] * job["height"] * 3:
            raise ValueError("native RGB bytes mismatch")
        if job.get("retain_native_frames"):
            path = safe_member(directory, sample["path"])
            if path.stat().st_size != sample["bytes"] or file_hash(path) != sample["sha256"]:
                raise ValueError("native retained bytes/checksum mismatch")
        elif sample.get("path"):
            raise ValueError("corpus mode unexpectedly retained native frame")
        if sample.get("thumbnail_path"):
            path = safe_member(directory, sample["thumbnail_path"])
            if path.stat().st_size != sample["thumbnail_bytes"] or file_hash(path) != sample["thumbnail_sha256"]:
                raise ValueError("thumbnail bytes/checksum mismatch")
            with path.open("rb") as stream:
                header = stream.read(24)
            if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
                raise ValueError("thumbnail is not lossless PNG")
            if len(header) != 24 or struct.unpack(">II", header[16:24]) != (256, 144):
                raise ValueError("thumbnail dimensions must be 256x144")
        elif not job.get("retain_native_frames"):
            raise ValueError("compact corpus result lacks thumbnail")
    return "success"


def read_frames(directory):
    plain = directory / "frames.jsonl"
    if plain.is_file():
        with plain.open() as stream:
            return [json.loads(line) for line in stream if line.strip()]
    zipped = directory / "frames.jsonl.gz"
    if zipped.is_file():
        with gzip.open(zipped, "rt") as stream:
            return [json.loads(line) for line in stream if line.strip()]
    return []


def compress_trace(path):
    target = path.with_suffix(path.suffix + ".gz")
    temporary = target.with_name(target.name + ".tmp")
    sha, size = hashlib.sha256(), 0
    with path.open("rb") as source, temporary.open("wb") as output:
        with gzip.GzipFile(fileobj=output, mode="wb", mtime=0, filename="") as zipped:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                sha.update(chunk); size += len(chunk); zipped.write(chunk)
    # Verify the retained gzip before replacing the original evidence.
    with gzip.open(temporary, "rb") as stream:
        restored = hashlib.file_digest(stream, "sha256").hexdigest()
    if restored != sha.hexdigest() or file_hash(path) != sha.hexdigest():
        raise ValueError("frame trace changed or compression checksum failed")
    os.replace(temporary, target)
    path.unlink()
    return {"path": target.name, "compressed_sha256": file_hash(target),
            "compressed_bytes": target.stat().st_size, "uncompressed_sha256": sha.hexdigest(),
            "uncompressed_bytes": size, "encoding": "gzip-lossless-jsonl"}


def deduplicate_repeat_pngs(first, second, work):
    if (first["status"] != "success" or second["status"] != "success"
            or first.get("selected_native_sha256") != second.get("selected_native_sha256")):
        return {"unique_thumbnail_files": 0, "shared_bytes": 0, "aliases": []}
    if any(first.get(field) != second.get(field) for field in ("protocol_sha256", "preset", "role", "measurement_frames")):
        raise ValueError("repeat thumbnail provenance differs")
    first_directory, second_directory = work / "jobs" / first["key"], work / "jobs" / second["key"]
    samples = {item["frame"]: item for item in first["result"]["selected_files"]}
    aliases, seen = [], set()
    for item in second["result"]["selected_files"]:
        previous = samples.get(item["frame"])
        if not previous or not previous.get("thumbnail_path") or not item.get("thumbnail_path"):
            continue
        source = safe_member(first_directory / "output", previous["thumbnail_path"])
        target = safe_member(second_directory / "output", item["thumbnail_path"])
        source_sha, target_sha = file_hash(source), file_hash(target)
        if source_sha != previous["thumbnail_sha256"] or target_sha != item["thumbnail_sha256"]:
            raise ValueError("repeat thumbnail checksum changed before linking")
        if source_sha != target_sha:
            # Equal native pixels do not require equal PNG encodings.
            continue
        if target in seen:
            continue
        seen.add(target)
        if not source.samefile(target):
            temporary = target.with_name(target.name + ".link.tmp")
            if temporary.exists():
                temporary.unlink()
            os.link(source, temporary)
            os.replace(temporary, target)
        aliases.append({"path": target.relative_to(second_directory).as_posix(),
                        "shared_with": source.relative_to(work).as_posix(), "sha256": target_sha,
                        "bytes": target.stat().st_size})
    metadata = {"unique_thumbnail_files": len(aliases), "shared_bytes": sum(item["bytes"] for item in aliases),
                "aliases": aliases}
    if second.get("thumbnail_deduplication") != metadata:
        second["thumbnail_deduplication"] = metadata
        second.pop("payload_sha256", None)
        save_row(second_directory / "row.json", second)
    return metadata


def read_cached(path, key, protocol_hash):
    if not path.is_file():
        return None
    try:
        row = json.loads(path.read_text())
        if (row.get("key") == key and row.get("protocol_sha256") == protocol_hash
                and row.get("status") in TERMINAL
                and row.get("payload_sha256") == digest({k: v for k, v in row.items() if k != "payload_sha256"})):
            for file in row.get("retained_files", []):
                target = path.parent / file["path"]
                if not target.resolve().is_relative_to(path.parent.resolve()) or file_hash(target) != file["sha256"]:
                    return None
            return row
    except (OSError, ValueError, TypeError):
        pass
    return None


def inventory():
    presets = ROOT / "core/src/main/assets/presets"
    records = [{"path": p.relative_to(presets).as_posix(), "sha256": file_hash(p), "bytes": p.stat().st_size}
               for p in sorted(presets.rglob("*.milk"))]
    if len(records) != 9606:
        raise ValueError(f"expected all 9606 presets, found {len(records)}")
    textures = ROOT / "core/src/main/assets/textures"
    texture_records = [{"path": p.relative_to(textures).as_posix(), "sha256": file_hash(p)}
                       for p in sorted(textures.rglob("*")) if p.is_file() and p.name != ".DS_Store"]
    return {"count": len(records), "presets": records, "corpus_sha256": digest(records),
            "textures": texture_records, "textures_sha256": digest(texture_records)}


def artifact(apk, role, corpus):
    with zipfile.ZipFile(apk) as archive:
        identity = json.loads(archive.read("assets/backend-identity.json"))
        if identity.get("variant") != role:
            raise ValueError("APK backend role mismatch")
        for key in ("source_commit", "ordered_patches", "instrumentation_sha256", "core_library_entry"):
            if not identity.get(key):
                raise ValueError(f"APK backend identity lacks {key}")
        if role == "baseline" and not identity["source_commit"].startswith("a59b4e5"):
            raise ValueError("baseline APK must contain actual a59b4e5 projectm-tv:core")
        core_sha = hashlib.sha256(archive.read(identity["core_library_entry"])).hexdigest()
        if identity.get("core_sha256") not in (None, core_sha):
            raise ValueError("APK embedded core digest mismatch")
        for records, prefix in ((corpus["presets"], "assets/presets/"), (corpus["textures"], "assets/textures/")):
            for record in records:
                if hashlib.sha256(archive.read(prefix + record["path"])).hexdigest() != record["sha256"]:
                    raise ValueError(f"APK asset differs from exact corpus: {record['path']}")
    return {"apk_path": str(apk.resolve()), "apk_sha256": file_hash(apk), "core_sha256": core_sha,
            "backend_identity": identity, "backend_identity_sha256": digest(identity)}


def prepare_pcm(destination):
    sys.path.insert(0, str(ROOT / "tools/preset-lab/src"))
    import numpy as np
    from preset_lab.bass_screen import bass_signals
    from preset_lab.models import RunConfig
    float_path = bass_signals(RunConfig(fps=30, warmup_seconds=4, measurement_seconds=12, seed=12345),
                              destination / "generation")["bass-0.30"]
    values = np.fromfile(float_path, dtype="<f4")
    long_path, short_path = destination / "pcm-480.u8", destination / "pcm-240.u8"
    np.clip(np.rint(128 + 127 * values), 0, 255).astype(np.uint8).tofile(long_path)
    short_path.write_bytes(long_path.read_bytes()[:240 * 1470])
    return {str(frames): {"path": str(path.resolve()), "sha256": file_hash(path), "bytes": path.stat().st_size}
            for frames, path in ((240, short_path), (480, long_path))}


def validate_observer_pair(baseline, candidate):
    first, second = baseline["backend_identity"], candidate["backend_identity"]
    for field in ("instrumentation_sha256", "harness_sources_sha256"):
        if not first.get(field) or first.get(field) != second.get(field):
            raise ValueError(f"baseline/candidate observer mismatch: {field}")


def prepare(args):
    validate_device(args.serial)
    corpus = inventory()
    roles = {role: artifact(path, role, corpus) for role, path in (("baseline", args.baseline_apk), ("candidate", args.candidate_apk))}
    validate_observer_pair(roles["baseline"], roles["candidate"])
    device = {key: adb(args.serial, "shell", "getprop", key).stdout.decode().strip()
              for key in ("ro.product.manufacturer", "ro.product.model", "ro.product.device", "ro.build.fingerprint", "ro.product.cpu.abi")}
    pcm = prepare_pcm(args.work / "signals")
    protocol = {"schema_version": 2, "backend": "production-projectm-tv-core-ProjectMJNI-EGL-GLES3",
                "device_serial": args.serial, "device": device, "roles": roles,
                "corpus_sha256": corpus["corpus_sha256"], "textures_sha256": corpus["textures_sha256"],
                "pcm": pcm, "pcm_protocol": "16s bass-0.30 float32, seed12345; clip(rint(128+127*x),0,255); short input is exact 8s byte prefix; full1470-byte JNI blocks",
                "config": {"width": 2364, "height": 1330, "fps": 30, "seed": 12345, "warmup_frames": 120,
                           "measurement_frames": 360, "capture_frames": capture_indices(360)},
                "transport": "ADB sync push to owned controlled /data/local/tmp + dedicated run-as cp private job/PCM; APK creates external output, normal ADB sync pull; no exec-in binary stdin",
                "capture_format": "native RGB8, bottom_to_top; GLES RGBA readback with alpha stripped before SHA256",
                "capture_hash_coverage": "corpus:selected frames only; full-readback pilot:every frame and concatenated native stream",
                "retention": "corpus256x144 lossless PNGs/compact sampled metrics; native files only selected pilot/proof jobs",
                "limitations": "One controlled signal/seed/GLES3 device; selected hashes do not represent unread frames; thumbnails are not historical1182 fidelity img_err; wrapper fallback/load warnings remain diagnostic evidence",
                "runner_sha256": file_hash(Path(__file__))}
    value = dict(protocol, sha256=digest(protocol))
    for name, data in (("inventory.json", corpus), ("protocol.json", value)):
        path = args.work / name
        if path.exists() and canonical(json.loads(path.read_text())) != canonical(data):
            raise ValueError(f"immutable {name} differs; select a new work directory")
        atomic(path, data)
    print(canonical({"protocol_sha256": value["sha256"], "presets": corpus["count"], "device": device}))


def load_inputs(work):
    protocol = json.loads((work / "protocol.json").read_text())
    if digest({k: v for k, v in protocol.items() if k != "sha256"}) != protocol["sha256"]:
        raise ValueError("immutable protocol checksum mismatch")
    if protocol.get("runner_sha256") != file_hash(Path(__file__)):
        raise ValueError("immutable runner changed; prepare a new protocol/work directory")
    corpus = json.loads((work / "inventory.json").read_text())
    if digest(corpus["presets"]) != corpus["corpus_sha256"] or corpus["corpus_sha256"] != protocol["corpus_sha256"]:
        raise ValueError("immutable corpus checksum mismatch")
    for role in protocol["roles"].values():
        if file_hash(role["apk_path"]) != role["apk_sha256"]:
            raise ValueError("immutable APK changed")
    for audio in protocol["pcm"].values():
        if file_hash(audio["path"]) != audio["sha256"]:
            raise ValueError("immutable PCM changed")
    return protocol, corpus


def require_awake(serial):
    power = adb(serial, "shell", "dumpsys", "power").stdout.decode(errors="replace")
    match = re.search(r"mWakefulness=(\w+)", power)
    if not match or match.group(1) != "Awake":
        raise RuntimeError("authorized TV is not awake; wait for user; no remote wake permitted")


def install_role(serial, role, work):
    require_awake(serial)
    adb(serial, "shell", "am", "force-stop", PACKAGE)
    # Preserve both legacy shell staging and private timeout partials before role clear.
    if adb(serial, "shell", "test", "-d", LEGACY_REMOTE, allow_failure=True).returncode == 0:
        recovery = work / "recovered-device" / ("legacy-" + str(time.time_ns()))
        recovery.mkdir(parents=True)
        pulled = adb(serial, "pull", LEGACY_REMOTE, str(recovery), timeout=300, allow_failure=True)
        (recovery / "pull.log").write_bytes(pulled.stdout + pulled.stderr)
        if pulled.returncode:
            raise RuntimeError("could not preserve prior legacy staging; refusing role clear")
    if adb(serial, "shell", "run-as", PACKAGE, "test", "-d", "files/jobs", allow_failure=True).returncode == 0:
        recovery = work / "recovered-device" / ("private-" + str(time.time_ns()))
        pull_private(serial, "files/jobs", recovery)
    adb(serial, "install", "-r", role["apk_path"], timeout=300)
    cleared = adb(serial, "shell", "pm", "clear", PACKAGE)
    if cleared.stdout.strip() != b"Success":
        raise RuntimeError("dedicated corecorpus data clear was not acknowledged")
    print(f"installed role with verified dedicated-package data clear: {role['backend_identity']['variant']}", flush=True)


def make_job(protocol, record, role, mode, repeat, measurement_frames):
    key = job_key(protocol["sha256"], record, role, mode, repeat, measurement_frames)
    remote = REMOTE + "/" + key
    remote_output = LEGACY_REMOTE + "/" + key + "/output"
    audio = protocol["pcm"][str(120 + measurement_frames)]
    return {"schema_version": 2, "job_id": key, "protocol_sha256": protocol["sha256"],
            "preset_filename": record["path"], "preset_sha256": record["sha256"],
            "width": 2364, "height": 1330, "fps": 30, "seed": 12345, "warmup_frames": 120,
            "measurement_frames": measurement_frames, "capture_mode": mode,
            "capture_frames": capture_indices(measurement_frames), "retain_native_frames": mode == "full",
            "pcm_uint8_path": remote + "/pcm.u8", "pcm_uint8_sha256": audio["sha256"],
            "output_directory": remote_output, "expected_core_sha256": protocol["roles"][role]["core_sha256"]}


def run_one(args, protocol, record, role, mode, repeat, measurement_frames, native=False):
    job = make_job(protocol, record, role, mode, repeat, measurement_frames)
    job["retain_native_frames"] = native
    # Retention flag affects proof artifacts but not rendering or selected hash identity.
    directory = args.work / "jobs" / job["job_id"]
    target = directory / "row.json"
    cached = read_cached(target, job["job_id"], protocol["sha256"])
    native_available = (cached is not None and cached.get("native_verified") is True
                        and all((directory / "output" / sample.get("path", "missing")).is_file()
                                for sample in cached.get("result", {}).get("selected_files", [])))
    if cached is not None and (not native or native_available):
        return cached
    require_awake(protocol["device_serial"])
    directory.mkdir(parents=True, exist_ok=True)
    atomic(directory / "job.json", job)
    start = time.monotonic()
    row = {"key": job["job_id"], "protocol_sha256": protocol["sha256"], "preset": record,
           "role": role, "repeat": repeat, "measurement_frames": measurement_frames, "capture_mode": mode,
           "status": "failed", "native_verified": False, "retained_files": []}
    try:
        if file_hash(ROOT / "core/src/main/assets/presets" / record["path"]) != record["sha256"]:
            raise ValueError("source preset changed after inventory")
        serial = protocol["device_serial"]
        remote = REMOTE + "/" + job["job_id"]
        adb(serial, "shell", "am", "force-stop", PACKAGE)
        # Delete only this dedicated job's staging path; never touch other apps/presets.
        relative = "files/jobs/" + job["job_id"]
        adb(serial, "shell", "run-as", PACKAGE, "rm", "-rf", relative)
        adb(serial, "shell", "run-as", PACKAGE, "mkdir", "-p", relative)
        push_private(serial, directory / "job.json", relative + "/job.json")
        audio = protocol["pcm"][str(120 + measurement_frames)]
        push_private(serial, audio["path"], relative + "/pcm.u8")
        process = adb(serial, "shell", "am", "instrument", "-w", "-e", "job", remote + "/job.json", COMPONENT,
                      timeout=args.timeout, allow_failure=True)
        (directory / "instrumentation.log").write_bytes(process.stdout + process.stderr)
        output = directory / "output"
        pull_external(serial, job["output_directory"], output)
        if not (output / "result.json").is_file():
            raise ValueError("missing atomic APK result; instrumentation failed or crashed")
        result = json.loads((output / "result.json").read_text())
        row["result"] = result
        frames = read_frames(output)
        row["status"] = validate_result(job, result, frames, output)
        row.update(result=result, selected_native_sha256={str(item["frame"]): item["sha256"] for item in result.get("selected_files", [])},
                   native_verified=native and row["status"] == "success")
        if process.returncode and row["status"] == "success":
            row.update(status="failed", error="instrumentation exited unsuccessfully despite result")
        adb(serial, "shell", "am", "force-stop", PACKAGE)
        # Host has pulled and verified all output; remove only owned remote scratch.
        cleanup_verified_job(serial, relative, LEGACY_REMOTE + "/" + job["job_id"], row)
    except subprocess.TimeoutExpired as error:
        row.update(status="timeout", error="instrumentation/ADB job timeout")
        captured = (error.output or b"") + (error.stderr or b"")
        (directory / "timeout-command.log").write_bytes(captured)
        adb(protocol["device_serial"], "shell", "am", "force-stop", PACKAGE, allow_failure=True)
        try:
            pull_external(protocol["device_serial"], job["output_directory"], directory / "output")
        except Exception as recovery_error:
            row["remote_partial_recovery_error"] = f"{type(recovery_error).__name__}: {recovery_error}"
    except Exception as error:
        row.update(status="failed", error=f"{type(error).__name__}: {error}")
    trace = directory / "output/frames.jsonl"
    if trace.is_file():
        metadata = compress_trace(trace)
        row["frame_trace"] = dict(metadata, path="output/" + metadata["path"])
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.name not in ("row.json", "row.json.tmp"):
            row["retained_files"].append({"path": path.relative_to(directory).as_posix(), "bytes": path.stat().st_size, "sha256": file_hash(path)})
    row["elapsed_seconds"] = time.monotonic() - start
    save_row(target, row)
    print(f"{role} {mode} repeat{repeat} {record['path']}: {row['status']} {row['elapsed_seconds']:.2f}s", flush=True)
    return row


def pilot(args, protocol, corpus):
    cases = [(CONTROLS[0],120), (CONTROLS[0],360), (CONTROLS[1],120), (CONTROLS[2],360)]
    checks = []
    for role, identity in protocol["roles"].items():
        install_role(protocol["device_serial"], identity, args.work)
        for name, duration in cases:
            record = next(record for record in corpus["presets"] if record["path"] == name)
            full = run_one(args, protocol, record, role, "full", 1, duration, native=True)
            selected = run_one(args, protocol, record, role, "selected", 1, duration, native=True)
            repeated = run_one(args, protocol, record, role, "selected", 2, duration, native=False)
            exact = (all(row["status"] == "success" for row in (full, selected, repeated))
                     and full.get("selected_native_sha256") == selected.get("selected_native_sha256") == repeated.get("selected_native_sha256"))
            check = {"role": role, "preset": record, "measurement_frames": duration, "full_vs_selected_exact": exact,
                     "full_key": full["key"], "selected_key": selected["key"], "repeat_key": repeated["key"]}
            checks.append(check)
            # Keep Royal native proofs, compact other full pilot jobs after byte verification.
            # Preserve their declared hashes and independently verified comparison result.
            if exact and name != CONTROLS[0]:
                directory = args.work / "jobs" / full["key"]
                discarded = []
                for sample in full["result"]["selected_files"]:
                    path = safe_member(directory / "output", sample["path"])
                    discarded.append({"path": str(path.relative_to(directory)), "sha256": sample["sha256"]})
                    path.unlink()
                names = {item["path"] for item in discarded}
                full["retained_files"] = [item for item in full["retained_files"] if item["path"] not in names]
                full["native_files_discarded_after_independent_verification"] = discarded
                full.pop("payload_sha256", None)
                save_row(directory / "row.json", full)
            atomic(args.work / "pilot-report.json", {"protocol_sha256": protocol["sha256"], "status": "running", "checks": checks})
    report = {"protocol_sha256": protocol["sha256"], "status": "ready_for_review" if len(checks) == 8 and all(c["full_vs_selected_exact"] for c in checks) else "failed",
              "checks": checks, "limitations": "Exact native selected-frame equivalence on eight core-backed cases only; unread frames have no hash in selected mode"}
    atomic(args.work / "pilot-report.json", report)
    if report["status"] != "ready_for_review":
        raise RuntimeError("core-backed selected-readback pilot failed")
    print(canonical(report), flush=True)


def scan(args, protocol, corpus):
    path = args.work / "pilot-report.json"
    report = json.loads(path.read_text())
    if (not args.reviewed_pilot_sha256 or file_hash(path) != args.reviewed_pilot_sha256
            or report.get("protocol_sha256") != protocol["sha256"] or report.get("status") != "ready_for_review"
            or len(report.get("checks", [])) != 8 or not all(c["full_vs_selected_exact"] for c in report["checks"])):
        raise ValueError("scan requires reviewed successful matching eight-check pilot SHA256")
    rows = []
    start = time.monotonic()
    def progress(state):
        value = {"state": state, "pid": os.getpid(), "protocol_sha256": protocol["sha256"],
                 "requested_role_presets": corpus["count"] * 2, "terminal_role_presets": len(rows),
                 "complete_coverage": len(rows) == corpus["count"] * 2,
                 "statuses": dict(Counter(row["status"] for row in rows)), "elapsed_seconds": time.monotonic()-start}
        atomic(args.work / "progress.json", value)
    progress("running")
    for role, identity in protocol["roles"].items():
        install_role(protocol["device_serial"], identity, args.work)
        for record in corpus["presets"]:
            if STOP.is_set():
                progress("interrupted"); return
            pair = [run_one(args, protocol, record, role, "selected", repeat, 360) for repeat in (1,2)]
            deduplicate_repeat_pngs(pair[0], pair[1], args.work)
            statuses = [row["status"] for row in pair]
            status = "success" if statuses == ["success", "success"] else next((s for s in statuses if s != "success"), "failed")
            if status == "success" and pair[0]["selected_native_sha256"] != pair[1]["selected_native_sha256"]:
                status = "nondeterministic"
            key = digest({"protocol_sha256": protocol["sha256"], "preset": record, "role": role})
            value = {"key": key, "protocol_sha256": protocol["sha256"], "preset": record, "role": role,
                     "status": status, "runs": [str((args.work / "jobs" / row["key"] / "row.json").relative_to(args.work)) for row in pair],
                     "repeat_exact_selected": status == "success", "hash_coverage": capture_indices(360)}
            save_row(args.work / "rows" / f"{key}.json", value)
            rows.append(value); progress("running")
    progress("complete")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "pilot", "scan"))
    parser.add_argument("--work", type=Path, default=WORK)
    parser.add_argument("--serial", default="192.168.51.53:5555")
    parser.add_argument("--baseline-apk", type=Path)
    parser.add_argument("--candidate-apk", type=Path)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--reviewed-pilot-sha256")
    args = parser.parse_args()
    validate_device(args.serial)
    args.work.mkdir(parents=True, exist_ok=True)
    if args.phase == "prepare":
        if not args.baseline_apk or not args.candidate_apk:
            parser.error("prepare requires both APKs")
        prepare(args); return
    for signum in (signal.SIGINT, signal.SIGTERM):
        signal.signal(signum, lambda *_: STOP.set())
    with (args.work / "host.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        protocol, corpus = load_inputs(args.work)
        validate_device(protocol["device_serial"])
        if args.phase == "pilot":
            pilot(args, protocol, corpus)
        else:
            scan(args, protocol, corpus)


if __name__ == "__main__":
    main()
