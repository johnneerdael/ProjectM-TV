"""Pinned mult0 makes plain unknown storage irrelevant to literal-zero products."""
import numpy as np
import pytest
from test_helper_state import lower
from field_math import evaluate,UnresolvedMath
from grid_math import evaluate_grid


@pytest.mark.parametrize('prefix,expression',[
    ('float2 rs;','0*rs'),('float2 rs;','rs*0'),
    ('float2 rs;','0*rs.xy'),('float rs;','0*rs'),
])
@pytest.mark.historical_profile("legacy_pre30")
def test_literal_zero_product_has_defined_value_without_initializing_storage(prefix,expression):
    model,result=lower('ret=float3('+expression+(',0' if 'float2' in prefix else '')+');',prefix)
    assert model.complete,model.unknown
    np.testing.assert_array_equal(evaluate(result),[0,0,0])
    np.testing.assert_array_equal(evaluate_grid(result,batch_shape=(2,)),np.zeros((2,3)))


@pytest.mark.historical_profile("legacy_pre30")
def test_zero_product_does_not_initialize_the_storage_for_later_reads():
    model,result=lower('float2 a=0*rs;ret=float3(rs,0);','float2 rs;')
    assert not model.complete
    assert result.op=='unknown'


def test_literal_zero_masks_partly_written_constant_storage():
    model,result=lower('float2 v;v.x=1;ret=float3(0*v,0);','')
    assert model.complete,model.unknown
    np.testing.assert_array_equal(evaluate(result),[0,0,0])


def test_matrix_product_remains_separate_from_component_zero_guard():
    model,result=lower('ret=float3((0*m)[0],0);','float2x2 m;')
    assert not model.complete
    assert result.op=='unknown'


@pytest.mark.parametrize('body',[
    'float a[2];ret=float3(0*a[3]);',
    'ret=float3(0*bass);',
])
def test_zero_storage_rule_does_not_hide_bounds_or_missing_uniforms(body):
    model,result=lower(body,'')
    if model.complete:
        with pytest.raises(UnresolvedMath):evaluate(result)
    else:assert result.op=='unknown'


def test_zero_product_does_not_discard_shared_helper_updates():
    model,result=lower('float a=bump(2)*0;ret=float3(a,g,0);')
    assert model.complete,model.unknown
    np.testing.assert_array_equal(evaluate(result),[0,3,0])
