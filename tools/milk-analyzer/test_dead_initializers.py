import pytest
import numpy as np
from test_helper_state import lower
from field_math import evaluate


def test_unused_pure_initializer_does_not_make_output_depend_on_unwritten_global():
    model,result=lower('float unused=dot(back,float3(.32,.49,.29));ret=.4;','float3 back;')
    assert model.complete,model.unknown
    np.testing.assert_allclose(evaluate(result),[.4]*3)


@pytest.mark.historical_profile("legacy_pre30")
def test_live_initializer_and_helper_returns_remain_obligations():
    model,result=lower('float used=dot(back,float3(1));ret=used;','float3 back;')
    assert not model.complete
    model,result=lower('ret=f();','float3 back;float f(){float v=dot(back,float3(1));return v;}')
    assert not model.complete


def test_unused_initializer_does_not_discard_shared_helper_effects():
    model,result=lower('float unused=bump(2);ret=float3(g);')
    assert model.complete,model.unknown
    np.testing.assert_array_equal(evaluate(result),[3]*3)


@pytest.mark.historical_profile("legacy_pre30")
def test_later_declaration_in_same_statement_keeps_earlier_value_live():
    model,result=lower('float a=dot(back,float3(1)),b=a;ret=b;','float3 back;')
    assert not model.complete


def test_unused_index_initializer_is_retained_for_domain_accounting():
    model,result=lower('float a[2];float unused=a[3];ret=.4;','')
    assert model.environment['unused'].op=='array_index'


def test_unused_aggregate_keeps_helper_effects():
    model,result=lower('float2 unused={bump(2),0};ret=float3(g);')
    assert model.complete,model.unknown
    np.testing.assert_array_equal(evaluate(result),[3]*3)


def test_unused_aggregate_keeps_indexed_initializer():
    model,result=lower('float a[2];float2 unused={a[0],0};ret=.4;','')
    assert model.environment['unused'].op!='uninitialized'
