import math
from pathlib import Path

from .identity import load_json

from .models import Corpus, Fingerprint, MatchDecision, PresetRecord, TrackRecord


def load_fingerprints(path: Path) -> list[Fingerprint]:
    files = sorted(path.glob("*-fingerprint.json")) if path.is_dir() else [path]
    if path.is_dir() and not files:
        files = sorted(path.glob("*.json"))
    results = []
    for file in files:
        value = load_json(file)
        if not isinstance(value, dict) or not {"preset", "raw", "normalized", "quality", "evidence"} <= value.keys():
            raise ValueError(f"not a fingerprint record: {file.name}")
        results.append(Fingerprint(PresetRecord(**value["preset"]), value["raw"], value["normalized"],
                                   value["quality"], value["evidence"]))
    if not results:
        raise ValueError("no cached fingerprints")
    return results


def load_cached_corpus(path: Path) -> Corpus:
    data = load_json(path)
    records = tuple(TrackRecord(t["id"], Path(t["path"]), tuple(t["genre_ids"]), t["sha256"],
                               t["duration"], tuple(tuple(p) for p in t["excerpts"])) for t in data["tracks"])
    return Corpus(records, data["descriptors"], data["identity"])


def _finite(value) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("non-finite matching input")
    return value


def _style(values: dict, targets: dict, weights: dict) -> tuple[float, dict, list]:
    terms, missing, total = {}, [], 0.0
    for field, target in targets.items():
        if values.get(field) is None:
            missing.append(field)
            continue
        weight = _finite(weights.get(field, 1))
        if weight <= 0:
            raise ValueError("matching weights must be positive")
        fit = max(0.0, 1 - abs(_finite(values[field]) - _finite(target)))
        terms[field] = weight * fit
        total += weight
    return (sum(terms.values()) / total if total else 0), terms, missing


def match_presets(fingerprints: list[Fingerprint], corpus: Corpus, genre_profiles: dict,
                  audience_profile: dict, overrides: dict | None = None) -> list[MatchDecision]:
    decisions = []
    preferred_weight = _finite(audience_profile.get("preferred_reference_weight", 2))
    if preferred_weight <= 0:
        raise ValueError("preferred reference weight must be positive")
    for genre in genre_profiles["genres"]:
        genre_id = genre["id"]
        references = [track for track in corpus.tracks if genre_id in track.genre_ids]
        if not references:
            continue
        for fp in fingerprints:
            music_terms, reference_details, weight_sum = [], [], 0.0
            for track in references:
                audio = corpus.descriptors[track.id]
                response = fp.raw.get("spectral_response", {})
                spectral_sum = 0.0
                band_sum = 0.0
                missing_bands = []
                for band, weight in audio["spectral_balance"].items():
                    weight = _finite(weight)
                    if weight < 0:
                        raise ValueError("negative spectral weight")
                    if response.get(band) is None:
                        missing_bands.append(band)
                        continue
                    value = _finite(response[band])
                    spectral_sum += weight * max(0.0, min(1.0, value))
                    band_sum += weight
                spectral = spectral_sum / band_sum if band_sum else 0.0
                onset_need = min(1.0, max(0.0, _finite(audio.get("onset_density", 0)) / 3))
                beat = fp.normalized.get("beat_lock")
                temporal = 1 - onset_need + onset_need * (_finite(beat) if beat is not None else 0)
                value = 0.75 * spectral + 0.25 * temporal
                weight = preferred_weight if audio.get("reference", {}).get("preferred") else 1.0
                music_terms.append(value * weight)
                weight_sum += weight
                reference_details.append({"id": track.id, "source_sha256": track.sha256,
                                          "weight": weight, "spectral_fit": spectral,
                                          "temporal_fit": temporal, "missing_bands": missing_bands})
            music_fit = sum(music_terms) / weight_sum
            style_fit, style_terms, missing_style = _style(
                fp.normalized, genre["targets"], genre_profiles.get("style_weights", {}))
            audience_fit, audience_terms, missing_audience = _style(
                fp.normalized, audience_profile["targets"], audience_profile.get("weights", {}))
            current_hashes = {track.sha256 for track in references}
            observations = [item for item in fp.evidence.get("music_validation", [])
                            if item.get("genre_id") == genre_id and item.get("track_sha256") in current_hashes
                            and item.get("status") == "success" and item.get("music_fit") is not None
                            and item.get("observed_features")]
            evidence_state = "predicted"
            if observations:
                reference_weights={item["id"]:item["weight"] for item in reference_details}
                weights=[reference_weights.get(item.get("track_id"),1.0) for item in observations]
                total=sum(weights)
                music_fit = sum(weight*_finite(item["music_fit"]) for weight,item in zip(weights,observations)) / total
                styles=[_style(item["observed_features"],genre["targets"],genre_profiles.get("style_weights",{}))
                        for item in observations]
                audiences=[_style(item["observed_features"],audience_profile["targets"],audience_profile.get("weights",{}))
                           for item in observations]
                style_fit=sum(w*s[0] for w,s in zip(weights,styles))/total
                audience_fit=sum(w*a[0] for w,a in zip(weights,audiences))/total
                style_terms={field:sum(w*s[1].get(field,0) for w,s in zip(weights,styles))/total
                             for field in genre["targets"]}
                audience_terms={field:sum(w*a[1].get(field,0) for w,a in zip(weights,audiences))/total
                                for field in audience_profile["targets"]}
                evidence_state = "music-tested"
            genre_fit = 0.45 * music_fit + 0.55 * style_fit
            score = 0.7 * genre_fit + 0.3 * audience_fit
            limit_values=[item["observed_features"] for item in observations] if observations else [fp.normalized]
            limits_ok = all(values.get(field) is not None and _finite(values[field]) <= _finite(limit)
                            for values in limit_values for field,limit in audience_profile.get("maximums",{}).items())
            measurements_present = all(not r["missing_bands"] for r in reference_details)
            included = bool(fp.quality.get("eligible") and limits_ok and measurements_present
                            and score >= _finite(genre.get("minimum_score", 0.47))
                            and music_fit >= _finite(genre.get("minimum_music_fit", 0.05)))
            override = (overrides or {}).get(f"{fp.preset.sha256}:{genre_id}")
            if override:
                if override.get("decision") not in ("include", "exclude"):
                    raise ValueError("unknown review override decision")
                included = override["decision"] == "include" and bool(fp.quality.get("eligible"))
                evidence_state = "reviewed"
            contributions = {"genre_style_fit": style_fit, "genre_style_terms": style_terms,
                             "audience_terms": audience_terms, "genre_fit": genre_fit,
                             "score_terms": {"music": 0.7 * 0.45 * music_fit,
                                             "style": 0.7 * 0.55 * style_fit, "audience": 0.3 * audience_fit},
                             "references": reference_details, "missing_style": missing_style,
                             "required_music_measurements_present": measurements_present,
                             "missing_audience": missing_audience, "limits_ok": limits_ok,
                             "quality": fp.quality, "override": override,
                             "music_test_count": len(observations),
                             "independent_validation": "unavailable",
                             "score_kind": "bounded preference fit"}
            decisions.append(MatchDecision(fp.preset, genre_id, music_fit, audience_fit,
                                           score, included, evidence_state, contributions))
    levels={"reviewed":2,"music-tested":1,"predicted":0}
    return sorted(decisions,key=lambda d:(d.genre_id,-levels[d.evidence_state],-d.score,d.preset.path.encode("utf-8")))
