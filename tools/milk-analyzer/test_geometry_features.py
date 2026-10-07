"""Analytic trajectories catch time scaling, false joins and missing support."""
import importlib

import numpy as np
import pytest


def summarize(rows):
    return importlib.import_module('geometry_features').trajectory_summary(rows)


def row(time, position, key='shape:0:0'):
    return {'time': time, 'components': {key: [position]}}


def test_constant_translation_has_speed_but_no_acceleration_or_jerk():
    result = summarize([row(t, [2*t, 0]) for t in [0, .2, .7, 1.3]])
    assert result['speed']['p95'] == pytest.approx(2)
    assert result['acceleration']['maximum'] == pytest.approx(0, abs=1e-12)
    assert result['jerk']['maximum'] == pytest.approx(0, abs=1e-12)
    assert result['visible_motion'] is None
    assert result['uses_display_fields'] is False


def test_nonuniform_cubic_trajectory_recovers_third_derivative():
    result = summarize([row(t, [t**3, 0]) for t in [0, .1, .8, 1.4]])
    assert result['jerk']['p95'] == pytest.approx(6)
    assert result['jerk']['samples'] == 1
    assert result['interval_kind'] == 'sampled finite-difference estimates'


def test_missing_derivative_support_is_unknown_not_zero():
    result = summarize([row(0, [0, 0]), row(1, [0, 0])])
    assert result['speed']['p95'] == 0
    assert result['acceleration']['p95'] is None
    assert result['jerk']['p95'] is None


def test_component_replacement_does_not_invent_a_teleport():
    result = summarize([row(0, [0, 0], 'a'), row(1, [100, 0], 'b')])
    assert result['speed']['p95'] is None
    assert result['component_births'] == 1
    assert result['component_deaths'] == 1


def test_topology_change_breaks_derivative_history():
    rows = [row(0, [0, 0]), row(1, [1, 0]),
            {'time': 2, 'components': {'shape:0:0': [[100, 0], [200, 0]]}}]
    result = summarize(rows)
    assert result['speed']['maximum'] == 1
    assert result['acceleration']['p95'] is None
    assert result['topology_changes'] == 1


@pytest.mark.parametrize('rows', [
    [row(0, [0, 0]), row(0, [1, 0])],
    [row(1, [0, 0]), row(0, [1, 0])],
    [row(0, [float('nan'), 0])],
    [row(float('inf'), [0, 0])],
])
def test_invalid_time_or_geometry_is_not_scored(rows):
    with pytest.raises(ValueError):
        summarize(rows)


def test_scene_shape_instances_keep_separate_trajectories():
    module = importlib.import_module('geometry_features')
    scene = {'viewport': [128, 72], 'frames': []}
    for time in [0, 1, 2, 3]:
        scene['frames'].append({'render_inputs': {'time': time}, 'shapes': [
            {'index': 0, 'values': {'instance': 0, 'x': .1*time, 'y': .5, 'rad': .1}},
            {'index': 0, 'values': {'instance': 1, 'x': .8, 'y': .5, 'rad': .1}},
        ]})
    result = module.scene_geometry_features(scene)
    assert result['components_seen'] == 2
    assert result['speed']['maximum'] == pytest.approx(.1, abs=1e-7)
    assert result['jerk']['maximum'] == pytest.approx(0, abs=2e-7)
    assert result['geometry_scope'] == 'custom shape fan vertices'


def test_empty_scene_does_not_claim_the_preset_is_inactive():
    module = importlib.import_module('geometry_features')
    result = module.scene_geometry_features({'viewport': [32, 32], 'frames': [
        {'render_inputs': {'time': 0}, 'shapes': []}]})
    assert result['speed']['p95'] is None
    assert result['preset_activity'] is None
    assert result['unknown_reasons']


