"""Source radial sampling formula and derivative envelopes, without images."""
import math
import pytest
from test_effect_families import read
from test_source_appearance import appearance


def radial(body, pixel=''):
    d=appearance(read('fWaveAlpha=0\nper_frame_1=warp=0;'+body+'\n'+pixel))
    assert 'native_radial_zoom' in d,'radial zoom descriptor missing'
    return d['native_radial_zoom']


def test_constant_neutral_exponent_preserves_uniform_zoom():
    r=radial('zoom=1.1;zoomexp=1;')
    assert r['status']=='bounded_radial_zoom_component'
    assert r['zoom_factor_range']==pytest.approx([1.1,1.1],abs=2e-7)
    assert r['log_zoom_radial_derivative_range']==[0,0]
    assert r['radial_derivative_positive_sufficient'] is True
    assert r['visible_effect_family'] is None


def test_nonuniform_radial_zoom_bounds_independent_formula_samples():
    r=radial('zoom=1.1;zoomexp=2;')
    z=r['native_zoom_domain'][0];e=r['native_zoomexp_domain'][0]
    for radius in (0,.2,.5,1,math.sqrt(2)):
        factor=z**(e**(2*radius-1))
        derivative=2*math.log(e)*math.log(z)*e**(2*radius-1)
        assert r['zoom_factor_range'][0]<=factor<=r['zoom_factor_range'][1]
        assert r['log_zoom_radial_derivative_range'][0]<=derivative<=r['log_zoom_radial_derivative_range'][1]
    assert r['radial_derivative_positive_sufficient'] is True


def test_large_radial_expansion_can_fail_sufficient_no_fold_condition():
    r=radial('zoom=2;zoomexp=4;')
    assert r['status']=='bounded_radial_zoom_component'
    assert r['radial_derivative_positive_sufficient'] is False
    assert r['actual_fold_present'] is None


def test_opposite_log_signs_have_positive_radial_derivative():
    r=radial('zoom=.8;zoomexp=2;')
    assert r['radial_derivative_positive_sufficient'] is True
    assert r['log_zoom_radial_derivative_range'][1]<0


def test_bounded_audio_domains_do_not_gain_temporal_smoothness():
    r=radial('zoom=1.1+.01*sin(bass);zoomexp=2+.1*cos(mid);')
    assert r['status']=='bounded_radial_zoom_component'
    assert r['nominal_continuity']=='unknown'
    assert set(r['assumed_finite_input_names'])=={'bass','mid'}


@pytest.mark.parametrize('body',['zoom=-1;zoomexp=2;','zoom=0;zoomexp=1;',
 'zoom=1;zoomexp=0;','zoom=bass;zoomexp=2;','zoom=1e20;zoomexp=20;'])
def test_invalid_or_unbounded_power_domain_is_unknown(body):
    r=radial(body)
    assert r['status']=='unknown'
    assert r['zoom_factor_range'] is None
    assert r['unknown_reasons']


def test_native_inner_power_underflow_is_not_hidden_by_finite_outer_power():
    r=radial('zoom=1;zoomexp=1e-38;')
    assert r['status']=='unknown'
    assert r['unknown_reasons']


def test_radial_derivative_formula_matches_independent_finite_difference():
    r=radial('zoom=1.1;zoomexp=2;')
    z=r['native_zoom_domain'][0];e=r['native_zoomexp_domain'][0]
    for radius in (.2,.5,1):
        h=1e-5
        sampling=lambda t:t/(z**(e**(2*t-1)))
        difference=(sampling(radius+h)-sampling(radius-h))/(2*h)
        factor=z**(e**(2*radius-1))
        derivative=(1-radius*2*math.log(e)*math.log(z)*e**(2*radius-1))/factor
        assert derivative==pytest.approx(difference,rel=1e-8)


def test_spatial_zoom_control_does_not_use_uniform_radial_formula():
    r=radial('zoom=1.1;zoomexp=2;','per_pixel_1=zoom=1+.01*rad;\n')
    assert r['status']=='unknown'


def test_other_spatial_controls_do_not_hide_independent_radial_component():
    r=radial('zoom=1.1;zoomexp=2;','per_pixel_1=rot=.1*rad;\n')
    assert r['status']=='bounded_radial_zoom_component'
    assert r['complete_sampling_map_area_ratio'] is None
