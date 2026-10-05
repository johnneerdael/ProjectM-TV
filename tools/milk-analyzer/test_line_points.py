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

    def test_explicit_eight_bit_point_centres_snap_only_near_window_boundaries(self):
        from line_points import draw_points
        # 1/256 px snapping changes +/- .001, while +/- .008 stays across the boundary.
        for delta, expected in [(-.001, [2,1]), (.001, [2,1]),
                                (-.008, [1,1]), (.008, [2,2])]:
            with self.subTest(delta=delta):
                positions=np.array([[2+delta,2+delta]])/4
                result=draw_points(np.zeros((4,4,4)),positions,[1,0,0,1],
                                   additive=False,quantize=False,subpixel_bits=8)
                np.testing.assert_array_equal(np.argwhere(result[...,0]>0),[expected])

    def test_default_point_centres_preserve_canonical_unsnapped_coverage(self):
        from line_points import draw_points
        for delta, expected in [(-.001, [1,1]), (.001, [2,2])]:
            with self.subTest(delta=delta):
                positions=np.array([[2+delta,2+delta]])/4
                result=draw_points(np.zeros((4,4,4)),positions,[1,0,0,1],
                                   additive=False,quantize=False)
                np.testing.assert_array_equal(np.argwhere(result[...,0]>0),[expected])

    def test_point_precision_is_an_explicit_parameter_including_the_upper_bound(self):
        from line_points import draw_points
        for bits, expected in [(4,[2,1]),(16,[2,2])]:
            with self.subTest(bits=bits):
                result=draw_points(np.zeros((4,4,4)),[[2.008/4,2.008/4]],[1,0,0,1],
                                   additive=False,quantize=False,subpixel_bits=bits)
                np.testing.assert_array_equal(np.argwhere(result[...,0]>0),[expected])

    def test_explicit_zero_bit_point_centres_and_halfway_rounding_are_mathematical_inputs(self):
        from line_points import draw_points
        result=draw_points(np.zeros((4,4,4)),[[2.25/4,1.75/4]],[1,0,0,1],
                           additive=False,quantize=False,subpixel_bits=0)
        np.testing.assert_array_equal(np.argwhere(result[...,0]>0),[[2,1]])
        # np.rint rounds exact halfway centres to even. Native halfway ties remain unverified.
        result=draw_points(np.zeros((4,4,4)),[[2.5/4,1.5/4]],[1,0,0,1],
                           additive=False,quantize=False,subpixel_bits=0)
        np.testing.assert_array_equal(np.argwhere(result[...,0]>0),[[2,1]])

    def test_point_subpixel_bits_reject_non_integer_boolean_and_out_of_range_settings(self):
        from line_points import draw_points
        for bits in [True,False,-1,17,1.5,8.0,np.nan,np.inf,'8']:
            with self.subTest(bits=bits),self.assertRaisesRegex(ValueError,'subpixel bits'):
                draw_points(np.zeros((4,4,4)),[[.5,.5]],[1]*4,
                            additive=False,subpixel_bits=bits)

    def test_point_centres_are_clipped_before_subpixel_rounding(self):
        from line_points import draw_points
        result=draw_points(np.zeros((4,4,4)),[[-.00001,.5]],[1]*4,
                           point_size=2,additive=False,subpixel_bits=0)
        self.assertEqual(np.count_nonzero(result),0)


if __name__=='__main__':unittest.main()
