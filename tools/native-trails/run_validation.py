#!/usr/bin/env python3
"""Focused, resumable actual-core Native trails rendering on an owned emulator."""
import argparse
import fcntl
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/preset-lab/src"))
from preset_lab.identity import canonical_json, digest, file_digest

spec = importlib.util.spec_from_file_location("core_corpus", ROOT / "tools/core-corpus/run_corpus.py")
corpus = importlib.util.module_from_spec(spec)
spec.loader.exec_module(corpus)

CAPTURES = [120, 150, 180, 210, 239, 300, 390, 479]
PROFILES = [
    ("authored", "baseline-native", 1280, 720, 0, 0, None),
    ("authored_repeat", "baseline-native", 1280, 720, 0, 0, None),
    ("native_before", "baseline-native", 3840, 2160, 1024, 768, None),
    ("native_off", "candidate-native", 3840, 2160, 1024, 768, -1),
    ("standard", "candidate-native", 3840, 2160, 1280, 720, 0),
    ("medium", "candidate-native", 3840, 2160, 1280, 720, 1),
    ("high", "candidate-native", 3840, 2160, 1280, 720, 2),
    ("standard_default", "candidate-native", 3840, 2160, 1280, 720, None),
]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(canonical_json(value) + "\n")
    temporary.replace(path)


def adb(device, *args, timeout=120, binary=False):
    return subprocess.check_output(["adb", "-s", device, *map(str, args)], timeout=timeout,
                                   text=not binary, stderr=subprocess.STDOUT)


def shell(device, *args, timeout=120):
    return adb(device, "shell", " ".join(shlex.quote(str(arg)) for arg in args), timeout=timeout)


def validate_user_id(user_id):
    if type(user_id) is not int or not 0 <= user_id <= 2147483647:
        raise ValueError("Invalid Android user_id: " + repr(user_id))
    return user_id


def current_user(device):
    value = shell(device, "am", "get-current-user").strip()
    if re.fullmatch(r"[0-9]+", value) is None:
        raise ValueError("Invalid current Android user: " + repr(value))
    return validate_user_id(int(value))


def install_worker(device, identity, user_id):
    validate_user_id(user_id)
    result = adb(device, "install", "-r", "--user", user_id, identity["apk"], timeout=180)
    if not result.strip().splitlines() or result.strip().splitlines()[-1].strip() != "Success":
        raise ValueError("Worker package install failed: " + result)
    package = identity["package"]
    lines = shell(device, "pm", "list", "packages", "--user", user_id, package).strip().splitlines()
    if any(re.fullmatch(r"package:[A-Za-z0-9_.]+", line) is None for line in lines) or "package:" + package not in lines:
        raise ValueError("Worker package lookup failed for Android user%d: %s" % (user_id, lines))


def private_directory(package, key, user_id):
    validate_user_id(user_id)
    return "/data/user/%d/%s/files/native-trails/%s" % (user_id, package, key)


def check_artifacts(identity):
    for name in ("apk", "aar"):
        if file_digest(Path(identity[name])) != identity[name + "_sha256"]:
            raise ValueError("Frozen " + name + " changed")
    with zipfile.ZipFile(identity["aar"]) as aar, zipfile.ZipFile(identity["apk"]) as apk:
        files = [name for name in apk.namelist() if name.startswith("lib/") and name.endswith(".so")]
        if "lib/arm64-v8a/libprojectmtv.so" not in files:
            raise ValueError("Worker is missing the tested arm64 core")
        for name in files:
            if name.replace("lib/", "jni/", 1) not in aar.namelist() or aar.read(name.replace("lib/", "jni/", 1)) != apk.read(name):
                raise ValueError("Worker APK is not using the frozen actual AAR")
        assets = [name for name in aar.namelist() if name.startswith("assets/") and not name.endswith("/")]
        for name in assets:
            if name not in apk.namelist() or aar.read(name) != apk.read(name):
                raise ValueError("Worker APK assets differ from the AAR")


