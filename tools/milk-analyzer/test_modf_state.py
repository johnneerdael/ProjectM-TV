"""Fractional returns and floating output storage follow target call semantics."""
import numpy as np
import pytest

import test_native_reader
from shader_fields import ShaderFields
from field_math import evaluate
from grid_math import evaluate_grid


def lower(body,helpers=''):
    section=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\ncomp_1=`'+helpers+
        'shader_body {'+body+'}\n')['sections']['comp_']
    assert section['status']=='parsed',section
    model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
    return model,model.lower(section['tree'])


@pytest.mark.parametrize('number,expected',[
    ('2.75',[.75,2,0]),('-2.75',[-.75,-2,0]),('-2.0',[-0.,-2,0]),
    ('0.0',[0,0,0]),('-0.0',[-0.,-0.,0]),
])
def test_fraction_and_output_integer_have_correct_values_and_sign(number,expected):
    model,result=lower('float whole;float f=modf('+number+',whole);ret=float3(f,whole,0);')
    assert model.complete,model.unknown
    actual=evaluate(result)
    np.testing.assert_array_equal(actual,expected)
    np.testing.assert_array_equal(np.signbit(actual[:2]),np.signbit(np.array(expected)[:2]))
    np.testing.assert_array_equal(evaluate_grid(result,batch_shape=(2,)),[expected,expected])


@pytest.mark.parametrize('body,helpers,expected',[
    ('float v=2.75;float f=modf(v,v);ret=float3(f,v,0);','',[.75,2,0]),
    ('float2 p;float f=modf(2.75,p.x);ret=float3(f,p.x,0);','',[.75,2,0]),
    ('float a[2];float f=modf(2.75,a[1]);ret=float3(f,a[1],0);','',[.75,2,0]),
    ('float2 whole;float2 f=modf(float2(2.75,-1.5),whole);ret=float3(f,whole.x);','',[.75,-.5,2]),
    ('modf(2.75,g);ret=float3(g);','float g=0;',[2,2,2]),
    ('for(int i=0;i<3;i++){modf(i+.75,g);}ret=float3(g);','float g=0;',[2,2,2]),
    ('float whole=0;for(int i=0;i<3;i++){modf(whole+1.75,whole);}ret=float3(whole);','',[3,3,3]),
    ('float whole;float f=add(modf(2.75,whole),whole);ret=float3(f,whole,0);',
     'float add(float a,float b){return a+b;} ',[2.75,2,0]),
])
def test_output_storage_and_call_order_are_preserved(body,helpers,expected):
    model,result=lower(body,helpers);assert model.complete,model.unknown
    np.testing.assert_allclose(evaluate(result),expected,atol=1e-6)
    np.testing.assert_allclose(evaluate_grid(result,batch_shape=(2,)),[expected,expected],atol=1e-6)


@pytest.mark.parametrize('body',[
    'float whole;ret=float3(modf(2.75,whole)+whole);',
    'float whole;ret=true?float3(modf(2.75,whole)):float3(0);',
    'float2 p;modf(2.75,p.x);ret=float3(p.y);',
    'const float whole=0;ret=float3(modf(2.75,whole));',
    'ret=float3(modf(2.75,1.));',
])
def test_unknown_order_unwritten_components_and_invalid_outputs_stay_unknown(body):
    model,result=lower(body)
    assert not model.complete
    assert result.op=='unknown'


@pytest.mark.parametrize('body',[
    'float whole=10;whole+=modf(2.75,whole);ret=float3(whole);',
    'float2 p=float2(10,0);p.x+=modf(2.75,p.x);ret=float3(p.x);',
    'float a[2]={10.,0.};a[0]+=modf(2.75,a[0]);ret=float3(a[0]);',
])
def test_local_output_mutating_compound_value_remains_unresolved(body):
    model,result=lower(body)
    assert not model.complete
    assert result.op=='unknown'


def test_integer_output_remains_float_beyond_signed_integer_range():
    model,result=lower('float whole;float f=modf(3e38,whole);ret=float3(f,whole,0);')
    assert model.complete,model.unknown
    expected=np.array([0,np.float32(3e38),0],dtype=np.float32)
    np.testing.assert_array_equal(evaluate(result),expected)
    np.testing.assert_array_equal(evaluate_grid(result,batch_shape=(2,)),[expected,expected])
