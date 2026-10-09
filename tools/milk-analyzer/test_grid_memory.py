"""Large evaluation inputs must not wait for cyclic GC after one shader call."""
import gc
import weakref
import numpy as np
import pytest
from shader_fields import Field
from grid_math import evaluate_grid
from field_math import UnresolvedMath


def field(name,dtype):return Field('input',dtype=dtype,detail={'name':name})


@pytest.fixture
def without_cycle_collection():
    gc.collect();enabled=gc.isenabled();gc.disable()
    try:yield
    finally:
        gc.collect()
        if enabled:gc.enable()


def test_completed_evaluation_releases_input_without_gc(without_cycle_collection):
    data=np.arange(32*32*3,dtype=np.float32).reshape(32,32,3);before=data.copy();ref=weakref.ref(data)
    inputs={'x':data};out=evaluate_grid(field('x','float3'),batch_shape=(32,32),inputs=inputs)
    np.testing.assert_array_equal(out,before);np.testing.assert_array_equal(data,before)
    assert inputs['x'] is data
    del data,inputs
    assert ref() is None, 'evaluation closures must release borrowed inputs immediately'
    np.testing.assert_array_equal(out,before) # returned values still own valid storage


def test_completed_evaluation_releases_sampler_closure(without_cycle_collection):
    texture=np.ones((32,32,4),np.float32);ref=weakref.ref(texture)
    def make_sampler(image):
        def sampler(detail,uv):return np.broadcast_to(image[0,0,:3],(len(uv),3)).copy()
        return sampler
    sampler=make_sampler(texture);sampler_ref=weakref.ref(sampler)
    expr=Field('sample',args=(field('uv','float2'),),dtype='float3',detail={'sampler':'test'})
    result=evaluate_grid(expr,batch_shape=(4,4),inputs={'uv':[.5,.5]},sample=sampler)
    del texture,sampler
    assert sampler_ref() is None and ref() is None
    np.testing.assert_array_equal(result,np.ones((4,4,3),np.float32))


def test_failed_evaluation_releases_inputs_but_retains_domain_error(without_cycle_collection):
    data=-np.ones((16,16),np.float32);ref=weakref.ref(data)
    expr=Field('log',args=(field('x','float'),),dtype='float')
    with pytest.raises(UnresolvedMath,match='numeric domain'):
        evaluate_grid(expr,batch_shape=(16,16),inputs={'x':data})
    del data
    assert ref() is None


def test_observation_callback_releases_captured_buffer(without_cycle_collection):
    data=np.ones((16,16,4),np.float32);ref=weakref.ref(data)
    def observer_factory(image):
        def observer(detail,uv,lanes):assert image.shape==(16,16,4)
        return observer
    observer=observer_factory(data);observer_ref=weakref.ref(observer)
    expr=Field('sample',args=(field('uv','float2'),),dtype='float3',detail={'sampler':'test'})
    result=evaluate_grid(expr,batch_shape=(2,2),inputs={'uv':[.5,.5]},
        sample=lambda detail,uv:np.ones((len(uv),3),np.float32),on_sample=observer)
    del observer,data
    assert observer_ref() is None and ref() is None
    np.testing.assert_array_equal(result,np.ones((2,2,3),np.float32))


def test_identical_branch_lanes_share_readonly_evaluation_context():
    uv=field('uv','float2');predicate=field('mask','bool')
    sampled=Field('sample',args=(uv,),dtype='float3',detail={'sampler':'test'})
    zero=Field('constant',dtype='float3',detail={'value':[0,0,0]})
    left=Field('select',args=(predicate,sampled,zero),dtype='float3')
    right=Field('select',args=(predicate,sampled,zero),dtype='float3')
    expression=Field('add',args=(left,right),dtype='float3')
    calls=[]
    def sample(detail,coordinates):
        calls.append(coordinates.copy());return np.full((len(coordinates),3),.25,np.float32)
    mask=np.array([True,False,True,False])
    output=evaluate_grid(expression,batch_shape=(4,),inputs={'uv':np.arange(8,dtype=np.float32).reshape(4,2),'mask':mask},sample=sample)
    np.testing.assert_array_equal(output,np.repeat((mask*.5)[:,None],3,axis=1))
    assert len(calls)==1, 'same node/lanes/state must not allocate a second sampled grid'
