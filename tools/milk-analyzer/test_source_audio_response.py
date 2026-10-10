"""Nominal control sensitivity is separate from audio timing and screen impact."""
import pytest
from shader_fields import Field
from test_effect_families import read
from test_source_appearance import appearance


def route(expression,code=1):
    d=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\nshape_0_per_frame1=rad='+expression+';\n'))
    return next(r for e in d['elements'] if e['id']=='shape_0' for r in e['audio_routes']
                if r['control']=='radius' and r['input_code']==code)


def response(expression,code=1):
    r=route(expression,code)
    assert 'nominal_audio_response' in r
    return r['nominal_audio_response']


def test_sine_audio_phase_gets_chain_rule_bound_without_timing_or_visibility():
    r=response('.2*sin(3*bass)')
    assert r['maximum_absolute_control_change_per_audio_unit']==pytest.approx(.6)
    assert r['bound_kind']=='upper_bound'
    assert r['visible_response_strength'] is None
    assert r['maximum_time_rate'] is None


def test_cross_band_phase_holds_other_inputs_fixed():
    assert response('.2*sin(3*bass+2*mid+time)')['maximum_absolute_control_change_per_audio_unit']==pytest.approx(.6)
    r=response('.2*sin(3*bass+2*mid+time)',2)
    assert r['maximum_absolute_control_change_per_audio_unit']==pytest.approx(.4)
    assert 'bass' in r['held_fixed_input_names']


def test_min_max_clamp_preserves_piecewise_continuous_response():
    r=response('min(max(bass*.2,0),1)')
    assert r['maximum_absolute_control_change_per_audio_unit']==pytest.approx(.2)
    assert r['nominal_continuity']=='piecewise_lipschitz'


@pytest.mark.parametrize('expression',['if(above(bass,1),.2,.8)','1/bass','sin(bass*mid)','sin(int(bass))','rand(bass)'])
def test_threshold_singular_unbounded_product_and_discrete_operations_abstain(expression):
    assert response(expression)['maximum_absolute_control_change_per_audio_unit'] is None


def test_safe_bounded_denominator_has_quotient_bound():
    assert response('1/(2+sin(bass))')['maximum_absolute_control_change_per_audio_unit']==pytest.approx(1)


def test_abs_reports_a_continuous_cusp_not_a_flash():
    r=response('abs(sin(bass))')
    assert r['maximum_absolute_control_change_per_audio_unit']==pytest.approx(1)
    assert r['nominal_continuity']=='piecewise_lipschitz'


def test_response_helper_preserves_explicit_finite_domain_premises():
    from source_control_bounds import scalar_response_envelope
    bass=Field('input',detail={'name':'bass'});mid=Field('input',detail={'name':'mid'})
    r=scalar_response_envelope(Field('multiply',(bass,mid)),input_names={'bass'},input_domains={'mid':[0,2]})
    assert r['maximum_absolute_control_change_per_audio_unit']==pytest.approx(2)
    assert r['declared_input_domains']=={'mid':[0,2]}


def test_native_narrowing_does_not_receive_nominal_continuity_credit():
    from source_control_bounds import scalar_response_envelope
    field=Field('narrow',(Field('input',detail={'name':'bass'}),),'float',{'numeric_domain':'shader-float32'})
    r=scalar_response_envelope(field,input_names={'bass'})
    assert r['maximum_absolute_control_change_per_audio_unit'] is None
    assert r['unknown_reasons']


def test_response_underflow_is_not_stationarity():
    assert response('sin(bass*1e-200)*1e-200')['maximum_absolute_control_change_per_audio_unit'] is None


def test_shader_packed_bands_use_correct_scalar_input_identity():
    from test_effect_families import shader
    d=appearance(shader('shader_body {ret=float3(.2*sin(bass),.3*cos(mid),.4*sin(treb));}'))
    routes={r['input_code']:r for e in d['elements'] for r in e['audio_routes']}
    for code,gain in [(1,.2),(2,.3),(3,.4)]:
        r=routes[code]['nominal_audio_response']
        assert r['maximum_absolute_control_change_per_audio_unit']==pytest.approx(gain)
        assert '_c3.'+'xyz'[code-1] in r['varying_input_names']


def test_shader_q_upload_keeps_response_unresolved():
    d=appearance(read('PSVERSION_COMP=2\nper_frame_1=q1=sin(bass);\ncomp_1=`shader_body {ret=float3(q1,0,0);}\n'))
    r=next(r for e in d['elements'] for r in e['audio_routes'] if r['input_code']==1)
    assert r['nominal_audio_response']['maximum_absolute_control_change_per_audio_unit'] is None


def test_instantaneous_state_control_is_not_recurrent_total_derivative():
    r=response('.2*sin(bass+k)')
    assert r['maximum_absolute_control_change_per_audio_unit']==pytest.approx(.2)
    assert 'k' in r['held_fixed_input_names']


def test_unknown_declared_domain_and_float_upload_remain_unknown():
    from source_control_bounds import scalar_response_envelope
    for node in [Field('unknown'),Field('cast',(Field('input',detail={'name':'bass'}),),'float')]:
        assert scalar_response_envelope(node,input_names={'bass'})['maximum_absolute_control_change_per_audio_unit'] is None


def test_missing_packed_parent_identity_is_not_invented():
    from source_control_bounds import scalar_response_envelope
    node=Field('member',(Field('input',dtype='float4'),),'float',{'field':'x','swizzle':True})
    assert scalar_response_envelope(node,input_names={'.x'})['maximum_absolute_control_change_per_audio_unit'] is None
