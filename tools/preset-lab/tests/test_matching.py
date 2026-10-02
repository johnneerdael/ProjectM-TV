from dataclasses import replace
from pathlib import Path

import pytest

from preset_lab.identity import load_json
from preset_lab.matching import match_presets
from preset_lab.models import Corpus, Fingerprint, PresetRecord, TrackRecord


def profiles():
    root = Path(__file__).parents[1] / "src/preset_lab/profiles"
    return load_json(root / "genres.json"), load_json(root / "audience-home.json")


def candidate(name, motion=0.2, smoothness=0.85, flash=0.02, response=0.8, eligible=True):
    return Fingerprint(PresetRecord(name, name[0] * 64, 0),
        {"spectral_response": {band: response for band in ("sub_bass", "bass", "mid", "treble")}},
        {"motion_speed": motion, "structural_motion": motion, "smoothness": smoothness,
         "persistence": 0.8, "flashiness": flash, "color_vibrancy": 0.6, "contrast": 0.5,
         "chaos": 1-smoothness, "beat_lock": response, "canvas_coverage": 0.9},
        {"eligible": eligible, "reasons": [] if eligible else ["low_visibility"]}, {})


def corpus(genre_ids):
    tracks = tuple(TrackRecord(g, Path(f"{g}.wav"), (g,), "f"*64, 30, ((0,30),)) for g in genre_ids)
    descriptors = {g: {"spectral_balance": {"sub_bass": 0.1, "bass": 0.3, "mid": 0.4, "treble": 0.2},
                       "onset_density": 3 if g == "dance" else 0.2} for g in genre_ids}
    return Corpus(tracks, descriptors, "f"*64)


def test_automatic_decisions_cover_all_genres_without_ratings():
    genres, audience = profiles()
    ids = [g["id"] for g in genres["genres"]]
    result = match_presets([candidate("calm.milk"), candidate("dance.milk", .6, .6)],
                           corpus(ids), genres, audience)
    assert {r.genre_id for r in result} == set(ids)
    assert all(r.evidence_state == "predicted" for r in result)
    assert len({r.genre_id for r in result if r.preset.path == "calm.milk" and r.included}) > 1


def test_quiet_persistent_beats_frantic_flashing_for_ambient():
    genres, audience = profiles()
    result = match_presets([candidate("calm.milk"), candidate("frantic.milk", .95, .05, .95)],
                           corpus(["ambient"]), genres, audience)
    ambient = {r.preset.path: r for r in result if r.genre_id == "ambient"}
    assert ambient["calm.milk"].score > ambient["frantic.milk"].score
    assert ambient["calm.milk"].included
    assert not ambient["frantic.milk"].included


def test_reactive_beats_intrinsic_only_motion_for_dance():
    genres, audience = profiles()
    result = match_presets([candidate("reactive.milk", .6, .6, .1, .9),
                            candidate("intrinsic.milk", .6, .6, .1, 0)],
                           corpus(["dance"]), genres, audience)
    dance = {r.preset.path: r for r in result if r.genre_id == "dance"}
    assert dance["reactive.milk"].music_fit > dance["intrinsic.milk"].music_fit
    assert dance["reactive.milk"].score > dance["intrinsic.milk"].score


def test_failed_quality_is_never_rescued_by_high_fit_or_override():
    genres, audience = profiles()
    fp = candidate("tiny.milk", eligible=False)
    overrides = {f"{fp.preset.sha256}:ambient": {"decision": "include", "reason": "test"}}
    result = match_presets([fp], corpus(["ambient"]), genres, audience, overrides)
    assert not any(r.included for r in result)


def test_audience_rescoring_changes_only_audience_contribution():
    genres, audience = profiles()
    fp = candidate("calm.milk", flash=.2)
    first = match_presets([fp], corpus(["ambient"]), genres, audience)
    changed = dict(audience, targets=dict(audience["targets"], flashiness=.7))
    second = match_presets([fp], corpus(["ambient"]), genres, changed)
    assert first[0].music_fit == second[0].music_fit
    assert first[0].audience_fit != second[0].audience_fit


def test_missing_nonfinite_response_cannot_become_a_valid_match():
    genres, audience = profiles()
    fp = candidate("invalid.milk")
    fp.raw["spectral_response"]["bass"] = float("nan")
    with pytest.raises(ValueError):
        match_presets([fp], corpus(["dance"]), genres, audience)


