import unittest
import numpy as np


class LinePointsTest(unittest.TestCase):
    def test_horizontal_line_is_half_open_and_interpolates_vertex_colour(self):
        from line_points import draw_lines
        positions=np.array([[.5,1.5],[3.5,1.5]])/4
        result=draw_lines(np.zeros((4,4,4)),positions,[[1,0,0,1],[0,0,1,1]],additive=False,quantize=False)
        np.testing.assert_allclose(result[1,:3,3],1)
        np.testing.assert_allclose(result[1,1],[2/3,0,1/3,1],atol=1e-6)
        self.assertEqual(result[1,3,3],0)
        self.assertEqual(np.count_nonzero(result[...,3]),3)

    def test_connected_segments_do_not_blend_the_shared_endpoint_twice(self):
        from line_points import draw_lines
        positions=np.array([[.5,1.5],[1.5,1.5],[3.5,1.5]])/4
        result=draw_lines(np.zeros((4,4,4)),positions,[[1,0,0,.5]]*3,additive=True,quantize=False)
        np.testing.assert_allclose(result[1,:3,0],.5)

    def test_diagonal_line_and_short_segment_follow_diamond_exit_coverage(self):
        from line_points import draw_lines
        result=draw_lines(np.zeros((4,4,4)),np.array([[.5,.5],[3.5,3.5]])/4,[[1]*4]*2,additive=False,quantize=False)
        np.testing.assert_array_equal(np.argwhere(result[...,3]>0),[[0,0],[1,1],[2,2]])
        result=draw_lines(np.zeros((4,4,4)),np.array([[.5,.5],[.6,.5]])/4,[[1]*4]*2,additive=False,quantize=False)
        self.assertEqual(np.count_nonzero(result),0)

    def test_points_use_square_coverage_and_separate_draw_blending(self):
        from line_points import draw_points
        result=draw_points(np.zeros((4,4,4)),[[.5,.5]],[[1,0,0,.5]],point_size=2,additive=False,quantize=False)
        np.testing.assert_array_equal(np.argwhere(result[...,0]>0),[[1,1],[1,2],[2,1],[2,2]])
        result=draw_points(np.zeros((4,4,4)),[[.375,.375]]*2,[[1,0,0,.5]]*2,point_size=1,additive=True,quantize=False)
        self.assertEqual(result[1,1,0],1)

    def test_outside_point_is_clipped_even_if_its_square_overlaps_the_viewport(self):
        from line_points import draw_points
        result=draw_points(np.zeros((4,4,4)),[[-.01,.5]],[[1]*4],point_size=2,additive=False)
        self.assertEqual(np.count_nonzero(result),0)


if __name__=='__main__':unittest.main()
