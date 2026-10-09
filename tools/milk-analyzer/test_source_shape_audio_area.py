"""Nominal audio-dependent polygon area, from source algebra only."""
import numpy as np
import pytest

from test_effect_families import read
from test_source_appearance import appearance


def response(body,extra=''):
    d=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\nshapecode_0_sides=4\n'
        +extra+'shape_0_per_frame1='+body+'\n'))
    e=next(e for e in d['elements'] if e['id']=='shape_0')
    assert 'audio_area_response' in e,'nominal audio-area response is missing'
    return e['audio_area_response']


def polynomial_value(poly,inputs):
    a=np.asarray(inputs)
    return poly['constant']+np.asarray(poly['linear'])@a+a@np.asarray(poly['quadratic_matrix'])@a


def test_bass_radius_produces_quadratic_area_and_sensitivity():
    r=response('rad=.2+.1*bass;a=1;a2=0;')
    assert r['source_model']=='affine_audio_radius'
    assert r['input_codes']==[1]
    assert r['radius_bias']==pytest.approx(.2)
    assert r['radius_gains']==pytest.approx([.1])
    p=r['nominal_area_polynomial_per_aspect_y']
    assert p['constant']==pytest.approx(.02)
    assert p['linear']==pytest.approx([.02])
    assert np.array(p['quadratic_matrix'])==pytest.approx(np.array([[.005]]))
    assert polynomial_value(p,[2])==pytest.approx(.08)
    assert r['area_derivative_constant_per_aspect_y']==pytest.approx([.02])
    assert np.array(r['area_derivative_linear_matrix_per_aspect_y'])==pytest.approx(np.array([[.01]]))
    assert r['area_to_alpha_integral_factor']==pytest.approx(1/3)
    assert r['visible_bass_response_strength'] is None


def test_multiple_bands_keep_cross_terms_and_input_order():
    r=response('rad=.1+.2*bass-.05*treb_att;')
    assert r['input_codes']==[1,6]
    p=r['nominal_area_polynomial_per_aspect_y']
    # Off-diagonal entries participate twice in a^T Q a.
    assert np.array(p['quadratic_matrix'])==pytest.approx(np.array([[.02,-.005],[-.005,.00125]]))
    for bass,treb in [(0,0),(1,2),(2,.5),(-1,2)]:
        assert polynomial_value(p,[bass,treb])==pytest.approx(.5*(.1+.2*bass-.05*treb)**2)


def test_straight_line_local_alias_is_resolved_from_source():
    r=response('k=.2+bass*.1;rad=k;')
    assert r['input_codes']==[1]
    assert r['radius_bias']==pytest.approx(.2)


@pytest.mark.parametrize('formula',[
    'bass*bass', 'abs(bass)', 'sin(bass)', 'min(.2,bass)',
    '.1+bass*.1+time*.01', '.1+bass*k',
])
def test_nonlinear_state_and_time_terms_do_not_become_audio_polynomials(formula):
    r=response('rad='+formula+';')
    assert r['source_model']=='unknown'
    assert r['nominal_area_polynomial_per_aspect_y'] is None
    assert r['input_codes'] is None
    assert r['unknown_reasons']


def test_init_audio_snapshot_is_not_current_band():
    r=response('rad=k;',extra='shape_0_init1=k=bass;\n')
    assert r['source_model']=='unknown'


def test_dynamic_side_count_keeps_area_unknown():
    r=response('rad=.2+bass*.1;sides=mid;')
    assert r['nominal_area_polynomial_per_aspect_y'] is None
    assert r['unknown_reasons']


def test_textured_fill_keeps_geometry_formula_but_material_factor_unknown():
    r=response('rad=.2+bass*.1;',extra='shapecode_0_textured=1\n')
    assert r['nominal_area_polynomial_per_aspect_y'] is not None
    assert r['area_to_alpha_integral_factor'] is None
    assert r['area_to_rgb_integral_factors']==[None]*3


def test_dynamic_opacity_is_not_assumed_constant_in_area_response():
    r=response('rad=.2+bass*.1;a=bass;')
    assert r['source_model']=='affine_audio_radius'
    assert r['area_to_alpha_integral_factor'] is None


def test_constant_radius_has_no_claimed_audio_sensitivity():
    r=response('rad=.2;')
    assert r['source_model']=='constant_radius'
    assert r['input_codes']==[]
    assert r['radius_gains']==[]
    assert r['nominal_area_polynomial_per_aspect_y']['constant']==pytest.approx(.02)


def test_overflowing_polynomial_coefficient_retains_unknown():
    r=response('rad=1e200*bass;')
    assert r['source_model']=='unknown'
    assert r['nominal_area_polynomial_per_aspect_y'] is None


def test_derivative_overflow_is_not_exported_as_infinity():
    r=response('rad=1.3e154*bass;sides=100;')
    assert r['source_model']=='unknown'
    assert r['area_derivative_linear_matrix_per_aspect_y'] is None


def test_constant_radius_outside_float32_domain_remains_unknown():
    r=response('rad=1e50;')
    assert r['source_model']=='unknown'


def test_unregistered_eel_volume_name_is_not_a_new_band_input():
    r=response('rad=vol;')
    assert r['source_model']=='unknown'


def test_known_eel_small_denominator_guard_removes_audio_radius():
    d=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\n'
                      'shape_0_per_frame1=rad=bass/.000001;\n'))
    assert not any(e['id']=='shape_0' for e in d['elements'])


def test_known_eel_regular_division_has_a_nominal_audio_coefficient():
    r=response('rad=bass/.1;')
    assert r['source_model']=='affine_audio_radius'
    assert r['radius_gains']==pytest.approx([10])
