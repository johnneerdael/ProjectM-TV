"""Conditional value ranges do not provide unknown input timing."""
import pytest
from test_effect_families import read
from test_source_appearance import appearance
from shader_fields import Field


def shape(body):
    d=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\nshape_0_per_frame1='+body+'\n'))
    return next(e for e in d['elements'] if e['id']=='shape_0')


def channel(expression):return shape('r='+expression+';')['material_temporal']['channels']['r']


def test_audio_sine_has_bounded_value_but_unknown_time_rate():
    c=channel('.5+.2*sin(bass)')
    assert c['raw_time_curve']['curve_kind']=='unknown'
    assert c['raw_time_curve']['maximum_absolute_control_rate_per_second'] is None
    assert c['raw_time_curve']['nominal_continuity']=='unknown'
    assert c['raw_time_curve']['nominal_value_range']==pytest.approx([.3,.7])
    assert c['possible_native_wrap_jump'] is False
    assert c['raw_time_curve']['value_envelope']['assumed_finite_input_names']==['bass']


def test_state_sine_bounds_preserve_named_finite_input_premise():
    c=channel('.1+.5*sin(k+bass*.03)')
    assert c['raw_time_curve']['nominal_value_range']==pytest.approx([-.4,.6])
    assert set(c['raw_time_curve']['value_envelope']['assumed_finite_input_names'])=={'bass','k'}
    assert c['possible_native_wrap_jump'] is True
    assert c['raw_time_curve']['period_seconds'] is None


def test_nested_min_max_can_bound_an_unbounded_input_without_audio_domain_guess():
    c=channel('min(max(bass,0),1)')
    assert c['raw_time_curve']['nominal_value_range']==pytest.approx([0,1])
    assert c['raw_time_curve']['maximum_absolute_control_rate_per_second'] is None
    assert c['possible_native_wrap_jump'] is False


def test_direct_band_input_has_no_invented_range():
    c=channel('bass')
    assert c['raw_time_curve']['nominal_value_range'] is None
    assert c['possible_native_wrap_jump'] is None


def test_conditional_branch_union_has_bounded_values_without_continuity():
    c=channel('if(above(bass,1),.2,.8)')
    assert c['raw_time_curve']['nominal_value_range']==pytest.approx([.2,.8])
    assert c['raw_time_curve']['maximum_absolute_control_rate_per_second'] is None
    assert c['raw_time_curve']['nominal_continuity']=='unknown'


def test_bounded_sine_of_square_has_no_false_rate():
    c=channel('.5+.2*sin(sqr(bass))')
    assert c['raw_time_curve']['nominal_value_range']==pytest.approx([.3,.7])
    assert c['raw_time_curve']['maximum_absolute_control_rate_per_second'] is None


def test_singular_or_unknown_effects_are_not_hidden_by_sine_range():
    from source_control_bounds import scalar_value_envelope
    cases=[Field('sin',(Field('unknown',detail={'reason':'unmodeled effect'}),)),
           Field('sin',(Field('divide',(Field('constant',detail={'value':1}),Field('input',detail={'name':'bass'}))),))]
    for field in cases:
        result=scalar_value_envelope(field)
        assert result['nominal_value_range'] is None
        assert result['unknown_reasons']


def test_sine_of_bounded_division_uses_proved_denominator_separation():
    c=channel('.5+.2*sin(bass/(2+sin(mid)))')
    assert c['raw_time_curve']['nominal_value_range']==pytest.approx([.3,.7])
    assert c['raw_time_curve']['maximum_absolute_control_rate_per_second'] is None


def test_zero_times_unbounded_finite_input_does_not_emit_nan_interval():
    from source_control_bounds import scalar_value_envelope
    field=Field('multiply',(Field('constant',detail={'value':0}),Field('input',detail={'name':'bass'})))
    result=scalar_value_envelope(field)
    assert result['nominal_value_range']==pytest.approx([0,0])


def test_finite_input_assumption_is_not_a_zero_initialization_or_render_certificate():
    c=channel('.5+.2*cos(k)')
    envelope=c['raw_time_curve']['value_envelope']
    assert envelope['uses_equation_execution'] is False
    assert envelope['uses_rendered_images'] is False
    assert envelope['native_numeric_certified'] is False
    assert envelope['nominal_value_range']==pytest.approx([.3,.7])


def test_known_overflow_inside_bounded_trig_is_not_hidden():
    from source_control_bounds import scalar_value_envelope
    large=Field('constant',detail={'value':1e308})
    field=Field('sin',(Field('multiply',(large,large)),))
    result=scalar_value_envelope(field)
    assert result['nominal_value_range'] is None
    assert result['unknown_reasons']


def test_uninitialized_input_and_random_calls_remain_opaque():
    from source_control_bounds import scalar_value_envelope
    for child in [Field('uninitialized',detail={'name':'mus'}),Field('rand',(Field('constant',detail={'value':10}),))]:
        result=scalar_value_envelope(Field('sin',(child,)))
        assert result['nominal_value_range'] is None


def test_value_bounds_do_not_mark_conditional_colour_changes_smooth():
    c=channel('if(equal(bass,1),.2,.8)')
    assert c['raw_time_curve']['nominal_value_range']==pytest.approx([.2,.8])
    assert c['raw_time_curve']['nominal_continuity']=='unknown'
    assert c['raw_time_curve']['maximum_absolute_control_rate_per_second'] is None
