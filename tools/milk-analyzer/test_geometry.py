import unittest
import importlib


class GeometryTest(unittest.TestCase):
    def test_custom_wave_includes_native_projection_reversal_and_aspect(self):
        geometry=importlib.import_module('geometry')
        x,y=geometry.custom_wave_feedback_screen(.375,.75,aspect_x=1,aspect_y=.5625)
        self.assertAlmostEqual(x,.375)
        self.assertAlmostEqual(y,.5-.25/.5625)

    def test_shape_centre_has_projection_reversal_without_wave_aspect_scaling(self):
        geometry=importlib.import_module('geometry')
        self.assertEqual(geometry.custom_shape_feedback_screen(.375,.75),(.375,.25))

    def test_offscreen_wave_coordinates_are_not_clamped_into_a_false_visible_bound(self):
        geometry=importlib.import_module('geometry')
        _,y=geometry.custom_wave_feedback_screen(.5,1.1,aspect_x=1,aspect_y=.5625)
        self.assertLess(y,0)
        with self.assertRaises(ValueError):
            geometry.custom_wave_feedback_screen(.5,.5,aspect_x=1,aspect_y=0)


if __name__=='__main__':unittest.main()
