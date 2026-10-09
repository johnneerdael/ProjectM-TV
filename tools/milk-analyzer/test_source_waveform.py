"""Static native waveform construction descriptors, without audio samples."""
import math
import pytest
from test_effect_families import read,shader,analyze
from test_source_appearance import appearance


def wave(extra=''):
    d=appearance(read('fWaveAlpha=1\n'+extra))
    return next((e for e in d['elements'] if e['id']=='builtin_wave'),None)


def test_circle_recipe_has_sample_channels_smoothing_and_native_mode():
    w=wave('nWaveMode=0\n')['waveform_recipe']
    assert w['effective_mode']==0
    assert w['form_name']=='audio_deformed_circle'
    assert w['geometry_closed_endpoint'] is True
    assert w['path_topology']=='strip'
    assert w['hardware_draw_primitive'] is None
    assert w['audio_inputs']==['waveform_right']
    assert w['base_radius_model_units']==.5
    assert w['sample_radial_gain']==pytest.approx(.4)
    assert w['nominal_rotation_rad_per_second']==pytest.approx(.2)
    assert w['actual_screen_coverage'] is None


def test_mode_conversion_matches_target_signed_remainder_and_truncation():
    w=wave('per_frame_1=wave_mode=16.9;\n')['waveform_recipe']
    assert w['effective_mode']==0
    assert 'circular_wave_primitive' in wave('per_frame_1=wave_mode=16.9;\n')['mechanisms']
    assert wave('per_frame_1=wave_mode=-1;\n') is None


def test_unknown_dot_flag_does_not_invent_a_line_only_family():
    w=wave('per_frame_1=wave_usedots=bass;\n')
    assert w['waveform_recipe']['hardware_draw_primitive'] is None
    assert w['waveform_recipe']['dots'] is None


def test_two_channel_line_preserves_separation_and_orientation_controls():
    w=wave('nWaveMode=7\nfWaveParam=.5\nwave_y=.3\n')['waveform_recipe']
    assert w['form_name']=='two_channel_parallel_traces'
    assert w['path_count']==2
    assert w['audio_inputs']==['waveform_left','waveform_right']
    assert w['line_angle_rad']==pytest.approx(1.57*.5,abs=2e-7)
    assert w['separation_normal_offset']==pytest.approx(.3**2,abs=2e-7)


def test_dot_and_nonzero_negative_flags_follow_evaluated_native_draw():
    w=wave('per_frame_1=wave_usedots=-.1;wave_additive=-1;\n')['waveform_recipe']
    assert w['hardware_draw_primitive']=='points'
    assert w['additive'] is True


def test_spectrum_and_stereo_inputs_are_not_audio_stems():
    w=wave('nWaveMode=8\n')['waveform_recipe']
    assert w['audio_inputs']==['spectrum_left']
    assert w['form_name']=='angled_log_spectrum_trace'
    assert w['audio_instrument_identity'] is None


def test_dynamic_mode_keeps_geometry_unknown_and_mode_audio_route():
    w=wave('per_frame_1=wave_mode=bass;\n')
    assert w['waveform_recipe']['effective_mode'] is None
    assert w['waveform_recipe']['form_name'] is None
    assert any(r['input_code']==1 and r['control']=='wave_mode' for r in w['audio_routes'])


def test_source_independent_composite_removes_disconnected_native_wave():
    record=analyze(read('fWaveAlpha=1\nPSVERSION_COMP=2\ncomp_1=`shader_body{ret=float3(.2,.3,.4);}\n'))
    assert not any(e['id']=='builtin_wave' for e in record['visual_description']['elements'])


def test_mode_three_opacity_policy_prevents_false_zero_alpha_omission():
    d=appearance(read('fWaveAlpha=0\nnWaveMode=3\n'))
    w=next(e for e in d['elements'] if e['id']=='builtin_wave')
    assert w['waveform_recipe']['effective_mode']==3
    assert w['waveform_recipe']['source_alpha_policy']=='reference coefficient*1.3*treb^2 before volume ramp; authored wave_a is replaced'
    assert 'builtin_wave' in d['composition']['configured_drawing_order']


def test_unknown_mode_with_zero_alpha_is_uncertain_not_proven_disabled():
    d=appearance(read('fWaveAlpha=0\nper_frame_1=wave_mode=bass;\n'))
    assert any(e['id']=='builtin_wave' for e in d['elements'])


def test_extended_unwritten_secondary_storage_does_not_claim_one_actual_path():
    w=wave('nWaveMode=9\n')['waveform_recipe']
    assert w['path_count'] is None
    assert w['primary_generated_path_count']==1
    assert w['secondary_storage_status']=='allocated by source without explicit vertex assignment; actual draw outcome not modeled'


def test_nonfinite_narrowed_wave_control_keeps_other_descriptor_data():
    d=appearance(read('fWaveAlpha=1\nnWaveMode=7\nper_frame_1=wave_mystery=1e100;wave_y=1e100;\n'))
    w=next(e for e in d['elements'] if e['id']=='builtin_wave')['waveform_recipe']
    assert w['line_angle_rad'] is None
    assert w['separation_normal_offset'] is None
    assert w['native_control_domains_verified'] is False
    assert 'sampling_geometry' in d


def test_known_mode_routes_ignore_unconsumed_authored_controls():
    w=wave('nWaveMode=3\nper_frame_1=wave_a=bass;wave_mystery=mid;\n')
    assert not any(r['control'] in {'wave_a','wave_mystery'} for r in w['audio_routes'])
    w=wave('nWaveMode=15\nper_frame_1=wave_x=treb;\n')
    assert not any(r['control']=='wave_x' for r in w['audio_routes'])


def test_path_topology_is_separate_from_context_dependent_draw_primitive():
    w=wave('nWaveMode=0\n')['waveform_recipe']
    assert w['path_topology']=='strip'
    assert w['hardware_draw_primitive'] is None
    assert set(w['hardware_draw_candidates'])=={'line_strip','triangle_strip'}
