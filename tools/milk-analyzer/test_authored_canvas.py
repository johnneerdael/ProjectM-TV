"""Analytical authored-canvas controls independent of renderer output."""
import numpy as np
import pytest


def test_integer_canvas_selection_preserves_native_dimensions_and_fallback():
    from authored_canvas import select_canvas
    assert select_canvas(3840,2160,1280,720)==(1280,720,3)
    assert select_canvas(1920,1080,1280,720)==(960,540,2)
    assert select_canvas(1280,720,1280,720) is None
    assert select_canvas(3841,2160,1280,720) is None
    assert select_canvas(3840,2160,0,0) is None


def test_block_downsample_and_standard_never_require_native_warp():
    from authored_canvas import block_downsample,combine_detail
    high=np.array([[0,.25],[.5,1]],np.float32)
    rgba=np.repeat(high[...,None],4,axis=-1)
    low=block_downsample(rgba,2,quantize=False)
    np.testing.assert_array_equal(low,np.full((1,1,4),.4375,np.float32))
    standard=combine_detail(low,None,alpha=0,output_size=(2,2),quantize=False)
    np.testing.assert_array_equal(standard,np.full((2,2,4),.4375,np.float32))


def test_centered_residual_reuses_one_channel_gain_per_block():
    from authored_canvas import combine_detail
    low=np.full((1,1,4),.5,np.float32)
    high=np.repeat(np.array([[0,1],[0,1]],np.float32)[...,None],4,axis=-1)
    result=combine_detail(low,high,alpha=.5,output_size=(2,2),quantize=False)
    expected=np.repeat(np.array([[.25,.75],[.25,.75]],np.float32)[...,None],4,axis=-1)
    np.testing.assert_allclose(result,expected,atol=2e-7)
    np.testing.assert_allclose(result.mean((0,1)),low[0,0],atol=2e-7)


def test_headroom_limit_keeps_block_mean_and_avoids_individual_clamping_bias():
    from authored_canvas import combine_detail
    low=np.full((1,1,4),.9,np.float32)
    high=np.repeat(np.array([[0,1],[0,1]],np.float32)[...,None],4,axis=-1)
    result=combine_detail(low,high,alpha=1,output_size=(2,2),quantize=False)
    np.testing.assert_allclose(result[...,0],[[.8,1],[.8,1]],atol=2e-7)
    np.testing.assert_allclose(result.mean((0,1)),low[0,0],atol=2e-7)


def test_invalid_values_and_noninteger_canvas_ratios_remain_rejected():
    from authored_canvas import combine_detail
    low=np.full((2,2,4),.5,np.float32)
    with pytest.raises(ValueError,match='ratio'):
        combine_detail(low,None,alpha=0,output_size=(5,4))
    with pytest.raises(ValueError,match='native warp'):
        combine_detail(low,None,alpha=.5,output_size=(4,4))
    with pytest.raises(ValueError,match='finite'):
        combine_detail(np.full((2,2,4),np.nan),None,alpha=0,output_size=(4,4))


def test_native_trails_gate_uses_physical_height_and_preserves_init_canvas():
    from authored_canvas import detail_configuration
    value=detail_configuration(native_size=(1920,1080),physical_size=(3840,2160),trails_level=1)
    assert value['alpha']==.5
    assert value['authored_size']==(960,540)
    assert value['initial_shader_canvas']==(1280,720)
    assert value['scale']==2
    disabled=detail_configuration(native_size=(3840,2160),physical_size=(1920,1080),trails_level=2)
    assert disabled['alpha']==-1
    assert disabled['authored_size'] is None
    assert disabled['reference_size']==(1024,768)


def test_true_4k_standard_medium_high_have_same_authored_canvas():
    from authored_canvas import detail_configuration
    for level,alpha in enumerate((0,.5,1)):
        value=detail_configuration(native_size=(3840,2160),physical_size=(3840,2160),trails_level=level)
        assert value['authored_size']==value['initial_shader_canvas']==(1280,720)
        assert value['alpha']==alpha and value['scale']==3


def test_detail_fallback_is_explicit_and_does_not_fabricate_an_allocated_canvas():
    from authored_canvas import detail_configuration
    value=detail_configuration(native_size=(3841,2160),physical_size=(3841,2160),trails_level=0)
    assert value['authored_size'] is None
    assert value['selection_status']=='no-integer-canvas'
    with pytest.raises(ValueError,match='trails'):
        detail_configuration(native_size=(3840,2160),physical_size=(3840,2160),trails_level=3)