def verify(directory, request, expected_hash):
    import cv2
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest.get("status") != "ok" or manifest.get("framesRendered") != 480:
        raise ValueError("Rendering failed: " + str(manifest.get("error", manifest)))
    if manifest.get("job") != request or manifest.get("requestSha256") != hashlib.sha256((canonical_json(request) + "\n").encode()).hexdigest():
        raise ValueError("Manifest is from another request")
    if manifest.get("presetAssetSha256") != expected_hash or manifest.get("verifiedPresetName") != request["preset"]:
        raise ValueError("Rendered preset identity changed")
    if manifest.get("glErrorChecks") != 480 or manifest.get("presetNameChecks") != 480:
        raise ValueError("Incomplete per-frame GL/preset checks")
    if manifest.get("eligiblePresetCountAfterFrame479") != 1 or manifest.get("presetChangeCounter") != 1:
        raise ValueError("Exact single-preset invariant failed")
    if not manifest.get("coreReleased") or not manifest.get("eglDestroyed"):
        raise ValueError("Core/context cleanup incomplete")
    if [capture["frame"] for capture in manifest["captures"]] != CAPTURES:
        raise ValueError("Incomplete temporal captures")
    for capture in manifest["captures"]:
        path = directory / ("frame-%03d.png" % capture["frame"])
        if file_digest(path) != capture["pngSha256"]:
            raise ValueError("Capture PNG checksum mismatch")
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None or image.shape[:2] != (request["height"], request["width"]):
            raise ValueError("Capture dimensions mismatch")
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if hashlib.sha256(rgb.tobytes()).hexdigest() != capture["rgbSha256"]:
            raise ValueError("Capture RGB checksum mismatch")
    return manifest


def render(device, identity, request, directory, pcm, preset_hash, user_id):
    package = identity["package"]
    private = private_directory(package, directory.name, user_id)
    staging = "/data/local/tmp/native-trails-%d-%s" % (user_id, directory.name)
    request = dict(request, pcmPath=private + "/audio.u8", outputDir=private + "/output")
    directory.mkdir(parents=True, exist_ok=True)
    if (directory / "manifest.json").exists():
        return verify(directory, request, preset_hash)
    write(directory / "request.json", request)
    old_property = shell(device, "getprop", "debug.projectmtv.preset").strip()
    try:
        shell(device, "am", "force-stop", "--user", user_id, package)
        shell(device, "mkdir", "-p", staging)
        shell(device, "run-as", package, "--user", user_id, "mkdir", "-p", private)
        for name, path in (("request.json", directory / "request.json"), ("audio.u8", pcm)):
            adb(device, "push", path, staging + "/" + name)
            shell(device, "run-as", package, "--user", user_id, "cp", staging + "/" + name, private + "/" + name)
        shell(device, "setprop", "debug.projectmtv.preset", corpus.preset_prefix(request["preset"]))
        output = shell(device, "am", "instrument", "--user", user_id, "-w", "-e", "job", private + "/request.json",
                       package + "/nl.neerdael.projectmtv.corpus.CorpusInstrumentation", timeout=600)
        (directory / "instrumentation.log").write_text(output)
        archive = adb(device, "exec-out", "run-as", package, "--user", user_id, "tar", "-cf", "-", "-C", private,
                      "output", binary=True)
        with tempfile.TemporaryDirectory(dir=directory) as temporary:
            tar = Path(temporary) / "captures.tar"
            tar.write_bytes(archive)
            with tarfile.open(tar) as stream:
                stream.extractall(temporary, filter="data")
            for path in (Path(temporary) / "output").iterdir():
                path.replace(directory / path.name)
        result = verify(directory, request, preset_hash)
        return result
    finally:
        shell(device, "setprop", "debug.projectmtv.preset", old_property)
        shell(device, "am", "force-stop", "--user", user_id, package)
        shell(device, "rm", "-rf", staging)
        shell(device, "run-as", package, "--user", user_id, "rm", "-rf", private)


def request(preset, width, height, rw, rh, level, instrumented=True):
    result = {"preset": preset, "width": width, "height": height, "referenceWidth": rw,
              "referenceHeight": rh, "seed": 12345, "instrumented": instrumented,
              "expectedPresetCount": 9606}
    if level is not None:
        result["nativeTrails"] = level
    return result


def initialize(work, workers, presets, device, user_id):
    validate_user_id(user_id)
    identities = {role: json.loads((workers / role / "identity.json").read_text())
                  for role in {profile[1] for profile in PROFILES}}
    for identity in identities.values():
        check_artifacts(identity)
    if len({item["assets_sha256"] for item in identities.values()}) != 1:
        raise ValueError("Baseline/candidate packaged assets differ")
    before = identities["baseline-native"]["ordered_patches"]
    for role, identity in identities.items():
        expected = before if role.startswith("baseline") else before + identity["ordered_patches"][len(before):]
        if identity["ordered_patches"] != expected or (role.startswith("candidate") and len(expected) != len(before) + 1):
            raise ValueError("Candidate must retain the exact released patch prefix and add one production patch")
    names = [name for name in presets.read_text().splitlines() if name]
    records = {name: file_digest(ROOT / "core/src/main/assets/presets" / name) for name in names}
    _, audio = corpus.signal()
    protocol = {"schema": 2, "user_id": user_id, "workers": identities, "presets": records, "profiles": PROFILES,
                "runner_sha256": file_digest(Path(__file__)), "device": device,
                "fingerprint": shell(device, "getprop", "ro.build.fingerprint").strip(),
                "pcm_sha256": hashlib.sha256(audio).hexdigest(), "frames": 480,
                "clock": "frame/30.0", "seed": 12345, "captures": CAPTURES,
                "limitations": "focused known presets; emulator GLES on host GPU, no physical TV performance claim"}
    path = work / "protocol.json"
    if path.exists():
        if json.loads(path.read_text()) != json.loads(canonical_json(protocol)):
            raise ValueError("Frozen protocol differs; use a new work directory")
    else:
        write(path, protocol)
        (work / "audio.u8").write_bytes(audio)
    if file_digest(work / "audio.u8") != protocol["pcm_sha256"]:
        raise ValueError("PCM changed")
    return protocol


