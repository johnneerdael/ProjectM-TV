import json
import wave
import subprocess
import cv2

import numpy as np
import pytest

from preset_lab.audio import describe_audio, load_corpus, select_excerpts


def write_wave(path, pcm, rate=44100):
    samples = np.asarray(pcm)
    if samples.ndim == 1:
        samples = samples[:, None]
    with wave.open(str(path), "wb") as file:
        file.setnchannels(samples.shape[1])
        file.setsampwidth(2)
        file.setframerate(rate)
        file.writeframes((samples * 32767).astype("<i2").tobytes())


def test_short_tracks_are_not_padded_or_repeated():
    assert select_excerpts(10) == ((0.0, 10.0),)
    assert select_excerpts(65) == ((1.25, 31.25), (33.75, 63.75))
    assert select_excerpts(240) == ((45.0, 75.0), (105.0, 135.0), (165.0, 195.0))


def test_silence_has_no_invented_beat_or_spectral_energy():
    features = describe_audio(np.zeros(44100, dtype=np.float32), 44100)
    assert features["rms"] == 0
    assert features["onsets"] == []
    assert features["beat_period"] is None
    assert sum(features["spectral_balance"].values()) == 0


def test_tonal_and_regular_attack_descriptors_are_measured():
    times = np.arange(4 * 44100) / 44100
    tone = 0.4 * np.sin(2 * np.pi * 80 * times)
    features = describe_audio(tone, 44100)
    assert features["spectral_balance"]["bass"] > 0.9
    attacks = tone * ((times % 0.5) < 0.1)
    features = describe_audio(attacks, 44100)
    assert len(features["onsets"]) >= 6
    assert features["beat_period"] == pytest.approx(0.5, abs=0.04)


def test_aliases_decode_and_cancellation_is_not_called_silence(tmp_path):
    root, cache = tmp_path / "audio", tmp_path / "cache"
    root.mkdir()
    names = ["ambient", "classical", "country", "dance", "folk", "hiphop", "jazz",
             "latin", "pop", "r&b", "reggae", "rock"]
    times = np.arange(44100) / 44100
    signal = 0.2 * np.sin(2 * np.pi * 440 * times)
    for name in names:
        write_wave(root / f"{name}.wav", np.column_stack((signal, -signal)))
    corpus = load_corpus(root, None, cache)
    assert {g for track in corpus.tracks for g in track.genre_ids} == {
        "ambient", "classical", "country", "dance", "folk-acoustic", "hip-hop", "jazz",
        "latin", "pop", "rnb-soul", "reggae", "rock"
    }
    assert all(d["stereo_cancellation_detected"] for d in corpus.descriptors.values())
    assert all(d["rms"] > 0.1 for d in corpus.descriptors.values())
    assert all(d["stems_available"] == [] for d in corpus.descriptors.values())
    assert load_corpus(root, None, cache).identity == corpus.identity


def test_explicit_paths_with_punctuation_and_excerpt_bounds(tmp_path):
    path = tmp_path / "John's café & rain.wav"
    write_wave(path, np.zeros(44100))
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"tracks": [{"id": "custom", "path": path.name,
                                               "genres": ["ambient"], "excerpts": [[0.2, 0.8]]}]}))
    corpus = load_corpus(tmp_path, manifest, tmp_path / "cache")
    assert corpus.tracks[0].excerpts == ((0.2, 0.8),)
    manifest.write_text(json.dumps({"tracks": [{"id": "custom", "path": path.name,
                                               "genres": ["ambient"], "excerpts": [[0.8, 2]]}]}))
    with pytest.raises(ValueError, match="excerpt"):
        load_corpus(tmp_path, manifest, tmp_path / "cache")


def test_corrupt_audio_fails_as_audio_error(tmp_path):
    (tmp_path / "dance.m4a").write_bytes(b"not an audio file")
    with pytest.raises(ValueError, match="audio"):
        load_corpus(tmp_path, None, tmp_path / "cache")


def test_attached_album_art_is_excluded_from_decoding(tmp_path):
    times = np.arange(44100) / 44100
    source = tmp_path / "source.wav"
    write_wave(source, 0.3 * np.sin(2 * np.pi * 440 * times))
    cover = tmp_path / "cover.jpg"
    cv2.imwrite(str(cover), np.full((16, 16, 3), 255, np.uint8))
    root = tmp_path / "audio"
    root.mkdir()
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(source),
                    "-i", str(cover), "-map", "0:a:0", "-map", "1:v:0", "-c:a", "aac",
                    "-c:v", "mjpeg", "-disposition:v", "attached_pic", str(root / "dance.m4a")],
                   check=True)
    corpus = load_corpus(root, None, tmp_path / "cache")
    assert len(corpus.tracks) == 1
    assert corpus.tracks[0].duration == pytest.approx(1, abs=0.05)
    assert corpus.descriptors["dance"]["rms"] > 0.15


def test_numbered_webm_samples_remain_in_the_same_broad_genre(tmp_path):
    source = tmp_path / "source.wav"
    write_wave(source, np.sin(np.arange(44100) * 0.03) * 0.2)
    root = tmp_path / "audio"
    root.mkdir()
    for number in (2, 3):
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(source),
                        "-c:a", "libopus", str(root / f"ambient{number}.webm")], check=True)
    corpus = load_corpus(root, None, tmp_path / "cache")
    assert [track.id for track in corpus.tracks] == ["ambient2", "ambient3"]
    assert [track.genre_ids for track in corpus.tracks] == [("ambient",), ("ambient",)]


def test_reference_annotations_are_not_measured_features(tmp_path):
    write_wave(tmp_path / "ambient.wav", np.zeros(44100))
    manifest = tmp_path / "reference.json"
    manifest.write_text(json.dumps({"tracks": [{"id": "ambient", "path": "ambient.wav",
        "genres": ["ambient"], "title": "Sparse reference", "test_scenarios": ["isolated_transients"]}]}))
    corpus = load_corpus(tmp_path, manifest, tmp_path / "cache")
    reference = corpus.descriptors["ambient"]["reference"]
    assert reference["title"] == "Sparse reference"
    assert reference["test_scenarios"] == ["isolated_transients"]
    assert reference["provenance"] == "user-provided expectations"
    assert corpus.descriptors["ambient"]["onset_density"] == 0


def test_stems_must_align_and_share_variant_gain(tmp_path):
    times = np.arange(44100) / 44100
    drums = 0.9 * np.sin(2 * np.pi * 80 * times)
    vocals = -0.7 * np.sin(2 * np.pi * 80 * times)
    write_wave(tmp_path / "mix.wav", drums + vocals)
    write_wave(tmp_path / "drums.wav", drums)
    write_wave(tmp_path / "vocals.wav", vocals)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"tracks": [{"id": "test", "path": "mix.wav",
        "genres": ["pop"], "stems": {"drums": "drums.wav", "vocals": "vocals.wav"}}]}))
    corpus = load_corpus(tmp_path, manifest, tmp_path / "cache")
    descriptor = corpus.descriptors["test"]
    variants = descriptor["variants"]
    mix = np.fromfile(descriptor["pcm_path"], dtype="<f4")
    no_drums = np.fromfile(variants["without_drums"], dtype="<f4")
    assert np.max(np.abs(no_drums)) / np.max(np.abs(mix)) == pytest.approx(3.5, rel=0.01)
    write_wave(tmp_path / "vocals.wav", vocals[:10000])
    with pytest.raises(ValueError, match="align"):
        load_corpus(tmp_path, manifest, tmp_path / "cache")
