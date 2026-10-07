"""Shared audio, device-session and capture helpers for focused validation.

The v2.2.1 full-corpus scanner and its scheduling/storage CLI are retired.
Use the original recorded Git revision to reproduce historical corpus evidence.
"""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import hashlib
from pathlib import Path
import re
import shlex
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "tools/preset-lab/src"))
from preset_lab.identity import digest, file_digest as file_hash
from preset_lab.inventory import valid_filename

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


if __name__ == "__main__":
    raise SystemExit("Legacy core-corpus CLI retired; use focused Native trails tools or the recorded historical Git revision.")
