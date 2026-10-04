import numpy as np
import pytest
import test_native_reader

from field_math import UnresolvedMath
from grid_math import evaluate_grid
from shader_fields import ShaderFields

PROFILE='apple-m4pro-gl41-nan-sampler-v1'


def lower(body,wrap):
    source=test_native_reader.NativeReaderTest().read('PSVERSION_WARP=2\nwarp_1=`shader_body { '+body+' }\n')
    model=ShaderFields(stage='warp',frame=0,warp_reads_blur=False,frame_wrap=float(wrap))
    result=model.lower(source['sections']['warp_']['tree'])
    assert model.complete,model.unknown
    return result


@pytest.mark.parametrize('wrap,expected',[(True,0),(False,1)])
def test_zero_rgb_normalization_resolves_only_at_observed_sampler_boundary(wrap,expected):
    field=lower('float3 p=GetPixel(uv);p/=p.x+p.y+p.z;float z=dot(p,float3(1,.985,.95));ret=GetPixel((uv-.5)*z+.5);',wrap)
    inputs={'_uv':np.array([[.25,.25,0,0],[.75,.75,0,0]],dtype=np.float32)}
    calls=[]
    def sample(detail,uv):
        calls.append(uv.copy())
        if len(calls)==1:return np.zeros((len(uv),4),dtype=np.float32)
        return np.column_stack((uv,np.full(len(uv),.25),np.ones(len(uv))))
    with pytest.raises(UnresolvedMath):evaluate_grid(field,batch_shape=(2,),inputs=inputs,sample=sample)
    calls.clear()
    actual=evaluate_grid(field,batch_shape=(2,),inputs=inputs,sample=sample,coordinate_profile=PROFILE)
    np.testing.assert_allclose(actual,[[expected,expected,.25]]*2)
    assert len(calls)==2


def test_sampler_coordinate_nan_does_not_leak_into_final_color_as_a_guessed_value():
    field=lower('float z=uv.x-uv.x;float bad=z/z;float3 c=GetPixel(float2(bad,bad));ret=c+bad;',True)
    with pytest.raises(UnresolvedMath):
        evaluate_grid(field,batch_shape=(1,),inputs={'_uv':[[.25,.25,0,0]]},sample=lambda d,uv:np.ones((len(uv),4)),coordinate_profile=PROFILE)


def test_unverified_infinity_coordinate_is_still_rejected():
    field=lower('float z=uv.x-uv.x;ret=GetPixel(float2(1/z));',True)
    with pytest.raises(UnresolvedMath):
        evaluate_grid(field,batch_shape=(1,),inputs={'_uv':[[.25,.25,0,0]]},sample=lambda d,uv:np.ones((len(uv),4)),coordinate_profile=PROFILE)
