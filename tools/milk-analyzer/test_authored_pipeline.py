"""Stage controls for authored feedback; no captured pixels enter these tests."""
import numpy as np
from pipeline_fields import SourcePipeline
from test_pipeline_fields import trees


def pipeline(warp=None, comp=None, **kwargs):
    return SourcePipeline(warp, comp, initial_feedback=np.zeros((16,32,4),np.float32),
                          warp_reads_blur=False, blur_levels=0, quantize=False, **kwargs)


def test_reported_canvas_does_not_resize_sampler_or_raster():
    warp, comp=trees('ret=float3(texsize_main.xy/32,_c7.x/32);',
                     'ret=float3(texsize_main.xy/32,_c7.x/32);')
    p=pipeline(warp,comp,shader_canvas_size=(16,8))
    result=p.step(warp_uv=p.original_uv,uniforms={},frame_wrap=1)
    assert result.feedback.shape==(16,32,4)
    np.testing.assert_array_equal(result.feedback[...,:3],np.broadcast_to([.5,.25,.5],(16,32,3)))
    np.testing.assert_array_equal(result.display[...,:3],result.feedback[...,:3])


def test_combine_runs_before_geometry_and_native_composite():
    warp, comp=trees('ret=.25;', 'ret=1-GetPixel(uv);')
    p=pipeline(warp,comp)
    calls=[]
    def combine(field):
        calls.append('combine')
        np.testing.assert_array_equal(field[...,:3],.25)
        field[...,:3]=.5
        return field
    def geometry(field,frame):
        calls.append('geometry')
        np.testing.assert_array_equal(field[...,:3],.5)
        field[...,:3]=.75
        return field
    result=p.step(warp_uv=p.original_uv,uniforms={},frame_wrap=1,
                  before_geometry=combine,draw=geometry)
    assert calls==['combine','geometry']
    np.testing.assert_allclose(result.warped[...,:3],.25)
    np.testing.assert_allclose(result.feedback[...,:3],.75)
    np.testing.assert_allclose(result.display[...,:3],.25)


def test_authored_target_can_skip_composite_entirely():
    warp, comp=trees('ret=.25;', 'ret=tex2D(sampler_missing,uv).xyz;')
    p=pipeline(warp,comp)
    result=p.step(warp_uv=p.original_uv,uniforms={},frame_wrap=1,render_composite=False)
    assert result.display is None
    np.testing.assert_allclose(result.feedback[...,:3],.25)
    assert p.frame==1


def test_authored_blur_banks_have_separate_warp_and_composite_ages():
    warp, comp=trees('ret=GetBlur1(uv);','ret=GetBlur1(uv);')
    p=pipeline(warp,comp)
    before={1:np.full((8,8,3),.25,np.float32)}
    after={1:np.full((8,8,3),.75,np.float32)}
    result=p.step(warp_uv=p.original_uv,uniforms={},frame_wrap=1,
                  supplied_blur=(before,after))
    np.testing.assert_allclose(result.warped[...,:3],.25)
    np.testing.assert_allclose(result.display[...,:3],.75)
    np.testing.assert_array_equal(p.blur[1],after[1])


def test_standard_skips_native_warp_and_retains_supplied_base():
    warp, comp=trees('ret=tex2D(sampler_missing,uv).xyz;','ret=GetPixel(uv);')
    p=pipeline(warp,comp)
    base=np.full((16,32,4),.5,np.float32)
    result=p.step(warp_uv=p.original_uv,uniforms={},frame_wrap=1,supplied_warp=base)
    np.testing.assert_array_equal(result.feedback,base)
    assert result.history['warp_evaluated'] is False
