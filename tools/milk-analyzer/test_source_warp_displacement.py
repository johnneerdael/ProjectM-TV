"""Analytic source sampling displacement, no frames or visible-speed claims."""
import math
import numpy as np
import pytest
from test_effect_families import read,shader
from test_source_appearance import appearance


def displacement(body,config=''):
    d=appearance(read('fWaveAlpha=0\n'+config+'per_frame_1=zoomexp=1;warp=0;'+body+'\n'))
    assert 'native_warp_displacement' in d,'native sampling displacement missing'
    return d['native_warp_displacement']


def test_identity_has_zero_nominal_rms_without_texel_or_visibility_claim():
    r=displacement('zoom=1;sx=1;sy=1;rot=0;dx=0;dy=0;')
    assert r['status']=='bounded_uniform_sampling_displacement'
    assert r['affine_rms_squared_aspect_coefficients']==[0,0,0]
    assert r['texel_alignment_included'] is False
    assert r['visible_motion_speed'] is None


def test_translation_rms_matches_displacement_length():
    r=displacement('zoom=1;sx=1;sy=1;rot=0;dx=.03;dy=-.04;')
    assert math.sqrt(r['affine_rms_squared_aspect_coefficients'][0])==pytest.approx(.05,abs=1e-8)
    assert r['affine_mean_displacement_aspect_corrected']==pytest.approx([-.03,.04],abs=1e-8)


def test_constant_zoom_rms_is_not_zero_despite_zero_parameter_rate():
    r=displacement('zoom=1.1;sx=1;sy=1;rot=0;')
    z=r['native_float32_controls']['zoom']
    expected=(1/z-1)**2/12
    assert r['affine_rms_squared_aspect_coefficients']==pytest.approx([0,expected,expected])


def test_rotation_stretch_center_rms_matches_independent_uniform_grid_integration():
    r=displacement('zoom=1.2;sx=1.3;sy=.8;rot=.3;cx=.3;cy=.7;dx=.04;dy=-.02;')
    p=r['native_float32_controls'];theta=p['rot'];R=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]])
    n=300;grid=(np.arange(n)+.5)/n-.5
    u,v=np.meshgrid(grid,grid)
    for ax,ay in [(1,1),(1,.5625),(.75,1)]:
        point=np.stack([ax*u,ay*v],axis=-1)
        rel=(point/p['zoom']+np.array([.5-p['cx'],.5-p['cy']]))/np.array([p['sx'],p['sy']])
        sampled=rel@R.T+np.array([p['cx']-p['dx']-.5,p['cy']-p['dy']-.5])
        actual=np.mean(np.sum((sampled-point)**2,axis=-1))
        coefficients=r['affine_rms_squared_aspect_coefficients']
        predicted=coefficients[0]+coefficients[1]*ax**2+coefficients[2]*ay**2
        assert predicted==pytest.approx(actual,rel=2e-5)


def test_dynamic_zoom_bound_covers_independent_parameter_points():
    r=displacement('zoom=1.1+.02*sin(time);sx=1;sy=1;rot=.01*sin(time);')
    assert r['affine_rms_squared_aspect_coefficients'] is None
    b=r['rms_upper_bound_terms']
    for t in (0,.4,1,3):
        z=1.1+.02*math.sin(t);theta=.01*math.sin(t);scale=1/z
        coeff=(scale**2-2*scale*math.cos(theta)+1)/12
        actual=math.sqrt(2*coeff)
        bound=b['translation_and_center']+b['centered_geometry']*math.sqrt(2)+b['procedural_warp']
        assert actual<=bound


def test_procedural_warp_has_separate_minkowski_displacement_term():
    r=displacement('zoom=1;sx=1;sy=1;rot=0;warp=.3;')
    assert r['rms_upper_bound_terms']['procedural_warp']==pytest.approx(math.sqrt(2)*2*.3*.0035,abs=1e-9)
    assert r['affine_rms_squared_aspect_coefficients']==[0,0,0]


@pytest.mark.parametrize('body',['zoom=0;','zoom=bass;','zoom=1;zoomexp=1.2;','zoom=1;rot=rand(10);'])
def test_unresolved_aggregate_domain_does_not_create_displacement(body):
    r=displacement(body)
    assert r['status']=='unknown'
    assert r['rms_upper_bound_terms'] is None


def test_invalid_warp_scale_does_not_disappear_when_warp_zero():
    r=displacement('zoom=1;',config='fWarpScale=0\n')
    assert r['status']=='unknown'


def test_disconnected_is_separate_from_unknown():
    r=appearance(shader('shader_body {ret=0;}'))['native_warp_displacement']
    assert r['status']=='not_contributing'


def test_dynamic_offcenter_stretch_bound_covers_independent_affine_rms():
    r=displacement('zoom=1.1+.02*sin(time);sx=1.2+.1*cos(time);sy=-.9;rot=.2*sin(time);cx=.3+.1*sin(time);cy=.6;dx=.03*cos(time);dy=-.02;')
    assert r['status']=='bounded_uniform_sampling_displacement'
    bounds=r['rms_upper_bound_terms']
    for t in (0,.4,1,3):
        z=1.1+.02*math.sin(t);sx=1.2+.1*math.cos(t);sy=-.9;rot=.2*math.sin(t)
        cx=.3+.1*math.sin(t);cy=.6;dx=.03*math.cos(t);dy=-.02
        c=math.cos(rot);s=math.sin(rot)
        B=np.array([[c,-s],[s,c]])@np.diag([1/(z*sx),1/(z*sy)])
        h=np.array([[c,-s],[s,c]])@np.diag([1/sx,1/sy])@np.array([.5-cx,.5-cy])+np.array([cx-dx-.5,cy-dy-.5])
        for ax,ay in [(1,1),(1,.5625),(.75,1)]:
            actual=math.sqrt(h@h+sum(np.sum((B-np.eye(2))[:,i]**2)*a*a/12 for i,a in enumerate([ax,ay])))
            bound=bounds['translation_and_center']+bounds['centered_geometry']*math.hypot(ax,ay)+bounds['procedural_warp']
            assert actual<=bound


@pytest.mark.parametrize('center,dx',[(1e20,.03),(.5,1e-20)])
def test_neutral_map_center_cancellation_cannot_lose_translation(center,dx):
    r=displacement(f'zoom=1;sx=1;sy=1;rot=0;cx={center};cy=.5;dx={dx};dy=0;')
    p=r['native_float32_controls']
    assert r['affine_mean_displacement_aspect_corrected']==pytest.approx([-p['dx'],0],rel=1e-12,abs=0)
    assert r['affine_rms_squared_aspect_coefficients'][0]==pytest.approx(p['dx']**2,rel=1e-12,abs=0)
