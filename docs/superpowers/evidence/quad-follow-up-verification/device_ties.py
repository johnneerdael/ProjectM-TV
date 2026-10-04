"""Approved AM9 PRO line-tie check using native-size readback; restore device state afterward."""
import json
import shlex
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "build/follow-ups/device-AM9-Pro"
SERIAL = "192.168.51.53:5555"
PACKAGE = "nl.neerdael.projectmtv.quadverify"
PREFS = f"/data/user/0/{PACKAGE}/shared_prefs/projectm_settings.xml"
LUMA = np.array([.2126, .7152, .0722])


def adb(*args):
    return subprocess.check_output(["adb", "-s", SERIAL, *args], text=True).strip()


def shell(*args):
    return adb("shell", shlex.join(args))


def awake():
    return "mWakefulness=Awake" in shell("dumpsys", "power")


def fixed_size(height):
    shell("am", "force-stop", PACKAGE)
    tree = ET.fromstring(shell("cat", PREFS))
    uid = shell("stat", "-c", "%u", PREFS)
    for key, kind, value in (("render_height", "int", str(height)), ("frame_rate_cap", "int", "60"),
                             ("auto_change_enabled", "boolean", "false"),
                             ("track_access_explained", "boolean", "true"),
                             ("track_info", "boolean", "false"), ("blank_detection_v3", "boolean", "false")):
        for item in list(tree):
            if item.get("name") == key:
                tree.remove(item)
        ET.SubElement(tree, kind, {"name": key, "value": value})
    path = OUT / f"settings-{height}.xml"
    ET.ElementTree(tree).write(path, encoding="utf-8", xml_declaration=True)
    adb("push", str(path), "/data/local/tmp/projectm-verify-settings.xml")
    shell("cp", "/data/local/tmp/projectm-verify-settings.xml", PREFS)
    shell("chown", f"{uid}:{uid}", PREFS)
    shell("chmod", "600", PREFS)


def main():
    before = json.loads((OUT / "before.json").read_text())
    results = []
    touched = ("debug.projectmtv.preset", "debug.projectmtv.verify.line_mode",
               "debug.projectmtv.verify.silence", "debug.projectmtv.verify.capture")
    try:
        for height in (1080, 720):
            for mode in ("classic", "unit"):
                if not awake():
                    raise RuntimeError("device is not awake; no launch attempted")
                fixed_size(height)
                shell("setprop", touched[0], "Geiss - Surface (1-02 Version)")
                shell("setprop", touched[1], mode)
                shell("setprop", touched[2], "1")
                shell("setprop", touched[3], "")
                shell("am", "start", "-S", "-n", f"{PACKAGE}/com.example.projectm.visualizer.MainActivity")
                time.sleep(4)
                token = str(time.monotonic_ns())
                shell("setprop", touched[3], token)
                time.sleep(1)
                pid = shell("pidof", PACKAGE)
                log = adb("logcat", "-d", "--pid=" + pid, "-s", "projectM-Verify", "projectM-Native", "VisualizerRenderer")
                (OUT / f"tie-{mode}-{height}.log").write_text(log)
                width = height * 16 // 9
                expected = f"render={width}x{height}"
                if expected not in log or "quad shader rejected" in log:
                    raise RuntimeError(f"unexpected render or shader fallback for {mode}/{height}")
                if "line quad shader linked" not in log or "motion-vector quad shader linked" not in log:
                    raise RuntimeError("missing actual shader link proof")
                if f"capture={token}" not in log:
                    raise RuntimeError("missing capture completion proof")
                path = OUT / f"tie-{mode}-{height}.rgba"
                adb("pull", f"/data/user/0/{PACKAGE}/cache/frame-{width}x{height}.rgba", str(path))
                pixels = np.frombuffer(path.read_bytes(), dtype=np.uint8)
                if pixels.size != width * height * 4:
                    raise RuntimeError("native capture byte count mismatch")
                frame = pixels.reshape(height, width, 4)[::-1, :, :3].copy()
                cv2.imwrite(str(OUT / f"tie-{mode}-{height}.png"), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                rows = frame[:, width//4:3*width//4].mean(axis=1) @ LUMA / 255
                center = rows[height//3:2*height//3]
                peak = height//3 + int(center.argmax())
                result = {"mode": mode, "height": height, "size": [width, height], "peak_row": peak,
                          "row_luma_near_peak": {str(y): float(rows[y]) for y in range(max(0, peak-4), min(height, peak+5))},
                          "capture": str(path.relative_to(ROOT)), "pcm_forced_silent": True,
                          "shader_links_confirmed": True}
                results.append(result)
                print(json.dumps(result), flush=True)
                (OUT / "tie-results.json").write_text(json.dumps(results, indent=2))
    finally:
        shell("am", "force-stop", PACKAGE)
        for key in touched:
            shell("setprop", key, before["debug_properties_before"].get(key, ""))
        if awake():
            shell("am", "start", "-n", before["original_foreground_component"])
        process = subprocess.run(["adb", "-s", SERIAL, "shell", "pidof", PACKAGE],
                                 text=True, capture_output=True)
        cleanup = {"debug_properties_restored": {key: shell("getprop", key) for key in touched},
                   "verification_app_stopped": process.returncode == 1 and not process.stdout.strip(),
                   "device_awake_after": awake()}
        (OUT / "cleanup.json").write_text(json.dumps(cleanup, indent=2))
        print("cleanup", json.dumps(cleanup), flush=True)
        if before.get("adbd_uid_before") == 2000:
            adb("unroot")


if __name__ == "__main__":
    main()
