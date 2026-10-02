import math
import re
import subprocess
from pathlib import Path

import numpy as np

from .identity import canonical_json, digest, file_digest, load_json
from .models import Corpus, TrackRecord

RATE = 44100
ALIASES = {"folk": "folk-acoustic", "hiphop": "hip-hop", "r&b": "rnb-soul"}
GENRES = tuple(g["id"] for g in load_json(Path(__file__).parent / "profiles/genres.json")["genres"])
BANDS = {"sub_bass": (20, 60), "bass": (60, 250), "mid": (250, 4000), "treble": (4000, 16000)}


def select_excerpts(duration: float) -> tuple[tuple[float, float], ...]:
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("audio duration must be positive and finite")
    if duration < 30:
        return ((0.0, duration),)
    if duration >= 120:
        return tuple((duration * fraction - 15, duration * fraction + 15)
                     for fraction in (0.25, 0.5, 0.75))
    count = min(3, int(duration // 30))
    return tuple((duration * (i + 0.5) / count - 15, duration * (i + 0.5) / count + 15)
                 for i in range(count))


def describe_audio(pcm: np.ndarray, sample_rate: int) -> dict:
    signal = np.asarray(pcm, dtype=np.float64)
    if signal.ndim != 1 or not len(signal) or not np.all(np.isfinite(signal)) or sample_rate <= 0:
        raise ValueError("invalid finite mono audio")
    duration = len(signal) / sample_rate
    window, hop = 2048, 1024
    analyzed = np.pad(signal, (0, max(0, window - len(signal))))
    blocks = np.lib.stride_tricks.sliding_window_view(analyzed, window)[::hop]
    rms = np.sqrt(np.mean(blocks * blocks, axis=1))
    power = np.abs(np.fft.rfft(blocks * np.hanning(window), axis=1)) ** 2
    frequencies = np.fft.rfftfreq(window, 1 / sample_rate)
    energies = {name: float(power[:, (frequencies >= low) & (frequencies < high)].sum())
                for name, (low, high) in BANDS.items()}
    total = sum(energies.values())
    balance = {name: value / total if total > 1e-10 else 0.0 for name, value in energies.items()}
    flux = np.r_[0.0, np.maximum(np.diff(power, axis=0), 0).sum(axis=1)]
    flux /= max(float(power.sum(axis=1).max()), 1e-10)
    threshold = max(0.03, float(np.median(flux) + 3 * np.median(np.abs(flux - np.median(flux)))))
    peaks = []
    for i in range(1, len(flux) - 1):
        time = (i * hop + window / 2) / sample_rate
        if (flux[i] > threshold and flux[i] >= flux[i - 1] and flux[i] > flux[i + 1]
                and rms[i] > rms[i - 1] * 1.01
                and (not peaks or time - peaks[-1] >= 0.08)):
            peaks.append(time)
    intervals = np.diff(peaks)
    period = None
    if len(intervals) >= 3 and float(np.std(intervals) / np.mean(intervals)) < 0.35:
        period = float(np.median(intervals))
    low, high = np.quantile(rms, (0.1, 0.9))
    dynamic = max(0.0, min(80.0, 20 * math.log10(max(float(high), 1e-8) / max(float(low), 1e-8))))
    return {"version": "audio-v1", "duration": duration, "rms": float(np.sqrt(np.mean(signal ** 2))),
            "peak": float(np.max(np.abs(signal))), "spectral_balance": balance,
            "onsets": peaks, "onset_density": len(peaks) / duration, "beat_period": period,
            "beat_period_method": "regular-onset intervals; not guaranteed metrical tempo",
            "dynamic_range_db": dynamic,
            "energy_variation": float(np.std(rms) / max(float(np.mean(rms)), 1e-8))}


def _decode(path: Path, cache: Path, decoder: str) -> tuple[Path, dict]:
    source_hash = file_digest(path)
    key = digest({"source": source_hash, "decoder": decoder, "rate": RATE,
                  "policy": "mono-preserve/stereo-mean/cancellation-left-v1"})
    mono, metadata_file = cache / f"{key}.f32", cache / f"{key}.json"
    if mono.is_file() and metadata_file.is_file():
        metadata = load_json(metadata_file)
        if mono.stat().st_size == metadata["samples"] * 4:
            return mono, metadata
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(path)],
                           text=True, capture_output=True)
    if probe.returncode:
        raise ValueError(f"cannot read audio {path.name}: {probe.stderr.strip()}")
    import json
    streams = [s for s in json.loads(probe.stdout)["streams"] if s["codec_type"] == "audio"]
    if not streams:
        raise ValueError(f"no audio stream in {path.name}")
    channels = 1 if streams[0]["channels"] == 1 else 2
    temporary = cache / f"{key}.stereo.tmp"
    result = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(path),
                             "-map", "0:a:0", "-vn", "-ar", str(RATE), "-ac", str(channels),
                             "-f", "f32le", str(temporary)], capture_output=True, text=True)
    if result.returncode or not temporary.is_file() or not temporary.stat().st_size:
        raise ValueError(f"cannot decode audio {path.name}: {result.stderr.strip()}")
    raw = np.memmap(temporary, dtype="<f4", mode="r").reshape(-1, channels)
    if not np.all(np.isfinite(raw)):
        raise ValueError(f"audio has non-finite samples: {path.name}")
    mixed = np.mean(raw, axis=1, dtype=np.float32)
    individual = float(np.sqrt(np.mean(raw.astype(np.float64) ** 2)))
    cancellation = channels == 2 and individual > 1e-5 and float(np.sqrt(np.mean(mixed ** 2))) < individual * 0.05
    if cancellation:
        mixed = np.array(raw[:, 0], copy=True)
    mixed.astype("<f4").tofile(mono)
    metadata = {"sha256": source_hash, "samples": len(mixed), "duration": len(mixed) / RATE,
                "sample_rate": RATE, "channels_in": streams[0]["channels"],
                "stereo_cancellation_detected": cancellation,
                "mixing": "left-channel-fallback" if cancellation else ("mono" if channels == 1 else "stereo-mean"),
                "decoder": decoder}
    del raw
    temporary.unlink()
    metadata_file.write_text(canonical_json(metadata))
    return mono, metadata


