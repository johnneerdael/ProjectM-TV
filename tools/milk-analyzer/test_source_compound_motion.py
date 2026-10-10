"""Analytic control bounds; no native frames or preset images."""
import math
import pytest
from test_effect_families import read
from test_source_appearance import appearance


def curve(expression,control='x'):
    d=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\nshape_0_per_frame1=x=.5;y=.5;rad=.1;ang=0;'+control+'='+expression+';\n'))
    shape=next(e for e in d['elements'] if e['id']=='shape_0')
    names={'x':'position_x','y':'position_y','rad':'radius','ang':'rotation'}
    return next(c for c in shape['motion_controls'] if c['control']==names[control])


def test_sum_of_oscillators_has_range_and_rate_upper_bounds():
    c=curve('.5+.1*sin(time)+.2*cos(2*time)')
    assert c['curve_kind']=='compound_time'
    assert c['nominal_value_range']==pytest.approx([.2,.8])
    assert c['maximum_absolute_control_rate_per_second']==pytest.approx(.5)
    assert c['rate_estimate_kind']=='upper_bound'
    assert c['nominal_value_range_kind']=='upper_bound'
    assert c['period_seconds'] is None


def test_nested_phase_modulation_uses_chain_rule_without_guessing_a_period():
    c=curve('.5+.1*sin(time+.2*sin(3*time))')
    assert c['curve_kind']=='compound_time'
    assert c['maximum_absolute_control_rate_per_second']==pytest.approx(.16)
    assert c['nominal_continuity']=='smooth_nominal'
    assert c['period_seconds'] is None


def test_oscillator_product_uses_both_product_rule_terms():
    c=curve('.5+.1*sin(time)*sin(2*time)')
    assert c['maximum_absolute_control_rate_per_second']==pytest.approx(.3)
    assert c['nominal_value_range']==pytest.approx([.4,.6])


def test_safe_varying_denominator_has_quotient_rule_bound():
    c=curve('1/(2+sin(time))')
    assert c['maximum_absolute_control_rate_per_second']==pytest.approx(1)
    assert c['nominal_value_range']==pytest.approx([1/3,1])


def test_absolute_value_preserves_cusp_information():
    c=curve('.5+.1*abs(sin(time))')
    assert c['maximum_absolute_control_rate_per_second']==pytest.approx(.1)
    assert c['nominal_value_range']==pytest.approx([.5,.6])
    assert c['nominal_continuity']=='piecewise_lipschitz'


def test_bounded_value_does_not_mean_bounded_rate_for_chirp():
    c=curve('.5+.1*sin(time*time)')
    assert c['curve_kind']=='unknown'
    assert c['maximum_absolute_control_rate_per_second'] is None
    assert c['nominal_value_range']==pytest.approx([.4,.6])


@pytest.mark.parametrize('expression',[
    '1/sin(time)',
    '.5+.1*sin(time)+bass',
    '.5+.1*sin(time)+k',
    'if(above(sin(time),0),.2,.8)',
    'rand(10)',
    '.5+sin(int(time))',
])
def test_missing_domains_steps_and_singularities_keep_rate_unknown(expression):
    c=curve(expression)
    assert c['maximum_absolute_control_rate_per_second'] is None
    assert c['curve_kind']=='unknown'


def test_known_single_oscillator_keeps_exact_estimate_kind():
    c=curve('.5+.2*sin(3*time)')
    assert c['curve_kind']=='sinusoidal_time'
    assert c['rate_estimate_kind']=='exact_nominal'
    assert c['nominal_value_range_kind']=='exact_nominal'


def test_compound_axes_supply_joint_speed_bound_without_inventing_circle():
    d=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\nshape_0_per_frame1=x=.5+.1*sin(time)+.2*cos(2*time);y=.5+.1*cos(time)+.2*sin(2*time);rad=.1;ang=0;\n'))
    s=next(e for e in d['elements'] if e['id']=='shape_0')
    t=s['center_trajectory']
    assert t['path_kind']=='independent_axis_curves'
    assert t['speed_estimate_kind']=='upper_bound'
    assert t['maximum_source_speed_units_per_second']==pytest.approx(math.hypot(.5,.5))
    assert s['vertex_motion']['maximum_vertex_speed_ndc_per_second_upper_bound']==pytest.approx(2*math.hypot(.5,.5))


def test_compound_rate_bound_does_not_mean_final_visible_speed():
    c=curve('.5+.1*sin(time)+.2*cos(2*time)')
    assert c['visible_motion_speed'] is None
    assert c['nominal_continuity']=='smooth_nominal'


def test_native_eel_guard_proves_zero_for_entire_denominator_envelope():
    c=curve('1/(.000009*sin(time))')
    assert c['maximum_absolute_control_rate_per_second']==0
    assert c['nominal_value_range']==[0,0]


def test_compound_rate_underflow_is_not_a_stationary_certificate():
    c=curve('sin(time*1e-200)*1e-200')
    assert c['maximum_absolute_control_rate_per_second'] is None
    assert c['unknown_reasons']


def test_cusp_information_survives_shape_and_instance_joins():
    d=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\nshapecode_0_num_inst=2\nshape_0_per_frame1=x=.5+.1*abs(sin(time+instance));y=.5;rad=.1;ang=0;\n'))
    s=next(e for e in d['elements'] if e['id']=='shape_0')
    assert s['center_trajectory']['nominal_continuity']=='unknown'
    assert s['vertex_motion']['nominal_continuity']=='unknown'
    assert s['instance_motion']['nominal_continuity']=='piecewise_lipschitz'
    assert all(r['nominal_continuity']=='piecewise_lipschitz' for r in s['instance_motion']['instances'])


def test_known_shape_join_preserves_cusp_classification():
    d=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\nshape_0_per_frame1=x=.5+.1*abs(sin(time));y=.5;rad=.1;ang=0;\n'))
    s=next(e for e in d['elements'] if e['id']=='shape_0')
    assert s['center_trajectory']['nominal_continuity']=='piecewise_lipschitz'
    assert s['vertex_motion']['nominal_continuity']=='piecewise_lipschitz'


def test_formerly_unsupported_sine_cosine_product_has_conservative_rate():
    c=curve('sin(time)*cos(time)')
    assert c['curve_kind']=='compound_time'
    assert c['maximum_absolute_control_rate_per_second']>=2
    assert c['maximum_absolute_control_rate_per_second']==pytest.approx(2)
    # Exact derivative is cos(2*t), whose true peak1 is within this loose bound.
    assert c['rate_estimate_kind']=='upper_bound'


def test_unknown_native_sides_do_not_claim_smooth_vertex_paths():
    d=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\nshape_0_per_frame1=x=.5;y=.5;rad=.1;ang=0;sides=3+bass;\n'))
    s=next(e for e in d['elements'] if e['id']=='shape_0')
    assert s['vertex_motion']['nominal_continuity']=='unknown'


@pytest.mark.parametrize('expression',[
    'sin(time*1e-200)/1e200',
    'sin(time*1e-200)/(1e200+sin(time))',
    'time*1e-200*1e-200',
])
def test_quotient_and_affine_rate_underflow_keep_nonzero_motion_unresolved(expression):
    c=curve(expression)
    assert c['maximum_absolute_control_rate_per_second'] is None


def test_rounded_singleton_envelope_does_not_prove_constant_trig():
    c=curve('sin(1+1e-20*sin(time))')
    assert c['curve_kind']=='compound_time'
    assert c['maximum_absolute_control_rate_per_second']>0
    assert c['maximum_absolute_control_rate_per_second']==pytest.approx(1e-20,rel=1e-10,abs=0)
