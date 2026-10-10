"""Nominal normalization seam size, not native event or visible flash evidence."""
import pytest
from test_source_wave_material import material


def gate(body,config=''):
    m=material(body,config)
    assert 'normalization_boundary_difference' in m,'wave normalization difference model missing'
    return m['normalization_boundary_difference']


def test_smooth_dim_red_gate_has_large_nominal_rgb_jump_weighted_by_alpha():
    r=gate('wave_r=.01+.005*sin(time);wave_g=0;wave_b=0;wave_brighten=1;wave_a=.4;')
    assert r['maximum_nominal_rgb_boundary_difference']==pytest.approx([.99,0,0],abs=1e-7)
    assert r['maximum_fixed_alpha_blended_rgb_boundary_difference']==pytest.approx([.396,0,0],abs=1e-7)
    assert r['visible_flash_strength'] is None
    assert r['nominal_crossing_event_rate_hz'] is None


def test_no_threshold_crossing_does_not_get_boundary_difference_record():
    assert gate('wave_r=.5+.1*sin(time);wave_brighten=1;')['possible_source_boundary_crossing'] is False


def test_unknown_brighten_flag_keeps_boundary_size_unknown():
    r=gate('wave_r=.01+.005*sin(time);wave_brighten=above(bass,1);')
    assert r['maximum_nominal_rgb_boundary_difference']==[None]*3


def test_unknown_alpha_keeps_unweighted_seam_but_no_blend_strength():
    r=gate('wave_r=.01+.005*sin(time);wave_g=0;wave_b=0;wave_brighten=1;wave_a=bass;')
    assert r['maximum_nominal_rgb_boundary_difference'][0]>0
    assert r['maximum_fixed_alpha_blended_rgb_boundary_difference']==[None]*3


def test_volume_modulation_remains_unknown_without_native_volume_domain():
    r=gate('wave_r=.01+.005*sin(time);wave_brighten=1;wave_a=.4;','bModWaveAlphaByVolume=1\n')
    assert r['maximum_fixed_alpha_blended_rgb_boundary_difference']==[None]*3


def test_activity_exports_wave_gate_with_local_size_and_unverified_visibility():
    from test_effect_families import read
    from test_source_appearance import appearance
    d=appearance(read('fWaveAlpha=.4\nnWaveMode=0\nper_frame_1=wave_r=.01+.005*sin(time);wave_g=0;wave_b=0;wave_brighten=1;\n'))
    hazards=d['activity']['flashing']['hazards']
    h=next((h for h in hazards if h['kind']=='builtin_wave_normalization_gate'),None)
    assert h is not None,'wave normalization risk omitted from activity hazards'
    assert h['maximum_nominal_rgb_boundary_difference']==pytest.approx([.99,0,0],abs=1e-7)
    assert h['visible_flashing_verified'] is False


def test_fixed_alpha_bound_exceeds_independently_computed_limiting_pairs():
    r=gate('wave_r=.01+.005*sin(time);wave_g=.004;wave_b=.002;wave_brighten=1;wave_a=.4;')
    t=r['normalization_threshold']
    for c,ceiling in zip((t,.004,.002),r['maximum_fixed_alpha_blended_rgb_boundary_difference']):
        assert .4*abs(c/t-c)<=ceiling+1e-12
