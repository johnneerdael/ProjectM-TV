"""Pointwise spatial control envelopes are not uniform affine transforms."""
import math
import numpy as np
import pytest
from test_effect_families import read
from test_source_appearance import appearance


def description(pixel,frame='zoom=1;zoomexp=1;warp=0;'):
    return appearance(read('fWaveAlpha=0\nper_frame_1='+frame+'\nper_pixel_1='+pixel+'\n'
        'warp_1=`shader_body {ret=GetPixel(uv);}\n'))


def test_spatial_zoom_and_rotation_have_separate_control_envelope():
    d=description('zoom=1+.01*rad;rot=.1*(x-.5);')
    r=d['native_spatial_displacement']
    assert r['status']=='bounded_spatial_sampling_displacement'
    assert r['control_domains']['zoom']==pytest.approx([1,1+.01*math.sqrt(2)],rel=1e-6)
    assert r['uniform_across_vertices'] is False
    assert d['native_warp_transport']['status']=='unknown'


def test_spatial_displacement_bound_covers_independent_grid():
    d=description('zoom=1+.05*rad;rot=.2*(x-.5);dx=.02*sin(ang);')
    r=d['native_spatial_displacement'];t=r['rms_upper_bound_terms']
    for ax,ay in ((1,1),(1,.5625)):
        q=(np.arange(80)+.5)/80-.5;u,v=np.meshgrid(q,q);p=np.stack([ax*u,ay*v],axis=-1)
        radius=2*np.linalg.norm(p,axis=-1);x=ax*u+.5;angle=np.arctan2(-ay*v,ax*u)
        z=(1+.05*radius).astype(np.float32);rotation=(.2*(x-.5)).astype(np.float32)
        moved=p/z[...,None];cx=np.cos(rotation);sx=np.sin(rotation)
        sampled=np.stack([moved[...,0]*cx-moved[...,1]*sx-.02*np.sin(angle),moved[...,0]*sx+moved[...,1]*cx],axis=-1)
        rms=math.sqrt(np.mean(np.sum((sampled-p)**2,axis=-1)))
        assert rms<=t['translation_and_center']+t['centered_geometry']*math.hypot(ax,ay)+t['procedural_warp']


def test_spatial_descriptor_propagates_into_lookup_separately():
    d=description('zoom=1+.01*rad;')
    r=d['activity']['motion_intensity']['native_lookup_transport'][0]
    assert r['spatial_native_lookup_transport']['native_mesh_contribution']=='bounded'
    assert r['native_mesh_contribution']=='unknown'


@pytest.mark.parametrize('pixel',['zoom=x;','zoom=1;rot=rand(10);','zoom=1;rot=k;k=k+.1;','zoom=1;rot=reg00;'])
def test_zero_crossing_random_or_stateful_controls_do_not_receive_safe_domain(pixel):
    assert description(pixel)['native_spatial_displacement']['status']=='unknown'


def test_main_frame_x_is_not_reinterpreted_as_mesh_coordinate():
    d=description('zoom=1;rot=k;','zoom=1;zoomexp=1;warp=0;k=x;')
    assert d['native_spatial_displacement']['status']=='unknown'


def test_frame_coordinate_input_cannot_hide_behind_spatial_formula():
    d=description('zoom=1+.01*rad+k;','zoom=1;zoomexp=1;warp=0;k=x;')
    assert d['native_spatial_displacement']['status']=='unknown'


def test_spatial_curve_does_not_certify_fold_area_or_visible_speed():
    r=description('zoom=1+.01*rad;')['native_spatial_displacement']
    assert r['complete_sampling_map_area_ratio'] is None
    assert r['visible_motion_speed'] is None


def test_coordinate_domains_cover_native_float32_corner_and_angle_endpoints():
    r=description('zoom=1+.01*rad;rot=.01*ang;')['native_spatial_displacement']
    assert r['coordinate_input_domains']['rad'][1]>=float(np.float32(math.sqrt(2)))
    assert r['coordinate_input_domains']['ang'][1]>=float(np.float32(math.pi))


def test_authored_coordinate_change_uses_its_expression_not_reset_range():
    d=description('x=2*x;zoom=1+.01*x;')
    r=d['native_spatial_displacement']
    assert r['status']=='bounded_spatial_sampling_displacement'
    assert r['control_domains']['zoom'][1]>=float(np.float32(1.02))


def test_spatial_reciprocal_pole_keeps_displacement_unknown():
    assert description('zoom=1;dx=1/(x-.5);')['native_spatial_displacement']['status']=='unknown'


def test_bounded_sine_does_not_hide_cross_vertex_persistent_input():
    r=description('zoom=1+.01*rad;rot=.1*sin(k);k=k+1;')['native_spatial_displacement']
    assert r['status']=='unknown'
