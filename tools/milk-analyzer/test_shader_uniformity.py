"""Prove lane independence without computing shader values or texture samples."""
import importlib.util
import numpy as np
import pytest
from shader_fields import Field,LoopPlan


def proof(field,inputs,shape=(4,4)):
    assert importlib.util.find_spec('shader_uniformity'), 'uniformity proof missing'
    from shader_uniformity import UniformityProof
    return UniformityProof(inputs,shape).is_uniform(field)


def var(name,dtype='float'):return Field('input',dtype=dtype,detail={'name':name})


def test_uniform_constants_time_audio_and_shared_expression_are_proven():
    time=var('time');bass=var('bass')
    expr=Field('multiply',(Field('sin',(time,)),bass))
    assert proof(expr,{'time':.3,'bass':1.1})
    assert proof(Field('add',(expr,expr)),{'time':.3,'bass':1.1})


def test_grid_data_is_not_uniform_even_if_values_happen_to_match():
    assert not proof(var('x'),{'x':np.ones((4,4),np.float32)})
    assert not proof(var('x','float2'),{'x':np.zeros((4,4,2),np.float32)})


def test_component_axes_are_distinct_from_same_size_lane_axes():
    assert proof(var('a','float4'),{'a':[1,2,3,4]},shape=(4,))
    assert not proof(var('a'),{'a':[1,2,3,4]},shape=(4,))


@pytest.mark.parametrize('kind',['sample','loop_slot','loop_result','sequence','array_write','write_member','unknown','uninitialized'])
def test_state_texture_effect_and_unknown_nodes_never_get_uniform_credit(kind):
    field=Field(kind,(Field('constant',detail={'value':1}),),detail={'reason':'unmodeled'})
    assert not proof(field,{})


def test_missing_input_is_not_invented_but_declared_default_can_be_proven():
    assert not proof(var('missing'),{})
    assert proof(Field('input',detail={'name':'unused','unbound_default':.25}),{})


def test_proof_budget_fails_closed_and_does_not_keep_input_arrays():
    from shader_uniformity import UniformityProof
    node=var('a')
    for _ in range(12):node=Field('add',(node,node))
    bounded=UniformityProof({'a':1},(4,4),max_nodes=3)
    assert not bounded.is_uniform(node) and bounded.budget_exceeded
    bounded.release()
    assert bounded.inputs is None and not bounded.cache
