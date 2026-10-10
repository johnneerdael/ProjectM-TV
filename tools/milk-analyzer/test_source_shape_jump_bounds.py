"""Shape jump ceilings depend on opacity, geometry and blend mode, not frames."""
import pytest
from test_source_shape_activity import activity
from source_material_temporal import PERIOD


def bounds(body,configuration=''):
    r=activity(body,configuration)
    return next(x for x in r['material_jump_bounds'] if x['part']=='fill')


def test_colour_wrap_jump_is_weighted_by_alpha():
    r=bounds('r=1+.1*sin(time);r2=r;g=0;g2=0;b=0;b2=0;a=.5;a2=.5;additive=1;')
    assert r['maximum_incoming_rgb_difference'][0]==pytest.approx(.5*PERIOD,rel=1e-6)
    assert r['maximum_incoming_rgb_difference'][1:]==[0,0]
    assert r['maximum_blended_rgb_difference']==r['maximum_incoming_rgb_difference']


def test_transparent_centre_colour_jump_is_tightened_by_barycentric_alpha():
    r=bounds('r=1+.1*sin(time);r2=.2;g=0;g2=0;b=0;b2=0;a=0;a2=.5;additive=1;')
    assert r['maximum_incoming_rgb_difference'][0]==pytest.approx(PERIOD/8,rel=1e-6)


def test_alpha_wrap_over_destination_uses_colour_contrast():
    r=bounds('r=.5;r2=.5;g=.5;g2=.5;b=.5;b2=.5;a=1+.1*sin(time);a2=a;additive=0;')
    assert r['maximum_blended_rgb_difference']==pytest.approx([.5]*3,rel=1e-6)
    assert r['destination_rgb_domain']==[0,1]


def test_nominal_area_weights_local_jump_and_counts_instances():
    r=bounds('r=1+.1*sin(time);r2=r;g=0;g2=0;b=0;b2=0;a=.5;a2=.5;rad=.2;sides=4;additive=1;',
        'shapecode_0_num_inst=3\n')
    assert r['nominal_fill_area_fraction_per_aspect_y_upper_bound']==pytest.approx(.02,rel=1e-6)
    assert r['summed_nominal_rgb_difference_integral_per_aspect_y'][0]==pytest.approx(.03*PERIOD,rel=1e-6)
    assert r['visible_flash_strength'] is None


def test_texture_inputs_keep_untextured_jump_bound_unknown():
    r=bounds('r=1+.1*sin(time);a=.5;a2=.5;textured=1;')
    assert r['maximum_blended_rgb_difference']==[None]*3


def test_static_gradient_has_zero_fixed_barycentric_material_difference():
    r=bounds('r=.2;r2=.8;g=.5;g2=.5;b=.4;b2=.4;a=.3;a2=.7;additive=0;')
    assert r['maximum_incoming_rgb_difference']==[0,0,0]
    assert r['maximum_blended_rgb_difference']==[0,0,0]


def test_unknown_alpha_does_not_gain_an_invented_jump_ceiling():
    r=bounds('r=1+.1*sin(time);a=bass;a2=a;')
    assert r['maximum_blended_rgb_difference']==[None]*3


def test_independent_fan_colour_pairs_respect_the_ceiling():
    r=bounds('r=1+.1*sin(time);r2=.4;a=.2;a2=.6;additive=0;')
    ceiling=r['maximum_blended_rgb_difference'][0]
    assert ceiling is not None
    for weight in (0,.1,.3,.5,.8,1):
        alpha=weight*.2+(1-weight)*.6
        before=weight*(PERIOD-1e-5)+(1-weight)*.4
        after=(1-weight)*.4
        assert alpha*abs(after-before)<=ceiling+1e-12


def test_border_draw_gate_includes_the_off_state_in_alpha_difference():
    r=activity('border_r=1;border_g=0;border_b=0;border_a=.0001+.00002*sin(time);additive=0;')
    b=next(x for x in r['material_jump_bounds'] if x['part']=='border')
    assert b['maximum_blended_rgb_difference'][0]>=.0001
    assert b['nominal_fill_area_fraction_per_aspect_y_upper_bound'] is None
