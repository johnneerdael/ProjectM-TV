"""Execution-phase snapshots are uniform without becoming known state values."""
import pytest
from test_effect_families import read
from test_source_appearance import appearance


def desc(raw):return appearance(read('fWaveAlpha=0\n'+raw))


def test_main_frame_persistent_state_is_uniform_but_has_unknown_rate():
    d=desc('per_frame_init_1=musicclock=0;\nper_frame_1=musicclock=musicclock+.1*bass;zoom=1.1+.01*sin(musicclock);zoomexp=1;warp=0;\n')
    t=d['native_warp_transport'];r=t['controls']['zoom']
    assert r['uniform_across_vertices'] is True
    assert t['status']=='bounded_uniform_affine_component'
    assert r['raw_time_curve']['maximum_absolute_control_rate_per_second'] is None
    assert r['uniformity_basis']=='frozen main/init phase scalar snapshots and readonly frame inputs'


def test_bare_main_local_read_is_frozen_without_inventing_zero():
    d=desc('per_frame_1=rot=.02*sin(musicclock);zoom=1.1;zoomexp=1;warp=0;\n')
    r=d['native_warp_transport']['controls']['rot']
    assert r['uniform_across_vertices'] is True
    assert r['native_float32_endpoint_domain']==pytest.approx([-.02,.02],abs=1e-8)
    assert r['raw_time_curve']['constant_value'] is None


def test_pixel_local_read_remains_unresolved_uniformity():
    d=desc('per_frame_1=zoom=1.1;zoomexp=1;warp=0;\nper_pixel_1=rot=.02*sin(musicclock);\n')
    r=d['native_warp_transport']['controls']['rot']
    assert r['uniform_across_vertices'] is False
    assert d['native_warp_transport']['status']=='unknown'


def test_pixel_q_mutation_overrides_copied_main_snapshot():
    d=desc('per_frame_init_1=musicclock=0;\nper_frame_1=musicclock=musicclock+.1;q1=musicclock;zoom=1.1;zoomexp=1;warp=0;\nper_pixel_1=q1=q1+.1;rot=.02*sin(q1);\n')
    assert d['native_warp_transport']['controls']['rot']['uniform_across_vertices'] is False


def test_main_q_copy_without_pixel_mutation_preserves_frozen_phase():
    d=desc('per_frame_init_1=musicclock=0;\nper_frame_1=musicclock=musicclock+.1;q1=musicclock;zoom=1.1;zoomexp=1;warp=0;\nper_pixel_1=rot=.02*sin(q1);\n')
    assert d['native_warp_transport']['controls']['rot']['uniform_across_vertices'] is True


def test_phase_provenance_is_serialized_on_source_expression_inputs():
    d=desc('per_frame_1=rot=.02*sin(musicclock);zoom=1.1;zoomexp=1;warp=0;\n')
    e=next(e for e in d['elements'] if e['id']=='mesh_warp')
    curve=next(c for c in e['motion_controls'] if c['control']=='rotation')
    inputs=[n for n in curve['expression']['nodes'] if n['op']=='input' and n['detail'].get('name')=='musicclock']
    assert inputs[0]['detail']['equation_phase']=='per_frame_'
    assert inputs[0]['detail']['value_binding']=='phase_scalar_snapshot'


def test_shared_register_and_per_pixel_rand_keep_guard():
    d=desc('per_frame_1=rot=.02*sin(reg00);zoom=1.1;zoomexp=1;warp=0;\n')
    assert d['native_warp_transport']['controls']['rot']['uniform_across_vertices'] is False
    d=desc('per_frame_1=zoom=1.1;zoomexp=1;warp=0;\nper_pixel_1=rot=rand(10);\n')
    assert d['native_warp_transport']['controls']['rot']['uniform_across_vertices'] is False


def test_main_local_named_like_coordinate_does_not_invent_spatial_rotation():
    from test_effect_families import analyze,families
    d=analyze(read('fWaveAlpha=0\nper_frame_1=rot=.02*sin(rad);zoom=1.1;zoomexp=1;warp=0;\n'))
    assert d['visual_description']['native_warp_transport']['controls']['rot']['uniform_across_vertices'] is True
    assert 'radial_twist' not in families(d)


def test_real_pixel_radius_still_identifies_radial_twist():
    from test_effect_families import analyze,families
    d=analyze(read('fWaveAlpha=0\nper_pixel_1=rot=.02*rad;\n'))
    assert 'radial_twist' in families(d)


def test_conditional_main_and_pixel_same_named_inputs_do_not_merge():
    from test_effect_families import analyze,families
    d=analyze(read('fWaveAlpha=0\nper_frame_1=rot=rad;zoom=1.1;zoomexp=1;warp=0;\nper_pixel_1=if(above(bass,1),rot=rot,rot=rad);\n'))
    assert d['visual_description']['native_warp_transport']['controls']['rot']['uniform_across_vertices'] is False
    assert d['visual_description']['native_warp_transport']['status']=='unknown'
    assert 'radial_twist' in families(d)
