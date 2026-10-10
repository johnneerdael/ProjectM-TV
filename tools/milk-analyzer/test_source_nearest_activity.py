"""Nearest filtering can jump; possible mechanisms are not observed flashes."""
import pytest
from test_effect_families import shader
from test_source_appearance import appearance


def hazards(code):
    d=appearance(shader('shader_body {'+code+'}'))
    return [h for h in d['activity']['flashing']['hazards'] if h['kind']=='nearest_lookup_temporal_jumps']


def test_moving_nearest_sample_has_nominal_grid_crossing_coefficients():
    h=hazards('ret=tex2D(sampler_pw_main,uv+float2(.1*time,.2*time)).rgb;')[0]
    assert h['grid_crossing_rate_coefficients_per_uploaded_dimension']==pytest.approx([.1,.2],rel=1e-6)
    assert h['rgb_jump_upper_bounds_from_direct_response']==pytest.approx([1]*3,rel=1e-6)
    assert h['visible_flashing_verified'] is False
    assert h['visible_flash_frequency_hz'] is None


def test_linear_filter_is_not_a_nearest_jump_mechanism():
    assert hazards('ret=GetPixel(uv+float2(.1*time,0));')==[]


def test_stationary_nearest_lookup_has_no_time_motion_jump_claim():
    assert hazards('ret=tex2D(sampler_pw_main,uv).rgb;')==[]


def test_sine_motion_cannot_borrow_linear_grid_crossing_rate():
    h=hazards('ret=tex2D(sampler_pw_main,uv+float2(.001*sin(100*time),0)).rgb;')[0]
    assert h['grid_crossing_rate_coefficients_per_uploaded_dimension'] is None
    assert h['maximum_lookup_axis_speed_uv_per_second'][0]==pytest.approx(.1,rel=1e-6)


def test_nested_nearest_sample_has_possible_rgb_route_without_jump_size_claim():
    h=hazards('float2 p=uv+.2*tex2D(sampler_pw_noise_lq,uv+float2(.1*time,0)).rg;ret=GetPixel(p);')[0]
    assert h['rgb_influence_route']=='nested_coordinate_path'
    assert h['rgb_jump_upper_bounds_from_direct_response']==[None]*3


def test_dead_nearest_sample_does_not_get_a_jump_hazard():
    assert hazards('float3 dead=tex2D(sampler_pw_main,uv+float2(.1*time,0)).rgb;ret=float3(.2,.3,.4);')==[]


def test_clamped_nearest_drift_does_not_get_repeat_crossing_frequency():
    h=hazards('ret=tex2D(sampler_pc_main,uv+float2(.1*time,0)).rgb;')[0]
    assert h['grid_crossing_rate_coefficients_per_uploaded_dimension'] is None
