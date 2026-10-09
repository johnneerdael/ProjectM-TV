"""Frame-free final-composite statistics retain the existing descriptor semantics."""
import numpy as np
import pytest
from descriptors import DescriptorStream
from field_math import UnresolvedMath
from grid_math import evaluate_grid
from test_shader_loops import lower
from test_uniform_descriptors import compare,qualified_hsv_backend


def reduced(expression,updates,**kwargs):
    from uniform_source_descriptors import uniform_expression_window
    return uniform_expression_window(expression,updates,viewport=(32,18),quantize=True,**kwargs)


def test_source_uniform_expression_preserves_storage_colour_flash_and_nulls():
    from feedback_field import unorm8
    model,expression=lower('shader_body {ret=float3(bass,.5+.2*sin(time),.1);}')
    assert model.complete
    updates=[{'time':(i+1)/15,'inputs':{'_c2':[(i+1)/15,15,i+1,0],
                                     '_c3':[.04+(i%4)*.18,1,1,1]}} for i in range(20)]
    result=reduced(expression,updates)
    full=DescriptorStream()
    for update in updates:
        rgb=evaluate_grid(expression,batch_shape=(18,32),inputs=update['inputs'])
        rgba=unorm8(np.concatenate((rgb,np.ones((18,32,1),np.float32)),axis=-1))
        full.add({'time':update['time'],'display':rgba})
    for group in ['colour','flashing','motion','structure']:compare(full.report()[group],result[group])
    assert result['uniform_source_execution']['display_fields_constructed'] is False
    assert result['uniform_source_execution']['shader_lanes_per_update']==1


@pytest.mark.parametrize('body,inputs',[
    ('ret=uv.x;',{'_uv':[.2,.2]}),
    ('ret=GetPixel(uv);',{'_uv':[.2,.2]}),
    ('ret=_vDiffuse.xyz;',{'_vDiffuse':[1,1,1,1]}),
    ('float x=0;for(int i=0;i<3;i++){x+=.1;}ret=x;',{}),
    ('ret=bass;',{}),
])
def test_spatial_resource_loop_and_missing_input_cases_abstain(body,inputs):
    model,expression=lower('shader_body {'+body+'}')
    assert model.complete
    with pytest.raises(UnresolvedMath,match='uniform'):
        reduced(expression,[{'time':.1,'inputs':inputs}])


def test_dead_spatial_read_does_not_block_constant_final_expression():
    model,expression=lower('shader_body {float2 unused=uv;ret=float3(.2,.4,.6);}')
    assert model.complete
    result=reduced(expression,[{'time':.1,'inputs':{}},{'time':.2,'inputs':{}}])
    assert result['flashing']['peak_rgb_change_area']==0


def test_nonfinite_output_and_spatial_shaped_uniform_are_not_silently_constant():
    model,expression=lower('shader_body {ret=1/bass;}')
    assert model.complete
    with pytest.raises((UnresolvedMath,ValueError)):
        reduced(expression,[{'time':.1,'inputs':{'_c3':[0,0,0,0]}}])
    model,expression=lower('shader_body {ret=bass;}')
    with pytest.raises(UnresolvedMath,match='uniform'):
        reduced(expression,[{'time':.1,'inputs':{'_c3':np.zeros((18,32,4),np.float32)}}])


def test_empty_or_nonmonotonic_schedule_is_rejected():
    _,expression=lower('shader_body {ret=.2;}')
    with pytest.raises(ValueError,match='nonempty'):
        reduced(expression,[])
    with pytest.raises(ValueError,match='increasing'):
        reduced(expression,[{'time':.2,'inputs':{}},{'time':.1,'inputs':{}}])


def test_declared_spatial_default_cannot_hide_point_query_dependence():
    from shader_fields import Field
    field=Field('input',dtype='float3',detail={'name':'_vDiffuse','unbound_default':[.2,.4,.6]})
    with pytest.raises(UnresolvedMath,match='uniform'):
        reduced(field,[{'time':.1,'inputs':{}}])
