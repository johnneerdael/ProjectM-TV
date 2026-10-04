"""Run isolated actual-core speed controls on the owned emulator-5580 only.

Keep the physical-TV runner frozen. Reuse its pure artifact validation, without
calling its device-control functions or changing its serial restrictions.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
WORK = ROOT / "build/follow-ups/core-corpus/mac-emulator/speed-probe"
SERIAL = "emulator-5580"
PACKAGE = "nl.neerdael.projectmtv.corecorpus"
COMPONENT = PACKAGE + "/nl.neerdael.projectm.corecorpus.CorpusInstrumentation"
spec = importlib.util.spec_from_file_location("core_corpus_validation", HERE / "run.py")
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)


def adb(*args, timeout=120, allow_failure=False):
    process = subprocess.run(["adb", "-s", SERIAL, *args], capture_output=True, timeout=timeout)
    if process.returncode and not allow_failure:
        raise RuntimeError(f"owned emulator adb failed: {args[0]} ({process.returncode})")
    return process


def guard():
    launch = json.loads((WORK.parent / "launch.json").read_text())
    if launch.get("serial") != SERIAL or launch.get("pid") != 92211:
        raise ValueError("owned emulator launch identity differs")
    import os
    os.kill(92211, 0)
    command = subprocess.check_output(["ps", "-p", "92211", "-o", "command="], text=True)
    if "ProjectM_Core_Corpus_Api34" not in command or "5580" not in command:
        raise ValueError("owned emulator PID is not the expected isolated AVD")
    if adb("shell", "getprop", "ro.kernel.qemu").stdout.strip() != b"1":
        raise ValueError("serial5580 is not the approved owned Android emulator")
    if adb("shell", "getprop", "sys.boot_completed").stdout.strip() != b"1":
        raise ValueError("owned emulator has not booted")


def prepare(tv_protocol):
    guard()
    original = json.loads(tv_protocol.read_text())
    original_hash = original.pop("sha256")
    if validation.digest(original) != original_hash:
        raise ValueError("source TV protocol checksum mismatch")
    device = {name: adb("shell", "getprop", name).stdout.decode().strip() for name in
              ("ro.kernel.qemu", "ro.build.fingerprint", "ro.product.model", "ro.product.cpu.abi")}
    protocol = dict(original, device_serial=SERIAL, device=device,
                    speed_probe_sha256=validation.file_hash(Path(__file__)),
                    reused_validation_runner_sha256=validation.file_hash(HERE / "run.py"),
                    source_input_protocol_sha256=original_hash,
                    limitations="Isolated Android-emulator actual-core speed controls; never reuse TV/CGL render records")
    protocol_hash = validation.digest(protocol)
    protocol["sha256"] = protocol_hash
    if WORK.exists() and (WORK / "protocol.json").exists():
        if json.loads((WORK / "protocol.json").read_text()) != protocol:
            raise ValueError("immutable emulator protocol differs")
    WORK.mkdir(parents=True, exist_ok=True)
    validation.atomic(WORK / "protocol.json", protocol)
    inventory = json.loads((tv_protocol.parent / "inventory.json").read_text())
    validation.atomic(WORK / "inventory.json", inventory)
    return protocol, inventory


def push_private(path, relative):
    temporary = "/data/local/tmp/corecorpus-emulator-" + validation.file_hash(path) + ".tmp"
    adb("push", str(path), temporary)
    adb("shell", "chmod", "0644", temporary)
    adb("shell", "run-as", PACKAGE, "cp", temporary, relative)
    adb("shell", "rm", temporary)


def run_control(protocol, record, role, repeat, mode):
    guard()
    job = validation.make_job(protocol, record, role, mode, repeat, 360)
    job["retain_native_frames"] = False
    directory = WORK / "jobs" / job["job_id"]
    if (directory / "row.json").exists():
        raise ValueError("speed record already exists; do not rerender/overwrite")
    directory.mkdir(parents=True)
    validation.atomic(directory / "job.json", job)
    relative = "files/jobs/" + job["job_id"]
    adb("shell", "am", "force-stop", PACKAGE)
    adb("shell", "run-as", PACKAGE, "mkdir", "-p", relative)
    push_private(directory / "job.json", relative + "/job.json")
    push_private(Path(protocol["pcm"]["480"]["path"]), relative + "/pcm.u8")
    start = time.monotonic()
    row = {"key": job["job_id"], "protocol_sha256": protocol["sha256"], "preset": record,
           "role": role, "repeat": repeat, "capture_mode": mode, "status": "failed"}
    try:
        process = adb("shell", "am", "instrument", "-w", "-e", "job",
                      validation.REMOTE + "/" + job["job_id"] + "/job.json", COMPONENT,
                      timeout=1200, allow_failure=True)
        row["instrumentation_wall_seconds"] = time.monotonic() - start
        (directory / "instrumentation.log").write_bytes(process.stdout + process.stderr)
        pulled = adb("pull", job["output_directory"], str(directory), timeout=300, allow_failure=True)
        (directory / "pull.log").write_bytes(pulled.stdout + pulled.stderr)
        if pulled.returncode:
            raise ValueError("owned emulator output pull failed")
        output = directory / "output"
        result = json.loads((output / "result.json").read_text())
        row["result"] = result
        frames = validation.read_frames(output)
        row["status"] = validation.validate_result(job, result, frames, output)
        row["selected_native_sha256"] = {str(item["frame"]): item["sha256"] for item in result.get("selected_files", [])}
        if row["status"] == "success" and process.returncode:
            row.update(status="failed", error="instrumentation returned nonzero")
        row["roundtrip_after_staging_wall_seconds"] = time.monotonic() - start
        logcat = adb("logcat", "-d", "--pid=" + str(result.get("pid", -1)), "-v", "threadtime", allow_failure=True)
        (directory / "core-logcat.txt").write_bytes(logcat.stdout + logcat.stderr)
    except Exception as error:
        row.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        row["elapsed_seconds"] = time.monotonic() - start
        validation.save_row(directory / "row.json", row)
    print(validation.canonical({k: row.get(k) for k in ("key", "status", "error", "instrumentation_wall_seconds", "roundtrip_after_staging_wall_seconds")} ), flush=True)
    return row


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tv-protocol", type=Path, required=True)
    parser.add_argument("--role", choices=("baseline", "candidate"), default="baseline")
    parser.add_argument("--control", type=int, choices=(0, 1, 2), default=0)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--mode", choices=("full", "selected"), default="selected")
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    protocol, corpus = prepare(args.tv_protocol)
    if args.install:
        guard()
        role = protocol["roles"][args.role]
        if validation.file_hash(role["apk_path"]) != role["apk_sha256"]:
            raise ValueError("source APK checksum changed")
        # This new owned emulator has no prior corecorpus records. Refuse destructive clears
        # after any speed record exists; fresh-process jobs have their own isolated skip file.
        if list((WORK / "jobs").glob("*/row.json")):
            raise ValueError("preserve owned emulator records before changing installed role")
        adb("shell", "am", "force-stop", PACKAGE)
        adb("install", "-r", role["apk_path"], timeout=300)
        cleared = adb("shell", "pm", "clear", PACKAGE)
        if cleared.stdout.strip() != b"Success":
            raise ValueError("owned dedicated-package clear was not acknowledged")
    record = next(row for row in corpus["presets"] if row["path"] == validation.CONTROLS[args.control])
    run_control(protocol, record, args.role, args.repeat, args.mode)
