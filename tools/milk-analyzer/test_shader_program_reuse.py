"""Static program reuse must preserve runtime inputs and texture-history identity."""
import copy
import gc
import weakref
import numpy as np
import pytest
from pipeline_fields import SourcePipeline
from shader_fields import ShaderFields
from test_pipeline_fields import trees


POLICY='cached-program-v1'


def pipeline(warp='ret=GetPixel(uv);',comp='ret=GetPixel(uv);',**kwargs):
    a,b=trees(warp,comp)
    return SourcePipeline(a,b,initial_feedback=np.zeros((18,32,4),np.float32),
                          warp_reads_blur=False,blur_levels=0,shader_lowering_policy=POLICY,**kwargs)


def count_lowerings(monkeypatch):
    calls=[];original=ShaderFields.lower
    def observe(self,*args,**kwargs):
        calls.append((self.stage,self.frame))
        return original(self,*args,**kwargs)
    monkeypatch.setattr(ShaderFields,'lower',observe)
    return calls


def test_one_program_per_stage_with_live_audio_time_and_uv(monkeypatch):
    new=pipeline('ret=GetPixel(uv)*.5+float3(bass*.1,uv.x*.2,0);',
                 'ret=GetPixel(uv)*(.5+sin(time)*.1);')
    old=SourcePipeline(new.warp_tree,new.composite_tree,initial_feedback=np.zeros((18,32,4),np.float32),
                       warp_reads_blur=False,blur_levels=0)
    calls=count_lowerings(monkeypatch)
    for i in range(5):
        kwargs=dict(uniforms={'_c2':[(i+1)/15,15,i+1,0],'_c3':[i*.2,1,1,1]},frame_wrap=1)
        old_result=old.step(warp_uv=old.original_uv,**kwargs)
        new.requires_warp_uv(frame_wrap=1,motion_state={})
        result=new.step(warp_uv=new.original_uv,**kwargs)
        np.testing.assert_array_equal(result.feedback,old_result.feedback)
        np.testing.assert_array_equal(result.display,old_result.display)
    assert len(calls)==12 #10 baseline calls plus two cached programs
    assert result.history['shader_lowering_policy']==POLICY
    assert result.history['shader_program_work']['retained_stages']==2
    assert result.history['shader_program_work']['lowerings']==2


def test_sampler_frames_and_nested_mutations_are_local_to_each_update():
    a,b=trees('ret=GetPixel(uv)+GetBlur1(uv)*.1;','ret=GetPixel(uv);')
    args=dict(initial_feedback=np.zeros((32,32,4)),warp_reads_blur=True,blur_levels=1)
    old=SourcePipeline(a,b,**args);new=SourcePipeline(a,b,**args,shader_lowering_policy=POLICY)
    for _ in range(3):
        traces=[]
        for p in [old,new]:
            trace=[]
            result=p.step(warp_uv=p.original_uv,uniforms={},frame_wrap=1,
                on_sample=lambda stage,detail,uv,lanes:trace.append((stage,copy.deepcopy(detail),lanes.tolist())))
            traces.append(trace)
        assert traces[0]==traces[1]
    assert len(new._program_cache)==2


def test_callback_detail_mutation_does_not_poison_cached_program():
    p=pipeline('ret=tex2D(sampler_texture,uv).xyz;')
    observed=[]
    def observer(stage,detail,uv,lanes):
        if detail['canonical_texture']=='texture':
            observed.append(detail['sampling_policy']['wrap'])
            detail['sampling_policy']['wrap']=False
    def external(detail,uv):
        assert detail['sampling_policy']['wrap'] is False #observer mutation remains visible within update
        return np.full((len(uv),4),.4,np.float32)
    for _ in range(3):p.step(warp_uv=p.original_uv,uniforms={},frame_wrap=1,on_sample=observer,external_sample=external)
    assert observed==[True]*3


def test_wrap_boundary_and_source_mutation_rebuild_only_affected_program(monkeypatch):
    p=pipeline();calls=count_lowerings(monkeypatch)
    for wrap in [1,.5,0,0,1]:p.step(warp_uv=p.original_uv,uniforms={},frame_wrap=wrap)
    assert [name for name,frame in calls].count('warp')==3
    assert [name for name,frame in calls].count('composite')==1
    replacement,_=trees('ret=.7;','ret=GetPixel(uv);')
    p.warp_tree[:]=replacement
    result=p.step(warp_uv=p.original_uv,uniforms={},frame_wrap=1)
    assert len(calls)==5
    np.testing.assert_allclose(result.feedback[...,:3],178/255,atol=1e-7)


@pytest.mark.parametrize('attribute,value',[
    ('main_binding_policy','projectmtv-core-2.2.6-v1'),
    ('warp_reads_blur',True),
    ('known_uniforms',{'_qf4':[1,0,0,0]}),
    ('known_uniform_components',{'_qf4':{'x':0}}),
    ('known_uniform_component_domains',{'_qf4':{'x':[0,1]}}),
    ('language_extensions',{'warp':['all']}),
    ('native_samplers',{'warp':{'sampler_main':'sampler2D'}}),
    ('array_initializer_policies',{'warp':'grouped-elements-v1'}),
    ('global_input_policies',{'warp':'projectmtv-implicit-extern-zero-v1'}),
])
def test_context_changes_invalidate_programs(attribute,value,monkeypatch):
    p=pipeline();p._lower_stage(p.warp_tree,'warp',1)
    calls=count_lowerings(monkeypatch);setattr(p,attribute,value)
    p._lower_stage(p.warp_tree,'warp',1)
    assert calls


