"""Defined highp infinities can have finite consumers; NaNs stay unresolved."""
import numpy as np
import pytest

from field_math import evaluate,UnresolvedMath
from grid_math import evaluate_grid
from test_field_math import lower

POLICY='gles300-highp-infinity-v1'


@pytest.mark.parametrize('body,expected',[
    ('float x=1/bass;ret=saturate(1-x*x);',[0,0,0]),
    ('float2 x=float2(1e29,2e29);ret=float3(1/(dot(x,x)+2));',[0,0,0]),
    ('float x=1/bass;ret=saturate(x);',[1,1,1]),
    ('float x=1/bass;ret=float3(0*x);',[0,0,0]),
    ('float x=1/bass;ret=float3(x*0);',[0,0,0]),
    ('float x=1;for(int i=0;i<2;i++){x/=bass;}ret=saturate(x);',[1,1,1]),
])
def test_highp_finite_consumers_agree_between_scalar_and_grid(body,expected):
    _,field=lower(body)
    inputs={'_c3':[0,0,0,0]}
    np.testing.assert_array_equal(evaluate(field,inputs=inputs,numeric_policy=POLICY),expected)
    np.testing.assert_array_equal(evaluate_grid(field,batch_shape=(2,),inputs=inputs,numeric_policy=POLICY),[expected]*2)


@pytest.mark.parametrize('body',[
    'ret=float3(0/bass);',
    'float x=1/bass;ret=saturate(x-x);',
    'float x=1/bass;x*=0;ret=saturate(x);',
    'ret=pow(bass,-.1);',
    'int x=1/bass;ret=float3(x);',
    'ret=GetPixel(float2(1/bass));',
    'ret=float3(-1/bass);',
])
def test_highp_policy_does_not_zero_undefined_domains_or_sampling(body):
    _,field=lower(body)
    inputs={'_c3':[0,0,0,0]}
    def sample(*args):pytest.fail('nonfinite sampling reached callback')
    with pytest.raises(UnresolvedMath):evaluate(field,inputs=inputs,sample=sample,numeric_policy=POLICY)
    with pytest.raises(UnresolvedMath):evaluate_grid(field,batch_shape=(2,),inputs=inputs,sample=sample,numeric_policy=POLICY)


def test_strict_default_still_rejects_infinity_and_profiles_cannot_mix():
    _,field=lower('ret=saturate(1/bass);')
    with pytest.raises(UnresolvedMath):evaluate(field,inputs={'_c3':[0]*4})
    with pytest.raises(UnresolvedMath):evaluate_grid(field,batch_shape=(1,),inputs={'_c3':[0]*4})
    with pytest.raises(UnresolvedMath):evaluate(field,numeric_policy='mediump')
    with pytest.raises(UnresolvedMath):evaluate_grid(field,batch_shape=(1,),numeric_policy=POLICY,
        coordinate_profile='apple-m4pro-gl41-nan-sampler-v1')


def test_isolated_highp_queries_close_at_the_declared_normalized_rgb_sink():
    from strict_source_features import colour_queries
    _,field=lower('ret=float3(1/bass);')
    result=colour_queries(field,[{'_c3':[0]*4}],numeric_policy=POLICY)
    assert result['status']=='computed'
    assert result['rgb_queries']==[[1,1,1]]
    assert result['uses_display_fields'] is False
    assert result['numeric_policy']==POLICY


def test_source_forecast_highp_is_explicit_and_gles_only():
    from test_forecast import native,BASE,predict,domain,BINARIES
    from shader_compat import check_shader
    from analyzer_test_profiles import validator_path
    source=native(BASE+'per_frame_1=q1=0;\ncomp_1=`shader_body {ret=float3(1/q1);}\n')
    evidence={'composite':check_shader(source['sections']['comp_']['source'],stage='composite',profile='gles300',
        translator=BINARIES/'milk-shader-translate',validator=validator_path(),samplers={'sampler_main':'sampler2D'},texture_sizes=[])}
    settings=domain();settings.update(profile='gles300',shader_numeric_policy=POLICY)
    result=predict(source,domain=settings,compatibility=evidence)
    assert result['status']=='computed'
    assert result['provenance']['shader_numeric_policy']==POLICY
    np.testing.assert_array_equal(result['frames'][0]['display'][...,:3],np.ones((32,32,3)))
    settings['profile']='glsl330'
    with pytest.raises(ValueError,match='GLES300'):predict(source,domain=settings,compatibility=evidence)


@pytest.mark.parametrize('bad',[float('nan'),float('inf'),1e100])
def test_zero_guard_does_not_hide_nonfinite_external_inputs(bad):
    _,field=lower('ret=float3(bass*0);')
    for policy in ('strict',POLICY):
        with pytest.raises(UnresolvedMath):evaluate(field,inputs={'_c3':[bad,0,0,0]},numeric_policy=policy)
        with pytest.raises(UnresolvedMath):evaluate_grid(field,batch_shape=(2,),inputs={'_c3':[bad,0,0,0]},numeric_policy=policy)


def test_nonfinite_lod_is_rejected_even_for_base_level_only_sampling():
    _,field=lower('ret=tex2Dlod(sampler_main,float4(uv,0,1/bass)).xyz;')
    inputs={'_uv':[.5,.5,0,0],'_c3':[0]*4}
    def sample(*args):pytest.fail('nonfinite LOD reached sampling callback')
    with pytest.raises(UnresolvedMath):evaluate_grid(field,batch_shape=(2,),inputs=inputs,sample=sample,numeric_policy=POLICY)


@pytest.mark.parametrize('inputs',[{'_c3':[1e-40,0,0,0]},{'_c3':[-1,1e-40,0,0]}])
def test_subnormal_division_requires_a_declared_flushing_policy(inputs):
    _,field=lower('ret=saturate(bass/mid);')
    with pytest.raises(UnresolvedMath):evaluate(field,inputs=inputs,numeric_policy=POLICY)
    with pytest.raises(UnresolvedMath):evaluate_grid(field,batch_shape=(2,),inputs=inputs,numeric_policy=POLICY)


def test_components_store_defined_infinity_until_normalized_consumption():
    _,field=lower('float3 x=0;x.x=1/bass;ret=saturate(x);')
    np.testing.assert_array_equal(evaluate(field,inputs={'_c3':[0]*4},numeric_policy=POLICY),[1,0,0])
    np.testing.assert_array_equal(evaluate_grid(field,batch_shape=(2,),inputs={'_c3':[0]*4},numeric_policy=POLICY),[[1,0,0]]*2)


def test_direct_pipeline_from_source_rejects_desktop_profile_with_gles_arithmetic():
    from test_forecast import native,BASE
    from pipeline_fields import SourcePipeline
    source=native(BASE)
    with pytest.raises(ValueError,match='GLES300'):
        SourcePipeline.from_source(source,profile='glsl330',compatibility={},initial_feedback=np.zeros((2,2,4)),
            warp_reads_blur=False,blur_levels=0,shader_numeric_policy=POLICY)
