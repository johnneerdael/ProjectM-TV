"""Nominal source-time crossing schedules do not certify native flashes."""
import math
import pytest
from test_source_material_temporal import material
from source_material_temporal import PERIOD


def schedule(body):return material(body)['channels']['r']['nominal_modulo_schedule']


def test_affine_colour_drift_has_one_crossing_per_modulo_period():
    r=schedule('r=.25*time;')
    assert r['nominal_crossing_event_rate_hz']==pytest.approx(.25/PERIOD)
    assert r['period_seconds']==pytest.approx(4*PERIOD)
    assert r['native_event_timing_verified'] is False
    assert r['visible_flash_frequency_hz'] is None


def test_single_boundary_sine_has_two_crossings_per_cycle():
    r=schedule('r=1+.1*sin(time);')
    assert r['strict_boundary_count']==1
    assert r['nominal_crossing_event_rate_hz']==pytest.approx(1/math.pi)
    assert len(r['crossings'][0]['event_offsets_seconds_mod_period'])==2


def test_multiple_crossed_cells_are_counted_without_merging_channels():
    r=schedule('r=2+2*sin(3*time);')
    assert r['strict_boundary_count']==3
    assert r['nominal_crossing_event_rate_hz']==pytest.approx(9/math.pi)


def test_negative_slope_and_cosine_phase_keep_nonnegative_cadence():
    r=schedule('r=.3-.25*time;')
    assert r['nominal_crossing_event_rate_hz']==pytest.approx(.25/PERIOD)
    r=schedule('r=1-.1*cos(-2*time+.5);')
    assert r['nominal_crossing_event_rate_hz']==pytest.approx(2/math.pi)
    assert all(0<=x<r['period_seconds'] for x in r['crossings'][0]['event_offsets_seconds_mod_period'])


@pytest.mark.parametrize('body',['r=bass;','r=k;','r=int(time);','r=.5;'])
def test_unknown_discrete_or_constant_input_does_not_get_periodic_crossing_rate(body):
    assert schedule(body)['nominal_crossing_event_rate_hz'] is None


def test_excessive_crossing_count_stays_explicitly_unquantified():
    r=schedule('r=100*sin(time);')
    assert r['nominal_crossing_event_rate_hz'] is None
    assert r['unknown_reasons']


def test_float32_frozen_channel_does_not_claim_native_crossing_schedule():
    r=schedule('r=1.003921627998352+1e-12*sin(time);')
    assert r['nominal_crossing_event_rate_hz'] is None
