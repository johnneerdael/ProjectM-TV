import numpy as np
import pytest
from test_shader_loops import lower
from shader_fields import ShaderFields
from field_math import evaluate
import test_native_reader


def current(body):
    source=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\ncomp_1='+chr(96)+'shader_body {'+body+'}\n')
    model=ShaderFields(stage='composite',frame=1,warp_reads_blur=False,array_initializer_policy='grouped-elements-v1')
    result=model.lower(source['sections']['comp_']['tree'])
    return model,result


@pytest.mark.parametrize('initializer',['1,2,3,4','float2(1,2),3,4'])
def test_current_array_groups_flat_or_mixed_lists(initializer):
    model,result=current('float2 a[2]={'+initializer+'};ret=float3(a[0],a[1].x);')
    assert model.complete,model.unknown
    np.testing.assert_array_equal(evaluate(result),[1,2,3])


def test_current_array_does_not_guess_partial_or_spanning_vectors():
    for code in ['float2 a[2]={1,2,3};ret=a[0].x;',
                 'float2 a[2]={1,float2(2,3),4};ret=a[0].x;']:
        model,_=current(code)
        assert not model.complete


def test_historical_layout_remains_rejected():
    model,_=lower('shader_body {float2 a[2]={1,2,3,4};ret=a[0].x;}')
    assert not model.complete
