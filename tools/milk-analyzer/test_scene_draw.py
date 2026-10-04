import unittest
import numpy as np


class SceneDrawTest(unittest.TestCase):
    def test_custom_then_builtin_wave_draw_order_and_copy_offsets(self):
        from scene_draw import draw_source_scene
        source={'values':{}};frame={'main':{'darken_center':0},'shapes':[]}
        custom=[{'positions':[[.375,.375]],'colours':[[1,0,0,1]],'draw_mode':'points','point_size':1,'copy_offsets':[[0,0]],'additive':False}]
        builtin={'positions':[[[.375,.375]]],'rgba':[0,1,0,1],'draw_mode':'points','copy_offsets':[[0,0],[.25,0]],'additive':False}
        result=draw_source_scene(np.zeros((4,4,4)),source,frame,builtin,custom,quantize=False)
        np.testing.assert_array_equal(result[1,1],[0,1,0,1])
        np.testing.assert_array_equal(result[1,2],[0,1,0,1])

    def test_darkened_centre_precedes_border_and_remains_local(self):
        from scene_draw import draw_source_scene
        source={'values':{}};frame={'main':{'darken_center':1},'shapes':[]}
        result=draw_source_scene(np.ones((128,128,4)),source,frame,None,[],quantize=False)
        self.assertLess(result[64,64,0],1)
        self.assertGreater(result[64,64,0],.90)
        self.assertEqual(result[0,0,0],1)

    def test_shape_outline_uses_untextured_border_colour(self):
        from scene_draw import draw_source_scene
        values={'x':.5,'y':.5,'rad':1,'sides':4,'r':0,'g':0,'b':0,'a':0,'a2':0,
                'border_r':1,'border_g':0,'border_b':0,'border_a':1}
        result=draw_source_scene(np.zeros((16,16,4)),{'values':{}},{'main':{},'shapes':[{'index':0,'values':values}]},None,[],quantize=False)
        self.assertGreater(np.count_nonzero(result[...,0]),10)
        self.assertEqual(result[8,8,0],0)

    def test_missing_named_shape_texture_remains_unresolved(self):
        from scene_draw import draw_source_scene
        frame={'main':{},'shapes':[{'index':0,'values':{'textured':1}}]}
        with self.assertRaisesRegex(ValueError,'texture'):
            draw_source_scene(np.zeros((16,16,4)),{'values':{}},frame,None,[])


if __name__=='__main__':unittest.main()
