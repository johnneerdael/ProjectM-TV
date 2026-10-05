import unittest
import numpy as np
import test_native_reader
from test_scene_equations import native,frames
from scene_equations import execute_scene


class SceneWarpTest(unittest.TestCase):
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
