import unittest
import numpy as np
from test_shader_components import lower
from test_scene_equations import native,frames
from scene_equations import execute_scene
from test_native_reader import READER
from test_native_wave import frame,BINARY


def audio(inputs):
    return {'frames':[{**frame(),**values,'vol':1} for values in inputs]}


class BuiltinWaveTest(unittest.TestCase):
    def test_native_wave_receives_original_double_renderer_time(self):
        from builtin_wave import source_builtin_wave
        from test_native_wave import NativeWaveTest
        source=native('nWaveMode=0\nfWaveSmoothing=0\n')
        inputs=frames()[:1];inputs[0]['time']=10001.123456789
        scene=execute_scene(source,inputs,reader=READER,width=512,height=288,mesh_x=8,mesh_y=8)
        data=audio(inputs)
        predicted=source_builtin_wave(source,scene,data,binary=BINARY)['frames'][0]
        process,expected=NativeWaveTest().run_wave(0,[{**data['frames'][0],
            'wave_x':scene['frames'][0]['main']['wave_x'],'wave_y':scene['frames'][0]['main']['wave_y'],
            'wave_mystery':scene['frames'][0]['main']['wave_mystery'],'wave_a':scene['frames'][0]['main']['wave_a']}],
            wave_smoothing=0)
        self.assertEqual(process.returncode,0,process.stderr)
        points=np.asarray(expected['frames'][0]['vertex_waves'][0],dtype=np.float32)
        screen=points*np.array([.5,-.5],dtype=np.float32)+np.float32(.5)
        np.testing.assert_array_equal(predicted['positions'][0],screen)
    def test_volume_modulation_overrides_mode_opacity_factor_in_native_order(self):
        from builtin_wave import source_builtin_wave
        source=native('nWaveMode=2\nfWaveAlpha=.8\nbModWaveAlphaByVolume=1\n')
        inputs=frames()[:1];scene=execute_scene(source,inputs,reader=READER,width=512,height=288,mesh_x=8,mesh_y=8)
        wave=source_builtin_wave(source,scene,audio(inputs),binary=BINARY)['frames'][0]
        self.assertAlmostEqual(wave['rgba'][3],.8,places=6)

    def test_file_mode_flags_and_native_projection_drive_drawing_spec(self):
        from builtin_wave import source_builtin_wave
        source=native('nWaveMode=6\nbWaveThick=1\nfWaveSmoothing=0\nwave_x=.25\nwave_y=.9\n'
                      'wave_r=.5\nwave_g=.5\nwave_b=.5\nfWaveAlpha=1.17\nbMaximizeWaveColor=0\n'
                      'per_frame_1=wave_mode=0;wave_thick=0;wave_additive=1;\n')
        scene=execute_scene(source,frames()[:1],reader=READER,width=512,height=288,mesh_x=8,mesh_y=8)
        result=source_builtin_wave(source,scene,audio(frames()[:1]),binary=BINARY)
        wave=result['frames'][0]
        self.assertEqual(result['mode'],6)
        self.assertEqual(wave['draw_mode'],'strip')
        self.assertEqual(len(wave['positions'][0]),159)
        self.assertAlmostEqual(float(np.mean(np.asarray(wave['positions'][0])[:,1])),.75,places=6)
        np.testing.assert_allclose(wave['rgba'],[.5,.5,.5,1])
        self.assertFalse(wave['additive'])
        np.testing.assert_allclose(wave['copy_offsets'],[[0,0],[1/512,0],[1/512,-1/288],[0,-1/288]])

    def test_source_colour_maximization_and_mode_specific_opacity(self):
        from builtin_wave import source_builtin_wave
        source=native('nWaveMode=2\nwave_r=.2\nwave_g=.4\nwave_b=.1\nfWaveAlpha=.8\n')
        scene=execute_scene(source,frames()[:1],reader=READER,width=512,height=288,mesh_x=8,mesh_y=8)
        wave=source_builtin_wave(source,scene,audio(frames()[:1]),binary=BINARY)['frames'][0]
        np.testing.assert_allclose(wave['rgba'],[.5,1,.25,.8*.09],atol=1e-7)

    def test_frame_audio_mismatch_is_rejected(self):
        from builtin_wave import source_builtin_wave
        source=native('nWaveMode=6\n');scene=execute_scene(source,frames(),reader=READER,mesh_x=8,mesh_y=8)
        with self.assertRaisesRegex(ValueError,'schedule'):
            source_builtin_wave(source,scene,audio(frames()[:1]),binary=BINARY)


if __name__=='__main__':unittest.main()
