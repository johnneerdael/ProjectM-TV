"""Measure bass-caused screen changes by executing the actual projectM engine.

Scores describe a fixed experiment, not a proof over every possible audio input.
Source-code heuristics never contribute to the screen score.
"""

from dataclasses import asdict
import hashlib
from pathlib import Path
import tempfile
import sys

import numpy as np

from .cache import read_cached_run, write_atomic
from .identity import digest, file_digest
from .models import EngineIdentity, JobSpec, PresetRecord, RunConfig
from .worker import render_job, validate_job

VERSION = "bass-screen-v1"
CODE_SHA256 = file_digest(Path(__file__))
AREA_THRESHOLD = 8 / 255
LEVELS = (.05, .15, .30)


def pixel_response(frame: np.ndarray, control: np.ndarray) -> dict:
    """M = mean RGB difference; A = fraction with difference above 8/255.

    M combines area and intensity without rewarding a bright, tiny element.
    Translation, deformation, color, brightness and shader effects all count.
    """
    if (frame.dtype != np.uint8 or control.dtype != np.uint8
            or frame.ndim != 3 or frame.shape[-1] != 3 or frame.shape != control.shape):
        raise ValueError("matched RGB uint8 frames required")
    difference = np.abs(frame.astype(np.float32) - control.astype(np.float32)).mean(axis=2) / 255
    affected = difference > AREA_THRESHOLD
    return {"magnitude": float(difference.mean()), "affected_area": float(affected.mean()),
            "local_intensity": float(difference[affected].mean()) if affected.any() else 0.}


def summarize_response(trajectory: list[dict], fps: float) -> dict:
    if not trajectory or fps <= 0:
        raise ValueError("nonempty screen trajectory and positive frame rate required")
    magnitude = np.array([f["magnitude"] for f in trajectory])
    peak = float(np.quantile(magnitude, .95))
    peak_index = int(np.argmin(np.abs(magnitude - peak)))
    # Latency uses the first pulse only: later feedback cannot establish onset.
    first = magnitude[:round(fps)]
    threshold = max(.002, float(first.max()) * .1)
    arrivals = np.flatnonzero(first > threshold)
    return {"peak_magnitude": peak, "mean_magnitude": float(magnitude.mean()),
            "area_at_peak": trajectory[peak_index]["affected_area"],
            "intensity_at_peak": trajectory[peak_index]["local_intensity"],
            "mean_affected_area": float(np.mean([f["affected_area"] for f in trajectory])),
            "first_pulse_peak_magnitude": float(np.quantile(first, .95)),
            "first_response_seconds": float(arrivals[0] / fps) if len(arrivals) else None}


def bass_signals(config: RunConfig, destination: Path) -> dict[str, Path]:
    """Identical carrier plus deterministic 20–250 Hz noise kick bursts.

    Test three amplitudes so a threshold or saturated response is observable.
    Burst onset every second, 10 ms attack, 120 ms decay. No mix normalization.
    """
    count = round((config.warmup_seconds + config.measurement_seconds) * 44100)
    time = np.arange(count) / 44100
    carrier = sum(.04 * np.sin(2 * np.pi * frequency * time) for frequency in (80, 440, 5000))
    spectrum = np.fft.rfft(np.random.default_rng(config.seed).standard_normal(count))
    frequencies = np.fft.rfftfreq(count, 1 / 44100)
    spectrum[(frequencies < 20) | (frequencies > 250)] = 0
    bass = np.fft.irfft(spectrum, n=count)
    bass /= max(float(np.max(np.abs(bass))), 1e-12)
    relative = np.maximum(time - config.warmup_seconds, 0) % 1
    envelope = np.minimum(relative / .01, 1) * np.exp(-relative / .12)
    envelope *= time >= config.warmup_seconds
    destination.mkdir(parents=True, exist_ok=True)
    result = {}
    for name, level in [("control", 0), *[(f"bass-{level:.2f}", level) for level in LEVELS]]:
        path = destination / f"{name}-{digest(asdict(config))[:12]}.f32"
        (carrier + level * envelope * bass).astype('<f4').tofile(path)
        result[name] = path
    return result


