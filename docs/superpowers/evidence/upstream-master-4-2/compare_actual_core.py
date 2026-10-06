#!/usr/bin/env python3
"""Bounded upstream-rebase comparison using the existing actual-core verifier.

Keep historical Native trails prefix/+1-patch protocols unchanged. Freeze each
role's complete artifact identity here, with the same PCM, preset, settings,
seed, logical clock, dimensions and captured frame numbers. No whole-corpus claim.
"""
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools/preset-lab/src"))
from preset_lab.identity import canonical_json, digest, file_digest

spec = importlib.util.spec_from_file_location("trails", ROOT / "tools/native-trails/run_validation.py")
trails = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = trails
spec.loader.exec_module(trails)

PRESETS = [
    "Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk",
    "midgitstraights of majillaen - featy sweet.milk",
    "Jc - Geometry 101.milk",
    "Mig_Oscilloscope022 b.milk",
]
SIZES = [("1080p", 1920, 1080, "inactive (render 1080p)"), ("4k", 3840, 2160, "1280×720")]


def helper_hashes():
    paths = ["tools/native-trails/run_validation.py", "tools/core-corpus/run_corpus.py",
             "tools/preset-lab/src/preset_lab/identity.py"]
    return {name: file_digest(ROOT / name) for name in paths}


def require_session(device, user_id, expected_helpers):
    if helper_hashes() != expected_helpers:
        raise ValueError("Runner helper source changed during the frozen comparison")
    if trails.current_user(device) != user_id:
        raise ValueError("Foreground Android user changed; preserve completed evidence")
    power = trails.shell(device, "dumpsys", "power")
    if not re.search(r"\bmWakefulness=Awake\b", power) or "mInteractive=false" in power:
        raise ValueError("TV must remain awake; stop without waking it")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    identities = {role: json.loads((path / "identity.json").read_text())
                  for role, path in [("baseline", args.baseline), ("candidate", args.candidate)]}
    expected = {"baseline": ("nl.neerdael.projectmtv.corpusrebasebaseline", "e0b0a967f0ffd7d332106c366668ed271718472b", 44, "b1bb994dbfaa04159630570cd9b2c255b173a6bd"),
                "candidate": ("nl.neerdael.projectmtv.corpusrebasecandidate", "6f64807467e312034883a4389e6aa80a675458bc", 3, "9f131997ef6aac61b2ada4dd05316113f39a720b")}
    for role, identity in identities.items():
        package, engine, count, source = expected[role]
        if identity["package"] != package or identity["engine_commit"] != engine or len(identity["ordered_patches"]) != count or identity["source_commit"] != source:
            raise ValueError("Unexpected role source/artifact identity: " + role)
        if identity.get("abi") != "armeabi-v7a":
            raise ValueError("This recorded AM6 protocol requires the validated ARMv7 artifacts")
        trails.check_artifacts(identity)
    if len({i["assets_sha256"] for i in identities.values()}) != 1:
        raise ValueError("Comparison assets differ")
    user_id = trails.current_user(args.device)
    helpers = helper_hashes()
    with trails.corpus.session_lock(args.device, 5037):
        require_session(args.device, user_id, helpers)
        _, pcm = trails.corpus.signal()
        protocol = {"schema": "projectmtv-master-rebase-v1", "device": args.device, "user_id": user_id,
                    "workers": identities, "presets": {name: file_digest(ROOT / "core/src/main/assets/presets" / name) for name in PRESETS},
                    "sizes": SIZES, "reference": [1024, 768], "native_trails": 0,
                    "clock": "frame/30", "seed": 12345, "frames": 480, "captures": trails.CAPTURES,
                    "pcm_sha256": hashlib.sha256(pcm).hexdigest(), "runner_sha256": file_digest(Path(__file__)),
                    "helper_sha256": helpers,
                    "fingerprint": trails.shell(args.device, "getprop", "ro.build.fingerprint").strip(),
                    "limits": "Focused instrumented actual-core controls; serialized physical-TV engine cost, not app FPS. Existing worker English labels say emulator and 512 retained PCM samples; actual sources retain the API's 576 samples. No whole-corpus/3.0-only GPU claim."}
        frozen = work / "protocol.json"
        if frozen.exists() and json.loads(frozen.read_text()) != json.loads(canonical_json(protocol)):
            raise ValueError("Frozen inputs changed; use a new work directory")
        trails.write(frozen, protocol)
        audio = work / "audio.u8"
        if audio.exists() and file_digest(audio) != protocol["pcm_sha256"]:
            raise ValueError("Frozen PCM changed")
        audio.write_bytes(pcm)
        installed = set()
        rows = []
        completed = 0
        # Repeat both roles at each size: detect nondeterminism before interpreting a difference.
        for preset in PRESETS:
            for label, width, height, canvas in SIZES:
                for role in ("baseline", "candidate"):
                    identity = identities[role]
                    if role not in installed:
                        require_session(args.device, user_id, helpers)
                        trails.install_worker(args.device, identity, user_id)
                        installed.add(role)
                    for repeat in (0, 1):
                        key = digest({"protocol": digest(protocol), "preset": preset, "size": label,
                                      "role": role, "repeat": repeat})
                        directory = work / "jobs" / key
                        require_session(args.device, user_id, helpers)
                        manifest = trails.render(args.device, identity,
                            trails.request(preset, width, height, 1024, 768, 0), directory, audio,
                            protocol["presets"][preset], user_id)
                        status = str(manifest.get("nativeTrailsStatus", "")).lower()
                        if "standard" not in status or canvas not in status or "fallback" in status:
                            raise ValueError("Expected production trails state did not match the render size: " + status)
                        row = {"preset": preset, "size": label, "role": role, "repeat": repeat,
                               "key": key, "status": manifest["status"], "trail_status": status,
                               "hashes": [c["rgbSha256"] for c in manifest["captures"]],
                               "frame_mean_ms": manifest.get("serializedFrameMeanMs"),
                               "frame_p90_ms": manifest.get("serializedFrameP90Ms"),
                               "pss_kb": manifest.get("pssAfterFramesKB")}
                        trails.write(directory / "row.json", row)
                        rows.append(row)
                        trails.write(work / "progress.json", {"protocol_sha256": digest(protocol), "rows": rows})
                        print(preset, label, role, repeat, "verified", flush=True)
                        completed += 1
                        if args.limit and completed >= args.limit:
                            return


if __name__ == "__main__":
    main()
