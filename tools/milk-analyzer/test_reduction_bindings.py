"""Standard HLSL reductions are distinct from author-written helper bodies."""
import numpy as np
import pytest

from field_math import evaluate
from grid_math import evaluate_grid
from shader_fields import ShaderFields
import test_native_reader


def section(body):
    return test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\ncomp_1=`'+body+'\n')['sections']['comp_']


def lower(source,*,tagged=True):
    model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
    result=model.lower(source['tree'],language_extensions=source.get('language_extensions',[]) if tagged else [])
    return model,result


def test_tagged_all_any_have_component_reduction_semantics_in_each_lane():
    source=section('shader_body {ret=float3(all(float3(uv,1)),any(float3(uv,0)),all(float2(-1,0)));}')
    assert set(source['language_extensions'])=={'all'}
    model,result=lower(source)
    assert model.complete,model.unknown
    uv=np.array([[0,0],[1,0],[-1,2]],dtype=np.float32)
    expected=[[0,0,0],[0,1,0],[1,1,0]]
    np.testing.assert_array_equal(evaluate_grid(result,batch_shape=(3,),inputs={'_uv':uv}),expected)
    for values,want in zip(uv,expected):np.testing.assert_array_equal(evaluate(result,inputs={'_uv':values}),want)


def test_scalar_and_matrix_reductions_do_not_normalize_or_ignore_zero_components():
    source=section('shader_body {ret=float3(all(-2.),all(float2x2(1,0,1,1)),any(float2x2(0,0,-1,0)));}')
    model,result=lower(source);assert model.complete,model.unknown
    np.testing.assert_array_equal(evaluate(result),[1,0,1])
    np.testing.assert_array_equal(evaluate_grid(result,batch_shape=(2,)),[[1,0,1],[1,0,1]])


def test_author_helper_named_all_keeps_its_own_meaning():
    source=section('bool all(float2 p){return false;} shader_body {ret=float3(all(float2(1,1)));}')
    assert source['language_extensions']==[]
    model,result=lower(source);assert model.complete,model.unknown
    np.testing.assert_array_equal(evaluate(result),[0,0,0])


def test_missing_extension_provenance_does_not_reinterpret_empty_helper_declarations():
    source=section('shader_body {ret=float3(all(float2(1,1)));}')
    model,result=lower(source,tagged=False)
    assert not model.complete
    assert result.op=='unknown'


def test_real_early_return_remains_explicitly_unresolved():
    source=section('bool all(float2 p){if(p.x>0)return false;return true;} shader_body {ret=float3(all(uv));}')
    model,result=lower(source)
    assert not model.complete
    assert result.op=='unknown'
