"""LOD controls cannot invent mip filtering for the pinned non-mip samplers."""
import numpy as np
import pytest

import test_native_reader
from shader_fields import ShaderFields,Field
from field_math import evaluate,UnresolvedMath
from grid_math import evaluate_grid


def lower(call):
    source=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\ncomp_1=`shader_body {ret='+call+'.xyz;}\n')
    model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
    return model,model.lower(source['sections']['comp_']['tree'])


@pytest.mark.parametrize('name',['tex2Dbias','tex2Dlod'])
@pytest.mark.parametrize('lod',[-8,0,8])
def test_base_level_sampling_preserves_xy_and_ignores_finite_lod(name,lod):
    model,result=lower(name+'(sampler_main,float4(.25,.75,123,'+str(lod)+'))')
    assert model.complete,model.unknown
    def sample(detail,coordinates):
        assert detail['sampling_policy']['mipmapped'] is False
        assert detail['lod_effect']=='base level only'
        np.testing.assert_allclose(coordinates,[.25,.75])
        return [.2,.4,.6,1]
    np.testing.assert_allclose(evaluate(result,sample=sample),[.2,.4,.6])
    def grid_sample(detail,coordinates):
        assert detail['lod_effect']=='base level only'
        np.testing.assert_allclose(coordinates,[[.25,.75],[.25,.75]])
        return np.broadcast_to([.2,.4,.6,1],(2,4))
    np.testing.assert_allclose(evaluate_grid(result,batch_shape=(2,),sample=grid_sample),[[.2,.4,.6],[.2,.4,.6]])


def test_missing_lod_input_does_not_silently_become_zero():
    model,result=lower('tex2Dbias(sampler_main,float4(.25,.75,0,bass))')
    assert model.complete,model.unknown
    with pytest.raises(UnresolvedMath,match='missing symbolic'):
        evaluate(result,sample=lambda d,c:[1,1,1,1])


def test_projected_texture_coordinates_remain_a_separate_unresolved_operation():
    model,result=lower('tex2Dproj(sampler_main,float4(.25,.75,0,2))')
    assert not model.complete
    assert result.op=='unknown'


def test_bass_only_in_lod_selector_does_not_invent_visible_bass_response():
    model,result=lower('tex2Dbias(sampler_main,float4(.25,.75,0,bass*32))')
    assert model.complete,model.unknown
    sample=lambda d,c:[c[0],c[1],.5,1]
    a=evaluate(result,inputs={'_c3':[.1,0,0,0]},sample=sample)
    b=evaluate(result,inputs={'_c3':[4,0,0,0]},sample=sample)
    np.testing.assert_array_equal(a,b)


def test_nonfinite_selector_remains_unresolved_even_on_base_level_sampler():
    model,result=lower('tex2Dlod(sampler_main,float4(.25,.75,0,1./0.))')
    assert model.complete,model.unknown
    with np.errstate(all='ignore'):
        with pytest.raises(UnresolvedMath):evaluate(result,sample=lambda d,c:[1,1,1,1])
        with pytest.raises(UnresolvedMath):evaluate_grid(result,batch_shape=(2,),sample=lambda d,c:np.ones((2,4)))


@pytest.mark.parametrize('policy',[{'mipmapped':True,'base_level':0},
    {'mipmapped':False,'base_level':1},{'mipmapped':False},{}])
def test_unproven_base_level_policy_cannot_execute_an_imported_lod_graph(policy):
    coordinates=Field('constant',dtype='float2',detail={'value':[.25,.75]})
    selector=Field('constant',dtype='float',detail={'value':8})
    sample=Field('sample',args=(coordinates,selector),dtype='float4',
        detail={'sampler':'sampler_main','lod_effect':'base level only','sampling_policy':policy})
    with pytest.raises(UnresolvedMath,match='overload'):
        evaluate(sample,sample=lambda d,c:[1,1,1,1])
    with pytest.raises(UnresolvedMath,match='overload'):
        evaluate_grid(sample,batch_shape=(2,),sample=lambda d,c:np.ones((2,4)))
