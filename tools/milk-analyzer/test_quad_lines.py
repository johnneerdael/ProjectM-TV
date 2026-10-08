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
def test_retained_clip_viewport_does_not_manufacture_subpixel_tie():
    import numpy as np
    from quad_lines import quad_line_vertices
    clip=np.array([[-.12099417299032211,.5047906041145325],
                   [-.12073306739330292,.5052019953727722],
                   [-.12051361054182053,.5055466890335083],
                   [-.12031729519367218,.5058546662330627]],np.float32)
    screen=clip*np.array([.5,-.5],np.float32)+np.float32(.5)
    old=quad_line_vertices(screen,[1,1,1,.625],width=256,height=144,clip_positions=clip)
    retained=quad_line_vertices(screen,[1,1,1,.625],width=256,height=144,
        clip_positions=clip,viewport_policy='retained-clip-window-v1')
    assert float(old[1]['positions'][2,0])*256==112.822265625
    assert retained[1]['window_positions'][2,0]==112.82226943969727
    assert np.rint(retained[1]['window_positions'][2,0]*256)/256==112.82421875
    np.testing.assert_array_equal(old[1]['positions'],retained[1]['positions'])


def test_explicit_window_vertices_drive_grid_coverage_and_require_finite_matching_coordinates():
    import numpy as np
    import pytest
    from primitives import draw_triangles
    field=np.zeros((2,2,4),np.float32)
    points=np.zeros((3,2),np.float32)
    colour=np.ones((3,4),np.float32)
    window=np.array([[.1,.1],[1.9,.1],[.1,1.9]],np.float64)
    result=draw_triangles(field,points,colour,[[0,1,2]],additive=False,
        raster_subpixel_bits=8,window_positions=window)
    np.testing.assert_array_equal(result[0,0],[1,1,1,1])
    with pytest.raises(ValueError,match='window'):
        draw_triangles(field,points,colour,[[0,1,2]],additive=False,
            raster_subpixel_bits=8,window_positions=np.full((3,2),np.nan))
    with pytest.raises(ValueError,match='window'):
        draw_triangles(field,points,colour,[[0,1,2]],additive=False,window_positions=window)


def test_retained_viewport_requires_grid_even_when_strip_is_degenerate():
    import numpy as np
    import pytest
    from quad_lines import draw_quad_lines
    with pytest.raises(ValueError,match='grid'):
        draw_quad_lines(np.zeros((2,2,4),np.float32),[[.5,.5],[.5,.5]],
            [1,1,1,1],additive=False,clip_positions=[[0,0],[0,0]],
            viewport_policy='retained-clip-window-v1')