def test_authored_instance_variable_does_not_replace_physical_draw_identity():
    module = importlib.import_module('geometry_features')
    scene = {'viewport': [32, 32], 'frames': []}
    for time in [0, 1]:
        scene['frames'].append({'render_inputs': {'time': time}, 'shapes': [
            {'index': 0, 'values': {'instance': 0, 'x': .1*time, 'y': .5}},
            {'index': 0, 'values': {'instance': 0, 'x': .8, 'y': .5}},
        ]})
    result = module.scene_geometry_features(scene)
    assert result['components_seen'] == 2
    assert result['speed']['maximum'] == pytest.approx(.1, abs=1e-7)


def test_exceeded_derivative_budget_is_explicit_unknown_not_a_partial_score():
    module = importlib.import_module('geometry_features')
    rows = [row(t, [t, 0]) for t in range(5)]
    result = module.trajectory_summary(rows, max_derivative_samples=1)
    assert result['speed']['p95'] is None
    assert result['budget_exceeded'] is True
    assert any('budget' in reason for reason in result['unknown_reasons'])


def test_signed_source_translation_preserves_screen_direction():
    result = summarize([row(0, [.6, .5]), row(1, [.4, .6])])
    translation = result['component_translation']['shape:0:0']
    assert translation['displacement'] == pytest.approx([-.2, .1])
    assert translation['horizontal'] == 'left'
    assert translation['vertical'] == 'down'
    assert translation['matched_intervals'] == 1


def test_signed_translation_does_not_join_missing_or_changed_vertices():
    result = summarize([row(0, [0, 0]),
                        {'time': 1, 'components': {}},
                        row(2, [100, 0]),
                        {'time': 3, 'components': {'shape:0:0': [[200, 0], [201, 0]]}}])
    assert result['component_translation'] == {}


def test_budget_failure_withholds_partial_signed_translation():
    result = importlib.import_module('geometry_features').trajectory_summary(
        [row(t, [t, 0]) for t in range(5)], max_derivative_samples=1)
    assert result['component_translation'] == {}
    assert result['component_bounds'] == {}


def test_separated_source_components_keep_individual_location_bounds():
    result=summarize([{'time':0,'components':{'left':[[.02,.4],[.08,.6]],
                                             'right':[[.92,.4],[.98,.6]]}}])
    assert result['component_bounds']['left']['first']['minimum']==pytest.approx([.02,.4])
    assert result['component_bounds']['left']['first']['maximum']==pytest.approx([.08,.6])
    assert result['component_bounds']['right']['first']['minimum']==pytest.approx([.92,.4])
    assert result['uses_display_fields'] is False


def test_source_bounds_track_window_extent_without_clipping_outside_geometry():
    result=summarize([row(0,[-.2,.5]),row(1,[1.2,.6])])
    bounds=result['component_bounds']['shape:0:0']
    assert bounds['window']['minimum']==pytest.approx([-.2,.5])
    assert bounds['window']['maximum']==pytest.approx([1.2,.6])
    assert bounds['last']['minimum']==pytest.approx([1.2,.6])
    assert bounds['frames']==2


def test_scene_geometry_can_declare_a_sufficient_full_window_budget():
    module=importlib.import_module('geometry_features')
    scene={'viewport':[128,72],'frames':[
        {'render_inputs':{'time':t},'shapes':[
            {'index':0,'values':{'x':.1*t,'y':.5,'rad':.1,'sides':3}}]}
        for t in [0,1,2,3]]}
    limited=module.scene_geometry_features(scene,max_derivative_samples=1)
    assert limited['budget_exceeded'] and limited['speed']['p95'] is None
    complete=module.scene_geometry_features(scene,max_derivative_samples=100)
    assert not complete['budget_exceeded']
    assert complete['frames_sampled']==4
    assert complete['derivative_sample_budget']==100
    assert complete['speed']['p95']==pytest.approx(.1,abs=1e-7)
    assert complete['visible_motion'] is None

@pytest.mark.parametrize('budget',[True,0,-1,1.5])
def test_scene_geometry_rejects_invalid_declared_budget_even_with_no_shapes(budget):
    module=importlib.import_module('geometry_features')
    with pytest.raises(ValueError,match='budget'):
        module.scene_geometry_features({'viewport':[32,32],'frames':[]},
                                       max_derivative_samples=budget)