def test_unserializable_context_bypasses_reuse_and_owner_is_collectable(monkeypatch):
    p=pipeline();calls=count_lowerings(monkeypatch)
    p.known_uniforms={'unused':np.array([1,2])}
    for _ in range(2):p._lower_stage(p.warp_tree,'warp',1)
    assert len(calls)==2 and not p._program_cache
    p.known_uniforms={}
    p._lower_stage(p.warp_tree,'warp',1)
    model=weakref.ref(p._program_cache['warp']['model']);owner=weakref.ref(p)
    del p;gc.collect()
    assert owner() is None and model() is None


def test_default_policy_and_invalid_wrap_never_reuse_or_bypass_validation():
    a,b=trees('ret=GetPixel(uv);','ret=GetPixel(uv);')
    old=SourcePipeline(a,b,initial_feedback=np.zeros((18,32,4)),warp_reads_blur=False,blur_levels=0)
    result=old.step(warp_uv=old.original_uv,uniforms={},frame_wrap=1)
    assert result.history['shader_lowering_policy']=='per-frame-v1' and not old._program_cache
    p=pipeline();p._lower_stage(p.warp_tree,'warp',1)
    with pytest.raises(ValueError,match='finite frame wrap'):
        p._lower_stage(p.warp_tree,'warp',np.nan)


def test_detached_original_context_cannot_mutate_a_cached_constant():
    p=pipeline('ret=bass;')
    original=[.2,0,0,0]
    p.known_uniforms={'_c3':original}
    first=p.step(warp_uv=p.original_uv,uniforms={},frame_wrap=1)
    p.known_uniforms={'_c3':[.2,0,0,0]}
    original[0]=.8
    second=p.step(warp_uv=p.original_uv,uniforms={},frame_wrap=1)
    np.testing.assert_array_equal(second.feedback,first.feedback)


def test_integer_and_string_component_keys_do_not_share_cache_identity():
    p=pipeline('ret=q29;')
    p.known_uniform_components={'_qh':{0:.5}}
    p.step(warp_uv=p.original_uv,uniforms={'_qh':[.1,0,0,0]},frame_wrap=1)
    p.known_uniform_components={'_qh':{'0':.5}}
    result=p.step(warp_uv=p.original_uv,uniforms={'_qh':[.1,0,0,0]},frame_wrap=1)
    np.testing.assert_allclose(result.feedback[...,:3],26/255,atol=1e-7)


def test_shared_sampler_policy_aliases_survive_per_update_detail_copy():
    a,b=trees('ret=(GetPixel(uv+float2(1.2,0))+GetPixel(uv+float2(1.2,0)))*.1;',
              'ret=GetPixel(uv);')
    initial=np.ones((18,32,4),np.float32);initial[:,:16,:3]=[1,0,0];initial[:,16:,:3]=[0,1,0]
    args=dict(initial_feedback=initial,warp_reads_blur=False,blur_levels=0)
    results=[];traces=[]
    for policy in ['per-frame-v1',POLICY]:
        p=SourcePipeline(a,b,**args,shader_lowering_policy=policy);trace=[]
        def observer(stage,detail,uv,lanes):
            if stage=='warp':
                trace.append(detail['sampling_policy']['wrap'])
                detail['sampling_policy']['wrap']=False
        results.append(p.step(warp_uv=p.original_uv,uniforms={},frame_wrap=1,on_sample=observer))
        traces.append(trace)
    assert traces[0]==traces[1]==[True,False]
    np.testing.assert_array_equal(results[0].feedback,results[1].feedback)


def test_wrap_scalar_type_change_cannot_bypass_nan_sampler_guard():
    from field_math import UnresolvedMath
    body='float z=uv.x-uv.x;float bad=z/z;ret=GetPixel(float2(bad,bad));'
    p=pipeline(body,coordinate_profile='apple-m4pro-gl41-nan-sampler-v1')
    p.step(warp_uv=p.original_uv,uniforms={},frame_wrap=1.)
    with pytest.raises(UnresolvedMath,match='NaN sampler addressing policy unresolved'):
        p.step(warp_uv=p.original_uv,uniforms={},frame_wrap=np.float32(1.))


def test_forecast_domain_selects_reuse_without_changing_descriptor_report(monkeypatch):
    import os
    from pathlib import Path
    import forecast
    import test_forecast
    import test_native_audio
    from shader_compat import check_shader
    from analyzer_test_profiles import validator_path
    binaries=Path(os.environ.get('MILK_TEST_CURRENT_BINARIES',test_forecast.BINARIES))
    monkeypatch.setattr(test_native_audio,'BINARY',binaries/'milk-audio-inputs')
    source=test_forecast.native(test_forecast.BASE+'comp_1=`shader_body {ret=float3(.3+.1*sin(time));}\n',binaries=binaries)
    compat={'composite':check_shader(source['sections']['comp_']['source'],stage='composite',profile='glsl330',
        translator=binaries/'milk-shader-translate',validator=validator_path(),samplers={'sampler_main':'sampler2D'},texture_sizes=[])}
    audio=test_forecast.audio(3);settings=test_forecast.domain()
    old=forecast.forecast_source(source,audio=audio,binaries=binaries,domain=settings,compatibility=compat)
    new=forecast.forecast_source(source,audio=audio,binaries=binaries,
        domain={**settings,'shader_lowering_policy':POLICY},compatibility=compat)
    assert old['descriptors']==new['descriptors']
    for a,b in zip(old['frames'],new['frames']):np.testing.assert_array_equal(a['display'],b['display'])
    assert new['frames'][-1]['history']['shader_program_work']['lowerings']==1
    assert new['provenance']['shader_lowering_policy']==POLICY
