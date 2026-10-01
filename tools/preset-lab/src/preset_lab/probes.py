from dataclasses import asdict
from pathlib import Path

import numpy as np

from .identity import digest, file_digest
from .models import RunConfig


def make_probes(config: RunConfig, destination: Path) -> list[dict]:
    if config.fps not in (30, 60) or config.warmup_seconds < 0 or config.measurement_seconds <= 0:
        raise ValueError("invalid probe timing")
    duration = config.warmup_seconds + config.measurement_seconds
    times = np.arange(round(duration * 44100)) / 44100
    carrier = sum(0.04 * np.sin(2 * np.pi * f * times) for f in (80, 440, 5000))
    intervention = times >= config.warmup_seconds
    relative = np.maximum(0, times - config.warmup_seconds)
    pulse = (relative % 0.5) < 0.2
    signals = {"steady": carrier.copy(), "silence": np.where(intervention, 0, carrier)}
    for band, frequency in (("sub_bass", 35), ("bass", 80), ("mid", 1000), ("treble", 8000)):
        signals[band] = carrier + intervention * pulse * 0.15 * np.sin(2 * np.pi * frequency * times)
    envelope = np.exp(-(relative % 0.5) * 25)
    signals["attack"] = carrier + intervention * envelope * 0.12 * np.sin(2 * np.pi * 440 * times)
    signals["sustained"] = carrier + intervention * (relative < config.measurement_seconds / 2) * 0.15 * np.sin(2 * np.pi * 220 * times)
    signals["amplitude_modulation"] = carrier + intervention * 0.12 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * relative)) * np.sin(2 * np.pi * 440 * times)
    for name, period in (("tempo_slow", 1.0), ("tempo_fast", 0.25)):
        signals[name] = carrier + intervention * ((relative % period) < period * 0.25) * 0.15 * np.sin(2 * np.pi * 80 * times)
    destination.mkdir(parents=True, exist_ok=True)
    probes = []
    for name, signal in signals.items():
        path = destination / f"{name}-{digest(asdict(config))[:12]}.f32"
        signal.astype("<f4").tofile(path)
        probes.append({"id": name, "pcm_path": str(path), "sha256": file_digest(path),
                       "warmup_seconds": config.warmup_seconds, "measurement_seconds": config.measurement_seconds,
                       "audio_path": config.audio_path, "sample_rate": 44100})
    return probes
