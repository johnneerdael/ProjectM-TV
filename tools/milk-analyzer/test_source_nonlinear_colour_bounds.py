"""Nominal nonlinear shader range bounds on declared texture inputs."""
import numpy as np
import pytest
from shader_fields import Field
from source_control_bounds import scalar_value_envelope
from test_effect_families import shader
from test_source_appearance import appearance


def scalar(op,*args):return Field(op,tuple(args),'float')
def constant(v):return Field('constant',detail={'value':v})
def domain(expr):return scalar_value_envelope(expr,input_domains={'x':[0,1]})
def colour(code):
    d=appearance(shader('shader_body {'+code+'}',stage='warp'))
    assert 'nonlinear_texture_colour_bounds' in d,'nonlinear colour bounds missing'
    return d['nonlinear_texture_colour_bounds']['stages']['warp']


def test_saturate_and_clamp_keep_exact_legal_endpoint_limits():
    x=Field('input',detail={'name':'x'})
    assert domain(scalar('saturate',scalar('multiply',x,constant(2))))['nominal_value_range']==[0,1]
    assert domain(scalar('clamp',x,constant(.2),constant(.8)))['nominal_value_range']==[.2,.8]


def test_positive_power_and_root_have_ranges_without_timing_credit():
    x=Field('input',detail={'name':'x'})
    assert domain(scalar('pow',x,constant(2)))['nominal_value_range']==pytest.approx([0,1])
    assert domain(scalar('sqrt',x))['nominal_value_range']==pytest.approx([0,1])
    assert domain(scalar('pow',x,constant(2)))['native_numeric_certified'] is False


def test_zero_nonpositive_power_and_negative_root_remain_unknown():
    x=Field('input',detail={'name':'x'})
    assert domain(scalar('pow',x,constant(-1)))['nominal_value_range'] is None
    assert domain(scalar('sqrt',scalar('subtract',x,constant(2))))['nominal_value_range'] is None


def test_powered_sample_has_raw_bounds_without_affine_gain_claim():
    r=colour('ret=pow(GetPixel(uv),2);')
    assert r['source_model']=='bounded_declared_texture_inputs'
    assert np.array(r['raw_rgb_bounds_if_samples_unit_interval'])==pytest.approx(np.array([[0,1]]*3),abs=1e-12)
    assert r['colour_difference_gain'] is None
    assert r['whole_feedback_contraction'] is None


def test_mixed_main_blur_clamp_can_bound_each_channel():
    r=colour('ret=saturate(GetPixel(uv)*1.2-GetBlur1(uv)*.2);')
    assert r['source_model']=='bounded_declared_texture_inputs'
    assert r['sample_textures']==['blur1','main']
    assert np.array(r['raw_rgb_bounds_if_samples_unit_interval'])==pytest.approx(np.array([[0,1]]*3))


def test_colour_multiplication_is_bounded_without_linearizing_it():
    r=colour('ret=GetPixel(uv)*GetBlur1(uv);')
    assert r['source_model']=='bounded_declared_texture_inputs'
    assert r['colour_difference_gain'] is None


def test_image_threshold_mask_gets_value_range_not_continuity():
    r=colour('ret=GetPixel(uv).r>.5;')
    assert np.array(r['raw_rgb_bounds_if_samples_unit_interval'])==pytest.approx(np.array([[0,1]]*3))
    assert r['visible_flashing'] is None


def test_singular_power_keeps_unknown_channel_domains():
    r=colour('ret=pow(GetPixel(uv),-1);')
    assert r['source_model']=='unknown'
    assert r['raw_rgb_bounds_if_samples_unit_interval'] is None
    assert r['unknown_reasons']


def test_shader_abs_lowering_is_retained_for_negative_power_base():
    r=colour('ret=pow(-GetPixel(uv),2);')
    assert r['source_model']=='bounded_declared_texture_inputs'


def test_dynamic_nonfinite_q_upload_cannot_hide_inside_clamp():
    from test_effect_families import read
    d=appearance(read('per_frame_1=q1=1e40*sin(time);\nwarp_1=`shader_body {ret=saturate(q1+GetPixel(uv));}\n'))
    assert d['nonlinear_texture_colour_bounds']['stages']['warp']['source_model']=='unknown'


def test_unresolved_upload_preserves_independently_known_colour_channels():
    from test_effect_families import read
    d=appearance(read('per_frame_1=q1=1e40*sin(time);\nwarp_1=`shader_body {ret=float3(saturate(q1),.5,.5);}\n'))
    r=d['nonlinear_texture_colour_bounds']['stages']['warp']
    assert r['source_model']=='partial_declared_texture_inputs'
    assert r['raw_rgb_bounds_if_samples_unit_interval'] is None
    assert r['channel_value_envelopes'][0]['nominal_value_range'] is None
    assert r['channel_value_envelopes'][0]['unknown_reasons']
    assert [c['nominal_value_range'] for c in r['channel_value_envelopes'][1:]]==[[.5,.5],[.5,.5]]


def test_lerp_mixture_including_extrapolation_is_bounded_without_clamping_weight():
    r=colour('ret=lerp(GetPixel(uv),GetBlur1(uv),2.);')
    assert np.array(r['raw_rgb_bounds_if_samples_unit_interval'])==pytest.approx(np.array([[-1,2]]*3),abs=1e-12)


def test_luminance_dot_colour_has_supported_raw_range():
    r=colour('ret=lum(GetPixel(uv));')
    assert r['source_model']=='bounded_declared_texture_inputs'
    assert np.array(r['raw_rgb_bounds_if_samples_unit_interval'])==pytest.approx(np.array([[0,1.1]]*3),abs=1e-7) #native lum weights .32+.49+.29


