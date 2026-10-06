"""Colour math controls are independent of preset renders or image labels."""
import colorsys
import importlib
import math

import numpy as np
import pytest


def palette(values, **settings):
    return importlib.import_module('palette_features').palette_summary(values, **settings)


def rgb(hue):
    return colorsys.hsv_to_rgb(hue/360, 1, 1)


@pytest.mark.parametrize('hue, expected', [(0, 1), (30, 1), (60, 1),
                                         (120, 0), (180, -1), (240, -1), (300, 0)])
def test_warm_cool_sectors_keep_green_and_purple_neutral(hue, expected):
    result = palette([rgb(hue)])
    assert result['warm_cool'] == pytest.approx(expected, abs=2e-6)
    assert result['chromatic_support'] == 1


def test_achromatic_samples_have_no_warmth_or_hue_entropy():
    result = palette([[0, 0, 0], [.5, .5, .5]])
    assert result['warm_cool'] is None
    assert result['hue_entropy_nats'] is None
    assert result['effective_hue_bins'] is None
    assert result['chromatic_support'] == 0


def test_query_weights_change_palette_mass_without_counting_grey_as_cold():
    result = palette([[1, 0, 0], [0, 0, 1], [.5, .5, .5]], weights=[3, 1, 4])
    assert result['warm_cool'] == pytest.approx(.5)
    assert result['chromatic_support'] == .5


def test_hue_entropy_is_in_nats_and_effective_bins_are_separate():
    result = palette([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    assert result['hue_entropy_nats'] == pytest.approx(math.log(3))
    assert result['effective_hue_bins'] == pytest.approx(3)


def test_large_finite_query_weights_do_not_overflow():
    result = palette([[1, 0, 0], [0, 0, 1]], weights=[1e308, 1e308])
    assert result['warm_cool'] == pytest.approx(0)
    assert result['chromatic_support'] == 1


def test_large_finite_histogram_is_normalized_before_entropy():
    module = importlib.import_module('palette_features')
    assert module.hue_entropy([1e308, 1e308]) == pytest.approx(math.log(2))


def test_underflowing_positive_query_weight_is_explicitly_unresolved():
    with pytest.raises(ValueError, match='underflow'):
        palette([[1, 0, 0], [.5, .5, .5]], weights=[1e-308, 1e308])


def test_subnormal_chromatic_weight_keeps_its_chromatic_relative_warmth():
    result = palette([rgb(111), [.5, .5, .5]], weights=[5e-324, 1])
    assert result['warm_cool'] == pytest.approx(math.cos(math.pi*21/60), abs=2e-6)


def test_circular_hue_rate_takes_the_short_path_across_red():
    module = importlib.import_module('palette_features')
    result = module.hue_change_summary([rgb(359)], [rgb(1)], dt=.1)
    assert result['p95_cycles_per_second'] == pytest.approx(2/360/.1, rel=1e-4)
    assert result['matched_chromatic_fraction'] == 1


def test_hue_changes_exclude_grey_even_with_large_arbitrary_hue_shifts():
    module = importlib.import_module('palette_features')
    result = module.hue_change_summary([[.5, .5, .5]], [[1, 0, 0]], dt=.1)
    assert result['p95_cycles_per_second'] is None
    assert result['matched_chromatic_fraction'] == 0


@pytest.mark.parametrize('values, settings', [
    ([[float('nan'), 0, 0]], {}), ([[2, 0, 0]], {}),
    ([[1, 0, 0]], {'weights': [-1]}), ([[1, 0, 0]], {'weights': [0]}),
    ([[1, 0, 0]], {'hue_bins': True}),
])
def test_invalid_colour_inputs_are_not_summarized(values, settings):
    with pytest.raises(ValueError):
        palette(values, **settings)
