import numpy as np
import pytest


def test_white_range_claim_rejects_intervening_cyan_even_when_endpoints_are_white():
    from prediction_windows import validate_colour_claim
    rgb=np.full((11,4,4,3),255,np.uint8);rgb[1::2,...,0]=74
    with pytest.raises(ValueError,match='frames.*51'):
        validate_colour_claim(rgb,frame_numbers=list(range(50,61)),claimed_frames=list(range(50,61)),
                              lower_rgb=[.95,.95,.95],upper_rgb=[1,1,1],minimum_area=.8)


def test_exact_white_phase_claim_is_supported_and_retains_per_frame_coverage():
    from prediction_windows import validate_colour_claim,describe_colour_presence
    rgb=np.full((11,4,4,3),255,np.uint8);rgb[1::2,...,0]=74
    result=validate_colour_claim(rgb,frame_numbers=list(range(50,61)),claimed_frames=[50,52,54,56,58,60],
                                lower_rgb=[.95,.95,.95],upper_rgb=[1,1,1],minimum_area=.8)
    assert result['matched_frames']==[50,52,54,56,58,60]
    assert result['coverage_by_frame']['51']==0
    assert result['claimed_frames_verified'] is True
    text=describe_colour_presence(result,label='white')
    assert '50, 52, 54, 56, 58, 60' in text
    assert 'every frame' not in text


@pytest.mark.parametrize('frames',[[1,1],[2,1],[0],[4]])
def test_bad_or_unknown_frame_ids_cannot_certify_colour_claim(frames):
    from prediction_windows import validate_colour_claim
    with pytest.raises(ValueError,match='frame'):
        validate_colour_claim(np.full((3,2,2,3),255,np.uint8),frame_numbers=[1,2,3],claimed_frames=frames,
                              lower_rgb=[.95]*3,upper_rgb=[1]*3,minimum_area=.8)


def test_empty_claim_cannot_earn_vacuous_temporal_credit():
    from prediction_windows import validate_colour_claim
    with pytest.raises(ValueError,match='nonempty'):
        validate_colour_claim(np.full((3,2,2,3),255,np.uint8),frame_numbers=[1,2,3],claimed_frames=[],
                              lower_rgb=[.95]*3,upper_rgb=[1]*3,minimum_area=.8)


def test_exact_unorm_endpoint_is_accepted_without_upward_float32_rounding():
    from prediction_windows import validate_colour_claim
    rgb=np.full((1,2,2,3),128,np.uint8);value=128/255
    result=validate_colour_claim(rgb,frame_numbers=[1],claimed_frames=[1],lower_rgb=[value]*3,upper_rgb=[value]*3,minimum_area=1)
    assert result['coverage_by_frame']['1']==1
    with pytest.raises(ValueError,match='unsupported'):
        validate_colour_claim(rgb,frame_numbers=[1],claimed_frames=[1],lower_rgb=[value+1e-8]*3,upper_rgb=[1]*3,minimum_area=1)


def test_formatter_cannot_expand_verified_white_phases_to_unverified_cyan():
    from prediction_windows import validate_colour_claim,describe_colour_presence
    rgb=np.full((3,2,2,3),255,np.uint8);rgb[1,...,0]=74
    result=validate_colour_claim(rgb,frame_numbers=[50,51,52],claimed_frames=[50,52],lower_rgb=[.95]*3,upper_rgb=[1]*3,minimum_area=.8)
    result['claimed_frames']=[50,51,52]
    with pytest.raises(ValueError,match='verified|coverage'):
        describe_colour_presence(result,label='white')
