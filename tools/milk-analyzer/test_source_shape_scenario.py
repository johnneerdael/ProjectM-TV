"""Declared audio ranges supplement shape material bounds without inventing beats."""
import pytest
from test_effect_families import read,analyze


def scenario(body,bands=None):
    request={'schema_version':1,'name':'shape audio range control','audio_band_ranges':bands or {'bass':[0,2]}}
    r=analyze(read('fWaveAlpha=0\nshapecode_0_enabled=1\nshape_0_per_frame1='+body+'\n'),input_scenario=request)
    d=r['visual_description'];element=next(e for e in d['elements'] if e['id']=='shape_0')
    assert 'scenario_material_envelope' in element,'declared shape material envelope missing'
    return d,element


def test_audio_colour_range_adds_jump_ceiling_without_replacing_unknown_lifetime():
    d,e=scenario('r=.2*bass;r2=r;g=0;g2=0;b=0;b2=0;a=.5;a2=.5;additive=1;')
    assert e['material_temporal']['channels']['r']['native_float32_endpoint_domain'] is None
    s=e['scenario_material_envelope'];c=s['channels']['r']
    assert c['native_float32_endpoint_domain']==pytest.approx([0,.4],abs=1e-7)
    assert c['possible_native_wrap_jump'] is False
    rows=d['activity']['flashing']['scenario_material_jump_bounds']
    fill=next(r for r in rows if r['part']=='fill')
    assert fill['maximum_blended_rgb_difference'][0]==pytest.approx(.2,abs=1e-6)
    assert fill['visible_flash_strength'] is None
    assert fill['input_scenario_sha256']==s['input_scenario_sha256']


def test_large_audio_swing_keeps_possible_wrap_without_timing_claim():
    _,e=scenario('r=bass;')
    c=e['scenario_material_envelope']['channels']['r']
    assert c['possible_native_wrap_jump'] is True
    assert c['nominal_modulo_schedule']['nominal_crossing_event_rate_hz'] is None


def test_missing_band_and_persistent_state_do_not_become_declared_inputs():
    _,e=scenario('r=mid;g=k;')
    assert e['scenario_material_envelope']['channels']['r']['native_float32_endpoint_domain'] is None
    assert e['scenario_material_envelope']['channels']['g']['native_float32_endpoint_domain'] is None


def test_declared_zero_alpha_excludes_fill_consumption_only_conditionally():
    _,e=scenario('a=bass;a2=a;r=1+.1*sin(time);',{'bass':[0,0]})
    assert e['scenario_material_envelope']['channels']['r']['may_be_consumed'] is False
    assert e['material_temporal']['channels']['r']['may_be_consumed'] is True


def test_known_native_overflow_retains_unknown_domain():
    _,e=scenario('r=bass*1e40;')
    assert e['scenario_material_envelope']['channels']['r']['native_float32_endpoint_domain'] is None


def test_opacity_changes_bound_destination_contrast_for_declared_states():
    d,_=scenario('r=.25;r2=.25;g=.25;g2=.25;b=.25;b2=.25;a=.1+.2*bass;a2=a;additive=0;')
    row=next(r for r in d['activity']['flashing']['scenario_material_jump_bounds'] if r['part']=='fill')
    ceiling=row['maximum_blended_rgb_difference'][0]
    assert ceiling==pytest.approx(.3,abs=1e-6)
    for before in (0,.2,1,2):
        for after in (0,.5,1.5,2):
            for destination in (0,.4,1):
                difference=abs((.1+.2*after-(.1+.2*before))*(.25-destination))
                assert difference<=ceiling


def test_textured_shape_does_not_gain_untextured_colour_difference():
    d,_=scenario('r=.2*bass;a=.5;a2=.5;textured=1;')
    row=next(r for r in d['activity']['flashing']['scenario_material_jump_bounds'] if r['part']=='fill')
    assert row['maximum_blended_rgb_difference']==[None]*3


def test_no_declared_scenario_adds_no_conditional_fields():
    r=analyze(read('shapecode_0_enabled=1\nshape_0_per_frame1=r=.2*bass;\n'))
    assert all('scenario_material_envelope' not in e for e in r['visual_description']['elements'])
    assert 'scenario_material_jump_bounds' not in r['visual_description']['activity']['flashing']
