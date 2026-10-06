"""Source warp queries and inverse-map transport require no image history."""
import importlib

import numpy as np
import pytest


def test_time_independent_translation_moves_feedback_every_update():
    module=importlib.import_module('source_transport')
    result=module.affine_transport([[1,0],[0,1]],[-.01,0],[[.5,.5]],dt=1/30)
    assert result['speed_p95_vp_s']==pytest.approx(.3)
    np.testing.assert_allclose(result['next_positions'],[[.51,.5]])
    assert result['visible_motion_established'] is False


def test_static_rotation_uses_inverse_query_map_not_zero_time_derivative():
    module=importlib.import_module('source_transport')
    result=module.affine_transport([[0,1],[-1,0]],[0,1],[[.75,.5]],dt=1/30)
    np.testing.assert_allclose(result['next_positions'],[[.5,.75]])
    assert result['speed_p95_vp_s']==pytest.approx(np.sqrt(.125)*30)


def test_singular_transport_or_unmodeled_boundary_policy_stays_unknown():
    module=importlib.import_module('source_transport')
    with pytest.raises(ValueError,match='invertible'):
        module.affine_transport([[0,0],[0,0]],[0,0],[[.5,.5]],dt=.1)
    with pytest.raises(ValueError,match='boundary'):
        module.affine_transport([[1,0],[0,1]],[0,0],[[.5,.5]],dt=.1,boundary='wrap')


def test_outside_viewport_transport_does_not_claim_visible_movement():
    module=importlib.import_module('source_transport')
    result=module.affine_transport([[1,0],[0,1]],[-2,0],[[.5,.5]],dt=.1)
    assert result['points_exiting_viewport']==1
    assert result['visible_motion_established'] is False


def test_sparse_warp_queries_reuse_native_mesh_without_viewport_surface():
    from scene_equations import execute_scene
    from scene_warp import warp_fields
    from test_scene_equations import native,frames
    from test_native_reader import READER
    source=native('warp=0\nzoom=1\ndx=.1\n')
    scene=execute_scene(source,frames()[:1],reader=READER,width=3840,height=2160,mesh_x=8,mesh_y=8)
    result=warp_fields(source,scene,0,query_uv=[[.25,.5],[.75,.5]])
    assert result['uv'].shape==(2,2)
    assert result['polar'].shape==(2,2)
    assert result['query_kind']=='isolated mesh queries'
    np.testing.assert_allclose(result['uv'],[[.15,.5],[.65,.5]],atol=1e-6)


def test_restricted_scalar_decay_reports_half_life_and_injection_bound():
    module=importlib.import_module('source_transport')
    result=module.linear_feedback_bounds(.98,fps=30,initial_bound=0,injection_bound=.01,steps=30)
    assert result['half_life_s']==pytest.approx(1.1436539504967687)
    assert result['asymptotic_state_bound']==pytest.approx(.5)
    assert result['state_bound_after_steps']==pytest.approx(.22725784030878144)
    assert result['source_recurrence_proved'] is False


@pytest.mark.parametrize('gain',[-.1,1,1.01,float('nan')])
def test_unstable_or_invalid_gain_is_not_assigned_a_gentle_half_life(gain):
    module=importlib.import_module('source_transport')
    with pytest.raises(ValueError):
        module.linear_feedback_bounds(gain,fps=30,initial_bound=1,injection_bound=0,steps=30)


def test_positive_feedback_underflow_is_not_returned_as_zero_upper_bound():
    module=importlib.import_module('source_transport')
    with pytest.raises(ValueError,match='underflow'):
        module.linear_feedback_bounds(1e-300,fps=30,initial_bound=1e-300,injection_bound=0,steps=1)


def test_half_life_reorders_arithmetic_to_avoid_overflowing_denominator():
    module=importlib.import_module('source_transport')
    result=module.linear_feedback_bounds(1e-300,fps=1e308,initial_bound=0,injection_bound=0,steps=1)
    assert result['half_life_s']>0
    assert result['half_life_s']==pytest.approx(1.0034333188799372e-311,rel=1e-10,abs=0)
