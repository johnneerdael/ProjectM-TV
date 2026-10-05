import unittest
from frame_chain import FrameChain


class FrameChainTest(unittest.TestCase):
    def test_motion_vectors_modify_previous_feedback_before_warp_and_blur(self):
        chain=FrameChain(warp_reads_blur=True,composite_discards=True,motion_vectors=True)
        first=chain.step();second=chain.step()
        self.assertEqual(first['warp_inputs']['main'].stage,'initial_feedback')
        self.assertEqual(second['motion_vector_input'],first['drawn_surface'])
        modified=second['motion_vector_output']
        self.assertEqual(second['warp_inputs']['main'],modified)
        self.assertEqual(second['composite_inputs']['blur_source'],modified)
        self.assertEqual(second['discard_target_contents'],modified)
        third=chain.step()
        self.assertEqual(third['warp_inputs']['blur_source'],modified)

    def test_main_sampling_flip_is_separate_from_unflipped_blur_source(self):
        result=FrameChain(warp_reads_blur=True).step()
        self.assertEqual(result['sampling_transforms']['warp_main'],'vertical_flip')
        self.assertEqual(result['sampling_transforms']['composite_main'],'vertical_flip')
        self.assertEqual(result['sampling_transforms']['blur_source'],'identity')

    def test_feedback_is_pre_composite_surface(self):
        chain=FrameChain(warp_reads_blur=False)
        first=chain.step()
        second=chain.step()
        self.assertEqual(second["warp_inputs"]["main"],first["drawn_surface"])
        self.assertNotEqual(second["warp_inputs"]["main"],first["display_surface"])

    def test_warp_blur_has_an_extra_frame_of_history(self):
        chain=FrameChain(warp_reads_blur=True)
        chain.step();chain.step();third=chain.step()
        self.assertEqual(third["warp_inputs"]["blur_source"].frame,0)
        self.assertEqual(third["composite_inputs"]["blur_source"].frame,1)

    def test_composite_main_contains_current_draws_and_blur_contains_previous_draws(self):
        chain=FrameChain(warp_reads_blur=True)
        chain.step();second=chain.step()
        self.assertEqual(second["composite_inputs"]["main"].frame,1)
        self.assertEqual(second["composite_inputs"]["blur_source"].frame,0)

    def test_no_warp_blur_reads_allows_blur_update_before_warp(self):
        chain=FrameChain(warp_reads_blur=False)
        chain.step();second=chain.step()
        self.assertEqual(second["blur_update_order"],"before_warp")
        self.assertEqual(second["warp_inputs"]["blur_source"],second["composite_inputs"]["blur_source"])

    def test_discard_retains_previous_feedback_not_previous_composite(self):
        chain=FrameChain(warp_reads_blur=True,composite_discards=True)
        first=chain.step();second=chain.step()
        self.assertEqual(second["discard_target_contents"],first["drawn_surface"])
        self.assertNotEqual(second["discard_target_contents"],first["display_surface"])


if __name__=="__main__":unittest.main()
