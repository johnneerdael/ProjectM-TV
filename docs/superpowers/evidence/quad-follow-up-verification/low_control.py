"""Separate low-height waveform injection from shader feedback and size-band noise."""
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from measure import ROOT, RunConfig, bass_signals, run_one


def replace_key(text, key, value):
    pattern = rf"^{re.escape(key)}=.*$"
    if len(re.findall(pattern, text, re.M)) != 1:
        raise ValueError(f"expected one {key}")
    return re.sub(pattern, f"{key}={value}", text, count=1, flags=re.M)


def main():
    source = ROOT / "core/src/main/assets/presets/TonyMilkdrop - I Like Cartoon --- Isosceles edit.milk"
    original = source.read_text()
    without_wave = replace_key(original, "fWaveAlpha", "0")
    last = max(int(n) for n in re.findall(r"^per_frame_(\d+)=", without_wave, re.M))
    without_wave += f"\nper_frame_{last+1}=wave_a=0;\n"
    work = ROOT / "build/follow-ups/verification/low-control"
    work.mkdir(parents=True, exist_ok=True)
    pcm = bass_signals(RunConfig(fps=30, warmup_seconds=4, measurement_seconds=4), work / "signals")["bass-0.30"]
    jobs = []
    for width, height in ((1182, 665), (1166, 656), (1200, 675), (640, 360), (630, 354),
                          (650, 366), (854, 480), (960, 540)):
        for repeat in (1, 2):
            jobs.append(("cartoon-uncut", original, f"c{width}x{height}", width, height,
                         False, "nosmooth", repeat, work, pcm))
    for width, height in ((640, 360), (854, 480), (960, 540), (1182, 665)):
        for quad in (False, True):
            for repeat in (1, 2):
                jobs.append(("cartoon-no-wave", without_wave, f"{'q' if quad else 'c'}{height}",
                             width, height, quad, "nosmooth", repeat, work, pcm))
    results = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        for row in pool.map(run_one, jobs):
            results.append(row)
            (work / "raw.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
