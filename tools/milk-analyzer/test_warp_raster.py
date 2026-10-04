import numpy as np
import pytest
from spatial import interpolate_mesh
from test_motion_pipeline import pipeline


def test_warp_interpolation_uses_window_raster_positions_and_original_attributes():
    x,y=np.meshgrid(np.arange(4,dtype=np.float32)/3,np.arange(4,dtype=np.float32)/3)
    values=np.stack((x,y),-1);query=np.array([[.35,.5]],dtype=np.float32)
    result=interpolate_mesh(values,query,raster_subpixel_bits=4,viewport=(10,10))
    expected=np.float32(1/3)+(np.float32(2/3)-np.float32(1/3))*(.35-.33125)/(.66875-.33125)
    np.testing.assert_allclose(result,[[expected,.5]],atol=1e-7)
    assert abs(result[0,0]-.35)>1e-3


@pytest.mark.parametrize('bits,viewport',[(True,(10,10)),(3,(10,10)),(4,None),(4,(0,10))])
def test_warp_raster_profile_requires_explicit_valid_dimensions(bits,viewport):
    with pytest.raises(ValueError):
        interpolate_mesh(np.zeros((2,2,2)),[[.5,.5]],raster_subpixel_bits=bits,viewport=viewport)


def test_pipeline_original_uv_channel_can_follow_actual_warp_raster_interpolation():
    from test_pipeline_fields import trees
    warp,comp=trees('ret=float3(uv_orig,0);','ret=.5;')
    p=pipeline(warp,comp);original=p.original_uv+[.01,.02]
    result=p.step(warp_uv=p.original_uv,warp_original_uv=original,uniforms={},frame_wrap=1)
    np.testing.assert_allclose(result.feedback[...,:2],np.clip(original,0,1),atol=1e-7)
