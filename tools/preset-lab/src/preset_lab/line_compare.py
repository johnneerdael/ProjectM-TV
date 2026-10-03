"""Compare projectM's GL lines with quad lines (projectM issue #682) on identical frames.

Each preset renders with the same synthetic audio, clock and seeds twice per render height: with
line_reference_height 0 (MilkDrop's 1 px GL lines) and with quad lines scaled to the 1080 reference.
Mean luma over the measurement window compares the two. The legacy frames' hash, checked against an
earlier report, proves the GL-line path unchanged. Line features are read statically from the preset
file (first occurrence of a key wins, as in the engine); per-frame code can still change them.
The legacy run at the reference height is rendered twice; presets whose two renders differ are
nondeterministic (unseeded randomness, wall clock) and are reported but left out of the statistics.
"""
import hashlib
import re
import statistics
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from .bass_screen import bass_signals
from .identity import canonical_json
from .models import EngineIdentity, JobSpec, PresetRecord, RunConfig
from .worker import render_job

VERSION = "line-compare-v1"
REFERENCE_HEIGHT = 1080
FIDELITY_TOLERANCE = .10
WARMUP_SECONDS = 4
MEASUREMENT_SECONDS = 4
LUMA = np.array([.2126, .7152, .0722], dtype=np.float32)
_KEY = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=\s*(\S+)", re.M)


@dataclass(frozen=True, slots=True)
class LineRunConfig(RunConfig):
    line_reference_height: int = 0


def mean_luma(frame: np.ndarray) -> float:
    if frame.dtype != np.uint8 or frame.ndim != 3 or frame.shape[-1] != 3:
        raise ValueError("RGB uint8 frame required")
    return float((frame.astype(np.float32) @ LUMA).mean() / 255)


def luma_ratio(legacy: float, quad: float) -> float | None:
    """Quad over legacy brightness; None when the legacy image is (nearly) black."""
    return None if legacy < 1e-3 else quad / legacy


def ladder_drift(low: float, high: float) -> float | None:
    """How much brightness changes between two render heights (0 = not at all)."""
    return None if high < 1e-3 else abs(low / high - 1)


def _values(text: str) -> dict[str, float]:
    values = {}
    for key, value in _KEY.findall(text):
        try:
            values.setdefault(key.lower(), float(value))
        except ValueError:
            continue
    return values


def line_features(text: str) -> list[str]:
    values = _values(text)
    def on(key):
        return values.get(key, 0) != 0
    waves = [i for i in range(4) if on(f"wavecode_{i}_enabled")]
    shapes = [i for i in range(4) if on(f"shapecode_{i}_enabled") and values.get(f"shapecode_{i}_border_a", 0) > 0]
    features = ["main_dots" if on("bwavedots") else "main_thick" if on("bwavethick") else "main_thin"]
    if any(on(f"wavecode_{i}_busedots") for i in waves):
        features.append("custom_dots")
    if any(not on(f"wavecode_{i}_busedots") and on(f"wavecode_{i}_bdrawthick") for i in waves):
        features.append("custom_thick")
    if any(not on(f"wavecode_{i}_busedots") and not on(f"wavecode_{i}_bdrawthick") for i in waves):
        features.append("custom_thin")
    if any(on(f"shapecode_{i}_thickoutline") for i in shapes):
        features.append("shape_thick")
    if any(not on(f"shapecode_{i}_thickoutline") for i in shapes):
        features.append("shape_thin")
    if values.get("mv_a", 1.0 if on("bmotionvectorson") else 0.0) > 0:
        features.append("motion_vectors")
    return features


def _config(height: int, reference: int) -> LineRunConfig:
    return LineRunConfig(width=round(height * 16 / 9), height=height, fps=30, warmup_seconds=WARMUP_SECONDS,
                         measurement_seconds=MEASUREMENT_SECONDS, line_reference_height=reference)


def measure_run(worker: Path, record: PresetRecord, repo: Path, work: Path, identity: EngineIdentity,
                config: LineRunConfig, pcm: Path, png: Path | None, timeout: float) -> dict:
    job = JobSpec(record, "line-compare", pcm, config, identity, repo / "core/src/main/assets/presets",
                  repo / "core/src/main/assets/textures", work / "jobs")
    warmup = round(config.warmup_seconds * config.fps)
    lumas, frames, index, last = [], hashlib.sha256(), 0, None
    def observe(frame):
        nonlocal index, last
        frames.update(frame.tobytes())
        if index >= warmup:
            lumas.append(mean_luma(frame))
        last = frame
        index += 1
    result = render_job(worker, job, observe, timeout)
    if result.status != "success":
        return {"status": result.status, "diagnostics": str(result.diagnostics_path)}
    if png is not None and last is not None:
        png.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(png), cv2.cvtColor(last, cv2.COLOR_RGB2BGR))
    return {"status": "success", "mean_luma": float(np.mean(lumas)), "frames_sha256": frames.hexdigest()}


