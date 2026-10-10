"""Flashing hazards and movement steps must describe effects, not parameter derivatives."""
import math
import pytest
from test_effect_families import shader,read,analyze
from test_source_appearance import appearance


def test_periodic_composite_blackout_gate_has_source_flash_cadence():
    a=appearance(shader('shader_body {ret=GetPixel(uv)*(sin(time*6)>0); }'))['activity']
    r=a['flashing']
    assert r['hazards']
    h=r['hazards'][0]
    assert h['kind']=='full_stage_blackout_gate'
    assert h['off_rgb']==[0,0,0]
    assert h['switch_event_rate_hz']==pytest.approx(6/math.pi)
    assert h['blackout_cycles_hz']==pytest.approx(6/math.tau)
    assert r['value'] is None


def test_background_addition_does_not_claim_full_stage_blackout():
    r=appearance(shader('shader_body {ret=.2+GetPixel(uv)*(sin(time*6)>0); }'))['activity']['flashing']
    assert not any(h['kind']=='full_stage_blackout_gate' for h in r['hazards'])


def test_spatial_mask_is_not_a_uniform_temporal_blackout_gate():
    r=appearance(shader('shader_body {ret=GetPixel(uv)*(sin(uv.x*6)>0); }'))['activity']['flashing']
    assert not r['hazards']


def test_static_rotation_has_feedback_motion_even_with_zero_parameter_rate():
    s=read('warp=0\nrot=.02\nfZoomExponent=1\nzoom=1\n')
    r=appearance(s)['activity']['motion_intensity']
    rotation=next(x for x in r['feedback_step_components'] if x['kind']=='rotation')
    assert rotation['absolute_radians_per_feedback_step']==pytest.approx(.02,rel=1e-6)
    assert rotation['degrees_per_second_per_feedback_fps']==pytest.approx(.02*180/math.pi,rel=1e-6)
    assert rotation['parameter_time_rate_is_motion_speed'] is False
    assert r['value'] is None


def test_constant_zoom_reports_per_step_motion_not_zero_speed():
    r=appearance(read('warp=0\nzoom=1.01\nfZoomExponent=1\n'))['activity']['motion_intensity']
    zoom=next(x for x in r['feedback_step_components'] if x['kind']=='zoom')
    assert zoom['scale_per_feedback_step']==pytest.approx(1.01,rel=1e-6)
    assert zoom['log_scale_per_second_per_feedback_fps']==pytest.approx(math.log(1.01),rel=1e-5)


def test_disconnected_feedback_has_no_native_feedback_step_motion():
    r=appearance(shader('shader_body {ret=float3(.2,.3,.4);}'))['activity']['motion_intensity']
    assert not r['feedback_step_components']


def test_known_singular_warp_does_not_publish_motion_step_components():
    r=appearance(read('warp=0\nrot=.02\nzoom=0\n'))['activity']['motion_intensity']
    assert r['feedback_step_components']==[]


def test_single_colour_channel_can_still_have_a_whole_stage_blackout():
    r=appearance(shader('shader_body {ret=float3(GetPixel(uv).r*(sin(time*6)>0),0,0);}'))['activity']['flashing']
    assert r['hazards'] and r['hazards'][0]['off_rgb']==[0,0,0]


def test_singular_colour_factor_does_not_certify_blackout():
    r=appearance(shader('shader_body {ret=GetPixel(uv)*(sin(time*6)>0)*(1/0);}'))['activity']['flashing']
    assert r['hazards']==[]


def test_unknown_warp_cannot_hide_known_singular_zoom():
    r=appearance(read('zoom=0\nrot=.02\nper_frame_1=warp=bass;\n'))['activity']['motion_intensity']
    assert r['feedback_step_components']==[]


def test_full_turn_rotation_reports_effective_matrix_angle():
    r=appearance(read(f'warp=0\nrot={math.tau}\nzoom=1\n'))['activity']['motion_intensity']
    rotation=next(x for x in r['feedback_step_components'] if x['kind']=='rotation')
    assert rotation['absolute_radians_per_feedback_step']<1e-6


def test_unknown_rgb_denominator_retains_finite_intermediate_premise():
    r=appearance(shader('shader_body {ret=GetPixel(uv)*(sin(time*6)>0)*(1/bass);}'))['activity']['flashing']
    assert r['hazards']
    assert any('All contributing RGB intermediates' in c for c in r['conditions'])
