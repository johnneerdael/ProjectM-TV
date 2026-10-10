"""Independent per-lane sampled-colour response through nonlinear RGB math."""
import numpy as np
import pytest
from test_effect_families import shader
from test_source_appearance import appearance


def description(code):return appearance(shader('shader_body {'+code+'}'))
def samples(code):
    return description(code)['nonlinear_texture_colour_bounds']['stages']['composite']['direct_sample_colour_response']['samples']


def test_squared_texture_has_diagonal_nonlinear_colour_gain():
    r=samples('ret=pow(GetPixel(uv),2);')[0]
    assert np.array(r['matrix_rgb_rgba_gain_upper_bounds'])==pytest.approx(np.array([[2,0,0,0],[0,2,0,0],[0,0,2,0]]),rel=1e-6)


def test_zero_touching_root_keeps_active_lane_gain_unknown():
    r=samples('ret=sqrt(GetPixel(uv));')[0]
    assert r['matrix_rgb_rgba_gain_upper_bounds'][0][0] is None
    assert r['matrix_rgb_rgba_gain_upper_bounds'][0][1:]==[0,0,0]


def test_sample_products_have_separate_fixed_other_sample_response():
    rows=samples('ret=GetPixel(uv)*GetBlur1(uv);')
    assert len(rows)==2
    for r in rows:assert r['matrix_rgb_rgba_gain_upper_bounds'][0]==pytest.approx([1,0,0,0],rel=1e-6)


def test_noise_mask_lerp_has_bounded_mask_influence():
    rows=samples('ret=lerp(GetPixel(uv),GetBlur1(uv),saturate(GetBlur2(uv).r*6-2));')
    r=next(x for x in rows if x['canonical_texture']=='blur2')
    assert [x[0] for x in r['matrix_rgb_rgba_gain_upper_bounds']]==pytest.approx([6]*3,rel=1e-6)


def test_nonlinear_colour_gain_propagates_sampling_motion():
    d=description('ret=pow(GetPixel(uv+float2(.1*time,0)),2);')
    r=d['activity']['motion_intensity']['texture_motion_bounds'][0]
    assert np.array(r['linear_texture_rgb_rate_coefficients_per_dimension'])==pytest.approx(np.array([[.2,0]]*3),rel=1e-6)
    assert r['colour_response_model']=='nonlinear_sample_lipschitz'


def test_sample_threshold_has_no_smooth_gain():
    r=samples('ret=GetPixel(uv).r>.5;')[0]
    assert [x[0] for x in r['matrix_rgb_rgba_gain_upper_bounds']]==[None]*3


def test_nested_lookup_coordinates_remain_outside_direct_sample_gain():
    d=description('ret=pow(GetPixel(GetBlur1(uv).rg),2);')
    r=d['nonlinear_texture_colour_bounds']['stages']['composite']['direct_sample_colour_response']
    assert len(r['samples'])==1
    assert r['includes_sampling_coordinate_response'] is False


def test_singular_product_cannot_certify_sample_gain():
    r=samples('ret=GetPixel(uv)*(1/0);')[0]
    assert all(v is None for row in r['matrix_rgb_rgba_gain_upper_bounds'] for v in row)


def test_float_vector_to_scalar_keeps_first_lane_response():
    r=samples('float a=(float)(tex2D(sampler_main,uv));ret=a*a;')[0]
    assert [row[0] for row in r['matrix_rgb_rgba_gain_upper_bounds']]==pytest.approx([2]*3,rel=1e-6)
    assert all(row[1:]==[0,0,0] for row in r['matrix_rgb_rgba_gain_upper_bounds'])


def test_float_width_coercions_do_not_hide_multiplicative_background_response():
    rows=samples('float3 background=tex2D(sampler_main,uv)+tex2D(sampler_noise_hq,uv);'
        'float blum=GetBlur1(background.rg)*background;ret=background-.1*blum;')
    assert any(v is not None and v>0 for row in rows[0]['matrix_rgb_rgba_gain_upper_bounds'] for v in row)


def test_integer_sample_cast_keeps_discontinuous_active_gain_unknown():
    r=samples('ret=(int)(GetPixel(uv).r*4);')[0]
    assert [row[0] for row in r['matrix_rgb_rgba_gain_upper_bounds']]==[None]*3


def test_unresolved_vector_integer_cast_never_claims_zero_sample_gain():
    r=samples('ret=(int)(tex2D(sampler_main,uv));')[0]
    assert [row[0] for row in r['matrix_rgb_rgba_gain_upper_bounds']]==[None]*3
