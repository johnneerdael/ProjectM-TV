"""Nominal vertex-motion bounds derived from known custom-shape formulas."""
import math
import pytest
from test_effect_families import read
from test_source_appearance import appearance


def model(body):
    d=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\nshape_0_per_frame1='+body+'\n'))
    shape=next(e for e in d['elements'] if e['id']=='shape_0')
    assert 'vertex_motion' in shape, 'nominal shape vertex-motion descriptor is missing'
    return shape['vertex_motion']


def test_stationary_vertices_are_distinct_from_stationary_feedback():
    m=model('x=.5;y=.5;rad=.2;ang=0;sides=4;')
    assert m['maximum_vertex_speed_ndc_per_second_upper_bound']==0
    assert m['visible_motion_speed'] is None


def test_centre_speed_converts_authored_coordinates_to_ndc():
    m=model('x=.5+.3*time;y=.5-.4*time;rad=.2;ang=0;sides=4;')
    assert m['centre_speed_ndc_per_second_upper_bound']==pytest.approx(1)
    assert m['maximum_vertex_speed_ndc_per_second_upper_bound']==pytest.approx(1)


def test_rotation_speed_scales_with_absolute_radius():
    m=model('x=.5;y=.5;rad=-.2;ang=3*time;sides=4;')
    assert m['maximum_absolute_radius_ndc']==pytest.approx(.2)
    assert m['maximum_vertex_speed_ndc_per_second_upper_bound']==pytest.approx(.6)


def test_breathing_radius_and_rotation_use_orthogonal_components():
    m=model('x=.5;y=.5;rad=.2+.1*sin(2*time);ang=3*time;sides=4;')
    assert m['maximum_radius_rate_ndc_per_second']==pytest.approx(.2)
    assert m['maximum_vertex_speed_ndc_per_second_upper_bound']==pytest.approx(math.hypot(.2,.9))
    # Independently differentiate one unprojected vertex for multiple phases.
    for t in [0,.1,.7,1.8,4.2]:
        r=.2+.1*math.sin(2*t);dr=.2*math.cos(2*t);a=3*t
        dx=dr*math.cos(a)-3*r*math.sin(a)
        dy=dr*math.sin(a)+3*r*math.cos(a)
        assert math.hypot(dx,dy)<=m['maximum_vertex_speed_ndc_per_second_upper_bound']+1e-12


def test_centre_and_local_motion_sum_is_bound_not_exact_joint_peak():
    m=model('x=.5+.1*cos(time);y=.5+.1*sin(time);rad=.2;ang=3*time;sides=4;')
    assert m['maximum_vertex_speed_ndc_per_second_upper_bound']==pytest.approx(.8)
    assert m['estimate_kind']=='upper_bound'


def test_unbounded_linear_radius_with_static_angle_has_finite_speed():
    m=model('x=.5;y=.5;rad=.2+.1*time;ang=0;sides=4;')
    assert m['maximum_absolute_radius_ndc'] is None
    assert m['maximum_vertex_speed_ndc_per_second_upper_bound']==pytest.approx(.1)


def test_unbounded_linear_radius_with_rotation_has_no_lifetime_speed_bound():
    m=model('x=.5;y=.5;rad=.2+.1*time;ang=time;sides=4;')
    assert m['maximum_vertex_speed_ndc_per_second_upper_bound'] is None
    assert m['unknown_reasons']


@pytest.mark.parametrize('body',[
    'x=bass;y=.5;rad=.2;ang=0;sides=4;',
    'x=.5;y=.5;rad=bass;ang=0;sides=4;',
    'x=.5;y=.5;rad=.2;ang=bass;sides=4;',
    'x=.5;y=.5;rad=.2;ang=0;sides=3+bass;',
    'x=.5;y=.5;rad=.2;ang=time*time;sides=4;',
])
def test_unresolved_or_discrete_controls_do_not_claim_smooth_motion(body):
    m=model(body)
    assert m['maximum_vertex_speed_ndc_per_second_upper_bound'] is None
    assert m['unknown_reasons']


def test_collapsed_radius_does_not_need_unknown_angle_rate():
    from shader_fields import Field
    from source_motion import planar_trajectory,shape_vertex_motion
    controls={name:Field('constant',detail={'value':value}) for name,value in [('x',.5),('y',.5),('rad',0)]}
    controls['ang']=Field('input',detail={'name':'bass'})
    t=planar_trajectory([controls['x'],controls['y']])
    m=shape_vertex_motion(controls,{'effective_sides':4},t)
    assert m['maximum_vertex_speed_ndc_per_second_upper_bound']==0


def test_huge_derived_speed_keeps_json_finite():
    m=model('x=8e307*time;y=0;rad=1e30;ang=1e308*time;sides=4;')
    assert m['maximum_vertex_speed_ndc_per_second_upper_bound'] is None
    assert m['unknown_reasons']


@pytest.mark.parametrize('body',[
    'x=1e40;y=.5;rad=.2;ang=0;sides=4;',
    'x=2e38;y=.5;rad=.2;ang=0;sides=4;',
    'x=.5;y=1e40;rad=.2;ang=0;sides=4;',
    'x=.5;y=.5;rad=1e40;ang=0;sides=4;',
    'x=.5;y=.5;rad=.2;ang=1e40;sides=4;',
])
def test_known_nonfinite_native_conversion_does_not_get_vacuous_speed_bound(body):
    m=model(body)
    assert m['maximum_vertex_speed_ndc_per_second_upper_bound'] is None
    assert any('float32' in reason for reason in m['unknown_reasons'])


def test_zero_radius_does_not_cancel_infinite_native_angle():
    from shader_fields import Field
    from source_motion import planar_trajectory,shape_vertex_motion
    controls={name:Field('constant',detail={'value':value}) for name,value in [('x',.5),('y',.5),('rad',0),('ang',1e40)]}
    t=planar_trajectory([controls['x'],controls['y']])
    m=shape_vertex_motion(controls,{'effective_sides':4},t)
    assert m['maximum_vertex_speed_ndc_per_second_upper_bound'] is None
    assert any('float32' in reason for reason in m['unknown_reasons'])


@pytest.mark.parametrize('body',[
    'x=2e38+sin(0*time);y=.5;rad=.2;ang=0;sides=4;',
    'x=.5;y=1e40+sin(0*time);rad=.2;ang=0;sides=4;',
    'x=.5;y=.5;rad=1e40+sin(0*time);ang=0;sides=4;',
    'x=.5;y=.5;rad=.2;ang=1e40+sin(0*time);sides=4;',
])
def test_derived_constant_curve_is_checked_against_native_conversion(body):
    m=model(body)
    assert m['maximum_vertex_speed_ndc_per_second_upper_bound'] is None
    assert any('float32' in reason for reason in m['unknown_reasons'])