def measure_preset_bass(record: PresetRecord, repo: Path, work: Path, worker: Path,
                        identity: EngineIdentity, config: RunConfig = RunConfig(),
                        signals: dict[str, Path] | None = None, timeout: float = 120) -> dict:
    preset_root = repo / "core/src/main/assets/presets"
    textures = repo / "core/src/main/assets/textures"
    if file_digest(preset_root / record.path) != record.sha256:
        raise ValueError(f"stale preset identity: {record.path}")
    signals = signals or bass_signals(config, work / "signals")
    dependencies = {"version": VERSION, "code": CODE_SHA256,
                    "preset": asdict(record), "config": asdict(config), "engine": asdict(identity),
                    "worker": file_digest(worker), "audio": {n: file_digest(p) for n, p in signals.items()},
                    "textures_sha256": digest([(p.name, file_digest(p)) for p in sorted(textures.iterdir())
                                               if p.is_file() and p.name != '.DS_Store'])}
    key = digest(dependencies)
    target = work / "cache" / f"{key}.json"
    cached = read_cached_run(target, key)
    if cached is not None:
        return dict(cached, reused=True, render_jobs=0)
    result = {"status": "unknown", "preset": asdict(record), "protocol": dependencies,
              "reused": False, "render_jobs": 0, "reasons": [], "levels": {}, "score": None,
              "score_units": "mean RGB difference across whole screen, 0..1",
              "area_threshold": AREA_THRESHOLD,
              "limitations": "Measured response for these signals, duration, seed and renderer; not all possible songs or states."}
    warmup = round(config.warmup_seconds * config.fps)
    work.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bass-frames-", dir=work) as directory:
        control_path = Path(directory) / "control.rgb"
        control = None
        hashes = {}
        for variant in ["control", "repeat", *[f"bass-{level:.2f}" for level in LEVELS]]:
            pcm = signals["control" if variant == "repeat" else variant]
            job = JobSpec(record, variant, pcm, config, identity, preset_root, textures, work / "jobs")
            expected = validate_job(job, timeout)
            full_hash, prefix = hashlib.sha256(), hashlib.sha256()
            trajectory = []
            index = 0
            output = control_path.open('wb') if variant == "control" else None
            def observe(frame):
                nonlocal index
                data = frame.tobytes()
                full_hash.update(data)
                if index < warmup:
                    prefix.update(data)
                if output is not None:
                    output.write(data)
                elif variant != "repeat" and index >= warmup:
                    trajectory.append(pixel_response(frame, control[index]))
                index += 1
            try:
                rendered = render_job(worker, job, observe, timeout)
            finally:
                if output is not None:
                    output.close()
            result["render_jobs"] += 1
            log = rendered.diagnostics_path.read_text(errors="replace")
            warnings = [line for line in log.splitlines() if any(term in line.lower() for term in
                        ("unable to load", "could not load", "failed to load", "warning"))]
            if rendered.status != "success" or warnings:
                result["reasons"].append(f"{variant}:render_failure_or_compatibility_warning")
                result["diagnostics"] = str(rendered.diagnostics_path)
                break
            hashes[variant] = (full_hash.hexdigest(), prefix.hexdigest())
            if variant == "control":
                control = np.memmap(control_path, dtype='u1', mode='r',
                                    shape=(expected, config.height, config.width, 3))
            elif hashes[variant][1] != hashes["control"][1]:
                result["reasons"].append("pre_intervention_drift")
                break
            elif variant == "repeat":
                if hashes[variant][0] != hashes["control"][0]:
                    result["reasons"].append("non_repeatable_control")
                    break
            else:
                result["levels"][variant] = summarize_response(trajectory, config.fps)
        if control is not None:
            del control
    if not result["reasons"]:
        result["status"] = "success"
        # Only measured pixels affect ranking; area is already included in M.
        result["score"] = float(np.mean([v["peak_magnitude"] for v in result["levels"].values()]))
        result["control_repeat_identical"] = True
        write_atomic(target, {"key": key, "run": result, "payload_sha256": digest(result)})
    return result


def scan_bass_screen(records: list[PresetRecord], repo: Path, work: Path, worker: Path,
                     identity: EngineIdentity, config: RunConfig = RunConfig()) -> dict:
    signals = bass_signals(config, work / "signals")
    results = []
    render_jobs = 0
    def snapshot(status):
        ranked = sorted([r for r in results if r['status'] == 'success'],
                        key=lambda r: (-r['score'], r['preset']['path']))
        return {"schema_version": 1, "protocol_version": VERSION, "status": status,
                "requested_presets": len(records), "completed_presets": len(results),
                "render_jobs": render_jobs, "reused_presets": sum(r['reused'] for r in results),
                "unknown_presets": sum(r['status'] == 'unknown' for r in results),
                "ranking_total": len(ranked), "ranking": ranked[:100],
                "measurements_directory": str(work / 'measurements'),
                "unknown": [{"preset":r['preset'], "reasons":r['reasons']}
                            for r in results if r['status'] == 'unknown']}
    write_atomic(work / 'ranking.json', snapshot('running'))
    try:
        for record in records:
            result = measure_preset_bass(record, repo, work, worker, identity, config, signals)
            results.append(result)
            render_jobs += result['render_jobs']
            write_atomic(work / 'measurements' / f'{digest(asdict(record))}.json', result)
            write_atomic(work / 'ranking.json', snapshot('running'))
            print(f"bass screen {len(results)}/{len(records)}: {record.path}: "
                  f"{result['status']} score={result['score']}", file=sys.stderr, flush=True)
    except KeyboardInterrupt:
        write_atomic(work / 'ranking.json', snapshot('interrupted'))
        raise
    report = snapshot('complete')
    write_atomic(work / 'ranking.json', report)
    return report
