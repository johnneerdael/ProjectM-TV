"""One real-device smoke job using the checksum-verified published core AAR."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import time

import numpy as np
from preset_lab.bass_screen import bass_signals
from preset_lab.models import RunConfig

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "nl.neerdael.projectmtv.corpuspublished"
PRESET = "Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk"
ADB = ["adb", "-P", "5038", "-s", "192.168.51.53:5555"]


def adb(*args, timeout=60, binary=False):
    result = subprocess.run(ADB + list(args), capture_output=True, timeout=timeout,
                            text=not binary, check=True)
    return result.stdout


def shell(*args):
    return adb("shell", " ".join(shlex.quote(str(a)) for a in args))


def main():
    work = ROOT / "build/core-corpus/published-smoke"
    work.mkdir(parents=True, exist_ok=True)
    power = shell("dumpsys", "power")
    assert "mWakefulness=Awake" in power, "TV is not awake; do not wake it"
    old_property = shell("getprop", "debug.projectmtv.preset").strip()
    config = RunConfig(width=1920, height=1080, fps=30, warmup_seconds=4,
                       measurement_seconds=12, seed=12345)
    source = bass_signals(config, work / "signals")["bass-0.30"]
    pcm = np.clip(np.rint(128 + 127 * np.fromfile(source, dtype="<f4")), 0, 255).astype(np.uint8)
    assert pcm.size == 705600
    (work / "audio.u8").write_bytes(pcm.tobytes())
    private = f"/data/user/0/{PACKAGE}/files/jobs/smoke-{time.time_ns()}"
    staging = f"/data/local/tmp/projectmtv-core-smoke-{time.time_ns()}"
    request = {"preset": PRESET, "seed": 12345, "referenceWidth": 1024,
               "referenceHeight": 768, "width": 1182, "height": 665,
               "pcmPath": private + "/audio.u8", "instrumented": False,
               "outputDir": private + "/output", "expectedPresetCount": 9606}
    (work / "request.json").write_text(json.dumps(request))
    try:
        adb("install", "-r", str(ROOT / "build/core-corpus/apks/core-corpus-published.apk"), timeout=180)
        shell("am", "force-stop", PACKAGE)
        # Stop production rendering while the dedicated benchmark owns the GPU; no preferences are written.
        shell("am", "force-stop", "nl.neerdael.projectmtv")
        shell("mkdir", "-p", staging)
        shell("run-as", PACKAGE, "mkdir", "-p", private)
        for name in ["request.json", "audio.u8"]:
            adb("push", str(work / name), staging + "/" + name)
            shell("run-as", PACKAGE, "cp", staging + "/" + name, private + "/" + name)
        shell("setprop", "debug.projectmtv.preset", PRESET.encode()[:80].decode(errors="ignore"))
        output = adb("shell", "am", "instrument", "-w", "-e", "job", private + "/request.json",
                     PACKAGE + "/nl.neerdael.projectmtv.corpus.CorpusInstrumentation", timeout=600)
        (work / "instrumentation.log").write_text(output)
        raw = shell("run-as", PACKAGE, "cat", private + "/output/manifest.json")
        (work / "manifest.json").write_text(raw)
        manifest = json.loads(raw)
        print(json.dumps({k:manifest.get(k) for k in ["status", "framesRendered", "verifiedPresetName", "glRenderer", "determinism", "error", "releaseError", "eglCleanupError"]}, indent=2), flush=True)
        assert manifest["status"] == "ok" and manifest["framesRendered"] == 480, raw
    finally:
        shell("setprop", "debug.projectmtv.preset", old_property)
        shell("am", "force-stop", PACKAGE)
        shell("rm", "-rf", staging)
        # Retain only this application's owned job until its capture checks finish.
        (work / "ownership.json").write_text(json.dumps({"package":PACKAGE,"private_job":private,
                                                        "property_restored":True},indent=2))


if __name__ == "__main__":
    main()
