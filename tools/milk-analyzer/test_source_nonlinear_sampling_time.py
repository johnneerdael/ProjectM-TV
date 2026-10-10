"""Non-affine lookup partial time derivatives keep mesh and texture history fixed."""
import math
import pytest
from test_effect_families import shader,analyze
from test_source_appearance import appearance


def description(code):return appearance(shader('shader_body {'+code+'}'))
def motion(code):return description(code)['sampling_geometry']['stages']['composite'][0]['sampling_motion']


def test_spatial_sine_ripple_has_partial_time_speed():
    r=motion('ret=GetPixel(uv+float2(.02*sin(8*uv.y+3*time),0));')
    assert r['maximum_lookup_axis_speed_uv_per_second']==pytest.approx([.06,0],rel=1e-6)
    assert r['maximum_feature_speed_basis_uv_per_second'] is None
    assert r['signed_feature_velocity_basis_uv_per_second'] is None


def test_two_axis_nonlinear_lookup_preserves_separate_rates():
    r=motion('ret=GetPixel(float2(sin(uv.x+2*time),cos(uv.y-3*time)));')
    assert r['maximum_lookup_axis_speed_uv_per_second']==pytest.approx([2,3],rel=1e-6)


def test_time_independent_spatial_nonlinearity_has_zero_partial_time_rate():
    r=motion('ret=GetPixel(sin(uv*8));')
    assert r['maximum_lookup_axis_speed_uv_per_second']==[0,0]
    assert r['total_lookup_speed_uv_per_second'] is None


def test_nonlinear_lookup_motion_reaches_rgb_gradient_coefficients():
    d=description('ret=.5*GetPixel(uv+float2(.02*sin(uv.y+3*time),0));')
    r=d['activity']['motion_intensity']['texture_motion_bounds'][0]
    assert r['linear_texture_rgb_rate_coefficients_per_dimension'][0]==pytest.approx([.03,0],rel=1e-6)


def test_nonlinear_audio_time_gain_requires_declared_amplitude():
    s=shader('shader_body {ret=GetPixel(uv+float2(.02*bass*sin(uv.y+3*time),0));}')
    d=analyze(s,input_scenario={'schema_version':1,'name':'ripple-time','audio_band_ranges':{'bass':[0,2]}})['visual_description']
    r=d['sampling_geometry']['stages']['composite'][0]['sampling_motion']
    assert r['maximum_lookup_axis_speed_uv_per_second'][0] is None
    assert r['scenario_sampling_motion']['maximum_lookup_axis_speed_uv_per_second']==pytest.approx([.12,0],rel=1e-6)


@pytest.mark.parametrize('coords',[
    'frac(uv+time)',
    'floor(uv+time)',
    'uv+float2(time/0,0)',
    'uv+GetBlur1(uv+time).rg',
    'float2(uv.x*time,uv.y)',
])
def test_discontinuous_singular_image_driven_or_unbounded_rate_is_not_certified(coords):
    r=motion('ret=GetPixel('+coords+');')
    assert any(x is None for x in r['maximum_lookup_axis_speed_uv_per_second'])


def test_independent_ripple_samples_respect_continuous_rate_bound():
    r=motion('ret=GetPixel(uv+float2(.02*sin(8*uv.y+3*time),.03*cos(5*uv.x-2*time)));')
    ceilings=r['maximum_lookup_axis_speed_uv_per_second']
    assert all(v is not None for v in ceilings)
    for x,y,t,dt in ((-.5,2,0,.01),(1.2,-3,3.1,.1),(0,0,10,-.02)):
        a=(x+.02*math.sin(8*y+3*t),y+.03*math.cos(5*x-2*t))
        b=(x+.02*math.sin(8*y+3*(t+dt)),y+.03*math.cos(5*x-2*(t+dt)))
        assert all(abs(v-u)<=bound*abs(dt)+1e-12 for u,v,bound in zip(a,b,ceilings))
