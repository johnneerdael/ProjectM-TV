"""Source-level material changes do not certify displayed flashing."""
import numpy as np
import pytest
from test_effect_families import read
from test_source_appearance import appearance


def material(body):
    d=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\nshape_0_per_frame1='+body+'\n'))
    s=next(e for e in d['elements'] if e['id']=='shape_0')
    assert 'material_temporal' in s, 'native material temporal export is missing'
    return s['material_temporal']


def test_constant_material_uses_actual_native_modulo_not_original_packed_bytes():
    m=material('r=1.1;a=.5;')
    c=m['channels']['r']
    from primitives import colour_modulo
    assert c['native_value_if_singleton']==float(colour_modulo(1.1))
    assert c['possible_native_wrap_jump'] is False
    assert m['visible_flashing'] is None


def test_safe_slow_colour_oscillation_has_nominal_rate_without_wrap():
    c=material('r=.5+.2*sin(.1*time);')['channels']['r']
    assert c['raw_time_curve']['maximum_absolute_control_rate_per_second']==pytest.approx(.02)
    assert c['possible_native_wrap_jump'] is False
    assert c['raw_time_curve']['period_seconds']==pytest.approx(20*np.pi)


def test_colour_and_opacity_crossing_modulo_period_report_possible_jumps():
    m=material('r=1+.1*sin(time);a=1+.1*cos(time);')
    assert m['channels']['r']['possible_native_wrap_jump'] is True
    assert m['channels']['a']['possible_native_wrap_jump'] is True
    assert m['possible_consumed_wrap_jump'] is True


def test_negative_near_zero_interval_accounts_for_native_addition_rounding():
    c=material('r=-.00000006+.00000004*sin(time);')['channels']['r']
    assert c['possible_native_wrap_jump'] is True


def test_zero_lower_endpoint_does_not_invent_a_negative_side_wrap():
    c=material('r=.5+.5*sin(time);')['channels']['r']
    assert c['possible_native_wrap_jump'] is False


def test_unresolved_audio_and_state_channels_keep_wrap_unknown():
    m=material('r=bass;g=k;')
    assert m['channels']['r']['possible_native_wrap_jump'] is None
    assert m['channels']['g']['possible_native_wrap_jump'] is None
    assert m['possible_consumed_wrap_jump'] is None


def test_border_gate_uses_raw_alpha_and_actual_native_threshold():
    m=material('border_a=.0001+.00002*sin(time);')
    assert m['border_gate']['possible_state_change'] is True
    assert m['border_gate']['nominal_always_enabled'] is None
    assert m['border_gate']['threshold']==float(np.float32(.0001))


def test_disabled_border_colour_risk_does_not_make_consumed_risk():
    m=material('border_a=0;border_r=1+.1*sin(time);')
    assert m['channels']['border_r']['possible_native_wrap_jump'] is True
    assert m['channels']['border_r']['may_be_consumed'] is False
    assert m['possible_consumed_wrap_jump'] is False


def test_border_alpha_modulo_is_separate_from_raw_draw_gate():
    m=material('border_a=-.2;')
    assert m['border_gate']['nominal_always_enabled'] is False
    assert m['channels']['border_a']['native_value_if_singleton']>0


def test_float32_singleton_domain_can_freeze_a_tiny_source_oscillation():
    c=material('r=.5+1e-10*sin(time);')['channels']['r']
    assert c['native_endpoint_domain_singleton'] is True
    assert c['native_value_if_singleton']==float(np.float32(.5))
    assert c['possible_native_wrap_jump'] is False


def test_known_float32_overflow_does_not_receive_material_certificate():
    c=material('r=1e40;')['channels']['r']
    assert c['possible_native_wrap_jump'] is None
    assert c['native_value_if_singleton'] is None
    assert c['unknown_reasons']


def test_no_native_frame_or_visible_flash_frequency_is_invented():
    m=material('r=1+.1*sin(time);')
    assert m['uses_equation_execution'] is False
    assert m['uses_rendered_images'] is False
    assert m['visible_flash_frequency_hz'] is None


def test_transparent_fan_colours_do_not_make_consumed_risk():
    m=material('a=0;a2=0;border_a=.2;r=1+.1*sin(time);')
    assert m['channels']['r']['possible_native_wrap_jump'] is True
    assert m['channels']['r']['may_be_consumed'] is False
    assert m['possible_consumed_wrap_jump'] is False


def test_transparent_centre_still_affects_fan_with_nonzero_edge_alpha():
    m=material('a=0;a2=.2;border_a=0;r=1+.1*sin(time);')
    assert m['channels']['r']['may_be_consumed'] is True
    assert m['possible_consumed_wrap_jump'] is True
