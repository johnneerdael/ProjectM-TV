"""Shader RGB partial time rates with explicitly held-fixed sample colours."""
import pytest
from test_effect_families import shader,read,analyze
from test_source_appearance import appearance


def response(code):
    r=appearance(shader('shader_body {'+code+'}',stage='warp'))
    return r['nonlinear_texture_colour_bounds']['stages']['warp']['direct_colour_time_response']


def rates(r):
    return [c['maximum_absolute_rgb_rate_per_source_second'] for c in r['channels']]


def test_sample_multiplied_by_time_pulse_has_rgb_partial_rate():
    r=response('ret=GetPixel(uv)*(.5+.5*sin(3*time));')
    assert rates(r)==pytest.approx([1.5]*3,rel=1e-6)
    assert r['total_rgb_rate_per_second'] is None
    assert r['visible_flash_frequency_hz'] is None


def test_time_in_sampling_position_is_not_direct_colour_change():
    r=response('ret=GetPixel(uv+float2(time,0));')
    assert rates(r)==[0,0,0]
    assert r['includes_sampling_coordinate_response'] is False
    assert r['samples_are_held_fixed'] is True


def test_threshold_time_colour_does_not_receive_finite_smooth_rate():
    assert rates(response('ret=GetPixel(uv)*(sin(time)>0);'))==[None]*3


def test_time_dependent_q_upload_does_not_become_fixed_input():
    d=appearance(read('per_frame_1=q1=.5+.1*sin(time);\nwarp_1=`shader_body {ret=float3(q1,.5,.5);}\n'))
    r=d['nonlinear_texture_colour_bounds']['stages']['warp']['direct_colour_time_response']
    assert rates(r)==[None,0,0]
    assert r['channels'][0]['unknown_reasons']


def test_declared_audio_range_bounds_audio_scaled_time_pulse():
    s=shader('shader_body {ret=GetPixel(uv)*sin(3*time)*bass;}',stage='warp')
    r=analyze(s,input_scenario={'schema_version':1,'name':'time-colour','audio_band_ranges':{'bass':[0,2]}})
    stage=r['visual_description']['nonlinear_texture_colour_bounds']['stages']['warp']
    assert rates(stage['direct_colour_time_response'])==[None]*3
    extra=stage['scenario_colour_envelope']['direct_colour_time_response']
    assert rates(extra)==pytest.approx([6]*3,rel=1e-6)
    assert extra['channels'][0]['declared_input_domains']['_c3.x']==[0,2]


def test_packed_shader_time_alias_has_same_partial_rate():
    assert rates(response('ret=GetPixel(uv)*sin(_c2.x*2);'))==pytest.approx([2]*3,rel=1e-6)


def test_singular_contributing_factor_cannot_certify_time_rate():
    assert rates(response('ret=GetPixel(uv)*sin(time)*(1/0);'))==[None]*3


def test_native_time_oscillator_formula_is_followed():
    assert rates(response('ret=GetPixel(uv)*_c8.x;'))==pytest.approx([.5*.329]*3,rel=1e-6)


def test_activity_links_direct_shader_colour_time_bounds():
    d=appearance(shader('shader_body {ret=GetPixel(uv)*sin(time*2);}'))
    rows=d['activity']['flashing']['shader_change_bounds']
    r=next(x for x in rows if x['stage']=='composite' and x['input_scenario_sha256'] is None)
    assert rates(r)==pytest.approx([2]*3,rel=1e-6)
    assert d['activity']['flashing']['value'] is None
