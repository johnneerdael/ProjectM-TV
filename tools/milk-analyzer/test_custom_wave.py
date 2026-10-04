import unittest
import numpy as np
from test_custom_wave_scene import native,audio_frames,READER,execute_scene


class CustomWaveTest(unittest.TestCase):
    def test_native_projection_colour_wrap_and_smoothing_use_point_equations(self):
        from custom_wave import source_custom_waves
        source=native('wavecode_0_enabled=1\nwavecode_0_samples=2\nwavecode_0_bDrawThick=1\n'
                      'wave_0_per_point1=x=sample;y=.75;r=1+sample;g=0;b=0;a=1;\n')
        scene=execute_scene(source,audio_frames()[:1],reader=READER,width=128,height=72,mesh_x=8,mesh_y=8)
        wave=source_custom_waves(source,scene)['frames'][0][0]
        self.assertEqual(wave['draw_mode'],'strip')
        self.assertEqual(len(wave['positions']),3)
        np.testing.assert_allclose(np.asarray(wave['positions'])[:,1],.5-.25/.5625,atol=1e-7)
        np.testing.assert_allclose(np.asarray(wave['colours'])[:,0],[1,1,254/255],atol=2e-7)
        np.testing.assert_allclose(wave['copy_offsets'],[[0,0],[.5/128,0],[.5/128,.5/128],[0,.5/128]])

    def test_thick_dots_use_size_two_and_one_draw_copy(self):
        from custom_wave import source_custom_waves
        source=native('wavecode_0_enabled=1\nwavecode_0_samples=2\nwavecode_0_bUseDots=1\nwavecode_0_bDrawThick=1\n')
        scene=execute_scene(source,audio_frames()[:1],reader=READER,mesh_x=8,mesh_y=8)
        wave=source_custom_waves(source,scene)['frames'][0][0]
        self.assertEqual(wave['draw_mode'],'points')
        self.assertEqual(wave['point_size'],2)
        self.assertEqual(wave['copy_offsets'],[[0,0]])


if __name__=='__main__':unittest.main()
