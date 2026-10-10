"""Nested lookup chains preserve dimension, filter and fixed-input premises."""
import numpy as np
import pytest
from test_effect_families import shader
from test_source_appearance import appearance


def description(code):return appearance(shader('shader_body {'+code+'}'))
def chains(code):return description(code)['activity']['motion_intensity']['nested_texture_motion']['chains']


def test_inner_sample_displacement_has_coordinate_gain_matrix():
    d=description('ret=GetPixel(uv+.2*GetBlur1(uv+float2(.1*time,0)).rg);')
    outer=d['sampling_geometry']['stages']['composite'][0]
    edges=outer['coordinate_sample_response']['samples']
    assert len(edges)==1
    assert np.array(edges[0]['matrix_uv_rgba_gain_upper_bounds'])==pytest.approx(np.array([[.2,0,0,0],[0,.2,0,0]]),rel=1e-6)


def test_two_level_chain_exports_dimension_polynomial():
    r=chains('ret=GetPixel(uv+.2*GetBlur1(uv+float2(.1*time,0)).rg);')[0]
    assert r['path_sample_site_indices'] and len(r['path_sample_site_indices'])==2
    # Winner*.1 * (.2*Wouter + .2*Houter), one independent RGB ceiling.
    coefficients=[t['coefficient'] for t in r['rgb_rate_polynomial'][0]]
    assert coefficients==pytest.approx([.02,.02],rel=1e-6)
    assert all(len(t['dimension_factors'])==2 for t in r['rgb_rate_polynomial'][0])
    assert r['visible_rgb_rate_per_second'] is None


def test_nonlinear_inner_sample_offset_has_gain_before_chain():
    d=description('ret=GetPixel(uv+float2(.05*pow(GetBlur1(uv+float2(.1*time,0)).r,2),0));')
    m=d['sampling_geometry']['stages']['composite'][0]['coordinate_sample_response']['samples'][0]
    assert m['matrix_uv_rgba_gain_upper_bounds'][0]==pytest.approx([.1,0,0,0],rel=1e-6)


def test_three_level_chain_retains_three_texture_dimension_factors():
    rows=chains('float2 p=uv+.2*GetBlur2(uv+float2(.1*time,0)).rg;'
                'ret=GetPixel(uv+.3*GetBlur1(p).rg);')
    r=next(x for x in rows if len(x['path_sample_site_indices'])==3)
    assert all(len(t['dimension_factors'])==3 for t in r['rgb_rate_polynomial'][0])


def test_nearest_outer_sampler_withholds_smooth_chain():
    rows=chains('ret=tex2D(sampler_pc_main,uv+.2*GetBlur1(uv+float2(.1*time,0)).rg).rgb;')
    assert rows==[]


def test_singular_nested_coordinate_does_not_get_chain_credit():
    rows=chains('ret=GetPixel(uv+float2(1/GetBlur1(uv+float2(.1*time,0)).r,0));')
    assert rows==[]


def test_no_nested_sample_does_not_invent_chain():
    assert chains('ret=GetPixel(uv+float2(.1*time,0));')==[]


def test_quantized_sample_coefficient_keeps_response_unknown():
    from shader_fields import Field
    from source_ripple_envelopes import coefficient_envelope
    x=Field('input',dtype='float',detail={'name':'x'})
    quantized=Field('narrow',(x,),'float',{'numeric_domain':'shader-float32'})
    r=coefficient_envelope(quantized,input_domains={'x':[0,1]},response_inputs={'x'})
    assert r['maximum_absolute_control_change_per_audio_unit'] is None


def test_nested_paths_never_claim_exhaustive_whole_image_bound():
    d=description('ret=GetPixel(uv+.2*GetBlur1(uv+float2(.1*time,0)).rg);')
    r=d['activity']['motion_intensity']['nested_texture_motion']
    assert r['chains']
    assert r['paths_are_exhaustive'] is False
    assert r['full_sampling_motion_bound_verified'] is False
