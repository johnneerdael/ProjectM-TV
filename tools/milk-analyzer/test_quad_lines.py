import numpy as np
import pytest


def test_right_angle_miter_matches_patched_vertex_shader():
    from quad_lines import quad_line_vertices
    points=np.array([[.25,.25],[.75,.25],[.75,.75]],np.float32)
    colours=np.tile([1,0,0,1],(3,1)).astype(np.float32)
    vertices=quad_line_vertices(points,colours,width=8,height=8)
    # Reflect native GL Y after expansion; preserve gl_VertexID order. Swapping
    # the sides also swaps the triangle diagonal and changes colour interpolation.
    expected=np.array([[2,2.5],[2,1.5],[5.5,2.5],[6.5,1.5]],np.float32)
    expected[:,1]-=1/64  # Patched GLES tie bias is positive GL Y, negative top-row Y.
    np.testing.assert_allclose(vertices[0]['positions']*8,expected,atol=1e-6)


def test_quad_line_pixel_border_tie_uses_gles_bias():
    from quad_lines import draw_quad_lines
    image=np.zeros((8,8,4),np.float32)
    result=draw_quad_lines(image,[[.25,.375],[.75,.375]],[1,0,0,1],additive=False)
    np.testing.assert_array_equal(np.nonzero(result[...,0]),([2,2,2,2],[2,3,4,5]))


def test_zero_length_segments_do_not_draw_and_loops_include_closing_segment():
    from quad_lines import quad_line_vertices
    points=[[.2,.2],[.2,.2],[.8,.2],[.8,.8]]
    colours=np.tile([1,1,1,1],(4,1))
    assert len(quad_line_vertices(points,colours,width=16,height=16))==2
    assert len(quad_line_vertices(points,colours,width=16,height=16,closed=True))==3


def test_native_clip_coordinates_preserve_short_segment_cutoff():
    from quad_lines import quad_line_vertices
    clip=np.array([[0,0],[1.9e-7,0]],np.float32)
    screen=clip*np.array([.5,-.5],np.float32)+np.float32(.5)
    colours=np.tile([1,1,1,1],(2,1))
    # Screen rounding turns the native 0.00009728px segment into 0.00012207px.
    assert len(quad_line_vertices(screen,colours,width=1024,height=768))==1
    assert quad_line_vertices(screen,colours,width=1024,height=768,clip_positions=clip)==[]


def test_quad_line_forwards_explicit_triangle_grid_to_coverage():
    from quad_lines import draw_quad_lines
    image=np.zeros((4,4,4),np.float32)
    # GLES tie bias lowers the top-row centre by1/64px. Arrange the upper edge
    # just past a pixel centre; an8bit triangle grid resolves it onto that centre.
    y=(1.0005+1/64)/4
    default=draw_quad_lines(image,[[.125,y],[.875,y]],[1,0,0,1],additive=False,quantize=False)
    snapped=draw_quad_lines(image,[[.125,y],[.875,y]],[1,0,0,1],additive=False,quantize=False,raster_subpixel_bits=8)
    np.testing.assert_array_equal(np.argwhere(default[...,0]>0),[[1,0],[1,1],[1,2]])
    np.testing.assert_array_equal(np.argwhere(snapped[...,0]>0),[[0,0],[0,1],[0,2]])


@pytest.mark.parametrize('bits',[True,3,17,np.nan])
def test_quad_line_rejects_bad_triangle_grid_even_when_no_segment_draws(bits):
    from quad_lines import draw_quad_lines
    with pytest.raises(ValueError,match='raster subpixel bits'):
        draw_quad_lines(np.zeros((4,4,4)),[[.5,.5],[.5,.5]],[1]*4,additive=False,raster_subpixel_bits=bits)