def test_exclusion_override_persists_by_content_identity():
    genres, audience = profiles()
    fp = candidate("calm.milk")
    overrides = {f"{fp.preset.sha256}:ambient": {"decision":"exclude", "reason":"personal preference"}}
    result = match_presets([fp], corpus(["ambient"]), genres, audience, overrides)
    ambient = next(r for r in result if r.genre_id == "ambient")
    assert not ambient.included
    assert ambient.evidence_state == "reviewed"
    assert match_presets([fp], corpus(["ambient"]), genres, audience, overrides) == result


def test_favourite_reference_influences_acoustic_matching():
    genres, audience = profiles()
    tracks = tuple(TrackRecord(str(i), Path(f"{i}.wav"), ("dance",), "f"*64,30,((0,30),)) for i in (1,2))
    descriptors = {"1":{"spectral_balance":{"bass":1},"onset_density":0},
                   "2":{"spectral_balance":{"mid":1},"onset_density":0,"reference":{"preferred":True}}}
    data = Corpus(tracks,descriptors,"f"*64)
    fp = candidate("bass.milk")
    fp.raw["spectral_response"].update(bass=1,mid=0)
    preferred = match_presets([fp],data,genres,audience)
    descriptors["2"]["reference"]["preferred"] = False
    equal = match_presets([fp],data,genres,audience)
    assert next(r for r in preferred if r.genre_id=="dance").music_fit < next(r for r in equal if r.genre_id=="dance").music_fit


def test_successful_render_counts_do_not_claim_music_tested_fit():
    genres, audience = profiles()
    fp = candidate("calm.milk")
    fp.evidence["music_validation"] = [{"genre_id":"ambient","track_sha256":"f"*64,"status":"success"}]
    result = match_presets([fp],corpus(["ambient"]),genres,audience)
    assert result[0].evidence_state == "predicted"


def test_missing_spectral_response_cannot_be_included():
    genres, audience = profiles()
    fp = candidate("missing.milk")
    fp.raw["spectral_response"]["bass"] = None
    result = match_presets([fp],corpus(["dance"]),genres,audience)
    assert not result[0].included


def test_cached_match_cli_never_calls_renderer(tmp_path,monkeypatch,capsys):
    import json
    from dataclasses import asdict
    from preset_lab.cli import main
    import preset_lab.worker
    def forbidden(*args,**kwargs):
        raise AssertionError("match must not render")
    monkeypatch.setattr(preset_lab.worker,"render_job",forbidden)
    fp=candidate("calm.milk")
    fingerprint_file=tmp_path/"fingerprint.json"
    fingerprint_file.write_text(json.dumps(asdict(fp)))
    data=corpus(["ambient"])
    corpus_file=tmp_path/"corpus.json"
    corpus_file.write_text(json.dumps({"identity":data.identity,"descriptors":data.descriptors,
        "tracks":[dict(asdict(t),path=str(t.path)) for t in data.tracks]}))
    assert main(["match","--fingerprints",str(fingerprint_file),"--corpus",str(corpus_file)]) == 0
    output=json.loads(capsys.readouterr().out)
    assert output["decisions"][0]["genre_id"]=="ambient"
    assert output["render_jobs"]==0


def test_music_observed_flashes_control_audience_inclusion():
    genres,audience=profiles()
    fp=candidate("calm.milk")
    observed=dict(fp.normalized,flashiness=.95)
    fp.evidence["music_validation"]=[{"genre_id":"ambient","track_sha256":"f"*64,
        "track_id":"ambient","status":"success","music_fit":.9,"observed_features":observed}]
    result=match_presets([fp],corpus(["ambient"]),genres,audience)
    assert result[0].evidence_state=="music-tested"
    assert not result[0].included


def test_music_tested_rank_is_distinct_from_a_higher_unchecked_prediction():
    genres,audience=profiles()
    predicted=candidate("predicted.milk")
    tested=candidate("tested.milk")
    tested.evidence["music_validation"]=[{"genre_id":"ambient","track_sha256":"f"*64,
        "track_id":"ambient","status":"success","music_fit":.3,
        "observed_features":dict(tested.normalized,motion_speed=.4)}]
    results=match_presets([predicted,tested],corpus(["ambient"]),genres,audience)
    assert results[0].preset.path=="tested.milk"
    assert results[0].evidence_state=="music-tested"
    assert results[0].score<results[1].score
