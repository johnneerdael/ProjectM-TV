import unittest
import importlib
import numpy as np


class SpatialTest(unittest.TestCase):
    def test_native_aspect_restore_multiplies_the_stored_float32_reciprocal(self):
        spatial=importlib.import_module('spatial')
        aspect=np.float32(.5625);dy=np.float32(.1412)
        expected=(np.float32(.5)-dy-np.float32(.5))*(np.float32(1)/aspect)+np.float32(.5)
        result=spatial.warp_vertex_uv([[0,0]],aspect_y=aspect,dy=dy)
        self.assertEqual(result[0,1],expected)

    def test_volume_sampling_preserves_gl_xyz_layout_and_trilinear_centres(self):
        spatial=importlib.import_module('spatial')
        volume=np.arange(8,dtype=np.float32).reshape(2,2,2)
        points=[[.25,.25,.25],[.75,.75,.75],[.5,.5,.5]]
        np.testing.assert_allclose(spatial.sample3d(volume,points,wrap=False,linear=True),[0,7,3.5])

    def test_volume_sampling_wraps_all_three_axes(self):
        spatial=importlib.import_module('spatial')
        volume=np.arange(8,dtype=np.float32).reshape(2,2,2)
        np.testing.assert_allclose(spatial.sample3d(volume,[[1.25,-.25,1.75]],wrap=True,linear=False),[6])
        np.testing.assert_allclose(spatial.sample3d(volume,[[1.25,-.25,1.75]],wrap=False,linear=False),[5])

    def test_identity_vertex_warp_cancels_widescreen_aspect(self):
        spatial=importlib.import_module('spatial')
        positions=np.array([[-1,-1],[0,0],[1,1]],dtype=np.float32)
        actual=spatial.warp_vertex_uv(positions,aspect_x=1,aspect_y=.5625)
        np.testing.assert_allclose(actual,[[0,0],[.5,.5],[1,1]],atol=1e-7)
        self.assertEqual(actual.dtype,np.float32)

    def test_stretch_then_rotation_then_translation_keeps_native_order(self):
        spatial=importlib.import_module('spatial')
        # Initial (.75,.5), stretch (.5,1) -> (1,.5), rotate -> (.5,1),
        # translate (.1,.2) -> (.4,.8). Reversing the operations differs.
        actual=spatial.warp_vertex_uv([[.5,0]],sx=.5,sy=1,rot=np.pi/2,dx=.1,dy=.2)
        np.testing.assert_allclose(actual,[[.4,.8]],atol=1e-6)

    def test_radial_zoom_uses_nested_exponent_and_preserves_unknown_domains(self):
        spatial=importlib.import_module('spatial')
        # At radius1, effective zoom is 2**(3**1)=8.
        actual=spatial.warp_vertex_uv([[1,0]],zoom=2,zoomexp=3)
        np.testing.assert_allclose(actual,[[.5625,.5]],atol=1e-7)
        with self.assertRaises(ValueError):spatial.warp_vertex_uv([[0,0]],sx=0)
        with self.assertRaises(ValueError):spatial.warp_vertex_uv([[0,0]],warp_scale=0)

    def test_mesh_inputs_preserve_native_angle_sign_for_equations(self):
        spatial=importlib.import_module('spatial')
        mesh=spatial.mesh_inputs(8,8,aspect_x=1,aspect_y=.5)
        self.assertEqual(mesh['position'].shape,(9,9,2))
        self.assertEqual(mesh['angle'][4,4],0)
        self.assertAlmostEqual(float(mesh['equation_ang'][8,4]),-np.pi/2,places=6)
        self.assertAlmostEqual(float(mesh['equation_y'][8,4]),.75)

    def test_mesh_interpolates_native_triangles_not_bilinear_patch(self):
        spatial=importlib.import_module('spatial')
        values=np.array([[0,0],[0,1]],dtype=np.float32)
        # The native diagonal joins top-right to bottom-left. First triangle
        # excludes bottom-right1; a bilinear interpolator would give .0625.
        np.testing.assert_allclose(spatial.interpolate_mesh(values,[[.25,.25],[.75,.75]]),[0,.5])

    def test_texture_linear_sampling_uses_texel_centres_and_wraps_edge_neighbors(self):
        spatial=importlib.import_module('spatial')
        field=np.array([[0,1]],dtype=np.float32)
        uv=np.array([[.25,.5],[.75,.5],[0,.5],[1.25,.5]],dtype=np.float32)
        np.testing.assert_allclose(spatial.sample2d(field,uv,wrap=True,linear=True,origin='top'),[0,1,.5,0])
        np.testing.assert_allclose(spatial.sample2d(field,uv,wrap=False,linear=True,origin='top'),[0,1,0,1])

    def test_sampling_origin_is_explicit(self):
        spatial=importlib.import_module('spatial')
        field=np.array([[1],[0]],dtype=np.float32)
        self.assertEqual(spatial.sample2d(field,[[.5,.25]],wrap=False,linear=False,origin='top')[0],1)
        self.assertEqual(spatial.sample2d(field,[[.5,.25]],wrap=False,linear=False,origin='bottom')[0],0)


if __name__=='__main__':unittest.main()
