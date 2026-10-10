"""Source material transfer rates are scoped to fixed geometry/destination."""
import pytest
from test_effect_families import read
from test_source_appearance import appearance


def activity(body,configuration=''):
    source=read('fWaveAlpha=0\nshapecode_0_enabled=1\n'+configuration+
                'shape_0_per_frame1='+body+'\n')
    return appearance(source)['activity']['flashing']


def fill(body,configuration=''):
    r=activity(body,configuration)
    return next(x for x in r['material_change_bounds'] if x['element_id']=='shape_0' and x['part']=='fill')


def test_slow_colour_rate_is_weighted_by_fan_alpha():
    r=fill('r=.5+.2*sin(.1*time);r2=r;g=0;g2=0;b=0;b2=0;a=.5;a2=.5;additive=1;')
    assert r['maximum_incoming_rgb_rate_per_second'][0]==pytest.approx(.01,abs=1e-7)
    assert r['maximum_incoming_rgb_rate_per_second'][1:]==[0,0]
    assert r['maximum_blended_rgb_rate_per_second']==r['maximum_incoming_rgb_rate_per_second']


def test_alpha_rate_affects_incoming_and_over_destination_terms():
    r=fill('r=.5;r2=.5;g=0;g2=0;b=0;b2=0;a=.5+.1*sin(2*time);a2=a;additive=0;')
    assert r['maximum_incoming_rgb_rate_per_second'][0]==pytest.approx(.1,abs=1e-7)
    assert r['maximum_blended_rgb_rate_per_second'][0]==pytest.approx(.3,abs=1e-7)
    assert r['destination_rgb_domain']==[0,1]


def test_transparent_centre_colour_still_contributes_through_interpolation():
    r=fill('r=.5+.2*sin(time);r2=.5;a=0;a2=.5;additive=1;')
    assert r['maximum_incoming_rgb_rate_per_second'][0]>=.1


def test_texture_content_prevents_untextured_blend_rate_claim():
    r=fill('r=.5+.2*sin(time);a=.5;a2=.5;textured=1;')
    assert r['maximum_incoming_rgb_rate_per_second']==[None,None,None]
    assert r['unknown_reasons']


def test_modulo_crossing_blocks_smooth_rate_and_has_local_jump_hazard():
    r=activity('r=1+.1*sin(time);a=.5;a2=.5;border_a=0;')
    f=next(x for x in r['material_change_bounds'] if x['part']=='fill')
    assert f['maximum_incoming_rgb_rate_per_second'][0] is None
    h=next(x for x in r['hazards'] if x['kind']=='shape_channel_modulo_crossing')
    assert h['element_id']=='shape_0' and 'r' in h['channels']
    assert h['visible_flashing_verified'] is False
    assert h['event_rate_hz'] is None


def test_fully_transparent_fill_has_no_colour_jump_hazard():
    r=activity('r=1+.1*sin(time);a=0;a2=0;border_a=0;')
    assert not r['hazards']


def test_border_gate_crossing_is_separate_from_colour_wrap():
    r=activity('border_a=.0001+.00002*sin(time);')
    assert any(h['kind']=='shape_border_draw_gate' for h in r['hazards'])


def test_material_rate_bounds_analytic_gradient_blend_derivative():
    import math
    r=fill('r=.4+.2*sin(3*time);r2=.3+.1*cos(2*time);a=.5+.1*sin(time);a2=.4+.1*cos(time);additive=0;')
    for step in range(65):
        t=step/8
        for fraction in (0,.1,.5,.9,1):
            c=fraction*(.4+.2*math.sin(3*t))+(1-fraction)*(.3+.1*math.cos(2*t))
            dc=fraction*.6*math.cos(3*t)-(1-fraction)*.2*math.sin(2*t)
            a=fraction*(.5+.1*math.sin(t))+(1-fraction)*(.4+.1*math.cos(t))
            da=fraction*.1*math.cos(t)-(1-fraction)*.1*math.sin(t)
            assert abs(a*dc+da*c)<=r['maximum_incoming_rgb_rate_per_second'][0]
            for destination in (0,.5,1):
                assert abs(a*dc+da*(c-destination))<=r['maximum_blended_rgb_rate_per_second'][0]


def test_overflowing_rate_ceiling_remains_unknown():
    from source_shape_activity import _sum_products
    assert _sum_products(1e308,1e308,0,0) is None
