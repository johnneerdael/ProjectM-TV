"""Conditional fan contribution bounds are not measured brightness."""
import pytest
from test_effect_families import read
from test_source_appearance import appearance


def item(body,config=''):
    d=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\nshapecode_0_sides=4\n'
                     'shapecode_0_rad=.5\n'+config+'shape_0_per_frame1='+body+'\n'))
    s=next(e for e in d['elements'] if e['id']=='shape_0')
    assert 'fill_envelope' in s, 'conditional fill contribution envelope is missing'
    return s['fill_envelope']


def test_constant_fill_bounds_contain_exact_existing_integrals():
    f=item('r=.2;g=.4;b=.8;a=.25;r2=.8;g2=.6;b2=.2;a2=.75;')
    assert f['mean_alpha_bounds']==pytest.approx([7/12,7/12],abs=2e-7)
    assert f['nominal_area_fraction_per_aspect_y_bounds']==pytest.approx([.125,.125])
    for pair in f['mean_rgb_times_alpha_bounds']:
        assert pair is not None and pair[0]==pytest.approx(pair[1])
    assert f['visible_screen_contribution'] is None


def test_dynamic_untextured_alpha_has_area_weighted_bounds():
    f=item('a=.3+.1*sin(time);a2=.6+.1*cos(time);r=1;r2=1;g=0;g2=0;b=0;b2=0;')
    assert f['mean_alpha_bounds']==pytest.approx([.4,.6],abs=2e-6)
    assert f['nominal_alpha_area_fraction_per_aspect_y_bounds']==pytest.approx([.05,.075],abs=2e-6)


def test_dynamic_radius_uses_nominal_area_range_not_a_fixed_radius_default():
    f=item('rad=.2+.1*sin(time);a=1;a2=1;')
    assert f['nominal_area_fraction_per_aspect_y_bounds']==pytest.approx([.005,.045],abs=2e-6)
    assert f['nominal_alpha_area_fraction_per_aspect_y_bounds']==pytest.approx([.005,.045],abs=2e-6)


def test_negative_radius_range_uses_squared_geometry_and_zero_lower_when_crossed():
    f=item('rad=.2*sin(time);a=1;a2=1;')
    assert f['nominal_area_fraction_per_aspect_y_bounds']==pytest.approx([0,.02],abs=2e-6)


def test_colour_alpha_bounds_keep_cross_vertex_covariance_terms():
    f=item('r=.4+.1*sin(time);r2=.1+.1*cos(time);a=.3+.1*sin(time);a2=.6+.1*cos(time);')
    expected_low=((.2+.5)*.3+(.2+3*.5)*0)/6
    expected_high=((.4+.7)*.5+(.4+3*.7)*.2)/6
    assert f['mean_rgb_times_alpha_bounds'][0]==pytest.approx([expected_low,expected_high],abs=3e-6)


def test_native_wrap_full_envelope_and_alpha_clipping_do_not_invent_linear_mean():
    f=item('a=1+.1*sin(time);a2=1+.1*cos(time);r=1;r2=1;')
    assert f['mean_alpha_bounds']==[0,1]
    assert f['mean_rgb_times_alpha_bounds'][0][0]==0
    assert f['mean_rgb_times_alpha_bounds'][0][1]>=1-2e-6


def test_repeated_instances_are_summed_not_union_coverage():
    f=item('a=.3+.1*sin(time);a2=.6+.1*cos(time);',config='shapecode_0_num_inst=3\n')
    assert f['summed_nominal_alpha_area_fraction_per_aspect_y_bounds']==pytest.approx([.15,.225],abs=4e-6)
    assert f['overlap_aggregation']=='sum; repeated coverage counted multiple times'


def test_textured_material_stays_unresolved_without_texture_contract():
    f=item('a=.3+.1*sin(time);a2=1;',config='shapecode_0_textured=1\n')
    assert f['mean_alpha_bounds'] is None
    assert f['mean_rgb_times_alpha_bounds']==[None]*3


def test_unknown_one_rgb_channel_keeps_other_channel_bounds():
    f=item('r=bass;r2=1;g=.2;g2=.2;b=.4;b2=.4;a=.5;a2=.5;')
    assert f['mean_rgb_times_alpha_bounds'][0] is None
    assert f['mean_rgb_times_alpha_bounds'][1]==pytest.approx([.1,.1],abs=2e-7)
    assert f['mean_rgb_times_alpha_bounds'][2]==pytest.approx([.2,.2],abs=2e-7)


def test_unbounded_radius_keeps_material_bounds_without_area():
    f=item('rad=bass;a=.3+.1*sin(time);a2=.6+.1*cos(time);')
    assert f['mean_alpha_bounds'] is not None
    assert f['nominal_area_fraction_per_aspect_y_bounds'] is None
    assert f['nominal_alpha_area_fraction_per_aspect_y_bounds'] is None


def test_no_renderer_samples_or_visible_strength_are_claimed():
    f=item('a=.3+.1*sin(time);a2=.6+.1*cos(time);')
    assert f['uses_rendered_images'] is False
    assert f['uses_equation_execution'] is False
    assert f['visible_screen_contribution'] is None
