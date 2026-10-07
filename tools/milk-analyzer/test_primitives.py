import unittest
import importlib
import numpy as np


class PrimitivesTest(unittest.TestCase):
    def test_native_border_sizes_are_clip_space_half_widths_and_inner_follows_outer(self):
        module=importlib.import_module('primitives')
        values={'ob_size':.25,'ib_size':.25,'ob_r':1,'ob_g':0,'ob_b':0,'ob_a':.5,
                'ib_r':0,'ib_g':1,'ib_b':0,'ib_a':1}
        result=module.draw_borders(np.zeros((16,16,4)),values,quantize=False)
        np.testing.assert_allclose(result[8,0],[.5,0,0,.25],atol=1e-6)
        np.testing.assert_allclose(result[8,2],[0,1,0,1],atol=1e-6)
        np.testing.assert_allclose(result[8,4],[0,0,0,0],atol=1e-6)
        np.testing.assert_allclose(result[0,0],[.5,0,0,.25],atol=1e-6)

    def test_omitted_shape_colours_use_native_red_centre_and_transparent_green_edge(self):
        module=importlib.import_module('primitives')
        fan=module.shape_fan({},aspect_y=1)
        np.testing.assert_allclose(fan['colours'][0],[1,0,0,1],atol=2e-7)
        np.testing.assert_allclose(fan['colours'][1:],np.tile([0,1,0,0],(len(fan['colours'])-1,1)),atol=2e-7)

    def test_equation_outputs_draw_a_visible_fan_into_feedback(self):
        module=importlib.import_module('primitives')
        values={'x':.5,'y':.5,'rad':1,'sides':4,'r':1,'g':0,'b':0,'a':1,
                'r2':1,'g2':0,'b2':0,'a2':1,'border_a':0,'textured':0,'additive':0}
        result=module.draw_shape(np.zeros((16,16,4)),values,aspect_y=1,quantize=False)
        self.assertGreater(result[8,8,0],.99)
        self.assertEqual(result[0,0,0],0)

    def test_missing_required_shape_texture_is_not_silently_untextured(self):
        module=importlib.import_module('primitives')
        with self.assertRaisesRegex(ValueError,'texture'):
            module.draw_shape(np.zeros((16,16,4)),{'textured':1},aspect_y=1,quantize=False)

    def test_native_alpha_blending_uses_source_alpha_on_all_four_channels(self):
        module=importlib.import_module('primitives')
        destination=np.array([0,0,1,1],dtype=np.float32)
        source=np.array([1,0,0,.5],dtype=np.float32)
        np.testing.assert_allclose(module.blend_rgba(destination,source,additive=False,quantize=False),[.5,0,.5,.75])
        np.testing.assert_allclose(module.blend_rgba(destination,source,additive=True,quantize=False),[.5,0,1,1])

    def test_colour_wrap_matches_native_float_modulo_instead_of_clamping(self):
        module=importlib.import_module('primitives')
        values=module.colour_modulo([1,2,-1])
        np.testing.assert_allclose(values,[1,254/255,1/255],atol=2e-7)

    def test_shape_fan_preserves_native_half_radius_aspect_and_projection(self):
        module=importlib.import_module('primitives')
        fan=module.shape_fan({'x':.5,'y':.75,'rad':.2,'ang':0,'sides':4,
                             'r':1,'g':0,'b':0,'a':1,'r2':0,'g2':0,'b2':1,'a2':0},aspect_y=.5)
        np.testing.assert_allclose(fan['positions'][0],[.5,.25])
        self.assertAlmostEqual(float(fan['positions'][1,0]),.5+.2*np.cos(np.pi/4)*.5/2,places=6)
        self.assertAlmostEqual(float(fan['positions'][1,1]),.25+.2*np.sin(np.pi/4)/2,places=6)
        np.testing.assert_allclose(fan['positions'][-1],fan['positions'][1])

    def test_triangle_colours_interpolate_at_pixel_centres_and_blend(self):
        module=importlib.import_module('primitives')
        target=np.zeros((2,2,4),dtype=np.float32)
        positions=np.array([[0,0],[1,0],[0,1]],dtype=np.float32)
        colours=np.array([[1,0,0,1],[0,1,0,1],[0,0,1,1]],dtype=np.float32)
        result=module.draw_triangles(target,positions,colours,[[0,1,2]],additive=False,quantize=False)
        np.testing.assert_allclose(result[0,0],[.5,.25,.25,1],atol=1e-6)
        np.testing.assert_allclose(result[1,1],[0,0,0,0])

    def test_shared_triangle_edges_do_not_blend_the_same_pixel_twice(self):
        module=importlib.import_module('primitives')
        positions=np.array([[0,0],[1,0],[0,1],[1,1]],dtype=np.float32)
        colours=np.tile([1,0,0,.5],(4,1)).astype(np.float32)
        result=module.draw_triangles(np.zeros((4,4,4)),positions,colours,[[0,1,2],[1,3,2]],additive=True,quantize=False)
        np.testing.assert_allclose(result[...,0],.5,atol=1e-6)

    def test_texture_modulates_fill_colour_and_alpha(self):
        module=importlib.import_module('primitives')
        positions=np.array([[0,0],[1,0],[0,1]],dtype=np.float32)
        colours=np.tile([1,1,1,1],(3,1)).astype(np.float32)
        def texture(uv):return np.tile([.2,.4,.6,.5],(len(uv),1))
        result=module.draw_triangles(np.zeros((2,2,4)),positions,colours,[[0,1,2]],additive=False,
                                     quantize=False,texture_uv=positions,texture_sample=texture)
        np.testing.assert_allclose(result[0,0],[.1,.2,.3,.25],atol=1e-6)

    def test_explicit_triangle_grid_changes_boundary_coverage_without_changing_default(self):
        from primitives import draw_triangles
        positions=np.array([[.5005,.5005],[3.4985,.5005],[.5005,3.4985]],np.float32)/4
        colours=np.tile([1,0,0,1],(3,1)).astype(np.float32)
        default=draw_triangles(np.zeros((4,4,4)),positions,colours,[[0,1,2]],additive=False,quantize=False)
        np.testing.assert_array_equal(np.argwhere(default[...,0]>0),[[1,1]])
        snapped=draw_triangles(np.zeros((4,4,4)),positions,colours,[[0,1,2]],additive=False,quantize=False,raster_subpixel_bits=8)
        np.testing.assert_array_equal(np.argwhere(snapped[...,0]>0),[[0,0],[0,1],[0,2],[1,0],[1,1],[2,0]])

    def test_snapped_shared_edges_preserve_once_only_blending_and_vertex_colours(self):
        from primitives import draw_triangles
        positions=np.array([[.5005,.5005],[3.4995,.5005],[.5005,3.4995],[3.4995,3.4995]],np.float32)/4
        colours=np.array([[0,0,0,.5],[1,0,0,.5],[0,1,0,.5],[1,1,0,.5]],np.float32)
        result=draw_triangles(np.zeros((4,4,4)),positions,colours,[[0,1,2],[1,3,2]],additive=True,quantize=False,raster_subpixel_bits=8)
        np.testing.assert_allclose(result[:3,:3,3],.25,atol=1e-7)
        np.testing.assert_allclose(result[1,1],[1/6,1/6,0,.25],atol=1e-7)
        self.assertEqual(np.count_nonzero(result[3]),0)
        self.assertEqual(np.count_nonzero(result[:,3]),0)

    def test_snapping_geometry_does_not_snap_texture_attributes(self):
        from primitives import draw_triangles
        positions=np.array([[.5005,.5005],[3.4995,.5005],[.5005,3.4995]],np.float32)/4
        uv=np.array([[.2,.3],[.7,.3],[.2,.8]],np.float32);seen=[]
        def texture(coordinates):
            seen.append(coordinates.copy())
            return np.column_stack((coordinates,np.zeros(len(coordinates)),np.ones(len(coordinates))))
        result=draw_triangles(np.zeros((4,4,4)),positions,np.ones((3,4)),[[0,1,2]],additive=False,quantize=False,
                              raster_subpixel_bits=8,texture_uv=uv,texture_sample=texture)
        np.testing.assert_allclose(seen[0][0],uv[0],atol=1e-8)
        np.testing.assert_allclose(result[0,0],[.2,.3,0,1],atol=1e-7)

    def test_snapped_offscreen_vertices_still_cover_visible_pixels(self):
        from primitives import draw_triangles
        positions=np.array([[-.25,-.25],[1.25,-.25],[-.25,1.25],[1.25,1.25]],np.float32)
        result=draw_triangles(np.zeros((4,4,4)),positions,np.tile([1,0,0,.5],(4,1)),[[0,1,2],[1,3,2]],
                              additive=True,quantize=False,raster_subpixel_bits=8)
        np.testing.assert_allclose(result[...,0],.5,atol=1e-7)

    def test_triangle_grid_rejects_malformed_precision_settings(self):
        from primitives import draw_triangles
        for bits in [True,False,3,17,8.0,np.nan,np.inf,'8']:
            with self.subTest(bits=bits),self.assertRaisesRegex(ValueError,'raster subpixel bits'):
                draw_triangles(np.zeros((4,4,4)),[[0,0],[1,0],[0,1]],np.ones((3,4)),[[0,1,2]],
                               additive=False,raster_subpixel_bits=bits)

    def test_triangle_grid_keeps_exact_window_boundary_on_non_power_of_two_viewports(self):
        from primitives import draw_triangles
        positions=np.array([[.5005,.5005],[10.4995,.5005],[.5005,6.4995]],np.float32)/[11,7]
        result=draw_triangles(np.zeros((7,11,4)),positions,np.tile([1,0,0,1],(3,1)),[[0,1,2]],
                              additive=False,quantize=False,raster_subpixel_bits=8)
        np.testing.assert_array_equal(result[0,0],[1,0,0,1])

    def test_shape_grid_snap_reaches_its_fill_coverage(self):
        from primitives import draw_shape
        values=dict(x=.5,y=.5,rad=1.4995/(2*np.sqrt(.5)),sides=4,r=1,g=0,b=0,a=1,
                    r2=1,g2=0,b2=0,a2=1,border_a=0)
        default=draw_shape(np.zeros((4,4,4)),values,aspect_y=1,quantize=False)
        self.assertEqual(np.count_nonzero(default[...,0]),4)
        snapped=draw_shape(np.zeros((4,4,4)),values,aspect_y=1,quantize=False,raster_subpixel_bits=8)
        np.testing.assert_array_equal(np.argwhere(snapped[...,0]>0),[[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]])

    def test_border_grid_snap_preserves_inner_edge_ownership(self):
        from primitives import draw_borders
        values=dict(ob_size=.25025,ob_r=1,ob_g=0,ob_b=0,ob_a=1,ib_a=0)
        default=draw_borders(np.zeros((4,4,4)),values,quantize=False)
        self.assertGreater(default[1,0,0],0)
        snapped=draw_borders(np.zeros((4,4,4)),values,quantize=False,raster_subpixel_bits=8)
        self.assertEqual(snapped[1,0,0],0)
        self.assertGreater(snapped[1,3,0],0)


if __name__=='__main__':unittest.main()


def test_corrected_shape_centres_cover_tiny_authored_integer_pixel():
    from primitives import draw_shape
    target=np.zeros((144,256,4),np.float32)
    values={'x':.5,'y':.5,'rad':.002,'sides':4,'r':1,'g':0,'b':0,'a':1,'r2':1,'g2':0,'b2':0,'a2':1}
    before=draw_shape(target,values,aspect_y=144/256,raster_subpixel_bits=8)
    after=draw_shape(target,values,aspect_y=144/256,raster_subpixel_bits=8,
                     centre_policy='projectmtv-core-2.3.22-shape-pixel-centres-v1')
    assert np.count_nonzero(before[...,0])==0
    assert np.count_nonzero(after[...,0])==1
    assert after[72,128,0]==1
