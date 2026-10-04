"""Native draw positions in the pre-composite feedback canvas, without images.

CustomWaveform applies inverse aspect to point coordinates; CustomShape does not
apply it to the centre. Both use PresetState::orthogonalProjection, whose Y scale
is -1 (glm::ortho(-1,1,1,-1,...)). Convert the resulting clip position to image
coordinates measured from the top. Final composite sampling, echo, wrapping,
feedback trails and clipping must be handled separately.
"""
import math


def custom_wave_feedback_screen(x:float,y:float,*,aspect_x:float,aspect_y:float)->tuple[float,float]:
    if not all(math.isfinite(v) for v in (x,y,aspect_x,aspect_y)) or min(aspect_x,aspect_y)<=0:
        raise ValueError('finite coordinates and positive finite aspect factors required')
    return .5+(x-.5)/aspect_x, .5-(y-.5)/aspect_y


def custom_shape_feedback_screen(x:float,y:float)->tuple[float,float]:
    if not all(math.isfinite(v) for v in (x,y)):
        raise ValueError('finite coordinates required')
    return x,1-y
