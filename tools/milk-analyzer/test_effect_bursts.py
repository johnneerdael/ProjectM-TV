import importlib
import importlib.util

import pytest


def measure(times, areas, **options):
    assert importlib.util.find_spec('effect_bursts') is not None, 'Effect burst measurement is not implemented'
    return importlib.import_module('effect_bursts').measure_bursts(times, areas, **options)


def test_contiguous_effects_form_one_burst_with_known_duration_and_area():
    report = measure([0, .1, .2, .3, .4], [0, .2, .4, 0, .1], area_threshold=.1)
    assert report['burst_count'] == 2
    first = report['bursts'][0]
    assert first['start_seconds'] == .1
    assert first['duration_seconds'] == pytest.approx(.2)
    assert first['peak_affected_area'] == .4
    assert first['left_censored'] is False
    assert first['right_censored'] is False
    assert report['bursts'][1]['right_censored'] is True


def test_constant_influence_is_not_counted_as_repeated_flashing():
    report = measure([0, .1, .2, .3], [.5, .5, .5, .5], area_threshold=.1)
    assert report['burst_count'] == 1
    assert report['uncensored_onsets'] == 0
    assert report['onset_rate_hz'] == 0
    assert report['bursts'][0]['left_censored'] is True
    assert report['bursts'][0]['right_censored'] is True


def test_zero_influence_has_zero_bursts():
    report = measure([0, .1, .2], [0, 0, 0], area_threshold=.1)
    assert report['burst_count'] == 0
    assert report['duty_fraction'] == 0


def test_irregular_sample_times_are_rejected_instead_of_inventing_a_frequency():
    with pytest.raises(ValueError, match='uniform'):
        measure([0, .1, .4], [0, .5, 0], area_threshold=.1)


@pytest.mark.parametrize('times,areas', [([0, .1], [0]), ([0, 0], [0, .5]),
                                      ([0, .1], [0, float('nan')]), ([0, .1], [0, 1.1])])
def test_invalid_trace_cannot_be_reported_as_calm(times, areas):
    with pytest.raises(ValueError):
        measure(times, areas, area_threshold=.1)
