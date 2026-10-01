import numpy as np

from preset_lab.models import RunConfig
from preset_lab.probes import make_probes


def test_all_probes_share_exact_warmup_and_have_complete_frames(tmp_path):
    config = RunConfig(measurement_seconds=2)
    probes = make_probes(config, tmp_path)
    signals = {item["id"]: np.fromfile(item["pcm_path"], dtype="<f4") for item in probes}
    assert {"silence", "steady", "sub_bass", "bass", "mid", "treble", "attack", "sustained",
            "tempo_slow", "tempo_fast"} <= signals.keys()
    baseline = signals["steady"]
    for signal in signals.values():
        assert signal.size == 6 * 44100
        assert np.array_equal(signal[:4 * 44100], baseline[:4 * 44100])
        assert np.all(np.isfinite(signal))
        assert np.max(np.abs(signal)) < 1
    assert np.all(signals["silence"][4 * 44100:] == 0)
    assert not np.array_equal(signals["bass"], baseline)


def test_interventions_do_not_independently_normalize_the_carrier(tmp_path):
    probes = make_probes(RunConfig(measurement_seconds=2), tmp_path)
    signals = {item["id"]: np.fromfile(item["pcm_path"], dtype="<f4") for item in probes}
    # The middle of the off-pulse interval is unchanged, including absolute gain.
    start, end = int(4.3 * 44100), int(4.45 * 44100)
    assert np.array_equal(signals["bass"][start:end], signals["steady"][start:end])
