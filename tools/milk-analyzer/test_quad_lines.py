import numpy as np


def test_right_angle_miter_matches_patched_vertex_shader():
    from quad_lines import quad_line_vertices
    points=np.array([[.25,.25],[.75,.25],[.75,.75]],np.float32)
    colours=np.tile([1,0,0,1],(3,1)).astype(np.float32)
    vertices=quad_line_vertices(points,colours,width=8,height=8)
    expected=np.array([[2,1.5],[2,2.5],[6.5,1.5],[5.5,2.5]],np.float32)
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
