"""Two-state sampled-colour moduli preserve domains, not infinite slopes at zero."""
import math
from types import SimpleNamespace
import pytest
from shader_fields import Field


def const(x):return Field('constant',dtype='float',detail={'value':x})
def var(n):return Field('input',dtype='float',detail={'name':n})
def op(n,*args):return Field(n,tuple(args),'float')


def scalar(field,delta,domains=None):
    from source_colour_modulus import scalar_difference_modulus,evaluate_colour_modulus
    r=scalar_difference_modulus(field,input_domains=domains or {'x':[0,1]},varying_inputs={'x'})
    return r,evaluate_colour_modulus(r,delta)


def test_square_root_has_holder_modulus_at_zero_not_a_finite_lipschitz_gain():
    r,d=scalar(op('pow',var('x'),const(.5)),.0001)
    assert r['status']=='bounded'
    assert d==pytest.approx(.01)
    assert r['lipschitz_gain_upper'] is None
    assert r['native_numeric_certified'] is False
    assert r['terms'][0]['exponent']==.5


def test_power_above_one_uses_bounded_domain_derivative():
    r,d=scalar(op('pow',var('x'),const(2)),.01)
    assert d==pytest.approx(.02)
    assert r['lipschitz_gain_upper']==pytest.approx(2)


def test_abs_clamp_and_soft_sample_mask_have_finite_difference_modulus():
    x=var('x');field=op('multiply',op('saturate',op('multiply',x,const(2))),op('abs',op('subtract',x,const(.5))))
    r,d=scalar(field,.01)
    assert r['status']=='bounded'
    # Product rule for two states: |a|<=1, |b|<=.5, da<=2δ, db<=δ.
    assert d==pytest.approx(.02)


def test_fractional_power_negative_base_is_not_reinterpreted_as_absolute_value():
    r,d=scalar(op('pow',op('subtract',var('x'),const(2)),const(.5)),.1)
    assert r['status']=='unknown' and d is None


@pytest.mark.parametrize('field',[
    op('pow',var('x'),const(-1)),
    op('pow',var('x'),var('p')),
    op('divide',var('x'),op('subtract',var('x'),const(.5))),
    op('multiply',const(0),op('divide',const(1),const(0))),
    Field('cast',(var('x'),),'float',{'target_type':'int'}),
    Field('narrow',(var('x'),),'float',{'numeric_domain':'shader-float32'}),
    op('frac',var('x')),
])
def test_unsupported_domain_cast_seam_or_exponent_remains_unknown(field):
    r,d=scalar(field,.1,{'x':[0,1],'p':[.5,2]})
    assert r['status']=='unknown' and d is None
    assert r['unknown_reasons']


def test_held_bounded_mask_gain_is_not_an_invented_mask_trajectory():
    r,d=scalar(op('multiply',var('x'),var('mask')),.01,{'x':[0,1],'mask':[0,.2]})
    assert d==pytest.approx(.002)
    assert r['held_fixed_input_names']==['mask']


def test_unbounded_held_mask_cannot_have_a_finite_gain():
    r,d=scalar(op('multiply',var('x'),var('mask')),.01)
    assert r['status']=='unknown' and d is None


def test_native_legacy_gamma_is_not_interpreted_as_authored_power():
    from source_colour_modulus import sampled_colour_difference_modulus
    a=SimpleNamespace(stages={'composite':{'kind':'legacy_composite'}},outputs={},source={})
    r=sampled_colour_difference_modulus(a)
    assert r['status']=='unknown'
    assert any('authored' in s for s in r['unknown_reasons'])


def source_case(code):
    from test_effect_families import shader
    from effect_families import _Analysis,_CACHE
    a=_Analysis(shader(code),'gles300',None);a.input_scenario=None
    token=_CACHE.set({})
    try:
        a.main_equations();a.primitives();a.shader('composite','comp_')
    finally:_CACHE.reset(token)
    # These controls test a declared selected authored branch. No native-driver
    # acceptance or execution follows from that declaration.
    a.stages['composite']={**a.stages['composite'],'kind':'custom_composite'}
    return a


def test_sampled_shader_root_modulus_uses_actual_typed_abs_domain_lowering():
    from source_colour_modulus import sampled_colour_difference_modulus,evaluate_colour_modulus
    a=source_case('shader_body {ret=pow(-GetPixel(uv),.5);}')
    r=sampled_colour_difference_modulus(a)
    assert r['status']=='bounded'
    assert evaluate_colour_modulus(r,.0001)==pytest.approx(.01)
    assert r['sampling_coordinate_response_included'] is False


