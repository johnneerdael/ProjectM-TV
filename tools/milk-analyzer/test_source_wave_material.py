"""Native built-in waveform material controls, without frames/audio history."""
import pytest
from test_effect_families import read
from test_source_appearance import appearance


def material(body='',config=''):
    d=appearance(read('fWaveAlpha=.8\nnWaveMode=0\n'+config+'per_frame_1='+body+'\n'))
    e=next(e for e in d['elements'] if e['id']=='builtin_wave')
    assert 'wave_material' in e,'built-in waveform material missing'
    return e['wave_material']


def test_rgb_clamps_before_optional_normalization_and_never_shape_wraps():
    r=material('wave_r=2;wave_g=-.2;wave_b=.5;wave_brighten=0;')
    assert r['constant_vertex_rgb']==[1,0,.5]
    assert r['colour_conversion']=='float32 clamp0..1 then optional maximum normalization'
    assert r['possible_normalization_gate_jump'] is False


def test_constant_normalized_rgb_is_exported_without_final_palette_claim():
    r=material('wave_r=.2;wave_g=.4;wave_b=.1;wave_brighten=1;')
    assert r['constant_vertex_rgb']==pytest.approx([.5,1,.25])
    assert r['final_palette_verified'] is False


def test_smooth_dim_colour_can_cross_hard_normalization_gate():
    r=material('wave_r=.01+.005*sin(time);wave_g=0;wave_b=0;wave_brighten=1;')
    assert r['possible_normalization_gate_jump'] is True
    assert r['normalization_gate']['threshold']==pytest.approx(.01,abs=1e-9)
    assert r['visible_flashing'] is None


def test_above_threshold_colour_does_not_gain_gate_jump():
    r=material('wave_r=.5+.1*sin(time);wave_g=.2;wave_b=.1;wave_brighten=1;')
    assert r['possible_normalization_gate_jump'] is False


def test_equality_at_native_gate_threshold_keeps_unscaled_rgb():
    r=material('wave_r=.01;wave_g=0;wave_b=0;wave_brighten=1;')
    assert r['constant_vertex_rgb']==pytest.approx([.01,0,0],abs=1e-9)


def test_bounded_audio_colour_keeps_unknown_timing():
    r=material('wave_r=.5+.5*sin(bass);wave_g=.2;wave_b=.1;wave_brighten=0;')
    assert r['channels']['wave_r']['raw_time_curve']['maximum_absolute_control_rate_per_second'] is None
    assert r['rgb_component_envelopes'][0]==pytest.approx([0,1],abs=1e-7)


def test_mode_one_alpha_boost_is_before_final_clamp():
    r=material('wave_mode=1;wave_a=.4;')
    assert r['alpha_recipe']['mode_gain']==pytest.approx(1.25)
    assert r['alpha_recipe']['alpha_envelope_without_volume_modulation']==pytest.approx([.5,.5],abs=1e-7)


def test_mode_three_discards_authored_alpha_and_declares_native_treble_input():
    r=material('wave_mode=3;wave_a=0;')
    assert r['channels']['wave_a']['consumed'] is False
    assert r['alpha_recipe']['authored_alpha_replaced'] is True
    assert r['alpha_recipe']['audio_input']=='native_audioData.treb'
    assert r['alpha_recipe']['alpha_envelope_without_volume_modulation'] is None


def test_volume_ramp_keeps_unbounded_ramp_before_final_clamp():
    r=material(config='bModWaveAlphaByVolume=1\nfModWaveAlphaStart=.75\nfModWaveAlphaEnd=.95\n')
    v=r['alpha_recipe']['volume_ramp']
    assert v['enabled'] is True
    assert v['ramp_clamped_before_multiplication'] is False
    assert v['input']=='native_audioData.vol'
    assert r['alpha_recipe']['final_alpha_envelope'] is None


def test_zero_volume_denominator_remains_unresolved_even_zero_authored_alpha():
    r=material('wave_a=0;wave_mode=3;',config='bModWaveAlphaByVolume=1\nfModWaveAlphaStart=.5\nfModWaveAlphaEnd=.5\n')
    assert r['alpha_recipe']['volume_ramp']['domain_status']=='unknown'
    assert r['alpha_recipe']['unknown_reasons']


def test_unknown_normalization_flag_is_not_a_no_jump_certificate():
    r=material('wave_brighten=above(bass,1);')
    assert r['possible_normalization_gate_jump'] is None


def test_nonfinite_rgb_conversion_remains_unknown():
    r=material('wave_r=1e40;wave_brighten=0;')
    assert r['constant_vertex_rgb'] is None
    assert r['channels']['wave_r']['native_float32_endpoint_domain'] is None


def test_volume_denominator_overflow_keeps_other_material_data():
    r=material(config='bModWaveAlphaByVolume=1\nfModWaveAlphaStart=-3e38\nfModWaveAlphaEnd=3e38\n')
    assert r['alpha_recipe']['volume_ramp']['domain_status']=='unknown'
    assert r['constant_vertex_rgb']==[1,1,1]


def test_disabled_volume_ramp_cannot_invalidate_known_authored_alpha():
    r=material(config='bModWaveAlphaByVolume=0\nfModWaveAlphaStart=-3e38\nfModWaveAlphaEnd=3e38\n')
    assert r['alpha_recipe']['final_alpha_envelope']==pytest.approx([.8,.8],abs=1e-7)


def test_hardware_points_share_material_alpha_gate_before_dot_scale():
    r=material('wave_usedots=1;wave_a=.002;')
    assert 'native_draw_gate' in r
    assert r['native_draw_gate']['paths']==['quad_lines','hardware_lines_or_points']
    assert r['native_draw_gate']['before_scaled_dot_alpha'] is True