def test_abs_power_does_not_change_literal_exponent_one_sign_exception():
    r=colour('ret=pow(-GetPixel(uv),1);')
    assert np.array(r['raw_rgb_bounds_if_samples_unit_interval'])==pytest.approx(np.array([[-1,0]]*3),abs=1e-12)


def test_canonical_swizzles_keep_independent_lane_domains_across_calls():
    from concurrent.futures import ThreadPoolExecutor
    source=shader('shader_body {ret=GetPixel(float2(ang,1/rad));}')
    def run(_):
        r=appearance(source)['nonlinear_texture_colour_bounds']['stages']['composite']
        for lane,channel in zip('xyz',r['channel_value_envelopes']):
            assert list(channel['declared_input_domains'])==[':coordinate-sample-0.'+lane]
        return r
    expected=run(0)
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert all(r==expected for r in pool.map(run,range(12)))


def test_fractional_colour_range_uses_floor_for_negative_inputs():
    x=Field('input',detail={'name':'x'})
    r=scalar_value_envelope(scalar('frac',x),input_domains={'x':[-.8,-.2]})
    assert r['nominal_value_range']==pytest.approx([.2,.8],abs=2e-15)
    assert r['native_numeric_certified'] is False


def test_fractional_colour_crossing_seam_keeps_unit_enclosure_without_rate():
    from source_control_bounds import compound_time_bounds
    x=Field('input',detail={'name':'x'})
    assert scalar_value_envelope(scalar('frac',x),input_domains={'x':[-.1,.1]})['nominal_value_range']==[0,1]
    assert scalar_value_envelope(scalar('frac',x))['nominal_value_range']==[0,1]
    r=compound_time_bounds(scalar('frac',Field('input',detail={'name':'time'})))
    assert r['maximum_absolute_control_rate_per_second'] is None


def test_floor_colour_levels_have_integer_enclosure_without_flash_claim():
    x=Field('input',detail={'name':'x'})
    r=domain(scalar('floor',scalar('multiply',x,constant(4))))
    assert r['nominal_value_range'][0]<=0 and r['nominal_value_range'][1]>=4
    assert scalar_value_envelope(scalar('floor',x),input_domains={'x':[-.8,2.2]})['nominal_value_range']==[-1,2]
    r=colour('ret=floor(GetPixel(uv)*4)/4;')
    assert r['source_model']=='bounded_declared_texture_inputs'
    assert r['visible_flashing'] is None


def test_frac_cannot_hide_known_singular_expression():
    r=scalar_value_envelope(scalar('frac',scalar('divide',constant(1),constant(0))))
    assert r['nominal_value_range'] is None


def test_colour_scenario_adds_audio_bounds_without_changing_default():
    from test_effect_families import analyze
    s=shader('shader_body {ret=GetPixel(uv)*bass;}',stage='warp')
    plain=analyze(s)['visual_description']['nonlinear_texture_colour_bounds']['stages']['warp']
    a=analyze(s,input_scenario={'schema_version':1,'name':'colour-test','audio_band_ranges':{'bass':[0,2]}})
    r=a['visual_description']['nonlinear_texture_colour_bounds']['stages']['warp']
    assert {k:v for k,v in r.items() if k!='scenario_colour_envelope'}==plain
    extra=r['scenario_colour_envelope']
    assert extra['source_model']=='bounded_declared_texture_inputs'
    assert np.array(extra['raw_rgb_bounds_if_samples_unit_interval'])==pytest.approx(np.array([[0,2]]*3),abs=2e-7)
    assert extra['input_scenario_sha256']==a['input_scenario']['record_sha256']
    assert extra['visible_flashing'] is None


def test_colour_scenario_keeps_missing_audio_and_nonfinite_q_upload_unknown():
    from test_effect_families import analyze,read
    scenario={'schema_version':1,'name':'colour-test','audio_band_ranges':{'bass':[0,2]}}
    for s in (shader('shader_body {ret=GetPixel(uv)*mid;}',stage='warp'),read('per_frame_1=q1=1e40;\nwarp_1=`shader_body {ret=saturate(q1+GetPixel(uv));}\n')):
        r=analyze(s,input_scenario=scenario)['visual_description']['nonlinear_texture_colour_bounds']['stages']['warp']['scenario_colour_envelope']
        assert r['source_model']=='unknown'
        assert r['raw_rgb_bounds_if_samples_unit_interval'] is None


def test_declared_audio_premise_survives_colour_q_upload_projection():
    from test_effect_families import analyze,read
    source=read('per_frame_1=q1=.5+.1*bass;\nwarp_1=`shader_body {ret=GetPixel(uv)*q1;}\n')
    r=analyze(source,input_scenario={'schema_version':1,'name':'q-premise','audio_band_ranges':{'bass':[0,2]}})['visual_description']['nonlinear_texture_colour_bounds']['stages']['warp']['scenario_colour_envelope']
    assert r['source_model']=='bounded_declared_texture_inputs'
    assert 'bass' in r['assumed_finite_nontexture_input_names']
    assert not any(name.startswith(':nonlinear-colour-') for name in r['assumed_finite_nontexture_input_names'])


@pytest.mark.parametrize('value',[10**16+1,-10**16-1])
def test_floor_integer_endpoint_conversion_preserves_nominal_enclosure(value):
    x=Field('input',detail={'name':'x'})
    r=scalar_value_envelope(scalar('floor',x),input_domains={'x':[value,value]})
    lo,hi=r['nominal_value_range']
    assert lo<=value<=hi
