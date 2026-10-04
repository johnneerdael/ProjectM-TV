import importlib
import importlib.util

import pytest


def policy():
    assert importlib.util.find_spec('audience_policy') is not None, 'Audience policy is not implemented'
    return importlib.import_module('audience_policy')


@pytest.mark.parametrize('score,expected', [
    (0, ['Chill']), (24.99, ['Chill']),
    (25, ['Chill', 'Normal']), (30, ['Chill', 'Normal']),
    (30.01, ['Normal']), (50, ['Normal']), (69.99, ['Normal']),
    (70, ['Normal', 'Party']), (75, ['Normal', 'Party']),
    (75.01, ['Party']), (100, ['Party']),
])
def test_user_intensity_bands_and_overlap_boundaries(score, expected):
    assert policy().labels_for_intensity(score) == expected


def test_unresolved_intensity_does_not_become_a_normal_classification():
    assert policy().labels_for_intensity(None) == []


@pytest.mark.parametrize('score', [-1, 101, float('nan'), float('inf'), True, '50'])
def test_invalid_intensity_cannot_receive_an_audience_label(score):
    module = policy()
    with pytest.raises(ValueError):
        module.labels_for_intensity(score)


@pytest.mark.parametrize('score,judgment,expected', [
    (28, 'Chill', True), (28, 'Normal', True), (28, 'Party', False),
    (72, 'Normal', True), (72, 'Party', True), (72, 'Chill', False),
    (30.01, 'Chill', False), (24.99, 'Normal', False),
    (69.99, 'Party', False), (75.01, 'Normal', False),
])
def test_correctness_means_score_inside_the_human_category_band(score, judgment, expected):
    assert policy().score_matches_judgment(score, judgment) is expected


def test_unknown_score_is_unscored_not_a_successful_band_match():
    assert policy().score_matches_judgment(None, 'Party') is None


def test_unknown_audience_name_cannot_be_used_as_validation_truth():
    with pytest.raises(ValueError):
        policy().score_matches_judgment(50, 'Midpoint')


@pytest.mark.parametrize('score,judgment,error', [(28, 'Chill', 0), (72, 'Normal', 0),
                                              (35, 'Chill', 5), (65, 'Party', 5),
                                              (20, 'Normal', 5), (80, 'Normal', 5)])
def test_band_error_is_measured_in_percentage_points(score, judgment, error):
    assert policy().score_band_error(score, judgment) == error


def test_five_point_tolerance_does_not_change_the_category_mapping():
    module=policy()
    assert module.labels_for_intensity(35) == ['Normal']
    assert module.score_matches_judgment(35, 'Chill', tolerance=5) is True
    assert module.score_matches_judgment(35.01, 'Chill', tolerance=5) is False
    assert module.score_matches_judgment(65, 'Party', tolerance=5) is True
    assert module.score_matches_judgment(64.99, 'Party', tolerance=5) is False


def test_unknown_score_has_unknown_band_error_even_with_tolerance():
    assert policy().score_band_error(None, 'Party') is None
    assert policy().score_matches_judgment(None, 'Party', tolerance=5) is None
