import numpy as np
import pytest
from pipeline_fields import SourcePipeline
from test_pipeline_fields import trees


def pair(alpha, warp=None, comp=None):
    from detail_pipeline import DetailPipeline
    common=dict(warp_reads_blur=False,blur_levels=0,quantize=False)
    low=SourcePipeline(warp,comp,initial_feedback=np.zeros((16,16,4),np.float32),**common)
    high=SourcePipeline(warp,comp,initial_feedback=np.zeros((32,32,4),np.float32),
                        shader_canvas_size=(16,16),**common)
    return DetailPipeline(low,high,alpha=alpha)


def test_authored_recurrence_does_not_consume_native_geometry_or_display():
    warp,comp=trees('ret=GetPixel(uv)*.5;','ret=0;')
    p=pair(0,warp,comp)
    def author(field,frame,previous):
        if frame==0:field[...,:3]=.4
        return field
    def native(field,frame,previous):
        field[...,:3]=1
        return field
    for index in range(2):
        result=p.step(authored_warp_uv=p.authored.original_uv,native_warp_uv=p.native.original_uv,
                      uniforms={},frame_wrap=1,draw_authored=author,draw_native=native)
        np.testing.assert_allclose(p.authored.feedback[...,:3],.4 if index==0 else .2)
        np.testing.assert_allclose(result.feedback[...,:3],1)
        np.testing.assert_allclose(result.display[...,:3],0)
        assert result.history['warp_evaluated'] is False


@pytest.mark.parametrize('alpha',[.5,1])
def test_positive_detail_uses_native_warp_but_authored_only_recurrence(alpha):
    warp,comp=trees('ret=GetPixel(uv);','ret=GetPixel(uv);')
    p=pair(alpha,warp,comp)
    p.authored.feedback[...,:3]=.5
    p.native.feedback[...,:3]=np.tile([0,1],16)[None,:,None]
    result=p.step(authored_warp_uv=p.authored.original_uv,native_warp_uv=p.native.original_uv,
                  uniforms={},frame_wrap=1)
    np.testing.assert_allclose(p.authored.feedback[...,:3],.5)
    np.testing.assert_allclose(result.feedback[:,::2,:3],.5-alpha*.5,atol=1e-6)
    np.testing.assert_allclose(result.feedback[:,1::2,:3],.5+alpha*.5,atol=1e-6)
    assert result.history['warp_evaluated'] is True


def test_failure_rolls_back_both_feedback_states():
    warp,comp=trees('ret=.5;','ret=tex2D(sampler_missing,uv).xyz;')
    p=pair(0,warp,comp)
    before=p.authored.feedback.copy()
    with pytest.raises(ValueError):
        p.step(authored_warp_uv=p.authored.original_uv,native_warp_uv=p.native.original_uv,
               uniforms={},frame_wrap=1)
    assert p.authored.frame==p.native.frame==0
    np.testing.assert_array_equal(p.authored.feedback,before)


def test_gain_class_switch_rebuilds_author_but_medium_high_switch_preserves_it():
    p=pair(.5)
    p.authored.feedback[...,:3]=.25
    p.native.feedback[...,:3]=1
    p.authored.frame=p.native.frame=4
    p.authored.first_frame=p.native.first_frame=False
    p.update_gain(1)
    np.testing.assert_array_equal(p.authored.feedback[...,:3],.25)
    assert p.authored.first_frame is False
    p.update_gain(0)
    np.testing.assert_array_equal(p.authored.feedback[...,:3],1)
    assert p.authored.first_frame is True
    assert p.authored.frame==4


def test_same_size_gain_rebuild_retains_uv_through_disabled_frame_and_reenable():
    warp,comp=trees('ret=GetPixel(uv);','ret=GetPixel(uv);')
    p=pair(.5,warp,comp)
    p.authored.frame=p.native.frame=4
    p.authored.first_frame=p.native.first_frame=False
    previous=p.authored.original_uv.copy()
    p.authored.motion_uv=previous.copy()
    p.authored.motion_uv_frame=3
    p.update_gain(0)
    np.testing.assert_array_equal(p.authored.motion_uv,previous)
    assert p.authored.motion_uv_frame==3
    for state in ({'mv_a':0},{'mv_a':1,'mv_x':2,'mv_y':2}):
        p.step(authored_warp_uv=p.authored.original_uv,native_warp_uv=p.native.original_uv,
               uniforms={},frame_wrap=1,motion_state=state)
    assert p.authored.motion_uv_frame==5
