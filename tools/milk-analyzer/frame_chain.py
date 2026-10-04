"""Symbolic surfaces and history for the pinned TV renderer; no pixels are inspected.

Derived from MilkdropPreset::RenderFrame. The next warp consumes the pre-composite
surface, not the displayed composite. Warp blur reads use the older cached blur
bank; composite reads the newly updated bank sourced from the previous feedback.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Surface:
    frame: int
    stage: str


class FrameChain:
    def __init__(self, *, warp_reads_blur: bool, composite_discards: bool=False,
                 motion_vectors: bool=False):
        self.warp_reads_blur=warp_reads_blur
        self.composite_discards=composite_discards
        self.motion_vectors=motion_vectors
        self.frame=0
        self.feedback=Surface(-1,"initial_feedback")
        self.blur_source=Surface(-2,"initial_empty_blur")

    def step(self) -> dict:
        previous=self.feedback
        motion_input=previous if self.motion_vectors and self.frame>0 else None
        motion_output=Surface(previous.frame,"feedback_with_current_motion_vectors") if motion_input else None
        if motion_output:
            previous=motion_output
        if not self.warp_reads_blur:
            self.blur_source=previous
        warp_blur=self.blur_source
        warped=Surface(self.frame,"warped")
        # Native order: shapes, custom waves, built-in waveform, darken-centre, borders.
        drawn=Surface(self.frame,"warped_with_draws")
        if self.warp_reads_blur:
            self.blur_source=previous
        displayed=Surface(self.frame,"composite_display")
        result={"frame":self.frame,"warp_inputs":{"main":previous,"blur_source":warp_blur},
                "motion_vector_input":motion_input,"motion_vector_output":motion_output,
                "sampling_transforms":{"warp_main":"vertical_flip",
                                       "composite_main":"vertical_flip","blur_source":"identity"},
                "warped_surface":warped,"drawn_surface":drawn,
                "composite_inputs":{"main":drawn,"blur_source":self.blur_source},
                "display_surface":displayed,
                "blur_update_order":"after_warp" if self.warp_reads_blur else "before_warp",
                "discard_target_contents":previous if self.composite_discards else None,
                "feedback_next":drawn}
        self.feedback=drawn
        self.frame+=1
        return result