def test_history_driven_lookup_coordinates_block_colour_only_modulus():
    from source_colour_modulus import sampled_colour_difference_modulus,evaluate_colour_modulus
    a=source_case('shader_body {ret=pow(GetPixel(uv+GetPixel(uv).xy*.1),.5);}')
    r=sampled_colour_difference_modulus(a)
    assert r['status']=='unknown' and evaluate_colour_modulus(r,.001) is None
    assert any('coordinate' in s for s in r['unknown_reasons'])


def test_bad_coordinate_and_unqualified_native_shader_selection_remain_unknown():
    from source_colour_modulus import sampled_colour_difference_modulus
    a=source_case('shader_body {ret=pow(GetPixel(uv/0),.5);}')
    assert sampled_colour_difference_modulus(a)['status']=='unknown'
    a=source_case('shader_body {ret=pow(GetPixel(uv),.5);}')
    a.stages['composite']['kind']='unknown'
    assert sampled_colour_difference_modulus(a)['status']=='unknown'


def test_actual_cool_blue_toast_colour_modulus_is_finite_before_any_frames():
    from test_effect_families import read
    from effect_families import _Analysis,_CACHE
    from source_colour_modulus import sampled_colour_difference_modulus,evaluate_colour_modulus
    from pathlib import Path
    p=Path(__file__).parents[2]/'core/src/main/assets/presets/cool blue toast.milk'
    a=_Analysis(read(p.read_bytes()),'gles300',None);a.input_scenario=None;token=_CACHE.set({})
    try:a.main_equations();a.primitives();a.shader('composite','comp_')
    finally:_CACHE.reset(token)
    a.stages['composite']={**a.stages['composite'],'kind':'custom_composite'}
    r=sampled_colour_difference_modulus(a)
    assert r['status']=='bounded'
    assert evaluate_colour_modulus(r,1e-6)<.01
    assert any(t['exponent']==.5 for c in r['channels'] for t in c['terms'])
    assert r['input_change_metric']=='maximum_declared_sample_RGBA_lane_change'


def test_independent_sample_lanes_do_not_cancel_like_a_common_diagonal_derivative():
    from source_colour_modulus import scalar_difference_modulus,evaluate_colour_modulus
    r=scalar_difference_modulus(op('subtract',var('x'),var('y')),input_domains={'x':[0,1],'y':[0,1]},varying_inputs={'x','y'})
    assert evaluate_colour_modulus(r,.01)==pytest.approx(.02)


def test_nested_holder_powers_keep_a_finite_modulus():
    r,d=scalar(op('pow',op('pow',var('x'),const(.5)),const(.5)),1e-8)
    assert d==pytest.approx(.01)
    assert r['terms'][0]['exponent']==.25


def test_native_exponent_underflow_and_intermediate_overflow_do_not_gain_certificates():
    p=Field('constant',dtype='float',detail={'value':1e-300,'native_value':0.,'renderer_literal':None})
    r,d=scalar(op('pow',var('x'),p),.01)
    assert r['status']=='unknown' and d is None
    from source_colour_modulus import sampled_colour_difference_modulus
    a=source_case('shader_body {ret=saturate(GetPixel(uv)*1e30*1e30);}')
    r=sampled_colour_difference_modulus(a)
    assert r['status']!='bounded'


def test_active_hard_sample_mask_seam_is_not_a_soft_modulus():
    condition=Field('greater',(var('x'),const(.5)),'bool')
    r,d=scalar(op('select',condition,const(1),const(0)),.01)
    assert r['status']=='unknown' and d is None


def test_norm_and_square_root_modulus_supports_zero_vector():
    vector=Field('components',(var('x'),var('x')),'float2')
    r,d=scalar(op('sqrt',op('length',vector)),.0001)
    assert r['status']=='bounded'
    assert d>=math.sqrt(math.sqrt(2)*.0001)
    assert d<.02


def test_actual_packed_sample_predicate_cannot_publish_a_zero_modulus():
    from source_colour_modulus import sampled_colour_difference_modulus,evaluate_colour_modulus
    a=source_case('shader_body {ret=GetPixel(uv).r>.5?float3(1,1,1):float3(0,0,0);}')
    r=sampled_colour_difference_modulus(a)
    assert r['status']!='bounded'
    assert evaluate_colour_modulus(r,1e-5) is None
    assert any('predicate seam' in reason for reason in r['unknown_reasons'])
