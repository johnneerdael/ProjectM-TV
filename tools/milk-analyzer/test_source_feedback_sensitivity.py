"""Aggregate raw warp sample sensitivity without a whole-renderer certificate."""
import pytest
from test_effect_families import shader,analyze
from test_source_appearance import appearance


def response(code):
    d=appearance(shader('shader_body {'+code+'}',stage='warp'))
    return d['feedback_colour_sensitivity']


def test_squared_main_colour_has_nonlinear_difference_gain():
    r=response('ret=.25*pow(GetPixel(uv),2);')
    assert r['maximum_fixed_coordinate_feedback_sample_gain']==pytest.approx(.5,rel=1e-6)
    assert r['maximum_previous_image_colour_gain']==pytest.approx(.5,rel=1e-6)
    assert r['sufficient_raw_warp_colour_contraction'] is True
    assert r['whole_feedback_contraction_verified'] is False


def test_distinct_feedback_sites_sum_absolute_row_gains():
    r=response('ret=.25*GetPixel(uv)*GetPixel(uv*.5);')
    assert r['maximum_previous_image_colour_gain']==pytest.approx(.5,rel=1e-6)
    assert len(r['sample_contributions'])==2


def test_gain_above_one_is_not_a_proved_instability():
    r=response('ret=pow(GetPixel(uv),2);')
    assert r['maximum_previous_image_colour_gain']==pytest.approx(2,rel=1e-6)
    assert r['sufficient_raw_warp_colour_contraction'] is False
    assert r['actual_feedback_stability'] is None


def test_blur_input_gain_does_not_invent_blur_to_previous_image_gain():
    r=response('ret=.25*pow(GetBlur1(uv),2);')
    assert r['maximum_fixed_coordinate_feedback_sample_gain']==pytest.approx(.5,rel=1e-6)
    assert r['maximum_previous_image_colour_gain'] is None
    assert r['sufficient_raw_warp_colour_contraction'] is None


def test_sample_driven_coordinates_keep_image_operator_unknown():
    r=response('ret=.25*pow(GetPixel(uv+.1*GetPixel(uv).rg),2);')
    assert r['maximum_fixed_coordinate_feedback_sample_gain']==pytest.approx(.5,rel=1e-6)
    assert r['maximum_previous_image_colour_gain'] is None


def test_external_texture_coordinates_can_add_feedback_response():
    r=response('ret=.2*GetPixel(uv)+tex2D(sampler_noise_lq,GetPixel(uv).rg).rgb;')
    assert r['maximum_fixed_coordinate_feedback_sample_gain']==pytest.approx(.2,rel=1e-6)
    assert r['maximum_previous_image_colour_gain'] is None


def test_feedback_alpha_columns_are_not_silently_dropped():
    r=response('float4 c=tex2D(sampler_main,uv);ret=.2*c.rgb+.3*c.a;')
    assert r['maximum_previous_image_colour_gain']==pytest.approx(.5,rel=1e-6)


@pytest.mark.parametrize('code',[
    'ret=sqrt(GetPixel(uv));',
    'ret=GetPixel(uv);if(ret.r>.7){ret.r=0;}',
    'ret=GetPixel(uv)*(1/0);',
])
def test_discontinuous_singular_or_unbounded_sample_response_stays_unknown(code):
    r=response(code)
    assert r['maximum_fixed_coordinate_feedback_sample_gain'] is None
    assert r['maximum_previous_image_colour_gain'] is None


def test_nonlinear_audio_gain_keeps_separate_scenario_bounds():
    s=shader('shader_body {ret=.1*bass*pow(GetPixel(uv),2);}',stage='warp')
    d=analyze(s,input_scenario={'schema_version':1,'name':'feedback-audio','audio_band_ranges':{'bass':[0,2]}})['visual_description']
    r=d['feedback_colour_sensitivity']
    assert r['maximum_previous_image_colour_gain'] is None
    e=r['scenario_feedback_colour_sensitivity']
    assert e['maximum_previous_image_colour_gain']==pytest.approx(.4,rel=1e-6)
    assert e['input_scenario_sha256'] is not None


def test_independent_colour_pairs_respect_squared_operator_ceiling():
    r=response('ret=.25*pow(GetPixel(uv),2);')
    gain=r['maximum_previous_image_colour_gain']
    for a,b in (([0,.5,1],[.2,.7,.8]),([1,1,1],[.99,.99,.99])):
        source=max(abs(x-y) for x,y in zip(a,b))
        out=max(abs(.25*x*x-.25*y*y) for x,y in zip(a,b))
        assert out<=gain*source+1e-12


@pytest.mark.parametrize('mutation',['clip','missing_lookup','mipmap','addressing'])
def test_incomplete_writes_or_unverified_sampler_contract_withhold_image_gain(mutation):
    from source_feedback_sensitivity import feedback_colour_sensitivity
    d=appearance(shader('shader_body {ret=.25*pow(GetPixel(uv),2);}',stage='warp'))
    if mutation=='missing_lookup':d['sampling_geometry']['stages']['warp']=[]
    elif mutation=='mipmap':d['sampling_geometry']['stages']['warp'][0]['sampling_policy']['mipmapped']=True
    elif mutation=='addressing':
        p=d['sampling_geometry']['stages']['warp'][0]['sampling_policy'];p['wrap']=None;p.pop('wrap_condition',None)
    r=feedback_colour_sensitivity(d,warp_contains_clip=mutation=='clip')
    assert r['maximum_fixed_coordinate_feedback_sample_gain']==pytest.approx(.5,rel=1e-6)
    assert r['maximum_previous_image_colour_gain'] is None
    assert r['unknown_reasons']
