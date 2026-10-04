import unittest
import numpy as np
import test_native_reader
from test_scene_equations import native,frames
from scene_equations import execute_scene


class ShaderUniformsTest(unittest.TestCase):
    def test_shader_inputs_use_render_state_and_saved_frame_q_not_pixel_writes(self):
        from shader_uniforms import source_uniforms
        source=native('per_frame_1=time=999;bass=99;q1=.7;q32=.9;\n'
                      'per_pixel_1=q1=123;\n')
        inputs=frames()[:1];inputs[0]['time']=10001.25
        scene=execute_scene(source,inputs,reader=test_native_reader.READER,mesh_x=8,mesh_y=8)
        uniforms=source_uniforms(scene,0)
        self.assertEqual(uniforms['_c2'],[1.25,30,1,0])
        self.assertEqual(uniforms['_c3'][0],1)
        self.assertEqual(uniforms['_c3'][3],float(np.float32(3)*np.float32(.333)))
        self.assertEqual(uniforms['_qa'][0],float(np.float32(.7)))
        self.assertEqual(uniforms['_qh'][3],float(np.float32(.9)))
        self.assertNotIn('rand_frame',uniforms)

    def test_source_equations_coordinates_and_uniforms_drive_shader_feedback(self):
        from shader_uniforms import source_uniforms
        from scene_warp import warp_fields
        from pipeline_fields import SourcePipeline
        source=native('PSVERSION_WARP=2\nPSVERSION_COMP=2\nwarp=0\n'
                      'per_frame_1=q1=bass*.5;\nper_pixel_1=dx=x*.2;\n'
                      'warp_1=`shader_body {ret=GetPixel(uv)*q1;}\n'
                      'comp_1=`shader_body {ret=GetPixel(uv);}\n')
        scene=execute_scene(source,frames(),reader=test_native_reader.READER,
                            width=16,height=16,mesh_x=8,mesh_y=8)
        initial=np.ones((16,16,4),dtype=np.float32)
        pipeline=SourcePipeline(source['sections']['warp_']['tree'],source['sections']['comp_']['tree'],
                                initial_feedback=initial,warp_reads_blur=False,blur_levels=0,quantize=False)
        for index,expected in enumerate([.5,.25]):
            mesh=warp_fields(source,scene,index)
            result=pipeline.step(warp_uv=mesh['uv'],warp_polar=mesh['polar'],
                                 uniforms=source_uniforms(scene,index),frame_wrap=scene['frames'][index]['main']['wrap'])
            np.testing.assert_allclose(result.feedback[...,:3],expected,atol=1e-6)


if __name__=='__main__':unittest.main()
