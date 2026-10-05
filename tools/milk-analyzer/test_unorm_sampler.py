import json
from pathlib import Path
import numpy as np
import pytest


def test_recorded_float_readbacks_match_fixed_sampler_arithmetic():
    from unorm_sampler import sample_unorm8
    proof=json.loads((Path(__file__).parent/'fixtures/swiftshader-sampler-learning-2026-10-04.json').read_text())
    for case in proof['cases']:
        width,height=case['dimensions'];texture=np.zeros((height,width,4),dtype=np.float32)
        texture[...,3]=1;texture[-1,0,0]=1
        for row in case['readback']['rows']:
            expected=np.array(row['rgba'],dtype=np.float32)
            np.testing.assert_array_equal(sample_unorm8(texture,row['uv'],wrap=False,linear=True,origin='bottom'),expected)


def test_sampler_requires_actual_unorm_storage_and_declared_origin():
    from unorm_sampler import sample_unorm8
    for texture,origin in [(np.full((2,2,4),.123),'top'),(np.zeros((2,2,4)),'guess')]:
        with pytest.raises(ValueError):sample_unorm8(texture,[.25,.25],wrap=False,linear=True,origin=origin)


def test_repeat_and_nearest_addressing_preserve_physical_texels():
    from unorm_sampler import sample_unorm8
    texture=np.array([[[1,0,0,1],[0,1,0,1]],[[0,0,1,1],[1,1,1,1]]],dtype=np.float32)
    np.testing.assert_array_equal(sample_unorm8(texture,[1.25,-.75],wrap=True,linear=False,origin='top'),[1,0,0,1])
    np.testing.assert_array_equal(sample_unorm8(texture,[.25,.25],wrap=False,linear=False,origin='bottom'),[0,0,1,1])


def test_pipeline_profile_is_explicit_and_requires_quantized_feedback():
    from pipeline_fields import SourcePipeline
    with pytest.raises(ValueError):SourcePipeline(None,None,initial_feedback=np.zeros((2,2,4)),
        warp_reads_blur=False,blur_levels=0,quantize=False,main_sampling_profile='swiftshader-unorm8-fixed16-v1')
    with pytest.raises(ValueError):SourcePipeline(None,None,initial_feedback=np.zeros((2,2,4)),
        warp_reads_blur=False,blur_levels=0,main_sampling_profile='guess')


@pytest.mark.parametrize('origin',['top','bottom'])
@pytest.mark.parametrize('linear',[False,True])
def test_near_zero_negative_repeat_coordinates_stay_inside_the_16bit_domain(origin,linear):
    from unorm_sampler import sample_unorm8
    texture=np.array([[[1,0,0,1],[0,1,0,1]],[[0,0,1,1],[1,1,1,1]]],dtype=np.float32)
    actual=sample_unorm8(texture,[[-1e-9,.25],[.25,-1e-9]],wrap=True,linear=linear,origin=origin)
    expected=sample_unorm8(texture,[[0,.25],[.25,0]],wrap=True,linear=linear,origin=origin)
    np.testing.assert_array_equal(actual,expected)
