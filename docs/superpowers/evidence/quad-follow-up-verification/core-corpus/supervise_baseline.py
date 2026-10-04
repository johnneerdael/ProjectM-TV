"""Restart only a dead baseline scanner with its original frozen command/inputs.

Never change the renderer, emulator, protocol or coverage records. The scan's
exclusive host.lock remains the final duplicate-process guard.
"""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
import signal
from pathlib import Path
import subprocess
import time


def disk_action(free_bytes, scanner_live, paused_for_disk):
    if paused_for_disk:
        return "resume" if free_bytes >= 12 * 1024 ** 3 else "wait"
    if free_bytes < 8 * 1024 ** 3:
        return "pause" if scanner_live else "wait"
    return "continue"


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def atomic(path, value):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, sort_keys=True) + "\n")
    os.replace(temporary, path)


def process(pid):
    found = subprocess.run(["ps", "-p", str(pid), "-o", "stat=,command="], capture_output=True, text=True)
    return found.stdout.strip() if found.returncode == 0 else ""


def scan_alive(pid, command, work):
    state = process(pid)
    return bool(state and not state.split()[0].startswith("Z")
                and command[1] in state and str(work) in state and " scan " in state)


def lock_available(work):
    with (work / "host.lock").open("a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
    return True


def validate_launch(launch, work):
    command = launch["command"]
    if launch["serial"] != "emulator-5580" or type(launch.get("emulator_pid")) is not int or launch["emulator_pid"] <= 0:
        raise ValueError("supervisor is restricted to the existing owned emulator")
    expected = {"--roles": "baseline", "--serial": "emulator-5580", "--work": str(work)}
    if len(command) < 3 or command[2] != "scan":
        raise ValueError("original command is not a baseline scan")
    for flag, value in expected.items():
        if flag not in command or command[command.index(flag) + 1] != value:
            raise ValueError(f"original command differs: {flag}")
    spec = importlib.util.spec_from_file_location("frozen_baseline_input_validation", command[1])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if Path(command[1]).name == "owner_bridge.py":
        require_hash = launch.get("owner_bridge_sha256")
        if require_hash is None or file_hash(command[1]) != require_hash:
            raise ValueError("reviewed owner bridge source differs")
        renderer = module.import_runner()
        protocol, _, _ = module.attach_epoch(renderer, work)
        renderer.load_inputs(work)
    else:
        protocol, _ = module.load_inputs(work)
    if protocol["sha256"] != launch["protocol_sha256"]:
        raise ValueError("immutable protocol does not match original launch")
    report = work / "pilot-report.json"
    expected_report = command[command.index("--reviewed-pilot-sha256") + 1]
    if file_hash(report) != expected_report:
        raise ValueError("reviewed pilot changed")
    return command


def monitor(work, launch_path, interval):
    launch = json.loads(launch_path.read_text())
    command = validate_launch(launch, work)
    pid = launch["pid"]
    output = work / "baseline-supervisor"
    output.mkdir(exist_ok=True)
    child = None
    prior_state = json.loads((output / "status.json").read_text()) if (output / "status.json").exists() else {}
    restarts = list(prior_state.get("restarts", []))
    paused_for_disk = bool(prior_state.get("paused_for_disk", False))
    while True:
        progress_path = work / "progress.json"
        progress = json.loads(progress_path.read_text()) if progress_path.exists() else {}
        if progress.get("protocol_sha256") != launch["protocol_sha256"]:
            raise ValueError("live progress protocol differs")
        state = {"supervisor_pid": os.getpid(), "scanner_pid": pid,
                 "protocol_sha256": launch["protocol_sha256"], "updated_unix_seconds": time.time(),
                 "terminal_baseline_pairs": progress.get("terminal_role_presets"), "restarts": restarts,
                 "paused_for_disk": paused_for_disk}
        # Completion belongs to the scanner + independent remote-ACK notifier, not this watcher.
        if progress.get("state") == "complete" and progress.get("execution_roles") == ["baseline"]:
            atomic(output / "status.json", dict(state, state="scanner_complete; awaiting independent completion ACK"))
            return
        available = os.statvfs(work).f_bavail * os.statvfs(work).f_frsize
        live = scan_alive(pid, command, work)
        action = disk_action(available, live, paused_for_disk)
        state["free_bytes"] = available
        if action == "pause":
            # This is the exact owned scanner, not the emulator or another process.
            if scan_alive(pid, command, work):
                os.kill(pid, signal.SIGTERM)
            paused_for_disk = True
            pause_event = {"event": "low_disk_SIGTERM_owned_scanner", "pid": pid,
                           "unix_seconds": time.time(), "free_bytes": available}
            restarts.append(pause_event)
            atomic(output / f"disk-pause-{time.time_ns()}.json", pause_event)
            atomic(output / "status.json", dict(state, state="disk_pause_requested; preserving in-flight job",
                                               paused_for_disk=True))
        elif paused_for_disk and live:
            atomic(output / "status.json", dict(state, state="waiting for graceful owned scanner exit", paused_for_disk=True))
        elif action == "wait":
            paused_for_disk = True
            atomic(output / "status.json", dict(state, state="disk_wait; require12GiB before resume", paused_for_disk=True))
        elif live:
            atomic(output / "status.json", dict(state, state="scanner_live"))
        elif not lock_available(work):
            atomic(output / "status.json", dict(state, state="another scanner holds host.lock; no restart"))
        else:
            # Validate only before a restart: avoid rehashing all assets while rendering is healthy.
            validate_launch(launch, work)
            emulator = process(launch["emulator_pid"])
            if "ProjectM_Core_Corpus_Api34" not in emulator or "5580" not in emulator:
                atomic(output / "status.json", dict(state, state="blocked: original emulator is absent"))
                return
            available = os.statvfs(work).f_bavail * os.statvfs(work).f_frsize
            if available < 8 * 1024 ** 3 or (paused_for_disk and available < 12 * 1024 ** 3):
                paused_for_disk = True
                atomic(output / "status.json", dict(state, state="disk_wait; preserve records", free_bytes=available, paused_for_disk=True))
                time.sleep(interval)
                continue
            stamp = time.time_ns()
            stdout = output / f"restart-{stamp}.stdout.log"
            stderr = output / f"restart-{stamp}.stderr.log"
            prior_pid = pid
            with stdout.open("wb") as out, stderr.open("wb") as err:
                child = subprocess.Popen(command, stdout=out, stderr=err, start_new_session=True,
                                         env=dict(os.environ, PYTHONFAULTHANDLER="1"))
            pid = child.pid
            paused_for_disk = False
            event = {"old_dead_pid": prior_pid, "new_pid": pid, "unix_seconds": time.time(),
                     "stdout": str(stdout), "stderr": str(stderr), "command": command,
                     "free_bytes": available, "source_changes": "none"}
            restarts.append(event)
            atomic(output / f"restart-{stamp}.json", event)
            atomic(output / "status.json", dict(state, scanner_pid=pid, paused_for_disk=False, state="confirmed dead scanner restarted"))
        if child is not None:
            child.poll()  # Reap our own completed subprocess rather than retaining a zombie.
        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True, type=Path)
    parser.add_argument("--launch", required=True, type=Path)
    parser.add_argument("--interval", type=int, default=30)
    args = parser.parse_args()
    if args.interval < 10:
        parser.error("supervisor interval must be at least10 seconds")
    with (args.work / "baseline-supervisor.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        monitor(args.work.resolve(), args.launch.resolve(), args.interval)