def load_corpus(root: Path, manifest: Path | None, cache: Path) -> Corpus:
    root, cache = root.resolve(), cache.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    decoder = subprocess.check_output(["ffmpeg", "-version"], text=True).splitlines()[0]
    if manifest:
        entries = load_json(manifest)["tracks"]
    else:
        paths = sorted(p for p in root.iterdir() if p.suffix.lower() in (".m4a", ".webm", ".wav", ".flac", ".mp3", ".ogg", ".opus", ".aac"))
        entries = [{"id": p.stem, "path": p.name,
                    "genres": [ALIASES.get(re.sub(r"\d+$", "", p.stem.lower()),
                                          re.sub(r"\d+$", "", p.stem.lower()))]}
                   for p in paths]
        references = {entry["path"]: entry for entry in load_json(
            Path(__file__).parent / "profiles/reference-corpus.json")["tracks"]}
        for entry in entries:
            reference = references.get(entry["path"], {})
            for field in ("title", "test_scenarios", "preferred"):
                if field in reference:
                    entry[field] = reference[field]
    if not entries:
        raise ValueError("audio corpus is empty")
    tracks, descriptors, ids, identities = [], {}, set(), []
    for entry in entries:
        track_id = entry["id"]
        genres = tuple(entry["genres"])
        if not track_id or track_id in ids or not genres or any(g not in GENRES for g in genres):
            raise ValueError("duplicate track ID or unknown/empty genre")
        ids.add(track_id)
        path = (root / entry["path"]).resolve()
        pcm_path, metadata = _decode(path, cache, decoder)
        raw = np.fromfile(pcm_path, dtype="<f4")
        excerpts = tuple(tuple(pair) for pair in entry.get("excerpts", select_excerpts(metadata["duration"])))
        if (not excerpts or any(len(pair) != 2 or not all(math.isfinite(float(x)) for x in pair)
            or not 0 <= pair[0] < pair[1] <= metadata["duration"] + 1e-6 for pair in excerpts)):
            raise ValueError(f"invalid excerpt bounds: {track_id}")
        excerpts = tuple((float(a), float(b)) for a, b in excerpts)
        source_stems, variants = {}, {}
        for source, relative in entry.get("stems", {}).items():
            if source not in ("drums", "bass_instrument", "melody", "vocals", "other"):
                raise ValueError(f"unsupported stem source: {source}")
            decoded, _ = _decode((root / relative).resolve(), cache, decoder)
            stem = np.fromfile(decoded, dtype="<f4")
            if len(stem) != len(raw):
                raise ValueError(f"stem must align with the full mix: {source}")
            source_stems[source] = stem
        variant_arrays = {f"without_{source}": raw - stem for source, stem in source_stems.items()}
        peak = max([float(np.max(np.abs(raw)))] + [float(np.max(np.abs(v))) for v in variant_arrays.values()])
        gain = min(1.0, 0.95 / peak) if peak else 1.0
        key = digest({"source": metadata["sha256"], "stems": {k: digest(v.tobytes().hex()) for k, v in source_stems.items()},
                      "gain": gain, "decoder": decoder})
        normalized = cache / f"{key}-mix.f32"
        (raw * gain).astype("<f4").tofile(normalized)
        for name, array in variant_arrays.items():
            output = cache / f"{key}-{name}.f32"
            (array * gain).astype("<f4").tofile(output)
            variants[name] = str(output)
        segment_features = []
        for start, end in excerpts:
            segment = raw[int(start * RATE):int(end * RATE)] * gain
            segment_features.append({"start": start, "end": end, "features": describe_audio(segment, RATE)})
        durations = np.array([s["end"] - s["start"] for s in segment_features])
        combined = {"version": "audio-v1", "pcm_path": str(normalized), "gain": gain,
                    "stereo_cancellation_detected": metadata["stereo_cancellation_detected"],
                    "mixing": metadata["mixing"], "stems_available": sorted(source_stems),
                    "variants": variants, "excerpts": segment_features, "evidence_level": "single-recording"}
        if entry.get("title") or entry.get("test_scenarios") or entry.get("preferred"):
            combined["reference"] = {"title": entry.get("title"),
                                      "test_scenarios": entry.get("test_scenarios", []),
                                      "preferred": bool(entry.get("preferred", False)),
                                      "provenance": "user-provided expectations"}
        for name in ("rms", "onset_density", "dynamic_range_db", "energy_variation"):
            combined[name] = float(np.average([s["features"][name] for s in segment_features], weights=durations))
        combined["spectral_balance"] = {band: float(np.average(
            [s["features"]["spectral_balance"][band] for s in segment_features], weights=durations)) for band in BANDS}
        periods = [s["features"]["beat_period"] for s in segment_features if s["features"]["beat_period"] is not None]
        combined["beat_period"] = float(np.median(periods)) if periods else None
        combined["onsets"] = [s["start"] + t for s in segment_features for t in s["features"]["onsets"]]
        record = TrackRecord(track_id, path, genres, metadata["sha256"], metadata["duration"], excerpts)
        tracks.append(record)
        descriptors[track_id] = combined
        identities.append({"id": track_id, "source": record.sha256, "genres": genres,
                           "excerpts": excerpts, "stems_and_gain": key,
                           "preferred": bool(entry.get("preferred", False))})
    identity = digest({"tracks": identities, "decoder": decoder, "feature_code": file_digest(Path(__file__))})
    return Corpus(tuple(tracks), descriptors, identity)
