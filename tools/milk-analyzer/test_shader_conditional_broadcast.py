"""Scalar ternary branches must populate every declared vector component."""
import numpy as np
import pytest
from shader_fields import Field,ShaderFields
from field_math import evaluate
from grid_math import evaluate_grid
from test_core2331_warp import read_source


@pytest.mark.parametrize('yes,no,expected', [
    (Field('constant',dtype='float3',detail={'value':[.2,.4,.6]}),Field('constant',dtype='float',detail={'value':0}),[.2,.4,.6]),
    (Field('constant',dtype='float',detail={'value':1}),Field('constant',dtype='float3',detail={'value':[.2,.4,.6]}),[1,1,1])])
def test_select_component_split_broadcasts_scalar(yes,no,expected):
    model=ShaderFields(stage='composite',frame=0,warp_reads_blur=False)
    value=Field('select',(Field('constant',dtype='bool',detail={'value':True}),yes,no),'float3')
    parts=model.parts(value)
    assert len(parts)==3
    np.testing.assert_array_equal([evaluate(v) for v in parts],np.array(expected,np.float32))


def test_native_conditional_sample_scalar_branch_lowers_and_runs_both_paths(tmp_path):
    source,_=read_source(tmp_path,
        'MILKDROP_PRESET_VERSION=201\nPSVERSION_COMP=2\n'
        'comp_1=`shader_body {ret=time>1?GetPixel(float2(ang,1/(rad+.1))):0;}\n')
    model=ShaderFields(stage='composite',frame=0,warp_reads_blur=False)
    expression=model.lower(source['sections']['comp_']['tree'])
    assert model.complete,model.unknown
    for time,expected in [(0,0),(2,.4)]:
        result=evaluate_grid(expression,batch_shape=(1,1),inputs={'_c2':[time,0,0,0],'_rad_ang':[.5,.1]},
                             sample=lambda detail,coordinates:np.full((1,1,4),.4,np.float32))
        np.testing.assert_array_equal(result,np.full((1,1,3),expected,np.float32))
