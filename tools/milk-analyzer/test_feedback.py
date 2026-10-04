import math
import unittest
import feedback
from feedback import clipped_affine_feedback, inverse_sqrt_ridge


class FeedbackTest(unittest.TestCase):
    def test_zero_seed_has_no_strictly_positive_support(self):
        result=inverse_sqrt_ridge(numerator=0,root_bias=.2,
                                 constant_injection=0,output_scale=.99)
        self.assertEqual(result['positive_support_end'],0)

    def test_delayed_feedback_preserves_two_distinct_history_coefficients(self):
        result=feedback.delayed_affine_feedback(recent_gain=.990495,
                                               older_gain=-.0297,injection=.01742)
        root=(.990495+math.sqrt(.990495**2-4*.0297))/2
        self.assertEqual(result['status'],'locally_stable')
        self.assertAlmostEqual(result['fixed_point'],.01742/(1-.990495+.0297))
        self.assertAlmostEqual(result['spectral_radius'],root)
        self.assertAlmostEqual(result['asymptotic_half_life_frames'],math.log(.5)/math.log(root))
        self.assertNotAlmostEqual(result['asymptotic_half_life_frames'],math.log(.5)/math.log(.960795),places=1)

    def test_delayed_feedback_with_complex_roots_uses_their_magnitude(self):
        result=feedback.delayed_affine_feedback(recent_gain=.4,older_gain=-.25,injection=.1)
        self.assertAlmostEqual(result['spectral_radius'],.5)
        self.assertAlmostEqual(result['asymptotic_half_life_frames'],1)

    def test_delayed_feedback_does_not_claim_global_contraction_with_negative_gain(self):
        result=feedback.delayed_affine_feedback(recent_gain=.990495,older_gain=-.0297,injection=.1)
        self.assertEqual(result['validity'],'unsaturated linear recurrence only')
        unstable=feedback.delayed_affine_feedback(recent_gain=1.2,older_gain=.1,injection=.1)
        self.assertEqual(unstable['status'],'locally_unstable_or_neutral')
        self.assertIsNone(unstable['asymptotic_half_life_frames'])

    def test_uniform_feedback_exposes_fixed_point_and_settling_time(self):
        result=clipped_affine_feedback(gain=.960795,injection=.01742)
        self.assertAlmostEqual(result["fixed_point"],.01742/(1-.960795))
        self.assertAlmostEqual(result["half_life_frames"],math.log(.5)/math.log(.960795))

    def test_negative_injection_does_not_create_a_positive_background(self):
        self.assertEqual(clipped_affine_feedback(gain=.960795,injection=-.006)["fixed_point"],0)

    def test_positive_seed_has_narrow_spatial_support(self):
        result=inverse_sqrt_ridge(numerator=.008,root_bias=.2,
                                 constant_injection=.99*.018-.04,output_scale=.99)
        edge=(.99*.008/(.04-.99*.018)-.2)**2
        self.assertAlmostEqual(result["positive_support_end"],edge)
        self.assertLess(result["positive_support_end"],.03)
        self.assertEqual(result["undefined_domain"],"coordinate < 0")

    def test_unstable_feedback_is_not_given_a_false_convergent_fixed_point(self):
        self.assertEqual(clipped_affine_feedback(gain=1.05,injection=.1)["status"],"noncontractive")


if __name__=="__main__":unittest.main()
