"""Numerical policies for the five published 2.3.15 engine fixes."""
import importlib

import numpy as np
import pytest


ENGINE = {'commit': 'e0b0a967f0ffd7d332106c366668ed271718472b',
          'patches_sha256': '7ef297fcab5d42d0531ec621ac6a464a5a0e7982da02bb40996bc62a886ae527'}
BLUR = 'projectmtv-core-2.3.15-blur-ranges-v1'
ZOOM = 'projectmtv-core-2.3.15-signed-unit-zoom-v1'
DISPLAY = 'projectmtv-core-2.3.15-live-display-controls-v1'
SHAPE = 'projectmtv-core-2.3.15-shape-sampler-v1'


def test_new_engine_selects_explicit_repeat_linear_for_all_unnamed_shapes():
    module = importlib.import_module('forecast')
    assert module.source_shape_sampler_policy(ENGINE, None) == SHAPE
    sampling = importlib.import_module('shape_sampling')
    entries = [{'index': 0, 'values': {'textured': 1}} for _ in range(2)]
    modes = sampling.shape_sampling_modes(entries, image_names={}, policy=SHAPE,
        warp_reads_blur=True, blur_level=3, frame_wrap=0)
    assert modes == {0: {'wrap': True, 'linear': True}, 1: {'wrap': True, 'linear': True}}


def test_current_shape_policy_preserves_named_descriptor_modes():
    module = importlib.import_module('shape_sampling')
    entries = [{'index': 0, 'values': {'textured': 1}}]
    assert module.shape_sampling_modes(entries, image_names={0: 'pc_test'}, policy=SHAPE,
        warp_reads_blur=False, blur_level=0, frame_wrap=1)[0] == {'wrap': False, 'linear': False}


def test_current_blur_policy_pushes_bounds_apart_instead_of_collapsing():
    module = importlib.import_module('blur')
    low, high = module.native_ranges([0]*3, [.01, 1, 1], policy=BLUR)
    assert low[0] == pytest.approx(-.045, abs=1e-8)
    assert high[0] == pytest.approx(.055, abs=1e-8)
    bank = module.blur_bank(np.full((32, 32, 3), .005), levels=1,
        minimum=[0]*3, maximum=[.01, 1, 1], policy=BLUR, quantize=False)
    np.testing.assert_allclose(bank[1], .5, atol=1e-6)


@pytest.mark.parametrize('minimum,maximum', [
    ([float('nan')]*3, [1]*3), ([1e300]*3, [1e300]*3),
    ([1e30]*3, [1e30]*3),
])
def test_unsupported_current_blur_triplet_uses_coherent_defaults(minimum, maximum):
    module = importlib.import_module('blur')
    low, high = module.native_ranges(minimum, maximum, policy=BLUR)
    np.testing.assert_array_equal(low, [0, 0, 0])
    np.testing.assert_array_equal(high, [1, 1, 1])


def test_signed_negative_zoom_is_defined_only_for_the_patched_unit_exponent():
    module = importlib.import_module('spatial')
    uv = module.warp_vertex_uv([[.5, .25]], zoom=-2, zoomexp=1, zoom_policy=ZOOM)
    np.testing.assert_allclose(uv, [[.375, .4375]], atol=1e-7)
    with pytest.raises(ValueError, match='power domain'):
        module.warp_vertex_uv([[.5, .25]], zoom=-2, zoomexp=2, zoom_policy=ZOOM)
    with pytest.raises(ValueError, match='power domain'):
        module.warp_vertex_uv([[.5, .25]], zoom=-2, zoomexp=1)


def controls(**changes):
    return {'gamma': 1, 'echo_alpha': 0, 'echo_zoom': 1, 'echo_orient': 0,
            'brighten': 0, 'darken': 0, 'solarize': 0, 'invert': 0, **changes}


def test_live_display_uses_evaluated_gamma_and_equation_only_filter():
    module = importlib.import_module('legacy_composite')
    field = np.full((8, 8, 4), .1, dtype=np.float32); field[..., 3] = 1
    expected = module.legacy_display(field, values={'fGammaAdj': '1', 'bInvert': '1'},
        time=0, hue_offsets=[0]*4, quantize=False)
    live = module.legacy_display(field, values={'fGammaAdj': '2'},
        main=controls(invert=-1), control_policy=DISPLAY, time=0, hue_offsets=[0]*4, quantize=False)
    np.testing.assert_array_equal(live, expected)


@pytest.mark.parametrize('orientation', [float('nan'), float('inf'), 2**31, -2**31-1])
def test_invalid_live_echo_orientation_omits_echo_but_preserves_gamma(orientation):
    module = importlib.import_module('legacy_composite')
    field = np.full((8, 8, 4), .1, dtype=np.float32); field[..., 3] = 1
    expected = module.legacy_display(field, values={'fGammaAdj': '1'},
        time=0, hue_offsets=[0]*4, quantize=False)
    live = module.legacy_display(field, values={}, main=controls(echo_alpha=1, echo_orient=orientation),
        control_policy=DISPLAY, time=0, hue_offsets=[0]*4, quantize=False)
    np.testing.assert_array_equal(live, expected)


def test_current_policy_cannot_borrow_a_mutated_engine_identity():
    module = importlib.import_module('forecast')
    with pytest.raises(ValueError, match='identity'):
        module.source_shape_sampler_policy({**ENGINE, 'patches_sha256': '0'*64}, SHAPE)


def test_live_filter_nonzero_predicate_handles_known_nan_and_unused_echo_alpha():
    module = importlib.import_module('legacy_composite')
    field = np.full((8,8,4), .1, dtype=np.float32)
    expected = module.legacy_display(field, values={'fGammaAdj':'1','bInvert':'1'},
        time=0, hue_offsets=[0]*4, quantize=False)
    actual = module.legacy_display(field, values={},
        main=controls(invert={'ieee':'nan'},echo_alpha={'ieee':'nan'}), control_policy=DISPLAY,
        time=0, hue_offsets=[0]*4, quantize=False)
    np.testing.assert_array_equal(actual,expected)
