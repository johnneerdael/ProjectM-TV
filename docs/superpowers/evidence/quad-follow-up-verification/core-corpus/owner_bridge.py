"""Explicit transport-owner epoch recovery around the unchanged frozen runner.

Keep every original render/protocol/cache identity. Record the actual replacement
emulator receipt separately; never pretend its PID equals the old receipt.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
GL_FIELDS = ("gl_vendor", "gl_renderer", "gl_version")


def require_digest(expected, actual, label):
    if expected != actual:
        raise ValueError(f"unchanged identity rejected: {label}")


def validate_owner_epoch(original, current, launch, expected_device, actual_device, expected_gl, actual_gl):
    if type(current.get("pid")) is not int or current["pid"] <= 0 or current["pid"] == original["pid"]:
        raise ValueError("new epoch must report its actual distinct live PID")
    for field in ("avd", "command", "ro.kernel.qemu"):
        require_digest(original[field], current[field], "owned " + field)
    require_digest("1", current["ro.kernel.qemu"], "emulator attestation")
    require_digest(original["pid"], launch.get("restarted_from_dead_pid"), "prior dead PID chain")
    require_digest(original["launch_sha256"], launch.get("prior_launch_sha256"), "original launch receipt chain")
    require_digest(expected_device, actual_device, "device fingerprint/ABI")
    require_digest(expected_gl, actual_gl, "GPU/GL driver")


def import_runner():
    spec = importlib.util.spec_from_file_location("frozen_core_runner_owner_epoch", HERE / "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def attach_epoch(module, work):
    protocol = json.loads((work / "protocol.json").read_text())
    original_owner = protocol["emulator_owner"]
    owner_dir = ROOT / "build/follow-ups/core-corpus/mac-emulator"
    actual_launch = json.loads((owner_dir / "launch.json").read_text())
    expected_actual_receipt_sha = module.file_hash(owner_dir / "launch.json")
    prior_path = Path(actual_launch["prior_launch_path"])
    require_digest(original_owner["launch_sha256"], module.file_hash(prior_path), "archived original launch")
    epoch_dir = work / "owner-epochs" / str(actual_launch["pid"])
    epoch_dir.mkdir(parents=True, exist_ok=True)
    expected_gl = None
    for row_path in (work / "jobs").glob("*/row.json"):
        row = json.loads(row_path.read_text())
        if (row.get("role") == "baseline" and row.get("status") == "success"
                and module.read_cached(row_path, row.get("key"), protocol["sha256"]) is not None):
            expected_gl = {key: row["result"][key] for key in GL_FIELDS}
            break
    if expected_gl is None:
        raise ValueError("no authenticated prior baseline driver receipt")
    original_guard = module.require_owned_emulator

    def actual_epoch_guard(serial):
        if serial != "emulator-5580":
            raise ValueError("owner bridge permits only owned emulator5580")
        current = original_guard(serial)  # Actual new PID/process/AVD/qemu checks, unchanged.
        require_digest(actual_launch["pid"], current["pid"], "current epoch PID")
        require_digest(expected_actual_receipt_sha, current["launch_sha256"], "current actual receipt")
        # Fingerprint uses the actual guest. No renderer calls or synthetic driver values.
        device = {key: module.adb(serial, "shell", "getprop", key).stdout.decode().strip()
                  for key in protocol["device"]}
        surface = module.adb(serial, "shell", "dumpsys", "SurfaceFlinger").stdout.decode(errors="replace")
        gpu_line = next((line.strip()[6:] for line in surface.splitlines() if line.strip().startswith("GLES: ")), None)
        if gpu_line is None or len(gpu_line.split(", ", 2)) != 3:
            raise ValueError("actual guest GPU identity is unavailable")
        actual_gl = dict(zip(GL_FIELDS, gpu_line.split(", ", 2)))
        validate_owner_epoch(original_owner, current, actual_launch, protocol["device"], device, expected_gl, actual_gl)
        return current

    def bridged_inputs(requested_work):
        require_digest(str(work), str(Path(requested_work).resolve()), "dataset path")
        current_protocol = json.loads((work / "protocol.json").read_text())
        require_digest(protocol, current_protocol, "immutable original protocol")
        require_digest(protocol["sha256"], module.digest({k: v for k, v in protocol.items() if k != "sha256"}), "protocol digest")
        require_digest(protocol["runner_sha256"], module.file_hash(HERE / "run.py"), "frozen renderer/runner source")
        corpus = json.loads((work / "inventory.json").read_text())
        require_digest(protocol["corpus_sha256"], module.digest(corpus["presets"]), "preset inventory")
        for role in protocol["roles"].values():
            require_digest(role["apk_sha256"], module.file_hash(role["apk_path"]), "actual core APK")
            with zipfile.ZipFile(role["apk_path"]) as archive:
                identity = json.loads(archive.read("assets/backend-identity.json"))
                require_digest(role["backend_identity"], identity, "core/harness/instrumentation source identity")
        for audio in protocol["pcm"].values():
            require_digest(audio["sha256"], module.file_hash(audio["path"]), "canonical PCM")
        owner = actual_epoch_guard(protocol["device_serial"])
        receipt = {"original_protocol_sha256": protocol["sha256"], "original_owner": original_owner,
                   "actual_current_owner": owner, "expected_driver": expected_gl,
                   "bridge_source_sha256": module.file_hash(Path(__file__)),
                   "adaptation": "isolated process replaces load_inputs volatile-owner equality with verified real owner epoch; original require_owned_emulator still validates actual PID/process/AVD/qemu; all render/input/cache identities unchanged",
                   "source_mutation": "none", "created_unix_seconds": time.time()}
        receipt_path = epoch_dir / "owner-receipt.json"
        if receipt_path.exists():
            saved = json.loads(receipt_path.read_text())
            require_digest({k: v for k, v in saved.items() if k != "created_unix_seconds"},
                           {k: v for k, v in receipt.items() if k != "created_unix_seconds"}, "immutable owner epoch receipt")
        else:
            module.atomic(receipt_path, receipt)
        return protocol, corpus

    original_run_one = module.run_one

    def observed_run_one(*args, **kwargs):
        job_args, requested_protocol, record, role, mode, repeat, duration = args[:7]
        key = module.job_key(requested_protocol["sha256"], record, role, mode, repeat, duration)
        row_path = job_args.work / "jobs" / key / "row.json"
        was_cached = module.read_cached(row_path, key, requested_protocol["sha256"]) is not None
        row = original_run_one(*args, **kwargs)
        if row.get("status") == "success":
            actual_gl = {key: row["result"][key] for key in GL_FIELDS}
            require_digest(expected_gl, actual_gl, "actual core GPU/GL driver")
        if not was_cached:
            row["execution_owner_epoch"] = {"actual_pid": actual_launch["pid"],
                                            "receipt_path": str(epoch_dir / "owner-receipt.json"),
                                            "receipt_sha256": module.file_hash(epoch_dir / "owner-receipt.json"),
                                            "original_protocol_sha256": requested_protocol["sha256"]}
            row.pop("payload_sha256", None)
            module.save_row(row_path, row)
        return row

    module.require_owned_emulator = actual_epoch_guard
    module.load_inputs = bridged_inputs
    module.run_one = observed_run_one
    return protocol, epoch_dir, expected_gl


def probe(module, work, protocol, epoch_dir, expected_gl):
    args = argparse.Namespace(work=epoch_dir / "probes", timeout=600)
    corpus = json.loads((work / "inventory.json").read_text())
    controls = [(module.CONTROLS[0], 360), (module.CONTROLS[1], 120), (module.CONTROLS[2], 360)]
    checks = []
    pilot = json.loads((work / "pilot-report.json").read_text())
    for name, duration in controls:
        previous = next(check for check in pilot["checks"] if check["role"] == "baseline"
                        and check["preset"]["path"] == name and check["measurement_frames"] == duration)
        prior = json.loads((work / "jobs" / previous["selected_key"] / "row.json").read_text())
        record = next(record for record in corpus["presets"] if record["path"] == name)
        row = module.run_one(args, protocol, record, "baseline", "selected", 7001, duration)
        exact = row["status"] == "success" and row["selected_native_sha256"] == prior["selected_native_sha256"]
        checks.append({"preset": name, "measurement_frames": duration, "new_key": row["key"],
                       "authenticated_prior_key": prior["key"], "exact_native_selected": exact})
        module.atomic(epoch_dir / "probe-report.json", {"original_protocol_sha256": protocol["sha256"], "checks": checks,
                                                       "status": "running" if len(checks) < 3 else "verified" if all(c["exact_native_selected"] for c in checks) else "failed"})
        if not exact:
            raise ValueError("restart control differs; stop before corpus resume")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("probe", "scan"))
    parser.add_argument("--work", type=Path, required=True)
    args, remainder = parser.parse_known_args()
    work = args.work.resolve()
    module = import_runner()
    protocol, epoch_dir, expected_gl = attach_epoch(module, work)
    module.load_inputs(work)
    if args.phase == "probe":
        if remainder:
            parser.error("probe takes no scanner arguments")
        probe(module, work, protocol, epoch_dir, expected_gl)
    else:
        report = json.loads((epoch_dir / "probe-report.json").read_text())
        if report.get("status") != "verified" or len(report.get("checks", [])) != 3:
            raise ValueError("scan requires three exact owner-epoch controls")
        sys.argv = [str(HERE / "run.py"), "scan", "--work", str(work), *remainder]
        module.main()
