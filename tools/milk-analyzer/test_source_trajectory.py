"""Paired source-coordinate paths, without projection or rendered frames."""
import math
import numpy as np
import pytest

from test_effect_families import read
from test_source_appearance import appearance


def path(body):
    d=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\nshape_0_per_frame1='+body+'\n'))
    e=next(e for e in d['elements'] if e['id']=='shape_0')
    assert 'center_trajectory' in e,'paired source trajectory is missing'
    return e['center_trajectory']


def test_constant_centre_is_stationary_source_path_not_still_feedback():
    t=path('x=.3;y=.6;')
    assert t['path_kind']=='stationary'
    assert t['center_source_xy']==pytest.approx([.3,.6])
    assert t['maximum_source_speed_units_per_second']==0
    assert t['visible_motion_speed'] is None


def test_linear_source_drift_has_joint_speed_and_direction():
    t=path('x=.5+.3*time;y=.5-.4*time;')
    assert t['path_kind']=='linear_drift'
    assert t['linear_velocity_source_xy']==pytest.approx([.3,-.4])
    assert t['maximum_source_speed_units_per_second']==pytest.approx(.5)


def test_quadrature_equal_amplitudes_form_source_circle():
    t=path('x=.5+.2*cos(2*time);y=.5+.2*sin(2*time);')
    assert t['path_kind']=='circle'
    assert t['period_seconds']==pytest.approx(math.pi)
    assert t['semiaxis_lengths_source_units']==pytest.approx([.2,.2])
    assert t['maximum_source_speed_units_per_second']==pytest.approx(.4)


def test_unequal_quadrature_amplitudes_form_source_ellipse():
    t=path('x=.5+.3*cos(2*time);y=.5+.1*sin(2*time);')
    assert t['path_kind']=='ellipse'
    assert t['semiaxis_lengths_source_units']==pytest.approx([.3,.1])
    assert t['maximum_source_speed_units_per_second']==pytest.approx(.6)


def test_identical_phase_functions_are_a_line_with_correlated_speed():
    t=path('x=.5+.3*sin(time+1);y=.5+.4*sin(time+1);')
    assert t['path_kind']=='line_oscillation'
    assert t['semiaxis_lengths_source_units'][0]==pytest.approx(.5)
    assert t['maximum_source_speed_units_per_second']==pytest.approx(.5)


def test_one_constant_axis_and_one_harmonic_axis_form_a_line():
    t=path('x=.5;y=.5+.2*sin(3*time);')
    assert t['path_kind']=='line_oscillation'
    assert t['maximum_source_speed_units_per_second']==pytest.approx(.6)


def test_negative_phase_rate_keeps_orientation_and_exact_joint_speed():
    t=path('x=.5+.2*cos(-2*time);y=.5+.2*sin(-2*time);')
    assert t['path_kind']=='circle'
    assert np.array(t['harmonic_matrix_source_xy'])==pytest.approx(np.array([[.2,0],[0,-.2]]))


def test_general_relative_phase_has_reconstructable_harmonic_matrix():
    t=path('x=.3+.2*cos(2*time+.4);y=.6+.1*sin(2*time-.7);')
    matrix=np.asarray(t['harmonic_matrix_source_xy'])
    for time in [0,.3,1.2]:
        predicted=np.asarray(t['center_source_xy'])+matrix@np.array([math.cos(2*time),math.sin(2*time)])
        assert predicted==pytest.approx([.3+.2*math.cos(2*time+.4),.6+.1*math.sin(2*time-.7)])


def test_different_rates_keep_path_family_and_global_period_unknown():
    t=path('x=.5+.1*cos(2*time);y=.5+.2*sin(3*time);')
    assert t['path_kind']=='independent_axis_curves'
    assert t['period_seconds'] is None
    assert t['speed_estimate_kind']=='upper_bound'
    assert t['maximum_source_speed_units_per_second']==pytest.approx(math.hypot(.2,.6))


@pytest.mark.parametrize('body',['x=bass;y=.5;', 'x=k;y=.5;', 'x=.5+sin(time*time);y=.5;'])
def test_unknown_axis_keeps_joint_trajectory_and_speed_unknown(body):
    t=path(body)
    assert t['path_kind']=='unknown'
    assert t['maximum_source_speed_units_per_second'] is None


def test_common_phase_circle_keeps_source_rotation():
    t=path('x=.5+.2*cos(time+1);y=.5+.2*sin(time+1);')
    assert t['path_kind']=='circle'
    assert t['semiaxis_lengths_source_units']==pytest.approx([.2,.2])


def test_overflowing_joint_speed_does_not_break_entire_source_export():
    t=path('x=1.6e308*time;y=1.6e308*time;')
    assert t['maximum_source_speed_units_per_second'] is None
    assert t['unknown_reasons']


def test_nearly_correlated_axes_are_not_classified_as_exact_line():
    t=path('x=.5+.3*sin(time+1);y=.5+.4*sin(time+1.00001);')
    assert t['path_kind']=='ellipse'
    assert t['semiaxis_lengths_source_units'][1]>0


@pytest.mark.parametrize('body',[
    'x=.5+.3*cos(time+1);y=.5+.4*cos(-time-1);',
    'x=.5+.3*sin(time+1);y=.5-.4*sin(-time-1);',
])
def test_opposite_rates_and_phases_keep_exact_source_line_identity(body):
    t=path(body)
    assert t['path_kind']=='line_oscillation'
    assert t['semiaxis_lengths_source_units']==pytest.approx([.5,0])


def test_opposite_rate_quadrature_equivalence_is_a_source_circle():
    t=path('x=.5+.2*cos(time+1);y=.5-.2*sin(-time-1);')
    assert t['path_kind']=='circle'
