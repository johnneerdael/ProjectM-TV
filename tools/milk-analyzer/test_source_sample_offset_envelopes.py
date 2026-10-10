"""Nonlinear sample-value offsets retain explicit unit-image premises."""
import pytest
from test_source_sampling import maps


def offset(code):
    r=maps(code)[0]
    assert 'sample_value_offset_envelope' in r
    return r['sample_value_offset_envelope']


def test_squared_image_offset_has_range_without_global_motion_claim():
    e=offset('ret=GetPixel(uv+float2(.05*pow(GetBlur1(uv).r,2),0));')
    assert e['source_model']=='sample_value_offset_bounds'
    assert e['offset_range_uv'][0]==pytest.approx([0,.05],abs=2e-8)
    assert e['offset_range_uv'][1]==[0,0]
    assert e['full_coordinate_sensitivity'] is None
    assert e['actual_feedback_persistence'] is None


def test_noise_driven_sinusoidal_offset_has_bounded_extent():
    e=offset('ret=GetPixel(uv+float2(.03*sin(tex2D(sampler_noise_lq,uv).r*6),0));')
    assert e['offset_range_uv'][0]==pytest.approx([-.03,.03],abs=2e-8)
    assert e['sample_textures']==['noise_lq']


def test_multiple_image_inputs_remain_independent_premises():
    e=offset('ret=GetPixel(uv+float2(.1*saturate(GetBlur1(uv).r-GetBlur2(uv).g),0));')
    assert e['offset_range_uv'][0]==pytest.approx([0,.1],abs=2e-8)
    assert e['sample_textures']==['blur1','blur2']


def test_singular_image_division_keeps_partial_coordinates():
    e=offset('ret=GetPixel(uv+float2(.05/GetPixel(uv).r,0));')
    assert e['offset_range_uv']==[None,[0,0]]
    assert e['source_model']=='partial_sample_value_offset_bounds'


def test_image_dependent_spatial_scale_does_not_claim_offset_only_model():
    e=offset('ret=GetPixel(uv*(1+GetPixel(uv).r));')
    assert e['source_model']=='unknown'
    assert e['offset_range_uv'] is None


def test_plain_lookup_does_not_invent_image_driven_offset():
    assert offset('ret=GetPixel(uv);')['source_model']=='unknown'


def test_constant_image_sampling_location_is_retained_without_global_feedback_claim():
    e=offset('ret=GetPixel(uv+float2(.1*pow(GetPixel(float2(.5,.5)).r,2),0));')
    assert e['sample_sites'][0]['coordinate_expression']
    assert e['coordinate_sample_dependency'] is False
    assert e['full_coordinate_sensitivity'] is None


def test_zero_products_do_not_hide_invalid_original_image_offset_domain():
    e=offset('ret=GetPixel(uv+float2((bass/0.)*0.+.05*pow(GetPixel(uv).r,2),0));')
    assert e['source_model']=='unknown'
    assert e['offset_range_uv'] is None


def test_luminance_offset_retains_native_non_normalized_weights():
    e=offset('ret=GetPixel(uv+float2(.1*lum(GetPixel(uv)),0));')
    assert e['offset_range_uv'][0]==pytest.approx([0,.11],abs=2e-8)
