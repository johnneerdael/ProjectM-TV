"""Sampling-map motion is scoped separately from image/history variation."""
import numpy as np
import pytest
from test_effect_families import shader,analyze
from test_source_appearance import appearance


def description(code):return appearance(shader('shader_body {'+code+'}'))
def record(code):return description(code)['sampling_geometry']['stages']['composite'][0]['sampling_motion']


def test_scaled_translation_has_inverse_feature_velocity():
    r=record('ret=GetPixel(2*uv+float2(.1*time,0));')
    assert r['maximum_lookup_axis_speed_uv_per_second']==pytest.approx([.1,0],rel=1e-6)
    assert r['signed_feature_velocity_basis_uv_per_second']==pytest.approx([-.05,0],rel=1e-6)
    assert r['maximum_feature_speed_basis_uv_per_second']==pytest.approx(.05,rel=1e-6)


def test_periodic_lookup_translation_has_speed_upper_bound_without_fixed_direction():
    r=record('ret=GetPixel(uv+float2(.02*sin(3*time),0));')
    assert r['maximum_lookup_axis_speed_uv_per_second']==pytest.approx([.06,0],rel=1e-6)
    assert r['signed_feature_velocity_basis_uv_per_second'] is None
    assert r['maximum_feature_speed_basis_uv_per_second']>=r['maximum_lookup_axis_speed_uv_per_second'][0]


def test_colour_weight_scales_texture_gradient_rate_coefficients():
    d=description('ret=GetPixel(uv+float2(.1*time,.2*time))*.5;')
    r=d['activity']['motion_intensity']['texture_motion_bounds'][0]
    assert np.array(r['linear_texture_rgb_rate_coefficients_per_dimension'])==pytest.approx(np.array([[.05,.1]]*3),rel=1e-6)
    assert r['texture_dimensions_verified'] is False
    assert r['visible_rgb_rate_per_second'] is None


def test_singular_affine_map_has_lookup_rate_without_inverse_feature_speed():
    r=record('ret=GetPixel(float2(.1*time,uv.y));')
    assert r['maximum_lookup_axis_speed_uv_per_second']==pytest.approx([.1,0],rel=1e-6)
    assert r['maximum_feature_speed_basis_uv_per_second'] is None


def test_known_singular_coordinate_cannot_publish_motion():
    r=record('ret=GetPixel(uv+float2(time/0,0));')
    assert r['maximum_lookup_axis_speed_uv_per_second']==[None,None]


def test_scenario_time_component_keeps_audio_fixed_and_scenario_identity():
    s=shader('shader_body {ret=GetPixel(uv+float2(bass*time*.1,0));}')
    d=analyze(s,input_scenario={'schema_version':1,'name':'sample-time','audio_band_ranges':{'bass':[0,2]}})['visual_description']
    m=d['sampling_geometry']['stages']['composite'][0]['sampling_motion']
    assert m['maximum_lookup_axis_speed_uv_per_second'][0] is None
    extra=m['scenario_sampling_motion']
    assert extra['maximum_lookup_axis_speed_uv_per_second']==pytest.approx([.2,0],rel=1e-6)
    assert extra['input_scenario_sha256'] is not None
    assert extra['total_lookup_speed_uv_per_second'] is None


def test_sample_motion_record_does_not_claim_fixed_feedback_or_screen_speed():
    r=record('ret=GetPixel(uv+float2(.1*time,0));')
    assert r['visible_screen_speed'] is None
    assert r['native_mesh_input_is_held_fixed'] is True
    assert any('history' in c for c in r['conditions'])


def test_nearest_sampling_cannot_get_bilinear_gradient_bound():
    d=description('ret=tex2D(sampler_pc_main,uv+float2(.1*time,0)).rgb;')
    r=d['activity']['motion_intensity']['texture_motion_bounds'][0]
    assert r['linear_texture_rgb_rate_coefficients_per_dimension']==[[None,None]]*3


def test_inverse_velocity_satisfies_affine_feature_motion_equation():
    r=record('ret=GetPixel(float2(2*uv.x+uv.y+.1*time,uv.x+3*uv.y+.2*time));')
    vx,vy=r['signed_feature_velocity_basis_uv_per_second']
    lookup=r['maximum_lookup_axis_speed_uv_per_second']
    assert 2*vx+vy+lookup[0]==pytest.approx(0,abs=1e-15)
    assert vx+3*vy+lookup[1]==pytest.approx(0,abs=1e-15)


def test_two_helper_lookups_keep_distinct_motion_and_colour_weights():
    d=appearance(shader('float3 tap(float2 p){return tex2D(sampler_main,p).rgb;} '
        'shader_body {ret=.2*tap(uv+float2(.1*time,0))+.8*tap(uv+float2(.4*time,0));}'))
    rows=d['activity']['motion_intensity']['texture_motion_bounds']
    assert len(rows)==2
    values=sorted(x['linear_texture_rgb_rate_coefficients_per_dimension'][0][0] for x in rows)
    assert values==pytest.approx([.02,.32],rel=1e-6)
