"""Audio-centre response uses source coordinates, not a guessed temporal speed."""
import pytest
from test_effect_families import read,analyze


def response(body,scenario=None,extra=''):
    r=analyze(read('fWaveAlpha=0\nshapecode_0_enabled=1\n'+extra+'shape_0_per_frame1='+body+'\n'),input_scenario=scenario)
    e=next(e for e in r['visual_description']['elements'] if e['id']=='shape_0')
    assert 'audio_center_response' in e,'shape centre response model missing'
    return e['audio_center_response']


def test_bass_center_gain_keeps_axis_sign_in_source_program_and_numeric_ceiling():
    r=response('x=.5+.1*bass;y=.5-.2*bass;')
    assert r['matrix_center_xy_per_audio_unit_upper_bounds'][0][0]==pytest.approx(.1)
    assert r['matrix_center_xy_per_audio_unit_upper_bounds'][1][0]==pytest.approx(.2)
    assert r['maximum_center_ndc_distance_per_audio_unit_upper_bounds'][0]==pytest.approx(2*(.1**2+.2**2)**.5)
    assert r['maximum_center_speed_ndc_per_second'] is None


def test_declared_band_range_bounds_nonlinear_audio_center_displacement():
    s={'schema_version':1,'name':'centre range','audio_band_ranges':{'bass':[0,2]}}
    r=response('x=.5+.1*bass*bass;y=.5;',s)
    assert r['matrix_center_xy_per_audio_unit_upper_bounds'][0][0] is None
    conditional=r['scenario_center_response']
    assert conditional['matrix_center_xy_per_audio_unit_upper_bounds'][0][0]==pytest.approx(.4)
    assert conditional['maximum_two_state_center_ndc_distance_upper_bound']==pytest.approx(.8,abs=1e-6)
    assert conditional['observed_runtime_inputs'] is False


def test_unknown_state_multiplier_stays_unknown_without_declared_state():
    r=response('x=.5+bass*k;y=.5;')
    assert r['matrix_center_xy_per_audio_unit_upper_bounds'][0][0] is None


def test_discontinuous_comparison_center_does_not_gain_lipschitz_response():
    r=response('x=above(bass,1);y=.5;')
    assert r['matrix_center_xy_per_audio_unit_upper_bounds'][0][0] is None


def test_shape_init_audio_snapshot_is_not_current_bass_response():
    r=response('x=k;y=.5;',extra='shape_0_init1=k=bass;\n')
    assert r['matrix_center_xy_per_audio_unit_upper_bounds'][0][0]==0


def test_nonlinear_declared_gain_bounds_independent_pairs():
    s={'schema_version':1,'name':'centre pairs','audio_band_ranges':{'bass':[0,2],'mid':[0,2]}}
    r=response('x=.5+.1*bass*bass;y=.5+.2*mid;',s)['scenario_center_response']
    matrix=r['matrix_center_xy_per_audio_unit_upper_bounds']
    for a in (0,.1,.5,1,1.5,2):
        for b in (0,.2,.9,1.7,2):
            assert abs(.1*(a*a-b*b))<=matrix[0][0]*abs(a-b)+1e-12
    assert r['maximum_two_state_center_ndc_distance_upper_bound']>=2*(.4**2+.4**2)**.5


def test_known_invalid_coordinate_does_not_gain_response():
    r=response('x=1e308*1e308*bass;y=.5;')
    assert r['matrix_center_xy_per_audio_unit_upper_bounds'][0][0] is None


def test_disconnected_band_is_zero_even_when_other_band_moves():
    r=response('x=.5+.1*bass;y=.5;')
    assert r['matrix_center_xy_per_audio_unit_upper_bounds'][0][1:]==[0]*5


def test_outward_rounding_overflow_keeps_null_instead_of_breaking_json():
    r=response('x=8.988465674311577e307*bass;y=.5;')
    assert r['maximum_center_ndc_distance_per_audio_unit_upper_bounds'][0] is None
