"""State-flow fixtures; values follow explicitly sequenced shader statements."""
import numpy as np
import pytest

import test_native_reader
from shader_fields import ShaderFields
from field_math import evaluate
from grid_math import evaluate_grid


PREFIX='float g=1; float bump(float v){g+=v;return g;} '


def lower(body,prefix=PREFIX):
    section=test_native_reader.NativeReaderTest().read(
        'PSVERSION_COMP=2\ncomp_1=`'+prefix+'shader_body {'+body+'}\n')['sections']['comp_']
    assert section['status']=='parsed',section
    model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
    return model,model.lower(section['tree'])


@pytest.mark.parametrize('prefix,body,expected',[
    (PREFIX,'float a=bump(2);float b=bump(4);ret=float3(a,b,g);',[3,7,7]),
    (PREFIX,'bump(2);ret=float3(g);',[3,3,3]),
    (PREFIX,'float g=9;float a=bump(2);ret=float3(g,a,0);',[9,3,0]),
    (PREFIX+'float outer(float g){float unused=bump(2);return g;} ',
     'float a=outer(g);ret=float3(a,g,0);',[1,3,0]),
    (PREFIX,'float a;{float g=9;a=bump(2);}ret=float3(g,a,0);',[3,3,0]),
    (PREFIX,'for(int i=0;i<3;i++){bump(1);}ret=float3(g);',[4,4,4]),
    (PREFIX+'float outer(float v){for(int i=0;i<3;i++){bump(v);}return g;} ',
     'float a=outer(2);ret=float3(a,g,0);',[7,7,0]),
])
def test_sequenced_helper_global_updates_preserve_scope_and_loop_state(prefix,body,expected):
    model,result=lower(body,prefix);assert model.complete,model.unknown
    np.testing.assert_allclose(evaluate(result),expected,atol=1e-6)
    np.testing.assert_allclose(evaluate_grid(result,batch_shape=(2,)),[expected,expected],atol=1e-6)


def test_branch_dependent_helper_writes_are_isolated_per_pixel():
    prefix='float g=1;float choose(float v){if(v>0){g=2;}else{g=4;}return g;} '
    model,result=lower('float a=choose(uv.x);ret=float3(a,g,0);',prefix)
    assert model.complete,model.unknown
    uv=np.array([[-1,0],[1,0]],dtype=np.float32)
    np.testing.assert_array_equal(evaluate_grid(result,batch_shape=(2,),inputs={'_uv':uv}),[[4,4,0],[2,2,0]])


def test_branch_update_then_loop_keeps_the_current_global_value():
    model,result=lower('if(uv.x>0){bump(1);}for(int i=0;i<3;i++){bump(1);}ret=float3(g);')
    assert model.complete,model.unknown
    uv=np.array([[-1,0],[1,0]],dtype=np.float32)
    np.testing.assert_array_equal(evaluate_grid(result,batch_shape=(2,),inputs={'_uv':uv}),[[4,4,4],[5,5,5]])


def test_loop_with_shared_and_shadowed_names_stays_unresolved():
    model,result=lower('float g=9;for(int i=0;i<3;i++){bump(1);}ret=float3(g);')
    assert not model.complete
    assert result.op=='unknown'


@pytest.mark.parametrize('body',[
    'ret=float3(bump(2)+g);',
    'ret=float3(g,bump(2),0);',
    'ret=uv.x>0?float3(bump(2)):float3(g);',
])
def test_unsequenced_or_conditional_shared_writes_remain_unknown(body):
    model,result=lower(body)
    assert not model.complete
    assert result.op=='unknown'


def test_index_helper_mutating_the_indexed_array_is_not_read_as_old_state():
    prefix='float a[2]={1.,2.};int change(){a[0]=9;return 0;} '
    model,result=lower('ret=float3(a[change()]);',prefix)
    assert not model.complete
    assert result.op=='unknown'


@pytest.mark.parametrize('storage,helper',[
    ('float a[2]={1.,2.};','float change(){i=1;return 9;}'),
    ('float2 a=float2(1,2);','float change(){i=1;return 9;}'),
    ('float a[2]={1.,2.};','float inner(){i=1;return 9;}float change(){return inner();}'),
])
def test_assignment_destination_index_is_captured_before_rhs_helper(storage,helper):
    model,result=lower('a[i]=change();ret=float3(a[0],a[1],i);','int i=0;'+storage+helper)
    assert model.complete,model.unknown
    np.testing.assert_array_equal(evaluate(result),[9,2,1])
    np.testing.assert_array_equal(evaluate_grid(result,batch_shape=(2,)),[[9,2,1],[9,2,1]])


def test_compound_assignment_keeps_a_captured_index_when_rhs_only_changes_index():
    model,result=lower('a[i]+=change();ret=float3(a[0],a[1],i);',
        'int i=0;float2 a=float2(1,2);float change(){i=1;return 9;}')
    assert model.complete,model.unknown
    np.testing.assert_array_equal(evaluate(result),[10,2,1])
    np.testing.assert_array_equal(evaluate_grid(result,batch_shape=(2,)),[[10,2,1],[10,2,1]])
