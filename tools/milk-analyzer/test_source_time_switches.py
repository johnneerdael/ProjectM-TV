"""Analytic threshold/floor events; frame sampling and visibility stay separate."""
import math
import pytest
from test_effect_families import read
from test_source_appearance import appearance


def curve(expr):
    d=appearance(read('fWaveAlpha=1\nper_frame_1=wave_r='+expr+';\n'))
    c=next(e for e in d['elements'] if e['id']=='builtin_wave')['wave_material']['channels']['wave_r']['raw_time_curve']
    assert 'time_switch_events' in c,'time switch events missing'
    return c


def test_sine_threshold_switch_has_period_duty_cycle_and_two_jumps():
    c=curve('if(above(sin(time*2),0),1,.1)');r=c['time_switch_events'][0]
    assert r['event_kind']=='periodic_threshold_crossing'
    assert r['period_seconds']==pytest.approx(math.pi)
    assert r['predicate_true_fraction']==pytest.approx(.5)
    assert r['events_per_period']==2
    assert r['nominal_event_rate_hz']==pytest.approx(2/math.pi)
    assert r['absolute_control_jump']==pytest.approx(.9)
    assert r['visible_flash_frequency_hz'] is None


def test_cosine_threshold_and_reversed_comparison_get_correct_duty():
    r=curve('if(below(.5,cos(time)),.8,.2)')['time_switch_events'][0]
    assert r['predicate_true_fraction']==pytest.approx(1/3)


def test_negative_amplitude_reverses_inequality_without_changing_frequency():
    r=curve('if(above(-2*sin(time)+1,2),.8,.2)')['time_switch_events'][0]
    assert r['predicate_true_fraction']==pytest.approx(1/3)


def test_signed_phase_rate_and_phase_offset_supply_event_offsets():
    r=curve('if(above(cos(-2*time+.4),0),1,0)')['time_switch_events'][0]
    expected=sorted([((math.pi/2-.4)/-2)%math.pi,((3*math.pi/2-.4)/-2)%math.pi])
    assert r['event_offsets_seconds_mod_period']==pytest.approx(expected)


@pytest.mark.parametrize('expr',['if(above(sin(time),2),1,0)','if(above(sin(time),1),1,0)',
 'if(above(sin(time),-1),1,0)','if(above(sin(bass),0),1,0)','if(above(sin(time*time),0),1,0)',
 'if(above(sin(time),0),.2,.2)'])
def test_unreachable_tangent_audio_nonlinear_or_equal_branches_do_not_get_crossing_schedule(expr):
    assert curve(expr)['time_switch_events']==[]


def test_floor_linear_time_has_step_interval_and_scaled_jump():
    r=curve('.1+.2*floor(time*3+.4)')['time_switch_events'][0]
    assert r['event_kind']=='affine_time_floor_steps'
    assert r['period_seconds']==pytest.approx(1/3)
    assert r['nominal_event_rate_hz']==3
    assert r['absolute_control_jump']==pytest.approx(.2)
    assert r['whole_control_levels_known'] is False


def test_nested_switch_keeps_site_frequency_but_not_whole_control_jump():
    r=curve('sin(if(above(cos(time),0),time,bass))')['time_switch_events'][0]
    assert r['absolute_control_jump'] is None
    assert r['scope']=='contributing source site; whole-control transfer unresolved'


def test_time_switches_do_not_claim_continuity_or_rendered_flashing():
    c=curve('if(above(sin(time),0),1,0)')
    assert c['nominal_continuity']=='unknown'
    assert c['time_switch_events'][0]['clock_kind']=='equation_time'


def test_eel_int_alias_is_floor_steps_but_shader_integer_cast_is_not():
    assert curve('int(-time*3+.4)')['time_switch_events'][0]['floor_operator_kind']=='EEL int/floor real floor'
    from shader_fields import Field
    from source_time_switches import time_switch_events
    time=Field('input',detail={'name':'time'})
    assert time_switch_events(Field('cast',(time,),'int',{'target_type':'int'}))==[]


def test_fractional_or_binary_cast_control_does_not_borrow_branch_jump():
    from shader_fields import Field
    from source_time_switches import time_switch_events
    from effect_families import _constant
    time=Field('input',detail={'name':'time'})
    predicate=Field('greater',(Field('sin',(time,)),_constant(0)))
    control=Field('cast',(Field('select',(predicate,_constant(.2),_constant(.3))),),'int',{'target_type':'int'})
    r=time_switch_events(control)[0]
    assert r['absolute_control_jump'] is None
    assert r['whole_control_levels_known'] is False


def test_extreme_but_finite_frequency_retains_nominal_sampling_caveat():
    r=curve('if(above(sin(time*1e308),0),1,0)')['time_switch_events'][0]
    assert math.isfinite(r['nominal_event_rate_hz'])
    assert r['visible_flash_frequency_hz'] is None


def test_integer_cast_cannot_borrow_scaled_floor_control_jump():
    from shader_fields import Field
    from source_time_switches import time_switch_events
    from effect_families import _constant
    time=Field('input',detail={'name':'time'})
    control=Field('cast',(Field('multiply',(_constant(.2),Field('floor',(time,)))),),'int',{'target_type':'int'})
    r=time_switch_events(control)[0]
    assert r['absolute_control_jump'] is None