def compare_preset(record: PresetRecord, repo: Path, work: Path, worker: Path, identity: EngineIdentity,
                   heights: tuple[int, ...], pcm: Path, timeout: float) -> dict:
    text = (repo / "core/src/main/assets/presets" / record.path).read_text(errors="replace")
    slug = hashlib.sha256(record.path.encode()).hexdigest()[:16]
    entry = {"preset": record.path, "frames": slug, "features": line_features(text), "runs": {}}
    for height in heights:
        for mode, reference in (("legacy", 0), ("quad", REFERENCE_HEIGHT)):
            png = work / "frames" / slug / f"{mode}-{height}.png" if height == REFERENCE_HEIGHT else None
            entry["runs"][f"{mode}-{height}"] = measure_run(worker, record, repo, work, identity,
                                                            _config(height, reference), pcm, png, timeout)
    runs = entry["runs"]
    runs[f"legacy-{REFERENCE_HEIGHT}-repeat"] = measure_run(worker, record, repo, work, identity,
                                                            _config(REFERENCE_HEIGHT, 0), pcm, None, timeout)
    entry["status"] = "success" if all(run["status"] == "success" for run in runs.values()) else "failed"
    if entry["status"] == "success":
        entry["nondeterministic"] = (runs[f"legacy-{REFERENCE_HEIGHT}"]["frames_sha256"]
                                     != runs[f"legacy-{REFERENCE_HEIGHT}-repeat"]["frames_sha256"])
        entry["ratio"] = luma_ratio(runs[f"legacy-{REFERENCE_HEIGHT}"]["mean_luma"],
                                    runs[f"quad-{REFERENCE_HEIGHT}"]["mean_luma"])
        others = sorted(h for h in heights if h != REFERENCE_HEIGHT)
        if len(others) == 2:
            low, high = others
            entry["drift"] = {mode: ladder_drift(runs[f"{mode}-{low}"]["mean_luma"], runs[f"{mode}-{high}"]["mean_luma"])
                              for mode in ("legacy", "quad")}
    return entry


def summarize(entries: list[dict], baseline: dict | None) -> dict:
    all_done = [e for e in entries if e["status"] == "success"]
    unstable = sorted(e["preset"] for e in all_done if e.get("nondeterministic"))
    done = [e for e in all_done if not e.get("nondeterministic")]
    measured = [e for e in done if e.get("ratio") is not None]
    deviations = [abs(e["ratio"] - 1) for e in measured]
    flagged = sorted(e["preset"] for e in measured if abs(e["ratio"] - 1) > FIDELITY_TOLERANCE)
    by_feature: dict[str, list[float]] = {}
    for e in measured:
        for feature in e["features"]:
            by_feature.setdefault(feature, []).append(e["ratio"])
    drift = {mode: [e["drift"][mode] for e in done if e.get("drift") and e["drift"][mode] is not None]
             for mode in ("legacy", "quad")}
    changed = []
    if baseline is not None:
        previous = {e["preset"]: e for e in baseline.get("presets", [])}
        for e in done:
            old_runs = previous.get(e["preset"], {}).get("runs", {})
            for key, run in sorted(e["runs"].items()):
                if key.startswith("legacy-") and not key.endswith("-repeat") and key in old_runs and old_runs[key].get("frames_sha256") != run["frames_sha256"]:
                    changed.append(f"{e['preset']} {key}")
    return {"version": VERSION, "presets": len(entries), "failed": len(entries) - len(all_done),
            "median_deviation": statistics.median(deviations) if deviations else None,
            "share_beyond_tolerance": len(flagged) / len(measured) if measured else None,
            "beyond_tolerance": flagged,
            "median_ratio_by_feature": {f: statistics.median(r) for f, r in sorted(by_feature.items())},
            "median_drift": {m: statistics.median(d) if d else None for m, d in drift.items()},
            "legacy_changed": changed, "nondeterministic": unstable}


def run_line_compare(records: list[PresetRecord], repo: Path, work: Path, worker: Path, identity: EngineIdentity,
                     heights: tuple[int, ...] = (1080, 720, 1440), baseline: dict | None = None,
                     concurrency: int = 1, timeout: float = 300) -> dict:
    if REFERENCE_HEIGHT not in heights:
        raise ValueError(f"the reference height {REFERENCE_HEIGHT} must be measured")
    signals = bass_signals(RunConfig(width=1920, height=1080, fps=30, warmup_seconds=WARMUP_SECONDS,
                                     measurement_seconds=MEASUREMENT_SECONDS), work / "signals")
    pcm = signals["bass-0.30"]
    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        entries = list(pool.map(lambda r: compare_preset(r, repo, work, worker, identity, heights, pcm, timeout), records))
    report = {"summary": summarize(entries, baseline), "presets": entries, "engine": asdict(identity)}
    work.mkdir(parents=True, exist_ok=True)
    (work / "report.json").write_text(canonical_json(report))
    return report
