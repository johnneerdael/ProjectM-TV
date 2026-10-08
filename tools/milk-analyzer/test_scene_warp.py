import unittest
import numpy as np
import test_native_reader
from test_scene_equations import native,frames
from scene_equations import execute_scene


class SceneWarpTest(unittest.TestCase):
    def test_same_equation_mesh_rasterizes_at_independent_output_size(self):
        from scene_warp import warp_fields
        source=native('warp=0\nfZoomExponent=2\nzoom=1.1\n'
                      'per_pixel_1=dx=x*.2;\n')
        scene=execute_scene(source,frames()[:1],reader=test_native_reader.READER,
                            width=16,height=8,mesh_x=8,mesh_y=8)
        original=warp_fields(source,scene,0,raster_subpixel_bits=8)
        result=warp_fields(source,scene,0,raster_subpixel_bits=8,output_size=(17,13))
        self.assertEqual(result['uv'].shape,(13,17,2))
        self.assertEqual(result['original_uv'].shape,(13,17,2))
        self.assertEqual(result['polar'].shape,(13,17,2))
        self.assertEqual(scene['viewport'],[16,8])
        np.testing.assert_array_equal(result['vertex_uv'],original['vertex_uv'])
        # Raster dimensions change interpolation queries, not the aspect or EEL snapshot.
        from spatial import interpolate_mesh
        x,y=np.meshgrid((np.arange(17,dtype=np.float32)+.5)/17,
                        (np.arange(13,dtype=np.float32)+.5)/13)
        query=np.stack((x,y),axis=-1)
        expected=interpolate_mesh(original['vertex_uv'],query,
                                  raster_subpixel_bits=8,viewport=(17,13))
        np.testing.assert_array_equal(result['uv'],expected)

    def test_isolated_warp_queries_use_output_raster_extent(self):
        from scene_warp import warp_fields
        source=native('warp=0\nper_pixel_1=dx=x*x*.2;\n')
        scene=execute_scene(source,frames()[:1],reader=test_native_reader.READER,
                            width=16,height=8,mesh_x=8,mesh_y=8)
        query=np.array([[.2,.3],[.8,.7]],np.float32)
        result=warp_fields(source,scene,0,query_uv=query,
                           raster_subpixel_bits=8,output_size=[17,13])
        from spatial import interpolate_mesh
        expected=interpolate_mesh(result['vertex_uv'],query,
                                  raster_subpixel_bits=8,viewport=(17,13))
        np.testing.assert_array_equal(result['uv'],expected)
        self.assertEqual(result['uv'].shape,(2,2))

    def test_warp_output_size_requires_positive_int32_dimensions(self):
        from scene_warp import warp_fields
        source=native('warp=0\n')
        scene=execute_scene(source,frames()[:1],reader=test_native_reader.READER,
                            width=8,height=8,mesh_x=8,mesh_y=8)
        for dimensions in [[],[8],(0,8),(8,-1),(True,8),(8.,8),(2**31,8)]:
            with self.subTest(dimensions=dimensions):
                with self.assertRaisesRegex(ValueError,'output size'):
                    warp_fields(source,scene,0,output_size=dimensions)

    def test_source_audio_and_pixel_equations_generate_the_uv_field(self):
        from scene_warp import warp_fields
        source=native('warp=0\nper_frame_1=q1=bass;\nper_pixel_1=dx=x*q1*.2;\n')
        scene=execute_scene(source,frames()[:1],reader=test_native_reader.READER,
                            width=16,height=16,mesh_x=8,mesh_y=8)
        result=warp_fields(source,scene,0)
        u,v=np.meshgrid((np.arange(16,dtype=np.float32)+.5)/16,
                        (np.arange(16,dtype=np.float32)+.5)/16)
        np.testing.assert_allclose(result['uv'][...,0],u*.8,atol=1e-7)
        np.testing.assert_allclose(result['uv'][...,1],v,atol=1e-7)
        self.assertEqual(result['uv'].shape,(16,16,2))
        self.assertEqual(result['polar'].shape,(16,16,2))
        self.assertFalse(result['appearance_prediction_complete'])

    def test_eel_outputs_are_stored_as_float32_before_vertex_shader_execution(self):
        from scene_warp import warp_fields
        source=native('warp=0\nper_pixel_1=zoom=1.00000005;\n')
        scene=execute_scene(source,frames()[:1],reader=test_native_reader.READER,
                            width=8,height=8,mesh_x=8,mesh_y=8)
        result=warp_fields(source,scene,0)
        u,v=np.meshgrid((np.arange(8,dtype=np.float32)+.5)/8,
                        (np.arange(8,dtype=np.float32)+.5)/8)
        np.testing.assert_array_equal(result['uv'],np.stack((u,v),axis=-1))

    def test_invalid_source_domains_remain_unresolved(self):
        from scene_warp import warp_fields
        source=native('fWarpScale=0\n')
        scene=execute_scene(source,frames()[:1],reader=test_native_reader.READER,mesh_x=8,mesh_y=8)
        with self.assertRaisesRegex(ValueError,'divisor'):warp_fields(source,scene,0)


if __name__=='__main__':unittest.main()
