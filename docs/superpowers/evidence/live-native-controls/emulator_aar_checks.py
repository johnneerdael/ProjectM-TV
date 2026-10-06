#!/usr/bin/env python3
"""Six focused jobs through actual core AARs on this task's dedicated emulator."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shlex
import subprocess
import time
import zipfile

PRESETS = [
    "319.milk",
    "Hexcollie - now entering the wormhole2 - mash0000 - if you like this, maybe you, like me, are insane.milk",
    "idiot - Forty Six and 2 (pushit!).milk",
]
BASELINE = "3bc37560a87000ec7ac446895fee8ad09e93b5c83a601014b5fc396bd1f3e6d6"
LIBRARY = "8bb82903af3825e16b734ceddf7316ba83da43509fb3fa3614537749a5c124f0"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adb", required=True)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--baseline-aar", type=Path, required=True)
    parser.add_argument("--candidate-aar", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--roles", choices=["baseline", "candidate"], nargs="+", default=["baseline", "candidate"])
    args = parser.parse_args()
    if args.serial != "emulator-5620":
        raise ValueError("This protocol owns only the dedicated emulator-5620")
    args.output.mkdir(parents=True, exist_ok=False)
    baseline = args.baseline_aar.read_bytes()
    assert digest(baseline) == BASELINE
    with zipfile.ZipFile(args.baseline_aar) as archive:
        assert digest(archive.read("jni/arm64-v8a/libprojectmtv.so")) == LIBRARY

    def adb(*command, binary=False, timeout=60):
        result = subprocess.run([args.adb, "-s", args.serial, *map(str, command)],
                                capture_output=True, text=not binary, timeout=timeout, check=True)
        return result.stdout

    def shell(*command, **kwargs):
        return adb("shell", shlex.join(map(str, command)), **kwargs)

    gpu = shell("dumpsys", "SurfaceFlinger")
    gpu_line = next(line for line in gpu.splitlines() if line.startswith("GLES:"))
    assert "Apple M4 Pro" in gpu_line and "Metal" in gpu_line, gpu_line
    # 16 s mono PCM: 110 Hz + 6 kHz, alternates amplitudes every second.
    pcm = bytes(max(0, min(255, round(128 + 127 *
        (.2 if (i // 44100) % 2 == 0 else .8) *
        (.65 * math.sin(2 * math.pi * 110 * i / 44100) +
         .35 * math.sin(2 * math.pi * 6000 * i / 44100))))) for i in range(480 * 1470))
    audio = args.output / "audio.u8"
    audio.write_bytes(pcm)
    old_property = shell("getprop", "debug.projectmtv.preset").strip()
    rows = []
    metadata = {"protocol": "live-controls-aar-smoke-v1", "serial": args.serial,
                "gpu": gpu_line, "pcmSha256": digest(pcm), "frames": 480,
                "clock": "production real clock, paced at 30 fps; RNG not fixed",
                "baselineAarSha256": digest(baseline),
                "candidateAarSha256": digest(args.candidate_aar.read_bytes()), "runs": rows}
    try:
        for witness, preset in enumerate(PRESETS):
            for role in args.roles:
                package = "nl.neerdael.projectmtv.corpus" + role
                job = f"/data/user/0/{package}/files/live-controls-{time.time_ns()}"
                staging = f"/data/local/tmp/live-controls-{time.time_ns()}"
                local = args.output / f"{witness}-{role}"
                local.mkdir()
                request = {"preset": preset, "width": 512, "height": 512,
                           "referenceWidth": 0, "referenceHeight": 0,
                           "seed": 12345, "instrumented": False,
                           "pcmPath": job + "/audio.u8", "outputDir": job + "/output",
                           "expectedPresetCount": 9606}
                request_file = local / "request.json"
                request_file.write_text(json.dumps(request, indent=2) + "\n")
                shell("am", "force-stop", package)
                shell("run-as", package, "mkdir", "-p", job)
                shell("mkdir", "-p", staging)
                try:
                    for file in (audio, request_file):
                        adb("push", file, staging + "/" + file.name)
                        shell("run-as", package, "cp", staging + "/" + file.name, job + "/" + file.name)
                    # The worker's skip mask leaves only this exact preset eligible.
                    shell("setprop", "debug.projectmtv.preset", preset.encode()[:80].decode())
                    log = adb("shell", "am", "instrument", "-w", "-e", "job", job + "/request.json",
                              package + "/nl.neerdael.projectmtv.corpus.CorpusInstrumentation", timeout=180)
                    (local / "instrumentation.log").write_text(log)
                    manifest = json.loads(shell("run-as", package, "cat", job + "/output/manifest.json"))
                    (local / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
                    assert manifest["status"] == "ok" and manifest["framesRendered"] == 480, manifest
                    assert manifest["verifiedPresetName"] == preset and manifest["pcmSha256"] == digest(pcm)
                    assert "M4 Pro" in manifest["glRenderer"], manifest["glRenderer"]
                    assert manifest["coreReleased"] and manifest["eglDestroyed"]
                    for capture in manifest["captures"]:
                        name = f"frame-{capture['frame']:03d}.png"
                        raw = adb("exec-out", "run-as", package, "cat", job + "/output/" + name, binary=True)
                        assert raw.startswith(b"\x89PNG\r\n\x1a\n")
                        assert digest(raw) == capture["pngSha256"]
                        (local / name).write_bytes(raw)
                    rows.append({"preset": preset, "role": role, "frames": 480,
                                 "wallMs": manifest["renderWallDurationMs"],
                                 "deliveredFps": 480000 / manifest["renderWallDurationMs"],
                                 "sourceSha256": manifest["presetAssetSha256"],
                                 "manifest": str(local / "manifest.json")})
                    print(json.dumps(rows[-1]), flush=True)
                finally:
                    shell("am", "force-stop", package)
                    shell("run-as", package, "rm", "-rf", job)
                    shell("rm", "-rf", staging)
    finally:
        shell("setprop", "debug.projectmtv.preset", old_property)
        metadata["propertyRestored"] = True
        (args.output / "summary.json").write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    main()
