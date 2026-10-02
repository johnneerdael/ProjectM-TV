import math

import numpy as np

from .models import Fingerprint, PresetRecord, StaticEvidence

METRIC_VERSION = "visual-v1"


def _correlation(left: np.ndarray, right: np.ndarray) -> float:
    if len(left) < 3 or np.std(left) < 1e-10 or np.std(right) < 1e-10:
        return 0.0
    return float(np.corrcoef(left, right)[0, 1])


def beat_coupling(events: np.ndarray, onset_frames: list[int], fps: float) -> dict:
    events = np.asarray(events, dtype=np.float64)
    reference = np.zeros(len(events))
    for frame in onset_frames:
        if 0 <= frame < len(events):
            reference[frame] = 1
    if reference.sum() < 3 or np.std(events) < 1e-10:
        return {"strength": 0.0, "lag_seconds": None, "correlation": 0.0,
                "control_correlation": 0.0, "available": bool(reference.sum() >= 3)}
    lags = range(min(int(fps * 0.5) + 1, len(events) // 3))
    correlations = [_correlation(events[lag:], reference[:len(events) - lag]) for lag in lags]
    lag = int(np.argmax(correlations))
    observed = max(0.0, correlations[lag])
    rng = np.random.default_rng(123)
    controls = []
    for _ in range(20):
        surrogate = rng.permutation(reference)
        controls.append(_correlation(events[lag:], surrogate[:len(events) - lag]))
    for fraction in (0.137, 0.293, 0.419, 0.617):
        shifted = np.roll(reference, max(1, int(len(events) * fraction)))
        controls.append(_correlation(events[lag:], shifted[:len(events) - lag]))
    control = max(0.0, float(np.median(controls)))
    return {"strength": max(0.0, min(1.0, observed - control)), "lag_seconds": lag / fps,
            "correlation": observed, "control_correlation": control, "available": True}


def _series(run: dict, field: str, trim: bool = True) -> np.ndarray:
    frames = run.get("frames", [])
    if trim:
        frames = frames[run.get("warmup_frames", 0):]
    return np.array([float(frame.get(field, 0)) for frame in frames], dtype=np.float64)


def _effect(candidate: dict, control: dict) -> tuple[float, np.ndarray]:
    parts = []
    for field, scale in (("brightness", 0.1), ("contrast", 0.1), ("saturation", 0.25),
                         ("edge_energy", 0.05), ("motion_speed", 0.25), ("coverage", 0.25)):
        left, right = _series(candidate, field), _series(control, field)
        length = min(len(left), len(right))
        if not length:
            return 0.0, np.zeros(0)
        parts.append(np.minimum(np.abs(left[:length] - right[:length]) / scale, 4))
    trajectory = np.sqrt(np.mean(np.array(parts) ** 2, axis=0))
    visibility = math.sqrt(float(np.mean(_series(candidate, "coverage"))))
    return float((1 - math.exp(-float(np.mean(trajectory)))) * visibility), trajectory


def fingerprint(preset: PresetRecord, trajectories: dict, static: StaticEvidence) -> Fingerprint:
    steady = trajectories.get("steady", {})
    failed = [name for name, run in trajectories.items() if run.get("status") != "success"]
    reasons = [f"render_failure:{name}" for name in failed]
    warnings = sorted({warning for run in trajectories.values() for warning in run.get("warnings", [])})
    if warnings:
        reasons.append("compatibility_warning")
    base = _series(steady, "coverage")
    if not len(base):
        reasons.append("missing_steady_measurement")
        base = np.zeros(1)
    visible_conditions = [_series(run, "coverage") for name, run in trajectories.items()
                          if name != "silence" and run.get("status") == "success" and len(_series(run, "coverage"))]
    blank_ratio = min((float(np.mean(values < 0.001)) for values in visible_conditions), default=1.0)
    if blank_ratio > 0.8:
        reasons.append("low_visibility")
    # All matched interventions must be identical before their onset.
    warmup = steady.get("warmup_frames", 0)
    for name, run in trajectories.items():
        if name == "steady" or run.get("status") != "success":
            continue
        if steady.get("prefix_sha256") and run.get("prefix_sha256") != steady["prefix_sha256"]:
            reasons.append("pre_intervention_drift")
        for field in ("brightness", "coverage", "saturation", "motion_speed"):
            a, b = _series(run, field, False)[:warmup], _series(steady, field, False)[:warmup]
            if len(a) != len(b) or (len(a) and not np.allclose(a, b, atol=1e-8, rtol=0)):
                reasons.append("pre_intervention_drift")
                break
    spectral, events, locks = {}, {}, []
    for name in ("sub_bass", "bass", "mid", "treble"):
        run = trajectories.get(name)
        if run and run.get("status") == "success" and steady.get("status") == "success":
            value, variation = _effect(run, steady)
            spectral[name] = value
            events[name] = variation
            cue_frames = [round(time * run["fps"]) - run.get("warmup_frames", 0)
                          for time in run.get("onsets", [])]
            event_energy = np.r_[0, np.maximum(np.diff(variation), 0)] if len(variation) else variation
            locks.append(beat_coupling(event_energy, cue_frames, run["fps"]))
        else:
            spectral[name] = None
            reasons.append(f"missing_spectral_measurement:{name}")
    sources = {}
    full = trajectories.get("music_full")
    for source in ("drums", "bass_instrument", "melody", "vocals"):
        removed = trajectories.get(f"without_{source}")
        sources[source] = _effect(full, removed)[0] if full and removed and full.get("status") == removed.get("status") == "success" else None
    fps = float(steady.get("fps", 30))
    brightness = _series(steady, "brightness")
    speed = _series(steady, "motion_speed")
    flash_rates = []
    for name, run in trajectories.items():
        if name == "silence" or run.get("status") != "success":
            continue
        luminance = _series(run, "brightness")
        color = _series(run, "color_change")
        if len(luminance) > 1:
            flash_rates.append(float(np.mean((np.abs(np.diff(luminance)) > 0.08)
                                            | (color[1:] > 0.08)) * run.get("fps", fps)))
    acceleration = np.diff(speed) * fps if len(speed) > 1 else np.zeros(1)
    jerk = np.diff(acceleration) * fps if len(acceleration) > 1 else np.zeros(1)
    def mean(field):
        values = _series(steady, field)
        return float(np.mean(values)) if len(values) else 0.0
    persistence = None
    if trajectories.get("sustained", {}).get("status") == "success":
        _, difference = _effect(trajectories["sustained"], steady)
        half = len(difference) // 2
        if half and float(np.mean(difference[:half])) > 1e-8:
            persistence = min(1.0, float(np.mean(difference[half:]) / np.mean(difference[:half])))
    behavior = {"brightness": mean("brightness"), "contrast": mean("contrast"),
                "edge_energy": mean("edge_energy"), "color_vibrancy": mean("saturation"),
                "canvas_coverage": mean("coverage"), "motion_speed": mean("motion_speed"),
                "motion_density": mean("motion_density"), "motion_irregularity": mean("motion_residual"),
                "rotation": mean("rotation"), "radial_expansion": mean("expansion"),
                "translation_x": mean("translation_x"), "translation_y": mean("translation_y"),
                "acceleration": float(np.mean(np.abs(acceleration))), "jerk": float(np.mean(np.abs(jerk))),
                "flash_events_per_second": max(flash_rates, default=0.0),
                "persistence": persistence, "beat_lock": max([lock["strength"] for lock in locks], default=0.0)}
    normalized = {"brightness": behavior["brightness"], "contrast": min(1.0, behavior["contrast"] * 3),
                  "edge_sharpness": math.tanh(behavior["edge_energy"] * 8),
                  "color_vibrancy": behavior["color_vibrancy"], "canvas_coverage": behavior["canvas_coverage"],
                  "motion_speed": math.tanh(behavior["motion_speed"] * 2),
                  "motion_density": behavior["motion_density"], "structural_motion": math.tanh(
                      (abs(behavior["rotation"]) + abs(behavior["radial_expansion"])
                       + math.hypot(behavior["translation_x"], behavior["translation_y"])) * 2),
                  "flashiness": 1 - math.exp(-behavior["flash_events_per_second"] / 3),
                  "smoothness": 1 / (1 + behavior["jerk"]),
                  "chaos": math.tanh(behavior["motion_irregularity"] * 3),
                  "persistence": persistence, "beat_lock": behavior["beat_lock"]}
    measurement_seconds = len(base) / fps
    active_runs = [run for name, run in trajectories.items() if name != "silence" and run.get("status") == "success"]
    flat_static = bool(active_runs) and all(
        len(_series(run, "brightness")) and float(np.mean(_series(run, "contrast"))) < 0.003
        and float(np.mean(_series(run, "motion_speed"))) < 0.002
        and float(np.std(_series(run, "brightness"))) < 0.003
        and float(np.mean(_series(run, "frame_change"))) < 1e-5 for run in active_runs)
    if flat_static:
        reasons.append("flat_static_output")
    quality = {"eligible": not reasons, "reasons": sorted(set(reasons)),
               "blank_ratio": blank_ratio, "clipping_ratio": mean("clipping_ratio"),
               "render_errors": len(failed), "warnings": warnings,
               "requires_extension": not failed and "pre_intervention_drift" not in reasons
                                     and (blank_ratio > 0.2 or max((float(np.mean(v)) for v in visible_conditions), default=0) < 0.02 or flat_static)
                                     and measurement_seconds < 60}
    raw = {"spectral_response": spectral, "source_response": sources, "behavior": behavior,
           "source_unavailable_reasons": {source: "aligned full-mix/source-removal experiment unavailable"
                                          for source, value in sources.items() if value is None},
           "beat_evidence": locks, "source_unavailable_reason": "aligned stem experiments not supplied" if not full else None}
    evidence = {"metric_version": METRIC_VERSION, "normalization_version": "fixed-visual-v1",
                "static": {"complete": static.complete, "paths": static.paths, "unsupported": static.unsupported},
                "units": {"flow": "viewport units/second", "rotation": "affine curl proxy/second",
                          "expansion": "affine scale rate/second", "luminance": "Rec.709 RGB weighted, 0..1"}}
    return Fingerprint(preset, raw, normalized, quality, evidence)
