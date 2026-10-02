import cv2
import numpy as np
import pytest

from preset_lab.features import measure_frame


def texture(width=128, height=96):
    rng = np.random.default_rng(123)
    return rng.integers(0, 256, (height, width, 3), dtype=np.uint8)


def test_dark_white_and_tiny_visibility_are_distinct():
    black = np.zeros((64, 96, 3), np.uint8)
    white = np.full_like(black, 255)
    tiny = black.copy()
    tiny[32, 48] = 255
    assert measure_frame(black, None, 30)["coverage"] == 0
    bright = measure_frame(white, black, 30)
    assert bright["brightness"] == pytest.approx(1)
    assert bright["coverage"] == 1
    assert bright["contrast"] == 0
    assert bright["luma_change"] == pytest.approx(1)
    assert measure_frame(tiny, black, 30)["coverage"] == pytest.approx(1 / (64 * 96))


def test_translation_is_in_viewport_units_per_second():
    previous = texture()
    current = cv2.warpAffine(previous, np.float32([[1, 0, 2], [0, 1, 0]]), (128, 96),
                             borderMode=cv2.BORDER_REFLECT)
    metrics = measure_frame(current, previous, 30)
    assert metrics["translation_x"] == pytest.approx(2 / 128 * 30, abs=0.04)
    assert abs(metrics["rotation"]) < 0.05
    assert abs(metrics["expansion"]) < 0.05
    assert metrics["motion_density"] > 0.8


def test_rotation_and_expansion_are_separate_from_translation():
    previous = texture()
    rotated = cv2.warpAffine(previous, cv2.getRotationMatrix2D((64, 48), 1, 1), (128, 96),
                             borderMode=cv2.BORDER_REFLECT)
    rotation = measure_frame(rotated, previous, 30)
    assert abs(rotation["rotation"]) > 0.3
    assert abs(rotation["expansion"]) < 0.12
    expanded = cv2.warpAffine(previous, cv2.getRotationMatrix2D((64, 48), 0, 1.01), (128, 96),
                              borderMode=cv2.BORDER_REFLECT)
    expansion = measure_frame(expanded, previous, 30)
    assert expansion["expansion"] > 0.15
    assert abs(expansion["rotation"]) < 0.08


def test_frame_rate_normalization_tracks_velocity_not_per_frame_distance():
    previous = texture()
    one = cv2.warpAffine(previous, np.float32([[1, 0, 1], [0, 1, 0]]), (128, 96),
                         borderMode=cv2.BORDER_REFLECT)
    two = cv2.warpAffine(previous, np.float32([[1, 0, 2], [0, 1, 0]]), (128, 96),
                         borderMode=cv2.BORDER_REFLECT)
    at60 = measure_frame(one, previous, 60)
    at30 = measure_frame(two, previous, 30)
    assert at60["translation_x"] == pytest.approx(at30["translation_x"], rel=0.1)


def test_resolution_normalization_tracks_same_viewport_motion():
    small = texture()
    large = cv2.resize(small, (256, 192), interpolation=cv2.INTER_LINEAR)
    moved_small = cv2.warpAffine(small, np.float32([[1, 0, 2], [0, 1, 0]]), (128, 96),
                                 borderMode=cv2.BORDER_REFLECT)
    moved_large = cv2.warpAffine(large, np.float32([[1, 0, 4], [0, 1, 0]]), (256, 192),
                                 borderMode=cv2.BORDER_REFLECT)
    assert measure_frame(moved_small, small, 30)["translation_x"] == pytest.approx(
        measure_frame(moved_large, large, 30)["translation_x"], rel=0.1)


def test_flat_images_do_not_claim_reliable_flow_fit():
    black = np.zeros((64, 96, 3), np.uint8)
    metrics = measure_frame(np.full_like(black, 127), black, 30)
    assert not metrics["motion_fit_available"]
    assert metrics["motion_speed"] == 0


def test_invalid_frame_shape_is_rejected():
    with pytest.raises(ValueError):
        measure_frame(np.zeros((12, 12), np.uint8), None, 30)
