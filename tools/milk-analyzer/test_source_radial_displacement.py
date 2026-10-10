"""Compose a bounded native radial zoom into feedback displacement."""
import math
import numpy as np
import pytest
from test_effect_families import read
from test_source_appearance import appearance


def description(body,pixel='',configuration=''):
    return appearance(read('fWaveAlpha=0\n'+configuration+'per_frame_1=warp=0;'+body+'\n'+pixel+
        'warp_1=`shader_body {ret=GetPixel(uv);}\n'))


def test_nonunit_positive_radial_exponent_has_displacement_bound():
    d=description('zoom=1.1;zoomexp=2;')
    r=d['native_warp_displacement']
    assert r['status']=='bounded_uniform_sampling_displacement'
    assert r['sampling_model']=='uniform_radial_zoom_envelope'
    assert r['affine_rms_squared_aspect_coefficients'] is None
    assert d['activity']['motion_intensity']['native_lookup_transport'][0]['native_mesh_contribution']=='bounded'


def test_radial_composition_covers_independent_grid_and_parameters():
    d=description('zoom=1.1+.01*sin(time);zoomexp=2+.1*cos(time);sx=1.2;sy=.8;rot=.1;cx=.3;cy=.6;dx=.03;dy=-.02;warp=.2;')
    r=d['native_warp_displacement'];t=r['rms_upper_bound_terms']
    grid=(np.arange(80)+.5)/80-.5;x,y=np.meshgrid(grid,grid)
    for clock in (0,.5,1.7):
        z=float(np.float32(1.1+.01*math.sin(clock)));e=float(np.float32(2+.1*math.cos(clock)))
        theta=float(np.float32(.1));R=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]])
        for ax,ay in ((1,1),(1,.5625)):
            p=np.stack([ax*x,ay*y],axis=-1);radius=2*np.linalg.norm(p,axis=-1)
            factors=z**(e**(2*radius-1))
            rel=(p/factors[...,None]+np.array([.2,-.1]))/np.array([1.2,.8])
            sampled=rel@R.T+np.array([-.2-.03,.1+.02])
            actual=math.sqrt(np.mean(np.sum((sampled-p)**2,axis=-1)))
            upper=t['translation_and_center']+t['centered_geometry']*math.hypot(ax,ay)+t['procedural_warp']
            assert actual<=upper


def test_spatial_rotation_prevents_uniform_radial_composition():
    r=description('zoom=1.1;zoomexp=2;','per_pixel_1=rot=.1*rad;\n')['native_warp_displacement']
    assert r['status']=='unknown'


@pytest.mark.parametrize('body',['zoom=-1;zoomexp=2;','zoom=1.1;zoomexp=0;',
 'zoom=1.1;zoomexp=2;sx=0;','zoom=1e20;zoomexp=20;'])
def test_singular_negative_or_overflow_radial_domains_remain_unknown(body):
    assert description(body)['native_warp_displacement']['status']=='unknown'


def test_neutral_exponent_keeps_exact_affine_output():
    r=description('zoom=1.1;zoomexp=1;')['native_warp_displacement']
    assert r['affine_rms_squared_aspect_coefficients'] is not None


def test_invalid_warp_scale_is_not_hidden_by_radial_fallback():
    assert description('zoom=1.1;zoomexp=2;',configuration='fWarpScale=0\n')['native_warp_displacement']['status']=='unknown'


def test_neutral_zoom_with_curved_exponent_keeps_near_identity_bound():
    r=description('zoom=1;zoomexp=2;sx=1;sy=1;rot=0;dx=0;dy=0;')['native_warp_displacement']
    assert r['status']=='bounded_uniform_sampling_displacement'
    t=r['rms_upper_bound_terms']
    assert t['translation_and_center']==0
    assert t['centered_geometry']<1e-12


def test_dynamic_center_stretch_and_radial_scale_are_jointly_bounded():
    r=description('zoom=1.1+.01*sin(time);zoomexp=2;sx=1.2+.1*cos(time);sy=-.8;cx=.3+.1*sin(time);cy=.6;rot=.1*sin(time);')['native_warp_displacement']
    assert r['status']=='bounded_uniform_sampling_displacement'
    assert all(math.isfinite(v) and v>=0 for v in r['rms_upper_bound_terms'].values())
