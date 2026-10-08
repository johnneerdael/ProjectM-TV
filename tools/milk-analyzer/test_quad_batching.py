"""Allocation regression and equivalence to ordered per-quad raster draws."""
import numpy as np
import pytest
from primitives import draw_triangles
from quad_lines import draw_quad_lines,quad_line_vertices,PROFILE,RETAINED_CLIP_VIEWPORT
from motion_vectors import draw_motion_vectors,motion_geometry


def ordered_reference(target,segments,*,additive,quantize,bits):
    result=target.copy()
    for segment in segments:
        result=draw_triangles(result,segment['positions'],segment['colours'],[[0,1,2],[2,1,3]],
            additive=additive,quantize=quantize,raster_subpixel_bits=bits,
            window_positions=segment.get('window_positions'))
    return result


@pytest.mark.parametrize('closed',[False,True])
@pytest.mark.parametrize('additive',[False,True])
@pytest.mark.parametrize('quantize',[False,True])
@pytest.mark.parametrize('retained',[False,True])
def test_batch_matches_overlapping_clipped_ordered_quads(closed,additive,quantize,retained):
    rng=np.random.default_rng(919)
    target=rng.uniform(0,1,(36,64,4)).astype(np.float32);before=target.copy()
    # Backtracking/self-intersecting strip exercises alpha ordering and shared joins.
    points=rng.uniform(-.1,1.1,(24,2)).astype(np.float32)
    colour=rng.uniform(-.2,1.2,(24,4)).astype(np.float32)
    kwargs=dict(width=64,height=36,closed=closed)
    if retained:kwargs.update(clip_positions=(points-.5)*np.array([2,-2],np.float32),viewport_policy=RETAINED_CLIP_VIEWPORT)
    expected=ordered_reference(target,quad_line_vertices(points,colour,**kwargs),additive=additive,quantize=quantize,bits=8)
    kwargs.pop('width');kwargs.pop('height')
    actual=draw_quad_lines(target,points,colour,additive=additive,quantize=quantize,raster_subpixel_bits=8,**kwargs)
    np.testing.assert_array_equal(actual,expected);np.testing.assert_array_equal(target,before)


def test_strip_owns_one_triangle_framebuffer_for_many_segments(monkeypatch):
    import quad_lines
    calls=[];original=quad_lines.draw_triangles
    def counted(*args,**kwargs):calls.append(len(args[3]));return original(*args,**kwargs)
    monkeypatch.setattr(quad_lines,'draw_triangles',counted)
    points=np.array([[.1,.1],[.8,.8],[.1,.8],[.8,.1]],np.float32)
    draw_quad_lines(np.zeros((36,64,4),np.float32),points,[1,.3,.2,.4],additive=False,raster_subpixel_bits=8)
    assert calls==[6], 'one ordered triangle batch, not one full-frame copy per quad'


def test_motion_vectors_batch_independent_ends_and_preserve_pixels(monkeypatch):
    import quad_lines
    target=np.zeros((48,64,4),np.float32);before=target.copy()
    x,y=np.meshgrid((np.arange(64,dtype=np.float32)+.5)/64,(np.arange(48,dtype=np.float32)+.5)/48)
    uv=np.stack((x,y),axis=-1)
    state=dict(mv_x=8,mv_y=6,mv_dx=0,mv_dy=0,mv_l=0,mv_r=.35,mv_g=.35,mv_b=.35,mv_a=.7)
    geometry=motion_geometry(state,previous_uv=uv,width=64,height=48)
    segments=[]
    for index,line in enumerate(geometry['positions']):
        segments.extend(quad_line_vertices(line,[.35,.35,.35,.7],width=64,height=48,clip_positions=geometry['clip_positions'][index]))
    expected=ordered_reference(target,segments,additive=False,quantize=True,bits=8)
    calls=[];original=quad_lines.draw_triangles
    def counted(*args,**kwargs):calls.append(len(args[3]));return original(*args,**kwargs)
    monkeypatch.setattr(quad_lines,'draw_triangles',counted)
    actual=draw_motion_vectors(target,state,previous_uv=uv,line_rendering_profile=PROFILE,raster_subpixel_bits=8)
    np.testing.assert_array_equal(actual,expected);np.testing.assert_array_equal(target,before)
    assert calls==[2*len(segments)]


def test_skipped_motion_quads_retain_finite_framebuffer_guard():
    state=dict(mv_x=2,mv_y=2,mv_l=1,mv_a=1)
    uv=np.full((8,8,2),1e20,np.float32)
    target=np.zeros((8,8,4),np.float32);target[0,0,0]=np.nan
    with np.errstate(over='ignore',invalid='ignore'):
        with pytest.raises(ValueError,match='nonfinite primitive framebuffer'):
            draw_motion_vectors(target,state,previous_uv=uv,line_rendering_profile=PROFILE)
    # Skipped finite geometry is still a valid no-op, not an invented error.
    target[0,0,0]=0
    with np.errstate(over='ignore',invalid='ignore'):
        actual=draw_motion_vectors(target,state,previous_uv=uv,line_rendering_profile=PROFILE)
    np.testing.assert_array_equal(actual,target)
