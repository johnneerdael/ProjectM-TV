"""Frozen uniform-control transport bounds; no image or time samples."""
import math
import pytest
from test_effect_families import read
from test_source_appearance import appearance


def transport(body):
    d=appearance(read('fWaveAlpha=0\nper_frame_1=zoomexp=1;warp=0;'+body+'\n'))
    assert 'native_warp_transport' in d,'source transport envelope missing'
    return d['native_warp_transport']


def test_dynamic_uniform_zoom_has_expansion_range_not_zero_motion():
    r=transport('zoom=1.1+.02*sin(time);sx=1;sy=1;rot=.2*sin(time);')
    assert r['status']=='bounded_uniform_affine_component'
    assert r['source_to_output_axis_scales']['x']==pytest.approx([1.08,1.12],abs=2e-7)
    assert r['axis_scale_behavior']['x']=='expansion'
    assert r['area_ratio_source_to_output']==pytest.approx([1.08**2,1.12**2],abs=5e-7)
    assert r['visible_screen_motion'] is None


def test_bounded_audio_controls_keep_timing_unknown_and_inputs_declared():
    r=transport('zoom=1+.02*sin(bass);sx=1;sy=1;rot=sin(mid);')
    assert r['status']=='bounded_uniform_affine_component'
    assert r['axis_scale_behavior']['x']=='crosses_neutral'
    assert r['controls']['zoom']['raw_time_curve']['maximum_absolute_control_rate_per_second'] is None
    assert 'bass' in r['controls']['zoom']['assumed_finite_input_names']


def test_negative_zoom_and_stretch_retain_orientation_parity():
    r=transport('zoom=-1.1;sx=-.5;sy=2;')
    assert r['orientation']=='reversing'
    assert r['source_to_output_axis_scales']['x']==pytest.approx([.55,.55],abs=2e-7)
    assert r['axis_scale_behavior']=={'x':'contraction','y':'expansion'}


def test_zero_crossing_zoom_abstains_instead_of_bounded_transform():
    r=transport('zoom=sin(time);sx=1;sy=1;')
    assert r['status']=='unknown'
    assert r['area_ratio_source_to_output'] is None
    assert r['unknown_reasons']


def test_spatial_controls_are_not_given_uniform_affine_area():
    r=appearance(read('fWaveAlpha=0\nper_frame_1=zoomexp=1;warp=0;\nper_pixel_1=zoom=1+.01*rad;\n'))
    assert 'native_warp_transport' in r
    r=r['native_warp_transport']
    assert r['status']=='unknown'
    assert r['area_ratio_source_to_output'] is None
    assert len(r['controls'])==10


def test_radial_zoom_power_keeps_affine_envelope_unknown():
    r=transport('zoom=1.1;zoomexp=1.2;')
    assert r['status']=='unknown'


def test_underflowed_scale_or_overflowed_float_conversion_abstains():
    for body in ('zoom=1e-50;sx=1;sy=1;','zoom=1;sx=1e-40;sy=1;','zoom=1e40;sx=1;sy=1;'):
        r=transport(body)
        assert r['status']=='unknown'
        assert r['unknown_reasons']


def test_nonzero_warp_does_not_promote_affine_area_to_complete_map():
    r=transport('zoom=1.1;warp=.3;sx=1;sy=1;')
    assert r['status']=='bounded_uniform_affine_component'
    assert r['complete_sampling_map_area_ratio'] is None
    assert r['procedural_warp_present'] is True


def test_neutral_is_classified_after_float32_conversion():
    r=transport('zoom=1.00000001;sx=1;sy=1;')
    assert r['axis_scale_behavior']=={'x':'neutral','y':'neutral'}


def test_unknown_zoom_keeps_independent_rotation_and_translation_domains():
    r=transport('zoom=bass;rot=.02*sin(time);dx=.01;')
    assert r['status']=='unknown'
    assert len(r['controls'])==10
    assert r['controls']['rot']['native_float32_endpoint_domain']==pytest.approx([-.02,.02],abs=1e-8)


def test_persistent_pixel_state_does_not_become_uniform_control():
    r=appearance(read('fWaveAlpha=0\nper_frame_1=zoomexp=1;warp=0;\nper_pixel_1=q1=q1+.01;zoom=1.1+sin(q1)*.01;\n'))['native_warp_transport']
    assert r['status']=='unknown'
    assert r['controls']['zoom']['uniform_across_vertices'] is False


def test_disconnected_feedback_is_separate_from_unknown():
    from test_effect_families import shader
    r=appearance(shader('shader_body {ret=0;}'))['native_warp_transport']
    assert r['status']=='not_contributing'


@pytest.mark.parametrize('control',['rot','dx','cx'])
def test_per_vertex_random_is_not_uniform_despite_no_named_dependencies(control):
    r=appearance(read('fWaveAlpha=0\nper_frame_1=zoom=1.1;zoomexp=1;warp=0;\nper_pixel_1='+control+'=rand(10);\n'))['native_warp_transport']
    assert r['status']=='unknown'
    assert r['unknown_reasons']
    assert r['controls'][control]['uniform_across_vertices'] is False
