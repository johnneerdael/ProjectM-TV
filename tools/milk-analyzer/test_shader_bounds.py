"""Source RGB envelopes must conservatively retain float/storage/domain behavior."""
import numpy as np
import pytest
from test_field_math import lower
from grid_math import evaluate_grid
from feedback_field import unorm8


def bound(body,**kwargs):
    from shader_bounds import stored_rgb_bounds
    model,expression=lower(body,stage='composite')
    assert model.complete,model.unknown
    return stored_rgb_bounds(expression,**kwargs)


UV={'_uv':{'lower':[0,0],'upper':[1,1]}}


def test_low_contrast_feedback_proves_no_thresholded_pulses_without_frames():
    result=bound('ret=GetPixel(uv)*.05;',inputs=UV,normalized_samplers=['sampler_main'])
    assert result['status']=='computed'
    assert result['no_sampled_brightness_or_rgb_jump'] is True
    assert result['maximum_rgb_jump_bound']<.1
    assert result['display_fields_constructed'] is False
    assert result['scope']=='stored RGB expression under declared input/sampler domain'
    assert result['automatic_preset_classification'] is False


def test_unorm_storage_can_cross_the_jump_threshold():
    result=bound('ret=GetPixel(uv)*.1;',inputs=UV,normalized_samplers=['sampler_main'])
    assert result['status']=='computed'
    assert result['maximum_rgb_jump_bound']>.1
    assert result['no_sampled_brightness_or_rgb_jump'] is False


def test_jump_bounds_include_float32_subtraction_rounding():
    result=bound('ret=clamp(GetPixel(uv)*.1,1.0/255,4.0/255);',inputs=UV,normalized_samplers=['sampler_main'])
    assert result['status']=='computed'
    low=np.float32(result['stored_rgb']['lower'][0]);high=np.float32(result['stored_rgb']['upper'][0])
    actual=float(np.float32(high-low))
    assert actual>float(np.float64(high)-np.float64(low)) #a rounding-sensitive witness
    assert result['maximum_rgb_jump_bound']>=actual


@pytest.mark.parametrize('body',[
    'ret=min(GetPixel(uv)*.2,.06);',
    'ret=clamp(GetPixel(uv)*.4,.2,.25);',
    'ret=abs(GetPixel(uv)-.5)*.1;',
    'ret=uv.x>.5?GetPixel(uv)*.04:GetPixel(uv)*.03;',
    'ret=float3(uv.x*.04,uv.y*.03,0);',
])
def test_nonuniform_source_envelopes_contain_sampled_numeric_results(body):
    model,expr=lower(body,stage='composite');assert model.complete
    result=bound(body,inputs=UV,normalized_samplers=['sampler_main'])
    assert result['status']=='computed',result
    rng=np.random.default_rng(744)
    uv=rng.uniform(0,1,(1000,2)).astype(np.float32)
    def sample(detail,coordinates):return rng.uniform(0,1,(len(coordinates),4)).astype(np.float32)
    rgb=unorm8(evaluate_grid(expr,batch_shape=(1000,),inputs={'_uv':uv},sample=sample))
    assert np.all(rgb>=result['stored_rgb']['lower'])
    assert np.all(rgb<=result['stored_rgb']['upper'])


def test_constant_stored_output_is_invariant_but_motion_estimates_not_invented():
    result=bound('ret=float3(2,-1,.2);')
    assert result['stored_rgb_invariant'] is True
    assert result['stored_rgb']['lower']==result['stored_rgb']['upper']
    assert result['motion_bound'] is None


@pytest.mark.parametrize('body,inputs,samplers',[
    ('ret=GetPixel(uv);',UV,[]),
    ('ret=GetPixel(uv);',{},['sampler_main']),
    ('ret=1/(uv.x-.5);',UV,[]),
    ('ret=log(uv.x);',UV,[]),
    ('float x=0;while(bass>0){x+=1;}ret=.02;',{'_c3':{'lower':[0]*4,'upper':[1]*4}},[]),
    ('ret=normalize(float3(uv,0));',UV,[]),
])
def test_unproved_resources_domains_and_control_effects_stay_unknown(body,inputs,samplers):
    result=bound(body,inputs=inputs,normalized_samplers=samplers)
    assert result['status']=='unknown'
    assert result['stored_rgb'] is None
    assert result['no_sampled_brightness_or_rgb_jump'] is None


def test_unselected_invalid_branch_is_not_evaluated():
    result=bound('ret=bass>0?float3(.02):float3(1/0);',
                 inputs={'_c3':{'lower':[1,0,0,0],'upper':[2,0,0,0]}})
    assert result['status']=='computed',result


def test_invalid_boxes_and_proof_budget_abstain():
    result=bound('ret=uv.x;',inputs={'_uv':{'lower':[1,0],'upper':[0,1]}})
    assert result['status']=='unknown'
    result=bound('ret=uv.x*.01;',inputs=UV,max_nodes=1)
    assert result['status']=='unknown' and 'budget' in ' '.join(result['unknown_reasons'])
