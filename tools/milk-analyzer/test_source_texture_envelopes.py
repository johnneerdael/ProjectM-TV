"""Independent sampled-texture colour bounds are not full feedback proofs."""
import numpy as np
import pytest
from test_effect_families import shader
from test_source_appearance import appearance


def envelopes(code):
    d=appearance(shader('shader_body {'+code+'}',stage='warp'))
    assert 'texture_colour_envelopes' in d,'texture mixture envelope missing'
    return d['texture_colour_envelopes']['stages']['warp']


def test_signed_main_blur_mixture_has_raw_colour_box_and_separate_history_gain():
    r=envelopes('ret=GetPixel(uv)*.6-GetBlur1(uv)*.2+.1;')
    assert r['source_model']=='bounded_affine_texture_inputs'
    assert np.array(r['raw_rgb_bounds_if_samples_unit_interval'])==pytest.approx(np.array([[-.1,.7]]*3),abs=2e-7)
    assert r['all_texture_colour_difference_gain']==pytest.approx(.8,abs=2e-7)
    assert r['main_or_blur_input_difference_gain']==pytest.approx(.8,abs=2e-7)
    assert r['whole_feedback_contraction'] is None


def test_external_noise_colour_remains_separate_from_history_weights():
    r=envelopes('ret=GetPixel(uv)*.4+tex2D(sampler_noise_lq,uv).rgb*.3;')
    assert r['all_texture_colour_difference_gain']==pytest.approx(.7,abs=2e-7)
    assert r['main_or_blur_input_difference_gain']==pytest.approx(.4,abs=2e-7)
    assert r['external_texture_input_difference_gain']==pytest.approx(.3,abs=2e-7)


def test_blur_decode_is_preserved_in_sample_coefficients():
    r=envelopes('ret=GetBlur1(uv)*.5;')
    assert r['all_texture_colour_difference_gain']==pytest.approx(.5,abs=1e-7)
    assert r['history_textures']==['blur1']


def test_nonzero_uv_colour_term_needs_declared_coordinate_domain():
    r=envelopes('ret=GetPixel(uv)*.4+float3(uv,0);')
    assert r['all_texture_colour_difference_gain']==pytest.approx(.4,abs=1e-7)
    assert r['raw_rgb_bounds_if_samples_unit_interval'] is None
    assert r['unknown_reasons']


def test_image_dependent_sampling_does_not_become_whole_colour_sensitivity():
    r=envelopes('ret=GetPixel(uv+GetPixel(uv).rg*.1)*.5;')
    assert r['coordinate_sample_dependency'] is True
    assert r['full_colour_sensitivity'] is None


def test_nonlinear_mixture_does_not_get_affine_envelopes():
    r=envelopes('ret=GetPixel(uv)*GetBlur1(uv);')
    assert r['source_model']=='unknown'
    assert r['all_texture_colour_difference_gain'] is None


def test_unbounded_offset_keeps_weight_gain_but_not_rgb_box():
    r=envelopes('ret=GetPixel(uv)*.4+bass;')
    assert r['all_texture_colour_difference_gain']==pytest.approx(.4,abs=1e-7)
    assert r['raw_rgb_bounds_if_samples_unit_interval'] is None


def test_outward_rounding_overflow_cannot_create_nonfinite_json_gain():
    import json,sys
    from source_texture_envelopes import texture_colour_envelopes
    matrix=[[sys.float_info.max,5e-324,0,0],[0,0,0,0],[0,0,0,0]]
    t={'stages':{'warp':{'source_model':'affine_sample_colour','coordinate_sample_dependency':False,
        'sample_contributions':[{'canonical_texture':'main','matrix_rgb_rgba':matrix}],
        'constant_offset_rgb':[0,0,0],'base_uv_matrix_rgb':[[0]*4]*3}}}
    r=texture_colour_envelopes(t)['stages']['warp']
    assert r['source_model']=='unknown'
    assert r['all_texture_colour_difference_gain'] is None
    assert r['unknown_reasons']
    json.dumps(r,allow_nan=False)