def run(work, workers, presets, device, selected):
    work.mkdir(parents=True, exist_ok=True)
    with (work / "run.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        user_id = current_user(device)
        protocol = initialize(work, workers, presets, device, user_id)
        installed = None
        rows = []
        for preset, sha in protocol["presets"].items():
            for profile, role, width, height, rw, rh, level in PROFILES:
                if selected and profile not in selected:
                    continue
                identity = protocol["workers"][role]
                if installed != identity["apk_sha256"]:
                    install_worker(device, identity, user_id)
                    installed = identity["apk_sha256"]
                key = digest({"protocol": digest(protocol), "preset": sha, "profile": profile})
                directory = work / "jobs" / key
                manifest = render(device, identity, request(preset, width, height, rw, rh, level),
                                  directory, work / "audio.u8", sha, user_id)
                if profile in ("standard", "medium", "high", "standard_default"):
                    expected = "standard" if profile == "standard_default" else profile
                    status = str(manifest.get("nativeTrailsStatus", "")).lower()
                    if expected not in status or "1280×720" not in status or "canvas" not in status or "fallback" in status:
                        raise ValueError("Production path did not activate: " + str(manifest.get("nativeTrailsStatus")))
                row = {"preset": preset, "profile": profile, "key": key, "status": manifest["status"],
                       "frame_hashes": [capture["rgbSha256"] for capture in manifest["captures"]],
                       "trail_status": manifest.get("nativeTrailsStatus"),
                       "duration_ms": manifest["renderWallDurationMs"],
                       "frame_mean_ms": manifest.get("serializedFrameMeanMs"),
                       "frame_p90_ms": manifest.get("serializedFrameP90Ms"),
                       "pss_kb": manifest.get("pssAfterFramesKB")}
                write(directory / "row.json", row)
                rows.append(row)
                write(work / "progress.json", {"protocol_sha256": digest(protocol), "finished": rows})
                print(preset + " / " + profile + " OK", flush=True)


def smoke(work, apk, aar, device):
    user_id = current_user(device)
    identity = {"apk": str(apk), "aar": str(aar), "apk_sha256": file_digest(apk),
                "aar_sha256": file_digest(aar), "package": "nl.neerdael.projectmtv.corpuspublished", "user_id": user_id}
    check_artifacts(identity)
    work.mkdir(parents=True, exist_ok=False)
    _, audio = corpus.signal()
    pcm = work / "audio.u8"
    pcm.write_bytes(audio)
    install_worker(device, identity, user_id)
    preset = "Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk"
    sha = file_digest(ROOT / "core/src/main/assets/presets" / preset)
    manifest = render(device, identity, request(preset, 3840, 2160, 1024, 768, None, False),
                      work / "published-acid-4k", pcm, sha, user_id)
    write(work / "identity.json", identity)
    print(canonical_json({key: manifest.get(key) for key in ("status", "framesRendered", "coreVersion", "glRenderer", "determinism")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("run", "smoke"))
    parser.add_argument("--device", required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--workers", type=Path)
    parser.add_argument("--presets", type=Path)
    parser.add_argument("--profiles", nargs="*")
    parser.add_argument("--apk", type=Path)
    parser.add_argument("--aar", type=Path)
    args = parser.parse_args()
    if not args.device.startswith("emulator-") or args.device == "emulator-5580":
        parser.error("Use a task-owned emulator; corpus-owner emulator-5580 is protected")
    if args.mode == "smoke":
        if args.apk is None or args.aar is None:
            parser.error("smoke requires --apk and --aar")
        smoke(args.work, args.apk.resolve(), args.aar.resolve(), args.device)
    else:
        if args.workers is None or args.presets is None:
            parser.error("run requires --workers and --presets")
        run(args.work, args.workers.resolve(), args.presets.resolve(), args.device, args.profiles)
