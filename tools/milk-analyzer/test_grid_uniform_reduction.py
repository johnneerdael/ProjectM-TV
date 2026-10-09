"""Uniform DAG reduction must preserve values, selected domains and sample lanes."""
import numpy as np
import pytest
from grid_math import evaluate_grid
from test_field_math import lower

POLICY='uniform-proof-v1'


def uv_field(shape):
    y,x=np.meshgrid(np.linspace(.1,.9,shape[0],dtype=np.float32),
                    np.linspace(.1,.9,shape[1],dtype=np.float32),indexing='ij')
    return np.stack((x,y,np.zeros_like(x),np.zeros_like(y)),axis=-1)


@pytest.mark.parametrize('body',[
    'ret=float3(sin(time)*bass,cos(time)+mid,pow(treb,.5));',
    'float a=sin(time*.75)*bass;ret=float3(uv.x+a,uv.y*a,a);',
    'ret=uv.x>.5?float3(log(bass)):float3(sin(time));',
    'float2x2 m=float2x2(cos(time),-sin(time),sin(time),cos(time));ret=float3(mul(uv,m),0);',
])
def test_reduced_values_are_bit_identical_for_uniform_and_mixed_graphs(body):
    _,field=lower(body);inputs={'_uv':uv_field((12,16)),'_c2':[.31,30,0,0],'_c3':[.75,.4,1.4,0]}
    baseline=evaluate_grid(field,batch_shape=(12,16),inputs=inputs)
    work={};reduced=evaluate_grid(field,batch_shape=(12,16),inputs=inputs,work_policy=POLICY,work=work)
    np.testing.assert_array_equal(reduced.view(np.uint32),baseline.view(np.uint32))
    assert work['uniform_subgraphs']>0 and work['math_lanes_avoided']>0


def test_entire_uniform_shader_evaluates_one_lane_without_full_math_arrays(monkeypatch):
    import grid_math
    _,field=lower('ret=float3(sin(time),cos(time),bass*.5);')
    rows=[];original=grid_math._convert
    def observe(value,dtype,count,**kwargs):
        rows.append(count);return original(value,dtype,count,**kwargs)
    monkeypatch.setattr(grid_math,'_convert',observe)
    result=evaluate_grid(field,batch_shape=(480,854),inputs={'_c2':[.3,30,0,0],'_c3':[.75,0,0,0]},work_policy=POLICY)
    assert result.shape==(480,854,3)
    assert max(rows)==1
    np.testing.assert_array_equal(result[0,0],result[-1,-1])
    assert result.flags.writeable


def test_sample_and_observer_keep_all_lanes_and_history_under_reduction():
    _,field=lower('ret=GetPixel(uv+float2(sin(time)*.02,0))*bass;')
    inputs={'_uv':uv_field((8,8)),'_c2':[.3,30,0,0],'_c3':[.75,0,0,0]}
    calls=[]
    def sample(detail,coordinates):
        calls.append(coordinates.copy());return np.column_stack((coordinates,np.ones((len(coordinates),2),np.float32)))
    observed=[]
    result=evaluate_grid(field,batch_shape=(8,8),inputs=inputs,sample=sample,
                         on_sample=lambda detail,coordinates,lanes:observed.append(lanes.copy()),work_policy=POLICY)
    assert result.shape==(8,8,3) and len(calls)==len(observed)==1
    assert calls[0].shape==(64,2)
    np.testing.assert_array_equal(observed[0],np.arange(64))


def test_unselected_bad_uniform_domain_is_not_eagerly_hoisted():
    _,field=lower('ret=uv.x>0?float3(1):float3(log(-1));')
    result=evaluate_grid(field,batch_shape=(8,8),inputs={'_uv':uv_field((8,8))},work_policy=POLICY)
    np.testing.assert_array_equal(result,1)


def test_uniform_loop_coefficients_do_not_freeze_evolving_loop_slots():
    _,field=lower('float x=0;for(int i=0;i<3;i++){x+=bass;}ret=float3(x,uv);')
    inputs={'_uv':uv_field((8,8)),'_c3':[.125,0,0,0]}
    baseline=evaluate_grid(field,batch_shape=(8,8),inputs=inputs)
    reduced=evaluate_grid(field,batch_shape=(8,8),inputs=inputs,work_policy=POLICY)
    np.testing.assert_array_equal(reduced,baseline)
    np.testing.assert_array_equal(reduced[...,0],.375)


def test_sampler_can_wrap_coordinates_in_place_and_reuse_the_node():
    from shader_fields import Field
    uv=Field('input',dtype='float2',detail={'name':'uv'})
    sample_node=Field('sample',(uv,),'float3',{'sampler':'test'})
    # Reuse the same coordinate node after the callback, preserving the old
    # writable callback boundary and its cached result ownership.
    channel=Field('member',(uv,),'float',{'field':'x','swizzle':True})
    expr=Field('add',(sample_node,channel),'float3')
    def sample(detail,coords):
        np.mod(coords,1,out=coords)
        return np.column_stack((coords,np.zeros(len(coords),np.float32)))
    before=evaluate_grid(expr,batch_shape=(4,),inputs={'uv':[1.25,1.5]},sample=sample)
    after=evaluate_grid(expr,batch_shape=(4,),inputs={'uv':[1.25,1.5]},sample=sample,work_policy=POLICY)
    np.testing.assert_array_equal(after,before)


def test_pipeline_reports_reduced_shader_work_without_changing_surfaces():
    from pipeline_fields import SourcePipeline
    from test_pipeline_fields import trees
    warp,comp=trees('ret=float3(sin(time)*.1+.3);','ret=GetPixel(uv)*(.5+sin(time)*.1);')
    args=dict(initial_feedback=np.zeros((18,32,4),np.float32),warp_reads_blur=False,blur_levels=0)
    old=SourcePipeline(warp,comp,**args)
    new=SourcePipeline(warp,comp,**args,shader_work_policy=POLICY)
    for time in [.1,.2,.3]:
        kwargs=dict(uniforms={'_c2':[time,30,0,0]},frame_wrap=1)
        baseline=old.step(warp_uv=old.original_uv,**kwargs)
        reduced=new.step(warp_uv=new.original_uv,**kwargs)
        np.testing.assert_array_equal(reduced.feedback,baseline.feedback)
        np.testing.assert_array_equal(reduced.display,baseline.display)
        assert reduced.history['shader_work_policy']==POLICY
        assert reduced.history['shader_work']['warp']['math_lanes_avoided']>0
